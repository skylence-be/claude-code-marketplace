---
description: Scaffold Wear OS Health Services monitoring (heart rate / exercise / passive)
---

Scaffold a Wear OS Health Services integration.

## Monitor Specification

$ARGUMENTS

## Guidance

Use `androidx.health:health-services-client`. Pick the client by use case and ALWAYS
check capabilities before registering.

### 1. Choose the client
- `MeasureClient` — on-demand spot reading (e.g. one heart-rate sample)
- `ExerciseClient` — active workout (real-time metrics; run in a foreground service)
- `PassiveMonitoringClient` — low-frequency background data (steps, passive HR)

### 2. Capability check (required first)
```kotlin
val client = HealthServices.getClient(context)
val caps = client.measureClient.getCapabilitiesAsync().await()
require(DataType.HEART_RATE_BPM in caps.supportedDataTypesMeasure) { "No HR sensor" }
```

### 3. Register & receive
```kotlin
val callback = object : MeasureCallback {
    override fun onAvailabilityChanged(d: DeltaDataType<*, *>, a: Availability) {}
    override fun onDataReceived(data: DataPointContainer) {
        val hr = data.getData(DataType.HEART_RATE_BPM).lastOrNull()?.value
    }
}
client.measureClient.registerMeasureCallback(DataType.HEART_RATE_BPM, callback)
// Unregister when done — an active sensor drains the battery.
```

### 4. Permissions
- Foreground HR: `BODY_SENSORS`
- Background (API 33–35): `BODY_SENSORS` + `BODY_SENSORS_BACKGROUND`
- Background (API 36+): `READ_HEALTH_DATA_IN_BACKGROUND`
- Active tracking service: `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_HEALTH`

### Rules
- Check capabilities before every registration; degrade gracefully when unsupported.
- Run active exercise sessions in a foreground service + Ongoing Activity.
- Test with Health Services synthetic data on the emulator, then a physical watch.

Generate the client setup, callback/service, permission declarations, and runtime requests.
