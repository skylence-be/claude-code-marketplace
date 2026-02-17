# Flutter / Dart Blueprint Best Practices Research

> Compiled from community best practices, official documentation, and developer blog posts (February 2026)

## Table of Contents

1. [Latest Flutter & Dart Versions](#1-latest-flutter--dart-versions)
2. [Dart 3 Language Features](#2-dart-3-language-features)
3. [Architecture Patterns](#3-architecture-patterns)
4. [State Management](#4-state-management)
5. [Project Structure](#5-project-structure)
6. [Navigation & Routing](#6-navigation--routing)
7. [Networking & API Layer](#7-networking--api-layer)
8. [Local Storage & Databases](#8-local-storage--databases)
9. [Testing Strategies](#9-testing-strategies)
10. [Performance Optimization](#10-performance-optimization)
11. [Platform-Specific Code](#11-platform-specific-code)
12. [CI/CD & DevOps](#12-cicd--devops)
13. [Code Generation](#13-code-generation)
14. [Theming & Design](#14-theming--design)
15. [Security](#15-security)
16. [Common Anti-Patterns](#16-common-anti-patterns)
17. [Community Conventions & Ecosystem](#17-community-conventions--ecosystem)

---

## 1. Latest Flutter & Dart Versions

### Current Stable (February 2026)

| Component | Version | Release Date |
|-----------|---------|--------------|
| **Flutter** | 3.41 | February 2026 |
| **Dart** | 3.11 | February 2026 |
| **Previous stable** | Flutter 3.38 / Dart 3.10 | November 2025 |

### Key 2025 Release Highlights

- **Flutter 3.29** (Feb 2025): Impeller became default rendering engine on iOS
- **Flutter 3.32** (May 2025, Google I/O): Ecosystem updates, new tooling
- **Flutter 3.35** (Aug 2025): Stateful hot reload for web became stable and enabled by default
- **Flutter 3.38** (Nov 2025): Impeller default on Android for API 29+ with Vulkan; Dart 3.10 with dot shorthands
- **Flutter 3.41** (Feb 2026): DevTools compiled with dart2wasm for performance; continued modularization of design libraries

### Impeller Rendering Engine

Impeller replaced Skia as Flutter's rendering engine, eliminating shader compilation jank through ahead-of-time shader compilation. Real-world results show e-commerce apps dropped from 12% frame drops on Skia to 1.5% on Impeller, with 30-50% reduction in jank frames during complex animations.

Sources:
- [Best Flutter Features in 2025 - DCM](https://dcm.dev/blog/2025/12/23/top-flutter-features-2025)
- [What's New in Flutter 3.41 - Flutter Blog](https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632)
- [Flutter 3.38 and Dart 3.10 - Foresight Mobile](https://foresightmobile.com/blog/flutter-3-38-dart-3-10-november-2025-update)
- [State of Flutter 2026](https://devnewsletter.com/p/state-of-flutter-2026/)

---

## 2. Dart 3 Language Features

### Core Features (Dart 3.0+)

**Records** - Efficient multi-value returns with type safety:
```dart
(String, int) getUserInfo() => ('Alice', 30);

// Named fields
({String name, int age}) getUserInfo() => (name: 'Alice', age: 30);
final user = getUserInfo();
print(user.name); // 'Alice'
```

**Pattern Matching** - Destructuring and matching in switch/if:
```dart
switch (shape) {
  case Circle(radius: var r) when r > 0:
    print('Circle with radius $r');
  case Rectangle(width: var w, height: var h):
    print('Rectangle: $w x $h');
}
```

**Sealed Classes** - Closed type hierarchies with exhaustive checking:
```dart
sealed class Result<T> {}
class Success<T> extends Result<T> { final T data; Success(this.data); }
class Failure<T> extends Result<T> { final String error; Failure(this.error); }

// Compiler enforces all cases are handled
String display(Result<String> result) => switch (result) {
  Success(data: var d) => 'Got: $d',
  Failure(error: var e) => 'Error: $e',
};
```

**Class Modifiers** - `base`, `interface`, `final`, `mixin`:
```dart
interface class Animal {}     // Can only be implemented, not extended
base class Vehicle {}         // Can only be extended, not implemented
final class Config {}         // Cannot be extended or implemented outside library
```

### Dart 3.7 (February 2025)
- **Wildcard variables**: `_` as non-binding local variable/parameter (no collisions)
- **Tall style formatter**: New dart format default
- Deprecated older web libraries in favor of `package:web` and `dart:js_interop`

### Dart 3.8 (May 2025)
- **Null-aware elements** for collections: easier conditional element insertion based on nullability
- `Iterable.withIterator`, `HttpClientBearerCredentials`

### Dart 3.9 (August 2025)
- Assumes null safety for type promotion, reachability, and definite assignment
- **Dart & Flutter MCP Server** introduced: bridge between IDE, CLI, codebase, and AI assistants

### Dart 3.10 (November 2025)
- **Dot shorthands** (`.`): more readable, less verbose code
- **Analyzer plugin system**: custom static analysis rules integrated into IDE
- **Build hooks**: now stable

### Dart 3.11 (February 2026)
- Performance improvements in the Dart analysis server (cached compiled analyzer plugin entry points)
- **Pub workspaces** support glob declarations for packages
- New `pub cache gc` command for disk space reclamation

### Macros Status (Cancelled)
Dart macros were cancelled in early 2025 due to unacceptable compilation performance. Instead, the team is shipping **augmentations**: the ability to split a class definition across multiple files using the `augment` keyword. This preserves the foundation for better code generation tools while keeping compilation fast.

Sources:
- [Best Dart Features 2025 - DCM](https://dcm.dev/blog/2025/12/20/top-dart-features-2025-years)
- [Announcing Dart 3.10](https://blog.dart.dev/announcing-dart-3-10-ea8b952b6088)
- [Announcing Dart 3.11](https://blog.dart.dev/announcing-dart-3-11-b6529be4203a)
- [Dart Language Evolution](https://dart.dev/resources/language/evolution)
- [Dart Patterns Official](https://dart.dev/language/patterns)

---

## 3. Architecture Patterns

### Architecture Selection Matrix

| Pattern | Best For | Complexity | Team Size | Testability |
|---------|----------|------------|-----------|-------------|
| **MVVM** (Flutter Official) | All app sizes, official recommendation | Medium | Any | High |
| **Clean Architecture** | Large-scale, enterprise apps | High | 5+ devs | Very High |
| **BLoC Pattern** | Enterprise, strict separation | High | 5+ devs | Very High |
| **Riverpod + Clean Arch** | Modern apps, compile-safe DI | Medium-High | 3+ devs | Very High |
| **Feature-First** | Modular apps with clear boundaries | Medium | 3+ devs | High |
| **Simple (setState)** | Prototypes, small apps | Low | Solo / 1-2 | Low |

### Flutter Official Architecture (MVVM)

Flutter's official architecture guidelines recommend **MVVM** in the UI layer with repositories and services in the data layer:

```
┌─────────────────────────────────┐
│          UI Layer (MVVM)        │
│  ┌─────────┐   ┌────────────┐  │
│  │  Views   │◄──│ ViewModels │  │
│  └─────────┘   └─────┬──────┘  │
└───────────────────────┼─────────┘
                        │
┌───────────────────────┼─────────┐
│        Data Layer               │
│  ┌──────────────┐  ┌─────────┐  │
│  │ Repositories  │──│Services │  │
│  └──────────────┘  └─────────┘  │
└─────────────────────────────────┘
```

- **Views**: Widget compositions describing how to present data; often a screen with a Scaffold
- **ViewModels**: Convert app data into UI State; one-to-one relationship with Views
- **Repositories**: Mediate between data sources and the domain/UI
- **Services**: Direct interaction with external APIs, databases, platform APIs

### Clean Architecture (Three-Layer)

```
┌────────────────────────────────────┐
│  Presentation Layer                │
│  (Widgets, Pages, BLoC/Cubit,     │
│   ViewModels, State)              │
├────────────────────────────────────┤
│  Domain Layer                      │
│  (Entities, Use Cases,            │
│   Repository Interfaces)          │
│  *** No external dependencies *** │
├────────────────────────────────────┤
│  Data Layer                        │
│  (Repository Implementations,     │
│   Data Sources, Models, DTOs)     │
└────────────────────────────────────┘
```

**Key principle**: The Domain layer is a pure Dart module with zero dependencies on Flutter or external packages. Dependencies point inward.

Sources:
- [Flutter App Architecture Guide (Official)](https://docs.flutter.dev/app-architecture/guide)
- [Flutter Architecture Case Study (Official)](https://docs.flutter.dev/app-architecture/case-study)
- [Flutter Architecture Recommendations (Official)](https://docs.flutter.dev/app-architecture/recommendations)
- [Flutter Architecture Patterns - f22labs](https://www.f22labs.com/blogs/flutter-architecture-patterns-bloc-provider-riverpod-and-more/)
- [Flutter App Architecture with Riverpod - Code With Andrea](https://codewithandrea.com/articles/flutter-app-architecture-riverpod-introduction/)

---

## 4. State Management

### State Management Decision Matrix

| Solution | Best For | Learning Curve | Boilerplate | Testability | Maturity |
|----------|----------|----------------|-------------|-------------|----------|
| **Riverpod 3** | Modern apps, most projects | Medium | Low (with codegen) | Excellent | High |
| **BLoC 8+** | Enterprise, strict architecture | High | High | Excellent | Very High |
| **Provider** | Simple apps, beginners | Low | Low | Good | High |
| **Signals** | Performance-critical, simple UIs | Low | Very Low | Good | Emerging |
| **GetX** | Prototypes only (avoid for production) | Low | Very Low | Poor | Declining |
| **setState** | Single-widget local state | None | None | N/A | Built-in |

### Riverpod 3.0 (Released September 2025)

Riverpod is the recommended modern state management solution for most Flutter projects:

```dart
// Using code generation (@riverpod annotation)
@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    return ref.watch(todoRepositoryProvider).fetchTodos();
  }

  Future<void> addTodo(Todo todo) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(todoRepositoryProvider).addTodo(todo);
      return ref.read(todoRepositoryProvider).fetchTodos();
    });
  }
}
```

**Key Riverpod 3.0 features**:
- Merged AutoDisposeNotifier and Notifier interfaces for cleaner API
- **Automatic retry with exponential backoff** for failed provider initialization
- **Offline persistence** (experimental): data caching and mutation operations
- **`ref.mounted`** property: check validity after async operations
- **Scoped providers**: active only in specific widget tree parts
- **Paused providers**: suspend updates for invisible widgets (performance boost)
- Enhanced code generation eliminating boilerplate

### BLoC 8.x

BLoC remains the gold standard for enterprise apps requiring strict separation:

```dart
// Events
sealed class AuthEvent {}
class LoginRequested extends AuthEvent {
  final String email;
  final String password;
  LoginRequested({required this.email, required this.password});
}

// States
sealed class AuthState {}
class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class AuthSuccess extends AuthState { final User user; AuthSuccess(this.user); }
class AuthFailure extends AuthState { final String error; AuthFailure(this.error); }

// BLoC
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc(this._authRepository) : super(AuthInitial()) {
    on<LoginRequested>(_onLoginRequested);
  }

  Future<void> _onLoginRequested(
    LoginRequested event, Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final user = await _authRepository.login(event.email, event.password);
      emit(AuthSuccess(user));
    } catch (e) {
      emit(AuthFailure(e.toString()));
    }
  }
}
```

**Key BLoC ecosystem packages**:
- `flutter_bloc`: Widget integration (BlocBuilder, BlocListener, BlocConsumer)
- `bloc_test`: Concise helpers for testing stream-based state
- `hydrated_bloc`: Persistent state across app restarts
- `replay_bloc`: Undo/redo support

### Why to Avoid GetX

- **Testing**: GetX navigation, dialogs, and snack bars use static context, making unit testing very difficult
- **Abstraction**: Hides important Flutter concepts (BuildContext, widget lifecycle) from developers
- **Dependency injection instability**: Controllers removed unexpectedly during hot reload
- **Maintenance**: Primarily maintained by a single developer without corporate backing
- **Documentation**: Only 35.1% of API elements have documentation comments
- **Community sentiment**: Even Flutter core team members have voiced concerns about GetX

### Signals (Emerging)

Signals provide fine-grained reactivity and surgical UI updates, ported from JavaScript frameworks (Vue, Preact, Angular) by Googler Rody Davis:

```dart
final count = signal(0);
final doubled = computed(() => count.value * 2);

// Widget rebuilds only when signal value changes
Watch((context) => Text('${doubled.value}'));
```

**Best for**: Stock trading apps, real-time dashboards, performance-critical UIs, low-end devices. Still maturing with limited async support and smaller community.

Sources:
- [What's New in Riverpod 3.0 (Official)](https://riverpod.dev/docs/whats_new)
- [Riverpod 3 New Features - DhiWise](https://www.dhiwise.com/post/riverpod-3-new-features-for-flutter-developers)
- [Flutter State Management 2025: Riverpod vs BLoC vs Signals - NuroByte](https://nurobyte.medium.com/flutter-state-management-in-2025-riverpod-vs-bloc-vs-signals-8569cbbef26f)
- [Flutter State Management Tool 2025 - Creole Studios](https://www.creolestudios.com/flutter-state-management-tool-comparison/)
- [BLoC Library](https://bloclibrary.dev/)
- [GetX Disadvantages - Medium](https://medium.com/@darwinmorocho/flutter-should-i-use-getx-832e0f3a00e8)

---

## 5. Project Structure

### Feature-First Clean Architecture (Recommended)

```
lib/
├── app/
│   ├── app.dart                    # Root MaterialApp/CupertinoApp
│   ├── router.dart                 # Route definitions (go_router/auto_route)
│   └── di.dart                     # Dependency injection setup
│
├── core/
│   ├── constants/                  # App-wide constants
│   ├── errors/                     # Custom exceptions, failure classes
│   ├── extensions/                 # Dart extension methods
│   ├── network/                    # Dio client, interceptors, API config
│   ├── theme/                      # ThemeData, ColorScheme, TextTheme
│   ├── utils/                      # Shared utilities, helpers
│   └── widgets/                    # Shared/base widgets
│
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── datasources/        # Remote & local data sources
│   │   │   ├── models/             # DTOs, JSON models (*.g.dart)
│   │   │   └── repositories/       # Repository implementations
│   │   ├── domain/
│   │   │   ├── entities/           # Business objects
│   │   │   ├── repositories/       # Repository interfaces (abstract)
│   │   │   └── usecases/           # Business logic use cases
│   │   └── presentation/
│   │       ├── bloc/               # BLoC/Cubit or providers
│   │       ├── pages/              # Screen widgets
│   │       └── widgets/            # Feature-specific widgets
│   │
│   ├── home/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   │
│   └── settings/
│       ├── data/
│       ├── domain/
│       └── presentation/
│
├── l10n/                           # Localization files
│   ├── app_en.arb
│   └── app_es.arb
│
└── main.dart                       # Entry point
```

### Feature-First vs Layer-First

| Approach | Structure | Best For | Drawback |
|----------|-----------|----------|----------|
| **Feature-First** | `features/auth/data/`, `features/auth/domain/` | Teams, scaling, clear ownership | More directories |
| **Layer-First** | `data/auth/`, `domain/auth/` | Small apps, rapid prototyping | Features scattered across layers |

**Recommendation**: Feature-first is the 2025 standard for production apps. Each feature is a self-contained module with its own data, domain, and presentation layers.

### Barrel Files

Barrel files (`export` re-exports from a single file) remain valuable for code organization but should be used strategically:

```dart
// features/auth/auth.dart (barrel file)
export 'data/repositories/auth_repository_impl.dart';
export 'domain/entities/user.dart';
export 'domain/repositories/auth_repository.dart';
export 'presentation/pages/login_page.dart';
```

**Best practice**: Use barrel files at feature/package level (coarse-grained), not at component level (fine-grained), to minimize analyzer performance degradation. The DCM tool provides an `avoid-barrel-files` rule for teams that prefer direct imports.

Sources:
- [Flutter Clean Architecture 2025 - Medium](https://medium.com/@flutter-app/flutter-3-38-clean-architecture-project-structure-for-2025-f6155ac40d87)
- [Clean Architecture in Flutter - Coding Studio](https://coding-studio.com/clean-architecture-in-flutter-a-complete-guide-with-code-examples-2025-edition/)
- [Flutter Clean Architecture in 2025 - Medium](https://medium.com/@tiger.chirag/flutter-clean-architecture-in-2025-the-right-way-to-structure-real-apps-152cf59f39f5)
- [Handling Flutter Imports Like a Pro 2025](https://www.bitsofflutter.dev/handling-flutter-imports-like-a-pro-2025-edition/)
- [DCM avoid-barrel-files Rule](https://dcm.dev/docs/rules/common/avoid-barrel-files/)

---

## 6. Navigation & Routing

### Router Package Decision Matrix

| Package | Best For | Type Safety | Code Gen | Deep Links | Web Support |
|---------|----------|-------------|----------|------------|-------------|
| **go_router** | Most projects, official recommendation | Good | No | Excellent | Excellent |
| **auto_route** | Large apps, type-safe routes | Excellent | Yes | Good | Good |
| **Navigator 2.0** | Custom routing needs | Manual | No | Manual | Manual |

### GoRouter (Recommended)

GoRouter is Flutter's officially recommended declarative routing package:

```dart
final router = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final isLoggedIn = ref.read(authProvider).isLoggedIn;
    if (!isLoggedIn && state.matchedLocation != '/login') {
      return '/login';
    }
    return null;
  },
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'details/:id',
          builder: (context, state) {
            final id = state.pathParameters['id']!;
            return DetailsScreen(id: id);
          },
        ),
      ],
    ),
    ShellRoute(
      builder: (context, state, child) => ScaffoldWithNav(child: child),
      routes: [
        GoRoute(path: '/feed', builder: (_, __) => const FeedScreen()),
        GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      ],
    ),
  ],
);
```

**GoRouter strengths**: URL-based navigation, browser history on web, redirect capabilities, deep link support, ShellRoute for persistent navigation shells.

### AutoRoute (For Large Projects)

AutoRoute uses code generation to provide strongly typed route definitions:

```dart
@RoutePage()
class HomeScreen extends StatelessWidget { ... }

@AutoRouterConfig()
class AppRouter extends RootStackRouter {
  @override
  List<AutoRoute> get routes => [
    AutoRoute(page: HomeRoute.page, initial: true),
    AutoRoute(page: DetailsRoute.page, path: '/details/:id'),
  ];
}

// Type-safe navigation
context.router.push(DetailsRoute(id: '123'));
```

**AutoRoute strengths**: Compile-time route verification, strongly typed argument passing, less boilerplate for complex routing hierarchies.

Sources:
- [Flutter Navigation and Routing (Official)](https://docs.flutter.dev/ui/navigation)
- [Flutter Navigation: Is GoRouter Still The Best Choice? - 8th Light](https://8thlight.com/insights/flutter-navigation-is-gorouter-still-the-best-choice)
- [Flutter Routing and Deep Linking Best Practices 2025](https://teachmeidea.com/flutter-routing-deep-linking-best-practices-2025/)
- [go_router package](https://pub.dev/packages/go_router)
- [auto_route package](https://pub.dev/packages/auto_route)

---

## 7. Networking & API Layer

### HTTP Client Decision Matrix

| Package | Best For | Code Gen | Interceptors | Type Safety | Complexity |
|---------|----------|----------|--------------|-------------|------------|
| **Dio** | Most projects, full-featured | No | Built-in | Manual | Medium |
| **Retrofit** | Large apps, type-safe APIs | Yes (build_runner) | Via Dio | Excellent | Medium-High |
| **http** | Simple apps, minimal deps | No | Manual | Manual | Low |

### Dio (Most Popular)

```dart
class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.example.com/v1',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.addAll([
      AuthInterceptor(),
      LogInterceptor(requestBody: true, responseBody: true),
      RetryInterceptor(dio: _dio, retries: 3),
    ]);
  }
}
```

### Custom Interceptor Pattern

```dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = tokenStorage.accessToken;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Refresh token and retry
      try {
        await refreshToken();
        final retryResponse = await _dio.fetch(err.requestOptions);
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

### Error Handling Pattern

```dart
sealed class ApiResult<T> {
  const ApiResult();
}
class ApiSuccess<T> extends ApiResult<T> {
  final T data;
  const ApiSuccess(this.data);
}
class ApiFailure<T> extends ApiResult<T> {
  final AppException exception;
  const ApiFailure(this.exception);
}

Future<ApiResult<T>> safeApiCall<T>(Future<T> Function() call) async {
  try {
    final result = await call();
    return ApiSuccess(result);
  } on DioException catch (e) {
    return ApiFailure(switch (e.type) {
      DioExceptionType.connectionTimeout => NetworkException('Connection timeout'),
      DioExceptionType.receiveTimeout => NetworkException('Receive timeout'),
      DioExceptionType.badResponse => ServerException(e.response?.statusCode ?? 0),
      _ => NetworkException('Network error'),
    });
  }
}
```

### Retrofit (Type-Safe Code Generation)

```dart
@RestApi(baseUrl: 'https://api.example.com/v1')
abstract class ApiService {
  factory ApiService(Dio dio) = _ApiService;

  @GET('/users/{id}')
  Future<UserDto> getUser(@Path('id') String id);

  @POST('/users')
  Future<UserDto> createUser(@Body() CreateUserRequest request);

  @GET('/users')
  Future<List<UserDto>> getUsers(@Query('page') int page);
}
```

Sources:
- [Mastering HTTP Calls in Flutter 2025 - Medium](https://medium.com/@pv.jassim/mastering-http-calls-in-flutter-2025-edition-http-vs-dio-vs-retrofit-1962ec46be43)
- [Networking in Flutter Using Dio - LogRocket](https://blog.logrocket.com/networking-flutter-using-dio/)
- [Retrofit in Flutter: Type-Safe APIs - Medium](https://medium.com/@rishad2002/retrofit-in-flutter-type-safe-clean-and-maintainable-apis-52a83c6848ca)
- [dio package](https://pub.dev/packages/dio)
- [retrofit package](https://pub.dev/packages/retrofit)

---

## 8. Local Storage & Databases

### Storage Decision Matrix

| Solution | Type | Best For | Performance | Complexity | Status |
|----------|------|----------|-------------|------------|--------|
| **shared_preferences** | Key-Value | Simple settings, flags | Fast | Very Low | Stable |
| **Hive** | Key-Value / NoSQL | Simple data, settings, small lists | Fast | Low | Maintenance mode* |
| **Isar** | NoSQL | Large datasets, indexed queries | Very Fast | Medium | Active |
| **Drift** (formerly Moor) | SQL (SQLite ORM) | Structured data, complex queries, migrations | Fast | Medium-High | Active, Recommended |
| **sqflite** | SQL (raw SQLite) | Direct SQL access, simple queries | Fast | Medium | Stable |
| **ObjectBox** | NoSQL | Speed at scale, relations | Very Fast | Medium | Active |

*Hive's author recommends Isar as its successor; both are community-maintained in 2025.

### Recommendations by Use Case

```
Simple settings, flags, preferences → shared_preferences
Notes app, small data, caching     → Hive or Isar
E-commerce, finance, structured    → Drift (type-safe SQL with migrations)
Chat, analytics, large datasets    → Isar or ObjectBox
Direct SQL control needed          → sqflite
```

### Drift Example (Recommended for Structured Data)

```dart
@DriftDatabase(tables: [Todos, Categories])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 2;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (m) => m.createAll(),
    onUpgrade: (m, from, to) async {
      if (from < 2) {
        await m.addColumn(todos, todos.category);
      }
    },
  );

  Stream<List<Todo>> watchAllTodos() => select(todos).watch();

  Future<int> addTodo(TodosCompanion entry) => into(todos).insert(entry);
}
```

### Isar Example (Fast NoSQL)

```dart
@collection
class Contact {
  Id id = Isar.autoIncrement;

  @Index(type: IndexType.value)
  late String name;

  late String email;
}

// Query with indexed speed
final contacts = await isar.contacts
    .where()
    .nameStartsWith('A')
    .sortByName()
    .findAll();
```

Sources:
- [Hive vs Drift vs Floor vs Isar 2025 - Quash](https://quashbugs.com/blog/hive-vs-drift-vs-floor-vs-isar-2025)
- [Flutter Databases Overview 2025 - GreenRobot](https://greenrobot.org/database/flutter-databases-overview/)
- [Best Local Database for Flutter - Dinko Marinac](https://dinkomarinac.dev/best-local-database-for-flutter-apps-a-complete-guide)
- [Flutter Local Database 2025 - BigOhTech](https://bigohtech.com/flutter-local-database)

---

## 9. Testing Strategies

### Testing Pyramid

| Layer | Percentage | Tool | Purpose |
|-------|-----------|------|---------|
| **Unit Tests** | ~50% | `test`, `mocktail`/`mockito` | Business logic, use cases, repositories |
| **Widget Tests** | ~30% | `flutter_test`, `golden_toolkit` | UI components, user interactions |
| **Integration Tests** | ~15% | `integration_test`, `patrol` | Complete user flows on device/emulator |
| **Golden Tests** | ~5% | `golden_toolkit` | Visual regression, pixel comparison |

### Unit Testing with Mocktail (Preferred over Mockito)

Mocktail is preferred because it handles non-nullable return types without code generation:

```dart
import 'package:mocktail/mocktail.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late AuthBloc authBloc;
  late MockAuthRepository mockAuthRepo;

  setUp(() {
    mockAuthRepo = MockAuthRepository();
    authBloc = AuthBloc(mockAuthRepo);
  });

  test('emits [AuthLoading, AuthSuccess] on successful login', () {
    when(() => mockAuthRepo.login(any(), any()))
        .thenAnswer((_) async => User(id: '1', name: 'Test'));

    expectLater(
      authBloc.stream,
      emitsInOrder([isA<AuthLoading>(), isA<AuthSuccess>()]),
    );

    authBloc.add(LoginRequested(email: 'test@test.com', password: 'pass'));
  });
}
```

### BLoC Testing with bloc_test

```dart
blocTest<AuthBloc, AuthState>(
  'emits [AuthLoading, AuthSuccess] when login succeeds',
  build: () {
    when(() => mockAuthRepo.login(any(), any()))
        .thenAnswer((_) async => testUser);
    return AuthBloc(mockAuthRepo);
  },
  act: (bloc) => bloc.add(LoginRequested(email: 'a@b.com', password: '123')),
  expect: () => [isA<AuthLoading>(), isA<AuthSuccess>()],
);
```

### Riverpod Testing

```dart
void main() {
  test('TodoList notifier fetches todos', () async {
    final container = ProviderContainer(
      overrides: [
        todoRepositoryProvider.overrideWithValue(MockTodoRepository()),
      ],
    );

    // Wait for the provider to complete
    await container.read(todoListProvider.future);

    final state = container.read(todoListProvider);
    expect(state.value, isNotEmpty);
  });
}
```

### Widget Testing

```dart
testWidgets('LoginPage shows error on invalid input', (tester) async {
  await tester.pumpWidget(
    const MaterialApp(home: LoginPage()),
  );

  await tester.tap(find.byType(ElevatedButton));
  await tester.pumpAndSettle();

  expect(find.text('Email is required'), findsOneWidget);
});
```

### Golden Tests

```dart
testGoldens('ProfileCard renders correctly', (tester) async {
  final builder = GoldenBuilder.grid(columns: 2, widthToHeightRatio: 1.5)
    ..addScenario('Default', const ProfileCard(name: 'Alice'))
    ..addScenario('Long name', const ProfileCard(name: 'Alexander Hamilton'));

  await tester.pumpWidgetBuilder(builder.build());
  await screenMatchesGolden(tester, 'profile_card_grid');
});
```

**Golden test best practices**: Run in headless CI environments, name assets descriptively, focus on stable components, gate pull requests on pass/fail.

### Patrol (Native UI Testing)

Patrol is an open-source framework for automated UI testing built specifically for Flutter. It allows writing end-to-end tests in pure Dart while also interacting with native elements (system dialogs, permissions, notifications) that Flutter test framework normally cannot reach.

Sources:
- [Flutter Testing Overview (Official)](https://docs.flutter.dev/testing/overview)
- [Navigating the Hard Parts of Testing in Flutter - DCM](https://dcm.dev/blog/2025/07/30/navigating-hard-parts-testing-flutter-developers)
- [Flutter Golden Tests - SolGuruz](https://solguruz.com/blog/flutter-golden-tests/)
- [Testing Riverpod Providers (Official)](https://riverpod.dev/docs/how_to/testing)
- [Flutter Testing Guide - YriKan](https://yrkan.com/blog/flutter-testing-guide/)

---

## 10. Performance Optimization

### Widget Rebuild Optimization

**1. Use const constructors religiously** - Reduces widget rebuilds by up to 70%:
```dart
// GOOD
const Text('Hello World')
const SizedBox(height: 16)
const EdgeInsets.all(16)

// BAD - rebuilds every time
Text('Hello World')
SizedBox(height: 16)
```

**2. Break down large widgets into smaller components**:
```dart
// BAD - entire widget rebuilds when counter changes
class BigWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      const Header(),           // Unnecessary rebuild
      CounterDisplay(),         // Only this needs to rebuild
      const Footer(),           // Unnecessary rebuild
    ]);
  }
}

// GOOD - only CounterDisplay rebuilds
```

**3. Use RepaintBoundary for frequently-updating widgets**:
```dart
RepaintBoundary(
  child: AnimatedGraph(data: liveData),  // Redraws only within boundary
)
```

**4. Prefer StatelessWidget when possible** - Flutter skips rebuild process for stateless widgets.

**5. Use ListView.builder for long lists** (lazy loading):
```dart
// BAD - builds all 10,000 items at once
ListView(children: items.map((i) => ItemWidget(i)).toList())

// GOOD - only builds visible items
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),
)
```

### Image Optimization

```dart
// Use CachedNetworkImage for network images
CachedNetworkImage(
  imageUrl: 'https://example.com/image.jpg',
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
  memCacheWidth: 300,   // Resize in memory cache
)
```

**Best practices**:
- Compress images server-side; serve WebP/AVIF formats
- Set explicit `width`/`height` to avoid layout shifts
- Use `memCacheWidth`/`memCacheHeight` to avoid decoding full-resolution images
- Use `ListView.builder` to lazy-load image lists

### State Management Performance

```dart
// BAD - rebuilds entire widget tree
BlocBuilder<CartBloc, CartState>(
  builder: (context, state) => Column(children: [
    CartItems(state.items),
    CartTotal(state.total),    // Rebuilds even when items change
  ]),
)

// GOOD - scoped rebuilds with buildWhen/select
BlocBuilder<CartBloc, CartState>(
  buildWhen: (prev, curr) => prev.total != curr.total,
  builder: (context, state) => CartTotal(state.total),
)

// Riverpod: use select for fine-grained rebuilds
final total = ref.watch(cartProvider.select((cart) => cart.total));
```

### Additional Performance Tips

- **Avoid heavy work in build()** - Move I/O and CPU work to services/background isolates
- **Dispose controllers**: Always dispose `TextEditingController`, `StreamSubscription`, `AnimationController` to prevent memory leaks
- **Use keys** for dynamic lists: `ValueKey`, `ObjectKey` for smooth list operations
- **Profile in release mode**: Debug mode is 10x slower; always use `--profile` for performance testing
- **Use DevTools**: Flutter DevTools for widget rebuild tracking, timeline, memory profiling
- **Impeller**: Now default on iOS and Android (API 29+) - eliminates shader jank

### Performance Targets

| Metric | Target |
|--------|--------|
| Frame rate | Consistent 60fps (120fps on high-refresh devices) |
| App startup | < 2 seconds cold start |
| Widget rebuilds | 60-80% reduction with optimization |
| Image loading | Cached, lazy-loaded, appropriately sized |
| Memory | No leaks from undisposed controllers/streams |

Sources:
- [Performance Best Practices (Official)](https://docs.flutter.dev/perf/best-practices)
- [13 Flutter Performance Optimization Techniques 2025 - f22labs](https://www.f22labs.com/blogs/13-flutter-performance-optimization-techniques-in-2025/)
- [Flutter Performance Optimization 2025 - ITNEXT](https://itnext.io/flutter-performance-optimization-10-techniques-that-actually-work-in-2025-4def9e5bbd2d)
- [Mastering Flutter Rebuild Optimization](https://763p.me/blog/2025/09/28/mastering-flutter-rebuild-optimization-eliminating-unnecessary-widget-rebuilds/)
- [Impeller Rendering Engine (Official)](https://docs.flutter.dev/perf/impeller)

---

## 11. Platform-Specific Code

### Pigeon (Recommended for Type-Safe Platform Channels)

Pigeon generates type-safe, null-safe, boilerplate-free platform channel code for iOS, Android, macOS, Windows, and more:

```dart
// pigeons/messages.dart
import 'package:pigeon/pigeon.dart';

class SearchRequest {
  String? query;
  int? limit;
}

class SearchReply {
  String? result;
  String? error;
}

@HostApi()  // Flutter → Native
abstract class SearchApi {
  SearchReply search(SearchRequest request);
}

@FlutterApi()  // Native → Flutter
abstract class SearchEventApi {
  void onSearchUpdate(SearchReply reply);
}
```

Run code generation:
```bash
dart run pigeon --input pigeons/messages.dart
```

This generates:
- Dart code for Flutter side
- Swift/Kotlin code for iOS/Android
- Type-safe method calls with no string-based channel names

### Conditional Imports (Platform-Specific Implementations)

```dart
// stub.dart (fallback)
Widget getPlatformWidget() => throw UnsupportedError('Platform not supported');

// mobile.dart
Widget getPlatformWidget() => const MobileWidget();

// web.dart
Widget getPlatformWidget() => const WebWidget();

// usage.dart
import 'stub.dart'
    if (dart.library.io) 'mobile.dart'
    if (dart.library.html) 'web.dart';
```

### Platform Detection

```dart
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

if (kIsWeb) {
  // Web-specific code
} else if (Platform.isIOS) {
  // iOS-specific code
} else if (Platform.isAndroid) {
  // Android-specific code
}
```

### FFI (Foreign Function Interface)

For performance-critical native code, FFI provides direct access to C libraries without message passing overhead:

```dart
final dylib = DynamicLibrary.open('libnative.so');
final nativeAdd = dylib.lookupFunction<Int32 Function(Int32, Int32), int Function(int, int)>('native_add');
print(nativeAdd(3, 4)); // 7
```

Sources:
- [Writing Custom Platform-Specific Code (Official)](https://docs.flutter.dev/platform-integration/platform-channels)
- [Pigeon Package](https://pub.dev/packages/pigeon)
- [Type-Safe Platform Channels with Pigeon 2025 - Medium](https://the-expert-developer.medium.com/%EF%B8%8F-type-safe-platform-channels-in-flutter-2025-with-pigeon-build-native-power-without-the-15f9db2d7d96)
- [Working with Native Elements: Platform Channel vs Pigeon vs FFI - Codemagic](https://blog.codemagic.io/working-with-native-elements/)

---

## 12. CI/CD & DevOps

### Platform Decision Matrix

| Platform | Best For | macOS Build | Cost Model | Complexity |
|----------|----------|-------------|------------|------------|
| **Codemagic** | Flutter-first, easy setup | Yes (cloud) | Free tier + paid | Low |
| **GitHub Actions** | Existing GitHub workflows | Via self-hosted or macOS runner | Free (public) + paid minutes | Medium |
| **Fastlane** | Automated signing & deployment | Local or CI | Free (OSS) | Medium-High |
| **Bitrise** | Mobile CI/CD | Yes (cloud) | Free tier + paid | Low-Medium |

### GitHub Actions Workflow

```yaml
name: Flutter CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
          channel: 'stable'
      - run: flutter pub get
      - run: dart analyze
      - run: flutter test --coverage
      - run: flutter build apk --release

  ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
      - run: flutter pub get
      - run: flutter build ios --release --no-codesign
```

### Flavors (Build Variants)

```dart
// lib/main_dev.dart
void main() => runApp(const App(environment: Environment.dev));

// lib/main_staging.dart
void main() => runApp(const App(environment: Environment.staging));

// lib/main_prod.dart
void main() => runApp(const App(environment: Environment.prod));
```

```bash
# Build specific flavor
flutter run --flavor dev -t lib/main_dev.dart
flutter build apk --flavor prod -t lib/main_prod.dart
```

Android `build.gradle` flavors:
```groovy
flavorDimensions "environment"
productFlavors {
    dev {
        dimension "environment"
        applicationIdSuffix ".dev"
        versionNameSuffix "-dev"
    }
    staging {
        dimension "environment"
        applicationIdSuffix ".staging"
        versionNameSuffix "-staging"
    }
    prod {
        dimension "environment"
    }
}
```

### Fastlane Integration

```ruby
# fastlane/Fastfile
platform :android do
  lane :deploy do
    gradle(task: "clean assembleRelease")
    upload_to_play_store(track: "internal")
  end
end

platform :ios do
  lane :deploy do
    build_app(workspace: "Runner.xcworkspace", scheme: "Runner")
    upload_to_testflight
  end
end
```

Sources:
- [Flutter CI/CD with Fastlane and GitHub Actions - NTT Data](https://nttdata-dach.github.io/posts/dd-fluttercicd-01-basics/)
- [CI/CD for Flutter with Fastlane, Codemagic, Build Flavors - Medium](https://medium.com/@tungnd.dev/ci-cd-for-flutter-with-fastlane-codemagic-build-flavors-42253cc95e97)
- [Codemagic](https://codemagic.io/start/)
- [CI/CD for Flutter - Code With Andrea](https://pro.codewithandrea.com/get-started-flutter/intro/15-ci-cd)

---

## 13. Code Generation

### Key Code Generation Packages

| Package | Purpose | Generates |
|---------|---------|-----------|
| **freezed** | Immutable data classes, unions | `copyWith`, `toString`, `==`, `hashCode`, JSON, union types |
| **json_serializable** | JSON serialization | `fromJson`, `toJson` methods |
| **build_runner** | Code generation orchestrator | Runs all generators |
| **auto_route** | Type-safe routing | Router config, route arguments |
| **retrofit_generator** | Type-safe API client | API implementation from annotations |
| **riverpod_generator** | Riverpod providers | Provider definitions from annotations |
| **injectable** | Dependency injection | GetIt registration code |

### Freezed (Immutable Data Classes)

```dart
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    required String email,
    @Default(false) bool isVerified,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// Sealed unions with Freezed
@freezed
sealed class AuthState with _$AuthState {
  const factory AuthState.initial() = AuthInitial;
  const factory AuthState.loading() = AuthLoading;
  const factory AuthState.authenticated(User user) = Authenticated;
  const factory AuthState.error(String message) = AuthError;
}
```

### json_serializable

```dart
import 'package:json_annotation/json_annotation.dart';

part 'product.g.dart';

@JsonSerializable()
class Product {
  final String id;
  final String name;

  @JsonKey(name: 'unit_price')
  final double unitPrice;

  @JsonKey(includeIfNull: false)
  final String? description;

  Product({required this.id, required this.name, required this.unitPrice, this.description});

  factory Product.fromJson(Map<String, dynamic> json) => _$ProductFromJson(json);
  Map<String, dynamic> toJson() => _$ProductToJson(this);
}
```

### Running Code Generation

```bash
# One-time build
dart run build_runner build --delete-conflicting-outputs

# Watch mode (regenerates on file changes)
dart run build_runner watch --delete-conflicting-outputs
```

### Augmentations (Future of Code Gen)

With Dart macros cancelled, **augmentations** (the `augment` keyword) are being shipped as the future foundation for better code generation, allowing class definitions to be split across multiple files while keeping compilation fast.

Sources:
- [Flutter Code Generation: freezed, json_serializable, build_runner](https://dasroot.net/posts/2026/01/flutter-code-generation-freezed-json-serializable-build-runner/)
- [How to Parse JSON with Freezed - Code With Andrea](https://codewithandrea.com/articles/parse-json-dart-codegen-freezed/)
- [freezed package](https://pub.dev/packages/freezed)
- [json_serializable package](https://pub.dev/packages/json_annotation)

---

## 14. Theming & Design

### Material 3 (Default in Flutter)

Material 3 is now the default design system in Flutter. Apps that still use Material 2 feel outdated on modern Android devices:

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,  // Default since Flutter 3.16
    colorSchemeSeed: Colors.blue,  // Dynamic color generation
    brightness: Brightness.light,
  ),
  darkTheme: ThemeData(
    useMaterial3: true,
    colorSchemeSeed: Colors.blue,
    brightness: Brightness.dark,
  ),
  themeMode: ThemeMode.system,
)
```

### Custom Theme with ColorScheme

```dart
final lightColorScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.light,
);

final darkColorScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.dark,
);

ThemeData buildTheme(ColorScheme colorScheme) {
  return ThemeData(
    colorScheme: colorScheme,
    useMaterial3: true,
    textTheme: GoogleFonts.interTextTheme(),
    appBarTheme: AppBarTheme(
      backgroundColor: colorScheme.surface,
      foregroundColor: colorScheme.onSurface,
      elevation: 0,
    ),
    cardTheme: CardTheme(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: colorScheme.surfaceContainerLow,
    ),
  );
}
```

### Adaptive & Responsive Design

**Responsive** = fitting UI into available space. **Adaptive** = selecting appropriate layout/input for the platform.

```dart
class AdaptiveScaffold extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;

    return Scaffold(
      body: Row(children: [
        if (width >= 840)      // Desktop: persistent sidebar
          const NavigationRail(/* ... */),
        Expanded(child: content),
      ]),
      bottomNavigationBar: width < 600   // Mobile: bottom nav
          ? const NavigationBar(/* ... */)
          : null,
    );
  }
}
```

### Material 3 Breakpoints

| Device | Width | Navigation |
|--------|-------|------------|
| Mobile | < 600px | NavigationBar (bottom) |
| Tablet | 600-839px | NavigationRail (side) |
| Desktop | >= 840px | NavigationDrawer (permanent) |

### LayoutBuilder for Responsive Widgets

```dart
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth >= 840) {
      return const TwoColumnLayout();
    } else {
      return const SingleColumnLayout();
    }
  },
)
```

Sources:
- [Adaptive and Responsive Design (Official)](https://docs.flutter.dev/ui/adaptive-responsive)
- [Best Practices for Adaptive Design (Official)](https://docs.flutter.dev/ui/adaptive-responsive/best-practices)
- [Material Design 3 for Flutter](https://m3.material.io/develop/flutter)
- [Material 3 & Fluent UI in Flutter - Medium](https://medium.com/@flutter-app/material-3-fluent-ui-in-flutter-modern-theming-bbb4e1882f6c)

---

## 15. Security

### Security Checklist

| Area | Recommendation | Package/Tool |
|------|---------------|--------------|
| **Secure storage** | Use platform-specific secure mechanisms | `flutter_secure_storage` |
| **API keys** | Never hardcode; use env vars or remote config | `envied`, `flutter_dotenv` |
| **Network** | HTTPS only; consider certificate pinning for finance apps | `dio` SecurityContext |
| **Code protection** | Obfuscate release builds | `--obfuscate` flag |
| **Dependency audit** | Scan for vulnerabilities | `dart pub outdated`, OSV |
| **Authentication** | JWT with secure token storage and refresh | `flutter_secure_storage` |
| **Data encryption** | Encrypt sensitive local data | `encrypt`, `pointycastle` |

### Secure Storage

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);

// Store token securely
await storage.write(key: 'access_token', value: token);

// Read token
final token = await storage.read(key: 'access_token');

// Delete on logout
await storage.deleteAll();
```

### Certificate Pinning

```dart
// Manual SSL pinning with SecurityContext
SecurityContext createSecurityContext() {
  final context = SecurityContext(withTrustedRoots: false);
  context.setTrustedCertificatesBytes(certificateBytes);
  return context;
}

// With Dio
final dio = Dio();
(dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
  final client = HttpClient(context: createSecurityContext());
  client.badCertificateCallback = (cert, host, port) => false;
  return client;
};
```

**When to pin**: Only for high-risk apps (financial, medical). Requires certificate lifecycle management; expired pins cause outages.

### Code Obfuscation

```bash
# Build with obfuscation
flutter build apk --release --obfuscate --split-debug-info=build/debug-info/

# iOS
flutter build ios --release --obfuscate --split-debug-info=build/debug-info/
```

### ProGuard for Android

```groovy
// android/app/build.gradle
buildTypes {
    release {
        minifyEnabled true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
}
```

```
# android/app/proguard-rules.pro
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
```

### Security Best Practices

1. **Never** store secrets in source code or assets
2. Encrypt data at rest and in transit
3. Implement token expiry with automatic refresh
4. Validate and sanitize all user inputs
5. Use biometric authentication for sensitive operations
6. Obfuscation is one layer -- supplement with encryption and runtime defenses
7. Integrate security checks into CI/CD pipeline

Sources:
- [Flutter Security (Official)](https://docs.flutter.dev/security)
- [Flutter App Security Vulnerabilities & Best Practices - Touchlane](https://touchlane.com/5-overlooked-flutter-security-vulnerabilities-and-how-to-address-them/)
- [Flutter Security Best Practices - SolGuruz](https://solguruz.com/blog/flutter-security-best-practices/)
- [Obfuscate Dart Code (Official)](https://docs.flutter.dev/deployment/obfuscate)
- [Building Secure Mobile App with Flutter - Repcik](https://tomasrepcik.dev/blog/2025/2025-10-12-secure-mobile-app/)

---

## 16. Common Anti-Patterns

### Performance Killers

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| Missing `const` constructors | Unnecessary widget rebuilds (up to 70% more) | Add `const` to every eligible constructor |
| Heavy work in `build()` | Blocks UI thread, causes jank | Move I/O/CPU work to services or isolates |
| `ListView` with all children | Builds all items at once, OOM on large lists | Use `ListView.builder` / slivers |
| Undisposed controllers | Memory leaks, laggy app over time | Always `dispose()` in `State.dispose()` |
| Large uncompressed images | High memory, slow loads, large app size | Compress, resize, use `CachedNetworkImage` |
| Unscoped state rebuilds | Entire subtree rebuilds on any state change | Use `select`, `buildWhen`, `Consumer` |
| Missing keys on dynamic lists | Flutter can't track items, glitchy list behavior | Use `ValueKey` or `ObjectKey` |

### State Management Mistakes

```dart
// BAD: Updating entire widget when only small part changes
setState(() {
  // This triggers rebuild of the entire stateful widget
  _counter++;
});

// GOOD: Isolate the changing part
BlocSelector<CounterBloc, CounterState, int>(
  selector: (state) => state.counter,
  builder: (context, counter) => Text('$counter'),
)
```

### Common Coding Mistakes

1. **`setState` called during build** - Move state changes to post-frame callbacks or event handlers
2. **`RenderFlex overflowed`** - Wrap content in `SingleChildScrollView`, `Expanded`, or `Flexible`
3. **Not using `mounted` check after async** - Always check `if (mounted)` before calling `setState` after `await`
4. **Testing only on one device** - Test on multiple screen sizes, densities, and platforms
5. **Trusting debug mode performance** - Always profile in `--profile` or `--release` mode
6. **Ignoring `dispose()`** - Leads to memory leaks with `TextEditingController`, `AnimationController`, `StreamSubscription`, `ScrollController`
7. **Deeply nested widget trees** - Extract into smaller widgets for maintainability and rebuild optimization

### Architecture Anti-Patterns

- **God widgets**: One massive widget doing everything. Split into smaller, focused components.
- **Business logic in UI**: Move to BLoC/ViewModel/UseCase layer.
- **Tight coupling to packages**: Abstract behind interfaces (Repository pattern).
- **Skipping the domain layer**: Even for small apps, entities and use cases aid testability.
- **Not using dependency injection**: Makes testing and swapping implementations difficult.

Sources:
- [Flutter Performance Mistakes 2025 - Medium](https://medium.com/@tiger.chirag/stop-doing-these-flutter-performance-mistakes-2026-edition-79cae09d5f22)
- [15 Common Mistakes in Flutter and Dart - DCM](https://dcm.dev/blog/2025/03/24/fifteen-common-mistakes-flutter-dart-development)
- [10 Flutter Mistakes Beginners Still Make 2025 - Medium](https://medium.com/@owaismustafa2000/10-flutter-mistakes-beginners-still-make-in-2025-and-how-to-avoid-them-f333c8600b6c)
- [Performance Best Practices (Official)](https://docs.flutter.dev/perf/best-practices)

---

## 17. Community Conventions & Ecosystem

### Linting & Analysis

| Tool | Purpose | Adoption |
|------|---------|----------|
| **very_good_analysis** | Comprehensive lint rules from Very Good Ventures | High (industry standard) |
| **DCM (Dart Code Metrics)** | Advanced code quality metrics and rules | Growing |
| **flutter_lints** | Official Flutter lint rules (lighter) | Default |
| **custom_lint** | Build your own lint rules | For teams with specific needs |

```yaml
# analysis_options.yaml (recommended)
include: package:very_good_analysis/analysis_options.yaml

analyzer:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"

linter:
  rules:
    # Override specific rules as needed
    public_member_api_docs: false
```

### Recommended Package Stack (2025-2026)

**State Management**:
- `flutter_riverpod` + `riverpod_generator` (modern choice)
- `flutter_bloc` + `bloc` (enterprise choice)

**Navigation**: `go_router` (official) or `auto_route` (large apps)

**Networking**: `dio` + `retrofit` (or `dio` alone)

**Code Generation**: `freezed` + `json_serializable` + `build_runner`

**Dependency Injection**: `get_it` + `injectable` or Riverpod's built-in DI

**Local Storage**: `drift` (structured) or `isar` (NoSQL)

**Secure Storage**: `flutter_secure_storage`

**Testing**:
- `mocktail` (mocking, preferred over mockito)
- `bloc_test` (BLoC testing)
- `golden_toolkit` (visual regression)
- `patrol` (native UI testing)

**Localization**: `intl` + `flutter_localizations`

**Animations**: `lottie` + Flutter built-in animations

**Images**: `cached_network_image`

**Logging**: `logger` or `talker`

**Environment**: `envied` (compile-time env vars)

### Naming Conventions

```
lib/
  feature_name/          # snake_case for directories
    feature_name_page.dart    # snake_case for files
    feature_name_bloc.dart
    feature_name_state.dart
```

- **Classes**: `PascalCase` - `UserRepository`, `AuthBloc`
- **Files**: `snake_case` - `user_repository.dart`, `auth_bloc.dart`
- **Variables/functions**: `camelCase` - `userName`, `fetchUser()`
- **Constants**: `camelCase` or `SCREAMING_SNAKE_CASE` (preference varies)
- **Private members**: prefix with `_` - `_internalState`
- **BLoC Events**: past tense - `LoginRequested`, `DataLoaded`
- **BLoC States**: adjective/status - `AuthLoading`, `AuthSuccess`, `AuthFailure`

### Essential CLI Commands

```bash
# Create new project
flutter create --org com.example --platforms ios,android my_app

# Analyze code
dart analyze

# Format code
dart format .

# Run tests with coverage
flutter test --coverage

# Generate code
dart run build_runner build --delete-conflicting-outputs

# Build release
flutter build apk --release --obfuscate --split-debug-info=build/debug-info/
flutter build ios --release

# Check outdated dependencies
dart pub outdated
```

Sources:
- [Top Open Source Packages Every Flutter Developer Should Know 2025 - Very Good Ventures](https://www.verygood.ventures/blog/top-open-source-packages-every-flutter-developer-should-know-in-2025)
- [Pub in Focus: Critical Dart & Flutter Packages - Very Good Ventures](https://www.verygood.ventures/blog/pub-in-focus-the-most-critical-dart-flutter-packages-of-2024)
- [Architecture Recommendations and Resources (Official)](https://docs.flutter.dev/app-architecture/recommendations)
- [Flutter App Development Best Practices 2025 - Miquido](https://www.miquido.com/blog/flutter-app-best-practices/)

---

## Blueprint Planning Checklist

1. **Flutter/Dart version**: Target Flutter 3.41+ / Dart 3.11+ (stable channel)
2. **Architecture**: MVVM (Flutter official) or Clean Architecture with feature-first organization?
3. **State management**: Riverpod 3 (modern) or BLoC 8+ (enterprise)? Avoid GetX.
4. **Project structure**: Feature-first with data/domain/presentation layers per feature
5. **Navigation**: go_router (most projects) or auto_route (large apps with code gen)
6. **Networking**: Dio with interceptors; Retrofit for type-safe code gen
7. **Local storage**: Drift for structured data, Isar for NoSQL, flutter_secure_storage for secrets
8. **Code generation**: freezed + json_serializable + build_runner
9. **Testing strategy**: 50% unit / 30% widget / 15% integration / 5% golden tests; mocktail for mocking
10. **Theming**: Material 3 with ColorScheme.fromSeed, adaptive layouts, responsive breakpoints
11. **Security**: Obfuscation, secure storage, no hardcoded secrets, certificate pinning for finance
12. **CI/CD**: GitHub Actions or Codemagic, Fastlane for deployment, flavors for environments
13. **Linting**: very_good_analysis + dart analyze in CI
14. **Platform code**: Pigeon for type-safe platform channels, conditional imports
15. **Performance**: const constructors, lazy lists, RepaintBoundary, scoped rebuilds, Impeller
16. **Dart features**: Use records, sealed classes, pattern matching, switch expressions
