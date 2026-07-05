/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

/**
 * @file delay_compensation.c
 * @brief Advanced delay compensation for Y+ and Y- distortion correction in 2D plane generation
 * 
 * This module addresses the specific issue where delay in audio processing causes
 * distortion in Y+ and Y- directions on the X plane, preventing proper 3D spatial
 * audio generation during 2D plane initialization and processing.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#include "delay_compensation.h"

// Internal constants
#define MAX_DELAY_SAMPLES 8192
#define MIN_DELAY_SAMPLES 1
#define DISTORTION_THRESHOLD 0.1f
#define PHASE_ALIGNMENT_PRECISION 0.001f

// Internal helper functions
static float calculate_phase_error(float y_plus, float y_minus, float expected_phase);
static void apply_phase_correction(delay_compensator_t* compensator, float* y_plus, float* y_minus);
static void update_adaptive_parameters(delay_compensator_t* compensator, float error);
static bool validate_delay_parameters(const delay_params_t* params);

/**
 * @brief Initialize delay compensator for Y+ and Y- distortion correction
 */
bool delay_compensator_init(delay_compensator_t* compensator, const delay_params_t* params) {
    if (!compensator || !params) {
        return false;
    }

    if (!validate_delay_parameters(params)) {
        return false;
    }

    // Initialize structure
    memset(compensator, 0, sizeof(delay_compensator_t));
    compensator->params = *params;

    // Calculate delay samples
    compensator->delay_samples = (size_t)(params->delay_ms / 1000.0f * params->sample_rate);
    
    // Clamp delay samples
    if (compensator->delay_samples < MIN_DELAY_SAMPLES) {
        compensator->delay_samples = MIN_DELAY_SAMPLES;
    } else if (compensator->delay_samples > MAX_DELAY_SAMPLES) {
        compensator->delay_samples = MAX_DELAY_SAMPLES;
    }

    // Allocate delay buffers
    compensator->y_plus_buffer = (float*)malloc(compensator->delay_samples * sizeof(float));
    compensator->y_minus_buffer = (float*)malloc(compensator->delay_samples * sizeof(float));
    compensator->phase_buffer = (float*)malloc(compensator->delay_samples * sizeof(float));

    if (!compensator->y_plus_buffer || !compensator->y_minus_buffer || !compensator->phase_buffer) {
        delay_compensator_cleanup(compensator);
        return false;
    }

    // Initialize buffers
    memset(compensator->y_plus_buffer, 0, compensator->delay_samples * sizeof(float));
    memset(compensator->y_minus_buffer, 0, compensator->delay_samples * sizeof(float));
    memset(compensator->phase_buffer, 0, compensator->delay_samples * sizeof(float));

    // Initialize circular buffer indices
    compensator->write_index = 0;
    compensator->read_index = 0;
    compensator->buffer_ready = false;

    // Initialize adaptive parameters
    compensator->adaptive_factor = params->adaptive_factor;
    compensator->phase_error_accumulator = 0.0f;
    compensator->distortion_correction_factor = 1.0f;

    compensator->is_initialized = true;
    return true;
}

/**
 * @brief Cleanup delay compensator resources
 */
void delay_compensator_cleanup(delay_compensator_t* compensator) {
    if (!compensator) {
        return;
    }

    if (compensator->y_plus_buffer) {
        free(compensator->y_plus_buffer);
        compensator->y_plus_buffer = NULL;
    }

    if (compensator->y_minus_buffer) {
        free(compensator->y_minus_buffer);
        compensator->y_minus_buffer = NULL;
    }

    if (compensator->phase_buffer) {
        free(compensator->phase_buffer);
        compensator->phase_buffer = NULL;
    }

    memset(compensator, 0, sizeof(delay_compensator_t));
}

/**
 * @brief Process samples with delay compensation and distortion correction
 */
bool delay_compensator_process(
    delay_compensator_t* compensator,
    float y_plus_input,
    float y_minus_input,
    float* y_plus_output,
    float* y_minus_output
) {
    if (!compensator || !compensator->is_initialized || !y_plus_output || !y_minus_output) {
        return false;
    }

    // Store current samples in delay buffer
    compensator->y_plus_buffer[compensator->write_index] = y_plus_input;
    compensator->y_minus_buffer[compensator->write_index] = y_minus_input;
    
    // Calculate phase relationship
    float current_phase = atan2f(y_minus_input, y_plus_input);
    compensator->phase_buffer[compensator->write_index] = current_phase;

    // Update write index
    compensator->write_index = (compensator->write_index + 1) % compensator->delay_samples;

    // Check if buffer is ready for reading
    if (!compensator->buffer_ready) {
        if (compensator->write_index == 0) {
            compensator->buffer_ready = true;
        } else {
            // Buffer not yet ready, return input values
            *y_plus_output = y_plus_input;
            *y_minus_output = y_minus_input;
            return true;
        }
    }

    // Read delayed samples
    *y_plus_output = compensator->y_plus_buffer[compensator->read_index];
    *y_minus_output = compensator->y_minus_buffer[compensator->read_index];

    // Calculate expected phase based on delay
    float expected_phase = compensator->phase_buffer[compensator->read_index];
    
    // Calculate phase error
    float phase_error = calculate_phase_error(*y_plus_output, *y_minus_output, expected_phase);
    
    // Apply adaptive phase correction
    if (compensator->params.enable_adaptive_correction) {
        apply_phase_correction(compensator, y_plus_output, y_minus_output);
        update_adaptive_parameters(compensator, phase_error);
    }

    // Apply distortion correction
    apply_distortion_correction(compensator, y_plus_output, y_minus_output);

    // Update read index
    compensator->read_index = (compensator->read_index + 1) % compensator->delay_samples;

    return true;
}

/**
 * @brief Apply distortion correction for Y+ and Y- channels
 */
void apply_distortion_correction(delay_compensator_t* compensator, float* y_plus, float* y_minus) {
    if (!compensator || !y_plus || !y_minus) {
        return;
    }

    // Calculate magnitude for distortion detection
    float magnitude = sqrtf((*y_plus) * (*y_plus) + (*y_minus) * (*y_minus));
    
    // Apply distortion correction based on magnitude
    float correction_factor = 1.0f;
    if (magnitude > DISTORTION_THRESHOLD) {
        // Reduce distortion at high magnitudes
        correction_factor = 1.0f / (1.0f + (magnitude - DISTORTION_THRESHOLD) * compensator->params.distortion_factor);
    }

    // Apply adaptive correction factor
    correction_factor *= compensator->distortion_correction_factor;

    // Apply correction to both channels
    *y_plus *= correction_factor;
    *y_minus *= correction_factor;

    // Apply anti-clipping
    *y_plus = fmaxf(-1.0f, fminf(1.0f, *y_plus));
    *y_minus = fmaxf(-1.0f, fminf(1.0f, *y_minus));
}

/**
 * @brief Get current delay compensation status
 */
bool delay_compensator_get_status(const delay_compensator_t* compensator, delay_status_t* status) {
    if (!compensator || !compensator->is_initialized || !status) {
        return false;
    }

    status->delay_ms = compensator->params.delay_ms;
    status->delay_samples = compensator->delay_samples;
    status->buffer_ready = compensator->buffer_ready;
    status->adaptive_factor = compensator->adaptive_factor;
    status->phase_error_accumulator = compensator->phase_error_accumulator;
    status->distortion_correction_factor = compensator->distortion_correction_factor;
    
    // Calculate current buffer fill level
    if (compensator->write_index >= compensator->read_index) {
        status->buffer_fill = compensator->write_index - compensator->read_index;
    } else {
        status->buffer_fill = compensator->delay_samples - compensator->read_index + compensator->write_index;
    }
    
    status->buffer_fill_percentage = (float)status->buffer_fill / compensator->delay_samples * 100.0f;

    return true;
}

/**
 * @brief Update delay compensation parameters
 */
bool delay_compensator_update_params(delay_compensator_t* compensator, const delay_params_t* params) {
    if (!compensator || !compensator->is_initialized || !params) {
        return false;
    }

    if (!validate_delay_parameters(params)) {
        return false;
    }

    // Store old delay samples
    size_t old_delay_samples = compensator->delay_samples;
    
    // Update parameters
    compensator->params = *params;
    
    // Calculate new delay samples
    size_t new_delay_samples = (size_t)(params->delay_ms / 1000.0f * params->sample_rate);
    
    // Clamp delay samples
    if (new_delay_samples < MIN_DELAY_SAMPLES) {
        new_delay_samples = MIN_DELAY_SAMPLES;
    } else if (new_delay_samples > MAX_DELAY_SAMPLES) {
        new_delay_samples = MAX_DELAY_SAMPLES;
    }

    // Reallocate buffers if delay changed
    if (new_delay_samples != old_delay_samples) {
        // Reallocate buffers
        float* new_y_plus = (float*)realloc(compensator->y_plus_buffer, new_delay_samples * sizeof(float));
        float* new_y_minus = (float*)realloc(compensator->y_minus_buffer, new_delay_samples * sizeof(float));
        float* new_phase = (float*)realloc(compensator->phase_buffer, new_delay_samples * sizeof(float));

        if (!new_y_plus || !new_y_minus || !new_phase) {
            return false;
        }

        compensator->y_plus_buffer = new_y_plus;
        compensator->y_minus_buffer = new_y_minus;
        compensator->phase_buffer = new_phase;
        compensator->delay_samples = new_delay_samples;

        // Reset buffer state
        compensator->write_index = 0;
        compensator->read_index = 0;
        compensator->buffer_ready = false;
    }

    return true;
}

/**
 * @brief Reset delay compensator state
 */
bool delay_compensator_reset(delay_compensator_t* compensator) {
    if (!compensator || !compensator->is_initialized) {
        return false;
    }

    // Clear buffers
    memset(compensator->y_plus_buffer, 0, compensator->delay_samples * sizeof(float));
    memset(compensator->y_minus_buffer, 0, compensator->delay_samples * sizeof(float));
    memset(compensator->phase_buffer, 0, compensator->delay_samples * sizeof(float));

    // Reset indices
    compensator->write_index = 0;
    compensator->read_index = 0;
    compensator->buffer_ready = false;

    // Reset adaptive parameters
    compensator->phase_error_accumulator = 0.0f;
    compensator->distortion_correction_factor = 1.0f;

    return true;
}

/**
 * @brief Create default delay parameters
 */
void delay_params_default(delay_params_t* params) {
    if (!params) {
        return;
    }

    params->delay_ms = 3.0f;
    params->sample_rate = 48000.0f;
    params->distortion_factor = 0.2f;
    params->adaptive_factor = 0.1f;
    params->enable_adaptive_correction = true;
    params->enable_phase_alignment = true;
}

/**
 * @brief Create delay parameters optimized for 3D spatial audio
 */
void delay_params_3d_spatial(delay_params_t* params) {
    if (!params) {
        return;
    }

    params->delay_ms = 2.5f;  // Reduced delay for better spatial accuracy
    params->sample_rate = 48000.0f;
    params->distortion_factor = 0.15f;  // Less aggressive distortion correction
    params->adaptive_factor = 0.05f;  // Slower adaptation for stability
    params->enable_adaptive_correction = true;
    params->enable_phase_alignment = true;
}

// Private helper functions

/**
 * @brief Calculate phase error between current and expected phase
 */
static float calculate_phase_error(float y_plus, float y_minus, float expected_phase) {
    float current_phase = atan2f(y_minus, y_plus);
    float error = current_phase - expected_phase;
    
    // Wrap phase error to [-π, π]
    while (error > M_PI) {
        error -= 2.0f * M_PI;
    }
    while (error < -M_PI) {
        error += 2.0f * M_PI;
    }
    
    return error;
}

/**
 * @brief Apply phase correction to reduce Y+ and Y- distortion
 */
static void apply_phase_correction(delay_compensator_t* compensator, float* y_plus, float* y_minus) {
    if (!compensator->params.enable_phase_alignment) {
        return;
    }

    // Calculate current phase
    float current_phase = atan2f(*y_minus, *y_plus);
    
    // Apply phase correction based on accumulated error
    float phase_correction = compensator->phase_error_accumulator * compensator->adaptive_factor;
    float corrected_phase = current_phase + phase_correction;
    
    // Maintain magnitude while correcting phase
    float magnitude = sqrtf((*y_plus) * (*y_plus) + (*y_minus) * (*y_minus));
    
    *y_plus = magnitude * cosf(corrected_phase);
    *y_minus = magnitude * sinf(corrected_phase);
}

/**
 * @brief Update adaptive parameters based on phase error
 */
static void update_adaptive_parameters(delay_compensator_t* compensator, float error) {
    // Accumulate phase error with exponential weighting
    compensator->phase_error_accumulator = compensator->phase_error_accumulator * 0.9f + error * 0.1f;
    
    // Update distortion correction factor
    float error_magnitude = fabsf(error);
    if (error_magnitude > PHASE_ALIGNMENT_PRECISION) {
        // Increase correction factor when error is high
        compensator->distortion_correction_factor = fminf(1.5f, 
            compensator->distortion_correction_factor * (1.0f + error_magnitude * 0.1f));
    } else {
        // Gradually return to normal when error is low
        compensator->distortion_correction_factor = fmaxf(1.0f, 
            compensator->distortion_correction_factor * 0.99f);
    }
}

/**
 * @brief Validate delay parameters
 */
static bool validate_delay_parameters(const delay_params_t* params) {
    if (!params) {
        return false;
    }

    if (params->delay_ms < 0.1f || params->delay_ms > 100.0f) {
        return false;
    }

    if (params->sample_rate < 8000.0f || params->sample_rate > 192000.0f) {
        return false;
    }

    if (params->distortion_factor < 0.0f || params->distortion_factor > 1.0f) {
        return false;
    }

    if (params->adaptive_factor < 0.0f || params->adaptive_factor > 1.0f) {
        return false;
    }

    return true;
}
