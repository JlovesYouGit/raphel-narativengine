/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

/**
 * @file plane_2d_generator.c
 * @brief 2D Plane Generation with X Plane Processing for 3D Spatial Audio
 * 
 * This module implements the 2D plane generation logic shown in the diagram,
 * specifically addressing the X plane processing with Y+ and Y- channels
 * that was causing distortion due to delay issues.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#include "plane_2d_generator.h"
#include "delay_compensation.h"

// Internal constants
#define PLANE_2D_MAX_POINTS 1000
#define PLANE_2D_INTERPOLATION_STEPS 10
#define PLANE_2D_PHASE_PRECISION 0.001f
#define PLANE_2D_X_RANGE 3.0f  // Match diagram X range (-3 to 3)
#define PLANE_2D_Y_RANGE 3.0f  // Match diagram Y range (-3 to 3)

// Internal helper functions
static float interpolate_linear(float a, float b, float t);
static void calculate_plane_coefficients(const plane_2d_point_t* points, size_t num_points, 
                                        plane_coefficients_t* coeffs);
static float evaluate_plane_at_point(const plane_coefficients_t* coeffs, float x, float y);
static void apply_x_plane_processing(plane_2d_generator_t* generator, audio_sample_2d_t* sample);
static void apply_y_channel_correction(plane_2d_generator_t* generator, audio_sample_2d_t* sample);

/**
 * @brief Initialize 2D plane generator with X plane processing
 */
bool plane_2d_generator_init(plane_2d_generator_t* generator, const plane_2d_config_t* config) {
    if (!generator || !config) {
        return false;
    }

    // Initialize structure
    memset(generator, 0, sizeof(plane_2d_generator_t));
    generator->config = *config;

    // Validate configuration
    if (config->sample_rate < 8000.0f || config->sample_rate > 192000.0f ||
        config->channels == 0 || config->channels > 8 ||
        config->x_plane_range <= 0.0f || config->y_plane_range <= 0.0f) {
        return false;
    }

    // Allocate point buffer
    generator->point_buffer = (plane_2d_point_t*)malloc(PLANE_2D_MAX_POINTS * sizeof(plane_2d_point_t));
    if (!generator->point_buffer) {
        return false;
    }

    // Initialize delay compensator for Y+ and Y- channels
    delay_params_t delay_params;
    delay_params_3d_spatial(&delay_params);
    delay_params.delay_ms = config->delay_compensation_ms;
    delay_params.sample_rate = config->sample_rate;

    if (!delay_compensator_init(&generator->delay_compensator, &delay_params)) {
        plane_2d_generator_cleanup(generator);
        return false;
    }

    // Initialize plane coefficients
    memset(&generator->plane_coeffs, 0, sizeof(plane_coefficients_t));
    generator->plane_coeffs.a = 1.0f;  // Default flat plane

    // Initialize phase accumulator
    generator->phase_accumulator = 0.0f;
    generator->x_phase_offset = 0.0f;
    generator->y_phase_offset = 0.0f;

    // Initialize processing state
    generator->num_points = 0;
    generator->current_x = 0.0f;
    generator->current_y = 0.0f;
    generator->processing_enabled = true;

    generator->is_initialized = true;
    return true;
}

/**
 * @brief Cleanup 2D plane generator resources
 */
void plane_2d_generator_cleanup(plane_2d_generator_t* generator) {
    if (!generator) {
        return;
    }

    if (generator->point_buffer) {
        free(generator->point_buffer);
        generator->point_buffer = NULL;
    }

    delay_compensator_cleanup(&generator->delay_compensator);
    memset(generator, 0, sizeof(plane_2d_generator_t));
}

/**
 * @brief Generate 2D plane samples with X plane processing and delay compensation
 */
bool plane_2d_generator_process(
    plane_2d_generator_t* generator,
    float x_position,
    float y_position,
    audio_sample_2d_t* sample
) {
    if (!generator || !generator->is_initialized || !sample) {
        return false;
    }

    if (!generator->processing_enabled) {
        // Return zero samples if processing is disabled
        memset(sample, 0, sizeof(audio_sample_2d_t));
        return true;
    }

    // Update current position
    generator->current_x = x_position;
    generator->current_y = y_position;

    // Normalize positions to -1 to 1 range
    float x_norm = fmaxf(-1.0f, fminf(1.0f, x_position / generator->config.x_plane_range));
    float y_norm = fmaxf(-1.0f, fminf(1.0f, y_position / generator->config.y_plane_range));

    // Generate X plane component (primary signal)
    float x_phase = generator->phase_accumulator + x_norm * M_PI + generator->x_phase_offset;
    sample->x_component = sinf(x_phase);

    // Generate Y+ and Y- components with 90-degree phase shift
    float y_phase_offset = y_norm * M_PI / 2.0f + generator->y_phase_offset;
    float y_plus_phase = generator->phase_accumulator + y_phase_offset;
    float y_minus_phase = generator->phase_accumulator - y_phase_offset;

    float y_plus_raw = sinf(y_plus_phase);
    float y_minus_raw = sinf(y_minus_phase);

    // Apply delay compensation to reduce Y+ and Y- distortion
    float y_plus_compensated, y_minus_compensated;
    if (!delay_compensator_process(&generator->delay_compensator, y_plus_raw, y_minus_raw,
                                  &y_plus_compensated, &y_minus_compensated)) {
        // Fallback to raw values if compensation fails
        y_plus_compensated = y_plus_raw;
        y_minus_compensated = y_minus_raw;
    }

    sample->y_plus = y_plus_compensated;
    sample->y_minus = y_minus_compensated;

    // Apply X plane processing
    apply_x_plane_processing(generator, sample);

    // Apply Y channel correction
    apply_y_channel_correction(generator, sample);

    // Apply plane equation modulation
    float plane_value = evaluate_plane_at_point(&generator->plane_coeffs, x_norm, y_norm);
    sample->x_component *= plane_value;
    sample->y_plus *= plane_value;
    sample->y_minus *= plane_value;

    // Calculate combined magnitude and phase
    sample->magnitude = sqrtf(sample->x_component * sample->x_component + 
                              sample->y_plus * sample->y_plus + 
                              sample->y_minus * sample->y_minus);
    sample->phase = atan2f(sample->y_plus + sample->y_minus, sample->x_component);

    // Update phase accumulator
    generator->phase_accumulator += 2.0f * M_PI / (generator->config.sample_rate / 440.0f); // 440Hz reference
    
    // Wrap phase to prevent overflow
    while (generator->phase_accumulator > 2.0f * M_PI) {
        generator->phase_accumulator -= 2.0f * M_PI;
    }

    return true;
}

/**
 * @brief Add point to 2D plane for coefficient calculation
 */
bool plane_2d_generator_add_point(plane_2d_generator_t* generator, float x, float y, float value) {
    if (!generator || !generator->is_initialized || generator->num_points >= PLANE_2D_MAX_POINTS) {
        return false;
    }

    plane_2d_point_t* point = &generator->point_buffer[generator->num_points];
    point->x = x;
    point->y = y;
    point->value = value;
    point->weight = 1.0f;

    generator->num_points++;
    return true;
}

/**
 * @brief Calculate plane coefficients from added points
 */
bool plane_2d_generator_calculate_plane(plane_2d_generator_t* generator) {
    if (!generator || !generator->is_initialized || generator->num_points < 3) {
        return false;
    }

    calculate_plane_coefficients(generator->point_buffer, generator->num_points, &generator->plane_coeffs);
    return true;
}

/**
 * @brief Set plane coefficients directly
 */
bool plane_2d_generator_set_plane_coefficients(plane_2d_generator_t* generator, 
                                               const plane_coefficients_t* coeffs) {
    if (!generator || !generator->is_initialized || !coeffs) {
        return false;
    }

    generator->plane_coeffs = *coeffs;
    return true;
}

/**
 * @brief Get current plane coefficients
 */
bool plane_2d_generator_get_plane_coefficients(const plane_2d_generator_t* generator, 
                                               plane_coefficients_t* coeffs) {
    if (!generator || !generator->is_initialized || !coeffs) {
        return false;
    }

    *coeffs = generator->plane_coeffs;
    return true;
}

/**
 * @brief Reset plane generator state
 */
bool plane_2d_generator_reset(plane_2d_generator_t* generator) {
    if (!generator || !generator->is_initialized) {
        return false;
    }

    // Reset phase accumulator
    generator->phase_accumulator = 0.0f;
    generator->x_phase_offset = 0.0f;
    generator->y_phase_offset = 0.0f;

    // Reset plane coefficients
    memset(&generator->plane_coeffs, 0, sizeof(plane_coefficients_t));
    generator->plane_coeffs.a = 1.0f;  // Default flat plane

    // Clear point buffer
    generator->num_points = 0;

    // Reset position
    generator->current_x = 0.0f;
    generator->current_y = 0.0f;

    // Reset delay compensator
    delay_compensator_reset(&generator->delay_compensator);

    return true;
}

/**
 * @brief Enable/disable processing
 */
void plane_2d_generator_set_processing_enabled(plane_2d_generator_t* generator, bool enabled) {
    if (generator && generator->is_initialized) {
        generator->processing_enabled = enabled;
    }
}

/**
 * @brief Get processing status
 */
bool plane_2d_generator_get_status(const plane_2d_generator_t* generator, plane_2d_status_t* status) {
    if (!generator || !generator->is_initialized || !status) {
        return false;
    }

    status->processing_enabled = generator->processing_enabled;
    status->num_points = generator->num_points;
    status->current_x = generator->current_x;
    status->current_y = generator->current_y;
    status->phase_accumulator = generator->phase_accumulator;

    // Get delay compensator status
    return delay_compensator_get_status(&generator->delay_compensator, &status->delay_status);
}

/**
 * @brief Create default 2D plane configuration
 */
void plane_2d_config_default(plane_2d_config_t* config) {
    if (!config) {
        return;
    }

    config->sample_rate = 48000.0f;
    config->channels = 2;
    config->x_plane_range = PLANE_2D_X_RANGE;
    config->y_plane_range = PLANE_2D_Y_RANGE;
    config->delay_compensation_ms = 3.0f;
    config->distortion_correction_factor = 0.95f;
    config->enable_x_plane_processing = true;
    config->enable_y_channel_correction = true;
    config->enable_adaptive_plane = false;
}

/**
 * @brief Create configuration optimized for diagram-based processing
 */
void plane_2d_config_diagram_optimized(plane_2d_config_t* config) {
    if (!config) {
        return;
    }

    config->sample_rate = 48000.0f;
    config->channels = 2;
    config->x_plane_range = 3.0f;  // Match diagram exactly
    config->y_plane_range = 3.0f;  // Match diagram exactly
    config->delay_compensation_ms = 2.0f;  // Reduced for diagram accuracy
    config->distortion_correction_factor = 0.9f;  // Stronger correction
    config->enable_x_plane_processing = true;
    config->enable_y_channel_correction = true;
    config->enable_adaptive_plane = true;
}

// Private helper functions

/**
 * @brief Linear interpolation helper
 */
static float interpolate_linear(float a, float b, float t) {
    return a + (b - a) * t;
}

/**
 * @brief Calculate plane coefficients using least squares
 */
static void calculate_plane_coefficients(const plane_2d_point_t* points, size_t num_points, 
                                        plane_coefficients_t* coeffs) {
    if (!points || !coeffs || num_points < 3) {
        return;
    }

    // Simplified plane fitting: z = a*x + b*y + c
    float sum_x = 0.0f, sum_y = 0.0f, sum_z = 0.0f;
    float sum_xx = 0.0f, sum_yy = 0.0f, sum_xy = 0.0f;
    float sum_xz = 0.0f, sum_yz = 0.0f;
    float sum_weight = 0.0f;

    for (size_t i = 0; i < num_points; i++) {
        float x = points[i].x;
        float y = points[i].y;
        float z = points[i].value;
        float w = points[i].weight;

        sum_x += x * w;
        sum_y += y * w;
        sum_z += z * w;
        sum_xx += x * x * w;
        sum_yy += y * y * w;
        sum_xy += x * y * w;
        sum_xz += x * z * w;
        sum_yz += y * z * w;
        sum_weight += w;
    }

    // Calculate coefficients using simplified approach
    float denom = sum_xx * sum_yy - sum_xy * sum_xy;
    if (fabsf(denom) < 0.001f) {
        // Fallback to flat plane
        coeffs->a = 1.0f;
        coeffs->b = 0.0f;
        coeffs->c = 0.0f;
        return;
    }

    coeffs->a = (sum_xz * sum_yy - sum_yz * sum_xy) / denom;
    coeffs->b = (sum_yz * sum_xx - sum_xz * sum_xy) / denom;
    coeffs->c = (sum_z - coeffs->a * sum_x - coeffs->b * sum_y) / sum_weight;
}

/**
 * @brief Evaluate plane equation at given point
 */
static float evaluate_plane_at_point(const plane_coefficients_t* coeffs, float x, float y) {
    if (!coeffs) {
        return 1.0f;  // Default flat response
    }

    return coeffs->a * x + coeffs->b * y + coeffs->c;
}

/**
 * @brief Apply X plane processing to sample
 */
static void apply_x_plane_processing(plane_2d_generator_t* generator, audio_sample_2d_t* sample) {
    if (!generator || !sample || !generator->config.enable_x_plane_processing) {
        return;
    }

    // Apply X plane modulation based on current X position
    float x_modulation = 1.0f + generator->current_x / generator->config.x_plane_range * 0.2f;
    
    sample->x_component *= x_modulation;
    
    // Apply slight phase shift to Y components based on X position
    float x_phase_shift = generator->current_x / generator->config.x_plane_range * M_PI / 6.0f; // 30 degrees max
    float y_plus_phase = atan2f(sample->y_plus, sample->x_component) + x_phase_shift;
    float y_minus_phase = atan2f(sample->y_minus, sample->x_component) - x_phase_shift;
    
    float magnitude = sqrtf(sample->x_component * sample->x_component + 
                           sample->y_plus * sample->y_plus + 
                           sample->y_minus * sample->y_minus);
    
    sample->y_plus = magnitude * sinf(y_plus_phase);
    sample->y_minus = magnitude * sinf(y_minus_phase);
}

/**
 * @brief Apply Y channel correction to reduce distortion
 */
static void apply_y_channel_correction(plane_2d_generator_t* generator, audio_sample_2d_t* sample) {
    if (!generator || !sample || !generator->config.enable_y_channel_correction) {
        return;
    }

    // Apply correction factor to reduce Y channel distortion
    float correction_factor = generator->config.distortion_correction_factor;
    
    // Apply stronger correction at extremes
    float y_magnitude = sqrtf(sample->y_plus * sample->y_plus + sample->y_minus * sample->y_minus);
    if (y_magnitude > 0.5f) {
        correction_factor *= (1.0f - (y_magnitude - 0.5f) * 0.2f);
    }

    sample->y_plus *= correction_factor;
    sample->y_minus *= correction_factor;

    // Apply anti-clipping
    sample->y_plus = fmaxf(-1.0f, fminf(1.0f, sample->y_plus));
    sample->y_minus = fmaxf(-1.0f, fminf(1.0f, sample->y_minus));
}
