# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

"""
Windows IOCTL Client for Directional Audio Control
Provides Python interface to communicate with the Windows directional audio driver
"""

import ctypes
import ctypes.wintypes
from typing import Optional, Tuple, Dict, Any
import struct
import logging

# Constants from driver header
GUID_DEVINTERFACE_DIRECTIONAL_AUDIO_CONTROL = '{12345678-1234-5678-12-34-56-78-9a-bc-de-f0}'

IOCTL_DIRECTIONAL_AUDIO_SET_POSITION = 0x222000
IOCTL_DIRECTIONAL_AUDIO_GET_POSITION = 0x222004
IOCTL_DIRECTIONAL_AUDIO_SET_CONFIG = 0x222008
IOCTL_DIRECTIONAL_AUDIO_GET_CONFIG = 0x22200C
IOCTL_DIRECTIONAL_AUDIO_ENABLE_PROCESSING = 0x222010
IOCTL_DIRECTIONAL_AUDIO_GET_STATUS = 0x222014

FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
FILE_ANY_ACCESS = 0

# CTL_CODE macro implementation
def CTL_CODE(device_type, function, method, access):
    return (device_type << 16) | (access << 14) | (function << 2) | method

# Recalculate IOCTLs with proper CTL_CODE
IOCTL_DIRECTIONAL_AUDIO_SET_POSITION = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_DIRECTIONAL_AUDIO_GET_POSITION = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_DIRECTIONAL_AUDIO_SET_CONFIG = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_DIRECTIONAL_AUDIO_GET_CONFIG = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_DIRECTIONAL_AUDIO_ENABLE_PROCESSING = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_ANY_ACCESS)
IOCTL_DIRECTIONAL_AUDIO_GET_STATUS = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x805, METHOD_BUFFERED, FILE_ANY_ACCESS)

# Data structures matching the driver
class DirectionalAudioPosition(ctypes.Structure):
    _fields_ = [
        ("X", ctypes.c_float),
        ("Y", ctypes.c_float),
        ("Z", ctypes.c_float),
        ("AvoidCenter", ctypes.c_bool),
        ("Azimuth", ctypes.c_float),
        ("Distance", ctypes.c_float),
    ]

class DirectionalAudioConfig(ctypes.Structure):
    _fields_ = [
        ("MaxAzimuthDegrees", ctypes.c_float),
        ("AvoidanceAngleDegrees", ctypes.c_float),
        ("ReferenceDistance", ctypes.c_float),
        ("EnableHRTF", ctypes.c_bool),
        ("EnableAmbisonics", ctypes.c_bool),
        ("SampleRate", ctypes.c_ulong),
        ("Channels", ctypes.c_ulong),
    ]

class DirectionalAudioEnable(ctypes.Structure):
    _fields_ = [
        ("EnableProcessing", ctypes.c_bool),
        ("EnableAvoidCenter", ctypes.c_bool),
    ]

class DirectionalAudioStatus(ctypes.Structure):
    _fields_ = [
        ("ProcessingEnabled", ctypes.c_bool),
        ("DriverReady", ctypes.c_bool),
        ("CurrentSampleRate", ctypes.c_ulong),
        ("CurrentChannels", ctypes.c_ulong),
        ("CurrentPosition", DirectionalAudioPosition),
        ("CurrentConfig", DirectionalAudioConfig),
    ]


class DirectionalAudioClient:
    """Client for communicating with the Windows directional audio driver"""
    
    def __init__(self):
        self.device_handle = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Connect to the directional audio device"""
        try:
            # Open device handle (simplified - in real implementation would find device path)
            device_path = r"\\.\DirectionalAudio"  # This would be the actual device path
            self.device_handle = ctypes.windll.kernel32.CreateFileW(
                device_path,
                0xC0000000,  # GENERIC_READ | GENERIC_WRITE
                3,            # FILE_SHARE_READ | FILE_SHARE_WRITE
                None,
                3,            # OPEN_EXISTING
                0,            # FILE_ATTRIBUTE_NORMAL
                None
            )
            
            if self.device_handle == -1 or self.device_handle is None:
                error = ctypes.get_last_error()
                self.logger.error(f"Failed to open device, error: {error}")
                return False
                
            self.logger.info("Successfully connected to directional audio device")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception connecting to device: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the device"""
        if self.device_handle:
            ctypes.windll.kernel32.CloseHandle(self.device_handle)
            self.device_handle = None
            self.logger.info("Disconnected from directional audio device")
    
    def _send_ioctl(self, ioctl_code: int, input_data: Optional[ctypes.Structure] = None, 
                   output_data_type: Optional[type] = None) -> Tuple[bool, Optional[ctypes.Structure]]:
        """Send IOCTL to the driver"""
        if not self.device_handle:
            return False, None
            
        try:
            # Prepare input buffer
            input_buffer = None
            input_size = 0
            if input_data:
                input_buffer = ctypes.byref(input_data)
                input_size = ctypes.sizeof(input_data)
            
            # Prepare output buffer
            output_buffer = None
            output_size = 0
            if output_data_type:
                output_buffer = ctypes.create_string_buffer(ctypes.sizeof(output_data_type))
                output_size = ctypes.sizeof(output_data_type)
            
            # Send IOCTL
            bytes_returned = ctypes.c_ulong()
            result = ctypes.windll.kernel32.DeviceIoControl(
                self.device_handle,
                ioctl_code,
                input_buffer,
                input_size,
                output_buffer,
                output_size,
                ctypes.byref(bytes_returned),
                None
            )
            
            if not result:
                error = ctypes.get_last_error()
                self.logger.error(f"IOCTL failed with error: {error}")
                return False, None
            
            # Parse output
            if output_data_type and output_buffer:
                output_obj = output_data_type()
                ctypes.memmove(ctypes.byref(output_obj), output_buffer, ctypes.sizeof(output_obj))
                return True, output_obj
                
            return True, None
            
        except Exception as e:
            self.logger.error(f"Exception sending IOCTL: {e}")
            return False, None
    
    def set_position(self, x: float, y: float, z: float = 0.0, avoid_center: bool = True) -> bool:
        """Set the audio source position"""
        position = DirectionalAudioPosition()
        position.X = float(x)
        position.Y = float(y)
        position.Z = float(z)
        position.AvoidCenter = avoid_center
        
        success, _ = self._send_ioctl(IOCTL_DIRECTIONAL_AUDIO_SET_POSITION, position)
        if success:
            self.logger.info(f"Set position: X={x}, Y={y}, Z={z}, AvoidCenter={avoid_center}")
        return success
    
    def get_position(self) -> Optional[Dict[str, Any]]:
        """Get the current audio source position"""
        success, position = self._send_ioctl(IOCTL_DIRECTIONAL_AUDIO_GET_POSITION, 
                                           None, DirectionalAudioPosition)
        if success and position:
            return {
                'x': position.X,
                'y': position.Y,
                'z': position.Z,
                'avoid_center': position.AvoidCenter,
                'azimuth': position.Azimuth,
                'distance': position.Distance
            }
        return None
    
    def set_config(self, max_azimuth_degrees: float = 40.0, avoidance_angle_degrees: float = 20.0,
                  reference_distance: float = 1.0, enable_hrtf: bool = True, 
                  enable_ambisonics: bool = False, sample_rate: int = 16000, 
                  channels: int = 2) -> bool:
        """Set the directional audio configuration"""
        config = DirectionalAudioConfig()
        config.MaxAzimuthDegrees = float(max_azimuth_degrees)
        config.AvoidanceAngleDegrees = float(avoidance_angle_degrees)
        config.ReferenceDistance = float(reference_distance)
        config.EnableHRTF = enable_hrtf
        config.EnableAmbisonics = enable_ambisonics
        config.SampleRate = sample_rate
        config.Channels = channels
        
        success, _ = self._send_ioctl(IOCTL_DIRECTIONAL_AUDIO_SET_CONFIG, config)
        if success:
            self.logger.info(f"Set config: MaxAzimuth={max_azimuth_degrees}°, "
                           f"AvoidanceAngle={avoidance_angle_degrees}°, "
                           f"SampleRate={sample_rate}, Channels={channels}")
        return success
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get the current configuration"""
        success, config = self._send_ioctl(IOCTL_DIRECTIONAL_AUDIO_GET_CONFIG, 
                                          None, DirectionalAudioConfig)
        if success and config:
            return {
                'max_azimuth_degrees': config.MaxAzimuthDegrees,
                'avoidance_angle_degrees': config.AvoidanceAngleDegrees,
                'reference_distance': config.ReferenceDistance,
                'enable_hrtf': config.EnableHRTF,
                'enable_ambisonics': config.EnableAmbisonics,
                'sample_rate': config.SampleRate,
                'channels': config.Channels
            }
        return None
    
    def enable_processing(self, enable_processing: bool = True, enable_avoid_center: bool = True) -> bool:
        """Enable or disable directional audio processing"""
        enable = DirectionalAudioEnable()
        enable.EnableProcessing = enable_processing
        enable.EnableAvoidCenter = enable_avoid_center
        
        success, _ = self._send_ioctl(IOCTL_DIRECTIONAL_AUDIO_ENABLE_PROCESSING, enable)
        if success:
            self.logger.info(f"Enable processing: {enable_processing}, Avoid center: {enable_avoid_center}")
        return success
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get the current driver status"""
        success, status = self._send_ioctl(IOCTL_DIRECTIONAL_AUDIO_GET_STATUS, 
                                          None, DirectionalAudioStatus)
        if success and status:
            return {
                'processing_enabled': status.ProcessingEnabled,
                'driver_ready': status.DriverReady,
                'current_sample_rate': status.CurrentSampleRate,
                'current_channels': status.CurrentChannels,
                'current_position': {
                    'x': status.CurrentPosition.X,
                    'y': status.CurrentPosition.Y,
                    'z': status.CurrentPosition.Z,
                    'avoid_center': status.CurrentPosition.AvoidCenter,
                    'azimuth': status.CurrentPosition.Azimuth,
                    'distance': status.CurrentPosition.Distance
                },
                'current_config': {
                    'max_azimuth_degrees': status.CurrentConfig.MaxAzimuthDegrees,
                    'avoidance_angle_degrees': status.CurrentConfig.AvoidanceAngleDegrees,
                    'reference_distance': status.CurrentConfig.ReferenceDistance,
                    'enable_hrtf': status.CurrentConfig.EnableHRTF,
                    'enable_ambisonics': status.CurrentConfig.EnableAmbisonics,
                    'sample_rate': status.CurrentConfig.SampleRate,
                    'channels': status.CurrentConfig.Channels
                }
            }
        return None


# Example usage and testing
def test_directional_audio_client():
    """Test the directional audio client"""
    logging.basicConfig(level=logging.INFO)
    
    client = DirectionalAudioClient()
    
    if not client.connect():
        print("Failed to connect to directional audio device")
        return
    
    try:
        # Test configuration
        print("Setting configuration...")
        if client.set_config(max_azimuth_degrees=40.0, avoidance_angle_degrees=20.0):
            print("Configuration set successfully")
        
        # Test enabling processing
        print("Enabling processing...")
        if client.enable_processing(True, True):
            print("Processing enabled successfully")
        
        # Test position setting
        positions = [
            (0.0, 0.0),   # Center
            (1.0, 0.0),   # Right
            (-1.0, 0.0),  # Left
            (0.5, 0.5),   # Upper-right with avoidance
            (0.5, -0.5),  # Lower-right with avoidance
        ]
        
        for x, y in positions:
            print(f"Setting position to ({x}, {y})...")
            if client.set_position(x, y):
                pos = client.get_position()
                if pos:
                    print(f"  Result: Azimuth={pos['azimuth']:.1f}°, Distance={pos['distance']:.2f}")
        
        # Get status
        print("Getting status...")
        status = client.get_status()
        if status:
            print(f"Driver ready: {status['driver_ready']}")
            print(f"Processing enabled: {status['processing_enabled']}")
            print(f"Current sample rate: {status['current_sample_rate']}")
            print(f"Current channels: {status['current_channels']}")
        
    finally:
        client.disconnect()


if __name__ == "__main__":
    test_directional_audio_client()
