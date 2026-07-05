/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

/**
 * @file audio_pipeline_integration.c
 * @brief Integrated Audio Processing Pipeline with Delay Correction for 3D Spatial Audio
 * 
 * This module integrates the Rust decoder, C encoder, delay compensation, and 2D plane
 * generation to create a complete audio processing pipeline that addresses the Y+ and Y-
 * distortion issues in the X plane during 2D plane generation.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#include "audio_pipeline_integration.h"
#include "audio_encoder.h"
#include "plane_2d_generator.h"
#include "delay_compensation.h"

// Internal constants
#define PIPELINE_MAX_BUFFER_SIZE 8192
#define PIPELINE_MIN_BUFFER_SIZE 64
#define PIPELINE_DEFAULT_SAMPLE_RATE 48000
#define PIPELINE_DEFAULT_CHANNELS 2
#define PIPELINE_PROCESSING_THREADS 4

// Internal helper functions
static bool validate_pipeline_config(const pipeline_config_t* config);
static void apply_crossfade(float* output, const float* input1, const float* input2, 
                           size_t length, float fade_factor);
static void process_audio_chunk(audio_pipeline_t* pipeline, const float* input, 
                               float* output, size_t chunk_size);
static bool initialize_processing_buffers(audio_pipeline_t* pipeline);
static void cleanup_processing_buffers(audio_pipeline_t* pipeline);

/**
 * @brief Initialize integrated audio processing pipeline
 */
bool audio_pipeline_init(audio_pipeline_t* pipeline, const pipeline_config_t* config) {
    if (!pipeline || !config) {
        return false;
    }

    if (!validate_pipeline_config(config)) {
        return false;
    }

    // Initialize structure
    memset(pipeline, 0, sizeof(audio_pipeline_t));
    pipeline->config = *config;

    // Initialize 2D plane generator
    plane_2d_config_t plane_config;
    plane_2d_config_diagram_optimized(&plane_config);
    plane_config.sample_rate = config->sample_rate;
    plane_config.channels = config->channels;
    plane_config.delay_compensation_ms = config->delay_compensation_ms;

    if (!plane_2d_generator_init(&pipeline->plane_generator, &plane_config)) {
        audio_pipeline_cleanup(pipeline);
        return false;
    }

    // Initialize audio encoder
    plane_2d_config_t encoder_config;
    plane_2d_config_3d_spatial(&encoder_config);
    encoder_config.sample_rate = config->sample_rate;
    encoder_config.channels = config->channels;
    encoder_config.delay_compensation_ms = config->delay_compensation_ms;

    if (!audio_encoder_init(&pipeline->audio_encoder, &encoder_config)) {
        audio_pipeline_cleanup(pipeline);
        return false;
    }

    // Initialize processing buffers
    pipeline->buffer_size = config->buffer_size;
    if (!initialize_processing_buffers(pipeline)) {
        audio_pipeline_cleanup(pipeline);
        return false;
    }

    // Initialize processing state
    pipeline->processing_enabled = true;
    pipeline->delay_compensation_enabled = config->enable_delay_compensation;
    pipeline->x_plane_processing_enabled = config->enable_x_plane_processing;
    pipeline->y_channel_correction_enabled = config->enable_y_channel_correction;

    // Initialize performance counters
    pipeline->samples_processed = 0;
    pipeline->frames_processed = 0;
    pipeline->processing_time_us = 0;

    pipeline->is_initialized = true;
    return true;
}

/**
 * @brief Cleanup audio processing pipeline resources
 */
void audio_pipeline_cleanup(audio_pipeline_t* pipeline) {
    if (!pipeline) {
        return;
    }

    cleanup_processing_buffers(pipeline);
    plane_2d_generator_cleanup(&pipeline->plane_generator);
    audio_encoder_cleanup(&pipeline->audio_encoder);
    memset(pipeline, 0, sizeof(audio_pipeline_t));
}

/**
 * @brief Process audio through integrated pipeline with delay correction
 */
bool audio_pipeline_process(
    audio_pipeline_t* pipeline,
    const float* input_samples,
    size_t input_count,
    float* output_samples,
    size_t output_capacity
) {
    if (!pipeline || !pipeline->is_initialized || !input_samples || !output_samples) {
        return false;
    }

    if (!pipeline->processing_enabled) {
        // Pass through if processing disabled
        size_t copy_count = input_count < output_capacity ? input_count : output_capacity;
        memcpy(output_samples, input_samples, copy_count * sizeof(float));
        return true;
    }

    // Check output capacity
    size_t required_capacity = input_count * 3; // X, Y+, Y- for each input
    if (output_capacity < required_capacity) {
        return false;
    }

    // Process in chunks to avoid buffer overflow
    size_t chunk_size = pipeline->buffer_size;
    size_t input_offset = 0;
    size_t output_offset = 0;

    while (input_offset < input_count) {
        size_t current_chunk = (input_count - input_offset) < chunk_size ? 
                              (input_count - input_offset) : chunk_size;

        // Process current chunk
        process_audio_chunk(pipeline, &input_samples[input_offset], 
                          &output_samples[output_offset], current_chunk);

        input_offset += current_chunk;
        output_offset += current_chunk * 3; // X, Y+, Y-
    }

    // Update performance counters
    pipeline->samples_processed += input_count;
    pipeline->frames_processed++;

    return true;
}

/**
 * @brief Process single sample through pipeline
 */
bool audio_pipeline_process_sample(audio_pipeline_t* pipeline, float input_sample, 
                                  audio_sample_2d_t* output_sample) {
    if (!pipeline || !pipeline->is_initialized || !output_sample) {
        return false;
    }

    if (!pipeline->processing_enabled) {
        // Return zero samples if processing disabled
        memset(output_sample, 0, sizeof(audio_sample_2d_t));
        return true;
    }

    // Calculate position based on sample value
    float x_position = (pipeline->samples_processed % pipeline->buffer_size) / 
                      (float)pipeline->buffer_size * 2.0f * pipeline->plane_generator.config.x_plane_range - 
                      pipeline->plane_generator.config.x_plane_range;
    float y_position = input_sample * pipeline->plane_generator.config.y_plane_range;

    // Generate 2D plane sample
    bool success = plane_2d_generator_process(&pipeline->plane_generator, x_position, y_position, output_sample);

    if (success) {
        pipeline->samples_processed++;
    }

    return success;
}

/**
 * @brief Update pipeline configuration
 */
bool audio_pipeline_update_config(audio_pipeline_t* pipeline, const pipeline_config_t* config) {
    if (!pipeline || !pipeline->is_initialized || !config) {
        return false;
    }

    if (!validate_pipeline_config(config)) {
        return false;
    }

    // Update configuration
    pipeline->config = *config;

    // Update plane generator configuration
    plane_2d_config_t plane_config;
    plane_config.sample_rate = config->sample_rate;
    plane_config.channels = config->channels;
    plane_config.delay_compensation_ms = config->delay_compensation_ms;
    plane_config.enable_x_plane_processing = config->enable_x_plane_processing;
    plane_config.enable_y_channel_correction = config->enable_y_channel_correction;

    if (!plane_2d_generator_set_plane_coefficients(&pipeline->plane_generator, &plane_config.plane_coeffs)) {
        return false;
    }

    // Update audio encoder configuration
    plane_2d_config_t encoder_config;
    encoder_config.sample_rate = config->sample_rate;
    encoder_config.channels = config->channels;
    encoder_config.delay_compensation_ms = config->delay_compensation_ms;

    if (!audio_encoder_update_delay_compensation(&pipeline->audio_encoder, config->delay_compensation_ms)) {
        return false;
    }

    // Reallocate buffers if size changed
    if (config->buffer_size != pipeline->buffer_size) {
        cleanup_processing_buffers(pipeline);
        pipeline->buffer_size = config->buffer_size;
        if (!initialize_processing_buffers(pipeline)) {
            return false;
        }
    }

    // Update processing flags
    pipeline->delay_compensation_enabled = config->enable_delay_compensation;
    pipeline->x_plane_processing_enabled = config->enable_x_plane_processing;
    pipeline->y_channel_correction_enabled = config->enable_y_channel_correction;

    return true;
}

/**
 * @brief Get pipeline status
 */
bool audio_pipeline_get_status(const audio_pipeline_t* pipeline, pipeline_status_t* status) {
    if (!pipeline || !pipeline->is_initialized || !status) {
        return false;
    }

    status->processing_enabled = pipeline->processing_enabled;
    status->delay_compensation_enabled = pipeline->delay_compensation_enabled;
    status->x_plane_processing_enabled = pipeline->x_plane_processing_enabled;
    status->y_channel_correction_enabled = pipeline->y_channel_correction_enabled;
    status->samples_processed = pipeline->samples_processed;
    status->frames_processed = pipeline->frames_processed;
    status->processing_time_us = pipeline->processing_time_us;

    // Get plane generator status
    return plane_2d_generator_get_status(&pipeline->plane_generator, &status->plane_status);
}

/**
 * @brief Reset pipeline state
 */
bool audio_pipeline_reset(audio_pipeline_t* pipeline) {
    if (!pipeline || !pipeline->is_initialized) {
        return false;
    }

    // Reset plane generator
    if (!plane_2d_generator_reset(&pipeline->plane_generator)) {
        return false;
    }

    // Reset audio encoder
    if (!audio_encoder_reset(&pipeline->audio_encoder)) {
        return false;
    }

    // Clear processing buffers
    if (pipeline->input_buffer) {
        memset(pipeline->input_buffer, 0, pipeline->buffer_size * sizeof(float));
    }
    if (pipeline->output_buffer) {
        memset(pipeline->output_buffer, 0, pipeline->buffer_size * 3 * sizeof(float));
    }
    if (pipeline->temp_buffer) {
        memset(pipeline->temp_buffer, 0, pipeline->buffer_size * sizeof(float));
    }

    // Reset performance counters
    pipeline->samples_processed = 0;
    pipeline->frames_processed = 0;
    pipeline->processing_time_us = 0;

    return true;
}

/**
 * @brief Enable/disable processing
 */
void audio_pipeline_set_processing_enabled(audio_pipeline_t* pipeline, bool enabled) {
    if (pipeline && pipeline->is_initialized) {
        pipeline->processing_enabled = enabled;
        plane_2d_generator_set_processing_enabled(&pipeline->plane_generator, enabled);
    }
}

/**
 * @brief Add calibration point for plane generation
 */
bool audio_pipeline_add_calibration_point(audio_pipeline_t* pipeline, float x, float y, float value) {
    if (!pipeline || !pipeline->is_initialized) {
        return false;
    }

    return plane_2d_generator_add_point(&pipeline->plane_generator, x, y, value);
}

/**
 * @brief Calculate plane from calibration points
 */
bool audio_pipeline_calibrate_plane(audio_pipeline_t* pipeline) {
    if (!pipeline || !pipeline->is_initialized) {
        return false;
    }

    return plane_2d_generator_calculate_plane(&pipeline->plane_generator);
}

/**
 * @brief Create default pipeline configuration
 */
void pipeline_config_default(pipeline_config_t* config) {
    if (!config) {
        return;
    }

    config->sample_rate = PIPELINE_DEFAULT_SAMPLE_RATE;
    config->channels = PIPELINE_DEFAULT_CHANNELS;
    config->buffer_size = 1024;
    config->delay_compensation_ms = 3.0f;
    config->enable_delay_compensation = true;
    config->enable_x_plane_processing = true;
    config->enable_y_channel_correction = true;
    config->enable_adaptive_processing = false;
}

/**
 * @brief Create configuration optimized for diagram-based processing
 */
void pipeline_config_diagram_optimized(pipeline_config_t* config) {
    if (!config) {
        return;
    }

    config->sample_rate = 48000;
    config->channels = 2;
    config->buffer_size = 2048;
    config->delay_compensation_ms = 2.0f;  // Reduced for diagram accuracy
    config->enable_delay_compensation = true;
    config->enable_x_plane_processing = true;
    config->enable_y_channel_correction = true;
    config->enable_adaptive_processing = true;
}

// Private helper functions

/**
 * @brief Validate pipeline configuration
 */
static bool validate_pipeline_config(const pipeline_config_t* config) {
    if (!config) {
        return false;
    }

    if (config->sample_rate < 8000 || config->sample_rate > 192000) {
        return false;
    }

    if (config->channels == 0 || config->channels > 8) {
        return false;
    }

    if (config->buffer_size < PIPELINE_MIN_BUFFER_SIZE || config->buffer_size > PIPELINE_MAX_BUFFER_SIZE) {
        return false;
    }

    if (config->delay_compensation_ms < 0.1f || config->delay_compensation_ms > 100.0f) {
        return false;
    }

    return true;
}

/**
 * @brief Apply crossfade between two audio signals
 */
static void apply_crossfade(float* output, const float* input1, const float* input2, 
                           size_t length, float fade_factor) {
    if (!output || !input1 || !input2) {
        return;
    }

    for (size_t i = 0; i < length; i++) {
        output[i] = input1[i] * (1.0f - fade_factor) + input2[i] * fade_factor;
    }
}

/**
 * @brief Process audio chunk through pipeline
 */
static void process_audio_chunk(audio_pipeline_t* pipeline, const float* input, 
                               float* output, size_t chunk_size) {
    if (!pipeline || !input || !output) {
        return;
    }

    for (size_t i = 0; i < chunk_size; i++) {
        audio_sample_2d_t sample;
        
        if (audio_pipeline_process_sample(pipeline, input[i], &sample)) {
            // Store processed samples
            output[i * 3] = sample.x_component;
            output[i * 3 + 1] = sample.y_plus;
            output[i * 3 + 2] = sample.y_minus;
        } else {
            // Zero output on failure
            output[i * 3] = 0.0f;
            output[i * 3 + 1] = 0.0f;
            output[i * 3 + 2] = 0.0f;
        }
    }
}

/**
 * @brief Initialize processing buffers
 */
static bool initialize_processing_buffers(audio_pipeline_t* pipeline) {
    if (!pipeline) {
        return false;
    }

    size_t buffer_size = pipeline->buffer_size;

    pipeline->input_buffer = (float*)malloc(buffer_size * sizeof(float));
    pipeline->output_buffer = (float*)malloc(buffer_size * 3 * sizeof(float));
    pipeline->temp_buffer = (float*)malloc(buffer_size * sizeof(float));

    if (!pipeline->input_buffer || !pipeline->output_buffer || !pipeline->temp_buffer) {
        cleanup_processing_buffers(pipeline);
        return false;
    }

    // Initialize buffers to zero
    memset(pipeline->input_buffer, 0, buffer_size * sizeof(float));
    memset(pipeline->output_buffer, 0, buffer_size * 3 * sizeof(float));
    memset(pipeline->temp_buffer, 0, buffer_size * sizeof(float));

    return true;
}

/**
 * @brief Cleanup processing buffers
 */
static void cleanup_processing_buffers(audio_pipeline_t* pipeline) {
    if (!pipeline) {
        return;
    }

    if (pipeline->input_buffer) {
        free(pipeline->input_buffer);
        pipeline->input_buffer = NULL;
    }

    if (pipeline->output_buffer) {
        free(pipeline->output_buffer);
        pipeline->output_buffer = NULL;
    }

    if (pipeline->temp_buffer) {
        free(pipeline->temp_buffer);
        pipeline->temp_buffer = NULL;
    }
}
