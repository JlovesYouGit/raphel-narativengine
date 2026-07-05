/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#ifndef DELAY_COMPENSATION_H
#define DELAY_COMPENSATION_H

#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Delay compensation parameters
 */
typedef struct {
    float delay_ms;                    // Delay compensation in milliseconds
    float sample_rate;                 // Audio sample rate
    float distortion_factor;           // Distortion correction factor (0.0 to 1.0)
    float adaptive_factor;             // Adaptive correction factor (0.0 to 1.0)
    bool enable_adaptive_correction;   // Enable adaptive phase correction
    bool enable_phase_alignment;       // Enable phase alignment
} delay_params_t;

/**
 * @brief Delay compensation status
 */
typedef struct {
    float delay_ms;                    // Current delay in milliseconds
    size_t delay_samples;              // Delay in samples
    bool buffer_ready;                 // Buffer ready for reading
    float adaptive_factor;             // Current adaptive factor
    float phase_error_accumulator;     // Accumulated phase error
    float distortion_correction_factor; // Current distortion correction factor
    size_t buffer_fill;                // Current buffer fill level
    float buffer_fill_percentage;      // Buffer fill percentage
} delay_status_t;

/**
 * @brief Delay compensator structure
 */
typedef struct {
    delay_params_t params;             // Compensation parameters
    float* y_plus_buffer;              // Y+ delay buffer
    float* y_minus_buffer;             // Y- delay buffer
    float* phase_buffer;               // Phase buffer for alignment
    size_t delay_samples;              // Number of delay samples
    size_t write_index;                // Buffer write index
    size_t read_index;                 // Buffer read index
    bool buffer_ready;                 // Buffer ready flag
    float adaptive_factor;             // Current adaptive factor
    float phase_error_accumulator;     // Accumulated phase error
    float distortion_correction_factor; // Current distortion correction factor
    bool is_initialized;               // Initialization flag
} delay_compensator_t;

/**
 * @brief Initialize delay compensator for Y+ and Y- distortion correction
 * @param compensator Pointer to compensator structure
 * @param params Delay compensation parameters
 * @return true on success, false on failure
 */
bool delay_compensator_init(delay_compensator_t* compensator, const delay_params_t* params);

/**
 * @brief Cleanup delay compensator resources
 * @param compensator Pointer to compensator structure
 */
void delay_compensator_cleanup(delay_compensator_t* compensator);

/**
 * @brief Process samples with delay compensation and distortion correction
 * @param compensator Pointer to compensator structure
 * @param y_plus_input Y+ input sample
 * @param y_minus_input Y- input sample
 * @param y_plus_output Pointer to store compensated Y+ output
 * @param y_minus_output Pointer to store compensated Y- output
 * @return true on success, false on failure
 */
bool delay_compensator_process(
    delay_compensator_t* compensator,
    float y_plus_input,
    float y_minus_input,
    float* y_plus_output,
    float* y_minus_output
);

/**
 * @brief Apply distortion correction for Y+ and Y- channels
 * @param compensator Pointer to compensator structure
 * @param y_plus Pointer to Y+ sample (modified in place)
 * @param y_minus Pointer to Y- sample (modified in place)
 */
void apply_distortion_correction(delay_compensator_t* compensator, float* y_plus, float* y_minus);

/**
 * @brief Get current delay compensation status
 * @param compensator Pointer to compensator structure
 * @param status Pointer to status structure
 * @return true on success, false on failure
 */
bool delay_compensator_get_status(const delay_compensator_t* compensator, delay_status_t* status);

/**
 * @brief Update delay compensation parameters
 * @param compensator Pointer to compensator structure
 * @param params New delay parameters
 * @return true on success, false on failure
 */
bool delay_compensator_update_params(delay_compensator_t* compensator, const delay_params_t* params);

/**
 * @brief Reset delay compensator state
 * @param compensator Pointer to compensator structure
 * @return true on success, false on failure
 */
bool delay_compensator_reset(delay_compensator_t* compensator);

/**
 * @brief Create default delay parameters
 * @param params Pointer to parameters structure
 */
void delay_params_default(delay_params_t* params);

/**
 * @brief Create delay parameters optimized for 3D spatial audio
 * @param params Pointer to parameters structure
 */
void delay_params_3d_spatial(delay_params_t* params);

/**
 * @brief Calculate processing delay in samples
 * @param compensator Pointer to compensator structure
 * @return Processing delay in samples
 */
static inline size_t delay_compensator_get_delay_samples(const delay_compensator_t* compensator) {
    return compensator ? compensator->delay_samples : 0;
}

/**
 * @brief Calculate processing delay in milliseconds
 * @param compensator Pointer to compensator structure
 * @return Processing delay in milliseconds
 */
static inline float delay_compensator_get_delay_ms(const delay_compensator_t* compensator) {
    return compensator ? compensator->params.delay_ms : 0.0f;
}

/**
 * @brief Check if compensator is ready for processing
 * @param compensator Pointer to compensator structure
 * @return true if ready, false otherwise
 */
static inline bool delay_compensator_is_ready(const delay_compensator_t* compensator) {
    return compensator && compensator->is_initialized && compensator->buffer_ready;
}

// Constants
#define DELAY_COMPENSATOR_MAX_DELAY_MS 100.0f
#define DELAY_COMPENSATOR_MIN_DELAY_MS 0.1f
#define DELAY_COMPENSATOR_MAX_SAMPLE_RATE 192000.0f
#define DELAY_COMPENSATOR_MIN_SAMPLE_RATE 8000.0f

#ifdef __cplusplus
}
#endif

#endif // DELAY_COMPENSATION_H
