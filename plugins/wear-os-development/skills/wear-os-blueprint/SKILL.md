---
name: wear-os-blueprint
description: Wear OS Blueprint: planning format for Kotlin + Compose smartwatch apps. Use when planning implementations or generating code.
category: wear-os
tags: [wear-os, blueprint, ai, planning, architecture, specification]
related_skills: [wear-os-compose-patterns, wear-os-tiles-complications, wear-os-health-services, wear-os-data-and-security]
---

# Wear OS Blueprint

Wear OS Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Kotlin + Jetpack Compose smartwatch apps. It bridges the gap between high-level requirements and production-ready code by deciding every surface, screen, dependency, permission, and power trade-off **before** a line is written — because a watch app fails on the details (battery, round screens, sensor permissions, standalone vs paired).

## When to Use This Skill

- Planning a new Wear OS app (standalone or phone-paired) from requirements
- Creating detailed specifications before writing Compose / Tiles / Health Services code
- Deciding which **surfaces** an app needs (main app, Tiles, Complications, Ongoing Activity)
- Documenting glanceable user flows and on-watch interactions
- Capturing every detail: Gradle coordinates, permissions, data types, background strategy
- Avoiding vague plans that lead to battery-draining or non-glanceable code

## Blueprint Plan Structure

A complete Wear OS Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# Run Tracker (Wear OS)

A standalone running app that tracks heart rate + distance on the watch.

## Key Decisions
- Standalone app (no phone required); direct network for sync
- UI: Jetpack Compose for Wear OS, Material 3 Expressive
- Active tracking via Health Services ExerciseClient + foreground service
- One Tile (start/resume run) + one Complication (last run distance)
- Persistence: Proto DataStore (NOT EncryptedSharedPreferences — deprecated)
- minSdk 30, targetSdk 34 (Android 14 / Wear OS 5 baseline; required by Play)
```

### 2. App Type & Surfaces

Decide standalone vs dependent, and enumerate every surface:

```markdown
## App Type
- Standalone: yes (`com.google.android.wearable.standalone` = true)
- Phone companion: optional (settings sync via Data Layer MessageClient)

## Surfaces
| Surface | Purpose | Entry point |
|---------|---------|-------------|
| Main app | Full run UI, history | Launcher / Tile tap |
| Tile | Start / resume a run (glance) | Tiles carousel |
| Complication | Last run distance | Watch face slot |
| Ongoing Activity | Live run progress while tracking | Foreground service notification |
```

### 3. User Flows

Document glanceable, step-by-step interactions (keep each ≤ a few taps):

```markdown
## User Flows

### Start a Run
1. User taps the Run Tracker Tile → app launches to Start screen
2. App checks Health Services capabilities (HEART_RATE_BPM, DISTANCE)
3. App requests BODY_SENSORS (+ ACCESS_FINE_LOCATION if GPS) if not granted
4. User taps Start → foreground service begins ExerciseClient session
5. Ongoing Activity chip appears; live metrics render via ScreenScaffold
6. User taps Stop → summary saved to DataStore, Complication updated
```

### 4. Gradle & Dependencies

List exact coordinates (pin current stable versions — see RESEARCH.md):

```markdown
## Dependencies
- androidx.wear.compose:compose-material3   # Material 3 Expressive UI
- androidx.wear.compose:compose-foundation  # TransformingLazyColumn
- androidx.wear.compose:compose-navigation  # Wear navigation
- androidx.health:health-services-client    # ExerciseClient / sensors
- androidx.wear:wear-ongoing                 # Ongoing Activity API
- androidx.wear.tiles:tiles + tiles-material # Tile
- androidx.wear.protolayout:protolayout-material3
- androidx.datastore:datastore               # Proto DataStore persistence
- androidx.work:work-runtime-ktx             # battery-aware sync
- com.google.android.gms:play-services-wearable  # Data Layer (if paired)
```

### 5. Screens (Compose for Wear OS)

Specify each screen, its scaffold, and key composables:

```markdown
## Screens

### StartScreen
**Scaffold**: AppScaffold > ScreenScaffold (TimeText auto)
**Composables**:
- Title (ListHeader)
- Primary Button "Start run" (Material 3 Button, fillMaxWidth)
- Capability gate: disabled + helper text if HEART_RATE_BPM unsupported

### ActiveRunScreen
**Scaffold**: ScreenScaffold
**Composables**:
- Large heart-rate + distance readouts (TimeText shows clock)
- Stop button
- Ambient-aware: low-power rendering in ambient mode

### HistoryScreen
**List**: TransformingLazyColumn (Material 3) of past runs
```

### 6. Data Model & Persistence

```markdown
## Data Model

### RunRecord (Proto DataStore message)
| Field | Type | Notes |
|-------|------|-------|
| id | string | UUID |
| started_at | int64 | epoch millis |
| duration_s | int32 | seconds |
| distance_m | double | meters |
| avg_hr | int32 | bpm |

**Store**: Proto DataStore `runs.pb` (typed, Flow-backed)
**Security**: no PII secrets in plaintext; if a token is stored, encrypt with
Tink + Android Keystore key, then persist ciphertext in DataStore.
```

### 7. Health Services Plan

```markdown
## Health Services
- Client: ExerciseClient (active session) + MeasureClient (spot HR on Start screen)
- Capabilities check BEFORE registering: getCapabilitiesAsync → assert
  DataType.HEART_RATE_BPM and DataType.DISTANCE
- Delivery: foreground service holds the session; ExerciseUpdateCallback → state
- Permissions: BODY_SENSORS (fg); BODY_SENSORS_BACKGROUND (API 33-35) or
  READ_HEALTH_DATA_IN_BACKGROUND (API 36+) only if background sampling needed
- Emulator: drive with Health Services synthetic data
```

### 8. Permissions

```markdown
## Permissions (AndroidManifest + runtime)
| Permission | Why | When requested |
|-----------|-----|----------------|
| BODY_SENSORS | heart rate | before first run |
| ACCESS_FINE_LOCATION | GPS distance | before first run (if GPS) |
| FOREGROUND_SERVICE + FOREGROUND_SERVICE_HEALTH | live tracking | manifest |
| POST_NOTIFICATIONS | ongoing-activity chip | first launch (API 33+) |
```

### 9. Background & Power Strategy

```markdown
## Background / Power
- Active run: foreground service + Ongoing Activity API (survives navigation)
- Periodic cloud sync: WorkManager, constraint RequiresCharging for non-urgent
- No wake locks; no always-on unless a deliberate ambient run face is built
- Data Layer listeners only while app active; transmit state changes, not polls
```

### 10. Testing Plan

```markdown
## Testing
- Compose UI tests (ComposeTestRule, auto-synchronized) for each screen
- Compose Preview Screenshot tests for round-screen + ambient layouts
- Health Services synthetic data for sensor flows on the emulator
- Manual: Wear OS 5.1 emulator AVD + at least one physical OEM watch
- Gate against Wear OS app-quality guidelines before release
```

## Blueprint Principles

- **Glanceable first** — every surface answers "what can the user see/do in 2 seconds?"
- **Battery is a feature** — pick the lightest background mechanism that works.
- **Verify capabilities, don't assume** — sensors and data types vary per device.
- **Round-screen native** — use Wear Compose libraries, never mobile Compose Material.
- **Decide surfaces up front** — app, Tile, Complication, and Ongoing Activity are
  separate deliverables with separate code paths.
- A vague plan leads to a watch app that drains the battery and ignores the round screen.
