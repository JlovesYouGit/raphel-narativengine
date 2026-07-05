/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#ifndef HD_AUDIO_BLUETOOTH_H
#define HD_AUDIO_BLUETOOTH_H

#include <ntddk.h>
#include <acx.h>
#include <ks.h>
#include <ksmedia.h>
#include <bthdef.h>
#include <bthsdpdef.h>

//
// HD Audio Bluetooth Device Interface GUID
//
DEFINE_GUID(GUID_DEVINTERFACE_HD_AUDIO_BLUETOOTH,
    0x8F2A1B3C, 0x4D5E, 0x6F7A, 0x8B, 0x9C, 0xD0, 0xE1, 0xF2, 0xA3, 0xB4, 0xC5);

//
// HD Audio Bluetooth Property Set GUID
//
DEFINE_GUID(GUID_HD_AUDIO_BLUETOOTH_PROPERTY_SET,
    0x7A9B2C1D, 0x3E4F, 0x5A6B, 0x7C, 0x8D, 0x9E, 0xA0, 0xB1, 0xC2, 0xD3, 0xE4);

//
// Bluetooth 5.2 Audio IOCTLs
//
#define IOCTL_HD_AUDIO_BLUETOOTH_SET_CODEC \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x900, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_GET_CODEC \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x901, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_SET_QUALITY \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x902, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_GET_QUALITY \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x903, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_SET_LATENCY \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x904, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_GET_LATENCY \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x905, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_SET_SPECTRUM \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x906, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_GET_SPECTRUM \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x907, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_ENABLE_LAG_CORRECTION \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x908, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_HD_AUDIO_BLUETOOTH_GET_CONNECTION_STATUS \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x909, METHOD_BUFFERED, FILE_ANY_ACCESS)

//
// HD Audio Codec Types
//
typedef enum {
    HD_AUDIO_CODEC_SBC = 0,
    HD_AUDIO_CODEC_AAC,
    HD_AUDIO_CODEC_LDAC,
    HD_AUDIO_CODEC_APTX,
    HD_AUDIO_CODEC_APTX_HD,
    HD_AUDIO_CODEC_LC3,
    HD_AUDIO_CODEC_LC3_PLUS,
    HD_AUDIO_CODEC_OPUS,
    HD_AUDIO_CODEC_MAX
} hd_audio_codec_t;

//
// Bluetooth Audio Quality Levels
//
typedef enum {
    HD_AUDIO_QUALITY_STANDARD = 0,
    HD_AUDIO_QUALITY_HIGH,
    HD_AUDIO_QUALITY_HD,
    HD_AUDIO_QUALITY_ULTRA_HD,
    HD_AUDIO_QUALITY_MAX
} hd_audio_quality_t;

//
// Bluetooth 5.2 Spectrum Configuration
//
typedef enum {
    HD_AUDIO_SPECTRUM_AUTO = 0,
    HD_AUDIO_SPECTRUM_NARROW,
    HD_AUDIO_SPECTRUM_WIDE,
    HD_AUDIO_SPECTRUM_ULTRA_WIDE,
    HD_AUDIO_SPECTRUM_ADAPTIVE,
    HD_AUDIO_SPECTRUM_MAX
} hd_audio_spectrum_t;

//
// Lag Correction Modes
//
typedef enum {
    HD_AUDIO_LAG_CORRECTION_OFF = 0,
    HD_AUDIO_LAG_CORRECTION_CONSERVATIVE,
    HD_AUDIO_LAG_CORRECTION_AGGRESSIVE,
    HD_AUDIO_LAG_CORRECTION_ADAPTIVE,
    HD_AUDIO_LAG_CORRECTION_MAX
} hd_audio_lag_correction_t;

//
// HD Audio Bluetooth Configuration
//
typedef struct _HD_AUDIO_BLUETOOTH_CONFIG {
    hd_audio_codec_t Codec;
    hd_audio_quality_t Quality;
    hd_audio_spectrum_t Spectrum;
    hd_audio_lag_correction_t LagCorrection;
    ULONG SampleRate;
    ULONG Channels;
    ULONG BitDepth;
    ULONG Bitrate;
    BOOLEAN EnableHD;
    BOOLEAN Enable5_2;
    BOOLEAN EnableLEAudio;
    BOOLEAN EnableStereo;
    FLOAT LatencyTarget;
    FLOAT BufferSize;
} HD_AUDIO_BLUETOOTH_CONFIG, *PHD_AUDIO_BLUETOOTH_CONFIG;

//
// HD Audio Bluetooth Status
//
typedef struct _HD_AUDIO_BLUETOOTH_STATUS {
    BOOLEAN Connected;
    BOOLEAN HDActive;
    BOOLEAN LEAudioActive;
    BOOLEAN LagCorrectionActive;
    ULONG CurrentSampleRate;
    ULONG CurrentChannels;
    ULONG CurrentBitrate;
    FLOAT CurrentLatency;
    FLOAT SignalStrength;
    ULONG PacketLoss;
    ULONG Retransmissions;
    ULONG BufferUnderruns;
    ULONG BufferOverruns;
    hd_audio_codec_t ActiveCodec;
    hd_audio_quality_t ActiveQuality;
    hd_audio_spectrum_t ActiveSpectrum;
} HD_AUDIO_BLUETOOTH_STATUS, *PHD_AUDIO_BLUETOOTH_STATUS;

//
// Bluetooth 5.2 Spectrum Parameters
//
typedef struct _HD_AUDIO_BLUETOOTH_SPECTRUM_PARAMS {
    hd_audio_spectrum_t SpectrumMode;
    ULONG CenterFrequency;
    ULONG Bandwidth;
    ULONG ChannelSpacing;
    ULONG PowerLevel;
    BOOLEAN EnableAdaptive;
    BOOLEAN EnableInterferenceDetection;
    BOOLEAN EnableFrequencyHopping;
    ULONG HopInterval;
    ULONG HopSequence;
} HD_AUDIO_BLUETOOTH_SPECTRUM_PARAMS, *PHD_AUDIO_BLUETOOTH_SPECTRUM_PARAMS;

//
// Lag Correction Parameters
//
typedef struct _HD_AUDIO_LAG_CORRECTION_PARAMS {
    hd_audio_lag_correction_t Mode;
    ULONG TargetLatencyMs;
    ULONG BufferSize;
    ULONG CorrectionThreshold;
    ULONG MaxCorrection;
    BOOLEAN EnableAdaptive;
    BOOLEAN EnablePrediction;
    BOOLEAN EnableJitterBuffer;
    FLOAT JitterBufferSize;
} HD_AUDIO_LUETOOTH_LAG_CORRECTION_PARAMS, *PHD_AUDIO_LUETOOTH_LAG_CORRECTION_PARAMS;

//
// HD Audio Bluetooth Device Context
//
typedef struct _HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT {
    HD_AUDIO_BLUETOOTH_CONFIG Config;
    HD_AUDIO_BLUETOOTH_STATUS Status;
    HD_AUDIO_BLUETOOTH_SPECTRUM_PARAMS SpectrumParams;
    HD_AUDIO_LUETOOTH_LAG_CORRECTION_PARAMS LagParams;
    
    // ACX objects
    ACXCIRCUIT RenderCircuit;
    ACXCIRCUIT CaptureCircuit;
    ACXELEMENT CodecElement;
    ACXELEMENT QualityElement;
    ACXELEMENT SpectrumElement;
    ACXELEMENT LagElement;
    
    // Buffers
    PVOID AudioBuffer;
    ULONG AudioBufferSize;
    PVOID LagBuffer;
    ULONG LagBufferSize;
    PVOID SpectrumBuffer;
    ULONG SpectrumBufferSize;
    
    // Synchronization
    WDFSPINLOCK ConfigLock;
    WDFSPINLOCK StatusLock;
    WDFSPINLOCK BufferLock;
    
    // Timers
    WDFTIMER LagTimer;
    WDFTIMER SpectrumTimer;
    WDFTIMER StatusTimer;
    
    // Bluetooth handles
    HANDLE BluetoothHandle;
    HANDLE LEAudioHandle;
    
    // Performance counters
    ULONG64 PacketsProcessed;
    ULONG64 BytesProcessed;
    ULONG64 LagCorrections;
    ULONG64 SpectrumAdjustments;
    ULONG64 QualityChanges;
    
    // Flags
    BOOLEAN Initialized;
    BOOLEAN HDActive;
    BOOLEAN LEAudioActive;
    BOOLEAN LagCorrectionEnabled;
    BOOLEAN SpectrumOptimizationEnabled;
} HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT, *PHD_AUDIO_BLUETOOTH_DEVICE_CONTEXT;

//
// HD Audio Bluetooth Circuit Context
//
typedef struct _HD_AUDIO_BLUETOOTH_CIRCUIT_CONTEXT {
    HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT* DeviceContext;
    BOOLEAN IsRender;
    BOOLEAN IsHD;
    BOOLEAN IsLEAudio;
    hd_audio_codec_t CurrentCodec;
    ULONG CurrentSampleRate;
    ULONG CurrentChannels;
} HD_AUDIO_BLUETOOTH_CIRCUIT_CONTEXT, *PHD_AUDIO_BLUETOOTH_CIRCUIT_CONTEXT;

//
// HD Audio Bluetooth Stream Context
//
typedef struct _HD_AUDIO_BLUETOOTH_STREAM_CONTEXT {
    HD_AUDIO_BLUETOOTH_CIRCUIT_CONTEXT* CircuitContext;
    BOOLEAN LagCorrectionEnabled;
    BOOLEAN SpectrumOptimizationEnabled;
    PVOID StreamBuffer;
    ULONG StreamBufferSize;
    ULONG64 PacketsProcessed;
    FLOAT AverageLatency;
    ULONG BufferUnderruns;
    ULONG BufferOverruns;
} HD_AUDIO_BLUETOOTH_STREAM_CONTEXT, *PHD_AUDIO_BLUETOOTH_STREAM_CONTEXT;

//
// Function Prototypes
//

NTSTATUS
HdAudioBluetoothDeviceAdd(
    _In_ WDFDRIVER Driver,
    _Inout_ PWDFDEVICE_INIT DeviceInit
    );

NTSTATUS
HdAudioBluetoothEvtDevicePrepareHardware(
    _In_ WDFDEVICE Device,
    _In_ WDFCMRESLIST ResourcesRaw,
    _In_ WDFCMRESLIST ResourcesTranslated
    );

NTSTATUS
HdAudioBluetoothEvtDeviceReleaseHardware(
    _In_ WDFDEVICE Device,
    _In_ WDFCMRESLIST ResourcesTranslated
    );

NTSTATUS
HdAudioBluetoothEvtDeviceD0Entry(
    _In_ WDFDEVICE Device,
    _In_ WDF_POWER_DEVICE_STATE PreviousState
    );

NTSTATUS
HdAudioBluetoothEvtDeviceD0Exit(
    _In_ WDFDEVICE Device,
    _In_ WDF_POWER_DEVICE_STATE TargetState
    );

VOID
HdAudioBluetoothEvtIoDeviceControl(
    _In_ WDFQUEUE Queue,
    _In_ WDFREQUEST Request,
    _In_ size_t OutputBufferLength,
    _In_ size_t InputBufferLength,
    _In_ ULONG IoControlCode
    );

//
// HD Audio Configuration Functions
//

NTSTATUS
HdAudioBluetoothSetConfig(
    _In_ WDFDEVICE Device,
    _In_ PHD_AUDIO_BLUETOOTH_CONFIG Config
    );

NTSTATUS
HdAudioBluetoothGetConfig(
    _In_ WDFDEVICE Device,
    _Out_ PHD_AUDIO_BLUETOOTH_CONFIG Config
    );

NTSTATUS
HdAudioBluetoothSetCodec(
    _In_ WDFDEVICE Device,
    _In_ hd_audio_codec_t Codec
    );

NTSTATUS
HdAudioBluetoothSetQuality(
    _In_ WDFDEVICE Device,
    _In_ hd_audio_quality_t Quality
    );

NTSTATUS
HdAudioBluetoothSetSpectrum(
    _In_ WDFDEVICE Device,
    _In_ PHD_AUDIO_BLUETOOTH_SPECTRUM_PARAMS SpectrumParams
    );

NTSTATUS
HdAudioBluetoothSetLagCorrection(
    _In_ WDFDEVICE Device,
    _In_ PHD_AUDIO_LUETOOTH_LAG_CORRECTION_PARAMS LagParams
    );

//
// HD Audio Status Functions
//

NTSTATUS
HdAudioBluetoothGetStatus(
    _In_ WDFDEVICE Device,
    _Out_ PHD_AUDIO_BLUETOOTH_STATUS Status
    );

NTSTATUS
HdAudioBluetoothGetConnectionStatus(
    _In_ WDFDEVICE Device,
    _Out_ PBOOLEAN Connected,
    _Out_ PBOOLEAN HDActive,
    _Out_ PBOOLEAN LEAudioActive
    );

//
// HD Audio Processing Functions
//

NTSTATUS
HdAudioBluetoothProcessAudio(
    _In_ HD_AUDIO_BLUETOOTH_STREAM_CONTEXT* StreamContext,
    _In_ PVOID InputBuffer,
    _In_ ULONG InputSize,
    _Out_ PVOID OutputBuffer,
    _Out_ PULONG OutputSize
    );

NTSTATUS
HdAudioBluetoothApplyLagCorrection(
    _In_ HD_AUDIO_BLUETOOTH_STREAM_CONTEXT* StreamContext,
    _In_ PVOID AudioBuffer,
    _In_ ULONG BufferSize
    );

NTSTATUS
HdAudioBluetoothOptimizeSpectrum(
    _In_ HD_AUDIO_BLUETOOTH_STREAM_CONTEXT* StreamContext,
    _In_ PVOID AudioBuffer,
    _In_ ULONG BufferSize
    );

//
// HD Audio ACX Functions
//

NTSTATUS
HdAudioBluetoothCircuitCreate(
    _In_ WDFDEVICE Device,
    _In_ ACXCIRCUIT Circuit,
    _In_ PACXCIRCUIT_INIT CircuitInit
    );

NTSTATUS
HdAudioBluetoothElementCreate(
    _In_ ACXCIRCUIT Circuit,
    _In_ ACXELEMENT Element,
    _In_ PACXELEMENT_INIT ElementInit
    );

NTSTATUS
HdAudioBluetoothStreamCreate(
    _In_ ACXCIRCUIT Circuit,
    _In_ ACXSTREAM Stream,
    _In_ PACXSTREAM_INIT StreamInit
    );

//
// HD Audio Property Handlers
//

NTSTATUS
HdAudioBluetoothPropertyCodec(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
HdAudioBluetoothPropertyQuality(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
HdAudioBluetoothPropertySpectrum(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
HdAudioBluetoothPropertyLagCorrection(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
HdAudioBluetoothPropertyStatus(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

//
// HD Audio Timer Functions
//

EVT_WDF_TIMER HdAudioBluetoothLagTimerFunction;
EVT_WDF_TIMER HdAudioBluetoothSpectrumTimerFunction;
EVT_WDF_TIMER HdAudioBluetoothStatusTimerFunction;

//
// HD Audio Helper Functions
//

NTSTATUS
HdAudioBluetoothInitializeDevice(
    _In_ HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT* DeviceContext
    );

NTSTATUS
HdAudioBluetoothConnectBluetooth(
    _In_ HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT* DeviceContext
    );

NTSTATUS
HdAudioBluetoothDisconnectBluetooth(
    _In_ HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT* DeviceContext
    );

NTSTATUS
HdAudioBluetoothNegotiateCodec(
    _In_ HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT* DeviceContext,
    _In_ hd_audio_codec_t PreferredCodec
    );

NTSTATUS
HdAudioBluetoothOptimizeFor5_2(
    _In_ HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT* DeviceContext
    );

//
// Context Type Definitions
//

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(HD_AUDIO_BLUETOOTH_DEVICE_CONTEXT, HdAudioBluetoothGetDeviceContext)
WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(HD_AUDIO_BLUETOOTH_CIRCUIT_CONTEXT, HdAudioBluetoothGetCircuitContext)
WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(HD_AUDIO_BLUETOOTH_STREAM_CONTEXT, HdAudioBluetoothGetStreamContext)

//
// Constants
//

#define HD_AUDIO_BLUETOOTH_MAX_SAMPLE_RATE 192000
#define HD_AUDIO_BLUETOOTH_MIN_SAMPLE_RATE 8000
#define HD_AUDIO_BLUETOOTH_MAX_CHANNELS 8
#define HD_AUDIO_BLUETOOTH_MIN_CHANNELS 1
#define HD_AUDIO_BLUETOOTH_MAX_BITRATE 1500000  // 1.5 Mbps for LDAC
#define HD_AUDIO_BLUETOOTH_MIN_BITRATE 32000    // 32 kbps for SBC
#define HD_AUDIO_BLUETOOTH_DEFAULT_LATENCY 40.0f  // 40ms default latency
#define HD_AUDIO_BLUETOOTH_MIN_LATENCY 10.0f     // 10ms minimum latency
#define HD_AUDIO_BLUETOOTH_MAX_LATENCY 200.0f    // 200ms maximum latency

#define HD_AUDIO_BLUETOOTH_BUFFER_SIZE 8192
#define HD_AUDIO_BLUETOOTH_LAG_BUFFER_SIZE 4096
#define HD_AUDIO_BLUETOOTH_SPECTRUM_BUFFER_SIZE 2048

#define HD_AUDIO_BLUETOOTH_TIMER_INTERVAL_MS 100  // 100ms timer interval
#define HD_AUDIO_BLUETOOTH_LAG_CORRECTION_INTERVAL_MS 50  // 50ms lag correction
#define HD_AUDIO_BLUETOOTH_SPECTRUM_OPTIMIZATION_INTERVAL_MS 200  // 200ms spectrum optimization

//
// Property Identifiers
//

typedef enum {
    KSPROPERTY_HD_AUDIO_BLUETOOTH_CODEC = 0,
    KSPROPERTY_HD_AUDIO_BLUETOOTH_QUALITY,
    KSPROPERTY_HD_AUDIO_BLUETOOTH_SPECTRUM,
    KSPROPERTY_HD_AUDIO_BLUETOOTH_LAG_CORRECTION,
    KSPROPERTY_HD_AUDIO_BLUETOOTH_STATUS,
    KSPROPERTY_HD_AUDIO_BLUETOOTH_CONNECTION_STATUS,
    KSPROPERTY_HD_AUDIO_BLUETOOTH_MAX
} KSPROPERTY_HD_AUDIO_BLUETOOTH;

//
// Pin and Node GUIDs
//

#define PIN_HD_AUDIO_BLUETOOTH_RENDER \
    { \
        0x8F2A1B3C, 0x4D5E, 0x6F7A, 0x8B, 0x9C, 0xD0, 0xE1, 0xF2, 0xA3, 0xB4, 0xC6 \
    }

#define PIN_HD_AUDIO_BLUETOOTH_CAPTURE \
    { \
        0x8F2A1B3C, 0x4D5E, 0x6F7A, 0x8B, 0x9C, 0xD0, 0xE1, 0xF2, 0xA3, 0xB4, 0xC7 \
    }

#define NODE_HD_AUDIO_BLUETOOTH_CODEC \
    { \
        0x7A9B2C1D, 0x3E4F, 0x5A6B, 0x7C, 0x8D, 0x9E, 0xA0, 0xB1, 0xC2, 0xD3, 0xE5 \
    }

#define NODE_HD_AUDIO_BLUETOOTH_QUALITY \
    { \
        0x7A9B2C1D, 0x3E4F, 0x5A6B, 0x7C, 0x8D, 0x9E, 0xA0, 0xB1, 0xC2, 0xD3, 0xE6 \
    }

#define NODE_HD_AUDIO_BLUETOOTH_SPECTRUM \
    { \
        0x7A9B2C1D, 0x3E4F, 0x5A6B, 0x7C, 0x8D, 0x9E, 0xA0, 0xB1, 0xC2, 0xD3, 0xE7 \
    }

#define NODE_HD_AUDIO_BLUETOOTH_LAG_CORRECTION \
    { \
        0x7A9B2C1D, 0x3E4F, 0x5A6B, 0x7C, 0x8D, 0x9E, 0xA0, 0xB1, 0xC2, 0xD3, 0xE8 \
    }

#endif // HD_AUDIO_BLUETOOTH_H
