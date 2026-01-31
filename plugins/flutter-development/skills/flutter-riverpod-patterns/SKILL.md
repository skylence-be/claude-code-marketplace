---
name: flutter-riverpod-patterns
description: Master Riverpod 2.6+ state management patterns including code generation, AsyncValue handling, Notifiers, provider families, and proper dispose patterns. Use when implementing state management, handling async data, or building reactive UIs.
category: flutter
tags: [flutter, riverpod, state-management, providers, async]
---

# Flutter Riverpod Patterns

Modern Riverpod 2.6+ patterns with code generation for type-safe state management.

## When to Use This Skill

- Setting up Riverpod in a Flutter application
- Creating providers with code generation
- Handling async data with AsyncValue
- Building reactive UIs that respond to state changes
- Managing complex state with Notifiers
- Implementing caching and invalidation patterns

## Setup

### Dependencies
```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^2.6.1
  riverpod_annotation: ^2.6.1

dev_dependencies:
  riverpod_generator: ^2.4.0
  build_runner: ^2.4.13
```

### App Configuration
```dart
// main.dart
void main() {
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}
```

## Provider Types

### Simple Provider (Read-Only)
```dart
// providers/api_client_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'api_client_provider.g.dart';

@riverpod
ApiClient apiClient(ApiClientRef ref) {
  final baseUrl = ref.watch(settingsProvider).apiUrl;
  final token = ref.watch(authTokenProvider);

  return ApiClient(baseUrl: baseUrl, token: token);
}
```

### Async Provider (FutureProvider)
```dart
// providers/projects_provider.dart
@riverpod
Future<List<Project>> projects(ProjectsRef ref) async {
  final client = ref.watch(apiClientProvider);
  return client.fetchProjects();
}

// Usage in widget
class ProjectList extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final projectsAsync = ref.watch(projectsProvider);

    return projectsAsync.when(
      data: (projects) => ListView.builder(
        itemCount: projects.length,
        itemBuilder: (context, index) => ProjectTile(projects[index]),
      ),
      loading: () => const CircularProgressIndicator(),
      error: (error, stack) => ErrorWidget(error.toString()),
    );
  }
}
```

### Notifier Provider (Mutable State)
```dart
// providers/timer_provider.dart
@riverpod
class Timer extends _$Timer {
  @override
  TimerState build() {
    // Initial state
    return const TimerState.stopped();
  }

  Future<void> start(int projectId) async {
    state = const TimerState.loading();

    try {
      final repository = ref.read(timerRepositoryProvider);
      final entry = await repository.startTimer(projectId);
      state = TimerState.running(entry);

      // Start periodic updates
      _startTicking();
    } catch (e, st) {
      state = TimerState.error(e.toString());
    }
  }

  Future<void> stop() async {
    if (state is! TimerStateRunning) return;

    final running = state as TimerStateRunning;
    state = const TimerState.loading();

    try {
      final repository = ref.read(timerRepositoryProvider);
      await repository.stopTimer(running.entry.id);
      state = const TimerState.stopped();
    } catch (e) {
      state = TimerState.error(e.toString());
    }
  }

  Timer? _ticker;

  void _startTicking() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) {
      if (state is TimerStateRunning) {
        final running = state as TimerStateRunning;
        state = TimerState.running(
          running.entry.copyWith(
            elapsed: running.entry.elapsed + 1,
          ),
        );
      }
    });

    // Cleanup on dispose
    ref.onDispose(() => _ticker?.cancel());
  }
}
```

### Family Provider (Parameterized)
```dart
// providers/entry_provider.dart
@riverpod
Future<TimeEntry> entry(EntryRef ref, String entryId) async {
  final repository = ref.watch(entriesRepositoryProvider);
  return repository.getEntry(entryId);
}

// Usage
final entryAsync = ref.watch(entryProvider(entryId));
```

### Async Notifier (Mutable Async State)
```dart
// providers/entries_provider.dart
@riverpod
class EntriesNotifier extends _$EntriesNotifier {
  @override
  Future<List<TimeEntry>> build() async {
    final repository = ref.watch(entriesRepositoryProvider);
    return repository.getEntries();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final repository = ref.read(entriesRepositoryProvider);
      return repository.getEntries();
    });
  }

  Future<void> delete(String entryId) async {
    // Optimistic update
    final previous = state.valueOrNull ?? [];
    state = AsyncData(
      previous.where((e) => e.id != entryId).toList(),
    );

    try {
      final repository = ref.read(entriesRepositoryProvider);
      await repository.deleteEntry(entryId);
    } catch (e) {
      // Rollback on error
      state = AsyncData(previous);
      rethrow;
    }
  }
}
```

## AsyncValue Patterns

### Complete Handling
```dart
Widget build(BuildContext context, WidgetRef ref) {
  final dataAsync = ref.watch(dataProvider);

  return dataAsync.when(
    data: (data) => DataView(data),
    loading: () => const LoadingIndicator(),
    error: (error, stack) => ErrorView(
      message: error.toString(),
      onRetry: () => ref.invalidate(dataProvider),
    ),
  );
}
```

### With Previous Data (Skeleton Loading)
```dart
Widget build(BuildContext context, WidgetRef ref) {
  final dataAsync = ref.watch(dataProvider);
  final previousData = dataAsync.valueOrNull;

  return Stack(
    children: [
      if (previousData != null)
        DataView(previousData),
      if (dataAsync.isLoading)
        const LoadingOverlay(),
      if (dataAsync.hasError)
        ErrorSnackbar(dataAsync.error!),
    ],
  );
}
```

### Combining Providers
```dart
@riverpod
Future<DashboardData> dashboard(DashboardRef ref) async {
  // Watch multiple providers in parallel
  final (projects, entries, stats) = await (
    ref.watch(projectsProvider.future),
    ref.watch(entriesProvider.future),
    ref.watch(statsProvider.future),
  ).wait;

  return DashboardData(
    projects: projects,
    entries: entries,
    stats: stats,
  );
}
```

## State Patterns

### Sealed Class State
```dart
// Using freezed for sealed unions
@freezed
class TimerState with _$TimerState {
  const factory TimerState.stopped() = TimerStateStopped;
  const factory TimerState.loading() = TimerStateLoading;
  const factory TimerState.running(TimeEntry entry) = TimerStateRunning;
  const factory TimerState.error(String message) = TimerStateError;
}

// Pattern matching in UI
Widget build(BuildContext context, WidgetRef ref) {
  final state = ref.watch(timerProvider);

  return switch (state) {
    TimerStateStopped() => const StartButton(),
    TimerStateLoading() => const CircularProgressIndicator(),
    TimerStateRunning(:final entry) => RunningTimer(entry: entry),
    TimerStateError(:final message) => ErrorText(message),
  };
}
```

## Caching & Invalidation

### Auto-Dispose (Default)
```dart
// Provider is disposed when no longer watched
@riverpod
Future<Data> data(DataRef ref) async {
  // Automatically disposed
  return fetchData();
}
```

### Keep Alive
```dart
@Riverpod(keepAlive: true)
Future<Settings> settings(SettingsRef ref) async {
  // Never auto-disposed
  return loadSettings();
}
```

### Manual Invalidation
```dart
// Refresh data
ref.invalidate(entriesProvider);

// Refresh and wait
await ref.refresh(entriesProvider.future);
```

### Cache Duration
```dart
@riverpod
Future<Data> cachedData(CachedDataRef ref) async {
  // Keep alive for 5 minutes after last listener
  final link = ref.keepAlive();

  Timer(const Duration(minutes: 5), link.close);

  return fetchData();
}
```

## Best Practices

1. **Use code generation** - Always use `@riverpod` annotation
2. **Prefer watch over read** - Ensures reactivity
3. **Handle all AsyncValue states** - loading, data, error
4. **Use ref.onDispose** - Clean up subscriptions/timers
5. **Keep providers focused** - Single responsibility
6. **Use families for parameters** - Not closures
7. **Invalidate for refresh** - Not setState patterns

## Code Generation

```bash
# Generate provider code
dart run build_runner build --delete-conflicting-outputs

# Watch mode during development
dart run build_runner watch --delete-conflicting-outputs
```
