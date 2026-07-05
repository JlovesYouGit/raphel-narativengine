# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
RadTTS FastPitch Decoder for WAV Format Processing
Advanced Text-to-Speech system with Megatron integration and wave signature generation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import librosa
import soundfile as sf
from nemo.utils import logging
from nemo.collections.tts.models import FastPitchModel
from nemo.collections.tts.modules.waveglow import WaveGlowModule

from nemo2riva.megatron_wave_correction.megatron_processor import MegatronWaveProcessor
from nemo2riva.wave_signature.transformer_generator import WaveSignatureTransformer
from nemo2riva.trajectory_override.x_wave_processor import XWaveTrajectoryProcessor
from nemo2riva.divergent_splicer.x_line_splicer import XLineWaveSplicer


@dataclass
class FastPitchConfig:
    """Configuration for FastPitch decoder"""
    sample_rate: int = 22050
    n_mel_channels: int = 80
    n_fft: int = 1024
    hop_length: int = 256
    win_length: int = 1024
    n_speakers: int = 1
    pitch_embedding_kernel: int = 3
    pitch_avg: bool = True
    pitch_norm: bool = True
    pitch_mean: float = 220.0
    pitch_std: float = 0.0
    pitch_fmin: float = 0.0
    pitch_fmax: float = 400.0
    supress_tokens: List = None
    emb_relational: bool = True
    emb_reduction: int = 1
    speaker_emb_weight: float = 1.0
    max_wav_value: float = 32768.0
    mel_fmin: float = 0.0
    mel_fmax: float = 8000.0
    window: str = "hann"
    n_mels: int = 80
    mel_norm: str = "slaney"
    mel_scale: str = "htk"
    normalize: bool = False
    preemphasis: float = 0.97
    n_frames: int = 512
    n_iter: int = 32
    denoiser_strength: float = 0.1


@dataclass
class WaveProcessingConfig:
    """Configuration for wave processing pipeline"""
    enable_megatron_correction: bool = True
    enable_transformer_signature: bool = True
    enable_trajectory_override: bool = True
    enable_divergent_splicing: bool = True
    
    # Wave trajectory parameters
    x0_start_position: float = 0.0
    xval_end_position: float = 1.0
    trajectory_length: int = 1024
    divergent_factor: float = 0.5
    
    # Splicer parameters
    splicer_segments: int = 2
    segment_overlap: float = 0.1
    divergent_threshold: float = 0.3


class FastPitchWAVDecoder:
    """
    Advanced FastPitch decoder with WAV format processing and Megatron integration
    """
    
    def __init__(self, fastpitch_config: FastPitchConfig, wave_config: WaveProcessingConfig):
        self.fastpitch_config = fastpitch_config
        self.wave_config = wave_config
        
        # Initialize FastPitch model
        self.fastpitch_model = None
        self.waveglow_model = None
        
        # Initialize wave processing components
        self.megatron_processor = None
        self.wave_signature_transformer = None
        self.trajectory_processor = None
        self.divergent_splicer = None
        
        # Processing state
        self.initialized = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        logging.info(f"FastPitch WAV Decoder initialized on device: {self.device}")
    
    def initialize_models(self, fastpitch_checkpoint: str, waveglow_checkpoint: str):
        """Initialize FastPitch and WaveGlow models"""
        try:
            # Load FastPitch model
            self.fastpitch_model = FastPitchModel.restore_from(
                fastpitch_checkpoint, 
                map_location=self.device
            )
            self.fastpitch_model.eval()
            
            # Load WaveGlow model
            self.waveglow_model = WaveGlowModule.restore_from(
                waveglow_checkpoint,
                map_location=self.device
            )
            self.waveglow_model.eval()
            
            logging.info("FastPitch and WaveGlow models loaded successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize models: {e}")
            raise
    
    def initialize_wave_processors(self):
        """Initialize wave processing components"""
        try:
            # Initialize Megatron wave processor
            if self.wave_config.enable_megatron_correction:
                from nemo2riva.megatron_wave_correction.megatron_config import MegatronConfig
                megatron_config = MegatronConfig(
                    model_type="wave_correction",
                    hidden_size=512,
                    num_layers=12,
                    num_attention_heads=8
                )
                self.megatron_processor = MegatronWaveProcessor(megatron_config)
                self.megatron_processor.initialize()
            
            # Initialize wave signature transformer
            if self.wave_config.enable_transformer_signature:
                from nemo2riva.wave_signature.transformer_config import TransformerConfig
                transformer_config = TransformerConfig(
                    d_model=512,
                    nhead=8,
                    num_encoder_layers=6,
                    num_decoder_layers=6,
                    dim_feedforward=2048
                )
                self.wave_signature_transformer = WaveSignatureTransformer(transformer_config)
                self.wave_signature_transformer.initialize()
            
            # Initialize trajectory processor
            if self.wave_config.enable_trajectory_override:
                from nemo2riva.trajectory_override.trajectory_config import TrajectoryConfig
                trajectory_config = TrajectoryConfig(
                    x0_start=self.wave_config.x0_start_position,
                    xval_end=self.wave_config.xval_end_position,
                    trajectory_length=self.wave_config.trajectory_length,
                    divergent_factor=self.wave_config.divergent_factor
                )
                self.trajectory_processor = XWaveTrajectoryProcessor(trajectory_config)
                self.trajectory_processor.initialize()
            
            # Initialize divergent splicer
            if self.wave_config.enable_divergent_splicing:
                from nemo2riva.divergent_splicer.splicer_config import SplicerConfig
                splicer_config = SplicerConfig(
                    segments=self.wave_config.splicer_segments,
                    overlap=self.wave_config.segment_overlap,
                    divergent_threshold=self.wave_config.divergent_threshold
                )
                self.divergent_splicer = XLineWaveSplicer(splicer_config)
                self.divergent_splicer.initialize()
            
            self.initialized = True
            logging.info("Wave processing components initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize wave processors: {e}")
            raise
    
    def decode_wav_to_mel(self, wav_path: str) -> torch.Tensor:
        """
        Decode WAV file to mel spectrogram using FastPitch
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Mel spectrogram tensor
        """
        try:
            # Load WAV file
            audio, sr = librosa.load(wav_path, sr=self.fastpitch_config.sample_rate)
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).to(self.device)
            
            # Generate mel spectrogram
            with torch.no_grad():
                mel_spec, _ = self.fastpitch_model.process_batch(
                    audio_tensor, 
                    speaker=0
                )
            
            logging.info(f"Generated mel spectrogram with shape: {mel_spec.shape}")
            return mel_spec
            
        except Exception as e:
            logging.error(f"Failed to decode WAV to mel: {e}")
            raise
    
    def mel_to_wave_with_processing(self, mel_spec: torch.Tensor, text: str = "") -> torch.Tensor:
        """
        Convert mel spectrogram to waveform with advanced wave processing
        
        Args:
            mel_spec: Input mel spectrogram
            text: Optional text for context
            
        Returns:
            Processed waveform tensor
        """
        try:
            # Step 1: Generate initial waveform with WaveGlow
            with torch.no_grad():
                initial_wave = self.waveglow_model.infer(mel_spec)
            
            logging.info(f"Generated initial waveform with shape: {initial_wave.shape}")
            
            # Step 2: Apply Megatron wave format correction
            if self.wave_config.enable_megatron_correction and self.megatron_processor:
                corrected_wave = self.megatron_processor.correct_wave_format(
                    initial_wave, 
                    text_context=text
                )
                logging.info("Applied Megatron wave format correction")
            else:
                corrected_wave = initial_wave
            
            # Step 3: Generate wave signature with transformer
            if self.wave_config.enable_transformer_signature and self.wave_signature_transformer:
                wave_signature = self.wave_signature_transformer.generate_signature(
                    corrected_wave,
                    mel_context=mel_spec
                )
                logging.info(f"Generated wave signature with shape: {wave_signature.shape}")
            else:
                wave_signature = corrected_wave
            
            # Step 4: Apply trajectory override with X0/Xval processing
            if self.wave_config.enable_trajectory_override and self.trajectory_processor:
                trajectory_wave = self.trajectory_processor.apply_trajectory_override(
                    wave_signature,
                    x0_start=self.wave_config.x0_start_position,
                    xval_end=self.wave_config.xval_end_position
                )
                logging.info("Applied trajectory override with X0/Xval processing")
            else:
                trajectory_wave = wave_signature
            
            # Step 5: Apply divergent X-line wave splicing
            if self.wave_config.enable_divergent_splicing and self.divergent_splicer:
                final_wave = self.divergent_splicer.splice_divergent_x_lines(
                    trajectory_wave,
                    segments=self.wave_config.splicer_segments,
                    divergent_factor=self.wave_config.divergent_factor
                )
                logging.info("Applied divergent X-line wave splicing")
            else:
                final_wave = trajectory_wave
            
            return final_wave
            
        except Exception as e:
            logging.error(f"Failed to process mel to wave: {e}")
            raise
    
    def process_wav_file(self, wav_path: str, output_path: str, text: str = "") -> Dict[str, any]:
        """
        Complete WAV file processing pipeline
        
        Args:
            wav_path: Input WAV file path
            output_path: Output WAV file path
            text: Optional text for context
            
        Returns:
            Processing results dictionary
        """
        try:
            logging.info(f"Starting WAV file processing: {wav_path}")
            
            # Decode WAV to mel spectrogram
            mel_spec = self.decode_wav_to_mel(wav_path)
            
            # Process mel to waveform with advanced processing
            processed_wave = self.mel_to_wave_with_processing(mel_spec, text)
            
            # Save processed waveform
            processed_wave_np = processed_wave.cpu().numpy()
            sf.write(output_path, processed_wave_np, self.fastpitch_config.sample_rate)
            
            # Generate processing results
            results = {
                "input_file": wav_path,
                "output_file": output_path,
                "mel_shape": mel_spec.shape,
                "wave_shape": processed_wave.shape,
                "sample_rate": self.fastpitch_config.sample_rate,
                "processing_steps": self._get_processing_steps(),
                "success": True
            }
            
            logging.info(f"WAV file processing completed: {output_path}")
            return results
            
        except Exception as e:
            logging.error(f"Failed to process WAV file: {e}")
            return {
                "input_file": wav_path,
                "output_file": output_path,
                "error": str(e),
                "success": False
            }
    
    def batch_process_wav_files(self, wav_paths: List[str], output_dir: str, 
                               texts: List[str] = None) -> List[Dict[str, any]]:
        """
        Batch process multiple WAV files
        
        Args:
            wav_paths: List of input WAV file paths
            output_dir: Output directory
            texts: Optional list of text contexts
            
        Returns:
            List of processing results
        """
        import os
        
        if texts is None:
            texts = [""] * len(wav_paths)
        
        results = []
        
        for i, wav_path in enumerate(wav_paths):
            try:
                # Generate output path
                os.makedirs(output_dir, exist_ok=True)
                filename = os.path.basename(wav_path)
                output_path = os.path.join(output_dir, f"processed_{filename}")
                
                # Process single file
                result = self.process_wav_file(wav_path, output_path, texts[i])
                results.append(result)
                
            except Exception as e:
                logging.error(f"Failed to process {wav_path}: {e}")
                results.append({
                    "input_file": wav_path,
                    "output_file": "",
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    def text_to_speech_with_processing(self, text: str, speaker_id: int = 0, 
                                      output_path: str = None) -> torch.Tensor:
        """
        Convert text to speech with advanced wave processing
        
        Args:
            text: Input text
            speaker_id: Speaker ID
            output_path: Optional output path
            
        Returns:
            Processed waveform tensor
        """
        try:
            logging.info(f"Starting text-to-speech processing: {text[:50]}...")
            
            # Generate mel spectrogram from text
            with torch.no_grad():
                mel_spec, _ = self.fastpitch_model.generate_spectrogram(
                    text=text,
                    speaker=speaker_id
                )
            
            # Process mel to waveform with advanced processing
            processed_wave = self.mel_to_wave_with_processing(mel_spec, text)
            
            # Save if output path provided
            if output_path:
                processed_wave_np = processed_wave.cpu().numpy()
                sf.write(output_path, processed_wave_np, self.fastpitch_config.sample_rate)
                logging.info(f"TTS output saved: {output_path}")
            
            return processed_wave
            
        except Exception as e:
            logging.error(f"Failed to convert text to speech: {e}")
            raise
    
    def get_processing_status(self) -> Dict[str, any]:
        """Get current processing status"""
        status = {
            "initialized": self.initialized,
            "device": str(self.device),
            "fastpitch_model_loaded": self.fastpitch_model is not None,
            "waveglow_model_loaded": self.waveglow_model is not None,
            "megatron_processor_loaded": self.megatron_processor is not None,
            "wave_signature_transformer_loaded": self.wave_signature_transformer is not None,
            "trajectory_processor_loaded": self.trajectory_processor is not None,
            "divergent_splicer_loaded": self.divergent_splicer is not None,
            "processing_steps": self._get_processing_steps()
        }
        return status
    
    def _get_processing_steps(self) -> List[str]:
        """Get list of enabled processing steps"""
        steps = ["FastPitch decoding", "WaveGlow inference"]
        
        if self.wave_config.enable_megatron_correction:
            steps.append("Megatron wave correction")
        
        if self.wave_config.enable_transformer_signature:
            steps.append("Transformer wave signature")
        
        if self.wave_config.enable_trajectory_override:
            steps.append("X0/Xval trajectory override")
        
        if self.wave_config.enable_divergent_splicing:
            steps.append("Divergent X-line splicing")
        
        return steps
    
    def update_wave_config(self, new_config: WaveProcessingConfig):
        """Update wave processing configuration"""
        self.wave_config = new_config
        
        # Reinitialize processors with new config
        if self.initialized:
            self.initialize_wave_processors()
        
        logging.info("Wave processing configuration updated")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.fastpitch_model:
                del self.fastpitch_model
            
            if self.waveglow_model:
                del self.waveglow_model
            
            if self.megatron_processor:
                self.megatron_processor.cleanup()
            
            if self.wave_signature_transformer:
                self.wave_signature_transformer.cleanup()
            
            if self.trajectory_processor:
                self.trajectory_processor.cleanup()
            
            if self.divergent_splicer:
                self.divergent_splicer.cleanup()
            
            torch.cuda.empty_cache()
            logging.info("FastPitch WAV decoder cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")


def create_fastpitch_decoder(fastpitch_config: Optional[FastPitchConfig] = None,
                           wave_config: Optional[WaveProcessingConfig] = None) -> FastPitchWAVDecoder:
    """
    Factory function to create FastPitch WAV decoder
    
    Args:
        fastpitch_config: FastPitch configuration
        wave_config: Wave processing configuration
        
    Returns:
        FastPitchWAVDecoder instance
    """
    if fastpitch_config is None:
        fastpitch_config = FastPitchConfig()
    
    if wave_config is None:
        wave_config = WaveProcessingConfig()
    
    return FastPitchWAVDecoder(fastpitch_config, wave_config)


def create_hd_audio_decoder(fastpitch_checkpoint: str, waveglow_checkpoint: str) -> FastPitchWAVDecoder:
    """
    Create decoder optimized for HD audio processing
    
    Args:
        fastpitch_checkpoint: Path to FastPitch checkpoint
        waveglow_checkpoint: Path to WaveGlow checkpoint
        
    Returns:
        Configured FastPitchWAVDecoder instance
    """
    # HD audio optimized configurations
    fastpitch_config = FastPitchConfig(
        sample_rate=44100,  # Higher sample rate for HD audio
        n_mel_channels=128,  # More mel channels for better quality
        n_fft=2048,         # Larger FFT for better frequency resolution
        hop_length=512,      # Larger hop length for HD audio
        win_length=2048,    # Larger window for HD audio
        mel_fmax=12000.0    # Higher frequency range for HD audio
    )
    
    wave_config = WaveProcessingConfig(
        enable_megatron_correction=True,
        enable_transformer_signature=True,
        enable_trajectory_override=True,
        enable_divergent_splicing=True,
        trajectory_length=2048,  # Longer trajectory for HD audio
        divergent_factor=0.3,    # Lower divergence for HD audio
        splicer_segments=3        # More segments for HD audio
    )
    
    decoder = FastPitchWAVDecoder(fastpitch_config, wave_config)
    decoder.initialize_models(fastpitch_checkpoint, waveglow_checkpoint)
    decoder.initialize_wave_processors()
    
    return decoder


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create decoder
    decoder = create_fastpitch_decoder()
    
    # Initialize with model checkpoints
    # decoder.initialize_models("path/to/fastpitch.nemo", "path/to/waveglow.nemo")
    # decoder.initialize_wave_processors()
    
    # Process a WAV file
    # results = decoder.process_wav_file("input.wav", "output.wav", "Hello world")
    # print(f"Processing results: {results}")
    
    # Text-to-speech with processing
    # waveform = decoder.text_to_speech_with_processing("Hello, this is a test", output_path="tts_output.wav")
    # print(f"Generated waveform shape: {waveform.shape}")
    
    print("FastPitch WAV decoder example completed")
