# Scaffolds & Chrome

Wear Compose Material 3 provides the screen chrome so you don't re-implement it.

## AppScaffold + ScreenScaffold

```kotlin
import androidx.wear.compose.material3.AppScaffold
import androidx.wear.compose.material3.ScreenScaffold
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.Text

@Composable
fun StartScreen(onStart: () -> Unit, sensorReady: Boolean) {
    AppScaffold {                 // app-level: hosts TimeText, scroll indicator
        ScreenScaffold {          // per-screen: positions content in safe area
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
            ) {
                Text("Run Tracker")
                Spacer(Modifier.height(8.dp))
                Button(
                    onClick = onStart,
                    enabled = sensorReady,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text(if (sensorReady) "Start run" else "No HR sensor") }
            }
        }
    }
}
```

- `AppScaffold` is set up **once** near the navigation root; `ScreenScaffold` wraps
  each destination so `TimeText` and the position/scroll indicators render correctly.
- `TimeText` is provided by the scaffold — don't draw your own clock.

## Buttons & cards

- Use Material 3 `Button`, `FilledTonalButton`, `OutlinedButton`, `IconButton`,
  and `Card` from `androidx.wear.compose.material3`.
- Make the primary action `fillMaxWidth()` for an easy tap target on a small screen.
- One primary action per screen keeps surfaces glanceable.

## Edge buttons & full-screen actions

For confirm/cancel use the Wear-specific edge button so the tap target hugs the round
bezel rather than a centered mobile-style button.

## Field lessons (building, 2026-06)

Verified on a real Pixel Watch build:

- **Round-screen overflow is unforgiving.** A round display gives roughly a **~192dp**
  in-flow content budget; content laid out past it is clipped by the bezel, not scrolled
  into view. Keep screens to in-flow layout inside the scaffold's safe area and let a
  list (TLC / SLC) own any overflow — don't push fixed-height columns past the curve.
- **Add a tap-to-refresh affordance.** Background, tile, and complication refresh are all
  throttled (15-min WorkManager floor, on-view tiles, a shared staleness gate), so a user
  who wants data *now* needs a manual path — a tap that triggers your refresh while still
  respecting the same staleness floor (see `wear-os-data-and-security`).

## Anti-patterns

- ❌ Importing `androidx.compose.material3.*` (mobile) — visually and behaviorally wrong
  on a watch, and mixing with Wear Material is explicitly unsupported.
- ❌ Hardcoding rectangular padding instead of relying on the scaffold's safe-area handling.
