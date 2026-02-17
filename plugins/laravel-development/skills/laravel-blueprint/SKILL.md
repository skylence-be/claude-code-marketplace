---
name: laravel-blueprint
description: Master Laravel Blueprint - the AI planning format for generating accurate, production-ready Laravel 12 code. Use when planning complex Laravel implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: laravel
tags: [laravel, blueprint, ai, planning, architecture, specification, scaffolding]
related_skills: [eloquent-relationships, laravel-api-design, laravel-testing-patterns, laravel-coding-standards, laravel-security-patterns, laravel-queues-jobs, laravel-caching-strategies]
---

# Laravel Blueprint

Laravel Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Laravel 12 projects. It bridges the gap between high-level requirements and production-ready code by specifying every model, controller, route, service, and test before a single line is written.

## When to Use This Skill

- Planning new Laravel 12 applications from scratch
- Creating detailed specifications before writing code
- Scaffolding models, controllers, migrations, and tests
- Documenting architecture decisions and data flows
- Ensuring all implementation details are captured (namespaces, relationships, validation, indexes)
- Avoiding vague plans that lead to vague code
- Generating `draft.yaml` files for `laravel-shift/blueprint` code generation

## Blueprint Plan Structure

A complete Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# Task Management Platform

A multi-tenant SaaS for managing projects and tasks with team collaboration.

## Key Decisions
- Multi-tenant via team_id scoping (not separate databases)
- RESTful API with Sanctum token authentication
- Architecture: MVC + Service Layer + Action classes
- Frontend: Inertia.js with Vue 3
- Queue driver: Redis via Horizon
- Monetary values stored as cents (integers)
- UUIDs for public-facing identifiers, auto-increment for internal
- Pest for testing, Larastan level 6 for static analysis
```

### 2. User Flows

Document step-by-step interactions:

```markdown
## User Flows

### Creating a Project
1. User navigates to /projects/create
2. Fills in project name (required, max 255)
3. Selects team members (multi-select, searchable)
4. Chooses visibility: public or private
5. Optionally sets a deadline (date picker, must be future)
6. System creates project, assigns creator as owner
7. Redirects to /projects/{project} with success notification

### Assigning a Task
1. User opens project task board
2. Clicks "New Task" button
3. Fills in: title (required), description (rich text), priority (enum), due_date (optional)
4. Assigns to team member (select, filtered by project members)
5. System creates task with status "todo"
6. Dispatches NotifyAssignee job to queue
7. Task appears on board in "Todo" column
```

### 3. Artisan Commands

Sequential commands for scaffolding:

```markdown
## Commands

php artisan make:model Team -mf --no-interaction
php artisan make:model Project -mf --no-interaction
php artisan make:model Task -mf --no-interaction
php artisan make:model Comment -mf --no-interaction
php artisan make:model Label -mf --no-interaction

php artisan make:controller Api/V1/ProjectController --api --no-interaction
php artisan make:controller Api/V1/TaskController --api --no-interaction
php artisan make:controller Api/V1/CommentController --api --no-interaction

php artisan make:request StoreProjectRequest --no-interaction
php artisan make:request UpdateProjectRequest --no-interaction
php artisan make:request StoreTaskRequest --no-interaction
php artisan make:request UpdateTaskRequest --no-interaction

php artisan make:resource ProjectResource --no-interaction
php artisan make:resource TaskResource --no-interaction
php artisan make:resource CommentResource --no-interaction

php artisan make:policy ProjectPolicy --model=Project --no-interaction
php artisan make:policy TaskPolicy --model=Task --no-interaction

php artisan make:action CreateProjectAction --no-interaction
php artisan make:action AssignTaskAction --no-interaction
# Note: make:action requires nunomaduro/essentials or lorisleiva/laravel-actions
# Without these packages, create Action classes manually in app/Actions/

php artisan make:job NotifyAssignee --no-interaction
php artisan make:event TaskStatusChanged --no-interaction
php artisan make:listener LogTaskStatusChange --event=TaskStatusChanged --no-interaction

php artisan make:mail TaskAssigned --markdown=emails.task-assigned --no-interaction
```

### 4. Models Specification

Include exact attributes, relationships, casts, and scopes:

```markdown
## Models

### Team
**Table**: teams

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigIncrements | primary |
| name | string | required |
| slug | string | required, unique |
| owner_id | foreignId | required, constrained to users |
| created_at | timestamp | |
| updated_at | timestamp | |

**Relationships**:
- belongsTo: User (as owner)
- belongsToMany: User (as members, pivot: team_user with role column)
- hasMany: Project

**Scopes**:
- forUser($user): where user is owner or member

---

### Project
**Table**: projects

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigIncrements | primary |
| uuid | uuid | unique, index |
| team_id | foreignId | required, constrained, cascadeOnDelete |
| name | string:255 | required |
| description | text | nullable |
| status | string | default: active, index |
| visibility | string | default: private |
| deadline | date | nullable |
| created_at | timestamp | |
| updated_at | timestamp | |
| deleted_at | timestamp | nullable |

**Relationships**:
- belongsTo: Team
- hasMany: Task
- belongsToMany: Label

**Casts**:
- status: ProjectStatus::class (enum)
- visibility: ProjectVisibility::class (enum)
- deadline: date

**Scopes**:
- active(): where status = active
- visible($user): where visibility = public OR team member

**Traits**: SoftDeletes

**UUID Setup** (for public-facing uuid column while keeping auto-increment id):
```php
protected static function booted(): void
{
    static::creating(fn (Project $project) => $project->uuid ??= (string) Str::uuid());
}
public function getRouteKeyName(): string { return 'uuid'; }
```

---

### Task
**Table**: tasks

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigIncrements | primary |
| uuid | uuid | unique, index |
| project_id | foreignId | required, constrained, cascadeOnDelete |
| assigned_to | foreignId | nullable, constrained to users |
| title | string:255 | required |
| description | longText | nullable |
| status | string | default: todo, index |
| priority | string | default: medium, index |
| position | integer | default: 0 |
| due_date | date | nullable |
| completed_at | timestamp | nullable |
| created_at | timestamp | |
| updated_at | timestamp | |

**Relationships**:
- belongsTo: Project
- belongsTo: User (as assignee)
- hasMany: Comment
- belongsToMany: Label

**Casts**:
- status: TaskStatus::class (enum)
- priority: TaskPriority::class (enum)
- due_date: date
- completed_at: datetime

**Scopes**:
- overdue(): where due_date < today AND status != done
- forStatus($status): where status = $status
```

### 5. Enums

Define all enums with backed values:

```markdown
## Enums

### TaskStatus
**File**: app/Enums/TaskStatus.php
Backed by: string

| Case | Value | Label |
|------|-------|-------|
| Todo | todo | To Do |
| InProgress | in_progress | In Progress |
| InReview | in_review | In Review |
| Done | done | Done |
| Cancelled | cancelled | Cancelled |

### TaskPriority
**File**: app/Enums/TaskPriority.php
Backed by: string

| Case | Value | Label |
|------|-------|-------|
| Low | low | Low |
| Medium | medium | Medium |
| High | high | High |
| Critical | critical | Critical |

### ProjectStatus
**File**: app/Enums/ProjectStatus.php
Backed by: string

| Case | Value | Label |
|------|-------|-------|
| Active | active | Active |
| Archived | archived | Archived |
| Completed | completed | Completed |

### ProjectVisibility
**File**: app/Enums/ProjectVisibility.php
Backed by: string

| Case | Value | Label |
|------|-------|-------|
| Public | public | Public |
| Private | private | Private |
```

### 6. Service & Action Classes

```markdown
## Services

### ProjectService
**File**: app/Services/ProjectService.php

- create(User $user, array $data): Project -- delegates to CreateProjectAction
- archive(Project $project): void -- sets status, dispatches ArchiveNotification
- addMember(Project $project, User $user): void -- syncs team membership

### TaskService
**File**: app/Services/TaskService.php

- create(Project $project, array $data): Task -- validates, creates, dispatches job
- assign(Task $task, User $user): void -- delegates to AssignTaskAction
- transition(Task $task, TaskStatus $status): void -- validates transition, fires event

## Actions

### CreateProjectAction
**File**: app/Actions/CreateProjectAction.php

- execute(User $user, array $data): Project
- Creates project with team association
- Sets creator as project owner
- Returns created project

### AssignTaskAction
**File**: app/Actions/AssignTaskAction.php

- execute(Task $task, User $user): Task
- Validates user belongs to project team
- Updates assigned_to
- Dispatches NotifyAssignee job
- Returns updated task
```

### 7. API Routes & Controllers

```markdown
## Routes

### routes/api.php

Route::prefix('v1')->middleware('auth:sanctum')->group(function () {
    Route::apiResource('projects', ProjectController::class);
    Route::apiResource('projects.tasks', TaskController::class)->shallow();
    Route::apiResource('tasks.comments', CommentController::class)->shallow();
    Route::post('tasks/{task}/assign', [TaskController::class, 'assign']);
    Route::patch('tasks/{task}/transition', [TaskController::class, 'transition']);
});

## Controllers

### ProjectController
**File**: app/Http/Controllers/Api/V1/ProjectController.php
**Middleware**: auth:sanctum

| Method | Route | Action | Request Class | Response |
|--------|-------|--------|---------------|----------|
| index | GET /api/v1/projects | List user's projects | -- | ProjectResource::collection, paginated |
| store | POST /api/v1/projects | Create project | StoreProjectRequest | ProjectResource, 201 |
| show | GET /api/v1/projects/{project} | Show project | -- | ProjectResource |
| update | PUT /api/v1/projects/{project} | Update project | UpdateProjectRequest | ProjectResource |
| destroy | DELETE /api/v1/projects/{project} | Soft-delete project | -- | 204 |

### TaskController
**File**: app/Http/Controllers/Api/V1/TaskController.php

| Method | Route | Action | Request Class | Response |
|--------|-------|--------|---------------|----------|
| index | GET /api/v1/projects/{project}/tasks | List project tasks | -- | TaskResource::collection, paginated |
| store | POST /api/v1/projects/{project}/tasks | Create task | StoreTaskRequest | TaskResource, 201 |
| show | GET /api/v1/tasks/{task} | Show task | -- | TaskResource |
| update | PUT /api/v1/tasks/{task} | Update task | UpdateTaskRequest | TaskResource |
| destroy | DELETE /api/v1/tasks/{task} | Delete task | -- | 204 |
| assign | POST /api/v1/tasks/{task}/assign | Assign task | AssignTaskRequest | TaskResource |
| transition | PATCH /api/v1/tasks/{task}/transition | Change status | TransitionTaskRequest | TaskResource |
```

### 8. Form Requests & Validation

```markdown
## Form Requests

### StoreProjectRequest
**File**: app/Http/Requests/StoreProjectRequest.php

| Field | Rules |
|-------|-------|
| name | ['required', 'string', 'max:255'] |
| description | ['nullable', 'string', 'max:5000'] |
| visibility | ['required', Rule::enum(ProjectVisibility::class)] |
| deadline | ['nullable', 'date', 'after:today'] |
| member_ids | ['nullable', 'array'] |
| member_ids.* | ['exists:users,id'] |

**authorize()**: return $this->user()->can('create', Project::class);

### StoreTaskRequest
**File**: app/Http/Requests/StoreTaskRequest.php

| Field | Rules |
|-------|-------|
| title | ['required', 'string', 'max:255'] |
| description | ['nullable', 'string'] |
| priority | ['required', Rule::enum(TaskPriority::class)] |
| assigned_to | ['nullable', 'exists:users,id'] |
| due_date | ['nullable', 'date', 'after_or_equal:today'] |
| label_ids | ['nullable', 'array'] |
| label_ids.* | ['exists:labels,id'] |

**authorize()**: return $this->user()->can('create', [Task::class, $this->route('project')]);
```

### 9. API Resources

```markdown
## API Resources

### ProjectResource
**File**: app/Http/Resources/ProjectResource.php

| Field | Source | Conditional |
|-------|--------|-------------|
| id | $this->uuid | no |
| name | $this->name | no |
| description | $this->description | no |
| status | $this->status->value | no |
| visibility | $this->visibility->value | no |
| deadline | $this->deadline?->toDateString() | no |
| tasks_count | $this->whenCounted('tasks') | yes |
| team | TeamResource($this->whenLoaded('team')) | yes |
| tasks | TaskResource::collection($this->whenLoaded('tasks')) | yes |
| created_at | $this->created_at->toIso8601String() | no |
| updated_at | $this->updated_at->toIso8601String() | no |

### TaskResource
**File**: app/Http/Resources/TaskResource.php

| Field | Source | Conditional |
|-------|--------|-------------|
| id | $this->uuid | no |
| title | $this->title | no |
| status | $this->status->value | no |
| priority | $this->priority->value | no |
| due_date | $this->due_date?->toDateString() | no |
| is_overdue | due_date past AND status != Done | no |
| assignee | UserResource($this->whenLoaded('assignee')) | yes |
| comments_count | $this->whenCounted('comments') | yes |
| labels | LabelResource::collection($this->whenLoaded('labels')) | yes |
| completed_at | $this->completed_at?->toIso8601String() | no |
```

### 10. Authorization

```markdown
## Authorization

### ProjectPolicy
**File**: app/Policies/ProjectPolicy.php

| Method | Condition |
|--------|-----------|
| viewAny | authenticated user |
| view | user is team member OR project visibility = public |
| create | authenticated user |
| update | user is team owner or admin role |
| delete | user is team owner |
| restore | user is team owner |
| forceDelete | user is team owner |

### TaskPolicy
**File**: app/Policies/TaskPolicy.php

| Method | Condition |
|--------|-----------|
| viewAny | user is project team member |
| view | user is project team member |
| create | user is project team member |
| update | user is assignee OR project team admin/owner |
| delete | user is project team admin/owner |
| assign | user is project team admin/owner |
| transition | user is assignee OR project team admin/owner |
```

### 11. Testing Strategy

```markdown
## Testing

### ProjectControllerTest (Feature)

**CRUD Tests**:
- can list projects for authenticated user
- cannot list projects when unauthenticated (401)
- can create project with valid data (201)
- cannot create project with invalid data (422)
- can view project as team member
- cannot view private project as non-member (403)
- can update project as team owner
- cannot update project as regular member (403)
- can soft-delete project as team owner (204)

**Validation Tests** (dataset pattern):
- required fields: name, visibility
- invalid enum values rejected
- deadline must be future date

**Scope Tests**:
- index only returns user's team projects
- archived projects excluded by default

### TaskControllerTest (Feature)

**CRUD Tests**:
- can list tasks for project member
- can create task with all fields
- can assign task to team member
- cannot assign task to non-team-member (422)

**Transition Tests**:
- can transition from todo to in_progress
- cannot transition from done to todo (invalid)
- transition to done sets completed_at timestamp

**Authorization Tests**:
- only assignee or admin can update task
- only admin/owner can delete task
```

### 12. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Register user and create team
2. [ ] Create project with members
3. [ ] Create tasks with different priorities
4. [ ] Assign task to team member
5. [ ] Verify notification dispatched
6. [ ] Transition task through all statuses
7. [ ] Verify completed_at set when done
8. [ ] Soft-delete project, confirm tasks cascade
9. [ ] API returns proper pagination headers
10. [ ] Unauthenticated requests return 401

### Automated
php artisan test --parallel
./vendor/bin/phpstan analyse --level=6
./vendor/bin/pint --test
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns.

### VAGUE PLAN (Before Blueprint)

```markdown
## Task Management App
- Users can create projects
- Projects have tasks
- Tasks can be assigned
- API with authentication
- Role-based permissions
```

**Problems:**
- No model columns, types, or constraints defined
- No relationship cardinality or foreign key details
- No validation rules for any field
- No enum definitions for statuses/priorities
- No API route structure or response formats
- No authorization conditions specified
- No test strategy defined

### BLUEPRINT (Implementation-Ready)

```markdown
## Task Model
**Table**: tasks

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigIncrements | primary |
| uuid | uuid | unique, index |
| project_id | foreignId | required, constrained, cascadeOnDelete |
| assigned_to | foreignId | nullable, constrained to users, nullOnDelete |
| title | string:255 | required |
| status | string | default: todo, index |
| priority | string | default: medium, index |
| due_date | date | nullable |
| completed_at | timestamp | nullable |

**Casts**: status -> TaskStatus::class, priority -> TaskPriority::class
**Scopes**: overdue(), forStatus($status), forPriority($priority)

### StoreTaskRequest Validation
| Field | Rules |
|-------|-------|
| title | ['required', 'string', 'max:255'] |
| priority | ['required', Rule::enum(TaskPriority::class)] |
| assigned_to | ['nullable', 'exists:users,id', new TeamMemberRule($project)] |
| due_date | ['nullable', 'date', 'after_or_equal:today'] |

### TaskController::store
```php
public function store(StoreTaskRequest $request, Project $project): JsonResponse
{
    $this->authorize('create', [Task::class, $project]);

    $task = $this->taskService->create($project, $request->validated());

    return TaskResource::make($task)
        ->response()
        ->setStatusCode(201);
}
```

### TaskPolicy::update
```php
public function update(User $user, Task $task): bool
{
    return $user->id === $task->assigned_to
        || $task->project->team->isAdminOrOwner($user);
}
```
```

## Architecture Decision Framework

Use this decision tree to select the right architecture for a project:

| Architecture | When to Choose | Team Size | Complexity |
|---|---|---|---|
| **Standard MVC** | Simple CRUD apps, MVPs, prototypes | 1-3 devs | Low |
| **MVC + Service Layer** | Medium apps with reusable business logic | 2-5 devs | Medium |
| **MVC + Actions** | Medium-large apps wanting SRP compliance | 3-8 devs | Medium |
| **Modular Monolith** | Large apps needing domain separation | 5-15 devs | High |
| **Domain-Driven Design** | Complex business domains, enterprise apps | 5+ devs | High |
| **Microservices** | Very large scale, independent team deployment | 10+ devs | Very High |

### Service Layer Pattern

The recommended layered architecture:

```
Controller -> Service -> Action -> Model
     |            |
     v            v
FormRequest   Event/Job/Notification
```

- **Controller**: HTTP request/response only. Calls service, returns resource.
- **Service**: Orchestrates multiple actions for a use case.
- **Action**: Single-responsibility business operation (e.g., `CreateProjectAction`).
- **Model**: Eloquent entity with relationships, scopes, casts, and accessors.

### Frontend Stack Decision

| Stack | Best For | When to Choose |
|---|---|---|
| **Blade** | Simple server-rendered pages, content sites | Minimal JS needed |
| **Livewire** | Interactive forms, dashboards, admin panels | Team prefers PHP |
| **Inertia + Vue/React** | SPAs with Laravel backend, rich interactivity | Team knows JS framework |
| **Filament** | Admin panels, back-office tools | Rapid CRUD development |
| **API-only** | Separate frontend team, mobile + web clients | Multiple consumer apps |

## Project Scaffolding Checklist

### 1. Installation and Foundation

```bash
composer create-project laravel/laravel project-name
cd project-name
cp .env.example .env
php artisan key:generate
```

Configure `.env`:
- `DB_CONNECTION`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`
- `CACHE_STORE=redis`
- `QUEUE_CONNECTION=redis`
- `SESSION_DRIVER=redis`

### 2. Core Package Installation

```bash
# Authentication
composer require laravel/sanctum

# Development tools
composer require --dev laravel-shift/blueprint
composer require --dev pestphp/pest pestphp/pest-plugin-laravel
composer require --dev larastan/larastan
composer require --dev laravel/pint

# Optional but common
composer require spatie/laravel-permission   # roles/permissions
composer require spatie/laravel-data          # DTOs
composer require spatie/laravel-query-builder # API filtering
```

### 3. Testing Setup

```bash
php artisan pest:install
```

Configure `phpunit.xml`:
```xml
<env name="DB_CONNECTION" value="mysql"/>
<env name="DB_DATABASE" value="testing"/>
<env name="QUEUE_CONNECTION" value="sync"/>
<env name="MAIL_MAILER" value="array"/>
<env name="CACHE_STORE" value="array"/>
```

### 4. Static Analysis Setup

Create `phpstan.neon`:
```neon
includes:
    - vendor/larastan/larastan/extension.neon

parameters:
    level: 6
    paths:
        - app/
    excludePaths:
        - vendor/
```

### 5. Code Style Setup

Create `pint.json`:
```json
{
    "preset": "laravel",
    "rules": {
        "ordered_imports": {
            "sort_algorithm": "alpha"
        }
    }
}
```

### 6. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_DATABASE: testing
          MYSQL_ROOT_PASSWORD: password
        ports: ['3306:3306']
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          coverage: xdebug
      - run: composer install --no-interaction
      - run: ./vendor/bin/pint --test
      - run: ./vendor/bin/phpstan analyse
      - run: php artisan test --parallel
```

## Model Design Patterns

### Relationship Planning Guide

| Relationship | When to Use | Example |
|---|---|---|
| `belongsTo` | Child references parent via foreign key | Comment belongs to Post |
| `hasOne` | Parent has exactly one child | User has one Profile |
| `hasMany` | Parent has multiple children | Post has many Comments |
| `belongsToMany` | Many-to-many via pivot table | User belongs to many Roles |
| `hasOneThrough` | Access distant relation through intermediate | Country has one latest Post through User |
| `hasManyThrough` | Access distant relations through intermediate | Country has many Posts through Users |
| `morphOne` | Polymorphic one-to-one | Image morphs to User or Post |
| `morphMany` | Polymorphic one-to-many | Comment morphs to Post or Video |
| `morphToMany` | Polymorphic many-to-many | Tag morphs to many Post, Video |

### Model Specification Template

```markdown
### ModelName
**Table**: table_name

| Column | Type | Constraints |
|--------|------|-------------|
| id | bigIncrements | primary |
| foreign_id | foreignId | constrained, cascadeOnDelete |
| name | string:255 | required |
| status | string | default: value, index |
| amount | integer | default: 0 (cents) |
| created_at | timestamp | |
| updated_at | timestamp | |

**Relationships**: belongsTo: Parent | hasMany: Child | belongsToMany: Related
**Casts**: status -> StatusEnum::class, amount -> integer
**Scopes**: active(), forStatus($status)
**Traits**: SoftDeletes, HasUuids
**Observers**: ModelObserver (creating, updating)
**Accessors**: formatted_amount: $this->amount / 100
```

### Eager Loading Rules

Always eager load relationships to avoid N+1 queries:

```php
// In controller
$projects = Project::with(['team', 'tasks' => function ($query) {
    $query->withCount('comments');
}])->paginate(15);

// In API Resource
'tasks' => TaskResource::collection($this->whenLoaded('tasks')),
'tasks_count' => $this->whenCounted('tasks'),
```

### Factory States Pattern

```php
class TaskFactory extends Factory
{
    public function definition(): array
    {
        return [
            'project_id' => Project::factory(),
            'title' => fake()->sentence(),
            'status' => TaskStatus::Todo,
            'priority' => TaskPriority::Medium,
        ];
    }

    public function highPriority(): static
    {
        return $this->state(fn () => ['priority' => TaskPriority::Critical]);
    }

    public function completed(): static
    {
        return $this->state(fn () => [
            'status' => TaskStatus::Done,
            'completed_at' => now(),
        ]);
    }

    public function overdue(): static
    {
        return $this->state(fn () => [
            'due_date' => now()->subDays(3),
            'status' => TaskStatus::InProgress,
        ]);
    }
}
```

## API Design Patterns

### Route Organization

```php
// routes/api.php
Route::prefix('v1')->as('api.v1.')->group(function () {
    // Public routes
    Route::post('login', [AuthController::class, 'login']);
    Route::post('register', [AuthController::class, 'register']);

    // Authenticated routes
    Route::middleware('auth:sanctum')->group(function () {
        Route::apiResource('projects', ProjectController::class);
        Route::apiResource('projects.tasks', TaskController::class)->shallow();
        Route::apiResource('tasks.comments', CommentController::class)->shallow();

        // Custom actions
        Route::post('tasks/{task}/assign', [TaskController::class, 'assign']);
        Route::patch('tasks/{task}/transition', [TaskController::class, 'transition']);
    });
});
```

### Controller Pattern

```php
class ProjectController extends Controller
{
    public function __construct(
        private readonly ProjectService $projectService,
    ) {}

    public function index(Request $request): AnonymousResourceCollection
    {
        $projects = $request->user()
            ->projects()
            ->with(['team', 'tasks'])
            ->withCount('tasks')
            ->latest()
            ->paginate(15);

        return ProjectResource::collection($projects);
    }

    public function store(StoreProjectRequest $request): JsonResponse
    {
        $project = $this->projectService->create(
            $request->user(),
            $request->validated(),
        );

        return ProjectResource::make($project)
            ->response()
            ->setStatusCode(201);
    }

    public function show(Project $project): ProjectResource
    {
        $this->authorize('view', $project);

        return ProjectResource::make(
            $project->load(['team.members', 'tasks.assignee']),
        );
    }

    public function update(UpdateProjectRequest $request, Project $project): ProjectResource
    {
        $project->update($request->validated());

        return ProjectResource::make($project->fresh());
    }

    public function destroy(Project $project): Response
    {
        $this->authorize('delete', $project);

        $project->delete();

        return response()->noContent();
    }
}
```

### API Resource Pattern

```php
class ProjectResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->uuid,
            'name' => $this->name,
            'description' => $this->description,
            'status' => $this->status->value,
            'visibility' => $this->visibility->value,
            'deadline' => $this->deadline?->toDateString(),
            'tasks_count' => $this->whenCounted('tasks'),
            'team' => new TeamResource($this->whenLoaded('team')),
            'tasks' => TaskResource::collection($this->whenLoaded('tasks')),
            'created_at' => $this->created_at->toIso8601String(),
            'updated_at' => $this->updated_at->toIso8601String(),
        ];
    }
}
```

### HTTP Status Code Reference

| Code | When to Return | Example |
|------|---------------|---------|
| 200 | Successful GET, PUT, PATCH | Fetching or updating a resource |
| 201 | Successful POST (resource created) | Creating a new project |
| 204 | Successful DELETE (no content) | Deleting a resource |
| 401 | Unauthenticated | Missing or invalid token |
| 403 | Forbidden | User lacks permission |
| 404 | Not found | Resource does not exist |
| 422 | Validation failed | Invalid form data |
| 429 | Rate limited | Too many requests |

### Always Paginate

Never return unbounded result sets from API endpoints:

```php
// Good
$projects = Project::paginate(15);
$projects = Project::cursorPaginate(15); // for large datasets

// Bad -- never do this for collections
$projects = Project::all();
```

## Testing Strategy

### Testing Pyramid

```
         /  E2E (Dusk)  \         <- Few, slow, expensive
        /  Feature Tests  \       <- Many, moderate speed (PRIORITY)
       /    Unit Tests     \      <- Many, fast, focused
      / Static Analysis     \     <- Automated, instant
     / Code Style (Pint)     \    <- Automated, instant
```

### Feature Test Patterns with Pest

#### CRUD Test Pattern

```php
use App\Models\User;
use App\Models\Project;

beforeEach(function () {
    $this->user = User::factory()->create();
    $this->actingAs($this->user);
});

it('can list projects', function () {
    Project::factory()->count(3)->for($this->user->teams()->first())->create();

    $this->getJson('/api/v1/projects')
        ->assertOk()
        ->assertJsonCount(3, 'data')
        ->assertJsonStructure([
            'data' => [['id', 'name', 'status', 'created_at']],
            'meta' => ['current_page', 'last_page', 'per_page', 'total'],
        ]);
});

it('can create a project with valid data', function () {
    $this->postJson('/api/v1/projects', [
        'name' => 'New Project',
        'visibility' => 'private',
    ])
        ->assertCreated()
        ->assertJsonPath('data.name', 'New Project')
        ->assertJsonPath('data.status', 'active');

    $this->assertDatabaseHas('projects', ['name' => 'New Project']);
});

it('returns 422 for invalid data', function () {
    $this->postJson('/api/v1/projects', [
        'name' => '',
    ])
        ->assertUnprocessable()
        ->assertJsonValidationErrors(['name', 'visibility']);
});

it('returns 401 when unauthenticated', function () {
    auth()->forgetGuards();

    $this->getJson('/api/v1/projects')
        ->assertUnauthorized();
});
```

#### Dataset Pattern for Validation

```php
it('validates required fields', function (string $field) {
    $this->postJson('/api/v1/projects', [$field => null])
        ->assertUnprocessable()
        ->assertJsonValidationErrors([$field]);
})->with(['name', 'visibility']);

it('validates enum fields', function (string $field, string $invalidValue) {
    $this->postJson('/api/v1/projects', [
        'name' => 'Test',
        'visibility' => 'private',
        $field => $invalidValue,
    ])
        ->assertUnprocessable()
        ->assertJsonValidationErrors([$field]);
})->with([
    ['visibility', 'invalid_visibility'],
    ['status', 'nonexistent_status'],
]);
```

#### Authorization Test Pattern

```php
it('allows team owner to update project', function () {
    $project = Project::factory()->create(['team_id' => $this->user->ownedTeams->first()->id]);

    $this->putJson("/api/v1/projects/{$project->uuid}", [
        'name' => 'Updated Name',
    ])->assertOk();
});

it('forbids non-admin from updating project', function () {
    $project = Project::factory()->create(); // different team

    $this->putJson("/api/v1/projects/{$project->uuid}", [
        'name' => 'Updated Name',
    ])->assertForbidden();
});

it('forbids non-admin from deleting project', function () {
    $project = Project::factory()->create();

    $this->deleteJson("/api/v1/projects/{$project->uuid}")
        ->assertForbidden();
});
```

#### Action/Service Unit Test Pattern

```php
use App\Actions\AssignTaskAction;
use App\Models\Task;
use App\Models\User;
use App\Jobs\NotifyAssignee;

it('assigns a task and dispatches notification', function () {
    Queue::fake();

    $task = Task::factory()->create();
    $user = User::factory()->create();
    $task->project->team->members()->attach($user);

    $action = new AssignTaskAction();
    $result = $action->execute($task, $user);

    expect($result->assigned_to)->toBe($user->id);
    Queue::assertPushed(NotifyAssignee::class);
});

it('throws exception when assigning to non-team-member', function () {
    $task = Task::factory()->create();
    $outsider = User::factory()->create();

    $action = new AssignTaskAction();
    $action->execute($task, $outsider);
})->throws(ValidationException::class);
```

#### HTTP Mock Pattern

```php
use Illuminate\Support\Facades\Http;

it('fetches external project data', function () {
    Http::fake([
        'api.example.com/projects/*' => Http::response([
            'name' => 'External Project',
            'status' => 'active',
        ]),
    ]);

    $this->getJson('/api/v1/import/external/123')
        ->assertOk()
        ->assertJsonPath('data.name', 'External Project');

    Http::assertSent(fn ($request) =>
        $request->url() === 'https://api.example.com/projects/123'
    );
});
```

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| Missing column types and constraints | Implementing agent guesses schema | Specify every column with type, length, nullable, default, index |
| Vague relationship definitions | Wrong cardinality or missing pivots | State exact type: `belongsToMany: Role (pivot: role_user with expires_at)` |
| No enum definitions | Inconsistent status/type values | Define all enums with backed values and cases |
| Missing validation rules | Inconsistent data integrity | Specify rules array for every form request field |
| No authorization conditions | Vague "admin only" rules | State exact condition: `user.id === project.team.owner_id` |
| Missing API response format | Inconsistent JSON structure | Define API Resource with exact fields and conditional includes |
| No eager loading plan | N+1 queries in production | Specify `with()` calls for every controller method |
| Skipping factory states | Hard to write focused tests | Define states for each meaningful variation (completed, overdue, etc.) |
| No error response format | Inconsistent error handling | Define standard error envelope: `{ message, errors }` |
| Missing indexes | Slow queries on filtered columns | Add index to every column used in where, orderBy, or unique constraints |
| No migration order | Foreign key failures | List migrations in dependency order (parents before children) |
| Missing cascade rules | Orphaned records on delete | Specify cascadeOnDelete, nullOnDelete, or restrictOnDelete for every foreign key |

## Best Practices

1. **Be explicit about every column** - Include type, length, nullable, default, and index for every database column
2. **Define all enums upfront** - List every case with its backed value before writing any model
3. **Specify complete validation rules** - Use array notation, include custom rules, reference Laravel's Rule class
4. **Document relationships bidirectionally** - If Post hasMany Comments, also show Comment belongsTo Post
5. **Include API response structures** - Show exact JSON shape with `whenLoaded`, `whenCounted` patterns
6. **Plan eager loading per endpoint** - Every controller method should specify its `with()` and `withCount()` calls
7. **Use factory states** - Define states for every meaningful model variation (draft, published, overdue, cancelled)
8. **Specify authorization conditions in plain English** - "user is team owner OR user has admin role on team"
9. **Include artisan commands in order** - Models first (parents before children), then controllers, then policies
10. **Map status transitions** - Document which status changes are valid and what side effects they trigger
11. **Always paginate API collections** - Specify page size and cursor vs offset pagination
12. **Test with datasets** - Use Pest dataset pattern for validation and enum testing
13. **Plan in dependency order** - Enums -> Models -> Services/Actions -> Controllers -> Policies -> Tests
14. **Include CI/CD configuration** - GitHub Actions workflow with Pint, Larastan, and Pest

## Anti-Patterns to Avoid

| Vague | Blueprint |
|-------|-----------|
| "users can create projects" | `POST /api/v1/projects` with StoreProjectRequest validation, 201 response, ProjectResource format |
| "tasks have statuses" | `TaskStatus` enum: Todo, InProgress, InReview, Done, Cancelled (string-backed) |
| "role-based permissions" | ProjectPolicy::update returns true when `$user->id === $project->team->owner_id` |
| "searchable dropdown" | `->relationship('team', 'name')->searchable()->preload()->required()` |
| "validate the request" | `['required', 'string', 'max:255']` for name, `[Rule::enum(TaskPriority::class)]` for priority |
| "return JSON response" | `ProjectResource::make($project)->response()->setStatusCode(201)` |
| "add tests" | Feature test: CRUD endpoints + authorization + validation datasets + service unit tests |
| "handle errors" | 401 unauthenticated, 403 forbidden, 404 not found, 422 validation, standard error envelope |
| "send notification" | `NotifyAssignee` job dispatched to Redis queue with `$task` and `$assignee` data |
| "cache the results" | `Cache::remember("projects.{$teamId}", 3600, fn () => ...)` with cache invalidation on update |

## Common Patterns

### Enum with Backed Values

```php
namespace App\Enums;

enum TaskStatus: string
{
    case Todo = 'todo';
    case InProgress = 'in_progress';
    case InReview = 'in_review';
    case Done = 'done';
    case Cancelled = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::Todo => 'To Do',
            self::InProgress => 'In Progress',
            self::InReview => 'In Review',
            self::Done => 'Done',
            self::Cancelled => 'Cancelled',
        };
    }
}
```

### Action Class

```php
namespace App\Actions;

use App\Models\Project;
use App\Models\User;

class CreateProjectAction
{
    public function execute(User $user, array $data): Project
    {
        $project = $user->ownedTeams()->first()->projects()->create([
            'name' => $data['name'],
            'description' => $data['description'] ?? null,
            'visibility' => $data['visibility'],
            'deadline' => $data['deadline'] ?? null,
        ]);

        if (! empty($data['member_ids'])) {
            $project->team->members()->syncWithoutDetaching($data['member_ids']);
        }

        return $project;
    }
}
```

### Scoped Queries

```php
// Model scope
public function scopeOverdue(Builder $query): Builder
{
    return $query->where('due_date', '<', now())
        ->whereNot('status', TaskStatus::Done);
}

// Usage in controller
$overdueTasks = Task::overdue()
    ->with('assignee')
    ->orderBy('due_date')
    ->paginate(15);
```

### Event + Listener Pattern

```php
// Event
class TaskStatusChanged
{
    public function __construct(
        public readonly Task $task,
        public readonly TaskStatus $oldStatus,
        public readonly TaskStatus $newStatus,
    ) {}
}

// Dispatching
TaskStatusChanged::dispatch($task, $oldStatus, $newStatus);

// Listener
class LogTaskStatusChange
{
    public function handle(TaskStatusChanged $event): void
    {
        activity()
            ->performedOn($event->task)
            ->withProperties([
                'old_status' => $event->oldStatus->value,
                'new_status' => $event->newStatus->value,
            ])
            ->log('Task status changed');
    }
}
```

### Monetary Values

```php
// Migration
$table->integer('amount')->default(0); // stored as cents

// Model accessor
protected function formattedAmount(): Attribute
{
    return Attribute::get(fn () => number_format($this->amount / 100, 2));
}

// API Resource
'amount' => $this->amount,               // raw cents for API consumers
'amount_formatted' => '$' . number_format($this->amount / 100, 2),
```

### Rate Limiting

```php
// In AppServiceProvider or RouteServiceProvider
RateLimiter::for('api', function (Request $request) {
    return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
});

// In route
Route::middleware(['auth:sanctum', 'throttle:api'])->group(function () {
    // ...
});
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Enums (4)
- app/Enums/TaskStatus.php
- app/Enums/TaskPriority.php
- app/Enums/ProjectStatus.php
- app/Enums/ProjectVisibility.php

### Models (5)
- app/Models/Team.php
- app/Models/Project.php
- app/Models/Task.php
- app/Models/Comment.php
- app/Models/Label.php

### Controllers (3)
- app/Http/Controllers/Api/V1/ProjectController.php
- app/Http/Controllers/Api/V1/TaskController.php
- app/Http/Controllers/Api/V1/CommentController.php

### Form Requests (4)
- app/Http/Requests/StoreProjectRequest.php
- app/Http/Requests/UpdateProjectRequest.php
- app/Http/Requests/StoreTaskRequest.php
- app/Http/Requests/UpdateTaskRequest.php

### API Resources (4)
- app/Http/Resources/ProjectResource.php
- app/Http/Resources/TaskResource.php
- app/Http/Resources/CommentResource.php
- app/Http/Resources/TeamResource.php

### Services (2)
- app/Services/ProjectService.php
- app/Services/TaskService.php

### Actions (2)
- app/Actions/CreateProjectAction.php
- app/Actions/AssignTaskAction.php

### Policies (2)
- app/Policies/ProjectPolicy.php
- app/Policies/TaskPolicy.php

### Events & Listeners (2)
- app/Events/TaskStatusChanged.php
- app/Listeners/LogTaskStatusChange.php

### Jobs & Mail (2)
- app/Jobs/NotifyAssignee.php
- app/Mail/TaskAssigned.php

### Migrations (6)
- database/migrations/xxxx_create_teams_table.php
- database/migrations/xxxx_create_team_user_table.php
- database/migrations/xxxx_create_projects_table.php
- database/migrations/xxxx_create_tasks_table.php
- database/migrations/xxxx_create_comments_table.php
- database/migrations/xxxx_create_labels_table.php

### Factories (5)
- database/factories/TeamFactory.php
- database/factories/ProjectFactory.php
- database/factories/TaskFactory.php
- database/factories/CommentFactory.php
- database/factories/LabelFactory.php

### Tests (4)
- tests/Feature/Api/V1/ProjectControllerTest.php
- tests/Feature/Api/V1/TaskControllerTest.php
- tests/Feature/Api/V1/CommentControllerTest.php
- tests/Unit/Actions/AssignTaskActionTest.php

### Configuration (3)
- pint.json
- phpstan.neon
- .github/workflows/ci.yml
```

## Deployment Planning

### Pre-Deployment Checklist

```markdown
## Pre-Deployment

### Environment Configuration
1. [ ] All .env variables documented and set for production
2. [ ] APP_DEBUG=false in production
3. [ ] APP_ENV=production
4. [ ] Database connection verified
5. [ ] Redis connection verified
6. [ ] Mail driver configured
7. [ ] Queue connection set to redis

### Security Checks
1. [ ] `composer audit` passes with no vulnerabilities
2. [ ] CORS configuration reviewed
3. [ ] Rate limiting configured for all API routes
4. [ ] Sanctum token expiration configured
5. [ ] .env, .env.example reviewed for secrets

### Performance
1. [ ] `php artisan config:cache`
2. [ ] `php artisan route:cache`
3. [ ] `php artisan view:cache`
4. [ ] `php artisan event:cache`
5. [ ] Database indexes created for all queried columns
6. [ ] Eager loading verified (no N+1 queries)
```

### CI/CD Pipeline Steps

| Step | Command | Purpose |
|------|---------|---------|
| 1. Code Style | `./vendor/bin/pint --test` | Enforce formatting |
| 2. Static Analysis | `./vendor/bin/phpstan analyse --level=6` | Catch type errors |
| 3. Tests | `php artisan test --parallel` | Verify behavior |
| 4. Security Audit | `composer audit` | Check vulnerabilities |
| 5. Build Assets | `npm run build` | Compile frontend |
| 6. Deploy | Platform-specific (Envoyer, Forge, Cloud) | Ship to production |
| 7. Post-Deploy | `php artisan migrate --force` | Run migrations |
| 8. Monitor | Check Sentry/Pulse for errors | Verify health |

### Deployment Strategy Options

| Strategy | Description | Best For |
|---|---|---|
| **Atomic Symlink** | Symlink switch to new release directory | Standard Laravel deploys |
| **Blue-Green** | Two identical environments, switch traffic | Zero-downtime, instant rollback |
| **Rolling** | Gradual update across instances | Large clusters |
| **Canary** | Route small percentage to new version | Risk-averse releases |

### Recommended Hosting & Tools

| Category | Tool |
|---|---|
| Hosting | Laravel Cloud, Forge, Vapor |
| CI/CD | GitHub Actions, GitLab CI |
| Deployment | Envoyer, Deployer |
| Monitoring | Sentry, Laravel Pulse |
| APM | New Relic, Datadog |
| Queue | Laravel Horizon |
| Logging | Flare, Papertrail |
| Security | `composer audit`, Snyk |
