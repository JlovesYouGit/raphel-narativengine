// SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT

//! Audio Format Decoder with Delay Compensation for 3D Spatial Audio
//! 
//! This module handles audio format decoding with specific focus on:
//! - Delay compensation for Y+ and Y- direction distortion
//! - 2D plane generation with X plane processing
//! - Real-time audio processing with minimal latency

use std::f32::consts::PI;
use std::sync::{Arc, Mutex};
use std::collections::VecDeque;

/// Audio sample format
#[derive(Debug, Clone, Copy)]
pub enum AudioFormat {
    F32,
    F64,
    S16,
    S24,
    S32,
}

/// 2D Plane configuration for spatial audio
#[derive(Debug, Clone)]
pub struct Plane2DConfig {
    pub sample_rate: u32,
    pub channels: u32,
    pub buffer_size: usize,
    pub x_plane_range: f32,  // X plane range (-3 to 3 as shown in diagram)
    pub y_plane_range: f32,  // Y plane range for distortion correction
    pub delay_compensation_ms: f32,
}

impl Default for Plane2DConfig {
    fn default() -> Self {
        Self {
            sample_rate: 16000,
            channels: 2,
            buffer_size: 1024,
            x_plane_range: 3.0,
            y_plane_range: 3.0,
            delay_compensation_ms: 5.0,
        }
    }
}

/// Delay compensation buffer for Y+ and Y- channels
#[derive(Debug)]
struct DelayBuffer {
    y_plus_buffer: VecDeque<f32>,
    y_minus_buffer: VecDeque<f32>,
    compensation_samples: usize,
}

impl DelayBuffer {
    fn new(compensation_samples: usize) -> Self {
        Self {
            y_plus_buffer: VecDeque::with_capacity(compensation_samples * 2),
            y_minus_buffer: VecDeque::with_capacity(compensation_samples * 2),
            compensation_samples,
        }
    }

    fn push_samples(&mut self, y_plus: f32, y_minus: f32) {
        self.y_plus_buffer.push_back(y_plus);
        self.y_minus_buffer.push_back(y_minus);
        
        // Maintain buffer size
        while self.y_plus_buffer.len() > self.compensation_samples * 2 {
            self.y_plus_buffer.pop_front();
        }
        while self.y_minus_buffer.len() > self.compensation_samples * 2 {
            self.y_minus_buffer.pop_front();
        }
    }

    fn get_compensated_samples(&self) -> Option<(f32, f32)> {
        if self.y_plus_buffer.len() >= self.compensation_samples && 
           self.y_minus_buffer.len() >= self.compensation_samples {
            let y_plus = self.y_plus_buffer[self.y_plus_buffer.len() - self.compensation_samples - 1];
            let y_minus = self.y_minus_buffer[self.y_minus_buffer.len() - self.compensation_samples - 1];
            Some((y_plus, y_minus))
        } else {
            None
        }
    }
}

/// 2D Plane Generator for X plane processing
#[derive(Debug)]
struct Plane2DGenerator {
    config: Plane2DConfig,
    delay_buffer: DelayBuffer,
    phase_accumulator: f32,
}

impl Plane2DGenerator {
    fn new(config: Plane2DConfig) -> Self {
        let compensation_samples = (config.delay_compensation_ms / 1000.0 * config.sample_rate as f32) as usize;
        Self {
            delay_buffer: DelayBuffer::new(compensation_samples),
            config,
            phase_accumulator: 0.0,
        }
    }

    /// Generate 2D plane samples with X plane processing
    fn generate_plane_samples(&mut self, x_position: f32, y_position: f32) -> (f32, f32, f32) {
        // Normalize positions to -1 to 1 range
        let x_norm = (x_position / self.config.x_plane_range).clamp(-1.0, 1.0);
        let y_norm = (y_position / self.config.y_plane_range).clamp(-1.0, 1.0);

        // Generate X plane component (primary signal)
        let x_phase = self.phase_accumulator + x_norm * PI;
        let x_component = (x_phase).sin();

        // Generate Y+ and Y- components with distortion correction
        let y_phase_offset = y_norm * PI / 2.0;  // 90-degree phase shift for Y components
        let y_plus_phase = self.phase_accumulator + y_phase_offset;
        let y_minus_phase = self.phase_accumulator - y_phase_offset;

        // Apply distortion correction for Y+ and Y-
        let distortion_factor = 1.0 - (y_norm.abs() * 0.2);  // Reduce distortion at extremes
        let y_plus = (y_plus_phase).sin() * distortion_factor;
        let y_minus = (y_minus_phase).sin() * distortion_factor;

        // Update phase accumulator
        self.phase_accumulator += 2.0 * PI / (self.config.sample_rate as f32 / 440.0); // 440Hz reference
        if self.phase_accumulator > 2.0 * PI {
            self.phase_accumulator -= 2.0 * PI;
        }

        // Apply delay compensation
        self.delay_buffer.push_samples(y_plus, y_minus);
        
        if let Some((compensated_y_plus, compensated_y_minus)) = self.delay_buffer.get_compensated_samples() {
            (x_component, compensated_y_plus, compensated_y_minus)
        } else {
            // Return uncompensated if buffer not ready
            (x_component, y_plus, y_minus)
        }
    }
}

/// Audio decoder with delay compensation
pub struct AudioDecoder {
    config: Plane2DConfig,
    plane_generator: Plane2DGenerator,
    input_buffer: Vec<f32>,
    output_buffer: Vec<f32>,
    current_format: AudioFormat,
}

impl AudioDecoder {
    /// Create new audio decoder with delay compensation
    pub fn new(config: Plane2DConfig) -> Self {
        Self {
            plane_generator: Plane2DGenerator::new(config.clone()),
            config,
            input_buffer: Vec::with_capacity(1024),
            output_buffer: Vec::with_capacity(1024 * 3), // X, Y+, Y-
            current_format: AudioFormat::F32,
        }
    }

    /// Decode audio format with 2D plane generation
    pub fn decode_with_plane_generation(&mut self, input_data: &[u8], format: AudioFormat) -> Result<Vec<f32>, String> {
        self.current_format = format;
        
        // Convert input data to f32 samples
        let samples = self.convert_to_f32(input_data, format)?;
        
        // Process samples with 2D plane generation
        let mut processed_samples = Vec::with_capacity(samples.len() * 3);
        
        for (i, &sample) in samples.iter().enumerate() {
            // Calculate position based on sample index and value
            let x_position = (i as f32 / samples.len() as f32 - 0.5) * 2.0 * self.config.x_plane_range;
            let y_position = sample * self.config.y_plane_range;
            
            // Generate 2D plane samples
            let (x_comp, y_plus, y_minus) = self.plane_generator.generate_plane_samples(x_position, y_position);
            
            // Apply additional distortion correction for Y+ and Y-
            let corrected_y_plus = self.apply_y_distortion_correction(y_plus, true);
            let corrected_y_minus = self.apply_y_distortion_correction(y_minus, false);
            
            processed_samples.extend_from_slice(&[x_comp, corrected_y_plus, corrected_y_minus]);
        }
        
        Ok(processed_samples)
    }

    /// Convert input data to f32 samples
    fn convert_to_f32(&self, input_data: &[u8], format: AudioFormat) -> Result<Vec<f32>, String> {
        match format {
            AudioFormat::F32 => {
                if input_data.len() % 4 != 0 {
                    return Err("Invalid F32 data length".to_string());
                }
                let samples = input_data.chunks_exact(4)
                    .map(|chunk| f32::from_le_bytes(chunk.try_into().unwrap()))
                    .collect();
                Ok(samples)
            }
            AudioFormat::F64 => {
                if input_data.len() % 8 != 0 {
                    return Err("Invalid F64 data length".to_string());
                }
                let samples = input_data.chunks_exact(8)
                    .map(|chunk| f64::from_le_bytes(chunk.try_into().unwrap()) as f32)
                    .collect();
                Ok(samples)
            }
            AudioFormat::S16 => {
                if input_data.len() % 2 != 0 {
                    return Err("Invalid S16 data length".to_string());
                }
                let samples = input_data.chunks_exact(2)
                    .map(|chunk| i16::from_le_bytes(chunk.try_into().unwrap()) as f32 / 32768.0)
                    .collect();
                Ok(samples)
            }
            AudioFormat::S24 => {
                if input_data.len() % 3 != 0 {
                    return Err("Invalid S24 data length".to_string());
                }
                let samples = input_data.chunks_exact(3)
                    .map(|chunk| {
                        let mut bytes = [0u8; 4];
                        bytes[0..3].copy_from_slice(chunk);
                        // Sign extend for 24-bit
                        if chunk[2] & 0x80 != 0 {
                            bytes[3] = 0xFF;
                        }
                        i32::from_le_bytes(bytes) as f32 / 8388608.0
                    })
                    .collect();
                Ok(samples)
            }
            AudioFormat::S32 => {
                if input_data.len() % 4 != 0 {
                    return Err("Invalid S32 data length".to_string());
                }
                let samples = input_data.chunks_exact(4)
                    .map(|chunk| i32::from_le_bytes(chunk.try_into().unwrap()) as f32 / 2147483648.0)
                    .collect();
                Ok(samples)
            }
        }
    }

    /// Apply distortion correction for Y+ and Y- channels
    fn apply_y_distortion_correction(&self, y_sample: f32, is_y_plus: bool) -> f32 {
        // Apply phase correction to reduce Y+ and Y- distortion
        let phase_correction = if is_y_plus { 1.0 } else { -1.0 };
        
        // Apply amplitude correction based on Y position
        let amplitude_correction = 1.0 - (y_sample.abs() * 0.1);  // 10% correction at extremes
        
        // Apply delay compensation correction
        let delay_factor = 1.0 + (self.config.delay_compensation_ms / 1000.0) * 0.05;
        
        y_sample * phase_correction * amplitude_correction * delay_factor
    }

    /// Get current delay compensation status
    pub fn get_delay_status(&self) -> DelayStatus {
        DelayStatus {
            compensation_ms: self.config.delay_compensation_ms,
            buffer_length: self.plane_generator.delay_buffer.y_plus_buffer.len(),
            is_ready: self.plane_generator.delay_buffer.y_plus_buffer.len() >= 
                     self.plane_generator.delay_buffer.compensation_samples,
        }
    }

    /// Update delay compensation value
    pub fn update_delay_compensation(&mut self, compensation_ms: f32) {
        self.config.delay_compensation_ms = compensation_ms;
        let compensation_samples = (compensation_ms / 1000.0 * self.config.sample_rate as f32) as usize;
        self.plane_generator.delay_buffer = DelayBuffer::new(compensation_samples);
    }

    /// Get current format
    pub fn current_format(&self) -> AudioFormat {
        self.current_format
    }
}

/// Delay compensation status
#[derive(Debug, Clone)]
pub struct DelayStatus {
    pub compensation_ms: f32,
    pub buffer_length: usize,
    pub is_ready: bool,
}

/// Audio decoder factory
pub struct AudioDecoderFactory;

impl AudioDecoderFactory {
    /// Create decoder with default configuration
    pub fn create_default() -> AudioDecoder {
        AudioDecoder::new(Plane2DConfig::default())
    }

    /// Create decoder with custom configuration
    pub fn create_with_config(config: Plane2DConfig) -> AudioDecoder {
        AudioDecoder::new(config)
    }

    /// Create decoder optimized for 3D spatial audio
    pub fn create_for_3d_spatial() -> AudioDecoder {
        let config = Plane2DConfig {
            sample_rate: 48000,
            channels: 2,
            buffer_size: 2048,
            x_plane_range: 3.0,  // Match diagram X range
            y_plane_range: 3.0,  // Match diagram Y range
            delay_compensation_ms: 3.0,  // Reduced delay for better spatial accuracy
        };
        AudioDecoder::new(config)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_delay_buffer() {
        let mut buffer = DelayBuffer::new(5);
        
        // Push samples
        for i in 0..10 {
            buffer.push_samples(i as f32, -(i as f32));
        }
        
        // Check compensated samples
        assert!(buffer.get_compensated_samples().is_some());
        let (y_plus, y_minus) = buffer.get_compensated_samples().unwrap();
        assert_eq!(y_plus, 4.0);  // Should be 5 samples behind
        assert_eq!(y_minus, -4.0);
    }

    #[test]
    fn test_plane_generation() {
        let config = Plane2DConfig::default();
        let mut generator = Plane2DGenerator::new(config);
        
        let (x, y_plus, y_minus) = generator.generate_plane_samples(1.0, 0.5);
        
        // Verify ranges are within expected bounds
        assert!(x >= -1.0 && x <= 1.0);
        assert!(y_plus >= -1.0 && y_plus <= 1.0);
        assert!(y_minus >= -1.0 && y_minus <= 1.0);
    }

    #[test]
    fn test_audio_decoder() {
        let mut decoder = AudioDecoderFactory::create_default();
        
        // Test F32 format
        let input_data = [0.5f32, -0.5f32, 0.0f32, 1.0f32]
            .iter()
            .flat_map(|&f| f.to_le_bytes().to_vec())
            .collect::<Vec<_>>();
        
        let result = decoder.decode_with_plane_generation(&input_data, AudioFormat::F32);
        assert!(result.is_ok());
        
        let processed = result.unwrap();
        assert_eq!(processed.len(), 12); // 4 samples * 3 components
    }
}
