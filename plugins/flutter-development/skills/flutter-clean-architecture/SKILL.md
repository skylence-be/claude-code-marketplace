---
name: flutter-clean-architecture
description: Master Flutter clean architecture with feature modules, data/domain/presentation layers, repository pattern, and dependency injection. Use when structuring Flutter projects, implementing data layers, or organizing feature modules.
category: flutter
tags: [flutter, architecture, clean-architecture, repository, features]
---

# Flutter Clean Architecture

Scalable Flutter project structure with feature modules and layered architecture.

## When to Use This Skill

- Setting up a new Flutter project structure
- Organizing features into modules
- Implementing repository pattern for data access
- Separating business logic from UI
- Creating testable, maintainable code

## Project Structure

```
lib/
├── main.dart                    # Entry point
├── app.dart                     # App widget with theme/routing
├── router.dart                  # GoRouter configuration
│
├── core/                        # Shared infrastructure
│   ├── constants/
│   │   ├── api_constants.dart   # API URLs, timeouts
│   │   └── app_constants.dart   # App-wide constants
│   │
│   ├── errors/
│   │   ├── exceptions.dart      # Custom exceptions
│   │   └── failures.dart        # Failure types for Either
│   │
│   ├── network/
│   │   ├── api_client.dart      # Dio instance
│   │   └── interceptors/
│   │       ├── auth_interceptor.dart
│   │       ├── error_interceptor.dart
│   │       └── cache_interceptor.dart
│   │
│   ├── storage/
│   │   ├── local_storage.dart   # Hive wrapper
│   │   └── secure_storage.dart  # Credentials storage
│   │
│   └── utils/
│       ├── validators.dart      # Input validation
│       └── formatters.dart      # Date/time/money formatters
│
├── features/                    # Feature modules
│   ├── auth/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   │
│   ├── timer/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   │
│   └── entries/
│       ├── data/
│       ├── domain/
│       └── presentation/
│
└── shared/                      # Shared UI
    ├── theme/
    │   ├── app_theme.dart
    │   └── app_colors.dart
    ├── providers/               # Global Riverpod providers
    └── widgets/                 # Reusable widgets
```

## Layer Responsibilities

### Data Layer
Handles external data sources and maps to domain entities.

```
feature/
└── data/
    ├── models/                  # JSON-serializable models
    │   └── entry_model.dart
    ├── datasources/             # Data sources
    │   ├── entry_remote_source.dart
    │   └── entry_local_source.dart
    └── repositories/            # Repository implementations
        └── entry_repository_impl.dart
```

#### Model (Data Transfer Object)
```dart
// data/models/entry_model.dart
import 'package:json_annotation/json_annotation.dart';

part 'entry_model.g.dart';

@JsonSerializable()
class EntryModel {
  final int id;
  final int projectId;
  @JsonKey(name: 'start_time')
  final DateTime startTime;
  @JsonKey(name: 'end_time')
  final DateTime? endTime;
  final String? description;

  const EntryModel({
    required this.id,
    required this.projectId,
    required this.startTime,
    this.endTime,
    this.description,
  });

  factory EntryModel.fromJson(Map<String, dynamic> json) =>
      _$EntryModelFromJson(json);

  Map<String, dynamic> toJson() => _$EntryModelToJson(this);

  // Convert to domain entity
  TimeEntry toEntity() {
    return TimeEntry(
      id: id.toString(),
      projectId: projectId.toString(),
      startTime: startTime,
      endTime: endTime,
      description: description,
    );
  }

  // Create from domain entity
  factory EntryModel.fromEntity(TimeEntry entity) {
    return EntryModel(
      id: int.parse(entity.id),
      projectId: int.parse(entity.projectId),
      startTime: entity.startTime,
      endTime: entity.endTime,
      description: entity.description,
    );
  }
}
```

#### Remote Data Source
```dart
// data/datasources/entry_remote_source.dart
class EntryRemoteSource {
  final Dio _client;

  EntryRemoteSource(this._client);

  Future<List<EntryModel>> getEntries() async {
    try {
      final response = await _client.get('/timesheets');
      return (response.data as List)
          .map((json) => EntryModel.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw _mapException(e);
    }
  }

  Future<EntryModel> createEntry(EntryModel entry) async {
    try {
      final response = await _client.post(
        '/timesheets',
        data: entry.toJson(),
      );
      return EntryModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _mapException(e);
    }
  }

  Exception _mapException(DioException e) {
    return switch (e.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.receiveTimeout => NetworkException('Connection timeout'),
      DioExceptionType.badResponse => _mapStatusCode(e.response?.statusCode),
      _ => NetworkException(e.message ?? 'Network error'),
    };
  }

  Exception _mapStatusCode(int? code) {
    return switch (code) {
      401 => AuthException('Unauthorized'),
      403 => AuthException('Forbidden'),
      404 => NotFoundException('Resource not found'),
      _ => ServerException('Server error: $code'),
    };
  }
}
```

#### Repository Implementation
```dart
// data/repositories/entry_repository_impl.dart
class EntryRepositoryImpl implements EntryRepository {
  final EntryRemoteSource _remoteSource;
  final EntryLocalSource _localSource;
  final NetworkInfo _networkInfo;

  EntryRepositoryImpl({
    required EntryRemoteSource remoteSource,
    required EntryLocalSource localSource,
    required NetworkInfo networkInfo,
  })  : _remoteSource = remoteSource,
        _localSource = localSource,
        _networkInfo = networkInfo;

  @override
  Future<List<TimeEntry>> getEntries() async {
    if (await _networkInfo.isConnected) {
      try {
        final models = await _remoteSource.getEntries();
        await _localSource.cacheEntries(models);
        return models.map((m) => m.toEntity()).toList();
      } on NetworkException {
        return _getCachedEntries();
      }
    } else {
      return _getCachedEntries();
    }
  }

  Future<List<TimeEntry>> _getCachedEntries() async {
    final cached = await _localSource.getCachedEntries();
    return cached.map((m) => m.toEntity()).toList();
  }

  @override
  Future<TimeEntry> createEntry(TimeEntry entry) async {
    final model = EntryModel.fromEntity(entry);
    final created = await _remoteSource.createEntry(model);
    return created.toEntity();
  }
}
```

### Domain Layer
Pure Dart with business logic and entities.

```
feature/
└── domain/
    ├── entities/                # Business entities
    │   └── time_entry.dart
    ├── repositories/            # Abstract repository contracts
    │   └── entry_repository.dart
    └── usecases/                # Business logic (optional)
        └── calculate_duration.dart
```

#### Entity
```dart
// domain/entities/time_entry.dart
import 'package:equatable/equatable.dart';

class TimeEntry extends Equatable {
  final String id;
  final String projectId;
  final DateTime startTime;
  final DateTime? endTime;
  final String? description;

  const TimeEntry({
    required this.id,
    required this.projectId,
    required this.startTime,
    this.endTime,
    this.description,
  });

  Duration get duration {
    final end = endTime ?? DateTime.now();
    return end.difference(startTime);
  }

  bool get isRunning => endTime == null;

  TimeEntry copyWith({
    String? id,
    String? projectId,
    DateTime? startTime,
    DateTime? endTime,
    String? description,
  }) {
    return TimeEntry(
      id: id ?? this.id,
      projectId: projectId ?? this.projectId,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      description: description ?? this.description,
    );
  }

  @override
  List<Object?> get props => [id, projectId, startTime, endTime, description];
}
```

#### Repository Contract
```dart
// domain/repositories/entry_repository.dart
abstract class EntryRepository {
  Future<List<TimeEntry>> getEntries();
  Future<TimeEntry> getEntry(String id);
  Future<TimeEntry> createEntry(TimeEntry entry);
  Future<TimeEntry> updateEntry(TimeEntry entry);
  Future<void> deleteEntry(String id);
}
```

### Presentation Layer
UI components and state management.

```
feature/
└── presentation/
    ├── providers/               # Riverpod providers
    │   ├── entries_provider.dart
    │   └── entry_form_provider.dart
    ├── screens/                 # Full-page widgets
    │   ├── entries_screen.dart
    │   └── entry_detail_screen.dart
    └── widgets/                 # Feature-specific widgets
        ├── entry_card.dart
        └── entry_form.dart
```

#### Provider with Repository
```dart
// presentation/providers/entries_provider.dart
@riverpod
EntryRepository entryRepository(EntryRepositoryRef ref) {
  return EntryRepositoryImpl(
    remoteSource: ref.watch(entryRemoteSourceProvider),
    localSource: ref.watch(entryLocalSourceProvider),
    networkInfo: ref.watch(networkInfoProvider),
  );
}

@riverpod
Future<List<TimeEntry>> entries(EntriesRef ref) async {
  final repository = ref.watch(entryRepositoryProvider);
  return repository.getEntries();
}
```

## Error Handling

### Exception Types
```dart
// core/errors/exceptions.dart
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
  const ServerException(super.message);
}

class CacheException extends AppException {
  const CacheException(super.message);
}

class NotFoundException extends AppException {
  const NotFoundException(super.message);
}

class ValidationException extends AppException {
  final Map<String, String> errors;
  const ValidationException(super.message, {this.errors = const {}});
}
```

### Error Handling in UI
```dart
Widget build(BuildContext context, WidgetRef ref) {
  final entriesAsync = ref.watch(entriesProvider);

  return entriesAsync.when(
    data: (entries) => EntriesList(entries: entries),
    loading: () => const EntriesLoadingSkeleton(),
    error: (error, _) => ErrorView(
      message: _getErrorMessage(error),
      onRetry: () => ref.invalidate(entriesProvider),
    ),
  );
}

String _getErrorMessage(Object error) {
  return switch (error) {
    NetworkException(:final message) => 'Network error: $message',
    AuthException() => 'Please log in again',
    NotFoundException() => 'Entry not found',
    _ => 'Something went wrong',
  };
}
```

## Testing

### Repository Test
```dart
void main() {
  late MockEntryRemoteSource mockRemoteSource;
  late MockEntryLocalSource mockLocalSource;
  late MockNetworkInfo mockNetworkInfo;
  late EntryRepositoryImpl repository;

  setUp(() {
    mockRemoteSource = MockEntryRemoteSource();
    mockLocalSource = MockEntryLocalSource();
    mockNetworkInfo = MockNetworkInfo();
    repository = EntryRepositoryImpl(
      remoteSource: mockRemoteSource,
      localSource: mockLocalSource,
      networkInfo: mockNetworkInfo,
    );
  });

  group('getEntries', () {
    test('returns remote data when online', () async {
      when(() => mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      when(() => mockRemoteSource.getEntries())
          .thenAnswer((_) async => [testEntryModel]);
      when(() => mockLocalSource.cacheEntries(any()))
          .thenAnswer((_) async {});

      final result = await repository.getEntries();

      expect(result, [testEntry]);
      verify(() => mockLocalSource.cacheEntries([testEntryModel])).called(1);
    });

    test('returns cached data when offline', () async {
      when(() => mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      when(() => mockLocalSource.getCachedEntries())
          .thenAnswer((_) async => [testEntryModel]);

      final result = await repository.getEntries();

      expect(result, [testEntry]);
      verifyNever(() => mockRemoteSource.getEntries());
    });
  });
}
```

## Best Practices

1. **Keep layers independent** - Domain has no Flutter dependencies
2. **Use contracts** - Abstract repositories for testing
3. **Map at boundaries** - Convert models ↔ entities at data layer
4. **Handle errors at each layer** - Catch and wrap appropriately
5. **Inject dependencies** - Use Riverpod for DI
6. **Test each layer** - Unit tests for all layers
