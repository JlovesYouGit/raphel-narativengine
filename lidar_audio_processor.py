# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
LIDAR Audio Processor
Advanced LIDAR-like processing for 3D audio bubble orientation and spatial audio
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import math
from nemo.utils import logging

from nemo2riva.spectrum_3d_bubble.spectrum_bubble_generator import SpectrumBubbleConfig, SpectrumBubble3DSystem


@dataclass
class LIDARAudioConfig:
    """Configuration for LIDAR audio processing"""
    # LIDAR detection parameters
    lidar_range: float = 5.0              # Detection range in meters
    angular_resolution: float = 1.0        # Angular resolution in degrees
    detection_precision: float = 0.02      # Detection precision in meters
    scan_rate: float = 30.0                # Scan rate in Hz
    
    # Head tracking parameters
    head_tracking_sensitivity: float = 0.8
    tilt_detection_threshold: float = 0.15   # Threshold for tilt detection
    orientation_smoothing: float = 0.1        # Smoothing factor for orientation
    
    # Spatial audio parameters
    spatial_audio_resolution: float = 0.05  # Spatial resolution in meters
    audio_falloff_exponent: float = 2.0      # Audio falloff exponent
    max_audio_sources: int = 64              # Maximum audio sources
    
    # Multi-bubble support
    enable_multi_bubble: bool = True
    max_bubbles: int = 8                    # Maximum number of bubbles
    bubble_overlap_threshold: float = 0.3    # Overlap threshold for bubbles
    
    # Real-time processing
    enable_real_time: bool = True
    processing_buffer_size: int = 1024
    latency_target_ms: float = 10.0


class LIDARHeadTracker(nn.Module):
    """LIDAR-like head tracking system"""
    
    def __init__(self, config: LIDARAudioConfig):
        super().__init__()
        self.config = config
        
        # Head tracking neural network
        self.head_tracker = nn.Sequential(
            nn.Linear(128, 256),  # Spectrum features
            nn.GELU(),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 6),  # X_tilt, Y_tilt, Z_rotation, confidence, position_x, position_y
            nn.Tanh()
        )
        
        # Orientation smoother
        self.orientation_smoother = nn.Parameter(torch.tensor(config.orientation_smoothing))
        
        # Position estimator
        self.position_estimator = nn.Sequential(
            nn.Linear(3, 64),  # X_tilt, Y_tilt, confidence
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 3),  # X, Y, Z position
            nn.Tanh()
        )
        
        # State tracking
        self.register_buffer('previous_orientation', torch.zeros(3))
        self.register_buffer('previous_position', torch.zeros(3))
        self.register_buffer('orientation_velocity', torch.zeros(3))
        
    def track_head_orientation(self, spectrum_features: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Track head orientation using LIDAR-like processing
        
        Args:
            spectrum_features: Spectrum features from audio
            
        Returns:
            Dictionary with head tracking data
        """
        # Process spectrum features through neural network
        tracking_output = self.head_tracker(spectrum_features)
        
        # Extract components
        x_tilt = tracking_output[:, 0]
        y_tilt = tracking_output[:, 1]
        z_rotation = tracking_output[:, 2]
        confidence = torch.abs(tracking_output[:, 3])
        position_x = tracking_output[:, 4]
        position_y = tracking_output[:, 5]
        
        # Apply smoothing to orientation
        smoothed_x_tilt = self.orientation_smoother * x_tilt + (1 - self.orientation_smoother) * self.previous_orientation[0]
        smoothed_y_tilt = self.orientation_smoother * y_tilt + (1 - self.orientation_smoother) * self.previous_orientation[1]
        smoothed_z_rotation = self.orientation_smoother * z_rotation + (1 - self.orientation_smoother) * self.previous_orientation[2]
        
        # Calculate orientation velocity
        orientation_velocity = torch.stack([
            smoothed_x_tilt - self.previous_orientation[0],
            smoothed_y_tilt - self.previous_orientation[1],
            smoothed_z_rotation - self.previous_orientation[2]
        ], dim=-1)
        
        # Estimate 3D position
        position_input = torch.stack([smoothed_x_tilt, smoothed_y_tilt, confidence], dim=-1)
        estimated_position = self.position_estimator(position_input)
        
        # Combine with position from tracking
        final_position = torch.stack([
            estimated_position[:, 0] + position_x,
            estimated_position[:, 1] + position_y,
            estimated_position[:, 2]
        ], dim=-1)
        
        # Update state
        self.previous_orientation.copy_(torch.stack([smoothed_x_tilt, smoothed_y_tilt, smoothed_z_rotation], dim=-1))
        self.previous_position.copy_(final_position)
        self.orientation_velocity.copy_(orientation_velocity)
        
        return {
            "x_tilt": smoothed_x_tilt,
            "y_tilt": smoothed_y_tilt,
            "z_rotation": smoothed_z_rotation,
            "confidence": confidence,
            "position": final_position,
            "velocity": orientation_velocity
        }
    
    def get_movement_direction(self) -> str:
        """Get movement direction based on orientation"""
        if torch.abs(self.orientation_velocity[0]) > self.config.tilt_detection_threshold:
            if self.orientation_velocity[0] > 0:
                return "right"
            else:
                return "left"
        elif torch.abs(self.orientation_velocity[1]) > self.config.tilt_detection_threshold:
            if self.orientation_velocity[1] > 0:
                return "head_up"
            else:
                return "head_down"
        else:
            return "stable"


class MultiBubbleManager(nn.Module):
    """Manager for multiple 3D audio bubbles"""
    
    def __init__(self, config: LIDARAudioConfig):
        super().__init__()
        self.config = config
        
        # Bubble management parameters
        self.max_bubbles = config.max_bubbles
        self.overlap_threshold = config.bubble_overlap_threshold
        
        # Bubble registration
        self.register_buffer('active_bubbles', torch.zeros(config.max_bubbles, 3))  # X, Y, Z centers
        self.register_buffer('bubble_intensities', torch.zeros(config.max_bubbles))
        self.register_buffer('bubble_orientations', torch.zeros(config.max_bubbles, 3))  # X_tilt, Y_tilt, Z_rotation
        
        # Bubble merger
        self.bubble_merger = nn.Sequential(
            nn.Linear(config.max_bubbles * 6, 128),  # All bubble data
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 3),  # Merged center
            nn.Tanh()
        )
        
        # Overlap detector
        self.overlap_detector = nn.Sequential(
            nn.Linear(config.max_bubbles * 3, 64),  # Bubble positions
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, config.max_bubbles),  # Overlap scores
            nn.Sigmoid()
        )
        
    def register_bubble(self, center: torch.Tensor, intensity: torch.Tensor, 
                        orientation: torch.Tensor) -> int:
        """
        Register a new bubble in the system
        
        Args:
            center: Bubble center [X, Y, Z]
            intensity: Bubble intensity
            orientation: Bubble orientation [X_tilt, Y_tilt, Z_rotation]
            
        Returns:
            Bubble index
        """
        # Find available bubble slot
        available_slots = torch.where(self.bubble_intensities < 0.1)[0]
        
        if len(available_slots) == 0:
            # Find weakest bubble to replace
            weakest_idx = torch.argmin(self.bubble_intensities)
            bubble_idx = weakest_idx
        else:
            bubble_idx = available_slots[0]
        
        # Register bubble
        self.active_bubbles[bubble_idx] = center
        self.bubble_intensities[bubble_idx] = intensity
        self.bubble_orientations[bubble_idx] = orientation
        
        return bubble_idx
    
    def detect_overlaps(self) -> torch.Tensor:
        """Detect overlapping bubbles"""
        # Calculate pairwise distances
        distances = torch.zeros(self.max_bubbles, self.max_bubbles)
        
        for i in range(self.max_bubbles):
            for j in range(self.max_bubbles):
                if i != j:
                    distance = torch.norm(self.active_bubbles[i] - self.active_bubbles[j])
                    distances[i, j] = distance
        
        # Detect overlaps (distance < threshold)
        overlap_scores = torch.exp(-distances / self.overlap_threshold)
        
        return overlap_scores
    
    def merge_overlapping_bubbles(self) -> torch.Tensor:
        """Merge overlapping bubbles"""
        # Detect overlaps
        overlap_scores = self.detect_overlaps()
        
        # Prepare input for merger
        bubble_data = torch.cat([
            self.active_bubbles,
            self.bubble_intensities.unsqueeze(1),
            self.bubble_orientations
        ], dim=-1)
        
        # Merge bubbles
        merged_center = self.bubble_merger(bubble_data)
        
        return merged_center
    
    def get_active_bubbles(self) -> Dict[str, torch.Tensor]:
        """Get information about active bubbles"""
        active_mask = self.bubble_intensities > 0.1
        
        return {
            "centers": self.active_bubbles[active_mask],
            "intensities": self.bubble_intensities[active_mask],
            "orientations": self.bubble_orientations[active_mask],
            "active_indices": torch.where(active_mask)[0],
            "count": active_mask.sum().item()
        }


class LIDARAudioProcessor:
    """
    LIDAR-like audio processor for 3D bubble system
    """
    
    def __init__(self, config: LIDARAudioConfig, sample_rate: int = 22050):
        self.config = config
        self.sample_rate = sample_rate
        
        # Initialize components
        self.head_tracker = LIDARHeadTracker(config)
        self.bubble_manager = MultiBubbleManager(config)
        
        # Spectrum bubble system
        bubble_config = SpectrumBubbleConfig(
            bubble_radius=config.lidar_range,
            bubble_resolution=64,
            spectrum_bins=128,
            frequency_range=(20.0, 20000.0),
            orientation_sensitivity=config.head_tracking_sensitivity,
            max_audio_sources=config.max_audio_sources,
            enable_lidar_detection=True,
            detection_precision=config.detection_precision,
            orientation_tracking=True,
            enable_multi_entry=True,
            dynamic_bubble=True
        )
        self.bubble_system = SpectrumBubble3DSystem(bubble_config, sample_rate)
        
        # Processing state
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Real-time processing buffer
        self.processing_buffer = torch.zeros(config.processing_buffer_size, sample_rate)
        self.buffer_write_pos = 0
        
        # LIDAR scan data
        self.lidar_scan_data = []
        self.scan_history = []
        
        logging.info(f"LIDAR Audio Processor initialized on device: {self.device}")
    
    def initialize(self):
        """Initialize the processor"""
        self.head_tracker.to(self.device)
        self.bubble_manager.to(self.device)
        self.bubble_system.initialize()
        
        self.head_tracker.eval()
        self.bubble_manager.eval()
        self.bubble_system.eval()
        
        self.initialized = True
        logging.info("LIDAR Audio Processor fully initialized")
    
    def process_audio_with_lidar(self, audio: torch.Tensor) -> Dict[str, any]:
        """
        Process audio with LIDAR-like 3D bubble generation
        
        Args:
            audio: Input audio tensor [batch_size, sequence_length]
            
        Returns:
            Dictionary with LIDAR processing results
        """
        if not self.initialized:
            raise RuntimeError("Processor not initialized. Call initialize() first.")
        
        # Ensure input is 2D
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)
        
        # Move to device
        audio = audio.to(self.device)
        
        # Add to processing buffer
        self._add_to_buffer(audio)
        
        # Extract spectrum features
        spectrum_features = self._extract_spectrum_features(audio)
        
        # Track head orientation
        head_tracking = self.head_tracker.track_head_orientation(spectrum_features)
        
        # Create audio sources based on spectrum
        audio_sources = self._create_lidar_audio_sources(spectrum_features, head_tracking)
        
        # Generate 3D bubble system
        bubble_result = self.bubble_system.process_spectrum_to_3d_bubble(audio, audio_sources)
        
        # Manage multiple bubbles
        if self.config.enable_multi_bubble:
            self._manage_multi_bubbles(head_tracking, bubble_result)
        
        # Create LIDAR scan data
        lidar_data = self._create_lidar_scan_data(head_tracking, bubble_result)
        
        # Get movement direction
        movement_direction = self.head_tracker.get_movement_direction()
        
        return {
            "head_tracking": head_tracking,
            "bubble_result": bubble_result,
            "multi_bubbles": self.bubble_manager.get_active_bubbles() if self.config.enable_multi_bubble else None,
            "lidar_scan": lidar_data,
            "movement_direction": movement_direction,
            "audio_sources": audio_sources
        }
    
    def _extract_spectrum_features(self, audio: torch.Tensor) -> torch.Tensor:
        """Extract spectrum features for LIDAR processing"""
        # Compute FFT
        fft = torch.fft.rfft(audio, dim=-1)
        magnitude = torch.abs(fft)
        
        # Extract features (magnitude, phase, spectral centroid, etc.)
        features = []
        
        # Magnitude features
        features.append(magnitude)
        
        # Phase features
        phase = torch.angle(fft)
        features.append(phase)
        
        # Spectral centroid
        freq_bins = torch.fft.rfftfreq(audio.size(-1), 1.0 / self.sample_rate, device=audio.device)
        spectral_centroid = torch.sum(magnitude * freq_bins.unsqueeze(0), dim=-1) / (torch.sum(magnitude, dim=-1) + 1e-8)
        features.append(spectral_centroid.unsqueeze(-1))
        
        # Spectral bandwidth
        spectral_bandwidth = torch.std(magnitude, dim=-1)
        features.append(spectral_bandwidth.unsqueeze(-1))
        
        # Concatenate features
        spectrum_features = torch.cat(features, dim=-1)
        
        # Pad or truncate to expected size
        expected_size = 128
        if spectrum_features.size(-1) < expected_size:
            padding = expected_size - spectrum_features.size(-1)
            spectrum_features = F.pad(spectrum_features, (0, padding))
        elif spectrum_features.size(-1) > expected_size:
            spectrum_features = spectrum_features[:, :expected_size]
        
        return spectrum_features
    
    def _create_lidar_audio_sources(self, spectrum_features: torch.Tensor, 
                                      head_tracking: Dict[str, torch.Tensor]) -> List[Dict[str, torch.Tensor]]:
        """Create audio sources based on LIDAR detection"""
        batch_size = spectrum_features.size(0)
        audio_sources = []
        
        for b in range(batch_size):
            # Find spectrum peaks (LIDAR detection points)
            magnitude = spectrum_features[b, :128]  # First 128 features are magnitude
            
            # Find peaks
            threshold = torch.mean(magnitude) + torch.std(magnitude) * 0.3
            peaks = []
            
            for i in range(1, magnitude.size(-1) - 1):
                if (magnitude[i] > threshold and 
                    magnitude[i] > magnitude[i-1] and 
                    magnitude[i] > magnitude[i+1]):
                    peaks.append(i)
            
            # Create audio sources from peaks
            for peak_idx in peaks[:self.config.max_audio_sources]:
                # Convert peak to 3D position using head orientation
                position = self._spectrum_peak_to_3d_position(peak_idx, head_tracking, b)
                
                # Create audio for this source
                audio = self._generate_audio_for_source(peak_idx, magnitude[peak_idx])
                
                audio_sources.append({
                    "position": position,
                    "audio": audio,
                    "frequency": self._peak_to_frequency(peak_idx),
                    "magnitude": magnitude[peak_idx],
                    "peak_index": peak_idx
                })
        
        return audio_sources
    
    def _spectrum_peak_to_3d_position(self, peak_idx: int, head_tracking: Dict[str, torch.Tensor], 
                                      batch_idx: int) -> torch.Tensor:
        """Convert spectrum peak to 3D position using head orientation"""
        # Map peak index to frequency
        freq = self._peak_to_frequency(peak_idx)
        
        # Normalize frequency to bubble radius
        freq_normalized = (freq - 20.0) / (20000.0 - 20.0)
        radius = freq_normalized * self.config.lidar_range
        
        # Use head orientation to determine position
        x_tilt = head_tracking["x_tilt"][batch_idx]
        y_tilt = head_tracking["y_tilt"][batch_idx]
        z_rotation = head_tracking["z_rotation"][batch_idx]
        
        # Convert to spherical coordinates
        theta = x_tilt * math.pi  # Azimuth from X tilt
        phi = (y_tilt + math.pi/2) * math.pi / 2  # Elevation from Y tilt
        
        # Convert to Cartesian
        x = radius * torch.cos(theta) * torch.sin(phi)
        y = radius * torch.sin(theta) * torch.sin(phi)
        z = radius * torch.cos(phi)
        
        # Add head position offset
        head_pos = head_tracking["position"][batch_idx]
        x += head_pos[0]
        y += head_pos[1]
        z += head_pos[2]
        
        return torch.tensor([x, y, z])
    
    def _peak_to_frequency(self, peak_idx: int) -> float:
        """Convert peak index to frequency"""
        # Simple linear mapping (in real implementation, this would use actual frequency bins)
        return 20.0 + peak_idx * (20000.0 - 20.0) / 128.0
    
    def _generate_audio_for_source(self, peak_idx: int, magnitude: float) -> torch.Tensor:
        """Generate audio for a specific source"""
        # Generate audio based on peak characteristics
        freq = self._peak_to_frequency(peak_idx)
        
        # Create sine wave at peak frequency
        duration = 1.0  # 1 second
        t = torch.linspace(0, duration, int(self.sample_rate * duration), device=self.device)
        
        # Generate audio with harmonics
        audio = magnitude * torch.sin(2 * math.pi * freq * t)
        
        # Add harmonics for richness
        for harmonic in [2, 3, 4]:
            audio += (magnitude / harmonic) * torch.sin(2 * math.pi * freq * harmonic * t)
        
        return audio.unsqueeze(0)
    
    def _manage_multi_bubbles(self, head_tracking: Dict[str, torch.Tensor], 
                                bubble_result: Dict[str, torch.Tensor]):
        """Manage multiple bubbles in the system"""
        # Register main bubble
        main_center = head_tracking["position"]
        main_intensity = torch.ones_like(main_center) * 0.8
        main_orientation = torch.stack([head_tracking["x_tilt"], head_tracking["y_tilt"], head_tracking["z_rotation"]], dim=-1)
        
        self.bubble_manager.register_bubble(main_center, main_intensity, main_orientation)
        
        # Detect and merge overlapping bubbles
        if torch.sum(self.bubble_manager.bubble_intensities > 0.1) > 1:
            merged_center = self.bubble_manager.merge_overlapping_bubbles()
            # Update main bubble center
            self.bubble_manager.active_bubbles[0] = merged_center
    
    def _create_lidar_scan_data(self, head_tracking: Dict[str, torch.Tensor], 
                                bubble_result: Dict[str, torch.Tensor]) -> Dict[str, any]:
        """Create LIDAR scan data"""
        return {
            "scan_points": self.bubble_manager.active_bubbles,
            "scan_intensities": self.bubble_manager.bubble_intensities,
            "scan_orientations": self.bubble_manager.bubble_orientations,
            "head_position": head_tracking["position"],
            "head_orientation": torch.stack([head_tracking["x_tilt"], head_tracking["y_tilt"], head_tracking["z_rotation"]]),
            "detection_confidence": head_tracking["confidence"],
            "movement_velocity": head_tracking["velocity"]
        }
    
    def _add_to_buffer(self, audio: torch.Tensor):
        """Add audio to processing buffer"""
        batch_size, seq_len = audio.shape
        
        # Add to buffer (circular)
        end_pos = self.buffer_write_pos + seq_len
        if end_pos <= self.processing_buffer.size(1):
            self.processing_buffer[:, self.buffer_write_pos:end_pos] = audio
        else:
            # Wrap around
            first_part = self.processing_buffer[:, self.buffer_write_pos:]
            second_part = audio[:, :end_pos - self.processing_buffer.size(1)]
            self.processing_buffer[:, self.buffer_write_pos:] = first_part
            self.processing_buffer[:, :second_part.size(1)] = second_part
        
        self.buffer_write_pos = end_pos % self.processing_buffer.size(1)
    
    def get_movement_direction(self) -> str:
        """Get current movement direction"""
        return self.head_tracker.get_movement_direction()
    
    def get_lidar_status(self) -> Dict[str, any]:
        """Get LIDAR system status"""
        return {
            "initialized": self.initialized,
            "device": str(self.device),
            "config": {
                "lidar_range": self.config.lidar_range,
                "angular_resolution": self.config.angular_resolution,
                "detection_precision": self.config.detection_precision,
                "scan_rate": self.config.scan_rate,
                "head_tracking_sensitivity": self.config.head_tracking_sensitivity,
                "max_audio_sources": self.config.max_audio_sources,
                "enable_multi_bubble": self.config.enable_multi_bubble,
                "max_bubbles": self.config.max_bubbles
            },
            "active_bubbles": self.bubble_manager.get_active_bubbles() if self.config.enable_multi_bubble else None,
            "movement_direction": self.get_movement_direction()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        del self.head_tracker
        del self.bubble_manager
        del self.bubble_system
        torch.cuda.empty_cache()
        logging.info("LIDAR Audio Processor cleanup completed")


def create_lidar_audio_processor(config: Optional[LIDARAudioConfig] = None, 
                               sample_rate: int = 22050) -> LIDARAudioProcessor:
    """
    Factory function to create LIDAR audio processor
    
    Args:
        config: LIDAR configuration
        sample_rate: Audio sample rate
        
    Returns:
        LIDARAudioProcessor instance
    """
    if config is None:
        config = LIDARAudioConfig()
    
    processor = LIDARAudioProcessor(config, sample_rate)
    processor.initialize()
    
    return processor


def create_high_precision_lidar_processor(sample_rate: int = 22050) -> LIDARAudioProcessor:
    """
    Create high-precision LIDAR audio processor
    
    Returns:
        Optimized LIDARAudioProcessor instance
    """
    config = LIDARAudioConfig(
        lidar_range=3.0,              # Moderate range for precision
        angular_resolution=0.5,        # High angular resolution
        detection_precision=0.01,      # High precision
        scan_rate=60.0,                # High scan rate
        head_tracking_sensitivity=0.9,    # High sensitivity
        tilt_detection_threshold=0.1,     # Low threshold for detection
        spatial_audio_resolution=0.02,  # High spatial resolution
        max_audio_sources=128,          # Many audio sources
        enable_multi_bubble=True,
        max_bubbles=16,                 # More bubbles
        bubble_overlap_threshold=0.2,    # Lower threshold for more merging
        enable_real_time=True,
        processing_buffer_size=2048,
        latency_target_ms=5.0
    )
    
    return create_lidar_audio_processor(config, sample_rate)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create LIDAR processor
    processor = create_lidar_audio_processor()
    
    # Create sample audio with multiple frequency components
    sample_rate = 22050
    duration = 2.0
    t = torch.linspace(0, duration, int(sample_rate * duration))
    
    # Create complex audio with multiple sources
    audio = (torch.sin(2 * torch.pi * 440 * t) + 
             0.5 * torch.sin(2 * torch.pi * 880 * t) +
             0.3 * torch.sin(2 * torch.pi * 1760 * t) +
             0.2 * torch.sin(2 * torch.pi * 3520 * t))
    
    # Process with LIDAR
    result = processor.process_audio_with_lidar(audio.unsqueeze(0))
    
    print(f"Head tracking: {result['head_tracking']}")
    print(f"Movement direction: {result['movement_direction']}")
    print(f"LIDAR scan points: {result['lidar_scan']['scan_points'].shape}")
    print(f"Audio sources: {len(result['audio_sources'])}")
    
    # Get LIDAR status
    status = processor.get_lidar_status()
    print(f"LIDAR status: {status}")
    
    # Cleanup
    processor.cleanup()
    
    print("LIDAR Audio Processor example completed")
