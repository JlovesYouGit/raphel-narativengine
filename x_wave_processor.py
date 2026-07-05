# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
X-Wave Trajectory Override Processor
Advanced trajectory override system treating each wave sine as X0 start, Xval as ending line by length
with divergent X-line processing for TTS wave generation
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
class TrajectoryConfig:
    """Configuration for X-wave trajectory override processor"""
    x0_start_position: float = 0.0
    xval_end_position: float = 1.0
    trajectory_length: int = 1024
    divergent_factor: float = 0.5
    trajectory_resolution: int = 100
    interpolation_method: str = "linear"  # linear, cubic, spline
    smoothing_factor: float = 0.1
    adaptive_trajectory: bool = True
    multi_trajectory: bool = True
    phase_alignment: bool = True
    
    # Wave processing parameters
    wave_frequency: float = 440.0  # Hz
    sample_rate: int = 22050
    amplitude_scale: float = 1.0
    phase_offset: float = 0.0
    
    # Divergent processing
    divergent_segments: int = 2
    divergent_threshold: float = 0.3
    divergent_smoothing: bool = True


class XWaveTrajectoryCalculator(nn.Module):
    """Calculator for X-wave trajectories"""
    
    def __init__(self, config: TrajectoryConfig):
        super().__init__()
        self.config = config
        
        # Trajectory parameters
        self.register_buffer('x0_start', torch.tensor(config.x0_start_position))
        self.register_buffer('xval_end', torch.tensor(config.xval_end_position))
        self.register_buffer('trajectory_length', torch.tensor(config.trajectory_length))
        
        # Learnable trajectory parameters
        self.trajectory_bias = nn.Parameter(torch.zeros(1))
        self.trajectory_scale = nn.Parameter(torch.ones(1))
        
        # Divergent parameters
        self.divergent_weight = nn.Parameter(torch.tensor(config.divergent_factor))
        
    def calculate_base_trajectory(self, batch_size: int = 1) -> torch.Tensor:
        """
        Calculate base X0 to Xval trajectory
        
        Args:
            batch_size: Batch size for trajectory calculation
            
        Returns:
            Base trajectory tensor [batch_size, trajectory_length]
        """
        # Create linear trajectory from X0 to Xval
        t = torch.linspace(0, 1, self.config.trajectory_length, device=self.x0_start.device)
        base_trajectory = self.x0_start + (self.xval_end - self.x0_start) * t
        
        # Apply learnable parameters
        base_trajectory = base_trajectory * self.trajectory_scale + self.trajectory_bias
        
        # Expand for batch
        base_trajectory = base_trajectory.unsqueeze(0).expand(batch_size, -1)
        
        return base_trajectory
    
    def calculate_divergent_trajectory(self, base_trajectory: torch.Tensor, 
                                     divergence_type: str = "sine") -> torch.Tensor:
        """
        Calculate divergent trajectory
        
        Args:
            base_trajectory: Base trajectory tensor
            divergence_type: Type of divergence (sine, cosine, exponential, linear)
            
        Returns:
            Divergent trajectory tensor
        """
        batch_size, seq_len = base_trajectory.shape
        t = torch.linspace(0, 1, seq_len, device=base_trajectory.device)
        
        if divergence_type == "sine":
            # Sine wave divergence
            divergent_component = torch.sin(2 * math.pi * t * self.config.divergent_segments) * self.divergent_weight
        elif divergence_type == "cosine":
            # Cosine wave divergence
            divergent_component = torch.cos(2 * math.pi * t * self.config.divergent_segments) * self.divergent_weight
        elif divergence_type == "exponential":
            # Exponential divergence
            divergent_component = torch.exp(t * self.divergent_weight) - 1
        elif divergence_type == "linear":
            # Linear divergence
            divergent_component = t * self.divergent_weight
        else:
            divergent_component = torch.zeros_like(t)
        
        # Apply divergent component to base trajectory
        divergent_trajectory = base_trajectory + divergent_component.unsqueeze(0).expand(batch_size, -1)
        
        return divergent_trajectory
    
    def calculate_multi_trajectory(self, base_trajectory: torch.Tensor) -> torch.Tensor:
        """
        Calculate multiple trajectories with different divergence patterns
        
        Args:
            base_trajectory: Base trajectory tensor
            
        Returns:
            Multi-trajectory tensor [batch_size, num_trajectories, trajectory_length]
        """
        batch_size, seq_len = base_trajectory.shape
        num_trajectories = self.config.divergent_segments
        
        trajectories = []
        
        for i in range(num_trajectories):
            # Calculate phase offset for each trajectory
            phase_offset = 2 * math.pi * i / num_trajectories
            
            # Create divergent trajectory with phase offset
            t = torch.linspace(0, 1, seq_len, device=base_trajectory.device)
            divergent_component = torch.sin(2 * math.pi * t * num_trajectories + phase_offset) * self.divergent_weight
            
            trajectory = base_trajectory + divergent_component.unsqueeze(0).expand(batch_size, -1)
            trajectories.append(trajectory)
        
        # Stack trajectories
        multi_trajectory = torch.stack(trajectories, dim=1)
        
        return multi_trajectory


class XWaveProcessor(nn.Module):
    """Main X-wave trajectory processor"""
    
    def __init__(self, config: TrajectoryConfig):
        super().__init__()
        self.config = config
        
        # Trajectory calculator
        self.trajectory_calculator = XWaveTrajectoryCalculator(config)
        
        # Wave generation layers
        self.wave_generator = nn.Sequential(
            nn.Linear(1, config.trajectory_length // 4),
            nn.GELU(),
            nn.Linear(config.trajectory_length // 4, config.trajectory_length // 2),
            nn.GELU(),
            nn.Linear(config.trajectory_length // 2, config.trajectory_length),
            nn.Tanh()
        )
        
        # Trajectory modulation layers
        self.trajectory_modulator = nn.Sequential(
            nn.Linear(config.trajectory_length, config.trajectory_length // 2),
            nn.GELU(),
            nn.Dropout(config.smoothing_factor),
            nn.Linear(config.trajectory_length // 2, config.trajectory_length),
            nn.Sigmoid()
        )
        
        # Phase alignment layers
        if config.phase_alignment:
            self.phase_aligner = nn.Sequential(
                nn.Linear(config.trajectory_length, config.trajectory_length // 2),
                nn.GELU(),
                nn.Linear(config.trajectory_length // 2, 1),
                nn.Tanh()
            )
        
        # Adaptive trajectory layers
        if config.adaptive_trajectory:
            self.adaptive_weight = nn.Parameter(torch.ones(1))
            self.adaptive_bias = nn.Parameter(torch.zeros(1))
        
        # Multi-trajectory processing
        if config.multi_trajectory:
            self.trajectory_fusion = nn.Sequential(
                nn.Linear(config.divergent_segments, 1),
                nn.Sigmoid()
            )
        
        # Interpolation layer
        self.interpolation_layer = self._create_interpolation_layer()
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _create_interpolation_layer(self) -> nn.Module:
        """Create interpolation layer based on method"""
        if self.config.interpolation_method == "cubic":
            return nn.Conv1d(1, 1, kernel_size=3, padding=1, bias=False)
        elif self.config.interpolation_method == "spline":
            return nn.Conv1d(1, 1, kernel_size=5, padding=2, bias=False)
        else:  # linear
            return nn.Conv1d(1, 1, kernel_size=1, bias=False)
    
    def _init_weights(self, module):
        """Initialize weights"""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=0.02)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Conv1d):
            nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
            if module.bias is not None:
                module.bias.data.zero_()
    
    def generate_base_wave(self, trajectory: torch.Tensor) -> torch.Tensor:
        """
        Generate base wave from trajectory
        
        Args:
            trajectory: Input trajectory tensor [batch_size, trajectory_length]
            
        Returns:
            Generated wave tensor [batch_size, trajectory_length]
        """
        batch_size, seq_len = trajectory.shape
        
        # Generate wave from trajectory
        # Use trajectory as control signal for wave generation
        wave_input = trajectory.unsqueeze(-1)  # [batch_size, trajectory_length, 1]
        generated_wave = self.wave_generator(wave_input).squeeze(-1)
        
        return generated_wave
    
    def apply_trajectory_modulation(self, wave: torch.Tensor, trajectory: torch.Tensor) -> torch.Tensor:
        """
        Apply trajectory modulation to wave
        
        Args:
            wave: Input wave tensor [batch_size, trajectory_length]
            trajectory: Trajectory tensor [batch_size, trajectory_length]
            
        Returns:
            Modulated wave tensor
        """
        # Calculate modulation weights from trajectory
        modulation_weights = self.trajectory_modulator(trajectory)
        
        # Apply modulation
        modulated_wave = wave * modulation_weights
        
        return modulated_wave
    
    def apply_phase_alignment(self, wave: torch.Tensor, trajectory: torch.Tensor) -> torch.Tensor:
        """
        Apply phase alignment between wave and trajectory
        
        Args:
            wave: Input wave tensor
            trajectory: Trajectory tensor
            
        Returns:
            Phase-aligned wave tensor
        """
        if not self.config.phase_alignment:
            return wave
        
        # Calculate phase offset
        phase_offset = self.phase_aligner(trajectory).squeeze(-1)
        
        # Apply phase offset to wave
        phase_aligned_wave = wave + phase_offset
        
        return phase_aligned_wave
    
    def process_single_trajectory(self, wave_input: torch.Tensor, x0_start: float = None, 
                                xval_end: float = None) -> torch.Tensor:
        """
        Process wave with single trajectory override
        
        Args:
            wave_input: Input wave tensor [batch_size, sequence_length]
            x0_start: Custom X0 start position
            xval_end: Custom Xval end position
            
        Returns:
            Processed wave tensor
        """
        batch_size, seq_len = wave_input.shape
        
        # Update trajectory parameters if provided
        if x0_start is not None:
            self.trajectory_calculator.x0_start.data = torch.tensor(x0_start, device=wave_input.device)
        if xval_end is not None:
            self.trajectory_calculator.xval_end.data = torch.tensor(xval_end, device=wave_input.device)
        
        # Calculate base trajectory
        base_trajectory = self.trajectory_calculator.calculate_base_trajectory(batch_size)
        
        # Calculate divergent trajectory
        divergent_trajectory = self.trajectory_calculator.calculate_divergent_trajectory(base_trajectory)
        
        # Generate base wave from trajectory
        trajectory_wave = self.generate_base_wave(divergent_trajectory)
        
        # Apply trajectory modulation
        modulated_wave = self.apply_trajectory_modulation(trajectory_wave, divergent_trajectory)
        
        # Apply phase alignment
        phase_aligned_wave = self.apply_phase_alignment(modulated_wave, divergent_trajectory)
        
        # Apply adaptive weighting
        if self.config.adaptive_trajectory:
            adaptive_weight = self.adaptive_weight + self.adaptive_bias
            phase_aligned_wave = phase_aligned_wave * adaptive_weight
        
        # Apply interpolation
        if seq_len != self.config.trajectory_length:
            # Reshape for interpolation
            wave_reshaped = phase_aligned_wave.unsqueeze(1)  # [batch_size, 1, seq_len]
            interpolated_wave = self.interpolation_layer(wave_reshaped)
            phase_aligned_wave = interpolated_wave.squeeze(1)
        
        # Combine with original wave
        processed_wave = wave_input + phase_aligned_wave * self.config.amplitude_scale
        
        return processed_wave
    
    def process_multi_trajectory(self, wave_input: torch.Tensor, x0_start: float = None, 
                               xval_end: float = None) -> torch.Tensor:
        """
        Process wave with multiple trajectory overrides
        
        Args:
            wave_input: Input wave tensor [batch_size, sequence_length]
            x0_start: Custom X0 start position
            xval_end: Custom Xval end position
            
        Returns:
            Processed wave tensor
        """
        if not self.config.multi_trajectory:
            return self.process_single_trajectory(wave_input, x0_start, xval_end)
        
        batch_size, seq_len = wave_input.shape
        
        # Update trajectory parameters if provided
        if x0_start is not None:
            self.trajectory_calculator.x0_start.data = torch.tensor(x0_start, device=wave_input.device)
        if xval_end is not None:
            self.trajectory_calculator.xval_end.data = torch.tensor(xval_end, device=wave_input.device)
        
        # Calculate base trajectory
        base_trajectory = self.trajectory_calculator.calculate_base_trajectory(batch_size)
        
        # Calculate multi-trajectory
        multi_trajectory = self.trajectory_calculator.calculate_multi_trajectory(base_trajectory)
        
        # Process each trajectory
        trajectory_waves = []
        for i in range(self.config.divergent_segments):
            trajectory = multi_trajectory[:, i, :]
            trajectory_wave = self.generate_base_wave(trajectory)
            modulated_wave = self.apply_trajectory_modulation(trajectory_wave, trajectory)
            phase_aligned_wave = self.apply_phase_alignment(modulated_wave, trajectory)
            trajectory_waves.append(phase_aligned_wave)
        
        # Fuse trajectories
        trajectory_stack = torch.stack(trajectory_waves, dim=1)  # [batch_size, num_trajectories, seq_len]
        
        # Calculate fusion weights
        fusion_weights = self.trajectory_fusion(torch.ones(self.config.divergent_segments, device=wave_input.device))
        
        # Apply fusion
        fused_wave = torch.sum(trajectory_stack * fusion_weights.view(1, -1, 1), dim=1)
        
        # Combine with original wave
        processed_wave = wave_input + fused_wave * self.config.amplitude_scale
        
        return processed_wave
    
    def apply_trajectory_override(self, wave_input: torch.Tensor, x0_start: float = None, 
                                xval_end: float = None) -> torch.Tensor:
        """
        Apply trajectory override to input wave
        
        Args:
            wave_input: Input wave tensor [batch_size, sequence_length]
            x0_start: Custom X0 start position
            xval_end: Custom Xval end position
            
        Returns:
            Processed wave tensor
        """
        if self.config.multi_trajectory:
            return self.process_multi_trajectory(wave_input, x0_start, xval_end)
        else:
            return self.process_single_trajectory(wave_input, x0_start, xval_end)


class XWaveTrajectoryProcessor:
    """
    High-level X-wave trajectory processor for TTS integration
    """
    
    def __init__(self, config: TrajectoryConfig):
        self.config = config
        self.processor = XWaveProcessor(config)
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Processing statistics
        self.processing_stats = {
            "total_processed": 0,
            "trajectory_overrides": 0,
            "multi_trajectory_used": 0,
            "phase_alignments": 0
        }
        
        logging.info(f"X-Wave trajectory processor initialized on device: {self.device}")
    
    def initialize(self):
        """Initialize the processor"""
        self.processor.to(self.device)
        self.processor.eval()
        self.initialized = True
        logging.info("X-Wave trajectory processor fully initialized")
    
    def apply_trajectory_override(self, wave_input: torch.Tensor, x0_start: float = None, 
                                xval_end: float = None) -> torch.Tensor:
        """
        Apply trajectory override to input wave
        
        Args:
            wave_input: Input wave tensor [batch_size, sequence_length] or [sequence_length]
            x0_start: Custom X0 start position
            xval_end: Custom Xval end position
            
        Returns:
            Processed wave tensor
        """
        if not self.initialized:
            raise RuntimeError("Processor not initialized. Call initialize() first.")
        
        # Ensure input is 2D
        if wave_input.dim() == 1:
            wave_input = wave_input.unsqueeze(0)
        
        # Move to device
        wave_input = wave_input.to(self.device)
        
        # Apply trajectory override
        with torch.no_grad():
            processed_wave = self.processor.apply_trajectory_override(wave_input, x0_start, xval_end)
        
        # Update statistics
        self.processing_stats["total_processed"] += wave_input.size(0)
        self.processing_stats["trajectory_overrides"] += 1
        if self.config.multi_trajectory:
            self.processing_stats["multi_trajectory_used"] += 1
        if self.config.phase_alignment:
            self.processing_stats["phase_alignments"] += 1
        
        # Return to original shape if input was 1D
        if wave_input.size(0) == 1 and processed_wave.size(0) == 1:
            processed_wave = processed_wave.squeeze(0)
        
        return processed_wave.cpu()
    
    def batch_process_waves(self, wave_inputs: List[torch.Tensor], 
                           x0_starts: List[float] = None, xval_ends: List[float] = None) -> List[torch.Tensor]:
        """
        Batch process multiple waves with trajectory overrides
        
        Args:
            wave_inputs: List of input wave tensors
            x0_starts: List of X0 start positions
            xval_ends: List of Xval end positions
            
        Returns:
            List of processed wave tensors
        """
        if not self.initialized:
            raise RuntimeError("Processor not initialized. Call initialize() first.")
        
        if x0_starts is None:
            x0_starts = [None] * len(wave_inputs)
        if xval_ends is None:
            xval_ends = [None] * len(wave_inputs)
        
        processed_waves = []
        
        for wave_input, x0_start, xval_end in zip(wave_inputs, x0_starts, xval_ends):
            processed_wave = self.apply_trajectory_override(wave_input, x0_start, xval_end)
            processed_waves.append(processed_wave)
        
        return processed_waves
    
    def analyze_trajectory_effect(self, original_wave: torch.Tensor, 
                                 processed_wave: torch.Tensor) -> Dict[str, float]:
        """
        Analyze the effect of trajectory override
        
        Args:
            original_wave: Original wave tensor
            processed_wave: Processed wave tensor
            
        Returns:
            Analysis results dictionary
        """
        # Convert to numpy for analysis
        orig_np = original_wave.cpu().numpy()
        proc_np = processed_wave.cpu().numpy()
        
        # Calculate metrics
        if len(orig_np.shape) > 1:
            orig_np = orig_np.flatten()
        if len(proc_np.shape) > 1:
            proc_np = proc_np.flatten()
        
        # Calculate differences
        difference = proc_np - orig_np
        mean_difference = float(np.mean(difference))
        std_difference = float(np.std(difference))
        
        # Calculate correlation
        correlation = float(np.corrcoef(orig_np, proc_np)[0, 1])
        
        # Calculate spectral changes
        orig_fft = np.fft.fft(orig_np)
        proc_fft = np.fft.fft(proc_np)
        spectral_diff = np.mean(np.abs(orig_fft - proc_fft))
        
        # Calculate trajectory metrics
        trajectory_length = self.config.trajectory_length
        x0_to_xval_range = self.config.xval_end_position - self.config.x0_start_position
        
        return {
            "mean_difference": mean_difference,
            "std_difference": std_difference,
            "correlation": correlation,
            "spectral_difference": float(spectral_diff),
            "trajectory_length": trajectory_length,
            "x0_to_xval_range": x0_to_xval_range,
            "divergent_factor": self.config.divergent_factor
        }
    
    def get_processing_status(self) -> Dict[str, any]:
        """Get processing status"""
        return {
            "initialized": self.initialized,
            "device": str(self.device),
            "config": {
                "x0_start_position": self.config.x0_start_position,
                "xval_end_position": self.config.xval_end_position,
                "trajectory_length": self.config.trajectory_length,
                "divergent_factor": self.config.divergent_factor,
                "multi_trajectory": self.config.multi_trajectory,
                "phase_alignment": self.config.phase_alignment
            },
            "processing_stats": self.processing_stats.copy()
        }
    
    def update_config(self, new_config: TrajectoryConfig):
        """Update configuration"""
        self.config = new_config
        
        # Reinitialize processor with new config
        self.processor = XWaveProcessor(new_config)
        self.processor.to(self.device)
        self.processor.eval()
        
        logging.info("X-Wave trajectory processor configuration updated")
    
    def reset_statistics(self):
        """Reset processing statistics"""
        self.processing_stats = {
            "total_processed": 0,
            "trajectory_overrides": 0,
            "multi_trajectory_used": 0,
            "phase_alignments": 0
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'processor'):
            del self.processor
        torch.cuda.empty_cache()
        logging.info("X-Wave trajectory processor cleanup completed")


def create_trajectory_processor(config: Optional[TrajectoryConfig] = None) -> XWaveTrajectoryProcessor:
    """
    Factory function to create X-wave trajectory processor
    
    Args:
        config: Trajectory configuration
        
    Returns:
        XWaveTrajectoryProcessor instance
    """
    if config is None:
        config = TrajectoryConfig()
    
    processor = XWaveTrajectoryProcessor(config)
    processor.initialize()
    
    return processor


def create_hd_trajectory_processor() -> XWaveTrajectoryProcessor:
    """
    Create processor optimized for HD audio trajectory processing
    
    Returns:
        Optimized XWaveTrajectoryProcessor instance
    """
    config = TrajectoryConfig(
        x0_start_position=0.0,
        xval_end_position=1.0,
        trajectory_length=2048,        # Longer trajectory for HD audio
        divergent_factor=0.3,          # Lower divergence for HD audio
        multi_trajectory=True,         # Multi-trajectory for HD audio
        divergent_segments=3,          # More segments for HD audio
        phase_alignment=True,          # Phase alignment for HD audio
        adaptive_trajectory=True,      # Adaptive processing for HD audio
        smoothing_factor=0.05,        # Less smoothing for HD audio
        interpolation_method="cubic"   # Cubic interpolation for HD audio
    )
    
    return create_trajectory_processor(config)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create processor
    processor = create_trajectory_processor()
    
    # Create sample wave
    sample_rate = 22050
    duration = 2.0  # 2 seconds
    t = torch.linspace(0, duration, int(sample_rate * duration))
    wave_input = torch.sin(2 * torch.pi * 440 * t)  # 440 Hz sine wave
    
    # Apply trajectory override
    processed_wave = processor.apply_trajectory_override(wave_input, x0_start=0.0, xval_end=1.0)
    
    print(f"Original wave shape: {wave_input.shape}")
    print(f"Processed wave shape: {processed_wave.shape}")
    
    # Analyze effect
    analysis = processor.analyze_trajectory_effect(wave_input, processed_wave)
    print(f"Trajectory effect analysis: {analysis}")
    
    # Get status
    status = processor.get_processing_status()
    print(f"Processing status: {status}")
    
    # Cleanup
    processor.cleanup()
    
    print("X-Wave trajectory processor example completed")
