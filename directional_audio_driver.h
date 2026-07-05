/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#ifndef DIRECTIONAL_AUDIO_DRIVER_H
#define DIRECTIONAL_AUDIO_DRIVER_H

#include <ntddk.h>
#include <acx.h>
#include <ks.h>
#include <ksmedia.h>

//
// Directional Audio Control Device Interface GUID
//
DEFINE_GUID(GUID_DEVINTERFACE_DIRECTIONAL_AUDIO_CONTROL,
    0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf0);

//
// Directional Audio Property Set GUID
//
DEFINE_GUID(GUID_DIRECTIONAL_AUDIO_PROPERTY_SET,
    0x87654321, 0x4321, 0x8765, 0x43, 0x21, 0x87, 0x65, 0x43, 0x21, 0x87, 0x65);

//
// Directional Audio IOCTLs
//
#define IOCTL_DIRECTIONAL_AUDIO_SET_POSITION \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_DIRECTIONAL_AUDIO_GET_POSITION \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_DIRECTIONAL_AUDIO_SET_CONFIG \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_DIRECTIONAL_AUDIO_GET_CONFIG \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_DIRECTIONAL_AUDIO_ENABLE_PROCESSING \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_DIRECTIONAL_AUDIO_GET_STATUS \
    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x805, METHOD_BUFFERED, FILE_ANY_ACCESS)

//
// Directional Audio Property Identifiers
//
typedef enum {
    KSPROPERTY_DIRECTIONAL_AUDIO_POSITION = 0,
    KSPROPERTY_DIRECTIONAL_AUDIO_CONFIG,
    KSPROPERTY_DIRECTIONAL_AUDIO_ENABLE,
    KSPROPERTY_DIRECTIONAL_AUDIO_STATUS,
    KSPROPERTY_DIRECTIONAL_AUDIO_MAX
} KSPROPERTY_DIRECTIONAL_AUDIO;

//
// Directional Audio Data Structures
//

typedef struct _DIRECTIONAL_AUDIO_POSITION {
    FLOAT X;                    // X coordinate position
    FLOAT Y;                    // Y coordinate position
    FLOAT Z;                    // Z coordinate position (reserved for future 3D)
    BOOLEAN AvoidCenter;        // Enable center avoidance logic
    FLOAT Azimuth;              // Calculated azimuth angle (degrees)
    FLOAT Distance;             // Calculated distance
} DIRECTIONAL_AUDIO_POSITION, *PDIRECTIONAL_AUDIO_POSITION;

typedef struct _DIRECTIONAL_AUDIO_CONFIG {
    FLOAT MaxAzimuthDegrees;    // Maximum azimuth angle (default: 40.0)
    FLOAT AvoidanceAngleDegrees; // Avoidance angle from center (default: 20.0)
    FLOAT ReferenceDistance;    // Reference distance for attenuation
    BOOLEAN EnableHRTF;         // Enable HRTF processing
    BOOLEAN EnableAmbisonics;   // Enable ambisonics processing
    ULONG SampleRate;           // Audio sample rate
    ULONG Channels;             // Number of audio channels
} DIRECTIONAL_AUDIO_CONFIG, *PDIRECTIONAL_AUDIO_CONFIG;

typedef struct _DIRECTIONAL_AUDIO_STATUS {
    BOOLEAN ProcessingEnabled;  // Whether directional processing is active
    BOOLEAN DriverReady;        // Driver initialization status
    ULONG CurrentSampleRate;    // Current audio sample rate
    ULONG CurrentChannels;      // Current number of channels
    DIRECTIONAL_AUDIO_POSITION CurrentPosition; // Current audio position
    DIRECTIONAL_AUDIO_CONFIG CurrentConfig;     // Current configuration
} DIRECTIONAL_AUDIO_STATUS, *PDIRECTIONAL_AUDIO_STATUS;

typedef struct _DIRECTIONAL_AUDIO_ENABLE {
    BOOLEAN EnableProcessing;   // Enable/disable directional processing
    BOOLEAN EnableAvoidCenter;  // Enable/disable center avoidance
} DIRECTIONAL_AUDIO_ENABLE, *PDIRECTIONAL_AUDIO_ENABLE;

//
// ACX Circuit and Element Definitions
//

typedef enum {
    DIRECTIONAL_AUDIO_CIRCUIT_RENDER = 0,
    DIRECTIONAL_AUDIO_CIRCUIT_CAPTURE,
    DIRECTIONAL_AUDIO_CIRCUIT_MAX
} DIRECTIONAL_AUDIO_CIRCUIT_TYPE;

typedef enum {
    DIRECTIONAL_AUDIO_ELEMENT_POSITIONER = 0,
    DIRECTIONAL_AUDIO_ELEMENT_PROCESSOR,
    DIRECTIONAL_AUDIO_ELEMENT_MAX
} DIRECTIONAL_AUDIO_ELEMENT_TYPE;

//
// ACX Pin Properties
//
#define PIN_DIRECTIONAL_AUDIO_RENDER \
    { \
        0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf1 \
    }

#define PIN_DIRECTIONAL_AUDIO_CAPTURE \
    { \
        0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf2 \
    }

//
// ACX Node Types
//
#define NODE_DIRECTIONAL_AUDIO_POSITIONER \
    { \
        0x87654321, 0x4321, 0x8765, 0x43, 0x21, 0x87, 0x65, 0x43, 0x21, 0x87, 0x66 \
    }

#define NODE_DIRECTIONAL_AUDIO_PROCESSOR \
    { \
        0x87654321, 0x4321, 0x8765, 0x43, 0x21, 0x87, 0x65, 0x43, 0x21, 0x87, 0x67 \
    }

//
// Function Prototypes
//

NTSTATUS
DirectionalAudioDeviceAdd(
    _In_ WDFDRIVER Driver,
    _Inout_ PWDFDEVICE_INIT DeviceInit
    );

NTSTATUS
DirectionalAudioEvtDevicePrepareHardware(
    _In_ WDFDEVICE Device,
    _In_ WDFCMRESLIST ResourcesRaw,
    _In_ WDFCMRESLIST ResourcesTranslated
    );

NTSTATUS
DirectionalAudioEvtDeviceReleaseHardware(
    _In_ WDFDEVICE Device,
    _In_ WDFCMRESLIST ResourcesTranslated
    );

NTSTATUS
DirectionalAudioEvtDeviceD0Entry(
    _In_ WDFDEVICE Device,
    _In_ WDF_POWER_DEVICE_STATE PreviousState
    );

NTSTATUS
DirectionalAudioEvtDeviceD0Exit(
    _In_ WDFDEVICE Device,
    _In_ WDF_POWER_DEVICE_STATE TargetState
    );

VOID
DirectionalAudioEvtIoDeviceControl(
    _In_ WDFQUEUE Queue,
    _In_ WDFREQUEST Request,
    _In_ size_t OutputBufferLength,
    _In_ size_t InputBufferLength,
    _In_ ULONG IoControlCode
    );

NTSTATUS
DirectionalAudioSetPosition(
    _In_ WDFDEVICE Device,
    _In_ PDIRECTIONAL_AUDIO_POSITION Position
    );

NTSTATUS
DirectionalAudioGetPosition(
    _In_ WDFDEVICE Device,
    _Out_ PDIRECTIONAL_AUDIO_POSITION Position
    );

NTSTATUS
DirectionalAudioSetConfig(
    _In_ WDFDEVICE Device,
    _In_ PDIRECTIONAL_AUDIO_CONFIG Config
    );

NTSTATUS
DirectionalAudioGetConfig(
    _In_ WDFDEVICE Device,
    _Out_ PDIRECTIONAL_AUDIO_CONFIG Config
    );

NTSTATUS
DirectionalAudioEnableProcessing(
    _In_ WDFDEVICE Device,
    _In_ PDIRECTIONAL_AUDIO_ENABLE Enable
    );

NTSTATUS
DirectionalAudioGetStatus(
    _In_ WDFDEVICE Device,
    _Out_ PDIRECTIONAL_AUDIO_STATUS Status
    );

//
// ACX Circuit Callbacks
//

NTSTATUS
DirectionalAudioCircuitCreate(
    _In_ WDFDEVICE Device,
    _In_ ACXCIRCUIT Circuit,
    _In_ PACXCIRCUIT_INIT CircuitInit
    );

NTSTATUS
DirectionalAudioElementCreate(
    _In_ ACXCIRCUIT Circuit,
    _In_ ACXELEMENT Element,
    _In_ PACXELEMENT_INIT ElementInit
    );

NTSTATUS
DirectionalAudioStreamCreate(
    _In_ ACXCIRCUIT Circuit,
    _In_ ACXSTREAM Stream,
    _In_ PACXSTREAM_INIT StreamInit
    );

//
// Property Handlers
//

NTSTATUS
DirectionalAudioPropertyPosition(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
DirectionalAudioPropertyConfig(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
DirectionalAudioPropertyEnable(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

NTSTATUS
DirectionalAudioPropertyStatus(
    _In_ ACXELEMENT Element,
    _In_ PKSPROPERTY Property,
    _In_ PVOID Value,
    _In_ ULONG ValueLength,
    _Inout_ PULONG BytesReturned
    );

//
// Context Structures
//

typedef struct _DIRECTIONAL_AUDIO_DEVICE_CONTEXT {
    BOOLEAN ProcessingEnabled;
    BOOLEAN AvoidCenterEnabled;
    DIRECTIONAL_AUDIO_POSITION CurrentPosition;
    DIRECTIONAL_AUDIO_CONFIG CurrentConfig;
    WDFSPINLOCK PositionLock;
    WDFSPINLOCK ConfigLock;
    ACXCIRCUIT RenderCircuit;
    ACXCIRCUIT CaptureCircuit;
} DIRECTIONAL_AUDIO_DEVICE_CONTEXT, *PDIRECTIONAL_AUDIO_DEVICE_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DIRECTIONAL_AUDIO_DEVICE_CONTEXT, DirectionalAudioGetDeviceContext)

typedef struct _DIRECTIONAL_AUDIO_CIRCUIT_CONTEXT {
    DIRECTIONAL_AUDIO_CIRCUIT_TYPE CircuitType;
    ACXELEMENT PositionerElement;
    ACXELEMENT ProcessorElement;
} DIRECTIONAL_AUDIO_CIRCUIT_CONTEXT, *PDIRECTIONAL_AUDIO_CIRCUIT_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DIRECTIONAL_AUDIO_CIRCUIT_CONTEXT, DirectionalAudioGetCircuitContext)

typedef struct _DIRECTIONAL_AUDIO_STREAM_CONTEXT {
    BOOLEAN DirectionalProcessingEnabled;
    DIRECTIONAL_AUDIO_POSITION StreamPosition;
} DIRECTIONAL_AUDIO_STREAM_CONTEXT, *PDIRECTIONAL_AUDIO_STREAM_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DIRECTIONAL_AUDIO_STREAM_CONTEXT, DirectionalAudioGetStreamContext)

//
// Constants
//
#define DIRECTIONAL_AUDIO_MAX_CHANNELS 8
#define DIRECTIONAL_AUDIO_MIN_SAMPLE_RATE 8000
#define DIRECTIONAL_AUDIO_MAX_SAMPLE_RATE 192000
#define DIRECTIONAL_AUDIO_DEFAULT_SAMPLE_RATE 16000
#define DIRECTIONAL_AUDIO_DEFAULT_CHANNELS 2

#endif // DIRECTIONAL_AUDIO_DRIVER_H
