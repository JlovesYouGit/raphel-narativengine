/* SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved. */
/* SPDX-License-Identifier: MIT */

#include "directional_audio_driver.h"
#include <initguid.h>

//
// Driver Entry Point
//
NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
    )
{
    WDF_DRIVER_CONFIG config;
    NTSTATUS status;

    DbgPrint("Directional Audio Driver: DriverEntry called\n");

    //
    // Initialize driver config
    //
    WDF_DRIVER_CONFIG_INIT(&config, DirectionalAudioDeviceAdd);

    //
    // Create a WDF driver object
    //
    status = WdfDriverCreate(
        DriverObject,
        RegistryPath,
        WDF_NO_OBJECT_ATTRIBUTES,
        &config,
        WDF_NO_HANDLE
    );

    if (!NT_SUCCESS(status)) {
        DbgPrint("Directional Audio Driver: WdfDriverCreate failed, status=0x%x\n", status);
        return status;
    }

    DbgPrint("Directional Audio Driver: DriverEntry completed successfully\n");
    return status;
}

//
// Device Add Callback
//
NTSTATUS
DirectionalAudioDeviceAdd(
    _In_ WDFDRIVER Driver,
    _Inout_ PWDFDEVICE_INIT DeviceInit
    )
{
    UNREFERENCED_PARAMETER(Driver);
    
    WDFDEVICE device;
    WDF_OBJECT_ATTRIBUTES deviceAttributes;
    DIRECTIONAL_AUDIO_DEVICE_CONTEXT* deviceContext;
    NTSTATUS status;

    DbgPrint("Directional Audio Driver: DirectionalAudioDeviceAdd called\n");

    //
    // Set device properties
    //
    WdfDeviceInitSetDeviceType(DeviceInit, FILE_DEVICE_SOUND);
    WdfDeviceInitSetExclusive(DeviceInit, FALSE);

    //
    // Initialize device attributes
    //
    WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&deviceAttributes, DIRECTIONAL_AUDIO_DEVICE_CONTEXT);

    //
    // Create device
    //
    status = WdfDeviceCreate(&DeviceInit, &deviceAttributes, &device);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Directional Audio Driver: WdfDeviceCreate failed, status=0x%x\n", status);
        return status;
    }

    //
    // Initialize device context
    //
    deviceContext = DirectionalAudioGetDeviceContext(device);
    RtlZeroMemory(deviceContext, sizeof(DIRECTIONAL_AUDIO_DEVICE_CONTEXT));

    //
    // Initialize default configuration
    //
    deviceContext->ProcessingEnabled = TRUE;
    deviceContext->AvoidCenterEnabled = TRUE;
    deviceContext->CurrentPosition.X = 0.0f;
    deviceContext->CurrentPosition.Y = 0.0f;
    deviceContext->CurrentPosition.Z = 0.0f;
    deviceContext->CurrentPosition.AvoidCenter = TRUE;
    deviceContext->CurrentPosition.Azimuth = 0.0f;
    deviceContext->CurrentPosition.Distance = 1.0f;

    deviceContext->CurrentConfig.MaxAzimuthDegrees = 40.0f;
    deviceContext->CurrentConfig.AvoidanceAngleDegrees = 20.0f;
    deviceContext->CurrentConfig.ReferenceDistance = 1.0f;
    deviceContext->CurrentConfig.EnableHRTF = TRUE;
    deviceContext->CurrentConfig.EnableAmbisonics = FALSE;
    deviceContext->CurrentConfig.SampleRate = DIRECTIONAL_AUDIO_DEFAULT_SAMPLE_RATE;
    deviceContext->CurrentConfig.Channels = DIRECTIONAL_AUDIO_DEFAULT_CHANNELS;

    //
    // Create spin locks
    //
    WDF_OBJECT_ATTRIBUTES spinLockAttributes;
    WDF_OBJECT_ATTRIBUTES_INIT(&spinLockAttributes);
    spinLockAttributes.ParentObject = device;

    status = WdfSpinLockCreate(&spinLockAttributes, &deviceContext->PositionLock);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Directional Audio Driver: WdfSpinLockCreate (PositionLock) failed, status=0x%x\n", status);
        return status;
    }

    status = WdfSpinLockCreate(&spinLockAttributes, &deviceContext->ConfigLock);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Directional Audio Driver: WdfSpinLockCreate (ConfigLock) failed, status=0x%x\n", status);
        return status;
    }

    //
    // Set up device callbacks
    //
    WDF_PNPPOWER_EVENT_CALLBACKS pnpPowerCallbacks;
    WDF_PNPPOWER_EVENT_CALLBACKS_INIT(&pnpPowerCallbacks);
    pnpPowerCallbacks.EvtDevicePrepareHardware = DirectionalAudioEvtDevicePrepareHardware;
    pnpPowerCallbacks.EvtDeviceReleaseHardware = DirectionalAudioEvtDeviceReleaseHardware;
    pnpPowerCallbacks.EvtDeviceD0Entry = DirectionalAudioEvtDeviceD0Entry;
    pnpPowerCallbacks.EvtDeviceD0Exit = DirectionalAudioEvtDeviceD0Exit;

    WdfDeviceSetPnpPowerEventCallbacks(device, &pnpPowerCallbacks);

    //
    // Create I/O queue for device control
    //
    WDF_IO_QUEUE_CONFIG queueConfig;
    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&queueConfig, WdfIoQueueDispatchParallel);
    queueConfig.EvtIoDeviceControl = DirectionalAudioEvtIoDeviceControl;

    status = WdfIoQueueCreate(device, &queueConfig, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
    if (!NT_SUCCESS(status)) {
        DbgPrint("Directional Audio Driver: WdfIoQueueCreate failed, status=0x%x\n", status);
        return status;
    }

    //
    // Register device interface
    //
    status = WdfDeviceCreateDeviceInterface(
        device,
        &GUID_DEVINTERFACE_DIRECTIONAL_AUDIO_CONTROL,
        NULL
    );
    if (!NT_SUCCESS(status)) {
        DbgPrint("Directional Audio Driver: WdfDeviceCreateDeviceInterface failed, status=0x%x\n", status);
        return status;
    }

    DbgPrint("Directional Audio Driver: DirectionalAudioDeviceAdd completed successfully\n");
    return status;
}

//
// Prepare Hardware Callback
//
NTSTATUS
DirectionalAudioEvtDevicePrepareHardware(
    _In_ WDFDEVICE Device,
    _In_ WDFCMRESLIST ResourcesRaw,
    _In_ WDFCMRESLIST ResourcesTranslated
    )
{
    UNREFERENCED_PARAMETER(Device);
    UNREFERENCED_PARAMETER(ResourcesRaw);
    UNREFERENCED_PARAMETER(ResourcesTranslated);

    DbgPrint("Directional Audio Driver: DirectionalAudioEvtDevicePrepareHardware called\n");

    //
    // Initialize ACX circuits and elements here
    //
    // This would involve creating ACX circuits for render and capture,
    // along with the directional audio processing elements

    return STATUS_SUCCESS;
}

//
// Release Hardware Callback
//
NTSTATUS
DirectionalAudioEvtDeviceReleaseHardware(
    _In_ WDFDEVICE Device,
    _In_ WDFCMRESLIST ResourcesTranslated
    )
{
    UNREFERENCED_PARAMETER(Device);
    UNREFERENCED_PARAMETER(ResourcesTranslated);

    DbgPrint("Directional Audio Driver: DirectionalAudioEvtDeviceReleaseHardware called\n");

    return STATUS_SUCCESS;
}

//
// D0 Entry Callback
//
NTSTATUS
DirectionalAudioEvtDeviceD0Entry(
    _In_ WDFDEVICE Device,
    _In_ WDF_POWER_DEVICE_STATE PreviousState
    )
{
    UNREFERENCED_PARAMETER(Device);
    UNREFERENCED_PARAMETER(PreviousState);

    DbgPrint("Directional Audio Driver: DirectionalAudioEvtDeviceD0Entry called\n");

    return STATUS_SUCCESS;
}

//
// D0 Exit Callback
//
NTSTATUS
DirectionalAudioEvtDeviceD0Exit(
    _In_ WDFDEVICE Device,
    _In_ WDF_POWER_DEVICE_STATE TargetState
    )
{
    UNREFERENCED_PARAMETER(Device);
    UNREFERENCED_PARAMETER(TargetState);

    DbgPrint("Directional Audio Driver: DirectionalAudioEvtDeviceD0Exit called\n");

    return STATUS_SUCCESS;
}

//
// I/O Control Handler
//
VOID
DirectionalAudioEvtIoDeviceControl(
    _In_ WDFQUEUE Queue,
    _In_ WDFREQUEST Request,
    _In_ size_t OutputBufferLength,
    _In_ size_t InputBufferLength,
    _In_ ULONG IoControlCode
    )
{
    UNREFERENCED_PARAMETER(Queue);
    UNREFERENCED_PARAMETER(OutputBufferLength);
    UNREFERENCED_PARAMETER(InputBufferLength);

    NTSTATUS status = STATUS_SUCCESS;
    size_t bytesReturned = 0;
    WDFDEVICE device;
    PVOID inputBuffer = NULL;
    PVOID outputBuffer = NULL;

    device = WdfIoQueueGetDevice(Queue);

    DbgPrint("Directional Audio Driver: DirectionalAudioEvtIoDeviceControl called, IOCTL=0x%x\n", IoControlCode);

    switch (IoControlCode) {
    case IOCTL_DIRECTIONAL_AUDIO_SET_POSITION:
        status = WdfRequestRetrieveInputBuffer(Request, sizeof(DIRECTIONAL_AUDIO_POSITION), &inputBuffer, NULL);
        if (NT_SUCCESS(status)) {
            status = DirectionalAudioSetPosition(device, (PDIRECTIONAL_AUDIO_POSITION)inputBuffer);
        }
        break;

    case IOCTL_DIRECTIONAL_AUDIO_GET_POSITION:
        status = WdfRequestRetrieveOutputBuffer(Request, sizeof(DIRECTIONAL_AUDIO_POSITION), &outputBuffer, &bytesReturned);
        if (NT_SUCCESS(status)) {
            status = DirectionalAudioGetPosition(device, (PDIRECTIONAL_AUDIO_POSITION)outputBuffer);
            if (NT_SUCCESS(status)) {
                bytesReturned = sizeof(DIRECTIONAL_AUDIO_POSITION);
            }
        }
        break;

    case IOCTL_DIRECTIONAL_AUDIO_SET_CONFIG:
        status = WdfRequestRetrieveInputBuffer(Request, sizeof(DIRECTIONAL_AUDIO_CONFIG), &inputBuffer, NULL);
        if (NT_SUCCESS(status)) {
            status = DirectionalAudioSetConfig(device, (PDIRECTIONAL_AUDIO_CONFIG)inputBuffer);
        }
        break;

    case IOCTL_DIRECTIONAL_AUDIO_GET_CONFIG:
        status = WdfRequestRetrieveOutputBuffer(Request, sizeof(DIRECTIONAL_AUDIO_CONFIG), &outputBuffer, &bytesReturned);
        if (NT_SUCCESS(status)) {
            status = DirectionalAudioGetConfig(device, (PDIRECTIONAL_AUDIO_CONFIG)outputBuffer);
            if (NT_SUCCESS(status)) {
                bytesReturned = sizeof(DIRECTIONAL_AUDIO_CONFIG);
            }
        }
        break;

    case IOCTL_DIRECTIONAL_AUDIO_ENABLE_PROCESSING:
        status = WdfRequestRetrieveInputBuffer(Request, sizeof(DIRECTIONAL_AUDIO_ENABLE), &inputBuffer, NULL);
        if (NT_SUCCESS(status)) {
            status = DirectionalAudioEnableProcessing(device, (PDIRECTIONAL_AUDIO_ENABLE)inputBuffer);
        }
        break;

    case IOCTL_DIRECTIONAL_AUDIO_GET_STATUS:
        status = WdfRequestRetrieveOutputBuffer(Request, sizeof(DIRECTIONAL_AUDIO_STATUS), &outputBuffer, &bytesReturned);
        if (NT_SUCCESS(status)) {
            status = DirectionalAudioGetStatus(device, (PDIRECTIONAL_AUDIO_STATUS)outputBuffer);
            if (NT_SUCCESS(status)) {
                bytesReturned = sizeof(DIRECTIONAL_AUDIO_STATUS);
            }
        }
        break;

    default:
        status = STATUS_INVALID_DEVICE_REQUEST;
        break;
    }

    WdfRequestCompleteWithInformation(Request, status, bytesReturned);
}

//
// Position Control Functions
//
NTSTATUS
DirectionalAudioSetPosition(
    _In_ WDFDEVICE Device,
    _In_ PDIRECTIONAL_AUDIO_POSITION Position
    )
{
    PDIRECTIONAL_AUDIO_DEVICE_CONTEXT deviceContext;
    FLOAT azimuth, distance;

    deviceContext = DirectionalAudioGetDeviceContext(Device);

    DbgPrint("Directional Audio Driver: Setting position to X=%.2f, Y=%.2f, Z=%.2f\n",
             Position->X, Position->Y, Position->Z);

    //
    // Calculate azimuth and distance based on directional logic
    //
    if (Position->X == 0.0f && Position->Y == 0.0f) {
        azimuth = 0.0f;
    } else {
        azimuth = (FLOAT)(atan2(Position->Y, Position->X) * 180.0 / M_PI);
    }

    //
    // Apply 40-degree constraint from X axis
    //
    if (azimuth > deviceContext->CurrentConfig.MaxAzimuthDegrees) {
        azimuth = deviceContext->CurrentConfig.MaxAzimuthDegrees;
    } else if (azimuth < -deviceContext->CurrentConfig.MaxAzimuthDegrees) {
        azimuth = -deviceContext->CurrentConfig.MaxAzimuthDegrees;
    }

    //
    // Apply avoidance logic - avoid Y point by 20 degrees inward center
    //
    if (Position->AvoidCenter && fabs(Position->Y) > 0.1f) {
        FLOAT avoidance = (Position->Y > 0.0f ? 1.0f : -1.0f) * deviceContext->CurrentConfig.AvoidanceAngleDegrees;
        azimuth -= avoidance;

        // Re-apply constraints after avoidance
        if (azimuth > deviceContext->CurrentConfig.MaxAzimuthDegrees) {
            azimuth = deviceContext->CurrentConfig.MaxAzimuthDegrees;
        } else if (azimuth < -deviceContext->CurrentConfig.MaxAzimuthDegrees) {
            azimuth = -deviceContext->CurrentConfig.MaxAzimuthDegrees;
        }
    }

    //
    // Calculate distance for volume attenuation
    //
    distance = (FLOAT)sqrt(Position->X * Position->X + Position->Y * Position->Y + Position->Z * Position->Z);

    //
    // Update device context under lock
    //
    WdfSpinLockAcquire(deviceContext->PositionLock);
    deviceContext->CurrentPosition.X = Position->X;
    deviceContext->CurrentPosition.Y = Position->Y;
    deviceContext->CurrentPosition.Z = Position->Z;
    deviceContext->CurrentPosition.AvoidCenter = Position->AvoidCenter;
    deviceContext->CurrentPosition.Azimuth = azimuth;
    deviceContext->CurrentPosition.Distance = distance;
    WdfSpinLockRelease(deviceContext->PositionLock);

    DbgPrint("Directional Audio Driver: Position set - Azimuth=%.1f°, Distance=%.2f\n", azimuth, distance);

    return STATUS_SUCCESS;
}

NTSTATUS
DirectionalAudioGetPosition(
    _In_ WDFDEVICE Device,
    _Out_ PDIRECTIONAL_AUDIO_POSITION Position
    )
{
    PDIRECTIONAL_AUDIO_DEVICE_CONTEXT deviceContext;

    deviceContext = DirectionalAudioGetDeviceContext(Device);

    WdfSpinLockAcquire(deviceContext->PositionLock);
    *Position = deviceContext->CurrentPosition;
    WdfSpinLockRelease(deviceContext->PositionLock);

    return STATUS_SUCCESS;
}

//
// Configuration Functions
//
NTSTATUS
DirectionalAudioSetConfig(
    _In_ WDFDEVICE Device,
    _In_ PDIRECTIONAL_AUDIO_CONFIG Config
    )
{
    PDIRECTIONAL_AUDIO_DEVICE_CONTEXT deviceContext;

    deviceContext = DirectionalAudioGetDeviceContext(Device);

    DbgPrint("Directional Audio Driver: Setting configuration\n");

    WdfSpinLockAcquire(deviceContext->ConfigLock);
    deviceContext->CurrentConfig = *Config;
    WdfSpinLockRelease(deviceContext->ConfigLock);

    return STATUS_SUCCESS;
}

NTSTATUS
DirectionalAudioGetConfig(
    _In_ WDFDEVICE Device,
    _Out_ PDIRECTIONAL_AUDIO_CONFIG Config
    )
{
    PDIRECTIONAL_AUDIO_DEVICE_CONTEXT deviceContext;

    deviceContext = DirectionalAudioGetDeviceContext(Device);

    WdfSpinLockAcquire(deviceContext->ConfigLock);
    *Config = deviceContext->CurrentConfig;
    WdfSpinLockRelease(deviceContext->ConfigLock);

    return STATUS_SUCCESS;
}

//
// Enable/Disable Functions
//
NTSTATUS
DirectionalAudioEnableProcessing(
    _In_ WDFDEVICE Device,
    _In_ PDIRECTIONAL_AUDIO_ENABLE Enable
    )
{
    PDIRECTIONAL_AUDIO_DEVICE_CONTEXT deviceContext;

    deviceContext = DirectionalAudioGetDeviceContext(Device);

    DbgPrint("Directional Audio Driver: %s processing, %s center avoidance\n",
             Enable->EnableProcessing ? "Enabling" : "Disabling",
             Enable->EnableAvoidCenter ? "Enabling" : "Disabling");

    WdfSpinLockAcquire(deviceContext->PositionLock);
    deviceContext->ProcessingEnabled = Enable->EnableProcessing;
    deviceContext->AvoidCenterEnabled = Enable->EnableAvoidCenter;
    deviceContext->CurrentPosition.AvoidCenter = Enable->EnableAvoidCenter;
    WdfSpinLockRelease(deviceContext->PositionLock);

    return STATUS_SUCCESS;
}

//
// Status Function
//
NTSTATUS
DirectionalAudioGetStatus(
    _In_ WDFDEVICE Device,
    _Out_ PDIRECTIONAL_AUDIO_STATUS Status
    )
{
    PDIRECTIONAL_AUDIO_DEVICE_CONTEXT deviceContext;

    deviceContext = DirectionalAudioGetDeviceContext(Device);

    Status->ProcessingEnabled = deviceContext->ProcessingEnabled;
    Status->DriverReady = TRUE;

    WdfSpinLockAcquire(deviceContext->ConfigLock);
    Status->CurrentSampleRate = deviceContext->CurrentConfig.SampleRate;
    Status->CurrentChannels = deviceContext->CurrentConfig.Channels;
    Status->CurrentConfig = deviceContext->CurrentConfig;
    WdfSpinLockRelease(deviceContext->ConfigLock);

    WdfSpinLockAcquire(deviceContext->PositionLock);
    Status->CurrentPosition = deviceContext->CurrentPosition;
    WdfSpinLockRelease(deviceContext->PositionLock);

    return STATUS_SUCCESS;
}
