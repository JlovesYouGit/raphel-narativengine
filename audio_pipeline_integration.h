/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#ifndef AUDIO_PIPELINE_INTEGRATION_H
#define AUDIO_PIPELINE_INTEGRATION_H

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include "audio_encoder.h"
#include "plane_2d_generator.h"
#include "delay_compensation.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Audio processing pipeline configuration
 */
typedef struct {
    uint32_t sample_rate;                    // Audio sample rate
    uint32_t channels;                      // Number of audio channels
    size_t buffer_size;                      // Processing buffer size
    float delay_compensation_ms;             // Delay compensation for Y+ and Y-
    bool enable_delay_compensation;          // Enable delay compensation
    bool enable_x_plane_processing;          // Enable X plane processing
    bool enable_y_channel_correction;        // Enable Y channel correction
    bool enable_adaptive_processing;          // Enable adaptive processing
} pipeline_config_t;

/**
 * @brief Audio processing pipeline status
 */
typedef struct {
    bool processing_enabled;                // Processing enabled flag
    bool delay_compensation_enabled;         // Delay compensation enabled flag
    bool x_plane_processing_enabled;         // X plane processing enabled flag
    bool y_channel_correction_enabled;       // Y channel correction enabled flag
    uint64_t samples_processed;              // Total samples processed
    uint64_t frames_processed;               // Total frames processed
    uint64_t processing_time_us;             // Total processing time in microseconds
    plane_2d_status_t plane_status;          // Plane generator status
} pipeline_status_t;

/**
 * @brief Integrated audio processing pipeline structure
 */
typedef struct {
    pipeline_config_t config;                // Pipeline configuration
    plane_2d_generator_t plane_generator;     // 2D plane generator
    audio_encoder_t audio_encoder;            // Audio encoder
    float* input_buffer;                     // Input processing buffer
    float* output_buffer;                    // Output processing buffer
    float* temp_buffer;                      // Temporary processing buffer
    size_t buffer_size;                      // Current buffer size
    bool processing_enabled;                  // Processing enabled flag
    bool delay_compensation_enabled;           // Delay compensation enabled flag
    bool x_plane_processing_enabled;          // X plane processing enabled flag
    bool y_channel_correction_enabled;        // Y channel correction enabled flag
    uint64_t samples_processed;              // Total samples processed
    uint64_t frames_processed;               // Total frames processed
    uint64_t processing_time_us;             // Total processing time in microseconds
    bool is_initialized;                      // Initialization flag
} audio_pipeline_t;

/**
 * @brief Initialize integrated audio processing pipeline
 * @param pipeline Pointer to pipeline structure
 * @param config Pipeline configuration
 * @return true on success, false on failure
 */
bool audio_pipeline_init(audio_pipeline_t* pipeline, const pipeline_config_t* config);

/**
 * @brief Cleanup audio processing pipeline resources
 * @param pipeline Pointer to pipeline structure
 */
void audio_pipeline_cleanup(audio_pipeline_t* pipeline);

/**
 * @brief Process audio through integrated pipeline with delay correction
 * @param pipeline Pointer to pipeline structure
 * @param input_samples Input audio samples
 * @param input_count Number of input samples
 * @param output_samples Output buffer for processed samples
 * @param output_capacity Output buffer capacity
 * @return true on success, false on failure
 */
bool audio_pipeline_process(
    audio_pipeline_t* pipeline,
    const float* input_samples,
    size_t input_count,
    float* output_samples,
    size_t output_capacity
);

/**
 * @brief Process single sample through pipeline
 * @param pipeline Pointer to pipeline structure
 * @param input_sample Input audio sample
 * @param output_sample Output sample structure
 * @return true on success, false on failure
 */
bool audio_pipeline_process_sample(audio_pipeline_t* pipeline, float input_sample, 
                                  audio_sample_2d_t* output_sample);

/**
 * @brief Update pipeline configuration
 * @param pipeline Pointer to pipeline structure
 * @param config New pipeline configuration
 * @return true on success, false on failure
 */
bool audio_pipeline_update_config(audio_pipeline_t* pipeline, const pipeline_config_t* config);

/**
 * @brief Get pipeline status
 * @param pipeline Pointer to pipeline structure
 * @param status Output status structure
 * @return true on success, false on failure
 */
bool audio_pipeline_get_status(const audio_pipeline_t* pipeline, pipeline_status_t* status);

/**
 * @brief Reset pipeline state
 * @param pipeline Pointer to pipeline structure
 * @return true on success, false on failure
 */
bool audio_pipeline_reset(audio_pipeline_t* pipeline);

/**
 * @brief Enable/disable processing
 * @param pipeline Pointer to pipeline structure
 * @param enabled Processing enabled flag
 */
void audio_pipeline_set_processing_enabled(audio_pipeline_t* pipeline, bool enabled);

/**
 * @brief Add calibration point for plane generation
 * @param pipeline Pointer to pipeline structure
 * @param x X coordinate
 * @param y Y coordinate
 * @param value Value at point
 * @return true on success, false on failure
 */
bool audio_pipeline_add_calibration_point(audio_pipeline_t* pipeline, float x, float y, float value);

/**
 * @brief Calculate plane from calibration points
 * @param pipeline Pointer to pipeline structure
 * @return true on success, false on failure
 */
bool audio_pipeline_calibrate_plane(audio_pipeline_t* pipeline);

/**
 * @brief Create default pipeline configuration
 * @param config Pointer to configuration structure
 */
void pipeline_config_default(pipeline_config_t* config);

/**
 * @brief Create configuration optimized for diagram-based processing
 * @param config Pointer to configuration structure
 */
void pipeline_config_diagram_optimized(pipeline_config_t* config);

/**
 * @brief Get current processing delay in samples
 * @param pipeline Pointer to pipeline structure
 * @return Processing delay in samples
 */
static inline size_t audio_pipeline_get_delay_samples(const audio_pipeline_t* pipeline) {
    return pipeline ? plane_2d_generator_get_delay_samples(&pipeline->plane_generator) : 0;
}

/**
 * @brief Get current processing delay in milliseconds
 * @param pipeline Pointer to pipeline structure
 * @return Processing delay in milliseconds
 */
static inline float audio_pipeline_get_delay_ms(const audio_pipeline_t* pipeline) {
    return pipeline ? plane_2d_generator_get_delay_ms(&pipeline->plane_generator) : 0.0f;
}

/**
 * @brief Check if pipeline is ready for processing
 * @param pipeline Pointer to pipeline structure
 * @return true if ready, false otherwise
 */
static inline bool audio_pipeline_is_ready(const audio_pipeline_t* pipeline) {
    return pipeline && pipeline->is_initialized && 
           plane_2d_generator_is_ready(&pipeline->plane_generator);
}

/**
 * @brief Get processing performance metrics
 * @param pipeline Pointer to pipeline structure
 * @param samples_per_second Output samples per second
 * @param average_processing_time_us Output average processing time in microseconds
 * @return true on success, false on failure
 */
static inline bool audio_pipeline_get_performance_metrics(
    const audio_pipeline_t* pipeline,
    float* samples_per_second,
    float* average_processing_time_us
) {
    if (!pipeline || !samples_per_second || !average_processing_time_us) {
        return false;
    }

    if (pipeline->frames_processed == 0) {
        *samples_per_second = 0.0f;
        *average_processing_time_us = 0.0f;
        return true;
    }

    *samples_per_second = (float)pipeline->samples_processed / pipeline->frames_processed;
    *average_processing_time_us = (float)pipeline->processing_time_us / pipeline->frames_processed;

    return true;
}

// Constants
#define PIPELINE_DEFAULT_SAMPLE_RATE 48000
#define PIPELINE_DEFAULT_CHANNELS 2
#define PIPELINE_DEFAULT_BUFFER_SIZE 1024
#define PIPELINE_DEFAULT_DELAY_MS 3.0f
#define PIPELINE_MAX_BUFFER_SIZE 8192
#define PIPELINE_MIN_BUFFER_SIZE 64
#define PIPELINE_MIN_SAMPLE_RATE 8000
#define PIPELINE_MAX_SAMPLE_RATE 192000
#define PIPELINE_MAX_CHANNELS 8

// Error codes
typedef enum {
    PIPELINE_SUCCESS = 0,
    PIPELINE_ERROR_INVALID_PARAM,
    PIPELINE_ERROR_NOT_INITIALIZED,
    PIPELINE_ERROR_BUFFER_OVERFLOW,
    PIPELINE_ERROR_PROCESSING_FAILED,
    PIPELINE_ERROR_MEMORY_ALLOCATION,
    PIPELINE_ERROR_CONFIG_INVALID
} pipeline_error_t;

/**
 * @brief Get error string for error code
 * @param error Error code
 * @return Error description string
 */
static inline const char* pipeline_error_string(pipeline_error_t error) {
    switch (error) {
        case PIPELINE_SUCCESS:
            return "Success";
        case PIPELINE_ERROR_INVALID_PARAM:
            return "Invalid parameter";
        case PIPELINE_ERROR_NOT_INITIALIZED:
            return "Pipeline not initialized";
        case PIPELINE_ERROR_BUFFER_OVERFLOW:
            return "Buffer overflow";
        case PIPELINE_ERROR_PROCESSING_FAILED:
            return "Processing failed";
        case PIPELINE_ERROR_MEMORY_ALLOCATION:
            return "Memory allocation failed";
        case PIPELINE_ERROR_CONFIG_INVALID:
            return "Invalid configuration";
        default:
            return "Unknown error";
    }
}

#ifdef __cplusplus
}
#endif

#endif // AUDIO_PIPELINE_INTEGRATION_H
