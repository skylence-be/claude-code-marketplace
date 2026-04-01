# Flutter Review Rules

Technology-specific review rules for Flutter 3.x and Dart applications. Loaded when `pubspec.yaml` with Flutter SDK dependency is detected.

## Detection
- `pubspec.yaml` contains `flutter` SDK dependency
- `.dart` files in the changeset
- `lib/` directory with Flutter widget files

## Anti-Patterns to Flag

### setState After dispose
Calling `setState()` after the widget has been disposed, causing a framework error.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** Async operation followed by `setState()` without checking `mounted`
- **Fix:** Add `if (!mounted) return;` before `setState()` in async callbacks

### BuildContext Across Async Gaps
Using `BuildContext` after an `await` — the context may be invalid if the widget was unmounted.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `await someOperation(); Navigator.of(context).push(...)` or `ScaffoldMessenger.of(context)`
- **Fix:** Check `if (!context.mounted) return;` before using context after await

### Missing dispose() for Controllers
Creating `TextEditingController`, `AnimationController`, `ScrollController`, or `StreamSubscription` without disposing.
- **Severity:** High (performance)
- **Pattern:** Controller created in `initState()` or as field without corresponding `dispose()` method
- **Fix:** Override `dispose()` and call `controller.dispose()` then `super.dispose()`

### Missing const Constructors
Widget constructors that could be `const` but aren't, preventing compile-time constant optimization.
- **Severity:** Low (performance)
- **Pattern:** `MyWidget({required this.title})` without `const` keyword, where all fields are final
- **Fix:** Add `const`: `const MyWidget({required this.title})`

### GlobalKey Misuse
Using `GlobalKey` for simple communication between widgets when callbacks or controllers would suffice.
- **Severity:** Medium (performance)
- **Pattern:** `GlobalKey<MyWidgetState>()` used to call methods on child widgets
- **Fix:** Use callbacks, `ValueNotifier`, or controller patterns instead

### Riverpod ref.read in Build Methods
Using `ref.read()` inside `build()` means the widget won't rebuild when the provider changes.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `ref.read(provider)` inside `build()` or `ConsumerWidget.build()`
- **Fix:** Use `ref.watch(provider)` to reactively rebuild on changes

### Missing Error Handling on Futures
Unhandled Future errors causing silent failures or unhandled exception crashes.
- **Severity:** Medium (error-handling)
- **Pattern:** `someAsyncFunction()` without `.catchError()`, `try/catch`, or `AsyncValue` error handling
- **Fix:** Wrap in try-catch or use `.catchError()`, or handle `AsyncValue.error` state in Riverpod

### setState in initState
Calling `setState()` inside `initState()` is unnecessary and can cause issues.
- **Severity:** Medium (correctness)
- **Pattern:** `@override void initState() { super.initState(); setState(() { ... }); }`
- **Fix:** Assign values directly in `initState()` without `setState()` — the first `build()` hasn't happened yet
