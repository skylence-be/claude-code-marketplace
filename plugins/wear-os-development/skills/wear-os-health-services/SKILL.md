---
name: wear-os-health-services
description: Wear OS Health Services for heart rate, sensors, exercise, and passive monitoring. Use when reading watch sensor data.
category: wear-os
tags: [wear-os, health-services, sensors, heart-rate, exercise, passive-monitoring]
related_skills: [wear-os-blueprint, wear-os-tiles-complications, wear-os-data-and-security]
---

# Wear OS Health Services

Use **Health Services** (`androidx.health:health-services-client`) instead of raw
`SensorManager` — it provides batching, on-device data fusion, and power-efficient
delivery tuned for watches. Three clients cover the common needs.

## Pick a client

| Client | Use case | Lifecycle |
|--------|----------|-----------|
| `MeasureClient` | On-demand spot reading (e.g. one heart-rate sample) | While screen on / app foreground |
| `ExerciseClient` | Active workout with real-time metrics, auto-pause, GPS | Foreground service holds the session |
| `PassiveMonitoringClient` | Low-frequency, long-lived background data (steps, passive HR) | `PassiveListenerService` / callback |

## Always check capabilities first

Sensors and supported data types vary per device — verify before registering.

```kotlin
val healthClient = HealthServices.getClient(context)
val measureClient = healthClient.measureClient
val caps = measureClient.getCapabilitiesAsync().await()
val canHr = DataType.HEART_RATE_BPM in caps.supportedDataTypesMeasure
if (!canHr) { /* disable the feature, show helper text */ }
```

## MeasureClient — spot heart rate

```kotlin
val callback = object : MeasureCallback {
    override fun onAvailabilityChanged(dataType: DeltaDataType<*, *>, availability: Availability) {}
    override fun onDataReceived(data: DataPointContainer) {
        val hr = data.getData(DataType.HEART_RATE_BPM).lastOrNull()?.value
    }
}
measureClient.registerMeasureCallback(DataType.HEART_RATE_BPM, callback)
// ... unregister when done (it keeps the sensor on).
```

## ExerciseClient — active workout

- Start an exercise with an `ExerciseConfig` (data types, GPS, auto-pause).
- Receive `ExerciseUpdate`s via an `ExerciseUpdateCallback`.
- Hold the session inside a **foreground service** + Ongoing Activity so it survives the
  user navigating away (see `wear-os-tiles-complications`).

## PassiveMonitoringClient — background

- Implement a `PassiveListenerService` (system-managed) **or** register a
  `PassiveListenerCallback` (only while active).
- Data arrives in **batches** that may mix data types — iterate the container.
- Use for steps / passive HR where updates are infrequent and battery matters.

## Permissions

| Scenario | Permission(s) |
|----------|---------------|
| Foreground body sensors (HR) | `BODY_SENSORS` |
| Background body sensors, API 33–35 | `BODY_SENSORS` + `BODY_SENSORS_BACKGROUND` |
| Background health data, API 36+ | `READ_HEALTH_DATA_IN_BACKGROUND` |
| Foreground service for tracking | `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_HEALTH` |

Request runtime permissions before registering, and degrade gracefully when denied.

## Testing

- Use Health Services **synthetic / simulated data** to drive sensor flows on the
  emulator (no physical heart rate required).
- Still validate on at least one physical OEM watch before release — real sensor timing
  and availability differ.

## Do / Don't

- ✅ Check capabilities before every registration.
- ✅ Unregister callbacks promptly — an active sensor drains the battery.
- ✅ Run active sessions in a foreground service.
- ❌ Don't use raw `SensorManager` for HR/exercise on Wear.
- ❌ Don't request background sensor permissions unless you truly sample in the background.
