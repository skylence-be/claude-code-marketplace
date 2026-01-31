---
description: Create Flutter feature module with clean architecture
model: claude-sonnet-4-5
---

Create a new feature module with data/domain/presentation layers.

## Feature Specification

$ARGUMENTS

## Feature Module Structure

### 1. **Directory Structure**

```
lib/features/{feature_name}/
├── data/
│   ├── models/
│   │   └── {name}_model.dart
│   ├── datasources/
│   │   ├── {name}_remote_source.dart
│   │   └── {name}_local_source.dart
│   └── repositories/
│       └── {name}_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── {name}.dart
│   └── repositories/
│       └── {name}_repository.dart
└── presentation/
    ├── providers/
    │   └── {name}_provider.dart
    ├── screens/
    │   └── {name}_screen.dart
    └── widgets/
        └── {name}_card.dart
```

### 2. **Domain Entity**

```dart
// domain/entities/project.dart
import 'package:equatable/equatable.dart';

class Project extends Equatable {
  final String id;
  final String name;
  final String customerId;
  final String? description;
  final bool isActive;
  final DateTime createdAt;

  const Project({
    required this.id,
    required this.name,
    required this.customerId,
    this.description,
    this.isActive = true,
    required this.createdAt,
  });

  Project copyWith({
    String? id,
    String? name,
    String? customerId,
    String? description,
    bool? isActive,
    DateTime? createdAt,
  }) {
    return Project(
      id: id ?? this.id,
      name: name ?? this.name,
      customerId: customerId ?? this.customerId,
      description: description ?? this.description,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [id, name, customerId, description, isActive, createdAt];
}
```

### 3. **Repository Contract**

```dart
// domain/repositories/project_repository.dart
import '../entities/project.dart';

abstract class ProjectRepository {
  Future<List<Project>> getProjects({int? customerId});
  Future<Project> getProject(String id);
  Future<Project> createProject(Project project);
  Future<Project> updateProject(Project project);
  Future<void> deleteProject(String id);
}
```

### 4. **Data Model**

```dart
// data/models/project_model.dart
import 'package:json_annotation/json_annotation.dart';
import '../../domain/entities/project.dart';

part 'project_model.g.dart';

@JsonSerializable()
class ProjectModel {
  final int id;
  final String name;
  @JsonKey(name: 'customer_id')
  final int customerId;
  final String? description;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  const ProjectModel({
    required this.id,
    required this.name,
    required this.customerId,
    this.description,
    this.isActive = true,
    required this.createdAt,
  });

  factory ProjectModel.fromJson(Map<String, dynamic> json) =>
      _$ProjectModelFromJson(json);

  Map<String, dynamic> toJson() => _$ProjectModelToJson(this);

  Project toEntity() {
    return Project(
      id: id.toString(),
      name: name,
      customerId: customerId.toString(),
      description: description,
      isActive: isActive,
      createdAt: createdAt,
    );
  }

  factory ProjectModel.fromEntity(Project entity) {
    return ProjectModel(
      id: int.parse(entity.id),
      name: entity.name,
      customerId: int.parse(entity.customerId),
      description: entity.description,
      isActive: entity.isActive,
      createdAt: entity.createdAt,
    );
  }
}
```

### 5. **Remote Data Source**

```dart
// data/datasources/project_remote_source.dart
import 'package:dio/dio.dart';
import '../models/project_model.dart';

class ProjectRemoteSource {
  final Dio _client;

  ProjectRemoteSource(this._client);

  Future<List<ProjectModel>> getProjects({int? customerId}) async {
    final queryParams = <String, dynamic>{};
    if (customerId != null) {
      queryParams['customer'] = customerId;
    }

    final response = await _client.get(
      '/projects',
      queryParameters: queryParams,
    );

    return (response.data as List)
        .map((json) => ProjectModel.fromJson(json))
        .toList();
  }

  Future<ProjectModel> getProject(int id) async {
    final response = await _client.get('/projects/$id');
    return ProjectModel.fromJson(response.data);
  }

  Future<ProjectModel> createProject(ProjectModel project) async {
    final response = await _client.post(
      '/projects',
      data: project.toJson(),
    );
    return ProjectModel.fromJson(response.data);
  }

  Future<ProjectModel> updateProject(ProjectModel project) async {
    final response = await _client.patch(
      '/projects/${project.id}',
      data: project.toJson(),
    );
    return ProjectModel.fromJson(response.data);
  }

  Future<void> deleteProject(int id) async {
    await _client.delete('/projects/$id');
  }
}
```

### 6. **Repository Implementation**

```dart
// data/repositories/project_repository_impl.dart
import '../../domain/entities/project.dart';
import '../../domain/repositories/project_repository.dart';
import '../datasources/project_remote_source.dart';
import '../models/project_model.dart';

class ProjectRepositoryImpl implements ProjectRepository {
  final ProjectRemoteSource _remoteSource;

  ProjectRepositoryImpl(this._remoteSource);

  @override
  Future<List<Project>> getProjects({int? customerId}) async {
    final models = await _remoteSource.getProjects(customerId: customerId);
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<Project> getProject(String id) async {
    final model = await _remoteSource.getProject(int.parse(id));
    return model.toEntity();
  }

  @override
  Future<Project> createProject(Project project) async {
    final model = ProjectModel.fromEntity(project);
    final created = await _remoteSource.createProject(model);
    return created.toEntity();
  }

  @override
  Future<Project> updateProject(Project project) async {
    final model = ProjectModel.fromEntity(project);
    final updated = await _remoteSource.updateProject(model);
    return updated.toEntity();
  }

  @override
  Future<void> deleteProject(String id) async {
    await _remoteSource.deleteProject(int.parse(id));
  }
}
```

### 7. **Riverpod Provider**

```dart
// presentation/providers/project_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../domain/entities/project.dart';
import '../../domain/repositories/project_repository.dart';
import '../../data/repositories/project_repository_impl.dart';
import '../../data/datasources/project_remote_source.dart';

part 'project_provider.g.dart';

@riverpod
ProjectRemoteSource projectRemoteSource(ProjectRemoteSourceRef ref) {
  final client = ref.watch(dioClientProvider);
  return ProjectRemoteSource(client);
}

@riverpod
ProjectRepository projectRepository(ProjectRepositoryRef ref) {
  return ProjectRepositoryImpl(ref.watch(projectRemoteSourceProvider));
}

@riverpod
Future<List<Project>> projects(ProjectsRef ref, {int? customerId}) async {
  final repository = ref.watch(projectRepositoryProvider);
  return repository.getProjects(customerId: customerId);
}

@riverpod
Future<Project> project(ProjectRef ref, String id) async {
  final repository = ref.watch(projectRepositoryProvider);
  return repository.getProject(id);
}
```

### 8. **Screen Widget**

```dart
// presentation/screens/projects_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/project_provider.dart';
import '../widgets/project_card.dart';

class ProjectsScreen extends ConsumerWidget {
  const ProjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final projectsAsync = ref.watch(projectsProvider());

    return Scaffold(
      appBar: AppBar(
        title: const Text('Projects'),
      ),
      body: projectsAsync.when(
        data: (projects) => projects.isEmpty
            ? const Center(child: Text('No projects found'))
            : ListView.builder(
                itemCount: projects.length,
                itemBuilder: (context, index) {
                  return ProjectCard(project: projects[index]);
                },
              ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $error'),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () => ref.invalidate(projectsProvider()),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

Generate complete feature module with all layers and proper architecture.
