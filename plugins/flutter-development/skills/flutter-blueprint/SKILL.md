---
name: flutter-blueprint
description: Structured planning format for Flutter apps — bridges requirements to production-ready code. Use when planning Flutter implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: flutter
tags: [flutter, dart, blueprint, planning, architecture, mobile]
related_skills: [flutter-clean-architecture, flutter-riverpod-patterns]
---

# Flutter Blueprint

Flutter Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Flutter projects. It bridges the gap between high-level requirements and production-ready code by specifying every decision — architecture, state management, packages, file paths, data models, and code patterns — before a single line is written.

## When to Use This Skill

- Planning a new Flutter application from scratch
- Creating detailed specifications before writing code
- Generating comprehensive project architectures with feature modules
- Documenting user flows, data models, and API contracts
- Ensuring all decisions are captured (packages, patterns, file paths)
- Avoiding vague plans that lead to inconsistent code
- Planning offline-first, multi-platform, or enterprise Flutter apps

## Blueprint Plan Structure

A complete Blueprint includes these numbered sections:

### 1. Overview & Key Decisions

```markdown
# Mobile Task Manager

A cross-platform task management app with offline-first sync, categories, due dates, notifications, biometric auth, and dark/light theming.

## Key Decisions
- Targets: iOS 16+, Android API 26+ (Android 8.0+)
- Flutter 3.41+ / Dart 3.11+ (stable channel)
- Architecture: Feature-first Clean Architecture
- State management: Riverpod 3 with code generation
- Navigation: GoRouter with ShellRoute for bottom nav
- Local database: Drift (type-safe SQLite with migrations)
- Remote API: Dio with auth interceptor + retry
- Offline-first: local DB is source of truth; sync queue for pending changes
- Auth: JWT stored in flutter_secure_storage; biometric unlock via local_auth
- Theming: Material 3 with ColorScheme.fromSeed, system dark/light mode
- Code generation: freezed + json_serializable + riverpod_generator + build_runner
- Linting: very_good_analysis
- Testing: mocktail for mocks, bloc_test not needed (Riverpod), golden_toolkit for visual regression
```

### 2. User Flows

Document step-by-step interactions:

```markdown
## User Flows

### Onboarding / Login
1. App launches, checks flutter_secure_storage for JWT
2. If no token or token expired: navigate to /login
3. User enters email + password
4. On success: store JWT, navigate to /tasks
5. Optional: enable biometric unlock via local_auth

### Creating a Task
1. User taps FAB on TaskListScreen
2. Bottom sheet opens with task form:
   - Title (required, max 100 chars)
   - Description (optional, max 500 chars)
   - Category dropdown (from local categories)
   - Due date picker (optional, must be today or later)
   - Priority toggle buttons (low / medium / high)
3. User taps Save
4. Task saved to Drift DB immediately (offline-first)
5. Sync queue entry created for remote push
6. Snackbar: "Task created"

### Completing a Task
1. User swipes task right or taps checkbox
2. Optimistic update: task marked complete locally
3. Sync queue entry created
4. Undo snackbar shown for 5 seconds
5. If undo tapped: revert local state, remove sync entry

### Offline Sync
1. App detects connectivity via connectivity_plus
2. When online: process sync queue (FIFO)
3. For each pending operation: POST/PUT/DELETE to API
4. On success: mark sync entry as completed
5. On conflict (409): pull server version, prompt user to resolve
6. Pull new/updated tasks from server since last sync timestamp
```

### 3. Project Setup

Sequential commands for scaffolding:

```markdown
## Commands

flutter create --org com.example --platforms ios,android task_manager
cd task_manager

# Core dependencies
flutter pub add flutter_riverpod riverpod_annotation go_router dio
flutter pub add drift drift_flutter flutter_secure_storage
flutter pub add freezed_annotation json_annotation equatable
flutter pub add connectivity_plus local_auth flutter_local_notifications
flutter pub add cached_network_image google_fonts intl
flutter pub add envied logger

# Dev dependencies
flutter pub add --dev riverpod_generator build_runner freezed
flutter pub add --dev json_serializable drift_dev envied_generator
flutter pub add --dev very_good_analysis mocktail golden_toolkit

# Generate code
dart run build_runner build --delete-conflicting-outputs
```

### 4. Architecture & State Management

Specify architecture pattern and state management approach:

```markdown
## Architecture

Pattern: Feature-first Clean Architecture with Riverpod 3

### Layers
- Presentation: Pages, Widgets, Riverpod providers (ViewModels)
- Domain: Entities, Repository interfaces, Use cases (optional)
- Data: Repository implementations, Data sources, DTOs/Models

### Dependency Rule
Dependencies point inward. Domain has zero Flutter/package dependencies.
Presentation depends on Domain. Data depends on Domain.
Riverpod provides the glue (DI) without a service locator.

### State Management: Riverpod 3
- @riverpod annotation for all providers (code generation)
- AsyncNotifier for mutable async state (task lists, sync status)
- Provider for read-only dependencies (ApiClient, Database)
- Family providers for parameterized lookups (single task by ID)
- ref.watch for reactive rebuilds; ref.read for one-shot actions
- AsyncValue.when() for loading/data/error in every async widget
```

### 5. Data Models

Include exact attributes, relationships, and serialization:

```markdown
## Models

### Task
**Drift Table**: tasks

| Column         | Dart Type   | SQL Type         | Constraints                  |
|----------------|-------------|------------------|------------------------------|
| id             | String      | TEXT             | primary, UUID v4             |
| title          | String      | TEXT             | required, max 100            |
| description    | String?     | TEXT             | nullable                     |
| categoryId     | String?     | TEXT             | nullable, FK to categories   |
| priority       | Priority    | INTEGER          | enum mapped, default: medium |
| dueDate        | DateTime?   | INTEGER (epoch)  | nullable                     |
| isCompleted    | bool        | INTEGER (0/1)    | default: false               |
| completedAt    | DateTime?   | INTEGER (epoch)  | nullable                     |
| createdAt      | DateTime    | INTEGER (epoch)  | required                     |
| updatedAt      | DateTime    | INTEGER (epoch)  | required                     |
| syncStatus     | SyncStatus  | INTEGER          | enum mapped, default: synced |

### Category
**Drift Table**: categories

| Column   | Dart Type | SQL Type | Constraints       |
|----------|-----------|----------|--------------------|
| id       | String    | TEXT     | primary, UUID v4   |
| name     | String    | TEXT     | required, unique   |
| color    | int       | INTEGER  | ARGB color value   |
| icon     | String    | TEXT     | Material icon name |

### SyncQueueEntry
**Drift Table**: sync_queue

| Column     | Dart Type   | SQL Type        | Constraints               |
|------------|-------------|-----------------|---------------------------|
| id         | int         | INTEGER         | autoIncrement, primary    |
| entityType | String      | TEXT            | 'task' or 'category'     |
| entityId   | String      | TEXT            | UUID of the entity        |
| operation  | String      | TEXT            | 'create','update','delete'|
| payload    | String      | TEXT            | JSON-encoded body         |
| createdAt  | DateTime    | INTEGER (epoch) | required                  |
| retryCount | int         | INTEGER         | default: 0                |
```

### 6. Repository Layer

```markdown
## Repositories

### TaskRepository (interface)
**Location**: lib/features/tasks/domain/repositories/task_repository.dart

Methods:
- Stream<List<Task>> watchTasks({TaskFilter? filter})
- Future<Task> getTask(String id)
- Future<void> createTask(Task task)
- Future<void> updateTask(Task task)
- Future<void> deleteTask(String id)
- Future<void> toggleComplete(String id)

### TaskRepositoryImpl
**Location**: lib/features/tasks/data/repositories/task_repository_impl.dart
**Depends on**: TaskLocalDataSource, SyncQueueDataSource

Behavior:
- All reads come from Drift (local DB)
- All writes go to Drift first, then enqueue sync entry
- No direct API calls; sync service handles remote push/pull

### SyncService
**Location**: lib/core/sync/sync_service.dart
**Depends on**: SyncQueueDataSource, ApiClient, ConnectivityService

Behavior:
- Watches connectivity_plus stream
- When online: drain sync queue in order
- Exponential backoff on failure (max 3 retries)
- Pull remote changes after push completes
- Emit SyncState (idle, syncing, error) via Riverpod provider
```

### 7. Navigation & Routing

```markdown
## Navigation

### GoRouter Configuration
**Location**: lib/app/router.dart

Routes:
| Path               | Screen              | Auth Required | Shell |
|--------------------|---------------------|---------------|-------|
| /login             | LoginScreen         | No            | No    |
| /tasks             | TaskListScreen      | Yes           | Yes   |
| /tasks/:id         | TaskDetailScreen    | Yes           | No    |
| /tasks/create      | TaskFormScreen      | Yes           | No    |
| /tasks/:id/edit    | TaskFormScreen      | Yes           | No    |
| /categories        | CategoryListScreen  | Yes           | Yes   |
| /settings          | SettingsScreen      | Yes           | Yes   |

### ShellRoute
Bottom NavigationBar with 3 destinations:
- Tasks (icon: check_circle_outline)
- Categories (icon: label_outline)
- Settings (icon: settings_outlined)

### Auth Redirect
Global redirect checks authProvider. If not authenticated and path != /login, redirect to /login.
If authenticated and path == /login, redirect to /tasks.
```

### 8. UI Components

```markdown
## Screens & Widgets

### TaskListScreen
- AppBar with search toggle and filter chip bar
- Filter chips: All, Today, Upcoming, Completed
- ListView.builder with TaskCard widgets
- FAB: navigate to /tasks/create
- Swipe-to-complete (Dismissible), swipe-to-delete with confirmation
- Pull-to-refresh triggers sync
- Empty state widget when no tasks match filter

### TaskCard (widget)
- Leading: priority color indicator (vertical bar)
- Title + optional due date chip
- Category badge (colored dot + name)
- Trailing: checkbox for completion toggle
- Tap: navigate to /tasks/:id

### TaskFormScreen
- Shared for create and edit (receives optional Task)
- Form fields: title (TextFormField), description (TextFormField multiline),
  category (DropdownButtonFormField), dueDate (DatePicker), priority (SegmentedButton)
- Validation: title required and <= 100 chars; dueDate >= today if set
- Save button in AppBar

### TaskDetailScreen
- Hero animation on task title from TaskCard
- Full task details with edit/delete actions in AppBar
- Completion toggle button

### CategoryListScreen
- ReorderableListView for drag-to-reorder
- Each tile shows color dot, icon, name, task count
- Slidable for edit/delete
- FAB to add category via dialog

### SettingsScreen
- Theme mode selector (system/light/dark)
- Biometric toggle
- Sync status indicator
- Clear local data button (with confirmation)
- App version info
```

### 9. Platform Integration

```markdown
## Platform Integration

### Notifications (flutter_local_notifications)
- Schedule due date reminders at 9:00 AM on due date
- When task created/updated with dueDate: schedule notification
- When task completed or dueDate removed: cancel notification
- Android: default channel "Task Reminders", importance: high
- iOS: request provisional permission on first task with due date

### Biometric Auth (local_auth)
- Settings toggle to enable/disable
- When enabled: check on app resume (AppLifecycleListener)
- Supported: fingerprint, face ID, device PIN fallback
- Store biometric preference in shared_preferences (not secure storage)

### Connectivity (connectivity_plus)
- Monitor via stream in SyncService
- Show offline banner (Material Banner) when disconnected
- Auto-trigger sync when connectivity restored
```

### 10. Theming

```markdown
## Theming

### Color Scheme
Seed color: Color(0xFF4A6CF7) (vibrant blue)
Generated via ColorScheme.fromSeed for both light and dark

### ThemeData Configuration
**Location**: lib/core/theme/app_theme.dart

- useMaterial3: true
- Text theme: GoogleFonts.interTextTheme()
- Card: elevation 0, border radius 12, surfaceContainerLow
- AppBar: surface color, no elevation, onSurface foreground
- FAB: primaryContainer color
- InputDecoration: OutlineInputBorder with border radius 8
- SegmentedButton: used for priority selector

### Priority Colors
| Priority | Light Mode         | Dark Mode          |
|----------|--------------------|--------------------|
| Low      | Colors.green       | Colors.green[300]  |
| Medium   | Colors.orange      | Colors.orange[300] |
| High     | Colors.red         | Colors.red[300]    |

### Responsive Breakpoints
| Device  | Width    | Layout                        |
|---------|----------|-------------------------------|
| Mobile  | < 600    | Single column, bottom nav     |
| Tablet  | 600-839  | Two column master-detail      |
| Desktop | >= 840   | NavigationRail + expanded view|
```

### 11. Testing Strategy

```markdown
## Testing

### Unit Tests (~50%)
- TaskRepositoryImpl: verify local-first behavior, sync queue creation
- SyncService: verify queue processing, retry logic, conflict handling
- Entities: verify copyWith, equality, computed properties
- Providers: verify state transitions with ProviderContainer overrides

### Widget Tests (~30%)
- TaskCard: renders title, category, priority indicator, due date
- TaskFormScreen: validates required fields, date constraints
- TaskListScreen: shows empty state, renders list, swipe actions
- Theme: light/dark mode renders correctly

### Integration Tests (~15%)
- Full task CRUD flow: create, read, update, complete, delete
- Offline mode: create tasks offline, verify sync on reconnect
- Auth flow: login, access protected screen, logout

### Golden Tests (~5%)
- TaskCard in all priority variants (light + dark)
- Empty state screen
- TaskListScreen with sample data

### Test Packages
- mocktail: mock repositories and data sources
- golden_toolkit: visual regression
- ProviderContainer with overrides for Riverpod testing
```

### 12. Build & Deployment

```markdown
## Build & Deployment

### Flavors
| Flavor  | Entry Point         | Bundle Suffix | API Base URL                    |
|---------|---------------------|---------------|----------------------------------|
| dev     | lib/main_dev.dart   | .dev          | https://dev-api.example.com/v1   |
| staging | lib/main_staging.dart| .staging     | https://staging-api.example.com/v1|
| prod    | lib/main_prod.dart  | (none)        | https://api.example.com/v1       |

### Environment Variables (envied)
- API_BASE_URL: per-flavor API endpoint
- API_KEY: compile-time obfuscated key

### CI (GitHub Actions)
- On push/PR: flutter analyze, flutter test --coverage, build APK
- On tag: build release APK + IPA, upload to Play Store / TestFlight

### Release Build
flutter build apk --release --obfuscate --split-debug-info=build/debug-info/ --flavor prod -t lib/main_prod.dart
flutter build ios --release --obfuscate --split-debug-info=build/debug-info/ --flavor prod -t lib/main_prod.dart
```

### 13. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Fresh install: login screen appears
2. [ ] Login with valid credentials: navigates to task list
3. [ ] Create task with all fields: appears in list
4. [ ] Edit task: changes reflected immediately
5. [ ] Mark task complete: checkbox, strikethrough, completedAt set
6. [ ] Undo complete: reverts within 5 seconds
7. [ ] Delete task with confirmation: removed from list
8. [ ] Filter tasks: All / Today / Upcoming / Completed
9. [ ] Search tasks by title
10. [ ] Create/edit/delete category
11. [ ] Airplane mode: create tasks, verify offline banner
12. [ ] Reconnect: sync completes, remote changes pulled
13. [ ] Toggle dark mode in settings
14. [ ] Enable biometric auth, background app, resume: biometric prompt
15. [ ] Due date notification fires at scheduled time
16. [ ] Pull-to-refresh triggers sync

### Automated
flutter analyze
flutter test --coverage
flutter test --tags=golden --update-goldens  # (first run only)
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns.

**VAGUE PLAN (Before Blueprint)**

```markdown
## Task Manager App
- Task list with CRUD
- Categories
- Offline support
- Notifications
- Dark mode
```

**Problems:**
- No architecture decision (BLoC? Riverpod? setState?)
- No offline strategy (local-first? cache? which database?)
- No navigation structure or auth flow
- No data model definitions (what fields? types? constraints?)
- No package selections
- No file paths or project structure
- No sync conflict resolution
- No testing approach

**BLUEPRINT (Implementation-Ready)**

**Task Entity**
**Location**: `lib/features/tasks/domain/entities/task.dart`
**Code gen**: freezed with JSON serialization

```dart
@freezed
class Task with _$Task {
  const factory Task({
    required String id,
    required String title,
    String? description,
    String? categoryId,
    @Default(Priority.medium) Priority priority,
    DateTime? dueDate,
    @Default(false) bool isCompleted,
    DateTime? completedAt,
    required DateTime createdAt,
    required DateTime updatedAt,
    @Default(SyncStatus.synced) SyncStatus syncStatus,
  }) = _Task;

  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);
}
```

**Priority Enum**
**Location**: `lib/features/tasks/domain/entities/priority.dart`

```dart
enum Priority {
  low,
  medium,
  high;

  String get label => switch (this) {
    Priority.low => 'Low',
    Priority.medium => 'Medium',
    Priority.high => 'High',
  };

  Color color(BuildContext context) => switch (this) {
    Priority.low => Colors.green,
    Priority.medium => Colors.orange,
    Priority.high => Colors.red,
  };

  int get sortOrder => switch (this) {
    Priority.high => 0,
    Priority.medium => 1,
    Priority.low => 2,
  };
}
```

**Drift Table Definition**
**Location**: `lib/core/database/tables/tasks_table.dart`

```dart
class Tasks extends Table {
  TextColumn get id => text()();
  TextColumn get title => text().withLength(min: 1, max: 100)();
  TextColumn get description => text().nullable()();
  TextColumn get categoryId => text().nullable().references(Categories, #id)();
  IntColumn get priority => intEnum<Priority>()();
  DateTimeColumn get dueDate => dateTime().nullable()();
  BoolColumn get isCompleted => boolean().withDefault(const Constant(false))();
  DateTimeColumn get completedAt => dateTime().nullable()();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  IntColumn get syncStatus => intEnum<SyncStatus>()();

  @override
  Set<Column> get primaryKey => {id};
}
```

**Task Repository Provider**
**Location**: `lib/features/tasks/presentation/providers/task_providers.dart`

```dart
@riverpod
TaskRepository taskRepository(TaskRepositoryRef ref) {
  return TaskRepositoryImpl(
    localDataSource: ref.watch(taskLocalDataSourceProvider),
    syncQueue: ref.watch(syncQueueDataSourceProvider),
  );
}

@riverpod
class TaskListNotifier extends _$TaskListNotifier {
  @override
  Stream<List<Task>> build({TaskFilter? filter}) {
    final repository = ref.watch(taskRepositoryProvider);
    return repository.watchTasks(filter: filter);
  }

  Future<void> createTask(Task task) async {
    final repository = ref.read(taskRepositoryProvider);
    await repository.createTask(task);
  }

  Future<void> toggleComplete(String taskId) async {
    final repository = ref.read(taskRepositoryProvider);
    await repository.toggleComplete(taskId);
  }

  Future<void> deleteTask(String taskId) async {
    final repository = ref.read(taskRepositoryProvider);
    await repository.deleteTask(taskId);
  }
}
```

**GoRouter Configuration**
**Location**: `lib/app/router.dart`

```dart
@riverpod
GoRouter router(RouterRef ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/tasks',
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isLoginRoute = state.matchedLocation == '/login';

      if (!isLoggedIn && !isLoginRoute) return '/login';
      if (isLoggedIn && isLoginRoute) return '/tasks';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(
            path: '/tasks',
            builder: (context, state) => const TaskListScreen(),
            routes: [
              GoRoute(
                path: 'create',
                builder: (context, state) => const TaskFormScreen(),
              ),
              GoRoute(
                path: ':id',
                builder: (context, state) => TaskDetailScreen(
                  taskId: state.pathParameters['id']!,
                ),
              ),
              GoRoute(
                path: ':id/edit',
                builder: (context, state) => TaskFormScreen(
                  taskId: state.pathParameters['id'],
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/categories',
            builder: (context, state) => const CategoryListScreen(),
          ),
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),
    ],
  );
}
```

## Decision Trees

### State Management Selection

| Criteria | Riverpod 3 | BLoC 8+ | Provider | Signals |
|----------|-----------|---------|----------|---------|
| **Choose when** | Most projects (default) | Enterprise, strict event audit | Simple apps, beginners | Real-time dashboards |
| Team size | Any | 5+ devs | Solo / 1-2 | Any |
| Boilerplate | Low (code gen) | High (events + states) | Low | Very low |
| Async support | Excellent (AsyncNotifier) | Excellent (stream-based) | Good | Limited |
| Testability | Excellent (ProviderContainer) | Excellent (bloc_test) | Good | Good |
| Learning curve | Medium | High | Low | Low |
| DI built-in | Yes | No (needs get_it) | Yes (scoped) | No |
| Code generation | Yes (@riverpod) | No | No | No |

**Default choice**: Riverpod 3 for new projects. BLoC for teams already invested in it or needing strict event traceability.

### Architecture Pattern Selection

| Factor | MVVM (Flutter Official) | Clean Architecture | Feature-First Clean | Simple (setState) |
|--------|------------------------|-------------------|--------------------|--------------------|
| **Choose when** | Official compliance | Enterprise, multi-team | Production apps (default) | Prototypes |
| App complexity | Any | High | Medium-High | Low |
| Number of features | Any | 10+ | 3+ | 1-3 |
| Team size | Any | 5+ | 2+ | Solo |
| Testability | High | Very high | Very high | Low |
| Initial setup cost | Low | High | Medium | None |

**Default choice**: Feature-first Clean Architecture. It balances modularity with pragmatism.

### Navigation Package Selection

| Factor | GoRouter | AutoRoute | Navigator 2.0 (raw) |
|--------|----------|-----------|---------------------|
| **Choose when** | Most projects (default) | Large apps, type-safe routes | Custom navigation logic |
| Deep links | Excellent | Good | Manual |
| Web support | Excellent | Good | Manual |
| Code generation | No | Yes (required) | No |
| ShellRoute support | Built-in | Via nested navigation | Manual |
| Type-safe args | Partial (string params) | Full (generated classes) | Manual |
| Redirect guards | Built-in | Via route guards | Manual |

**Default choice**: GoRouter. Use AutoRoute only for large apps needing compile-time route verification.

### Local Database Selection

| Factor | Drift | Isar | Hive | shared_preferences |
|--------|-------|------|------|-------------------|
| **Choose when** | Structured data, migrations | Large NoSQL datasets | Simple caching | Flags and settings |
| Query complexity | Full SQL | Indexed NoSQL | Key-value only | Key-value only |
| Migrations | Built-in, type-safe | Schema-based | N/A | N/A |
| Reactive streams | Yes (watch queries) | Yes (watch queries) | Yes (box.watch) | No |
| Code generation | Yes (build_runner) | Yes (build_runner) | Yes (type adapters) | No |
| Data size | Any | Large datasets | Small-medium | Tiny |

**Default choice**: Drift for app data. shared_preferences for simple settings. flutter_secure_storage for secrets.

## Package Selection Guide

### Recommended Stack (2025-2026)

**State Management**

| Package | Version | Purpose |
|---------|---------|---------|
| flutter_riverpod | ^2.6.1 | Widget integration |
| riverpod_annotation | ^2.6.1 | @riverpod annotations |
| riverpod_generator | ^2.4.0 | Code generation (dev) |

**Navigation**

| Package | Version | Purpose |
|---------|---------|---------|
| go_router | ^14.0.0 | Declarative routing |

**Networking**

| Package | Version | Purpose |
|---------|---------|---------|
| dio | ^5.7.0 | HTTP client with interceptors |
| retrofit | ^4.4.0 | Type-safe API (optional, large projects) |

**Data & Storage**

| Package | Version | Purpose |
|---------|---------|---------|
| drift | ^2.22.0 | Type-safe SQLite ORM |
| drift_flutter | ^0.2.0 | Flutter bindings for Drift |
| flutter_secure_storage | ^9.2.0 | Secure credential storage |
| shared_preferences | ^2.3.0 | Simple key-value settings |

**Code Generation**

| Package | Version | Purpose |
|---------|---------|---------|
| freezed | ^2.5.0 | Immutable classes, sealed unions |
| freezed_annotation | ^2.4.0 | @freezed annotations |
| json_serializable | ^6.8.0 | JSON serialization |
| json_annotation | ^4.9.0 | @JsonKey annotations |
| build_runner | ^2.4.0 | Orchestrates code gen |

**Platform Integration**

| Package | Version | Purpose |
|---------|---------|---------|
| local_auth | ^2.3.0 | Biometric authentication |
| flutter_local_notifications | ^18.0.0 | Scheduled notifications |
| connectivity_plus | ^6.1.0 | Network connectivity monitoring |

**UI & Theming**

| Package | Version | Purpose |
|---------|---------|---------|
| google_fonts | ^6.2.0 | Custom font loading |
| cached_network_image | ^3.4.0 | Image caching |

**Quality & DevEx**

| Package | Version | Purpose |
|---------|---------|---------|
| very_good_analysis | ^7.0.0 | Strict lint rules |
| envied | ^1.0.0 | Compile-time env vars |
| logger | ^2.5.0 | Structured logging |

**Testing**

| Package | Version | Purpose |
|---------|---------|---------|
| mocktail | ^1.0.0 | Mock classes without codegen |
| golden_toolkit | ^0.15.0 | Visual regression tests |

### Packages to Avoid

| Package | Reason | Alternative |
|---------|--------|-------------|
| GetX | Poor testability, single maintainer, hides BuildContext | Riverpod or BLoC |
| provider (for complex apps) | Limited scalability, no code gen | Riverpod 3 |
| http (for complex apps) | No interceptors, no retry, no cancel | Dio |
| sqflite (for new projects) | No type safety, manual SQL | Drift |
| Hive (for new projects) | Maintenance mode, author recommends Isar | Drift or Isar |

## Performance Optimization Rules

### Widget Rebuild Rules

| Rule | Bad | Good |
|------|-----|------|
| Use const constructors | `Text('Hello')` | `const Text('Hello')` |
| Break down large widgets | One 500-line build() | Extract sub-widgets |
| Use ListView.builder | `ListView(children: items.map(...).toList())` | `ListView.builder(itemBuilder: ...)` |
| Scope state rebuilds | `ref.watch(cartProvider)` rebuilds on any change | `ref.watch(cartProvider.select((c) => c.total))` |
| Use RepaintBoundary | Animated widget repaints parent | `RepaintBoundary(child: AnimatedWidget())` |
| Prefer StatelessWidget | StatefulWidget with no local state | StatelessWidget or ConsumerWidget |

### Memory Rules

| Rule | What to Check | Fix |
|------|--------------|-----|
| Dispose controllers | TextEditingController, ScrollController, AnimationController | Always dispose in State.dispose() |
| Cancel subscriptions | StreamSubscription, Timer | Cancel in dispose() or ref.onDispose() |
| Use ref.onDispose | Riverpod providers with timers/streams | `ref.onDispose(() => timer.cancel())` |
| Size images | Full-resolution images decoded into memory | Use `memCacheWidth` / `memCacheHeight` |
| Avoid closures in build | `onPressed: () => doThing()` creates new instance each build | Extract to method or use const callbacks |

### Performance Targets

| Metric | Target |
|--------|--------|
| Frame rate | 60fps sustained (120fps on ProMotion devices) |
| Cold start | < 2 seconds |
| Widget rebuilds | Reduce 60-80% with const + select |
| App size (APK) | < 15MB for simple apps |
| Memory | No leaks from undisposed controllers/streams |

### Profiling Commands

```bash
# Profile mode (accurate performance, no debug overhead)
flutter run --profile

# Analyze app size
flutter build apk --analyze-size

# Run DevTools
flutter pub global activate devtools
dart devtools
```

## Common Anti-Patterns

### Architecture Anti-Patterns

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| God widget | Single widget with 500+ lines, mixed concerns | Extract into screen + smaller widgets |
| Business logic in UI | onPressed handler does API call + validation | Move to Notifier/UseCase, UI only dispatches |
| Tight coupling to packages | `Dio` imported directly in presentation | Abstract behind repository interface |
| Skipping domain layer | Data models used directly in UI | Create domain entities; map at data layer boundary |
| No dependency injection | `final repo = TaskRepositoryImpl()` | Use Riverpod providers for all dependencies |
| setState for shared state | setState in parent, pass callbacks down | Use Riverpod/BLoC for cross-widget state |

### Code Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Missing `const` | Up to 70% more widget rebuilds | Add const to every eligible constructor and widget |
| `ListView` without builder | Builds all items, OOM on large lists | Use `ListView.builder` or `ListView.separated` |
| Heavy work in `build()` | Blocks UI thread, causes jank | Move to provider/service, use FutureBuilder or AsyncValue |
| `setState` after `await` without mounted check | Crash if widget unmounted | Check `if (mounted)` before setState; or use Riverpod |
| Deeply nested widget trees | Hard to read, hard to optimize | Extract named widgets, max 3-4 levels of nesting |
| String-based navigation | `Navigator.pushNamed('/tasks')` | Use GoRouter with typed path constants |
| Catching generic Exception | Swallows all errors silently | Catch specific exceptions, log others |
| Not using pattern matching | Long if/else chains for sealed classes | Use `switch` expression with exhaustive matching |

### Testing Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No tests | Regressions on every change | Minimum 50% unit + 30% widget test coverage |
| Testing implementation | Tests break on refactor | Test behavior (output given input), not internal state |
| No mocking | Tests hit real API/DB | Use mocktail mocks; override Riverpod providers |
| Testing only happy path | Misses edge cases and errors | Test error states, empty states, boundary values |
| Profiling in debug mode | Debug is 10x slower, misleading metrics | Always profile with `--profile` flag |

## Common Code Patterns

### Freezed Data Class with JSON

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'task.freezed.dart';
part 'task.g.dart';

@freezed
class Task with _$Task {
  const factory Task({
    required String id,
    required String title,
    String? description,
    String? categoryId,
    @Default(Priority.medium) Priority priority,
    DateTime? dueDate,
    @Default(false) bool isCompleted,
    DateTime? completedAt,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Task;

  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);
}
```

### Sealed Class for State

```dart
sealed class SyncState {
  const SyncState();
}

class SyncIdle extends SyncState {
  const SyncIdle();
}

class SyncInProgress extends SyncState {
  final int pending;
  final int total;
  const SyncInProgress({required this.pending, required this.total});
}

class SyncCompleted extends SyncState {
  final int syncedCount;
  const SyncCompleted({required this.syncedCount});
}

class SyncError extends SyncState {
  final String message;
  final int failedCount;
  const SyncError({required this.message, required this.failedCount});
}
```

### Riverpod AsyncNotifier (CRUD)

```dart
@riverpod
class TaskListNotifier extends _$TaskListNotifier {
  @override
  Future<List<Task>> build() async {
    final repository = ref.watch(taskRepositoryProvider);
    return repository.getTasks();
  }

  Future<void> addTask(Task task) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(taskRepositoryProvider).createTask(task);
      return ref.read(taskRepositoryProvider).getTasks();
    });
  }

  Future<void> deleteTask(String id) async {
    // Optimistic delete
    final previous = state.valueOrNull ?? [];
    state = AsyncData(previous.where((t) => t.id != id).toList());

    try {
      await ref.read(taskRepositoryProvider).deleteTask(id);
    } catch (e) {
      state = AsyncData(previous); // Rollback
      rethrow;
    }
  }
}
```

### Riverpod Stream Provider (Reactive Drift Queries)

```dart
@riverpod
Stream<List<Task>> taskStream(TaskStreamRef ref) {
  final db = ref.watch(databaseProvider);
  return db.watchAllTasks();
}
```

### Riverpod Family Provider (Single Item)

```dart
@riverpod
Future<Task> taskById(TaskByIdRef ref, String taskId) async {
  final repository = ref.watch(taskRepositoryProvider);
  return repository.getTask(taskId);
}

// Usage in widget:
final taskAsync = ref.watch(taskByIdProvider(taskId));
```

### GoRouter with Auth Guard

```dart
GoRouter(
  redirect: (context, state) {
    final isLoggedIn = ref.read(authProvider).isAuthenticated;
    final isLoginRoute = state.matchedLocation == '/login';

    if (!isLoggedIn && !isLoginRoute) return '/login';
    if (isLoggedIn && isLoginRoute) return '/tasks';
    return null;
  },
  routes: [/* ... */],
);
```

### ShellRoute with Bottom Navigation

```dart
ShellRoute(
  builder: (context, state, child) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _calculateIndex(state.matchedLocation),
        onDestinationSelected: (index) {
          switch (index) {
            case 0: context.go('/tasks');
            case 1: context.go('/categories');
            case 2: context.go('/settings');
          }
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.check_circle_outline), label: 'Tasks'),
          NavigationDestination(icon: Icon(Icons.label_outline), label: 'Categories'),
          NavigationDestination(icon: Icon(Icons.settings_outlined), label: 'Settings'),
        ],
      ),
    );
  },
  routes: [/* task, category, settings routes */],
)
```

### Dio Client with Auth Interceptor

```dart
class ApiClient {
  late final Dio _dio;

  ApiClient({required String baseUrl, required SecureStorage secureStorage}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.addAll([
      AuthInterceptor(secureStorage: secureStorage, dio: _dio),
      LogInterceptor(requestBody: true, responseBody: true),
    ]);
  }

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? queryParameters}) =>
      _dio.get<T>(path, queryParameters: queryParameters);

  Future<Response<T>> post<T>(String path, {Object? data}) =>
      _dio.post<T>(path, data: data);

  Future<Response<T>> put<T>(String path, {Object? data}) =>
      _dio.put<T>(path, data: data);

  Future<Response<T>> delete<T>(String path) =>
      _dio.delete<T>(path);
}
```

### Auth Interceptor with Token Refresh

```dart
class AuthInterceptor extends Interceptor {
  final SecureStorage _secureStorage;
  final Dio _dio;

  AuthInterceptor({required SecureStorage secureStorage, required Dio dio})
      : _secureStorage = secureStorage,
        _dio = dio;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _secureStorage.read('access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      try {
        final refreshToken = await _secureStorage.read('refresh_token');
        final response = await _dio.post('/auth/refresh', data: {'token': refreshToken});
        final newToken = response.data['access_token'] as String;
        await _secureStorage.write('access_token', newToken);

        // Retry original request
        final retryResponse = await _dio.fetch(err.requestOptions
          ..headers['Authorization'] = 'Bearer $newToken');
        handler.resolve(retryResponse);
      } catch (e) {
        handler.reject(err);
      }
    } else {
      handler.next(err);
    }
  }
}
```

### Drift Database Definition

```dart
@DriftDatabase(tables: [Tasks, Categories, SyncQueue])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (m) => m.createAll(),
    onUpgrade: (m, from, to) async {
      // Add migration steps as schema evolves
    },
  );

  // Reactive queries
  Stream<List<TaskData>> watchAllTasks() => select(tasks).watch();

  Stream<List<TaskData>> watchTasksByFilter(TaskFilter filter) {
    final query = select(tasks);
    switch (filter) {
      case TaskFilter.today:
        final now = DateTime.now();
        final startOfDay = DateTime(now.year, now.month, now.day);
        final endOfDay = startOfDay.add(const Duration(days: 1));
        query.where((t) => t.dueDate.isBetweenValues(startOfDay, endOfDay));
      case TaskFilter.upcoming:
        query.where((t) => t.dueDate.isBiggerThanValue(DateTime.now()));
      case TaskFilter.completed:
        query.where((t) => t.isCompleted.equals(true));
      case TaskFilter.all:
        break;
    }
    return query.watch();
  }

  Future<void> insertTask(TasksCompanion task) => into(tasks).insert(task);
  Future<void> updateTask(TasksCompanion task) => (update(tasks)
    ..where((t) => t.id.equals(task.id.value)))
    .write(task);
  Future<void> deleteTaskById(String id) =>
    (delete(tasks)..where((t) => t.id.equals(id))).go();
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'task_manager.db'));
    return NativeDatabase.createInBackground(file);
  });
}
```

### Error Handling with Sealed Classes

```dart
sealed class AppException implements Exception {
  final String message;
  const AppException(this.message);
}

class NetworkException extends AppException {
  const NetworkException(super.message);
}

class AuthException extends AppException {
  const AuthException(super.message);
}

class ServerException extends AppException {
  final int statusCode;
  const ServerException(this.statusCode) : super('Server error: $statusCode');
}

class CacheException extends AppException {
  const CacheException(super.message);
}

// Map Dio errors to domain exceptions
AppException mapDioException(DioException e) => switch (e.type) {
  DioExceptionType.connectionTimeout => const NetworkException('Connection timeout'),
  DioExceptionType.receiveTimeout => const NetworkException('Receive timeout'),
  DioExceptionType.badResponse => switch (e.response?.statusCode) {
    401 => const AuthException('Unauthorized'),
    403 => const AuthException('Forbidden'),
    404 => const NetworkException('Not found'),
    _ => ServerException(e.response?.statusCode ?? 0),
  },
  _ => NetworkException(e.message ?? 'Network error'),
};
```

### AsyncValue Pattern in Widget

```dart
class TaskListScreen extends ConsumerWidget {
  const TaskListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasksAsync = ref.watch(taskListNotifierProvider);

    return tasksAsync.when(
      data: (tasks) => tasks.isEmpty
          ? const EmptyTasksView()
          : ListView.builder(
              itemCount: tasks.length,
              itemBuilder: (context, index) => TaskCard(task: tasks[index]),
            ),
      loading: () => const TaskListSkeleton(),
      error: (error, _) => ErrorView(
        message: _mapError(error),
        onRetry: () => ref.invalidate(taskListNotifierProvider),
      ),
    );
  }

  String _mapError(Object error) => switch (error) {
    NetworkException(:final message) => message,
    AuthException() => 'Please log in again',
    _ => 'Something went wrong. Pull to refresh.',
  };
}
```

### Material 3 Theme Configuration

```dart
class AppTheme {
  static const _seedColor = Color(0xFF4A6CF7);

  static ThemeData light() => _buildTheme(Brightness.light);
  static ThemeData dark() => _buildTheme(Brightness.dark);

  static ThemeData _buildTheme(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: GoogleFonts.interTextTheme(),
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.onSurface,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        color: colorScheme.surfaceContainerLow,
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        filled: true,
        fillColor: colorScheme.surfaceContainerLowest,
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: colorScheme.primaryContainer,
        foregroundColor: colorScheme.onPrimaryContainer,
      ),
    );
  }
}
```

### Widget Test with Riverpod Override

```dart
void main() {
  group('TaskListScreen', () {
    testWidgets('shows empty state when no tasks', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            taskListNotifierProvider.overrideWith(
              () => FakeTaskListNotifier([]),
            ),
          ],
          child: const MaterialApp(home: TaskListScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(EmptyTasksView), findsOneWidget);
    });

    testWidgets('renders task cards when data exists', (tester) async {
      final tasks = [
        Task(id: '1', title: 'Buy groceries', createdAt: DateTime.now(), updatedAt: DateTime.now()),
        Task(id: '2', title: 'Walk the dog', createdAt: DateTime.now(), updatedAt: DateTime.now()),
      ];

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            taskListNotifierProvider.overrideWith(
              () => FakeTaskListNotifier(tasks),
            ),
          ],
          child: const MaterialApp(home: TaskListScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Buy groceries'), findsOneWidget);
      expect(find.text('Walk the dog'), findsOneWidget);
    });
  });
}
```

### Repository Unit Test with Mocktail

```dart
class MockTaskLocalDataSource extends Mock implements TaskLocalDataSource {}
class MockSyncQueueDataSource extends Mock implements SyncQueueDataSource {}

void main() {
  late MockTaskLocalDataSource mockLocalSource;
  late MockSyncQueueDataSource mockSyncQueue;
  late TaskRepositoryImpl repository;

  setUp(() {
    mockLocalSource = MockTaskLocalDataSource();
    mockSyncQueue = MockSyncQueueDataSource();
    repository = TaskRepositoryImpl(
      localDataSource: mockLocalSource,
      syncQueue: mockSyncQueue,
    );
  });

  group('createTask', () {
    test('saves task to local DB and enqueues sync entry', () async {
      final task = Task(
        id: 'uuid-1',
        title: 'Test task',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      when(() => mockLocalSource.insertTask(any()))
          .thenAnswer((_) async {});
      when(() => mockSyncQueue.enqueue(any()))
          .thenAnswer((_) async {});

      await repository.createTask(task);

      verify(() => mockLocalSource.insertTask(any())).called(1);
      verify(() => mockSyncQueue.enqueue(
        any(that: isA<SyncQueueEntry>()
          .having((e) => e.operation, 'operation', 'create')
          .having((e) => e.entityId, 'entityId', 'uuid-1')),
      )).called(1);
    });
  });

  group('toggleComplete', () {
    test('marks task complete and records timestamp', () async {
      final task = Task(
        id: 'uuid-1',
        title: 'Test',
        isCompleted: false,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      when(() => mockLocalSource.getTask('uuid-1'))
          .thenAnswer((_) async => task);
      when(() => mockLocalSource.updateTask(any()))
          .thenAnswer((_) async {});
      when(() => mockSyncQueue.enqueue(any()))
          .thenAnswer((_) async {});

      await repository.toggleComplete('uuid-1');

      verify(() => mockLocalSource.updateTask(
        any(that: isA<Task>()
          .having((t) => t.isCompleted, 'isCompleted', true)
          .having((t) => t.completedAt, 'completedAt', isNotNull)),
      )).called(1);
    });
  });
}
```

### Golden Test

```dart
void main() {
  testGoldens('TaskCard renders all priority variants', (tester) async {
    final builder = GoldenBuilder.grid(columns: 3, widthToHeightRatio: 2.5)
      ..addScenario(
        'Low priority',
        TaskCard(task: Task(
          id: '1', title: 'Low task', priority: Priority.low,
          createdAt: DateTime(2026, 1, 1), updatedAt: DateTime(2026, 1, 1),
        )),
      )
      ..addScenario(
        'Medium priority',
        TaskCard(task: Task(
          id: '2', title: 'Medium task', priority: Priority.medium,
          createdAt: DateTime(2026, 1, 1), updatedAt: DateTime(2026, 1, 1),
        )),
      )
      ..addScenario(
        'High priority',
        TaskCard(task: Task(
          id: '3', title: 'High task', priority: Priority.high,
          dueDate: DateTime(2026, 2, 20),
          createdAt: DateTime(2026, 1, 1), updatedAt: DateTime(2026, 1, 1),
        )),
      );

    await tester.pumpWidgetBuilder(
      builder.build(),
      wrapper: materialAppWrapper(theme: AppTheme.light()),
    );
    await screenMatchesGolden(tester, 'task_card_priorities');
  });
}
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Entry Points (3)
- lib/main_dev.dart
- lib/main_staging.dart
- lib/main_prod.dart

### App Shell (3)
- lib/app/app.dart
- lib/app/router.dart
- lib/app/environment.dart

### Core — Database (2)
- lib/core/database/app_database.dart
- lib/core/database/app_database.g.dart

### Core — Database Tables (3)
- lib/core/database/tables/tasks_table.dart
- lib/core/database/tables/categories_table.dart
- lib/core/database/tables/sync_queue_table.dart

### Core — Network (3)
- lib/core/network/api_client.dart
- lib/core/network/interceptors/auth_interceptor.dart
- lib/core/network/interceptors/retry_interceptor.dart

### Core — Sync (2)
- lib/core/sync/sync_service.dart
- lib/core/sync/sync_state.dart

### Core — Storage (1)
- lib/core/storage/secure_storage.dart

### Core — Theme (1)
- lib/core/theme/app_theme.dart

### Core — Errors (1)
- lib/core/errors/exceptions.dart

### Core — Utils (2)
- lib/core/utils/date_formatters.dart
- lib/core/utils/validators.dart

### Core — Widgets (3)
- lib/core/widgets/empty_state.dart
- lib/core/widgets/error_view.dart
- lib/core/widgets/loading_skeleton.dart

### Feature — Auth (8)
- lib/features/auth/data/datasources/auth_remote_source.dart
- lib/features/auth/data/models/auth_response_model.dart
- lib/features/auth/data/repositories/auth_repository_impl.dart
- lib/features/auth/domain/entities/user.dart
- lib/features/auth/domain/repositories/auth_repository.dart
- lib/features/auth/presentation/providers/auth_provider.dart
- lib/features/auth/presentation/screens/login_screen.dart
- lib/features/auth/presentation/widgets/login_form.dart

### Feature — Tasks (14)
- lib/features/tasks/data/datasources/task_local_source.dart
- lib/features/tasks/data/datasources/task_remote_source.dart
- lib/features/tasks/data/models/task_model.dart
- lib/features/tasks/data/repositories/task_repository_impl.dart
- lib/features/tasks/domain/entities/task.dart
- lib/features/tasks/domain/entities/priority.dart
- lib/features/tasks/domain/entities/task_filter.dart
- lib/features/tasks/domain/repositories/task_repository.dart
- lib/features/tasks/presentation/providers/task_providers.dart
- lib/features/tasks/presentation/screens/task_list_screen.dart
- lib/features/tasks/presentation/screens/task_detail_screen.dart
- lib/features/tasks/presentation/screens/task_form_screen.dart
- lib/features/tasks/presentation/widgets/task_card.dart
- lib/features/tasks/presentation/widgets/task_filter_bar.dart

### Feature — Categories (10)
- lib/features/categories/data/datasources/category_local_source.dart
- lib/features/categories/data/models/category_model.dart
- lib/features/categories/data/repositories/category_repository_impl.dart
- lib/features/categories/domain/entities/category.dart
- lib/features/categories/domain/repositories/category_repository.dart
- lib/features/categories/presentation/providers/category_providers.dart
- lib/features/categories/presentation/screens/category_list_screen.dart
- lib/features/categories/presentation/widgets/category_tile.dart
- lib/features/categories/presentation/widgets/category_form_dialog.dart
- lib/features/categories/presentation/widgets/category_picker.dart

### Feature — Settings (5)
- lib/features/settings/data/repositories/settings_repository_impl.dart
- lib/features/settings/domain/repositories/settings_repository.dart
- lib/features/settings/presentation/providers/settings_provider.dart
- lib/features/settings/presentation/screens/settings_screen.dart
- lib/features/settings/presentation/widgets/theme_selector.dart

### Feature — Notifications (3)
- lib/features/notifications/data/notification_service.dart
- lib/features/notifications/presentation/providers/notification_provider.dart
- lib/features/notifications/domain/notification_scheduler.dart

### Tests — Unit (5)
- test/features/tasks/data/repositories/task_repository_impl_test.dart
- test/features/auth/data/repositories/auth_repository_impl_test.dart
- test/core/sync/sync_service_test.dart
- test/features/tasks/domain/entities/task_test.dart
- test/features/tasks/domain/entities/priority_test.dart

### Tests — Widget (5)
- test/features/tasks/presentation/screens/task_list_screen_test.dart
- test/features/tasks/presentation/screens/task_form_screen_test.dart
- test/features/tasks/presentation/widgets/task_card_test.dart
- test/features/categories/presentation/screens/category_list_screen_test.dart
- test/features/settings/presentation/screens/settings_screen_test.dart

### Tests — Golden (2)
- test/goldens/task_card_test.dart
- test/goldens/empty_state_test.dart

### Tests — Integration (2)
- integration_test/task_crud_test.dart
- integration_test/offline_sync_test.dart

### Configuration (3)
- analysis_options.yaml
- .env.dev
- .env.prod

### Total: ~81 files
```

## Dart Language Features to Use

Prefer modern Dart 3+ features throughout the codebase:

| Feature | Use For | Example |
|---------|---------|---------|
| Sealed classes | State types, error types, result types | `sealed class AuthState {}` |
| Records | Multi-value returns | `(String, int) parseInput()` |
| Pattern matching | Switch expressions on types | `switch (state) { Success(:var data) => ... }` |
| Switch expressions | Inline mapping | `final label = switch (priority) { Priority.low => 'Low', ... };` |
| Class modifiers | API boundaries | `final class AppConfig {}` |
| Null-aware elements | Conditional list items | `[if (title != null) title]` |
| Wildcard variables | Unused parameters | `map.forEach((_, value) => ...)` |

## analysis_options.yaml Template

```yaml
include: package:very_good_analysis/analysis_options.yaml

analyzer:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
    - "**/*.drift.dart"
  errors:
    invalid_annotation_target: ignore

linter:
  rules:
    public_member_api_docs: false
    lines_longer_than_80_chars: false
    flutter_style_todos: false
```

## CI/CD Template (GitHub Actions)

```yaml
name: Flutter CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
          channel: stable
      - run: flutter pub get
      - run: dart analyze --fatal-infos
      - run: dart format --set-exit-if-changed .
      - run: flutter test --coverage

  build-android:
    needs: analyze-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
      - run: flutter pub get
      - run: flutter build apk --release --flavor prod -t lib/main_prod.dart

  build-ios:
    needs: analyze-and-test
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
      - run: flutter pub get
      - run: flutter build ios --release --no-codesign --flavor prod -t lib/main_prod.dart
```

## Best Practices

1. **Be explicit** - Include file paths, package versions, exact method signatures
2. **Specify every model field** - Column name, Dart type, SQL type, constraints
3. **Show complete code** - Not just names, but full configurations with imports
4. **Document offline strategy** - Local-first vs cache-first vs online-only
5. **Map every route** - Path, screen, auth requirement, shell membership
6. **Include user flows** - Step-by-step interactions for every feature
7. **Define error handling** - Sealed exception types, UI error mapping
8. **Specify state management** - Which provider type for each use case
9. **Plan sync conflicts** - How to detect and resolve server/local divergence
10. **Test at every layer** - Unit, widget, golden, integration proportions
11. **File inventory** - Categorized list of all files to be created
12. **Plan in order** - Models, then Domain, then Data, then Presentation, then Tests
13. **Verify Dart features** - Use sealed classes, pattern matching, records throughout
14. **Include CI/CD** - Analyze, test, build pipeline from day one

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| No architecture decision | Inconsistent patterns across features | Specify architecture + state management in section 1 |
| Missing package versions | Version conflicts during setup | Pin versions in pubspec.yaml section |
| Vague data models | "A task has some fields" | Full table with column, type, constraints |
| No offline strategy | App crashes or loses data offline | Define local-first or cache strategy explicitly |
| Missing sync conflict resolution | Silent data loss | Specify detection (409) + resolution (user prompt or last-write-wins) |
| No file paths | Agent creates files in wrong locations | Include full path for every file |
| Unspecified navigation | Routes invented during coding | Full route table with paths, screens, guards |
| No error handling plan | Generic "Something went wrong" | Sealed exceptions + per-screen error mapping |
| Testing as afterthought | No testable architecture | Plan test strategy alongside architecture |
| Missing code generation setup | Compilation errors on first build | Include build_runner commands in setup |
| Choosing GetX | Poor testability, maintenance risk | Use Riverpod or BLoC instead |
| No CI/CD | Manual, error-prone releases | Include GitHub Actions workflow in Blueprint |
