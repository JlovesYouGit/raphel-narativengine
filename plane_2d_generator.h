/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#ifndef PLANE_2D_GENERATOR_H
#define PLANE_2D_GENERATOR_H

#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include "delay_compensation.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 2D plane point definition
 */
typedef struct {
    float x;        // X coordinate
    float y;        // Y coordinate
    float value;    // Value at point
    float weight;   // Weight for coefficient calculation
} plane_2d_point_t;

/**
 * @brief Plane coefficients (z = a*x + b*y + c)
 */
typedef struct {
    float a;        // X coefficient
    float b;        // Y coefficient
    float c;        // Constant term
} plane_coefficients_t;

/**
 * @brief Audio sample structure for 2D plane processing
 */
typedef struct {
    float x_component;    // X plane component
    float y_plus;         // Y+ component
    float y_minus;        // Y- component
    float magnitude;      // Combined magnitude
    float phase;          // Combined phase
} audio_sample_2d_t;

/**
 * @brief 2D plane generator configuration
 */
typedef struct {
    float sample_rate;                    // Audio sample rate
    uint32_t channels;                    // Number of channels
    float x_plane_range;                  // X plane range (matches diagram -3 to 3)
    float y_plane_range;                  // Y plane range (matches diagram -3 to 3)
    float delay_compensation_ms;          // Delay compensation for Y+ and Y-
    float distortion_correction_factor;  // Distortion correction factor
    bool enable_x_plane_processing;      // Enable X plane processing
    bool enable_y_channel_correction;      // Enable Y channel correction
    bool enable_adaptive_plane;           // Enable adaptive plane calculation
} plane_2d_config_t;

/**
 * @brief 2D plane generator status
 */
typedef struct {
    bool processing_enabled;               // Processing enabled flag
    size_t num_points;                    // Number of points in buffer
    float current_x;                      // Current X position
    float current_y;                      // Current Y position
    float phase_accumulator;              // Current phase accumulator
    delay_status_t delay_status;          // Delay compensator status
} plane_2d_status_t;

/**
 * @brief 2D plane generator structure
 */
typedef struct {
    plane_2d_config_t config;             // Generator configuration
    plane_2d_point_t* point_buffer;       // Point buffer for plane calculation
    plane_coefficients_t plane_coeffs;    // Current plane coefficients
    delay_compensator_t delay_compensator; // Delay compensator for Y+ and Y-
    float phase_accumulator;              // Phase accumulator for signal generation
    float x_phase_offset;                 // X plane phase offset
    float y_phase_offset;                 // Y plane phase offset
    size_t num_points;                    // Current number of points
    float current_x;                      // Current X position
    float current_y;                      // Current Y position
    bool processing_enabled;              // Processing enabled flag
    bool is_initialized;                  // Initialization flag
} plane_2d_generator_t;

/**
 * @brief Initialize 2D plane generator with X plane processing
 * @param generator Pointer to generator structure
 * @param config Generator configuration
 * @return true on success, false on failure
 */
bool plane_2d_generator_init(plane_2d_generator_t* generator, const plane_2d_config_t* config);

/**
 * @brief Cleanup 2D plane generator resources
 * @param generator Pointer to generator structure
 */
void plane_2d_generator_cleanup(plane_2d_generator_t* generator);

/**
 * @brief Generate 2D plane samples with X plane processing and delay compensation
 * @param generator Pointer to generator structure
 * @param x_position X position on plane
 * @param y_position Y position on plane
 * @param sample Output sample structure
 * @return true on success, false on failure
 */
bool plane_2d_generator_process(
    plane_2d_generator_t* generator,
    float x_position,
    float y_position,
    audio_sample_2d_t* sample
);

/**
 * @brief Add point to 2D plane for coefficient calculation
 * @param generator Pointer to generator structure
 * @param x X coordinate
 * @param y Y coordinate
 * @param value Value at point
 * @return true on success, false on failure
 */
bool plane_2d_generator_add_point(plane_2d_generator_t* generator, float x, float y, float value);

/**
 * @brief Calculate plane coefficients from added points
 * @param generator Pointer to generator structure
 * @return true on success, false on failure
 */
bool plane_2d_generator_calculate_plane(plane_2d_generator_t* generator);

/**
 * @brief Set plane coefficients directly
 * @param generator Pointer to generator structure
 * @param coeffs Plane coefficients
 * @return true on success, false on failure
 */
bool plane_2d_generator_set_plane_coefficients(plane_2d_generator_t* generator, 
                                               const plane_coefficients_t* coeffs);

/**
 * @brief Get current plane coefficients
 * @param generator Pointer to generator structure
 * @param coeffs Output coefficients structure
 * @return true on success, false on failure
 */
bool plane_2d_generator_get_plane_coefficients(const plane_2d_generator_t* generator, 
                                               plane_coefficients_t* coeffs);

/**
 * @brief Reset plane generator state
 * @param generator Pointer to generator structure
 * @return true on success, false on failure
 */
bool plane_2d_generator_reset(plane_2d_generator_t* generator);

/**
 * @brief Enable/disable processing
 * @param generator Pointer to generator structure
 * @param enabled Processing enabled flag
 */
void plane_2d_generator_set_processing_enabled(plane_2d_generator_t* generator, bool enabled);

/**
 * @brief Get processing status
 * @param generator Pointer to generator structure
 * @param status Output status structure
 * @return true on success, false on failure
 */
bool plane_2d_generator_get_status(const plane_2d_generator_t* generator, plane_2d_status_t* status);

/**
 * @brief Create default 2D plane configuration
 * @param config Pointer to configuration structure
 */
void plane_2d_config_default(plane_2d_config_t* config);

/**
 * @brief Create configuration optimized for diagram-based processing
 * @param config Pointer to configuration structure
 */
void plane_2d_config_diagram_optimized(plane_2d_config_t* config);

/**
 * @brief Get current processing delay in samples
 * @param generator Pointer to generator structure
 * @return Processing delay in samples
 */
static inline size_t plane_2d_generator_get_delay_samples(const plane_2d_generator_t* generator) {
    return generator ? delay_compensator_get_delay_samples(&generator->delay_compensator) : 0;
}

/**
 * @brief Get current processing delay in milliseconds
 * @param generator Pointer to generator structure
 * @return Processing delay in milliseconds
 */
static inline float plane_2d_generator_get_delay_ms(const plane_2d_generator_t* generator) {
    return generator ? delay_compensator_get_delay_ms(&generator->delay_compensator) : 0.0f;
}

/**
 * @brief Check if generator is ready for processing
 * @param generator Pointer to generator structure
 * @return true if ready, false otherwise
 */
static inline bool plane_2d_generator_is_ready(const plane_2d_generator_t* generator) {
    return generator && generator->is_initialized && 
           delay_compensator_is_ready(&generator->delay_compensator);
}

// Constants
#define PLANE_2D_DEFAULT_SAMPLE_RATE 48000.0f
#define PLANE_2D_DEFAULT_CHANNELS 2
#define PLANE_2D_DEFAULT_X_RANGE 3.0f
#define PLANE_2D_DEFAULT_Y_RANGE 3.0f
#define PLANE_2D_DEFAULT_DELAY_MS 3.0f
#define PLANE_2D_MAX_POINTS 1000
#define PLANE_2D_MIN_POINTS_FOR_PLANE 3

#ifdef __cplusplus
}
#endif

#endif // PLANE_2D_GENERATOR_H
