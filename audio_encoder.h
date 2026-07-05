/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#ifndef AUDIO_ENCODER_H
#define AUDIO_ENCODER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Audio format enumeration
typedef enum {
    AUDIO_FORMAT_F32 = 0,
    AUDIO_FORMAT_F64,
    AUDIO_FORMAT_S16,
    AUDIO_FORMAT_S24,
    AUDIO_FORMAT_S32,
    AUDIO_FORMAT_UNKNOWN
} audio_format_t;

// 2D Plane configuration structure
typedef struct {
    uint32_t sample_rate;
    uint32_t channels;
    size_t buffer_size;
    float x_plane_range;      // X plane range (-3 to 3 as shown in diagram)
    float y_plane_range;      // Y plane range for distortion correction
    float delay_compensation_ms;
    float distortion_factor;  // Additional distortion correction factor
} plane_2d_config_t;

// Delay compensation buffer structure
typedef struct {
    float* y_plus_buffer;
    float* y_minus_buffer;
    size_t buffer_capacity;
    size_t buffer_head;
    size_t buffer_tail;
    size_t compensation_samples;
    bool is_ready;
} delay_buffer_t;

// 2D Plane generator structure
typedef struct {
    plane_2d_config_t config;
    delay_buffer_t delay_buffer;
    float phase_accumulator;
    float x_phase_offset;
    float y_phase_offset;
} plane_2d_generator_t;

// Audio encoder structure
typedef struct {
    plane_2d_generator_t plane_generator;
    float* input_buffer;
    float* output_buffer;
    audio_format_t current_format;
    size_t input_buffer_size;
    size_t output_buffer_size;
    bool is_initialized;
} audio_encoder_t;

// Delay status structure
typedef struct {
    float compensation_ms;
    size_t buffer_length;
    bool is_ready;
    float current_delay_ms;
} delay_status_t;

// Audio sample structure for 2D plane processing
typedef struct {
    float x_component;    // X plane component
    float y_plus;         // Y+ component
    float y_minus;        // Y- component
    float magnitude;      // Combined magnitude
    float phase;          // Combined phase
} audio_sample_2d_t;

// Function prototypes

/**
 * @brief Initialize audio encoder with 2D plane configuration
 * @param encoder Pointer to encoder structure
 * @param config 2D plane configuration
 * @return true on success, false on failure
 */
bool audio_encoder_init(audio_encoder_t* encoder, const plane_2d_config_t* config);

/**
 * @brief Cleanup audio encoder resources
 * @param encoder Pointer to encoder structure
 */
void audio_encoder_cleanup(audio_encoder_t* encoder);

/**
 * @brief Encode audio with 2D plane generation and delay compensation
 * @param encoder Pointer to encoder structure
 * @param input_samples Input audio samples (interleaved)
 * @param input_count Number of input samples
 * @param output_samples Output buffer for processed samples
 * @param output_capacity Capacity of output buffer
 * @return Number of output samples on success, 0 on failure
 */
size_t audio_encoder_encode_with_plane(
    audio_encoder_t* encoder,
    const float* input_samples,
    size_t input_count,
    float* output_samples,
    size_t output_capacity
);

/**
 * @brief Process single sample with 2D plane generation
 * @param generator Pointer to plane generator
 * @param x_position X position on plane
 * @param y_position Y position on plane
 * @param sample Output sample structure
 * @return true on success, false on failure
 */
bool plane_generator_process_sample(
    plane_2d_generator_t* generator,
    float x_position,
    float y_position,
    audio_sample_2d_t* sample
);

/**
 * @brief Initialize delay buffer for Y+ and Y- compensation
 * @param buffer Pointer to delay buffer structure
 * @param compensation_samples Number of samples to compensate
 * @return true on success, false on failure
 */
bool delay_buffer_init(delay_buffer_t* buffer, size_t compensation_samples);

/**
 * @brief Push samples into delay buffer
 * @param buffer Pointer to delay buffer structure
 * @param y_plus Y+ sample value
 * @param y_minus Y- sample value
 * @return true on success, false on failure
 */
bool delay_buffer_push(delay_buffer_t* buffer, float y_plus, float y_minus);

/**
 * @brief Get compensated samples from delay buffer
 * @param buffer Pointer to delay buffer structure
 * @param y_plus Pointer to store compensated Y+ sample
 * @param y_minus Pointer to store compensated Y- sample
 * @return true if samples available, false if buffer not ready
 */
bool delay_buffer_get_compensated(
    const delay_buffer_t* buffer,
    float* y_plus,
    float* y_minus
);

/**
 * @brief Apply distortion correction for Y+ and Y- channels
 * @param y_sample Y channel sample
 * @param is_y_plus true for Y+ channel, false for Y- channel
 * @param distortion_factor Distortion correction factor
 * @return Corrected sample value
 */
float apply_y_distortion_correction(
    float y_sample,
    bool is_y_plus,
    float distortion_factor
);

/**
 * @brief Convert audio samples to different format
 * @param input_samples Input samples in F32 format
 * @param input_count Number of input samples
 * @param output_buffer Output buffer
 * @param output_capacity Output buffer capacity
 * @param format Target format
 * @return Number of bytes written on success, 0 on failure
 */
size_t convert_audio_format(
    const float* input_samples,
    size_t input_count,
    uint8_t* output_buffer,
    size_t output_capacity,
    audio_format_t format
);

/**
 * @brief Get current delay compensation status
 * @param encoder Pointer to encoder structure
 * @param status Pointer to status structure
 * @return true on success, false on failure
 */
bool audio_encoder_get_delay_status(
    const audio_encoder_t* encoder,
    delay_status_t* status
);

/**
 * @brief Update delay compensation value
 * @param encoder Pointer to encoder structure
 * @param compensation_ms New compensation value in milliseconds
 * @return true on success, false on failure
 */
bool audio_encoder_update_delay_compensation(
    audio_encoder_t* encoder,
    float compensation_ms
);

/**
 * @brief Create default 2D plane configuration
 * @param config Pointer to configuration structure
 */
void plane_2d_config_default(plane_2d_config_t* config);

/**
 * @brief Create configuration optimized for 3D spatial audio
 * @param config Pointer to configuration structure
 */
void plane_2d_config_3d_spatial(plane_2d_config_t* config);

/**
 * @brief Validate audio encoder state
 * @param encoder Pointer to encoder structure
 * @return true if encoder is valid and ready, false otherwise
 */
bool audio_encoder_is_valid(const audio_encoder_t* encoder);

/**
 * @brief Reset encoder state
 * @param encoder Pointer to encoder structure
 * @return true on success, false on failure
 */
bool audio_encoder_reset(audio_encoder_t* encoder);

/**
 * @brief Calculate processing delay in samples
 * @param encoder Pointer to encoder structure
 * @return Processing delay in samples
 */
size_t audio_encoder_get_processing_delay_samples(const audio_encoder_t* encoder);

/**
 * @brief Calculate processing delay in milliseconds
 * @param encoder Pointer to encoder structure
 * @return Processing delay in milliseconds
 */
float audio_encoder_get_processing_delay_ms(const audio_encoder_t* encoder);

// Constants
#define AUDIO_ENCODER_MAX_CHANNELS 8
#define AUDIO_ENCODER_MAX_SAMPLE_RATE 192000
#define AUDIO_ENCODER_MIN_SAMPLE_RATE 8000
#define AUDIO_ENCODER_DEFAULT_BUFFER_SIZE 1024
#define AUDIO_ENCODER_MAX_DELAY_MS 100.0f
#define AUDIO_ENCODER_MIN_DELAY_MS 0.1f

// Error codes
typedef enum {
    AUDIO_ENCODER_SUCCESS = 0,
    AUDIO_ENCODER_ERROR_INVALID_PARAM,
    AUDIO_ENCODER_ERROR_NOT_INITIALIZED,
    AUDIO_ENCODER_ERROR_BUFFER_OVERFLOW,
    AUDIO_ENCODER_ERROR_UNSUPPORTED_FORMAT,
    AUDIO_ENCODER_ERROR_MEMORY_ALLOCATION,
    AUDIO_ENCODER_ERROR_PROCESSING
} audio_encoder_error_t;

// Error handling
const char* audio_encoder_error_string(audio_encoder_error_t error);

#ifdef __cplusplus
}
#endif

#endif // AUDIO_ENCODER_H
