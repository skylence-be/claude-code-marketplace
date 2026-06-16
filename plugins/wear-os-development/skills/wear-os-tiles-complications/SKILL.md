---
name: wear-os-tiles-complications
description: Wear OS Tiles, ProtoLayout, Complications, and Ongoing Activity surfaces. Use when building glanceable Wear surfaces.
category: wear-os
tags: [wear-os, tiles, protolayout, complications, ongoing-activity, glanceable]
related_skills: [wear-os-blueprint, wear-os-compose-patterns, wear-os-health-services]
---

# Wear OS Tiles, Complications & Ongoing Activity

Tiles, Complications, and Ongoing Activities are the **glanceable** surfaces around your
app. They are NOT Compose at runtime — Tiles/Complications render declarative
**ProtoLayout** objects. Keep them cheap and let a tap open the full app for actions.

## Tiles (ProtoLayout)

Tiles are built with `androidx.wear.tiles` + `androidx.wear.protolayout`. Prefer
`Material3TileService`: a single `suspend` function returns both layout and resources,
managing `MaterialScope` / `ProtoLayoutScope` for you.

```kotlin
// Dependencies (pin current stable — see RESEARCH.md):
// androidx.wear.tiles:tiles
// androidx.wear.tiles:tiles-material
// androidx.wear.protolayout:protolayout-material3

class RunTileService : Material3TileService() {
    override suspend fun tileLayout(/* ... */): /* ProtoLayout */ {
        // Build a glanceable layout: title + one primary action (Start run)
        // Tapping launches the app via a LaunchAction / loadAction clickable.
    }
}
```

Register in `AndroidManifest.xml`:
```xml
<service
    android:name=".tiles.RunTileService"
    android:exported="true"
    android:permission="com.google.android.wearable.permission.BIND_TILE_PROVIDER">
    <intent-filter>
        <action android:name="androidx.wear.tiles.action.BIND_TILE_PROVIDER" />
    </intent-filter>
    <!-- preview drawable meta-data -->
</service>
```

### Tile best practices
- **Don't overcrowd** — a tile is a glance, not a screen. Show the single most useful
  thing and let a tap open the app to act.
- Tiles refresh **periodically**; keep `tileLayout` cheap and cache where possible.
  Request fresh data with a tile update rather than polling in the layout.
- Use ProtoLayout Material 3 components for consistent Material 3 Expressive styling.
- `METADATA_GROUP_KEY` groups multiple `TileService`s in the manifest for cross-OS
  version switching of the "same" tile.

## Complications

A complication is supplied by a `ComplicationDataSourceService` (complication data
source / provider) that returns typed `ComplicationData` for a watch-face slot.

```kotlin
class LastRunComplicationService : SuspendingComplicationDataSourceService() {
    override fun getPreviewData(type: ComplicationType): ComplicationData? = /* sample */

    override suspend fun onComplicationRequest(request: ComplicationRequest): ComplicationData {
        // Return e.g. SHORT_TEXT "5.2 km" from the latest stored run
    }
}
```

- Declare which `ComplicationType`s you support (SHORT_TEXT, RANGED_VALUE, etc.).
- Always provide preview data for the watch-face picker.
- Keep the request handler fast and read from local storage (DataStore), not the network.

## Ongoing Activity

For long-running, user-visible work (workout, media), pair a **foreground service**
with the **Ongoing Activity API** (`androidx.wear:wear-ongoing`). This surfaces a
persistent notification plus a tappable chip so the user can jump back into the session.

```kotlin
val ongoingActivity = OngoingActivity.Builder(applicationContext, NOTIF_ID, notificationBuilder)
    .setStaticIcon(R.drawable.ic_run)
    .setTouchIntent(launchAppPendingIntent)   // resume, don't restart
    .setStatus(Status.Builder().addTemplate("#distance# km").build())
    .build()
ongoingActivity.apply(applicationContext)
```

- Tapping the chip must **resume** the in-progress activity, never start a new instance.
- If a Tile can start the activity, indicate when one is already in progress.

## Surface decision guide

| Need | Surface |
|------|---------|
| Glance + one quick action | Tile |
| A value on the watch face | Complication |
| Live progress of a running task | Ongoing Activity (+ foreground service) |
| Full interaction / history | Main Compose app |
