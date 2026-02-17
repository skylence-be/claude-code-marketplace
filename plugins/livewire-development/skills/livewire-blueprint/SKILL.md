---
name: livewire-blueprint
description: Master Livewire Blueprint - the AI planning format for generating accurate, production-ready Livewire v4 code. Use when planning complex Livewire implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: livewire
tags: [livewire, blueprint, ai, planning, architecture, specification, alpine, islands]
related_skills: [livewire-forms-validation, livewire-performance-optimization, livewire4-reactive-patterns]
---

# Livewire Blueprint

Livewire Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Livewire v4 projects. It bridges the gap between high-level requirements and production-ready code.

## When to Use This Skill

- Planning complex Livewire component implementations
- Creating detailed specifications before writing code
- Generating comprehensive component architectures with Alpine.js integration
- Documenting user flows, state management, and real-time interactions
- Ensuring all details are captured (component format, properties, actions, events)
- Avoiding vague plans that lead to vague code
- Deciding between Livewire, Blade, Alpine, or Islands for each UI region

## Blueprint Plan Structure

A complete Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# Task Management Dashboard

A real-time task management dashboard with drag-and-drop columns, inline editing, and team collaboration.

## Key Decisions
- Single-File Components (SFC) as default format
- Islands architecture for independent column updates
- Alpine.js for drag-and-drop and micro-interactions
- Form Objects for task create/edit validation
- Polling on activity feed island (5s interval)
- wire:navigate for SPA-style page transitions
```

### 2. User Flows

Document step-by-step interactions:

```markdown
## User Flows

### Creating a Task
1. User clicks "Add Task" button in a column
2. Alpine.js opens inline form (no server roundtrip)
3. User fills title (required), description (optional), assignee (searchable select)
4. wire:model.blur validates title on blur
5. User clicks "Save" -- calls save() action
6. Server validates via Form Object, creates task, dispatches 'task-created' event
7. Board column island refreshes via event listener
8. Notification toast confirms creation

### Dragging a Task Between Columns
1. User drags task card (Alpine.js + wire:sort)
2. Drop triggers $wire.moveTask(taskId, newStatus, newPosition)
3. Server authorizes move, updates status and sort_order
4. Source and destination column islands refresh
```

### 3. Artisan Commands

Sequential commands for scaffolding:

```markdown
## Commands

php artisan make:livewire task-board --no-interaction
php artisan make:livewire task.create --no-interaction
php artisan make:livewire task.edit --no-interaction
php artisan make:livewire activity-feed --no-interaction
php artisan make:model Task -mf --no-interaction
php artisan make:model TaskComment -mf --no-interaction
php artisan make:policy TaskPolicy --no-interaction
```

### 4. Models Specification

Include exact attributes, relationships, and methods:

```markdown
## Models

### Task
**Table**: tasks

| Column | Type | Constraints |
|--------|------|-------------|
| id | uuid | primary |
| team_id | foreignId | required, constrained |
| creator_id | foreignId | required, constrained (users) |
| assignee_id | foreignId | nullable, constrained (users) |
| title | string | required, max:255 |
| description | text | nullable |
| status | string | default: todo |
| priority | string | default: medium |
| sort_order | integer | default: 0 |
| due_date | date | nullable |

**Relationships**:
- belongsTo: Team, Creator (User), Assignee (User)
- hasMany: TaskComment

**Scopes**:
- forStatus(TaskStatus $status): Filter by status column
- ordered(): Order by sort_order asc

**Traits**: HasUuids, SoftDeletes
```

### 5. Enums

```markdown
## Enums

### TaskStatus

| Case | Label | Color |
|------|-------|-------|
| Todo | To Do | gray |
| InProgress | In Progress | blue |
| Review | In Review | yellow |
| Done | Done | green |

### TaskPriority

| Case | Label | Color | Icon |
|------|-------|-------|------|
| Low | Low | gray | arrow-down |
| Medium | Medium | yellow | minus |
| High | High | orange | arrow-up |
| Urgent | Urgent | red | exclamation-triangle |
```

### 6. Component Specifications

Complete components with properties, actions, and template structure:

```markdown
## Components

### TaskBoard (Full-Page)
**Format**: Single-File Component
**Route**: Route::livewire('/dashboard', 'task-board')->name('dashboard')
**Layout**: layouts::app

#### Properties
| Property | Type | Modifier | Purpose |
|----------|------|----------|---------|
| teamId | int | #[Locked] | Current team ID |
| filterAssignee | ?int | public | Filter by assignee |
| filterPriority | ?string | public | Filter by priority |

#### Computed Properties
| Name | Return Type | Cache | Query |
|------|-------------|-------|-------|
| tasks | Collection | request | Task::forTeam($this->teamId)->with('assignee')->ordered()->get() |
| teamMembers | Collection | persist | User::where('team_id', $this->teamId)->select('id', 'name')->get() |

#### Actions
| Action | Parameters | Authorization | Side Effects |
|--------|-----------|---------------|--------------|
| moveTask | int $taskId, string $status, int $position | TaskPolicy::update | Updates status + sort_order, dispatches 'task-moved' |
| deleteTask | int $taskId | TaskPolicy::delete | Soft deletes, dispatches 'task-deleted' |

#### Template Structure
- Header: title, filter dropdowns (Alpine.js)
- Columns: one @island per TaskStatus
  - Each island: wire:poll.5s, renders filtered tasks
  - Task cards: draggable via wire:sort
- Activity feed sidebar: @island(lazy: true)
```

### 7. Authorization

```markdown
## Authorization

### TaskPolicy
- viewAny: team member
- view: team member
- create: team member
- update: creator or assignee or team admin
- delete: creator or team admin
- moveTask: team member (any member can reorganize)
```

### 8. Events Map

```markdown
## Events

| Event | Dispatched From | Listened By | Payload |
|-------|----------------|-------------|---------|
| task-created | TaskCreate component | TaskBoard islands | taskId, status |
| task-updated | TaskEdit component | TaskBoard islands | taskId |
| task-moved | TaskBoard.moveTask | Activity feed island | taskId, oldStatus, newStatus |
| task-deleted | TaskBoard.deleteTask | TaskBoard islands | taskId, status |
```

### 9. Testing Strategy

```markdown
## Testing

### TaskBoardTest

**Smoke Tests**:
- Board page renders for authenticated team member
- Board page returns 403 for non-team member

**Action Tests**:
- moveTask updates status and sort_order
- moveTask rejects unauthorized user
- deleteTask soft deletes and dispatches event

**Validation Tests**:
- Task creation requires title
- Task title max 255 characters

**Event Tests**:
- task-created event dispatched on save
- task-moved event contains correct payload
```

### 10. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Navigate to /dashboard via wire:navigate
2. [ ] Create task with all fields
3. [ ] Drag task between columns
4. [ ] Verify island-level refresh (no full page re-render)
5. [ ] Inline edit task title
6. [ ] Delete task with confirmation
7. [ ] Filter by assignee
8. [ ] Activity feed loads lazily
9. [ ] Polling updates activity feed

### Automated
php artisan test --filter=TaskBoardTest
php artisan test --filter=TaskCreateTest
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns.

### VAGUE PLAN (Before Blueprint)

```markdown
## Task Board
- Show tasks in columns by status
- Drag and drop between columns
- Create and edit tasks
- Real-time updates
- Activity feed
```

**Problems:**
- No component format decision (SFC vs class-based?)
- No architecture decision (Islands? Nested components? Alpine?)
- No state management strategy (wire:model modifiers? Computed properties?)
- No performance plan (lazy loading? polling interval? debounce?)
- No authorization in actions
- No event communication map

### BLUEPRINT (Implementation-Ready)

**TaskBoard Component**
- **Format**: Single-File Component (.wire.php)
- **Route**: `Route::livewire('/dashboard', 'task-board')`

**Properties**:

| Property | Type | Modifier | Binding |
|----------|------|----------|---------|
| teamId | int | #[Locked] | mount() param |
| filterAssignee | ?int | public | wire:model.live |
| filterPriority | ?string | public | wire:model.live |

**Computed Properties**:

```php
#[Computed]
public function tasks(): Collection
{
    return Task::query()
        ->where('team_id', $this->teamId)
        ->when($this->filterAssignee, fn ($q, $id) => $q->where('assignee_id', $id))
        ->when($this->filterPriority, fn ($q, $p) => $q->where('priority', $p))
        ->with('assignee:id,name,avatar')
        ->ordered()
        ->get()
        ->groupBy('status');
}
```

**Actions**:

```php
public function moveTask(int $taskId, string $newStatus, int $newPosition): void
{
    $task = Task::findOrFail($taskId);
    $this->authorize('update', $task);

    $task->update([
        'status' => TaskStatus::from($newStatus),
        'sort_order' => $newPosition,
    ]);

    $this->dispatch('task-moved', taskId: $taskId, status: $newStatus);
}
```

**Template (Islands Architecture)**:

```blade
<div>
    {{-- Filters (Alpine-only, no server roundtrip for open/close) --}}
    <div x-data="{ open: false }">
        <button @click="open = !open">Filters</button>
        <div x-show="open" x-transition>
            <select wire:model.live="filterAssignee">...</select>
            <select wire:model.live="filterPriority">...</select>
        </div>
    </div>

    {{-- Columns as Islands --}}
    <div class="grid grid-cols-4 gap-4">
        @foreach(TaskStatus::cases() as $status)
            @island(key: $status->value)
                <div wire:sortable="moveTask" wire:sortable-group="{{ $status->value }}">
                    @foreach($this->tasks[$status->value] ?? [] as $task)
                        <div wire:sortable.item="{{ $task->id }}" wire:key="task-{{ $task->id }}">
                            <x-task-card :task="$task" />
                        </div>
                    @endforeach
                </div>
            @endisland
        @endforeach
    </div>

    {{-- Activity Feed (lazy-loaded island) --}}
    @island(key: 'activity', lazy: true)
        <div wire:poll.5s>
            @foreach($this->recentActivity as $activity)
                <x-activity-item :activity="$activity" />
            @endforeach
        </div>
    @endisland
</div>
```

## Component Architecture Decision Tree

Choose the right tool for each UI region:

| Question | Yes | No |
|----------|-----|-----|
| Does it need server-side data or actions? | **Livewire component** | Continue below |
| Is it a reusable UI element (button, card, badge)? | **Blade component** | Continue below |
| Is it a micro-interaction (dropdown, modal, toggle)? | **Alpine.js** | Continue below |
| Is it an independent region that updates on its own? | **Island** | Livewire component |
| Does it need to update without affecting siblings? | **Island** | Livewire component |
| Is it expensive to render within a larger component? | **Island** | Inline in parent |

### Nesting Rules

| Pattern | Allowed | Notes |
|---------|---------|-------|
| Livewire > Blade component | Yes | Preferred for UI decomposition |
| Livewire > Alpine.js | Yes | Use `$wire` for communication |
| Livewire > Island | Yes | v4 only, independent refresh |
| Livewire > Livewire (1 level) | Yes | Use sparingly, communicate via events |
| Livewire > Livewire > Livewire | No | Max 1 level of Livewire nesting |
| Blade > Livewire | Yes | Common for placing components in layouts |

## Component Format Selection

| Factor | Single-File (SFC) | Multi-File (MFC) | Class-Based |
|--------|-------------------|-------------------|-------------|
| **Created with** | `make:livewire name` | `make:livewire name --mfc` | `make:livewire name --class` |
| **Best for** | Most components | Complex components with JS/CSS | Teams migrating from v3 |
| **File location** | `resources/views/components/` | `resources/views/components/name/` | `app/Livewire/` + `resources/views/livewire/` |
| **IDE support** | Good (single file) | Best (separate files) | Traditional (two files) |
| **Template** | Same file below `<?php ... ?>` | `name.blade.php` | Separate Blade file |
| **JS/CSS** | Inline `@script`/`@style` | Separate `.js`/`.css` files | Inline `@script`/`@style` |
| **When to choose** | Default choice | Needs separate JS/CSS or large template | Existing v3 codebase |

### SFC Structure Example

```php
<?php
// resources/views/components/task-create.wire.php

use App\Models\Task;
use App\Livewire\Forms\TaskForm;
use Livewire\Component;

new class extends Component {
    public TaskForm $form;

    public function save(): void
    {
        $this->authorize('create', Task::class);
        $this->form->store();
        $this->dispatch('task-created');
        $this->reset();
    }
}
?>

<div>
    <form wire:submit="save">
        <input wire:model.blur="form.title" type="text" />
        @error('form.title') <span>{{ $message }}</span> @enderror

        <textarea wire:model.blur="form.description"></textarea>

        <button type="submit" wire:loading.attr="disabled">
            <span wire:loading.remove>Create Task</span>
            <span wire:loading>Saving...</span>
        </button>
    </form>
</div>
```

## Performance Optimization Tiers

Plan performance from the start. Each tier addresses a different bottleneck:

### Tier 1: Property and Payload Optimization

| Rule | Bad | Good |
|------|-----|------|
| Use primitives over objects | `public Task $task` | `public int $taskId` with `#[Locked]` |
| Computed properties for queries | `public Collection $tasks` | `#[Computed] public function tasks()` |
| Minimize public properties | 15 public properties | Extract to Form Object |
| Route model binding in mount | `public User $user` property | `mount(User $user) { $this->userId = $user->id; }` |

### Tier 2: Rendering Optimization

| Technique | Use Case | Impact |
|-----------|----------|--------|
| `wire:ignore` | Static elements (maps, charts) | Saved 200ms per update in benchmarks |
| `wire:key` | Every item in loops | Prevents DOM diffing failures |
| Islands (`@island`) | Independent UI regions | 1.6s to 131ms in data table benchmark |
| Blaze Compiler | Static template portions | Up to 20x faster Blade rendering |

### Tier 3: Loading Strategies

| Technique | Directive | Use Case |
|-----------|-----------|----------|
| Lazy loading | `#[Lazy]` or `wire:lazy` | Below-fold components; boosted LCP by 40% |
| Deferred loading | `#[Defer]` | Non-critical content after page load |
| Placeholder | `@placeholder` | Skeleton loaders during lazy load |
| Async actions | `#[Async]` | Non-blocking action execution |

### Tier 4: Data Retrieval

```php
// BAD: Loads everything
#[Computed]
public function tasks(): Collection
{
    return Task::all();
}

// GOOD: Selective, eager-loaded, paginated
#[Computed]
public function tasks(): LengthAwarePaginator
{
    return Task::query()
        ->select('id', 'title', 'status', 'assignee_id', 'due_date')
        ->with('assignee:id,name')
        ->where('team_id', $this->teamId)
        ->ordered()
        ->paginate(25);
}
```

### Tier 5: Network Optimization

| Rule | Bad | Good |
|------|-----|------|
| Avoid unnecessary live binding | `wire:model.live` on every field | `wire:model` (deferred) or `wire:model.blur` |
| Debounce search inputs | `wire:model.live` | `wire:model.live.debounce.300ms` |
| Dispatch from Blade | `$this->dispatch('event')` in PHP after click | `$dispatch('event')` in Blade (no roundtrip) |
| Queue heavy work | Inline processing | `dispatch(new ProcessTask($id))` |

### Tier 6: SPA Navigation

```blade
{{-- Link interception for instant navigation --}}
<a href="/tasks" wire:navigate>Tasks</a>

{{-- Prefetch on hover --}}
<a href="/tasks" wire:navigate.hover>Tasks</a>

{{-- Persist elements across navigations --}}
@persist('player')
    <audio src="{{ $episode->url }}" x-data x-ref="player"></audio>
@endpersist
```

## Form Handling and Validation Patterns

### Form Objects (Recommended)

Extract validation and persistence logic into reusable Form Objects:

```php
<?php

namespace App\Livewire\Forms;

use App\Models\Task;
use Livewire\Form;
use Livewire\Attributes\Validate;

class TaskForm extends Form
{
    #[Validate('required|min:3|max:255')]
    public string $title = '';

    #[Validate('nullable|string|max:5000')]
    public string $description = '';

    #[Validate('required|exists:users,id')]
    public ?int $assignee_id = null;

    #[Validate('required')]
    public string $priority = 'medium';

    #[Validate('nullable|date|after:today')]
    public ?string $due_date = null;

    public function store(): Task
    {
        $this->validate();
        $task = Task::create($this->only(['title', 'description', 'assignee_id', 'priority', 'due_date']));
        $this->reset();
        return $task;
    }

    public function update(Task $task): void
    {
        $this->validate();
        $task->update($this->only(['title', 'description', 'assignee_id', 'priority', 'due_date']));
    }

    public function setTask(Task $task): void
    {
        $this->title = $task->title;
        $this->description = $task->description ?? '';
        $this->assignee_id = $task->assignee_id;
        $this->priority = $task->priority->value;
        $this->due_date = $task->due_date?->format('Y-m-d');
    }
}
```

### Validation Strategy Selection

| Strategy | Directive | Best For |
|----------|-----------|----------|
| On blur | `wire:model.blur` + `$this->validateOnly()` | Individual field feedback |
| On submit | `wire:model` (deferred) + `$this->validate()` | Simple forms, fewer requests |
| Real-time | `wire:model.live.debounce.300ms` | Search, username availability |
| Hybrid | `.blur` for most fields, `.live.debounce` for search | Complex forms (recommended) |

### Validation Code Pattern

```php
<?php
// In a Single-File Component

use Livewire\Component;
use App\Livewire\Forms\TaskForm;

new class extends Component {
    public TaskForm $form;

    public function updatedFormTitle(): void
    {
        $this->validateOnly('form.title');
    }

    public function save(): void
    {
        $task = $this->form->store();
        $this->dispatch('task-created', taskId: $task->id);

        session()->flash('message', 'Task created.');
    }
}
?>

<div>
    <form wire:submit="save">
        <div>
            <label for="title">Title</label>
            <input wire:model.blur="form.title" id="title" type="text" />
            @error('form.title') <span class="text-red-500">{{ $message }}</span> @enderror
        </div>

        <div>
            <label for="description">Description</label>
            <textarea wire:model="form.description" id="description"></textarea>
        </div>

        <div>
            <label for="due_date">Due Date</label>
            <input wire:model="form.due_date" id="due_date" type="date" />
            @error('form.due_date') <span class="text-red-500">{{ $message }}</span> @enderror
        </div>

        <button type="submit">
            <span wire:loading.remove wire:target="save">Create Task</span>
            <span wire:loading wire:target="save">Creating...</span>
        </button>
    </form>
</div>
```

### Form Best Practices

- Validate on blur (`wire:model.blur`) for best UX balance
- Always validate server-side even with client-side validation
- Use `$this->reset()` or `$this->form->reset()` after successful submissions
- Avoid nested forms inside Form Objects
- Keep file upload inputs on the main component, not inside Form Objects (race condition risk)
- Use separate Form Objects for Create and Edit when validation rules differ significantly

## State Management Patterns

### Property Types and Modifiers

| Modifier | Purpose | Example |
|----------|---------|---------|
| `public` | Two-way bindable, included in payload | `public string $search = ''` |
| `#[Locked]` | Server-only, cannot be modified from client | `#[Locked] public int $teamId` |
| `#[Computed]` | Request-cached derived data | `#[Computed] public function tasks()` |
| `#[Computed(persist: true)]` | Cached across requests | Expensive computations |
| `#[Computed(cache: true, key: '...')]` | Shared global cache | Dashboard stats |

### wire:model Modifiers

| Modifier | Behavior | Use When |
|----------|----------|----------|
| `wire:model` | Deferred (default) -- syncs on next action | Most form fields |
| `wire:model.live` | Immediate sync on input | Search fields, real-time preview |
| `wire:model.blur` | Syncs on blur | Validation on field exit |
| `wire:model.live.debounce.300ms` | Throttled immediate sync | Search inputs |
| `wire:model.live.blur` | Syncs on blur (v4 syntax) | Field-level validation |

### Component Communication

```php
// Parent to Child: Props
<livewire:task-card :task-id="$task->id" />

// Child to Parent: Events
// In child:
$this->dispatch('task-saved', taskId: $task->id);

// In parent template:
<livewire:task-create @task-saved="$refresh" />

// Or in parent PHP:
#[On('task-saved')]
public function handleTaskSaved(int $taskId): void
{
    // React to child event
}

// Sibling to Sibling: Global dispatch
$this->dispatch('task-updated')->to('activity-feed');

// Island refresh from parent
$wire.$island('activity').$refresh()
```

### State Design Checklist

| Question | If Yes | If No |
|----------|--------|-------|
| Does the client need to read/write it? | `public` property | `#[Locked]` or private |
| Is it derived from other data? | `#[Computed]` | Direct property |
| Is it expensive to compute? | `#[Computed(persist: true)]` | `#[Computed]` |
| Is it shared across components? | `#[Computed(cache: true)]` | Local computed |
| Is it an ID or security-sensitive? | `#[Locked]` | `public` |
| Does it need two-way binding? | `wire:model` + `public` | One-way via prop |

## Alpine.js Integration Patterns

### The `$wire` Object

`$wire` is the primary bridge between Alpine.js and Livewire. Prefer it over `@entangle`.

```blade
{{-- Reading properties --}}
<div x-data>
    <span x-text="$wire.title"></span>
</div>

{{-- Calling actions --}}
<button x-data @click="await $wire.deleteTask({{ $task->id }})">
    Delete
</button>

{{-- Conditional rendering --}}
<div x-data="{ editing: false }">
    <h3 x-show="!editing" @click="editing = true" x-text="$wire.title"></h3>
    <input x-show="editing"
           x-ref="titleInput"
           :value="$wire.title"
           @keydown.enter="$wire.updateTitle($refs.titleInput.value); editing = false"
           @keydown.escape="editing = false" />
</div>

{{-- Island access (v4) --}}
<button x-data @click="$wire.$island('comments').$refresh()">
    Refresh Comments
</button>
```

### When to Use `$wire` vs `@entangle`

| Approach | Use When | Avoid When |
|----------|----------|------------|
| `$wire.property` | Reading/writing Livewire state from Alpine | N/A (always safe) |
| `$wire.method()` | Calling server actions | N/A (always safe) |
| `$wire.entangle('prop')` | True bidirectional sync needed | Simple reads/writes (creates duplicate state) |
| Alpine-only `x-data` | Client-only UI state (open/close, tabs) | State needs to persist across requests |

### Extract Alpine to Blade Components

When Alpine logic is reusable, extract it into a Blade component:

```blade
{{-- resources/views/components/dropdown.blade.php --}}
@props(['label'])

<div x-data="{ open: false }" @click.outside="open = false" {{ $attributes }}>
    <button @click="open = !open">{{ $label }}</button>
    <div x-show="open" x-transition {{ $attributes->merge(['class' => 'absolute mt-2']) }}>
        {{ $slot }}
    </div>
</div>

{{-- Usage inside a Livewire component --}}
<x-dropdown label="Actions">
    <button @click="$wire.archive({{ $task->id }})">Archive</button>
    <button @click="$wire.delete({{ $task->id }})">Delete</button>
</x-dropdown>
```

## Security Best Practices

### The Golden Rule

> **Treat all public properties as user input.**

Every public property on a Livewire component can be modified by the client. Never trust their values without validation.

### Authorization in Every Action

The most common Livewire security vulnerability: calling an action without verifying the user has permission.

```php
// BAD: No authorization
public function delete(int $taskId): void
{
    Task::find($taskId)->delete();
}

// GOOD: Authorize before every mutating action
public function delete(int $taskId): void
{
    $task = Task::findOrFail($taskId);
    $this->authorize('delete', $task);
    $task->delete();
    $this->dispatch('task-deleted', taskId: $taskId);
}
```

### Property Protection

| Technique | Purpose | Example |
|-----------|---------|---------|
| `#[Locked]` | Prevent client modification | `#[Locked] public int $userId` |
| Model binding | Livewire guards against ID swaps | `public Task $task` (auto-protected) |
| Validation | Sanitize all input | `#[Validate('required','max:255')]` |
| Authorization | Verify permissions | `$this->authorize('update', $task)` |

### Security Checklist for Blueprint Plans

| Item | Check |
|------|-------|
| Every action method calls `$this->authorize()` | Required |
| IDs and non-editable data use `#[Locked]` | Required |
| All public properties have validation rules | Required |
| Sensitive queries scope to current user/team | Required |
| File uploads validate type and size | Required |
| Rate limiting on expensive actions | Recommended |
| Persistent middleware for role checks | `Livewire::addPersistentMiddleware([...])` |

## Testing Strategies

### Tier 1: Smoke Tests

Every component must render without errors:

```php
it('renders the task board page', function () {
    $user = User::factory()->create();

    $this->actingAs($user)
        ->get('/dashboard')
        ->assertSeeLivewire('task-board');
});
```

### Tier 2: Property and Action Tests

```php
it('creates a task via form object', function () {
    $user = User::factory()->create();

    Livewire::actingAs($user)
        ->test('task.create')
        ->set('form.title', 'New Feature')
        ->set('form.priority', 'high')
        ->call('save')
        ->assertHasNoErrors();

    expect(Task::where('title', 'New Feature')->exists())->toBeTrue();
});

it('moves a task to a new status', function () {
    $user = User::factory()->create();
    $task = Task::factory()->for($user, 'creator')->create(['status' => 'todo']);

    Livewire::actingAs($user)
        ->test('task-board', ['teamId' => $user->team_id])
        ->call('moveTask', $task->id, 'in_progress', 0)
        ->assertHasNoErrors();

    expect($task->fresh()->status->value)->toBe('in_progress');
});
```

### Tier 3: Validation Tests (Dataset Pattern)

```php
it('validates required fields', function (string $field) {
    $user = User::factory()->create();

    Livewire::actingAs($user)
        ->test('task.create')
        ->set($field, '')
        ->call('save')
        ->assertHasErrors([$field => 'required']);
})->with([
    'form.title',
    'form.priority',
]);

it('validates field constraints', function (string $field, mixed $value, string $rule) {
    $user = User::factory()->create();

    Livewire::actingAs($user)
        ->test('task.create')
        ->set($field, $value)
        ->call('save')
        ->assertHasErrors([$field => $rule]);
})->with([
    ['form.title', str_repeat('a', 256), 'max'],
    ['form.due_date', '2020-01-01', 'after'],
    ['form.assignee_id', 99999, 'exists'],
]);
```

### Tier 4: Event Tests

```php
it('dispatches task-created event on save', function () {
    $user = User::factory()->create();

    Livewire::actingAs($user)
        ->test('task.create')
        ->set('form.title', 'Event Test')
        ->set('form.priority', 'medium')
        ->call('save')
        ->assertDispatched('task-created');
});
```

### Tier 5: Authorization Tests

```php
it('forbids non-creator from deleting a task', function () {
    $creator = User::factory()->create();
    $other = User::factory()->create(['team_id' => $creator->team_id]);
    $task = Task::factory()->for($creator, 'creator')->create();

    Livewire::actingAs($other)
        ->test('task-board', ['teamId' => $other->team_id])
        ->call('deleteTask', $task->id)
        ->assertForbidden();
});
```

### Tier 6: View Output Tests

```php
it('displays task cards with correct priority badges', function () {
    $user = User::factory()->create();
    Task::factory()->for($user, 'creator')->create([
        'title' => 'Urgent Bug',
        'priority' => 'urgent',
        'team_id' => $user->team_id,
    ]);

    Livewire::actingAs($user)
        ->test('task-board', ['teamId' => $user->team_id])
        ->assertSee('Urgent Bug');
});
```

### Testing Caveat

Livewire test helpers (`->set()`, `->call()`) interact with properties and methods but **do not interact with the actual view file**. They will not test Alpine.js behavior, `wire:click` bindings, or client-side logic. Use Pest Browser Plugin (Playwright-powered) for full user-flow testing in v4.

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| No component format decision | Inconsistent file structure | Specify SFC, MFC, or class-based for each component |
| Using Livewire for static UI | Unnecessary server requests | Use Blade components for presentational elements |
| Deep Livewire nesting | Performance degradation, bugs | Max 1 level; use Blade for deeper nesting |
| Missing `wire:key` in loops | DOM diffing failures, ghost elements | Always add `wire:key="unique-{{ $id }}"` |
| `wire:model.live` everywhere | Excessive network requests | Default to deferred; use `.blur` or `.live.debounce` |
| Eloquent models as public props | Large JSON payloads | Use primitive IDs with `#[Locked]`, computed for queries |
| No authorization in actions | Security vulnerability (#1 pitfall) | `$this->authorize()` in every mutating action |
| Missing loading states | Poor UX during server roundtrips | Add `wire:loading` to every action trigger |
| `@entangle` when `$wire` suffices | Duplicate state, predictability issues | Use `$wire.property` for reads, `$wire.method()` for actions |
| No event communication map | Components don't coordinate | Document all events with source, listener, and payload |
| Missing computed properties | Redundant database queries | Use `#[Computed]` for any derived data |
| No performance tier planning | Slow page loads discovered late | Apply tiers 1-6 during planning phase |
| Forgetting `#[Locked]` on IDs | Client can tamper with IDs | Lock all non-editable properties |
| Not scoping queries to tenant | Data leaks across teams/users | Always scope queries: `->where('team_id', ...)` |

## Best Practices

1. **Be explicit about component format** -- Specify SFC, MFC, or class-based for every component
2. **Choose the right tool** -- Livewire for server interactivity, Blade for UI, Alpine for micro-interactions, Islands for independent regions
3. **Use Form Objects** -- Extract validation and persistence into reusable Form classes
4. **Authorize every action** -- `$this->authorize()` before any database mutation
5. **Lock non-editable properties** -- `#[Locked]` on IDs, team scopes, and config values
6. **Use computed properties** -- `#[Computed]` for all derived data and queries
7. **Minimize live bindings** -- Default to deferred `wire:model`; use `.blur` for validation, `.live.debounce` for search
8. **Plan events upfront** -- Map dispatched events, listeners, and payloads before coding
9. **Add loading states** -- `wire:loading` on every user-triggered action
10. **Use Islands for dashboards** -- Independent refresh, polling, and lazy loading per region
11. **Test authorization first** -- Authorization tests catch the most critical bugs
12. **Keep primitives in properties** -- Pass IDs, not models; use computed properties for queries
13. **Include scaffold commands** -- List all `php artisan make:livewire` commands in order
14. **File inventory** -- Categorized list of all generated files at the end of every Blueprint

## Anti-Patterns to Avoid

| Vague | Blueprint |
|-------|-----------|
| "searchable dropdown" | `wire:model.live.debounce.300ms` with computed property filtering query |
| "drag and drop" | `wire:sort` with `moveTask(int $id, string $status, int $position)` action |
| "real-time updates" | `@island` with `wire:poll.5s` on activity feed, event-driven refresh on board |
| "form with validation" | Form Object with `#[Validate]` attributes, `wire:model.blur`, `$this->validateOnly()` |
| "delete button" | Action with `$this->authorize('delete', $task)`, confirmation dialog, event dispatch |
| "loading state" | `wire:loading` on button, `wire:loading.attr="disabled"`, target-specific indicators |
| "filters" | Alpine `x-data` for open/close, `wire:model.live` on selects, computed property with `->when()` |
| "shows user info" | `#[Computed] public function user()` with `->select('id','name')`, not `public User $user` |
| "caches data" | `#[Computed(persist: true)]` or `Cache::remember()` with specific TTL |
| "pagination" | `->paginate(25)` or cursor pagination, not `->get()` on full dataset |

## Common Patterns

### Computed Property with Filtering

```php
#[Computed]
public function tasks(): LengthAwarePaginator
{
    return Task::query()
        ->select('id', 'title', 'status', 'priority', 'assignee_id', 'due_date')
        ->with('assignee:id,name')
        ->where('team_id', $this->teamId)
        ->when($this->search, fn ($q, $s) => $q->where('title', 'like', "%{$s}%"))
        ->when($this->filterStatus, fn ($q, $s) => $q->where('status', $s))
        ->ordered()
        ->paginate(25);
}
```

### Inline Editing with Alpine

```blade
<div x-data="{ editing: false, value: $wire.title }" wire:key="task-{{ $task->id }}">
    <span x-show="!editing" @dblclick="editing = true; $nextTick(() => $refs.input.focus())">
        {{ $task->title }}
    </span>
    <input x-show="editing"
           x-ref="input"
           x-model="value"
           @keydown.enter="$wire.updateTitle({{ $task->id }}, value); editing = false"
           @keydown.escape="editing = false; value = $wire.title"
           @click.outside="editing = false" />
</div>
```

### Confirmation Dialog Pattern

```blade
<div x-data="{ confirming: false }">
    <button @click="confirming = true" class="text-red-600">Delete</button>

    <div x-show="confirming" x-transition>
        <p>Are you sure?</p>
        <button @click="await $wire.delete({{ $task->id }}); confirming = false">
            Yes, delete
        </button>
        <button @click="confirming = false">Cancel</button>
    </div>
</div>
```

### Lazy-Loaded Island with Placeholder

```blade
@island(key: 'stats', lazy: true)
    @placeholder
        <div class="animate-pulse h-24 bg-gray-200 rounded"></div>
    @endplaceholder

    <div class="grid grid-cols-3 gap-4">
        <x-stat-card label="Open" :value="$this->openCount" />
        <x-stat-card label="In Progress" :value="$this->inProgressCount" />
        <x-stat-card label="Done" :value="$this->doneCount" />
    </div>
@endisland
```

### Debounced Search

```php
<?php
use Livewire\Component;
use Livewire\Attributes\Computed;

new class extends Component {
    public string $search = '';

    #[Computed]
    public function results(): Collection
    {
        return Task::query()
            ->where('team_id', $this->teamId)
            ->where('title', 'like', "%{$this->search}%")
            ->select('id', 'title', 'status')
            ->limit(10)
            ->get();
    }
}
?>

<div>
    <input wire:model.live.debounce.300ms="search"
           type="text"
           placeholder="Search tasks..." />

    <ul>
        @foreach($this->results as $task)
            <li wire:key="result-{{ $task->id }}">{{ $task->title }}</li>
        @endforeach
    </ul>
</div>
```

### Event-Driven Component Refresh

```blade
{{-- Parent component template --}}
<div>
    {{-- Child dispatches 'task-created', parent refreshes via @task-created --}}
    <livewire:task-create @task-created="$refresh" />

    {{-- Island refreshes when parent re-renders --}}
    @island(key: 'task-list')
        @foreach($this->tasks as $task)
            <x-task-card :task="$task" wire:key="task-{{ $task->id }}" />
        @endforeach
    @endisland
</div>
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Enums (2)
- app/Enums/TaskStatus.php
- app/Enums/TaskPriority.php

### Models (2)
- app/Models/Task.php
- app/Models/TaskComment.php

### Form Objects (1)
- app/Livewire/Forms/TaskForm.php

### Components - Single-File (4)
- resources/views/components/task-board.wire.php
- resources/views/components/task/create.wire.php
- resources/views/components/task/edit.wire.php
- resources/views/components/activity-feed.wire.php

### Blade Components (3)
- resources/views/components/task-card.blade.php
- resources/views/components/stat-card.blade.php
- resources/views/components/activity-item.blade.php

### Policies (1)
- app/Policies/TaskPolicy.php

### Migrations (2)
- database/migrations/xxxx_create_tasks_table.php
- database/migrations/xxxx_create_task_comments_table.php

### Factories (2)
- database/factories/TaskFactory.php
- database/factories/TaskCommentFactory.php

### Tests (3)
- tests/Feature/Livewire/TaskBoardTest.php
- tests/Feature/Livewire/TaskCreateTest.php
- tests/Feature/Livewire/TaskEditTest.php

### Routes
- routes/web.php (updated with Route::livewire entries)
```
