---
name: wear-os-compose-patterns
description: Compose for Wear OS: Material 3 Expressive scaffolds, scaling lists, navigation, ambient. Use when building Wear OS UI.
category: wear-os
tags: [wear-os, compose, material3, ui, round-screen, navigation]
related_skills: [wear-os-blueprint, wear-os-tiles-complications, wear-os-data-and-security]
---

# Compose for Wear OS Patterns

Jetpack Compose is the **recommended** UI toolkit for Wear OS. Wear has its **own**
Material 3, Foundation, and Navigation libraries — do **not** mix mobile
`compose-material` with Wear Compose, and never assume a rectangular screen.

## Pattern Files

Load specific patterns based on your needs:

| Pattern | File | Use Case |
|---------|------|----------|
| Scaffolds & Chrome | [scaffolding.md](scaffolding.md) | AppScaffold, ScreenScaffold, TimeText, buttons |
| Lists & Scaling | [lists-and-scaling.md](lists-and-scaling.md) | ScalingLazyColumn, TransformingLazyColumn |
| Navigation & State | [navigation-and-state.md](navigation-and-state.md) | SwipeDismissableNavHost, ambient, state |

## Quick Reference

### Dependencies (pin current stable — see RESEARCH.md)
```kotlin
implementation("androidx.wear.compose:compose-material3:<latest>")  // M3 Expressive
implementation("androidx.wear.compose:compose-foundation:<latest>") // TLC, lazy
implementation("androidx.wear.compose:compose-navigation:<latest>")
```

### Minimal screen
```kotlin
@Composable
fun RunApp() {
    AppScaffold {                         // app-level chrome (TimeText)
        ScreenScaffold {                  // per-screen scaffold
            // round-screen aware content
            Button(onClick = { /* ... */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start run")
            }
        }
    }
}
```

### Material 3 Expressive
- Use `androidx.wear.compose.material3` components (`Button`, `Card`, `ListHeader`,
  `Text`, `TimeText`), NOT `androidx.compose.material3`.
- Prefer `TransformingLazyColumn` for new Material 3 lists; `ScalingLazyColumn` is the
  Material 2.5 list still available for migration.

### Round-screen rules
- Content must remain legible inside the circular safe area — let `ScreenScaffold` and
  the Wear components handle insets; don't hardcode rectangular padding.
- Keep each screen glanceable; one primary action per screen where possible.

### Do / Don't
- ✅ Wear Compose Material 3 + Foundation + Navigation libraries
- ✅ `AppScaffold` / `ScreenScaffold` / `TimeText` for chrome
- ❌ Mobile `androidx.compose.material`/`material3` components on a watch
- ❌ Assuming a rectangular screen or fixed pixel layouts
