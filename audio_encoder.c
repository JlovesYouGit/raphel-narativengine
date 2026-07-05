/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#include "audio_encoder.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdio.h>

// Private helper functions
static float wrap_phase(float phase);
static float calculate_distortion_factor(float y_position, float range);
static bool allocate_buffers(audio_encoder_t* encoder);
static void free_buffers(audio_encoder_t* encoder);

// Implementation

bool audio_encoder_init(audio_encoder_t* encoder, const plane_2d_config_t* config) {
    if (!encoder || !config) {
        return false;
    }

    // Initialize structure
    memset(encoder, 0, sizeof(audio_encoder_t));
    
    // Copy configuration
    encoder->plane_generator.config = *config;
    
    // Initialize delay buffer
    size_t compensation_samples = (size_t)(config->delay_compensation_ms / 1000.0f * config->sample_rate);
    if (!delay_buffer_init(&encoder->plane_generator.delay_buffer, compensation_samples)) {
        return false;
    }

    // Initialize phase accumulator
    encoder->plane_generator.phase_accumulator = 0.0f;
    encoder->plane_generator.x_phase_offset = 0.0f;
    encoder->plane_generator.y_phase_offset = 0.0f;

    // Allocate buffers
    if (!allocate_buffers(encoder)) {
        audio_encoder_cleanup(encoder);
        return false;
    }

    encoder->is_initialized = true;
    return true;
}

void audio_encoder_cleanup(audio_encoder_t* encoder) {
    if (!encoder) {
        return;
    }

    free_buffers(encoder);
    delay_buffer_cleanup(&encoder->plane_generator.delay_buffer);
    memset(encoder, 0, sizeof(audio_encoder_t));
}

size_t audio_encoder_encode_with_plane(
    audio_encoder_t* encoder,
    const float* input_samples,
    size_t input_count,
    float* output_samples,
    size_t output_capacity
) {
    if (!encoder || !encoder->is_initialized || !input_samples || !output_samples) {
        return 0;
    }

    size_t required_capacity = input_count * 3; // X, Y+, Y- for each input
    if (output_capacity < required_capacity) {
        return 0;
    }

    size_t output_index = 0;
    
    for (size_t i = 0; i < input_count; i++) {
        // Calculate position based on sample index and value
        float x_position = ((float)i / input_count - 0.5f) * 2.0f * encoder->plane_generator.config.x_plane_range;
        float y_position = input_samples[i] * encoder->plane_generator.config.y_plane_range;

        // Process sample with 2D plane generation
        audio_sample_2d_t sample;
        if (!plane_generator_process_sample(&encoder->plane_generator, x_position, y_position, &sample)) {
            return 0;
        }

        // Store processed samples
        output_samples[output_index++] = sample.x_component;
        output_samples[output_index++] = sample.y_plus;
        output_samples[output_index++] = sample.y_minus;
    }

    return output_index;
}

bool plane_generator_process_sample(
    plane_2d_generator_t* generator,
    float x_position,
    float y_position,
    audio_sample_2d_t* sample
) {
    if (!generator || !sample) {
        return false;
    }

    // Normalize positions to -1 to 1 range
    float x_norm = fmaxf(-1.0f, fminf(1.0f, x_position / generator->config.x_plane_range));
    float y_norm = fmaxf(-1.0f, fminf(1.0f, y_position / generator->config.y_plane_range));

    // Generate X plane component (primary signal)
    float x_phase = generator->phase_accumulator + x_norm * M_PI;
    sample->x_component = sinf(x_phase);

    // Generate Y+ and Y- components with distortion correction
    float y_phase_offset = y_norm * M_PI / 2.0f;  // 90-degree phase shift for Y components
    float y_plus_phase = generator->phase_accumulator + y_phase_offset;
    float y_minus_phase = generator->phase_accumulator - y_phase_offset;

    // Apply distortion correction for Y+ and Y-
    float distortion_factor = calculate_distortion_factor(y_norm, generator->config.y_plane_range);
    float y_plus = sinf(y_plus_phase) * distortion_factor;
    float y_minus = sinf(y_minus_phase) * distortion_factor;

    // Apply delay compensation
    delay_buffer_push(&generator->delay_buffer, y_plus, y_minus);
    
    float compensated_y_plus, compensated_y_minus;
    if (delay_buffer_get_compensated(&generator->delay_buffer, &compensated_y_plus, &compensated_y_minus)) {
        sample->y_plus = apply_y_distortion_correction(compensated_y_plus, true, generator->config.distortion_factor);
        sample->y_minus = apply_y_distortion_correction(compensated_y_minus, false, generator->config.distortion_factor);
    } else {
        // Return uncompensated if buffer not ready
        sample->y_plus = apply_y_distortion_correction(y_plus, true, generator->config.distortion_factor);
        sample->y_minus = apply_y_distortion_correction(y_minus, false, generator->config.distortion_factor);
    }

    // Calculate combined magnitude and phase
    sample->magnitude = sqrtf(sample->x_component * sample->x_component + 
                              sample->y_plus * sample->y_plus + 
                              sample->y_minus * sample->y_minus);
    sample->phase = atan2f(sample->y_plus + sample->y_minus, sample->x_component);

    // Update phase accumulator
    generator->phase_accumulator += 2.0f * M_PI / (generator->config.sample_rate / 440.0f); // 440Hz reference
    generator->phase_accumulator = wrap_phase(generator->phase_accumulator);

    return true;
}

bool delay_buffer_init(delay_buffer_t* buffer, size_t compensation_samples) {
    if (!buffer || compensation_samples == 0) {
        return false;
    }

    buffer->buffer_capacity = compensation_samples * 2;
    buffer->compensation_samples = compensation_samples;
    buffer->buffer_head = 0;
    buffer->buffer_tail = 0;
    buffer->is_ready = false;

    // Allocate circular buffers
    buffer->y_plus_buffer = (float*)malloc(buffer->buffer_capacity * sizeof(float));
    buffer->y_minus_buffer = (float*)malloc(buffer->buffer_capacity * sizeof(float));

    if (!buffer->y_plus_buffer || !buffer->y_minus_buffer) {
        delay_buffer_cleanup(buffer);
        return false;
    }

    // Initialize buffers to zero
    memset(buffer->y_plus_buffer, 0, buffer->buffer_capacity * sizeof(float));
    memset(buffer->y_minus_buffer, 0, buffer->buffer_capacity * sizeof(float));

    return true;
}

void delay_buffer_cleanup(delay_buffer_t* buffer) {
    if (!buffer) {
        return;
    }

    if (buffer->y_plus_buffer) {
        free(buffer->y_plus_buffer);
        buffer->y_plus_buffer = NULL;
    }

    if (buffer->y_minus_buffer) {
        free(buffer->y_minus_buffer);
        buffer->y_minus_buffer = NULL;
    }

    memset(buffer, 0, sizeof(delay_buffer_t));
}

bool delay_buffer_push(delay_buffer_t* buffer, float y_plus, float y_minus) {
    if (!buffer || !buffer->y_plus_buffer || !buffer->y_minus_buffer) {
        return false;
    }

    // Store samples at head position
    buffer->y_plus_buffer[buffer->buffer_head] = y_plus;
    buffer->y_minus_buffer[buffer->buffer_head] = y_minus;

    // Update head position
    buffer->buffer_head = (buffer->buffer_head + 1) % buffer->buffer_capacity;

    // Update tail if buffer is full
    if ((buffer->buffer_head + 1) % buffer->buffer_capacity == buffer->buffer_tail) {
        buffer->buffer_tail = (buffer->buffer_tail + 1) % buffer->buffer_capacity;
    }

    // Mark as ready if we have enough samples
    size_t buffer_length = (buffer->buffer_head - buffer->buffer_tail + buffer->buffer_capacity) % buffer->buffer_capacity;
    buffer->is_ready = buffer_length >= buffer->compensation_samples;

    return true;
}

bool delay_buffer_get_compensated(
    const delay_buffer_t* buffer,
    float* y_plus,
    float* y_minus
) {
    if (!buffer || !y_plus || !y_minus || !buffer->is_ready) {
        return false;
    }

    // Calculate compensated position (compensation_samples behind head)
    size_t compensated_pos = (buffer->buffer_head - buffer->compensation_samples + buffer->buffer_capacity) % buffer->buffer_capacity;

    *y_plus = buffer->y_plus_buffer[compensated_pos];
    *y_minus = buffer->y_minus_buffer[compensated_pos];

    return true;
}

float apply_y_distortion_correction(
    float y_sample,
    bool is_y_plus,
    float distortion_factor
) {
    // Apply phase correction to reduce Y+ and Y- distortion
    float phase_correction = is_y_plus ? 1.0f : -1.0f;
    
    // Apply amplitude correction based on Y position
    float amplitude_correction = 1.0f - (fabsf(y_sample) * 0.1f);  // 10% correction at extremes
    
    // Apply distortion factor
    float corrected_sample = y_sample * phase_correction * amplitude_correction * distortion_factor;
    
    // Clamp to prevent overflow
    return fmaxf(-1.0f, fminf(1.0f, corrected_sample));
}

size_t convert_audio_format(
    const float* input_samples,
    size_t input_count,
    uint8_t* output_buffer,
    size_t output_capacity,
    audio_format_t format
) {
    if (!input_samples || !output_buffer) {
        return 0;
    }

    size_t bytes_per_sample;
    switch (format) {
        case AUDIO_FORMAT_F32:
            bytes_per_sample = 4;
            break;
        case AUDIO_FORMAT_F64:
            bytes_per_sample = 8;
            break;
        case AUDIO_FORMAT_S16:
            bytes_per_sample = 2;
            break;
        case AUDIO_FORMAT_S24:
            bytes_per_sample = 3;
            break;
        case AUDIO_FORMAT_S32:
            bytes_per_sample = 4;
            break;
        default:
            return 0;
    }

    size_t required_bytes = input_count * bytes_per_sample;
    if (output_capacity < required_bytes) {
        return 0;
    }

    switch (format) {
        case AUDIO_FORMAT_F32: {
            float* output = (float*)output_buffer;
            for (size_t i = 0; i < input_count; i++) {
                output[i] = input_samples[i];
            }
            break;
        }
        case AUDIO_FORMAT_F64: {
            double* output = (double*)output_buffer;
            for (size_t i = 0; i < input_count; i++) {
                output[i] = (double)input_samples[i];
            }
            break;
        }
        case AUDIO_FORMAT_S16: {
            int16_t* output = (int16_t*)output_buffer;
            for (size_t i = 0; i < input_count; i++) {
                output[i] = (int16_t)(input_samples[i] * 32767.0f);
            }
            break;
        }
        case AUDIO_FORMAT_S24: {
            for (size_t i = 0; i < input_count; i++) {
                int32_t sample = (int32_t)(input_samples[i] * 8388607.0f);
                output_buffer[i * 3] = (uint8_t)(sample & 0xFF);
                output_buffer[i * 3 + 1] = (uint8_t)((sample >> 8) & 0xFF);
                output_buffer[i * 3 + 2] = (uint8_t)((sample >> 16) & 0xFF);
            }
            break;
        }
        case AUDIO_FORMAT_S32: {
            int32_t* output = (int32_t*)output_buffer;
            for (size_t i = 0; i < input_count; i++) {
                output[i] = (int32_t)(input_samples[i] * 2147483647.0f);
            }
            break;
        }
        default:
            return 0;
    }

    return required_bytes;
}

bool audio_encoder_get_delay_status(
    const audio_encoder_t* encoder,
    delay_status_t* status
) {
    if (!encoder || !encoder->is_initialized || !status) {
        return false;
    }

    status->compensation_ms = encoder->plane_generator.config.delay_compensation_ms;
    status->buffer_length = (encoder->plane_generator.delay_buffer.buffer_head - 
                            encoder->plane_generator.delay_buffer.buffer_tail + 
                            encoder->plane_generator.delay_buffer.buffer_capacity) % 
                           encoder->plane_generator.delay_buffer.buffer_capacity;
    status->is_ready = encoder->plane_generator.delay_buffer.is_ready;
    status->current_delay_ms = (float)status->buffer_length / encoder->plane_generator.config.sample_rate * 1000.0f;

    return true;
}

bool audio_encoder_update_delay_compensation(
    audio_encoder_t* encoder,
    float compensation_ms
) {
    if (!encoder || !encoder->is_initialized) {
        return false;
    }

    // Clamp compensation value
    compensation_ms = fmaxf(AUDIO_ENCODER_MIN_DELAY_MS, fminf(AUDIO_ENCODER_MAX_DELAY_MS, compensation_ms));

    encoder->plane_generator.config.delay_compensation_ms = compensation_ms;
    
    // Reinitialize delay buffer with new compensation
    size_t compensation_samples = (size_t)(compensation_ms / 1000.0f * encoder->plane_generator.config.sample_rate);
    
    delay_buffer_cleanup(&encoder->plane_generator.delay_buffer);
    return delay_buffer_init(&encoder->plane_generator.delay_buffer, compensation_samples);
}

void plane_2d_config_default(plane_2d_config_t* config) {
    if (!config) {
        return;
    }

    config->sample_rate = 16000;
    config->channels = 2;
    config->buffer_size = AUDIO_ENCODER_DEFAULT_BUFFER_SIZE;
    config->x_plane_range = 3.0f;
    config->y_plane_range = 3.0f;
    config->delay_compensation_ms = 5.0f;
    config->distortion_factor = 1.0f;
}

void plane_2d_config_3d_spatial(plane_2d_config_t* config) {
    if (!config) {
        return;
    }

    config->sample_rate = 48000;
    config->channels = 2;
    config->buffer_size = 2048;
    config->x_plane_range = 3.0f;  // Match diagram X range
    config->y_plane_range = 3.0f;  // Match diagram Y range
    config->delay_compensation_ms = 3.0f;  // Reduced delay for better spatial accuracy
    config->distortion_factor = 0.95f;  // Slight reduction to prevent distortion
}

bool audio_encoder_is_valid(const audio_encoder_t* encoder) {
    if (!encoder || !encoder->is_initialized) {
        return false;
    }

    return encoder->input_buffer && encoder->output_buffer &&
           encoder->plane_generator.delay_buffer.y_plus_buffer &&
           encoder->plane_generator.delay_buffer.y_minus_buffer;
}

bool audio_encoder_reset(audio_encoder_t* encoder) {
    if (!encoder || !encoder->is_initialized) {
        return false;
    }

    // Reset phase accumulator
    encoder->plane_generator.phase_accumulator = 0.0f;
    encoder->plane_generator.x_phase_offset = 0.0f;
    encoder->plane_generator.y_phase_offset = 0.0f;

    // Reset delay buffer
    size_t compensation_samples = encoder->plane_generator.delay_buffer.compensation_samples;
    delay_buffer_cleanup(&encoder->plane_generator.delay_buffer);
    return delay_buffer_init(&encoder->plane_generator.delay_buffer, compensation_samples);
}

size_t audio_encoder_get_processing_delay_samples(const audio_encoder_t* encoder) {
    if (!encoder || !encoder->is_initialized) {
        return 0;
    }

    return encoder->plane_generator.delay_buffer.compensation_samples;
}

float audio_encoder_get_processing_delay_ms(const audio_encoder_t* encoder) {
    if (!encoder || !encoder->is_initialized) {
        return 0.0f;
    }

    return encoder->plane_generator.config.delay_compensation_ms;
}

const char* audio_encoder_error_string(audio_encoder_error_t error) {
    switch (error) {
        case AUDIO_ENCODER_SUCCESS:
            return "Success";
        case AUDIO_ENCODER_ERROR_INVALID_PARAM:
            return "Invalid parameter";
        case AUDIO_ENCODER_ERROR_NOT_INITIALIZED:
            return "Encoder not initialized";
        case AUDIO_ENCODER_ERROR_BUFFER_OVERFLOW:
            return "Buffer overflow";
        case AUDIO_ENCODER_ERROR_UNSUPPORTED_FORMAT:
            return "Unsupported audio format";
        case AUDIO_ENCODER_ERROR_MEMORY_ALLOCATION:
            return "Memory allocation failed";
        case AUDIO_ENCODER_ERROR_PROCESSING:
            return "Processing error";
        default:
            return "Unknown error";
    }
}

// Private helper functions

static float wrap_phase(float phase) {
    while (phase > 2.0f * M_PI) {
        phase -= 2.0f * M_PI;
    }
    while (phase < 0.0f) {
        phase += 2.0f * M_PI;
    }
    return phase;
}

static float calculate_distortion_factor(float y_position, float range) {
    // Calculate distortion factor based on Y position
    float normalized_y = fabsf(y_position / range);
    return 1.0f - (normalized_y * 0.2f);  // 20% reduction at extremes
}

static bool allocate_buffers(audio_encoder_t* encoder) {
    if (!encoder) {
        return false;
    }

    size_t input_size = encoder->plane_generator.config.buffer_size;
    size_t output_size = input_size * 3; // X, Y+, Y-

    encoder->input_buffer = (float*)malloc(input_size * sizeof(float));
    encoder->output_buffer = (float*)malloc(output_size * sizeof(float));

    if (!encoder->input_buffer || !encoder->output_buffer) {
        free_buffers(encoder);
        return false;
    }

    encoder->input_buffer_size = input_size;
    encoder->output_buffer_size = output_size;

    // Initialize buffers to zero
    memset(encoder->input_buffer, 0, input_size * sizeof(float));
    memset(encoder->output_buffer, 0, output_size * sizeof(float));

    return true;
}

static void free_buffers(audio_encoder_t* encoder) {
    if (!encoder) {
        return;
    }

    if (encoder->input_buffer) {
        free(encoder->input_buffer);
        encoder->input_buffer = NULL;
    }

    if (encoder->output_buffer) {
        free(encoder->output_buffer);
        encoder->output_buffer = NULL;
    }

    encoder->input_buffer_size = 0;
    encoder->output_buffer_size = 0;
}
