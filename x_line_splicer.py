# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Divergent X-Line Wave Splicer System
Advanced splicer system that diverges each X0 line wave into another X0 line wave
for TTS processing with specified 2-table processing
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
class SplicerConfig:
    """Configuration for divergent X-line wave splicer"""
    segments: int = 2
    overlap: float = 0.1
    divergent_threshold: float = 0.3
    splicer_resolution: int = 1024
    interpolation_method: str = "linear"  # linear, cubic, spline
    smoothing_factor: float = 0.1
    adaptive_splicing: bool = True
    multi_table_processing: bool = True
    phase_preservation: bool = True
    
    # X-line parameters
    x0_divergence_factor: float = 0.5
    x0_convergence_rate: float = 0.8
    x0_phase_alignment: bool = True
    x0_frequency_modulation: bool = True
    
    # Table processing parameters
    table_1_size: int = 512
    table_2_size: int = 512
    table_interpolation: bool = True
    table_smoothing: bool = True
    
    # Output parameters
    output_channels: int = 1
    normalize_output: bool = True
    clip_output: bool = True


class XLineGenerator(nn.Module):
    """Generator for X-line wave patterns"""
    
    def __init__(self, config: SplicerConfig):
        super().__init__()
        self.config = config
        
        # X-line generation parameters
        self.x0_divergence_weight = nn.Parameter(torch.tensor(config.x0_divergence_factor))
        self.x0_convergence_weight = nn.Parameter(torch.tensor(config.x0_convergence_rate))
        
        # Frequency modulation layers
        if config.x0_frequency_modulation:
            self.frequency_modulator = nn.Sequential(
                nn.Linear(1, 64),
                nn.GELU(),
                nn.Linear(64, 32),
                nn.GELU(),
                nn.Linear(32, 1),
                nn.Tanh()
            )
        
        # Phase alignment layers
        if config.x0_phase_alignment:
            self.phase_aligner = nn.Sequential(
                nn.Linear(config.splicer_resolution, 128),
                nn.GELU(),
                nn.Linear(128, 64),
                nn.GELU(),
                nn.Linear(64, 1),
                nn.Tanh()
            )
        
        # X-line wave generator
        self.x0_generator = nn.Sequential(
            nn.Linear(1, config.splicer_resolution // 4),
            nn.GELU(),
            nn.Linear(config.splicer_resolution // 4, config.splicer_resolution // 2),
            nn.GELU(),
            nn.Linear(config.splicer_resolution // 2, config.splicer_resolution),
            nn.Tanh()
        )
        
    def generate_x0_line(self, base_wave: torch.Tensor, segment_index: int = 0) -> torch.Tensor:
        """
        Generate X0 line wave from base wave
        
        Args:
            base_wave: Base wave tensor [batch_size, sequence_length]
            segment_index: Segment index for divergence
            
        Returns:
            X0 line wave tensor [batch_size, splicer_resolution]
        """
        batch_size, seq_len = base_wave.shape
        
        # Calculate divergence factor for this segment
        divergence_factor = self.x0_divergence_weight * (1.0 + segment_index * 0.1)
        
        # Generate base X0 line
        t = torch.linspace(0, 1, self.config.splicer_resolution, device=base_wave.device)
        x0_input = t.unsqueeze(0).unsqueeze(-1)  # [1, splicer_resolution, 1]
        
        x0_line = self.x0_generator(x0_input).squeeze(-1)  # [1, splicer_resolution]
        x0_line = x0_line.expand(batch_size, -1)
        
        # Apply divergence
        x0_line = x0_line * divergence_factor
        
        # Apply frequency modulation
        if self.config.x0_frequency_modulation:
            freq_mod = self.frequency_modulator(torch.tensor([[segment_index]], dtype=torch.float32, device=base_wave.device))
            x0_line = x0_line * (1.0 + freq_mod * 0.1)
        
        # Apply phase alignment
        if self.config.x0_phase_alignment:
            phase_alignment = self.phase_aligner(x0_line)
            x0_line = x0_line + phase_alignment
        
        return x0_line
    
    def generate_divergent_x0_lines(self, base_wave: torch.Tensor) -> torch.Tensor:
        """
        Generate multiple divergent X0 lines
        
        Args:
            base_wave: Base wave tensor [batch_size, sequence_length]
            
        Returns:
            Divergent X0 lines tensor [batch_size, segments, splicer_resolution]
        """
        batch_size, seq_len = base_wave.shape
        
        x0_lines = []
        
        for i in range(self.config.segments):
            x0_line = self.generate_x0_line(base_wave, i)
            x0_lines.append(x0_line)
        
        # Stack X0 lines
        divergent_x0_lines = torch.stack(x0_lines, dim=1)
        
        return divergent_x0_lines


class TableProcessor(nn.Module):
    """Processor for 2-table processing system"""
    
    def __init__(self, config: SplicerConfig):
        super().__init__()
        self.config = config
        
        # Table 1 processing
        self.table_1_processor = nn.Sequential(
            nn.Linear(config.table_1_size, config.table_1_size // 2),
            nn.GELU(),
            nn.Linear(config.table_1_size // 2, config.table_1_size // 4),
            nn.GELU(),
            nn.Linear(config.table_1_size // 4, config.table_1_size),
            nn.Tanh()
        )
        
        # Table 2 processing
        self.table_2_processor = nn.Sequential(
            nn.Linear(config.table_2_size, config.table_2_size // 2),
            nn.GELU(),
            nn.Linear(config.table_2_size // 2, config.table_2_size // 4),
            nn.GELU(),
            nn.Linear(config.table_2_size // 4, config.table_2_size),
            nn.Tanh()
        )
        
        # Table interpolation
        if config.table_interpolation:
            self.table_interpolator = nn.Sequential(
                nn.Linear(config.table_1_size + config.table_2_size, 256),
                nn.GELU(),
                nn.Linear(256, config.splicer_resolution),
                nn.Tanh()
            )
        
        # Table smoothing
        if config.table_smoothing:
            self.table_smoother = nn.Conv1d(1, 1, kernel_size=3, padding=1, bias=False)
    
    def process_table_1(self, input_data: torch.Tensor) -> torch.Tensor:
        """
        Process data through table 1
        
        Args:
            input_data: Input data tensor
            
        Returns:
            Processed table 1 data
        """
        # Ensure correct size
        if input_data.size(-1) != self.config.table_1_size:
            input_data = F.interpolate(input_data.unsqueeze(1), size=self.config.table_1_size, mode='linear').squeeze(1)
        
        return self.table_1_processor(input_data)
    
    def process_table_2(self, input_data: torch.Tensor) -> torch.Tensor:
        """
        Process data through table 2
        
        Args:
            input_data: Input data tensor
            
        Returns:
            Processed table 2 data
        """
        # Ensure correct size
        if input_data.size(-1) != self.config.table_2_size:
            input_data = F.interpolate(input_data.unsqueeze(1), size=self.config.table_2_size, mode='linear').squeeze(1)
        
        return self.table_2_processor(input_data)
    
    def interpolate_tables(self, table_1_output: torch.Tensor, table_2_output: torch.Tensor) -> torch.Tensor:
        """
        Interpolate between table outputs
        
        Args:
            table_1_output: Table 1 output
            table_2_output: Table 2 output
            
        Returns:
            Interpolated output
        """
        if not self.config.table_interpolation:
            return (table_1_output + table_2_output) / 2.0
        
        # Concatenate tables
        combined_input = torch.cat([table_1_output, table_2_output], dim=-1)
        
        # Interpolate
        interpolated = self.table_interpolator(combined_input)
        
        return interpolated
    
    def apply_smoothing(self, data: torch.Tensor) -> torch.Tensor:
        """
        Apply smoothing to processed data
        
        Args:
            data: Input data tensor
            
        Returns:
            Smoothed data tensor
        """
        if not self.config.table_smoothing:
            return data
        
        # Reshape for convolution
        data_reshaped = data.unsqueeze(1)  # [batch_size, 1, sequence_length]
        
        # Apply smoothing
        smoothed = self.table_smoother(data_reshaped)
        
        # Reshape back
        return smoothed.squeeze(1)


class XLineWaveSplicer(nn.Module):
    """Main X-line wave splicer"""
    
    def __init__(self, config: SplicerConfig):
        super().__init__()
        self.config = config
        
        # X-line generator
        self.x0_generator = XLineGenerator(config)
        
        # Table processor
        self.table_processor = TableProcessor(config)
        
        # Splicer layers
        self.splicer_fusion = nn.Sequential(
            nn.Linear(config.splicer_resolution * config.segments, config.splicer_resolution),
            nn.GELU(),
            nn.Dropout(config.smoothing_factor),
            nn.Linear(config.splicer_resolution, config.splicer_resolution // 2),
            nn.GELU(),
            nn.Linear(config.splicer_resolution // 2, config.output_channels)
        )
        
        # Divergence control
        self.divergence_control = nn.Parameter(torch.tensor(config.divergent_threshold))
        
        # Adaptive splicing
        if config.adaptive_splicing:
            self.adaptive_weight = nn.Parameter(torch.ones(1))
            self.adaptive_bias = nn.Parameter(torch.zeros(1))
        
        # Phase preservation
        if config.phase_preservation:
            self.phase_preserver = nn.Sequential(
                nn.Linear(config.splicer_resolution, 128),
                nn.GELU(),
                nn.Linear(128, 64),
                nn.GELU(),
                nn.Linear(64, 1),
                nn.Tanh()
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
    
    def splice_divergent_x_lines(self, wave_input: torch.Tensor, segments: int = None, 
                                divergent_factor: float = None) -> torch.Tensor:
        """
        Splice divergent X-line waves
        
        Args:
            wave_input: Input wave tensor [batch_size, sequence_length]
            segments: Number of segments (overrides config)
            divergent_factor: Divergent factor (overrides config)
            
        Returns:
            Spliced wave tensor [batch_size, output_length, output_channels]
        """
        batch_size, seq_len = wave_input.shape
        
        # Use provided parameters or config defaults
        if segments is None:
            segments = self.config.segments
        if divergent_factor is None:
            divergent_factor = self.config.divergent_threshold
        
        # Generate divergent X0 lines
        divergent_x0_lines = self.x0_generator.generate_divergent_x0_lines(wave_input)
        
        # Process through 2-table system
        if self.config.multi_table_processing:
            # Process each X0 line through tables
            processed_lines = []
            
            for i in range(segments):
                x0_line = divergent_x0_lines[:, i, :]
                
                # Process through table 1
                table_1_output = self.table_processor.process_table_1(x0_line)
                
                # Process through table 2
                table_2_output = self.table_processor.process_table_2(x0_line)
                
                # Interpolate table outputs
                interpolated_output = self.table_processor.interpolate_tables(table_1_output, table_2_output)
                
                # Apply smoothing
                smoothed_output = self.table_processor.apply_smoothing(interpolated_output)
                
                processed_lines.append(smoothed_output)
            
            # Stack processed lines
            processed_x0_lines = torch.stack(processed_lines, dim=1)
        else:
            processed_x0_lines = divergent_x0_lines
        
        # Apply divergence control
        divergence_applied = processed_x0_lines * self.divergence_control
        
        # Fuse divergent lines
        fused_input = divergence_applied.view(batch_size, -1)  # [batch_size, segments * splicer_resolution]
        
        # Apply splicer fusion
        spliced_output = self.splicer_fusion(fused_input)
        
        # Apply phase preservation
        if self.config.phase_preservation:
            # Use first X0 line for phase reference
            phase_reference = divergent_x0_lines[:, 0, :]
            phase_correction = self.phase_preserver(phase_reference)
            spliced_output = spliced_output + phase_correction
        
        # Apply adaptive weighting
        if self.config.adaptive_splicing:
            adaptive_weight = self.adaptive_weight + self.adaptive_bias
            spliced_output = spliced_output * adaptive_weight
        
        # Apply interpolation for final output
        if seq_len != self.config.splicer_resolution:
            # Reshape for interpolation
            spliced_reshaped = spliced_output.unsqueeze(1)  # [batch_size, 1, features]
            interpolated_output = self.interpolation_layer(spliced_reshaped)
            spliced_output = interpolated_output.squeeze(1)
        
        # Normalize and clip output
        if self.config.normalize_output:
            spliced_output = torch.tanh(spliced_output)
        
        if self.config.clip_output:
            spliced_output = torch.clamp(spliced_output, -1.0, 1.0)
        
        return spliced_output


class XLineWaveSplicerSystem:
    """
    High-level X-line wave splicer system for TTS integration
    """
    
    def __init__(self, config: SplicerConfig):
        self.config = config
        self.splicer = XLineWaveSplicer(config)
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Processing statistics
        self.processing_stats = {
            "total_spliced": 0,
            "divergent_lines_generated": 0,
            "table_processing_used": 0,
            "phase_preservations": 0
        }
        
        logging.info(f"X-Line wave splicer system initialized on device: {self.device}")
    
    def initialize(self):
        """Initialize the splicer system"""
        self.splicer.to(self.device)
        self.splicer.eval()
        self.initialized = True
        logging.info("X-Line wave splicer system fully initialized")
    
    def splice_divergent_x_lines(self, wave_input: torch.Tensor, segments: int = None, 
                                divergent_factor: float = None) -> torch.Tensor:
        """
        Splice divergent X-line waves
        
        Args:
            wave_input: Input wave tensor [batch_size, sequence_length] or [sequence_length]
            segments: Number of segments
            divergent_factor: Divergent factor
            
        Returns:
            Spliced wave tensor
        """
        if not self.initialized:
            raise RuntimeError("Splicer system not initialized. Call initialize() first.")
        
        # Ensure input is 2D
        if wave_input.dim() == 1:
            wave_input = wave_input.unsqueeze(0)
        
        # Move to device
        wave_input = wave_input.to(self.device)
        
        # Apply splicing
        with torch.no_grad():
            spliced_wave = self.splicer.splice_divergent_x_lines(wave_input, segments, divergent_factor)
        
        # Update statistics
        self.processing_stats["total_spliced"] += wave_input.size(0)
        self.processing_stats["divergent_lines_generated"] += self.config.segments
        if self.config.multi_table_processing:
            self.processing_stats["table_processing_used"] += 1
        if self.config.phase_preservation:
            self.processing_stats["phase_preservations"] += 1
        
        # Return to original shape if input was 1D
        if wave_input.size(0) == 1 and spliced_wave.size(0) == 1:
            spliced_wave = spliced_wave.squeeze(0)
        
        return spliced_wave.cpu()
    
    def batch_splice_waves(self, wave_inputs: List[torch.Tensor], 
                         segments_list: List[int] = None, 
                         divergent_factors: List[float] = None) -> List[torch.Tensor]:
        """
        Batch splice multiple waves
        
        Args:
            wave_inputs: List of input wave tensors
            segments_list: List of segment counts
            divergent_factors: List of divergent factors
            
        Returns:
            List of spliced wave tensors
        """
        if not self.initialized:
            raise RuntimeError("Splicer system not initialized. Call initialize() first.")
        
        if segments_list is None:
            segments_list = [None] * len(wave_inputs)
        if divergent_factors is None:
            divergent_factors = [None] * len(wave_inputs)
        
        spliced_waves = []
        
        for wave_input, segments, divergent_factor in zip(wave_inputs, segments_list, divergent_factors):
            spliced_wave = self.splice_divergent_x_lines(wave_input, segments, divergent_factor)
            spliced_waves.append(spliced_wave)
        
        return spliced_waves
    
    def analyze_splicing_effect(self, original_wave: torch.Tensor, 
                              spliced_wave: torch.Tensor) -> Dict[str, float]:
        """
        Analyze the effect of X-line splicing
        
        Args:
            original_wave: Original wave tensor
            spliced_wave: Spliced wave tensor
            
        Returns:
            Analysis results dictionary
        """
        # Convert to numpy for analysis
        orig_np = original_wave.cpu().numpy()
        spliced_np = spliced_wave.cpu().numpy()
        
        # Calculate metrics
        if len(orig_np.shape) > 1:
            orig_np = orig_np.flatten()
        if len(spliced_np.shape) > 1:
            spliced_np = spliced_np.flatten()
        
        # Calculate differences
        difference = spliced_np - orig_np
        mean_difference = float(np.mean(difference))
        std_difference = float(np.std(difference))
        
        # Calculate correlation
        correlation = float(np.corrcoef(orig_np, spliced_np)[0, 1])
        
        # Calculate spectral changes
        orig_fft = np.fft.fft(orig_np)
        spliced_fft = np.fft.fft(spliced_np)
        spectral_diff = np.mean(np.abs(orig_fft - spliced_fft))
        
        # Calculate divergence metrics
        divergence_metrics = {
            "segments_used": self.config.segments,
            "divergent_factor": self.config.divergent_threshold,
            "overlap_factor": self.config.overlap,
            "splicer_resolution": self.config.splicer_resolution
        }
        
        return {
            "mean_difference": mean_difference,
            "std_difference": std_difference,
            "correlation": correlation,
            "spectral_difference": float(spectral_diff),
            **divergence_metrics
        }
    
    def get_splicing_status(self) -> Dict[str, any]:
        """Get splicing status"""
        return {
            "initialized": self.initialized,
            "device": str(self.device),
            "config": {
                "segments": self.config.segments,
                "overlap": self.config.overlap,
                "divergent_threshold": self.config.divergent_threshold,
                "splicer_resolution": self.config.splicer_resolution,
                "multi_table_processing": self.config.multi_table_processing,
                "phase_preservation": self.config.phase_preservation
            },
            "processing_stats": self.processing_stats.copy()
        }
    
    def update_config(self, new_config: SplicerConfig):
        """Update configuration"""
        self.config = new_config
        
        # Reinitialize splicer with new config
        self.splicer = XLineWaveSplicer(new_config)
        self.splicer.to(self.device)
        self.splicer.eval()
        
        logging.info("X-Line wave splicer system configuration updated")
    
    def reset_statistics(self):
        """Reset processing statistics"""
        self.processing_stats = {
            "total_spliced": 0,
            "divergent_lines_generated": 0,
            "table_processing_used": 0,
            "phase_preservations": 0
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'splicer'):
            del self.splicer
        torch.cuda.empty_cache()
        logging.info("X-Line wave splicer system cleanup completed")


def create_splicer_system(config: Optional[SplicerConfig] = None) -> XLineWaveSplicerSystem:
    """
    Factory function to create X-line wave splicer system
    
    Args:
        config: Splicer configuration
        
    Returns:
        XLineWaveSplicerSystem instance
    """
    if config is None:
        config = SplicerConfig()
    
    splicer = XLineWaveSplicerSystem(config)
    splicer.initialize()
    
    return splicer


def create_hd_splicer_system() -> XLineWaveSplicerSystem:
    """
    Create splicer system optimized for HD audio
    
    Returns:
        Optimized XLineWaveSplicerSystem instance
    """
    config = SplicerConfig(
        segments=3,                    # More segments for HD audio
        overlap=0.05,                   # Less overlap for HD audio
        divergent_threshold=0.2,        # Lower threshold for HD audio
        splicer_resolution=2048,        # Higher resolution for HD audio
        multi_table_processing=True,     # Multi-table for HD audio
        phase_preservation=True,         # Phase preservation for HD audio
        table_1_size=1024,              # Larger tables for HD audio
        table_2_size=1024,              # Larger tables for HD audio
        interpolation_method="cubic",    # Cubic interpolation for HD audio
        adaptive_splicing=True,          # Adaptive splicing for HD audio
        smoothing_factor=0.05            # Less smoothing for HD audio
    )
    
    return create_splicer_system(config)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create splicer system
    splicer = create_splicer_system()
    
    # Create sample wave
    sample_rate = 22050
    duration = 2.0  # 2 seconds
    t = torch.linspace(0, duration, int(sample_rate * duration))
    wave_input = torch.sin(2 * torch.pi * 440 * t) + 0.3 * torch.sin(2 * torch.pi * 880 * t)
    
    # Apply divergent X-line splicing
    spliced_wave = splicer.splice_divergent_x_lines(wave_input, segments=2, divergent_factor=0.5)
    
    print(f"Original wave shape: {wave_input.shape}")
    print(f"Spliced wave shape: {spliced_wave.shape}")
    
    # Analyze effect
    analysis = splicer.analyze_splicing_effect(wave_input, spliced_wave)
    print(f"Splicing effect analysis: {analysis}")
    
    # Get status
    status = splicer.get_splicing_status()
    print(f"Splicing status: {status}")
    
    # Cleanup
    splicer.cleanup()
    
    print("X-Line wave splicer system example completed")
