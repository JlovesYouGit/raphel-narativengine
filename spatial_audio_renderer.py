# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Spatial Audio Renderer
Advanced 3D spatial audio rendering for bubble-based audio fields
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
class SpatialAudioConfig:
    """Configuration for spatial audio rendering"""
    # Rendering parameters
    sample_rate: int = 22050
    channels: int = 2  # Stereo
    buffer_size: int = 1024
    
    # 3D audio parameters
    hrtf_enabled: bool = True
    hrtf_resolution: int = 360  # Degrees
    elevation_resolution: int = 90  # Degrees
    
    # Spatial processing
    doppler_enabled: bool = True
    distance_attenuation: float = 1.0  # Inverse square law
    air_absorption: float = 0.001  # Air absorption coefficient
    
    # Bubble rendering
    bubble_falloff: float = 0.8
    max_render_distance: float = 10.0  # meters
    min_render_distance: float = 0.1  # meters
    
    # Real-time processing
    enable_real_time: bool = True
    processing_latency_ms: float = 5.0


class HRTFProcessor(nn.Module):
    """Head-Related Transfer Function processor"""
    
    def __init__(self, config: SpatialAudioConfig):
        super().__init__()
        self.config = config
        
        # HRTF parameters
        self.hrtf_resolution = config.hrtf_resolution
        self.elevation_resolution = config.elevation_resolution
        
        # Create HRTF database (simplified)
        self._create_hrtf_database()
        
        # HRTF interpolation network
        self.hrtf_interpolator = nn.Sequential(
            nn.Linear(2, 128),  # Azimuth, elevation
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 2),  # Left, right gains
            nn.Sigmoid()
        )
        
    def _create_hrtf_database(self):
        """Create simplified HRTF database"""
        # Create HRTF lookup table
        azimuths = torch.linspace(0, 360, self.hrtf_resolution)
        elevations = torch.linspace(-90, 90, self.elevation_resolution)
        
        # Initialize HRTF gains (simplified model)
        hrtf_left = torch.zeros(self.hrtf_resolution, self.elevation_resolution)
        hrtf_right = torch.zeros(self.hrtf_resolution, self.elevation_resolution)
        
        for i, az in enumerate(azimuths):
            for j, el in enumerate(elevations):
                # Simplified HRTF model
                # Left ear gets more from left side
                left_gain = 0.5 + 0.5 * torch.cos(torch.tensor(az * math.pi / 180))
                # Right ear gets more from right side
                right_gain = 0.5 + 0.5 * torch.cos(torch.tensor((az - 180) * math.pi / 180))
                
                # Elevation affects both ears
                elevation_factor = 0.8 + 0.2 * torch.cos(torch.tensor(el * math.pi / 180))
                
                hrtf_left[i, j] = left_gain * elevation_factor
                hrtf_right[i, j] = right_gain * elevation_factor
        
        self.register_buffer('hrtf_left', hrtf_left)
        self.register_buffer('hrtf_right', hrtf_right)
        self.register_buffer('azimuths', azimuths)
        self.register_buffer('elevations', elevations)
    
    def process_hrtf(self, audio: torch.Tensor, position: torch.Tensor, 
                     listener_position: torch.Tensor) -> torch.Tensor:
        """
        Process audio with HRTF for spatial positioning
        
        Args:
            audio: Input audio tensor [batch_size, sequence_length]
            position: Source position [X, Y, Z]
            listener_position: Listener position [X, Y, Z]
            
        Returns:
            Processed stereo audio [batch_size, 2, sequence_length]
        """
        # Calculate relative position
        relative_pos = position - listener_position
        
        # Convert to spherical coordinates
        distance = torch.norm(relative_pos)
        azimuth = torch.atan2(relative_pos[1], relative_pos[0]) * 180 / math.pi
        elevation = torch.asin(relative_pos[2] / (distance + 1e-8)) * 180 / math.pi
        
        # Normalize angles
        azimuth = (azimuth + 360) % 360
        elevation = (elevation + 90) % 180
        
        # Interpolate HRTF gains
        hrtf_gains = self._interpolate_hrtf(azimuth, elevation)
        
        # Apply HRTF to audio
        left_audio = audio * hrtf_gains[0]
        right_audio = audio * hrtf_gains[1]
        
        return torch.stack([left_audio, right_audio], dim=1)
    
    def _interpolate_hrtf(self, azimuth: float, elevation: float) -> torch.Tensor:
        """Interpolate HRTF gains for continuous positioning"""
        # Find nearest HRTF indices
        az_idx = int(azimuth / 360 * self.hrtf_resolution) % self.hrtf_resolution
        el_idx = int(elevation / 180 * self.elevation_resolution) % self.elevation_resolution
        
        # Get nearest HRTF gains
        left_gain = self.hrtf_left[az_idx, el_idx]
        right_gain = self.hrtf_right[az_idx, el_idx]
        
        return torch.tensor([left_gain, right_gain])


class DistanceAttenuator(nn.Module):
    """Distance-based audio attenuation"""
    
    def __init__(self, config: SpatialAudioConfig):
        super().__init__()
        self.config = config
        
        # Attenuation parameters
        self.distance_attenuation = config.distance_attenuation
        self.max_render_distance = config.max_render_distance
        self.min_render_distance = config.min_render_distance
        
        # Air absorption parameters
        self.air_absorption = config.air_absorption
        
        # Frequency-dependent absorption
        self.frequency_absorption = nn.Parameter(torch.tensor([0.001, 0.002, 0.003, 0.004]))
        
    def apply_distance_attenuation(self, audio: torch.Tensor, distance: float) -> torch.Tensor:
        """
        Apply distance-based attenuation to audio
        
        Args:
            audio: Input audio tensor
            distance: Distance from source to listener
            
        Returns:
            Attenuated audio tensor
        """
        # Clamp distance to render range
        distance = torch.clamp(torch.tensor(distance), self.min_render_distance, self.max_render_distance)
        
        # Apply inverse square law attenuation
        attenuation = 1.0 / (distance ** self.distance_attenuation)
        
        # Apply air absorption
        air_absorption_factor = torch.exp(-self.air_absorption * distance)
        
        # Combine attenuation factors
        total_attenuation = attenuation * air_absorption_factor
        
        return audio * total_attenuation


class DopplerProcessor(nn.Module):
    """Doppler effect processor"""
    
    def __init__(self, config: SpatialAudioConfig):
        super().__init__()
        self.config = config
        
        # Speed of sound (m/s)
        self.speed_of_sound = 343.0
        
        # Doppler calculation parameters
        self.previous_positions = {}
        self.previous_timestamps = {}
        
    def apply_doppler_effect(self, audio: torch.Tensor, source_position: torch.Tensor,
                           listener_position: torch.Tensor, source_id: int = 0) -> torch.Tensor:
        """
        Apply Doppler effect to audio based on relative motion
        
        Args:
            audio: Input audio tensor
            source_position: Current source position
            listener_position: Current listener position
            source_id: Source ID for tracking
            
        Returns:
            Audio with Doppler effect applied
        """
        # Get current timestamp
        current_time = torch.cuda.Event().record() if torch.cuda.is_available() else 0
        
        # Calculate relative velocity
        if source_id in self.previous_positions:
            # Calculate velocity
            dt = 0.033  # Assume 30 FPS (33ms per frame)
            dx = source_position - self.previous_positions[source_id]
            velocity = dx / dt
            
            # Calculate relative velocity towards listener
            relative_pos = listener_position - source_position
            distance = torch.norm(relative_pos)
            relative_direction = relative_pos / (distance + 1e-8)
            
            # Radial velocity (positive = approaching)
            radial_velocity = torch.dot(velocity, relative_direction)
            
            # Calculate Doppler shift
            doppler_factor = (self.speed_of_sound + radial_velocity) / self.speed_of_sound
            
            # Apply Doppler shift (simplified - just pitch shift)
            # In real implementation, this would use time-stretching
            doppler_audio = audio * doppler_factor
        else:
            doppler_audio = audio
        
        # Update position tracking
        self.previous_positions[source_id] = source_position
        self.previous_timestamps[source_id] = current_time
        
        return doppler_audio


class BubbleSpatialRenderer(nn.Module):
    """3D bubble spatial audio renderer"""
    
    def __init__(self, config: SpatialAudioConfig):
        super().__init__()
        self.config = config
        
        # Initialize components
        self.hrtf_processor = HRTFProcessor(config)
        self.distance_attenuator = DistanceAttenuator(config)
        self.doppler_processor = DopplerProcessor(config)
        
        # Rendering parameters
        self.bubble_falloff = config.bubble_falloff
        self.max_render_distance = config.max_render_distance
        
        # Audio mixing network
        self.audio_mixer = nn.Sequential(
            nn.Linear(2, 64),  # Left, right channels
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 2),  # Mixed output
            nn.Tanh()
        )
        
        # Bubble field processor
        self.bubble_field_processor = nn.Sequential(
            nn.Linear(3, 128),  # X, Y, Z position
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),  # Field intensity
            nn.Sigmoid()
        )
        
    def render_bubble_audio_field(self, bubble_data: Dict[str, torch.Tensor],
                                audio_sources: List[Dict[str, torch.Tensor]],
                                listener_position: torch.Tensor) -> torch.Tensor:
        """
        Render spatial audio from 3D bubble field
        
        Args:
            bubble_data: 3D bubble field data
            audio_sources: List of audio sources
            listener_position: Listener position in 3D space
            
        Returns:
            Rendered stereo audio
        """
        # Initialize output audio
        batch_size = bubble_data["bubble_field"].size(0)
        output_audio = torch.zeros(batch_size, 2, self.config.buffer_size, device=bubble_data["bubble_field"].device)
        
        # Process each audio source
        for source in audio_sources:
            source_position = source["position"]
            source_audio = source["audio"]
            source_id = source.get("id", 0)
            
            # Calculate distance
            distance = torch.norm(source_position - listener_position)
            
            # Skip if too far
            if distance > self.max_render_distance:
                continue
            
            # Apply distance attenuation
            attenuated_audio = self.distance_attenuator.apply_distance_attenuation(source_audio, distance)
            
            # Apply Doppler effect
            if self.config.doppler_enabled:
                doppler_audio = self.doppler_processor.apply_doppler_effect(
                    attenuated_audio, source_position, listener_position, source_id
                )
            else:
                doppler_audio = attenuated_audio
            
            # Apply HRTF for spatial positioning
            if self.config.hrtf_enabled:
                spatial_audio = self.hrtf_processor.process_hrtf(
                    doppler_audio, source_position, listener_position
                )
            else:
                # Simple panning
                pan = (source_position[0] + 1.0) / 2.0  # Normalize to 0-1
                left_gain = 1.0 - pan
                right_gain = pan
                left_audio = doppler_audio * left_gain
                right_audio = doppler_audio * right_gain
                spatial_audio = torch.stack([left_audio, right_audio], dim=1)
            
            # Apply bubble field modulation
            bubble_modulation = self._get_bubble_modulation(source_position, bubble_data)
            spatial_audio = spatial_audio * bubble_modulation
            
            # Mix into output
            min_len = min(spatial_audio.size(-1), output_audio.size(-1))
            output_audio[:, :, :min_len] += spatial_audio[:, :, :min_len]
        
        # Normalize output
        output_audio = torch.clamp(output_audio, -1.0, 1.0)
        
        return output_audio
    
    def _get_bubble_modulation(self, position: torch.Tensor, bubble_data: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Get bubble field modulation at position"""
        # Find nearest bubble field point
        grid_x = bubble_data["grid_x"]
        grid_y = bubble_data["grid_y"]
        grid_z = bubble_data["grid_z"]
        
        # Calculate distances to grid points
        distances = torch.sqrt((grid_x - position[0])**2 + 
                             (grid_y - position[1])**2 + 
                             (grid_z - position[2])**2)
        
        # Find nearest point
        min_dist_idx = torch.argmin(distances)
        
        # Get bubble field intensity at that point
        bubble_field = bubble_data["bubble_field"]
        
        # Convert to 3D indices
        x_idx = min_dist_idx // (grid_y.size(0) * grid_z.size(0))
        y_idx = (min_dist_idx % (grid_y.size(0) * grid_z.size(0))) // grid_z.size(0)
        z_idx = min_dist_idx % grid_z.size(0)
        
        # Get bubble intensity
        bubble_intensity = bubble_field[0, x_idx, y_idx, z_idx]
        
        # Apply falloff
        modulation = bubble_intensity * torch.exp(-min_dist_idx.item() * self.bubble_falloff)
        
        return torch.tensor([modulation, modulation])


class SpatialAudioRenderer:
    """
    High-level spatial audio renderer for 3D bubble systems
    """
    
    def __init__(self, config: SpatialAudioConfig, sample_rate: int = 22050):
        self.config = config
        self.sample_rate = sample_rate
        
        # Initialize renderer
        self.renderer = BubbleSpatialRenderer(config)
        
        # Processing state
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Listener position
        self.listener_position = torch.tensor([0.0, 0.0, 0.0])
        
        # Rendering statistics
        self.rendering_stats = {
            "total_renders": 0,
            "sources_rendered": 0,
            "average_distance": 0.0,
            "max_distance": 0.0
        }
        
        logging.info(f"Spatial Audio Renderer initialized on device: {self.device}")
    
    def initialize(self):
        """Initialize the renderer"""
        self.renderer.to(self.device)
        self.renderer.eval()
        
        self.initialized = True
        logging.info("Spatial Audio Renderer fully initialized")
    
    def render_3d_audio(self, bubble_data: Dict[str, torch.Tensor],
                        audio_sources: List[Dict[str, torch.Tensor]],
                        listener_position: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Render 3D spatial audio from bubble field and audio sources
        
        Args:
            bubble_data: 3D bubble field data
            audio_sources: List of audio sources
            listener_position: Optional listener position
            
        Returns:
            Rendered stereo audio
        """
        if not self.initialized:
            raise RuntimeError("Renderer not initialized. Call initialize() first.")
        
        # Update listener position
        if listener_position is not None:
            self.listener_position = listener_position.to(self.device)
        
        # Move data to device
        for key in bubble_data:
            if isinstance(bubble_data[key], torch.Tensor):
                bubble_data[key] = bubble_data[key].to(self.device)
        
        for source in audio_sources:
            source["position"] = source["position"].to(self.device)
            source["audio"] = source["audio"].to(self.device)
        
        # Render audio
        rendered_audio = self.renderer.render_bubble_audio_field(
            bubble_data, audio_sources, self.listener_position
        )
        
        # Update statistics
        self._update_rendering_stats(audio_sources, self.listener_position)
        
        return rendered_audio
    
    def _update_rendering_stats(self, audio_sources: List[Dict[str, torch.Tensor]], 
                               listener_position: torch.Tensor):
        """Update rendering statistics"""
        self.rendering_stats["total_renders"] += 1
        self.rendering_stats["sources_rendered"] += len(audio_sources)
        
        # Calculate distance statistics
        distances = []
        for source in audio_sources:
            distance = torch.norm(source["position"] - listener_position)
            distances.append(distance.item())
        
        if distances:
            avg_distance = sum(distances) / len(distances)
            max_distance = max(distances)
            
            # Update running averages
            total_renders = self.rendering_stats["total_renders"]
            self.rendering_stats["average_distance"] = (
                (self.rendering_stats["average_distance"] * (total_renders - 1) + avg_distance) / total_renders
            )
            self.rendering_stats["max_distance"] = max(self.rendering_stats["max_distance"], max_distance)
    
    def set_listener_position(self, position: torch.Tensor):
        """Set listener position"""
        self.listener_position = position.to(self.device)
    
    def get_rendering_status(self) -> Dict[str, any]:
        """Get rendering status"""
        return {
            "initialized": self.initialized,
            "device": str(self.device),
            "sample_rate": self.sample_rate,
            "config": {
                "hrtf_enabled": self.config.hrtf_enabled,
                "doppler_enabled": self.config.doppler_enabled,
                "max_render_distance": self.config.max_render_distance,
                "bubble_falloff": self.config.bubble_falloff,
                "enable_real_time": self.config.enable_real_time
            },
            "listener_position": self.listener_position.tolist(),
            "rendering_stats": self.rendering_stats.copy()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        del self.renderer
        torch.cuda.empty_cache()
        logging.info("Spatial Audio Renderer cleanup completed")


def create_spatial_audio_renderer(config: Optional[SpatialAudioConfig] = None, 
                                 sample_rate: int = 22050) -> SpatialAudioRenderer:
    """
    Factory function to create spatial audio renderer
    
    Args:
        config: Spatial audio configuration
        sample_rate: Audio sample rate
        
    Returns:
        SpatialAudioRenderer instance
    """
    if config is None:
        config = SpatialAudioConfig()
    
    renderer = SpatialAudioRenderer(config, sample_rate)
    renderer.initialize()
    
    return renderer


def create_high_quality_spatial_renderer(sample_rate: int = 22050) -> SpatialAudioRenderer:
    """
    Create high-quality spatial audio renderer
    
    Returns:
        Optimized SpatialAudioRenderer instance
    """
    config = SpatialAudioConfig(
        sample_rate=sample_rate,
        channels=2,
        hrtf_enabled=True,
        hrtf_resolution=720,  # Higher resolution
        elevation_resolution=180,  # Higher resolution
        doppler_enabled=True,
        distance_attenuation=1.0,
        air_absorption=0.002,
        bubble_falloff=0.9,
        max_render_distance=15.0,
        min_render_distance=0.05,
        enable_real_time=True,
        processing_latency_ms=2.0
    )
    
    return create_spatial_audio_renderer(config, sample_rate)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create spatial audio renderer
    renderer = create_spatial_audio_renderer()
    
    # Create sample bubble data
    bubble_field = torch.randn(1, 32, 32, 32)  # 3D bubble field
    grid_x = torch.linspace(-1, 1, 32)
    grid_y = torch.linspace(-1, 1, 32)
    grid_z = torch.linspace(-1, 1, 32)
    
    bubble_data = {
        "bubble_field": bubble_field,
        "grid_x": grid_x,
        "grid_y": grid_y,
        "grid_z": grid_z
    }
    
    # Create sample audio sources
    audio_sources = [
        {
            "position": torch.tensor([0.5, 0.0, 0.0]),
            "audio": torch.randn(1, 1024),
            "id": 0
        },
        {
            "position": torch.tensor([-0.5, 0.0, 0.0]),
            "audio": torch.randn(1, 1024),
            "id": 1
        }
    ]
    
    # Set listener position
    listener_position = torch.tensor([0.0, 0.0, 0.0])
    
    # Render spatial audio
    rendered_audio = renderer.render_3d_audio(bubble_data, audio_sources, listener_position)
    
    print(f"Rendered audio shape: {rendered_audio.shape}")
    
    # Get rendering status
    status = renderer.get_rendering_status()
    print(f"Rendering status: {status}")
    
    # Cleanup
    renderer.cleanup()
    
    print("Spatial Audio Renderer example completed")
