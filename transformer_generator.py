# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Transformer Wave Signature Generator
Advanced transformer-based wave signature generation for TTS processing
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
class TransformerConfig:
    """Configuration for transformer wave signature generator"""
    d_model: int = 512
    nhead: int = 8
    num_encoder_layers: int = 6
    num_decoder_layers: int = 6
    dim_feedforward: int = 2048
    dropout: float = 0.1
    activation: str = "gelu"
    layer_norm_eps: float = 1e-5
    batch_first: bool = True
    
    # Wave-specific parameters
    signature_length: int = 1024
    frequency_bins: int = 128
    temporal_resolution: int = 4
    signature_complexity: float = 0.8
    adaptive_signature: bool = True
    multi_scale_analysis: bool = True
    phase_preservation: bool = True
    
    # Output parameters
    output_channels: int = 1
    output_range: float = 1.0
    normalize_output: bool = True


class WaveSignatureEmbedding(nn.Module):
    """Embedding layer for wave signature generation"""
    
    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        
        # Wave analysis embeddings
        self.frequency_embedding = nn.Linear(config.frequency_bins, config.d_model // 4)
        self.time_embedding = nn.Linear(config.signature_length, config.d_model // 4)
        self.amplitude_embedding = nn.Linear(1, config.d_model // 4)
        self.phase_embedding = nn.Linear(1, config.d_model // 4)
        
        # Multi-scale analysis
        if config.multi_scale_analysis:
            self.scale_embeddings = nn.ModuleList([
                nn.Linear(config.frequency_bins // (2 ** i), config.d_model // 8)
                for i in range(3)  # 3 different scales
            ])
            scale_embedding_dim = config.d_model // 8 * 3
        else:
            scale_embedding_dim = 0
        
        # Combine embeddings
        total_embedding_dim = config.d_model // 4 * 4 + scale_embedding_dim
        self.embedding_projection = nn.Linear(total_embedding_dim, config.d_model)
        
        # Positional encoding
        self.positional_encoding = self._create_positional_encoding(
            config.signature_length,
            config.d_model
        )
        
        self.dropout = nn.Dropout(config.dropout)
    
    def _create_positional_encoding(self, max_len: int, d_model: int) -> torch.Tensor:
        """Create sinusoidal positional encoding"""
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        return pe.unsqueeze(0)
    
    def forward(self, wave_audio: torch.Tensor, mel_context: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass for wave signature embedding
        
        Args:
            wave_audio: Input wave audio tensor [batch_size, sequence_length]
            mel_context: Optional mel spectrogram context [batch_size, mel_bins, mel_frames]
            
        Returns:
            Embedded wave signature [batch_size, signature_length, d_model]
        """
        batch_size, seq_len = wave_audio.shape
        
        # Convert wave to frequency domain
        wave_complex = torch.fft.rfft(wave_audio, dim=-1)
        wave_magnitude = torch.abs(wave_complex)
        wave_phase = torch.angle(wave_complex)
        
        # Pad or truncate to signature length
        if seq_len != self.config.signature_length:
            if seq_len < self.config.signature_length:
                # Pad with zeros
                pad_length = self.config.signature_length - seq_len
                wave_audio = F.pad(wave_audio, (0, pad_length))
                wave_magnitude = F.pad(wave_magnitude, (0, pad_length))
                wave_phase = F.pad(wave_phase, (0, pad_length))
            else:
                # Truncate
                wave_audio = wave_audio[:, :self.config.signature_length]
                wave_magnitude = wave_magnitude[:, :self.config.signature_length]
                wave_phase = wave_phase[:, :self.config.signature_length]
            seq_len = self.config.signature_length
        
        # Frequency domain embedding
        freq_emb = self.frequency_embedding(wave_magnitude)
        
        # Time domain embedding
        time_emb = self.time_embedding(wave_audio.unsqueeze(-1))
        
        # Amplitude and phase embeddings
        amp_emb = self.amplitude_embedding(wave_audio.unsqueeze(-1))
        phase_emb = self.phase_embedding(wave_phase.unsqueeze(-1))
        
        # Multi-scale embeddings
        scale_embeddings = []
        if self.config.multi_scale_analysis:
            for i, scale_embedding in enumerate(self.scale_embeddings):
                # Downsample for different scales
                scale_factor = 2 ** i
                downsampled = F.avg_pool1d(wave_magnitude.unsqueeze(1), kernel_size=scale_factor, stride=scale_factor)
                scale_emb = scale_embedding(downsampled.squeeze(1))
                
                # Upsample back to original size
                scale_emb = F.interpolate(scale_emb.unsqueeze(1), size=self.config.signature_length, mode='linear', align_corners=False)
                scale_embeddings.append(scale_emb.squeeze(1))
        
        # Combine all embeddings
        embeddings = [freq_emb, time_emb, amp_emb, phase_emb] + scale_embeddings
        combined_emb = torch.cat(embeddings, dim=-1)
        
        # Project to d_model
        projected_emb = self.embedding_projection(combined_emb)
        
        # Add positional encoding
        pos_enc = self.positional_encoding[:, :seq_len, :].to(wave_audio.device)
        final_emb = projected_emb + pos_enc
        
        return self.dropout(final_emb)


class WaveSignatureTransformer(nn.Module):
    """Main transformer for wave signature generation"""
    
    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        
        # Input embedding
        self.embedding = WaveSignatureEmbedding(config)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            activation=config.activation,
            layer_norm_eps=config.layer_norm_eps,
            batch_first=config.batch_first
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=config.num_encoder_layers)
        
        # Transformer decoder
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=config.d_model,
            nhead=config.nhead,
            dim_feedforward=config.dim_feedforward,
            dropout=config.dropout,
            activation=config.activation,
            layer_norm_eps=config.layer_norm_eps,
            batch_first=config.batch_first
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=config.num_decoder_layers)
        
        # Output projection
        self.output_projection = nn.Sequential(
            nn.Linear(config.d_model, config.d_model // 2),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.d_model // 2, config.output_channels)
        )
        
        # Signature complexity control
        self.signature_complexity = nn.Parameter(torch.tensor(config.signature_complexity))
        
        # Adaptive signature
        self.adaptive_signature = config.adaptive_signature
        if self.adaptive_signature:
            self.adaptive_weight = nn.Linear(config.d_model, 1)
            self.adaptive_activation = nn.Sigmoid()
        
        # Phase preservation
        self.phase_preservation = config.phase_preservation
        if self.phase_preservation:
            self.phase_predictor = nn.Linear(config.d_model, 1)
        
    def forward(self, wave_audio: torch.Tensor, mel_context: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass for wave signature generation
        
        Args:
            wave_audio: Input wave audio tensor [batch_size, sequence_length]
            mel_context: Optional mel spectrogram context
            
        Returns:
            Generated wave signature [batch_size, signature_length, output_channels]
        """
        # Input embedding
        embedded_wave = self.embedding(wave_audio, mel_context)
        
        # Create target sequence (autoregressive)
        target_sequence = embedded_wave
        
        # Encoder pass
        memory = self.encoder(embedded_wave)
        
        # Decoder pass
        decoded = self.decoder(target_sequence, memory)
        
        # Output projection
        signature = self.output_projection(decoded)
        
        # Apply signature complexity control
        signature = signature * self.signature_complexity
        
        # Adaptive signature weighting
        if self.adaptive_signature:
            adaptive_weight = self.adaptive_weight(decoded)
            adaptive_weight = self.adaptive_activation(adaptive_weight)
            signature = signature * adaptive_weight
        
        # Phase preservation
        if self.phase_preservation:
            phase_correction = self.phase_predictor(decoded)
            signature = signature + phase_correction
        
        # Normalize output
        if self.config.normalize_output:
            signature = torch.tanh(signature) * self.config.output_range
        
        return signature
    
    def generate_signature(self, wave_audio: torch.Tensor, mel_context: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Generate wave signature
        
        Args:
            wave_audio: Input wave audio tensor
            mel_context: Optional mel spectrogram context
            
        Returns:
            Generated wave signature tensor
        """
        self.eval()
        with torch.no_grad():
            return self.forward(wave_audio, mel_context)
    
    def initialize(self):
        """Initialize the transformer"""
        self.eval()
        logging.info(f"Wave signature transformer initialized with {self.config.num_encoder_layers} encoder layers and {self.config.num_decoder_layers} decoder layers")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'encoder'):
            del self.encoder
        if hasattr(self, 'decoder'):
            del self.decoder
        if hasattr(self, 'embedding'):
            del self.embedding
        torch.cuda.empty_cache()
        logging.info("Wave signature transformer cleanup completed")
    
    def get_generation_stats(self) -> Dict[str, any]:
        """Get generation statistics"""
        return {
            "d_model": self.config.d_model,
            "nhead": self.config.nhead,
            "num_encoder_layers": self.config.num_encoder_layers,
            "num_decoder_layers": self.config.num_decoder_layers,
            "signature_length": self.config.signature_length,
            "frequency_bins": self.config.frequency_bins,
            "signature_complexity": self.signature_complexity.item(),
            "adaptive_signature": self.adaptive_signature,
            "multi_scale_analysis": self.config.multi_scale_analysis,
            "phase_preservation": self.phase_preservation,
            "output_channels": self.config.output_channels
        }


class WaveSignatureGenerator:
    """
    High-level wave signature generator with additional processing
    """
    
    def __init__(self, config: TransformerConfig):
        self.config = config
        self.transformer = WaveSignatureTransformer(config)
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Additional processing components
        self.signature_enhancer = None
        self.quality_analyzer = None
        
        logging.info(f"Wave signature generator initialized on device: {self.device}")
    
    def initialize(self):
        """Initialize the generator"""
        self.transformer.to(self.device)
        self.transformer.initialize()
        
        # Initialize additional components
        self._initialize_enhancer()
        self._initialize_analyzer()
        
        self.initialized = True
        logging.info("Wave signature generator fully initialized")
    
    def _initialize_enhancer(self):
        """Initialize signature enhancer"""
        self.signature_enhancer = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv1d(16, 8, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv1d(8, 1, kernel_size=3, padding=1),
            nn.Tanh()
        ).to(self.device)
    
    def _initialize_analyzer(self):
        """Initialize quality analyzer"""
        self.quality_analyzer = nn.Sequential(
            nn.Linear(self.config.signature_length, 256),
            nn.GELU(),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        ).to(self.device)
    
    def generate_signature(self, wave_audio: torch.Tensor, mel_context: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Generate enhanced wave signature
        
        Args:
            wave_audio: Input wave audio tensor
            mel_context: Optional mel spectrogram context
            
        Returns:
            Enhanced wave signature tensor
        """
        if not self.initialized:
            raise RuntimeError("Generator not initialized. Call initialize() first.")
        
        # Move to device
        wave_audio = wave_audio.to(self.device)
        if mel_context is not None:
            mel_context = mel_context.to(self.device)
        
        # Generate base signature
        signature = self.transformer.generate_signature(wave_audio, mel_context)
        
        # Enhance signature
        if self.signature_enhancer is not None:
            enhanced_signature = self.signature_enhancer(signature.squeeze(-1))
            signature = enhanced_signature.unsqueeze(-1)
        
        # Analyze quality
        quality_score = None
        if self.quality_analyzer is not None:
            quality_score = self.quality_analyzer(signature.squeeze(-1))
        
        # Log quality information
        if quality_score is not None:
            avg_quality = quality_score.mean().item()
            logging.debug(f"Generated signature quality score: {avg_quality:.3f}")
        
        return signature
    
    def batch_generate_signatures(self, wave_audios: List[torch.Tensor], 
                                 mel_contexts: Optional[List[torch.Tensor]] = None) -> List[torch.Tensor]:
        """
        Generate signatures for multiple wave audio inputs
        
        Args:
            wave_audios: List of wave audio tensors
            mel_contexts: Optional list of mel spectrogram contexts
            
        Returns:
            List of generated signature tensors
        """
        if not self.initialized:
            raise RuntimeError("Generator not initialized. Call initialize() first.")
        
        if mel_contexts is None:
            mel_contexts = [None] * len(wave_audios)
        
        signatures = []
        
        for wave_audio, mel_context in zip(wave_audios, mel_contexts):
            signature = self.generate_signature(wave_audio, mel_context)
            signatures.append(signature)
        
        return signatures
    
    def analyze_signature_quality(self, signature: torch.Tensor) -> Dict[str, float]:
        """
        Analyze the quality of generated signature
        
        Args:
            signature: Generated signature tensor
            
        Returns:
            Quality analysis dictionary
        """
        if not self.initialized or self.quality_analyzer is None:
            return {"error": "Quality analyzer not available"}
        
        signature = signature.to(self.device)
        
        with torch.no_grad():
            quality_score = self.quality_analyzer(signature.squeeze(-1))
            
            # Additional quality metrics
            signature_np = signature.cpu().numpy()
            
            # Calculate statistics
            mean_amplitude = float(np.mean(np.abs(signature_np)))
            peak_amplitude = float(np.max(np.abs(signature_np)))
            zero_crossing_rate = self._calculate_zero_crossing_rate(signature_np)
            spectral_centroid = self._calculate_spectral_centroid(signature_np)
            
            return {
                "quality_score": float(quality_score.mean().item()),
                "mean_amplitude": mean_amplitude,
                "peak_amplitude": peak_amplitude,
                "zero_crossing_rate": zero_crossing_rate,
                "spectral_centroid": spectral_centroid
            }
    
    def _calculate_zero_crossing_rate(self, signal: np.ndarray) -> float:
        """Calculate zero crossing rate"""
        if len(signal.shape) > 1:
            signal = signal.flatten()
        
        zero_crossings = np.where(np.diff(np.signbit(signal)))[0]
        return len(zero_crossings) / len(signal)
    
    def _calculate_spectral_centroid(self, signal: np.ndarray) -> float:
        """Calculate spectral centroid"""
        if len(signal.shape) > 1:
            signal = signal.flatten()
        
        # Compute FFT
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal))
        
        # Calculate spectral centroid
        magnitude = np.abs(fft)
        spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        
        return float(spectral_centroid)
    
    def get_generation_status(self) -> Dict[str, any]:
        """Get generation status"""
        return {
            "initialized": self.initialized,
            "device": str(self.device),
            "transformer_stats": self.transformer.get_generation_stats(),
            "signature_enhancer_available": self.signature_enhancer is not None,
            "quality_analyzer_available": self.quality_analyzer is not None
        }
    
    def update_config(self, new_config: TransformerConfig):
        """Update configuration"""
        self.config = new_config
        
        # Reinitialize transformer with new config
        self.transformer = WaveSignatureTransformer(new_config)
        self.transformer.to(self.device)
        self.transformer.initialize()
        
        logging.info("Wave signature generator configuration updated")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.transformer:
            self.transformer.cleanup()
        
        if self.signature_enhancer:
            del self.signature_enhancer
        
        if self.quality_analyzer:
            del self.quality_analyzer
        
        torch.cuda.empty_cache()
        logging.info("Wave signature generator cleanup completed")


def create_transformer_generator(config: Optional[TransformerConfig] = None) -> WaveSignatureGenerator:
    """
    Factory function to create transformer wave signature generator
    
    Args:
        config: Transformer configuration
        
    Returns:
        WaveSignatureGenerator instance
    """
    if config is None:
        config = TransformerConfig()
    
    generator = WaveSignatureGenerator(config)
    generator.initialize()
    
    return generator


def create_hd_signature_generator() -> WaveSignatureGenerator:
    """
    Create generator optimized for HD audio signatures
    
    Returns:
        Optimized WaveSignatureGenerator instance
    """
    config = TransformerConfig(
        d_model=1024,                # Larger model for HD audio
        nhead=16,                     # More attention heads
        num_encoder_layers=8,         # More encoder layers
        num_decoder_layers=8,         # More decoder layers
        dim_feedforward=4096,         # Larger feedforward
        signature_length=2048,        # Longer signature for HD audio
        frequency_bins=256,           # More frequency bins for HD audio
        signature_complexity=0.9,     # Higher complexity for HD audio
        adaptive_signature=True,      # Adaptive processing
        multi_scale_analysis=True,    # Multi-scale analysis
        phase_preservation=True,       # Phase preservation
        output_channels=2              # Stereo output for HD audio
    )
    
    return create_transformer_generator(config)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create generator
    generator = create_transformer_generator()
    
    # Create sample wave audio
    sample_rate = 22050
    duration = 2.0  # 2 seconds
    t = torch.linspace(0, duration, int(sample_rate * duration))
    wave_audio = torch.sin(2 * torch.pi * 440 * t) + 0.5 * torch.sin(2 * torch.pi * 880 * t)
    
    # Generate signature
    signature = generator.generate_signature(wave_audio.unsqueeze(0))
    
    print(f"Input wave shape: {wave_audio.shape}")
    print(f"Generated signature shape: {signature.shape}")
    
    # Analyze quality
    quality = generator.analyze_signature_quality(signature)
    print(f"Signature quality: {quality}")
    
    # Get generation status
    status = generator.get_generation_status()
    print(f"Generation status: {status}")
    
    # Cleanup
    generator.cleanup()
    
    print("Wave signature generator example completed")
