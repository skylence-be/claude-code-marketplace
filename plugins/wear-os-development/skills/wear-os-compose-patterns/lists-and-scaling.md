# Lists & Scaling

Round screens need lists that scale/fade toward the curved edges. Wear Compose gives
two purpose-built lists — pick by design system.

## TransformingLazyColumn (Material 3 — prefer for new apps)

`TransformingLazyColumn` (TLC) lives in Wear Compose Foundation lazy. Items scale and
morph as they scroll, driven by a `TransformationSpec`.

```kotlin
import androidx.wear.compose.foundation.lazy.TransformingLazyColumn
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState

@Composable
fun RunHistory(runs: List<RunRecord>) {
    val state = rememberTransformingLazyColumnState()
    ScreenScaffold(scrollState = state) {
        TransformingLazyColumn(state = state) {
            items(runs, key = { it.id }) { run ->
                Card(onClick = { /* open */ }, modifier = Modifier.fillMaxWidth()) {
                    Text("${run.distanceM / 1000.0} km")
                }
            }
        }
    }
}
```

## ScalingLazyColumn (Material 2.5 — migration / legacy)

`ScalingLazyColumn` (SLC) lives in `androidx.wear.compose.material`. It scales and fades
items toward the edges. Still valid; use it when staying on Material 2.5 or migrating.

```kotlin
import androidx.wear.compose.material.ScalingLazyColumn
import androidx.wear.compose.material.rememberScalingLazyListState

val listState = rememberScalingLazyListState()
ScalingLazyColumn(state = listState) {
    items(runs) { run -> /* ... */ }
}
```

## Guidance

- New Material 3 Expressive UI → **TransformingLazyColumn**.
- Wire the list's scroll state into `ScreenScaffold(scrollState = ...)` so the position
  indicator tracks scrolling.
- Always supply stable `key`s for items.
- Don't use a plain mobile `LazyColumn` on a watch — it won't scale for the round screen.
