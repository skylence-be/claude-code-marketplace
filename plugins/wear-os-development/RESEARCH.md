# Wear OS Development — Best-Practices Research (2026)

> Phase-1 research backing the `wear-os-development` plugin skills. Every technical
> claim below is sourced from official Android/Google documentation (URLs inline).
> API names, artifact coordinates, and version requirements were verified against
> the linked docs — **no APIs were invented**. Where the brief implied a claim that
> the official docs do not literally state (e.g. "Google says don't use Flutter"),
> the honest, sourced position is recorded instead.

Researched 2026-06-16 (web). Primary source: `developer.android.com` + the Android
Developers Blog.

---

## 1. UI — Compose for Wear OS (Material 3 Expressive)

- **Jetpack Compose is the recommended UI toolkit for Wear OS.** It is the modern,
  declarative path and Google recommends it over the legacy Wear UI / View system.
- Wear OS has its **own** Material, Foundation, and Navigation libraries — distinct
  from mobile Compose. **Do not mix** mobile `compose-material` with Wear Compose;
  mixing produces unexpected behavior and is not optimized for round screens.
- Current design system is **Material 3 Expressive**, delivered by the Wear Compose
  Material 3 library `androidx.wear.compose:compose-material3`.
- Library family `androidx.wear.compose:compose-*` (foundation, material, material3,
  navigation). As of mid-2025 the stable line was ~`1.5.0` with `1.6.0-alpha`
  in development. Always pin the current stable from the release page below.
- Lists:
  - `ScalingLazyColumn` — the Material 2.5 round-screen list (scaling + transparency
    toward the edges). Still present in `androidx.wear.compose.material`.
  - `TransformingLazyColumn` (TLC) — the Material 3 successor in Wear Compose
    Foundation lazy; items scale/morph via a `TransformationSpec` as they scroll.
    Prefer TLC for new Material 3 apps.
- Use `AppScaffold` / `ScreenScaffold`, `TimeText`, and edge-hugging components from
  the Wear libraries rather than re-implementing chrome.

Sources:
- https://developer.android.com/training/wearables/compose
- https://developer.android.com/jetpack/androidx/releases/wear-compose-m3
- https://developer.android.com/jetpack/androidx/releases/wear-compose
- https://developer.android.com/training/wearables/compose/migrate-to-material3
- https://developer.android.com/training/wearables/compose/lists?version=3
- https://developer.android.com/training/wearables/compose/navigation

## 2. Tiles, ProtoLayout & Complications

- Tiles are **glanceable, declarative** surfaces built with Jetpack's
  `androidx.wear.tiles` + `androidx.wear.protolayout` libraries (NOT Compose at
  runtime — layouts are ProtoLayout objects).
- `Material3TileService` is the new Kotlin-friendly base: one `suspend` function
  returns both tile layout and resources, managing `MaterialScope` / `ProtoLayoutScope`
  for you. Prefer it over hand-rolled `TileService` for Material 3 tiles.
- ProtoLayout ships pre-built Material 3 Expressive components/layouts.
- Best practices: **don't overcrowd** a tile; show a glance and let a tap open the
  full app for actions. Tiles refresh periodically — keep work cheap.
- **Ongoing activities**: for long-running work (workout, media), surface progress in
  a tile and via the **Ongoing Activity API**; if a tile can start the activity,
  indicate when one is already in progress and resume it (don't start a new instance).
- **Complications** are provided by a `ComplicationDataSourceService` (a.k.a. complication
  data source / provider) for watch faces.
- `METADATA_GROUP_KEY` groups multiple `TileService` entries in the manifest for
  cross-OS-version switching.

Sources:
- https://developer.android.com/training/wearables/tiles
- https://developer.android.com/training/wearables/tiles/get_started
- https://developer.android.com/design/ui/wear/guides/surfaces/tiles/bestpractices
- https://developer.android.com/training/wearables/tiles/update
- https://developer.android.com/jetpack/androidx/releases/wear-protolayout
- https://developer.android.com/jetpack/androidx/releases/wear-tiles

## 3. Health Services (sensors / heart rate / passive monitoring)

- Use **Health Services** (`androidx.health:health-services-client`) rather than raw
  `SensorManager` — it provides batching, on-device data fusion, and power-efficient
  delivery. (Verified coordinate from docs: `androidx.health:health-services-client`,
  e.g. `1.1.0-alpha05`; pin current from the Health release page.)
- Clients:
  - `PassiveMonitoringClient` + `PassiveListenerService` (or `PassiveListenerCallback`)
    — low-frequency, long-lived background data (steps, passive heart rate). Data is
    delivered in **batches** that may mix data types.
  - `ExerciseClient` — active workout sessions (real-time metrics, auto-pause, GPS).
  - `MeasureClient` — on-demand spot measurements (e.g. a one-off heart-rate reading).
- **Always check capabilities first** (e.g. `getCapabilitiesAsync`) — verify
  `DataType.HEART_RATE_BPM` is supported before registering. Devices vary.
- Data types split into sample-in-time (`HEART_RATE_BPM`) vs interval (`DISTANCE`).
- Permissions:
  - Foreground body sensors: `BODY_SENSORS`.
  - Background body sensors (API 33–35): `BODY_SENSORS` + `BODY_SENSORS_BACKGROUND`.
  - API 36+ background health data: `READ_HEALTH_DATA_IN_BACKGROUND`.
- Health Services supports **simulated/synthetic data** for emulator testing.

Sources:
- https://developer.android.com/health-and-fitness/health-services
- https://developer.android.com/health-and-fitness/health-services/monitor-background
- https://developer.android.com/health-and-fitness/health-services/permissions
- https://developer.android.com/training/wearables/health-services/active
- https://developer.android.com/health-and-fitness/health-services/active-data/measure-client
- https://developer.android.com/reference/kotlin/androidx/health/services/client/PassiveMonitoringClient
- https://developer.android.com/health-and-fitness/health-services/simulated-data

## 4. Standalone vs companion apps & networking

- Declare app type with the `com.google.android.wearable.standalone` `meta-data`
  flag in the manifest. **Standalone** apps function without a paired phone;
  non-standalone depend on a companion phone app.
- **Data Layer API** (part of Google Play services) is the phone↔watch channel:
  `DataClient` (`DataItem` sync), `MessageClient` (`MessageEvent`), `CapabilityClient`
  (discover nodes/features), `ChannelClient` (large transfers).
  - Over Bluetooth it is a single encrypted channel; when BT is unavailable data is
    routed end-to-end-encrypted through Google Cloud.
  - **Do NOT use the Data Layer API to reach the network.** BLE bandwidth can be as
    low as ~4 KB/s. DataItems are meant to be small.
- For internet access, standalone watches communicate **directly over the network**
  (standard `HttpURLConnection`/OkHttp/Retrofit + WorkManager), not via the phone.
- `WearableListenerService` receives Data Layer events even when your app isn't
  running (system binds/unbinds it). If you only need events while active, register a
  **live listener** instead to save battery.
- Authentication on watches: use **Credential Manager** / OAuth flows designed for Wear
  (`auth-wear`), not phone-only UIs.

Sources:
- https://developer.android.com/training/wearables/apps/standalone-apps
- https://developer.android.com/training/wearables/apps/independent-vs-dependent
- https://developer.android.com/training/wearables/data/overview
- https://developer.android.com/training/wearables/data/client-types
- https://developer.android.com/training/wearables/data/network-communication
- https://developer.android.com/training/wearables/apps/auth-wear

## 5. Background work, battery & power

- Battery is the #1 constraint on a watch. Choose the lightest mechanism:
  - **WorkManager** for deferrable/periodic work — it is battery-aware and respects
    Doze/system optimizations. Don't schedule too frequently or for long durations.
    Use constraints like `RequiresCharging` for non-urgent sync.
  - **Foreground service + Ongoing Activity API** for user-visible long tasks (workout
    tracking, media) that must survive navigation — creates a persistent notification
    + tappable ongoing-activity chip.
  - Wake locks are a last resort; audit them (Battery Historian) and prefer
    higher-level APIs that keep the device awake correctly.
- **Always-on / ambient mode** significantly impacts battery — opt in deliberately and
  render a low-power ambient UI.
- Data Layer hygiene: set up listeners only when active; transmit **state changes**,
  not rapid polling.

Sources:
- https://developer.android.com/training/wearables/apps/power
- https://developer.android.com/training/wearables/apps/always-on
- https://developer.android.com/develop/background-work
- https://developer.android.com/develop/background-work/background-tasks/optimize-battery
- https://developer.android.com/develop/background-work/background-tasks/awake

## 6. Data persistence & security

- **`androidx.security:security-crypto` (EncryptedSharedPreferences / EncryptedFile)
  is DEPRECATED** as of the stable `1.1.0` release — there will be **no further
  releases**. Do not start new code on it.
- Recommended modern storage: **Jetpack DataStore** (`androidx.datastore`) —
  Preferences DataStore (key/value) or Proto DataStore (typed, protobuf-backed),
  coroutine/Flow based, transactional. A `SharedPreferencesMigration` constructor
  eases migration off EncryptedSharedPreferences.
- For secrets/keys: use the **Android Keystore** system (hardware-backed where
  available) to store key material; use **Tink** (Google's crypto library) for the
  actual encrypt/decrypt of payloads layered over DataStore/files.
- Follow the Android **security checklist**: least-privilege permissions, no secrets in
  plaintext prefs/logs, validate all Data Layer input.

Sources:
- https://developer.android.com/jetpack/androidx/releases/security
- https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences
- https://developer.android.com/jetpack/androidx/releases/datastore
- https://developer.android.com/topic/security/data
- https://developer.android.com/privacy-and-security/cryptography

## 7. Testing

- **Compose UI tests** are synchronized with the UI tree by default (`ComposeTestRule`
  waits for idle before assertions/actions); control the clock for animation snapshots.
- **Compose Preview Screenshot testing** is the recommended way to verify Wear visual
  attributes (round-screen layout, ambient).
- Test on **both emulators and physical devices** from major Wear OEMs; set up testing
  early. Use the Wear OS system images (e.g. Wear OS 5.1) in the emulator AVD.
- Use Wear-specific Material/Foundation/Navigation libraries in tests too.
- Health Services **synthetic data** lets you test sensor flows on an emulator.
- Meet the **Wear OS app quality** guidelines before publishing.

Sources:
- https://developer.android.com/docs/quality-guidelines/wear-app-quality
- https://developer.android.com/develop/ui/compose/testing
- https://developer.android.com/develop/ui/compose/testing/synchronization
- https://developer.android.com/training/testing/ui-tests/screenshot
- https://developer.android.com/training/wearables/versions/5-1

## 8. Platform versions, packaging & distribution

- **Target API level:** as of **Aug 31, 2025**, new apps submitted to Google Play must
  target **Android 14 (API 34)** or higher. Wear OS 5 is based on Android 14. Apps
  targeting API ≤31 are not discoverable on devices running a higher Wear OS version.
- **Wear OS 6** introduces behavior changes — test against `versions/6/changes`. It
  ships **Watch Face Format (WFF) v4**.
- **Watch Face Format:** as of **Jan 2026**, WFF is required to install watch faces on
  Wear OS 5+ devices and for all new watch faces on Play; legacy (AndroidX/SysUI)
  watch faces had to migrate/resubmit by **Jan 14, 2026**. Watches launching on
  Wear OS 6 only support WFF watch faces.
- Package the Wear app per the distribution guidance (embedded vs separate listing);
  ship correct ABIs.

Sources:
- https://developer.android.com/docs/quality-guidelines/wear-app-quality
- https://developer.android.com/training/wearables/versions/6/changes
- https://developer.android.com/training/wearables/wff
- https://android-developers.googleblog.com/2025/05/whats-new-in-wear-os-6.html
- https://developer.android.com/distribute/best-practices/launch/distribute-wear

## 9. Native vs cross-platform (the "Compose over Flutter" question)

- The official Android docs **recommend native Jetpack Compose (Kotlin)** as *the*
  approach for Wear OS, emphasizing the Wear-specific Material/Foundation/Navigation
  libraries and warning against reusing mobile Compose Material.
- **Honest scope note:** I did not find an official Android doc that explicitly tells
  developers *not to use Flutter* for Wear OS. The defensible, sourced statement is:
  *Google's first-party guidance and tooling (Wear Compose, Tiles/ProtoLayout, Health
  Services, Watch Face Format) target native Kotlin/Compose, which is the recommended
  and best-supported path.* The skills assert that, not a fabricated ban.

Sources:
- https://developer.android.com/training/wearables/compose
- https://developer.android.com/training/wearables/apps

---

## Coordinates quick-reference (verify current versions before pinning)

| Capability | Artifact | Notes |
|---|---|---|
| Wear Compose M3 | `androidx.wear.compose:compose-material3` | Material 3 Expressive |
| Wear Compose foundation/material/nav | `androidx.wear.compose:compose-foundation` / `compose-material` / `compose-navigation` | TLC lives in foundation lazy |
| Tiles | `androidx.wear.tiles:tiles` (+ `tiles-material`) | `Material3TileService` |
| ProtoLayout | `androidx.wear.protolayout:protolayout` (+ `-material3`, `-expression`) | declarative layouts |
| Health Services | `androidx.health:health-services-client` | Passive/Exercise/Measure clients |
| Data Layer | `com.google.android.gms:play-services-wearable` | DataClient/MessageClient/CapabilityClient |
| Storage | `androidx.datastore:datastore-preferences` / `datastore` | replaces EncryptedSharedPreferences |
| Background | `androidx.work:work-runtime-ktx` | battery-aware deferrable work |
| Ongoing activity | `androidx.wear:wear-ongoing` | ongoing-activity chip |
