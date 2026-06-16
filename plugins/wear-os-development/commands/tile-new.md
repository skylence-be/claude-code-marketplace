---
description: Create a Wear OS Tile with ProtoLayout (Material3TileService)
---

Create a glanceable Wear OS Tile.

## Tile Specification

$ARGUMENTS

## Guidance

Build the Tile with `androidx.wear.tiles` + `androidx.wear.protolayout` using
`Material3TileService` (a single `suspend` function returns layout + resources).

### 1. Service
```kotlin
class RunTileService : Material3TileService() {
    override suspend fun tileLayout(/* requestParams */): /* ProtoLayout */ {
        // Glanceable: title + ONE primary action. A tap opens the app to act.
        // Use ProtoLayout Material 3 components for Material 3 Expressive styling.
    }
}
```

### 2. Manifest registration
```xml
<service
    android:name=".tiles.RunTileService"
    android:exported="true"
    android:permission="com.google.android.wearable.permission.BIND_TILE_PROVIDER">
    <intent-filter>
        <action android:name="androidx.wear.tiles.action.BIND_TILE_PROVIDER" />
    </intent-filter>
    <meta-data
        android:name="androidx.wear.tiles.PREVIEW"
        android:resource="@drawable/tile_preview" />
</service>
```

### Rules
- Don't overcrowd — one glance, one action; tap to open the app.
- Keep `tileLayout` cheap; tiles refresh periodically. Refresh data via a tile update,
  not by polling inside the layout.
- Provide a preview drawable for the tiles carousel.

Generate the complete TileService, layout builder, and manifest entry.
