# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
3D Spectrum Bubble Generator
Creates 3D bubbles from spectrum signals for precise 3D spatial audio fields
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import math
from nemo.utils import logging


@dataclass
class SpectrumBubbleConfig:
    """Configuration for 3D spectrum bubble generation"""
    # Bubble dimensions
    bubble_radius: float = 1.0  # meters
    bubble_resolution: int = 64   # points per dimension
    bubble_center: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # X, Y, Z center
    
    # Spectrum processing
    spectrum_bins: int = 128
    frequency_range: Tuple[float, float] = (20.0, 20000.0)  # Hz
    spectrum_smoothing: float = 0.1
    orientation_sensitivity: float = 0.8
    
    # Head tracking
    head_tilt_threshold: float = 0.3  # Threshold for head tilt detection
    x_tilt_sensitivity: float = 0.7      # Sensitivity for X-axis tilt
    y_tilt_sensitivity: float = 0.8      # Sensitivity for Y-axis tilt (head tilt)
    
    # 3D spatial audio
    spatial_resolution: float = 0.1     # meters between audio points
    max_audio_sources: int = 16         # Maximum audio sources in bubble
    audio_falloff: float = 0.8           # Audio falloff factor
    
    # LIDAR-like detection
    enable_lidar_detection: bool = True
    detection_precision: float = 0.05    # Detection precision in meters
    orientation_tracking: bool = True
    
    # Multi-audio entry points
    enable_multi_entry: bool = True
    entry_point_resolution: int = 8      # Points per entry point
    dynamic_bubble: bool = True          # Dynamic bubble adjustment


class SpectrumAnalyzer(nn.Module):
    """Spectrum analyzer for bubble generation"""
    
    def __init__(self, config: SpectrumBubbleConfig):
        super().__init__()
        self.config = config
        
        # FFT parameters
        self.n_fft = 2048
        self.hop_length = 512
        self.win_length = 2048
        
        # Frequency bins
        self.freq_bins = torch.linspace(config.frequency_range[0], config.frequency_range[1], config.spectrum_bins)
        
        # Spectrum processing layers
        self.spectrum_processor = nn.Sequential(
            nn.Linear(config.spectrum_bins, 256),
            nn.GELU(),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 3),  # X, Y, Z orientation
            nn.Tanh()
        )
        
        # Orientation detection layers
        self.orientation_detector = nn.Sequential(
            nn.Linear(config.spectrum_bins, 128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 3),  # X_tilt, Y_tilt, confidence
            nn.Sigmoid()
        )
        
    def analyze_spectrum(self, audio: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Analyze audio spectrum for bubble generation
        
        Args:
            audio: Input audio tensor [batch_size, sequence_length]
            
        Returns:
            Dictionary with spectrum analysis results
        """
        batch_size, seq_len = audio.shape
        
        # Compute STFT
        stft = torch.stft(
            audio,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=torch.hann_window(self.n_fft, device=audio.device),
            return_complex=True
        )
        
        # Get magnitude spectrum
        magnitude = torch.abs(stft)  # [batch_size, n_fft//2+1, time_frames]
        
        # Average over time frames
        avg_magnitude = torch.mean(magnitude, dim=-1)  # [batch_size, n_fft//2+1]
        
        # Interpolate to desired spectrum bins
        current_freq_bins = torch.fft.rfftfreq(self.n_fft, 1.0 / 22050, device=audio.device)
        avg_magnitude = F.interpolate(
            avg_magnitude.unsqueeze(1), 
            size=self.config.spectrum_bins, 
            mode='linear', 
            align_corners=False
        ).squeeze(1)
        
        # Apply spectrum smoothing
        smoothed_magnitude = self._apply_spectrum_smoothing(avg_magnitude)
        
        # Process spectrum for 3D orientation
        orientation = self.spectrum_processor(smoothed_magnitude)
        
        # Detect head orientation
        head_orientation = self.orientation_detector(smoothed_magnitude)
        
        return {
            "magnitude": avg_magnitude,
            "smoothed_magnitude": smoothed_magnitude,
            "orientation": orientation,  # X, Y, Z bubble center
            "head_orientation": head_orientation,  # X_tilt, Y_tilt, confidence
            "freq_bins": self.freq_bins
        }
    
    def _apply_spectrum_smoothing(self, magnitude: torch.Tensor) -> torch.Tensor:
        """Apply smoothing to spectrum"""
        # Simple exponential smoothing
        smoothed = magnitude.clone()
        for i in range(1, magnitude.size(-1)):
            smoothed[:, i] = self.config.spectrum_smoothing * smoothed[:, i-1] + \
                           (1 - self.config.spectrum_smoothing) * magnitude[:, i]
        return smoothed


class Bubble3DGenerator(nn.Module):
    """3D bubble generator from spectrum data"""
    
    def __init__(self, config: SpectrumBubbleConfig):
        super().__init__()
        self.config = config
        
        # Create 3D grid
        self._create_3d_grid()
        
        # Bubble shape generator
        self.bubble_generator = nn.Sequential(
            nn.Linear(3, 128),  # X, Y, Z center
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),  # Bubble intensity
            nn.Sigmoid()
        )
        
        # Orientation processor
        self.orientation_processor = nn.Sequential(
            nn.Linear(3, 64),  # X_tilt, Y_tilt, confidence
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 3),  # Processed orientation
            nn.Tanh()
        )
        
        # Multi-entry point generator
        if self.config.enable_multi_entry:
            self.entry_generator = nn.Sequential(
                nn.Linear(3, 128),  # Orientation + spectrum
                nn.GELU(),
                nn.Linear(128, 64),
                nn.GELU(),
                nn.Linear(64, self.config.entry_point_resolution * 3),  # Entry points
                nn.Sigmoid()
            )
        
    def _create_3d_grid(self):
        """Create 3D grid for bubble"""
        # Create 3D coordinates
        x = torch.linspace(-self.config.bubble_radius, self.config.bubble_radius, self.config.bubble_resolution)
        y = torch.linspace(-self.config.bubble_radius, self.config.bubble_radius, self.config.bubble_resolution)
        z = torch.linspace(-self.config.bubble_radius, self.config.bubble_radius, self.config.bubble_resolution)
        
        # Create 3D meshgrid
        X, Y, Z = torch.meshgrid(x, y, z, indexing='ij')
        
        # Store as buffers
        self.register_buffer('grid_x', X)
        self.register_buffer('grid_y', Y)
        self.register_buffer('grid_z', Z)
        
        # Calculate distances from center
        center_x, center_y, center_z = self.config.bubble_center
        distances = torch.sqrt((X - center_x)**2 + (Y - center_y)**2 + (Z - center_z)**2)
        self.register_buffer('distances', distances)
        
        # Create bubble mask
        bubble_mask = distances <= self.config.bubble_radius
        self.register_buffer('bubble_mask', bubble_mask)
        
        # Create spherical coordinates for orientation
        theta = torch.atan2(Y - center_y, X - center_x)  # Azimuth
        phi = torch.acos(torch.clamp((Z - center_z) / (distances + 1e-8), -1, 1))  # Elevation
        self.register_buffer('theta', theta)
        self.register_buffer('phi', phi)
    
    def generate_3d_bubble(self, spectrum_data: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        Generate 3D bubble from spectrum data
        
        Args:
            spectrum_data: Spectrum analysis results
            
        Returns:
            Dictionary with 3D bubble data
        """
        batch_size = spectrum_data["orientation"].size(0)
        
        # Get bubble center from spectrum
        bubble_center = spectrum_data["orientation"]  # [batch_size, 3]
        
        # Process head orientation
        head_orientation = self.orientation_processor(spectrum_data["head_orientation"])
        
        # Generate bubble intensity at center
        bubble_intensity = self.bubble_generator(bubble_center)
        
        # Create 3D bubble intensity field
        bubble_field = torch.zeros(batch_size, self.config.bubble_resolution, 
                                    self.config.bubble_resolution, self.config.bubble_resolution,
                                    device=spectrum_data["orientation"].device)
        
        for b in range(batch_size):
            # Calculate intensity based on distance from center
            center_x, center_y, center_z = bubble_center[b]
            
            # Adjust center based on head orientation
            x_tilt, y_tilt, confidence = head_orientation[b]
            
            # Apply head tilt to bubble center (LIDAR-like tracking)
            adjusted_center_x = center_x + x_tilt * self.config.x_tilt_sensitivity
            adjusted_center_y = center_y + y_tilt * self.config.y_tilt_sensitivity
            adjusted_center_z = center_z
            
            # Calculate distances from adjusted center
            distances = torch.sqrt((self.grid_x - adjusted_center_x)**2 + 
                               (self.grid_y - adjusted_center_y)**2 + 
                               (self.grid_z - adjusted_center_z)**2)
            
            # Generate bubble intensity field
            intensity = bubble_intensity[b] * torch.exp(-distances / self.config.bubble_radius)
            
            # Apply bubble mask
            intensity = intensity * self.bubble_mask.float()
            
            # Apply orientation-based modulation
            orientation_modulation = self._calculate_orientation_modulation(
                x_tilt, y_tilt, self.theta, self.phi
            )
            intensity = intensity * orientation_modulation.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
            
            bubble_field[b] = intensity
        
        # Generate multi-entry points if enabled
        entry_points = None
        if self.config.enable_multi_entry:
            entry_points = self._generate_entry_points(spectrum_data, bubble_center)
        
        return {
            "bubble_field": bubble_field,
            "bubble_center": bubble_center,
            "bubble_intensity": bubble_intensity,
            "head_orientation": head_orientation,
            "entry_points": entry_points,
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "grid_z": self.grid_z,
            "bubble_mask": self.bubble_mask
        }
    
    def _calculate_orientation_modulation(self, x_tilt: float, y_tilt: float, 
                                         theta: torch.Tensor, phi: torch.Tensor) -> torch.Tensor:
        """Calculate orientation-based modulation for bubble field"""
        # Convert head tilt to spherical coordinates
        head_theta = torch.atan2(y_tilt, x_tilt)  # Head orientation angle
        head_phi = torch.asin(torch.clamp(y_tilt, -1, 1))  # Head tilt angle
        
        # Calculate angular difference
        theta_diff = torch.cos(theta - head_theta)
        phi_diff = torch.cos(phi - head_phi)
        
        # Combine for orientation modulation
        modulation = theta_diff * phi_diff
        
        return modulation
    
    def _generate_entry_points(self, spectrum_data: Dict[str, torch.Tensor], 
                              bubble_center: torch.Tensor) -> torch.Tensor:
        """Generate multi-entry points for audio sources"""
        batch_size = bubble_center.size(0)
        
        # Combine orientation and spectrum for entry generation
        combined_input = torch.cat([
            spectrum_data["head_orientation"],
            spectrum_data["smoothed_magnitude"].mean(dim=-1, keepdim=True)
        ], dim=-1)
        
        # Generate entry points
        entry_points_flat = self.entry_generator(combined_input)
        
        # Reshape to entry points
        entry_points = entry_points_flat.view(batch_size, self.config.entry_point_resolution, 3)
        
        # Scale to bubble radius
        entry_points = entry_points * self.config.bubble_radius
        
        return entry_points


class AudioField3D(nn.Module):
    """3D audio field generator for bubble space"""
    
    def __init__(self, config: SpectrumBubbleConfig):
        super().__init__()
        self.config = config
        
        # Audio field parameters
        self.spatial_resolution = config.spatial_resolution
        self.max_audio_sources = config.max_audio_sources
        self.audio_falloff = config.audio_falloff
        
        # Audio source generator
        self.audio_source_generator = nn.Sequential(
            nn.Linear(3, 64),  # 3D position
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),  # Audio intensity
            nn.Sigmoid()
        )
        
        # Spatial audio processor
        self.spatial_processor = nn.Sequential(
            nn.Linear(3, 128),  # Position + distance
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 2),  # Left/Right audio
            nn.Tanh()
        )
        
    def generate_3d_audio_field(self, bubble_data: Dict[str, torch.Tensor], 
                                audio_sources: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """
        Generate 3D audio field from bubble and audio sources
        
        Args:
            bubble_data: 3D bubble data
            audio_sources: List of audio source data
            
        Returns:
            Dictionary with 3D audio field data
        """
        batch_size = bubble_data["bubble_field"].size(0)
        
        # Initialize audio field
        audio_field = torch.zeros(batch_size, 2,  # Stereo
                                    self.config.bubble_resolution,
                                    self.config.bubble_resolution,
                                    self.config.bubble_resolution,
                                    device=bubble_data["bubble_field"].device)
        
        # Process each audio source
        for source in audio_sources:
            source_position = source["position"]  # [batch_size, 3]
            source_audio = source["audio"]  # [batch_size, sequence_length]
            
            # Generate audio intensity at source position
            source_intensity = self.audio_source_generator(source_position)
            
            # Calculate spatial audio for each point in bubble
            for b in range(batch_size):
                # Calculate distances from source to each point
                source_x, source_y, source_z = source_position[b]
                
                distances = torch.sqrt((bubble_data["grid_x"] - source_x)**2 + 
                                   (bubble_data["grid_y"] - source_y)**2 + 
                                   (bubble_data["grid_z"] - source_z)**2)
                
                # Apply audio falloff
                audio_intensity = source_intensity[b] * torch.exp(-distances / self.audio_falloff)
                
                # Modulate by bubble field
                audio_intensity = audio_intensity * bubble_data["bubble_field"][b]
                
                # Generate spatial audio (left/right)
                for i in range(self.config.bubble_resolution):
                    for j in range(self.config.bubble_resolution):
                        for k in range(self.config.bubble_resolution):
                            if bubble_data["bubble_mask"][i, j, k]:
                                position = torch.tensor([
                                    bubble_data["grid_x"][i, j, k],
                                    bubble_data["grid_y"][i, j, k],
                                    bubble_data["grid_z"][i, j, k]
                                ], device=source_position.device)
                                
                                spatial_input = torch.cat([
                                    position - source_position[b],
                                    distances[i, j, k:k+1]
                                ])
                                
                                spatial_audio = self.spatial_processor(spatial_input)
                                
                                # Apply to audio field
                                audio_field[b, :, i, j, k] = spatial_audio * audio_intensity[i, j, k]
        
        return {
            "audio_field": audio_field,
            "bubble_mask": bubble_data["bubble_mask"],
            "grid_coordinates": {
                "x": bubble_data["grid_x"],
                "y": bubble_data["grid_y"],
                "z": bubble_data["grid_z"]
            }
        }


class SpectrumBubble3DSystem:
    """
    Complete 3D spectrum bubble system
    """
    
    def __init__(self, config: SpectrumBubbleConfig, sample_rate: int = 22050):
        self.config = config
        self.sample_rate = sample_rate
        
        # Initialize components
        self.spectrum_analyzer = SpectrumAnalyzer(config)
        self.bubble_generator = Bubble3DGenerator(config)
        self.audio_field_3d = AudioField3D(config)
        
        # Processing state
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Current bubble state
        self.current_bubble = None
        self.current_head_orientation = None
        self.current_audio_field = None
        
        # Tracking data
        self.tracking_history = []
        self.max_history_length = 100
        
        logging.info(f"3D Spectrum Bubble System initialized on device: {self.device}")
    
    def initialize(self):
        """Initialize the system"""
        self.spectrum_analyzer.to(self.device)
        self.bubble_generator.to(self.device)
        self.audio_field_3d.to(self.device)
        
        self.spectrum_analyzer.eval()
        self.bubble_generator.eval()
        self.audio_field_3d.eval()
        
        self.initialized = True
        logging.info("3D Spectrum Bubble System fully initialized")
    
    def process_spectrum_to_3d_bubble(self, audio: torch.Tensor, 
                                      audio_sources: List[Dict[str, torch.Tensor]] = None) -> Dict[str, torch.Tensor]:
        """
        Process spectrum signal to generate 3D bubble with spatial audio
        
        Args:
            audio: Input audio tensor [batch_size, sequence_length]
            audio_sources: List of audio sources with positions
            
        Returns:
            Dictionary with 3D bubble and audio field data
        """
        if not self.initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        # Ensure input is 2D
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)
        
        # Move to device
        audio = audio.to(self.device)
        
        # Step 1: Analyze spectrum
        spectrum_data = self.spectrum_analyzer.analyze_spectrum(audio)
        
        # Step 2: Generate 3D bubble
        bubble_data = self.bubble_generator.generate_3d_bubble(spectrum_data)
        
        # Step 3: Generate 3D audio field
        if audio_sources is None:
            # Create default audio sources
            audio_sources = self._create_default_audio_sources(spectrum_data)
        
        audio_field_data = self.audio_field_3d.generate_3d_audio_field(bubble_data, audio_sources)
        
        # Update current state
        self.current_bubble = bubble_data
        self.current_head_orientation = spectrum_data["head_orientation"]
        self.current_audio_field = audio_field_data
        
        # Add to tracking history
        self._add_to_tracking_history(spectrum_data, bubble_data)
        
        return {
            "spectrum_data": spectrum_data,
            "bubble_data": bubble_data,
            "audio_field_data": audio_field_data,
            "head_orientation": spectrum_data["head_orientation"],
            "tracking_history": self.tracking_history[-1] if self.tracking_history else None
        }
    
    def _create_default_audio_sources(self, spectrum_data: Dict[str, torch.Tensor]) -> List[Dict[str, torch.Tensor]]:
        """Create default audio sources from spectrum data"""
        batch_size = spectrum_data["orientation"].size(0)
        audio_sources = []
        
        # Create audio sources based on spectrum peaks
        for b in range(batch_size):
            # Find spectrum peaks
            magnitude = spectrum_data["smoothed_magnitude"][b]
            peaks = self._find_spectrum_peaks(magnitude)
            
            for peak_idx in peaks[:self.config.max_audio_sources]:
                # Convert peak to 3D position
                freq = spectrum_data["freq_bins"][peak_idx]
                position = self._frequency_to_3d_position(freq, spectrum_data["orientation"][b])
                
                # Create dummy audio (in real implementation, this would be actual audio)
                audio = torch.randn(1, 1024)  # Placeholder
                
                audio_sources.append({
                    "position": position.unsqueeze(0),
                    "audio": audio,
                    "frequency": freq,
                    "magnitude": magnitude[peak_idx]
                })
        
        return audio_sources
    
    def _find_spectrum_peaks(self, magnitude: torch.Tensor) -> List[int]:
        """Find peaks in spectrum magnitude"""
        # Simple peak detection
        peaks = []
        threshold = torch.mean(magnitude) + torch.std(magnitude) * 0.5
        
        for i in range(1, magnitude.size(-1) - 1):
            if (magnitude[i] > threshold and 
                magnitude[i] > magnitude[i-1] and 
                magnitude[i] > magnitude[i+1]):
                peaks.append(i)
        
        return peaks
    
    def _frequency_to_3d_position(self, frequency: float, orientation: torch.Tensor) -> torch.Tensor:
        """Convert frequency to 3D position in bubble"""
        # Map frequency to bubble radius (low freq = center, high freq = edge)
        freq_normalized = (frequency - self.config.frequency_range[0]) / \
                        (self.config.frequency_range[1] - self.config.frequency_range[0])
        
        # Convert to radial position
        radius = freq_normalized * self.config.bubble_radius
        
        # Use orientation to determine angle
        theta = orientation[0]  # X component for angle
        phi = orientation[1]    # Y component for elevation
        
        # Convert spherical to Cartesian
        x = radius * torch.cos(theta) * torch.sin(phi)
        y = radius * torch.sin(theta) * torch.sin(phi)
        z = radius * torch.cos(phi)
        
        return torch.tensor([x, y, z])
    
    def _add_to_tracking_history(self, spectrum_data: Dict[str, torch.Tensor], 
                               bubble_data: Dict[str, torch.Tensor]):
        """Add data to tracking history"""
        history_entry = {
            "timestamp": torch.tensor([torch.cuda.Event().record() if self.device.type == 'cuda' else 0], 
                                   device=self.device),
            "head_orientation": spectrum_data["head_orientation"].cpu(),
            "bubble_center": bubble_data["bubble_center"].cpu(),
            "bubble_intensity": bubble_data["bubble_intensity"].cpu()
        }
        
        self.tracking_history.append(history_entry)
        
        # Limit history length
        if len(self.tracking_history) > self.max_history_length:
            self.tracking_history.pop(0)
    
    def get_head_orientation(self) -> torch.Tensor:
        """Get current head orientation"""
        if self.current_head_orientation is not None:
            return self.current_head_orientation.cpu()
        return torch.zeros(3)
    
    def get_bubble_center(self) -> torch.Tensor:
        """Get current bubble center"""
        if self.current_bubble is not None:
            return self.current_bubble["bubble_center"].cpu()
        return torch.zeros(3)
    
    def get_audio_at_position(self, position: torch.Tensor) -> torch.Tensor:
        """Get audio at specific 3D position"""
        if self.current_audio_field is None:
            return torch.zeros(2)
        
        # Find nearest grid point
        x_idx = torch.argmin(torch.abs(self.current_audio_field["grid_coordinates"]["x"] - position[0]))
        y_idx = torch.argmin(torch.abs(self.current_audio_field["grid_coordinates"]["y"] - position[1]))
        z_idx = torch.argmin(torch.abs(self.current_audio_field["grid_coordinates"]["z"] - position[2]))
        
        # Get audio at that position
        audio = self.current_audio_field["audio_field"][0, :, x_idx, y_idx, z_idx]
        
        return audio
    
    def get_system_status(self) -> Dict[str, any]:
        """Get system status"""
        return {
            "initialized": self.initialized,
            "device": str(self.device),
            "sample_rate": self.sample_rate,
            "config": {
                "bubble_radius": self.config.bubble_radius,
                "bubble_resolution": self.config.bubble_resolution,
                "spectrum_bins": self.config.spectrum_bins,
                "frequency_range": self.config.frequency_range,
                "max_audio_sources": self.config.max_audio_sources,
                "enable_lidar_detection": self.config.enable_lidar_detection,
                "enable_multi_entry": self.config.enable_multi_entry
            },
            "tracking_history_length": len(self.tracking_history),
            "current_state": {
                "has_bubble": self.current_bubble is not None,
                "has_audio_field": self.current_audio_field is not None,
                "head_orientation": self.get_head_orientation().tolist() if self.current_head_orientation is not None else [0, 0, 0],
                "bubble_center": self.get_bubble_center().tolist() if self.current_bubble is not None else [0, 0, 0]
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        del self.spectrum_analyzer
        del self.bubble_generator
        del self.audio_field_3d
        torch.cuda.empty_cache()
        logging.info("3D Spectrum Bubble System cleanup completed")


def create_spectrum_bubble_system(config: Optional[SpectrumBubbleConfig] = None, 
                               sample_rate: int = 22050) -> SpectrumBubble3DSystem:
    """
    Factory function to create 3D spectrum bubble system
    
    Args:
        config: Bubble configuration
        sample_rate: Audio sample rate
        
    Returns:
        SpectrumBubble3DSystem instance
    """
    if config is None:
        config = SpectrumBubbleConfig()
    
    system = SpectrumBubble3DSystem(config, sample_rate)
    system.initialize()
    
    return system


def create_lidar_audio_bubble_system(sample_rate: int = 22050) -> SpectrumBubble3DSystem:
    """
    Create system optimized for LIDAR-like audio bubble detection
    
    Returns:
        Optimized SpectrumBubble3DSystem instance
    """
    config = SpectrumBubbleConfig(
        bubble_radius=2.0,              # Larger bubble for LIDAR range
        bubble_resolution=128,           # Higher resolution for precision
        spectrum_bins=256,              # More spectrum bins for detail
        frequency_range=(20.0, 20000.0),  # Full audio frequency range
        orientation_sensitivity=0.9,      # High sensitivity for orientation
        head_tilt_threshold=0.2,         # Lower threshold for detection
        x_tilt_sensitivity=0.8,          # High X-axis sensitivity
        y_tilt_sensitivity=0.9,          # High Y-axis sensitivity (head tilt)
        spatial_resolution=0.05,          # Higher spatial resolution
        max_audio_sources=32,             # More audio sources
        enable_lidar_detection=True,
        detection_precision=0.02,         # Higher precision
        orientation_tracking=True,
        enable_multi_entry=True,
        entry_point_resolution=16,         # More entry points
        dynamic_bubble=True
    )
    
    return create_spectrum_bubble_system(config, sample_rate)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create LIDAR audio bubble system
    system = create_lidar_audio_bubble_system()
    
    # Create sample audio with spectrum content
    sample_rate = 22050
    duration = 2.0
    t = torch.linspace(0, duration, int(sample_rate * duration))
    
    # Create audio with multiple frequency components
    audio = torch.sin(2 * torch.pi * 440 * t) + 0.5 * torch.sin(2 * torch.pi * 880 * t)
    audio += 0.3 * torch.sin(2 * torch.pi * 2000 * t) + 0.2 * torch.sin(2 * torch.pi * 4000 * t)
    
    # Process spectrum to 3D bubble
    result = system.process_spectrum_to_3d_bubble(audio.unsqueeze(0))
    
    print(f"3D bubble generated with shape: {result['bubble_data']['bubble_field'].shape}")
    print(f"Head orientation: {result['head_orientation']}")
    print(f"Bubble center: {result['bubble_data']['bubble_center']}")
    
    # Get audio at specific position
    test_position = torch.tensor([0.5, 0.3, 0.2])  # X, Y, Z position in bubble
    audio_at_position = system.get_audio_at_position(test_position)
    print(f"Audio at position {test_position.tolist()}: {audio_at_position}")
    
    # Get system status
    status = system.get_system_status()
    print(f"System status: {status}")
    
    # Cleanup
    system.cleanup()
    
    print("3D Spectrum Bubble System example completed")
