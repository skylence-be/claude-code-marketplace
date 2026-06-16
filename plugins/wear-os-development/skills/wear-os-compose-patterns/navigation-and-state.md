# Navigation & State

## Wear navigation

Use the Wear Compose Navigation library (`androidx.wear.compose:compose-navigation`),
which provides swipe-to-dismiss-aware navigation rather than mobile NavHost.

```kotlin
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController
import androidx.wear.compose.navigation.composable

@Composable
fun RunNav() {
    val navController = rememberSwipeDismissableNavController()
    AppScaffold {
        SwipeDismissableNavHost(navController, startDestination = "start") {
            composable("start") { StartScreen(onStart = { navController.navigate("active") }) }
            composable("active") { ActiveRunScreen() }
            composable("history") { RunHistory(runs = /* ... */) }
        }
    }
}
```

- `SwipeDismissableNavHost` honors the watch's edge-swipe-back gesture.
- Keep the back stack shallow — deep navigation is awkward on a watch.

## State & architecture

- Hold UI state in a `ViewModel`; expose `StateFlow`, collect with
  `collectAsStateWithLifecycle()`.
- Keep composables stateless where possible; hoist state to the ViewModel.
- For long-running work (an exercise session) the source of truth is a **foreground
  service**, and the UI observes it — see `wear-os-health-services`.

## Ambient mode

Always-on / ambient mode keeps the app visible while the screen dims, at real battery
cost. Opt in deliberately:

- Render a simplified, low-color, low-refresh UI in ambient.
- Avoid animations and frequent updates while ambient.
- Only add always-on when the use case (e.g. a live run) justifies it.

## Anti-patterns

- ❌ Mobile `NavHost` (loses swipe-to-dismiss semantics).
- ❌ Driving long-running session state from a composable instead of a service.
- ❌ Always-on by default — it is one of the biggest battery drains on a watch.
