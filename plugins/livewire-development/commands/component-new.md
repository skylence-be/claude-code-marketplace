---
description: Create Livewire 4 component with reactive properties
model: claude-sonnet-4-5
---

Create a Livewire 4 component following modern patterns.

## Component Specification

$ARGUMENTS

## Livewire 4 Component Patterns

### 1. **Single-File Component (⚡)** (resources/views/livewire/counter.blade.php)

The default format in Livewire 4. PHP and Blade in one file.

```php
<?php

use Livewire\Component;
use Livewire\Attributes\Computed;

new class extends Component {
    public int $count = 0;

    public function increment(): void
    {
        $this->count++;
    }

    #[Computed]
    public function doubled(): int
    {
        return $this->count * 2;
    }
}
?>

<div>
    <button wire:click="increment">Count: {{ $count }}</button>
    <span>Doubled: {{ $this->doubled }}</span>
</div>

<style>
    /* Automatically scoped to this component */
    button { background: #3b82f6; color: white; padding: 0.5rem 1rem; }
</style>
```

### 2. **Multi-File Component (MFC)** (resources/views/livewire/dashboard/)

For complex components. Create with `php artisan make:livewire dashboard --mfc`.

```
dashboard/
├── dashboard.php      # Component class
├── dashboard.blade.php # Template
├── dashboard.js       # Optional JavaScript
├── dashboard.css      # Optional CSS
└── dashboard.test.php # Optional tests
```

### 3. **Page Component with Route::livewire()**

```php
// routes/web.php
Route::livewire('/posts', 'pages::post-list');
Route::livewire('/posts/{post}', 'pages::post-show');

// resources/views/livewire/pages/post-list.blade.php (SFC)
<?php

use App\Models\Post;
use Livewire\Component;
use Livewire\WithPagination;
use Livewire\Attributes\Title;
use Livewire\Attributes\Layout;

new #[Title('Posts')] #[Layout('layouts::app')] class extends Component {
    use WithPagination;

    public string $search = '';

    public function render()
    {
        return view()->with([
            'posts' => Post::search($this->search)->paginate(10),
        ]);
    }
}
?>

<div>
    <input wire:model.live.debounce.300ms="search" placeholder="Search...">
    @foreach ($posts as $post)
        <div wire:key="{{ $post->id }}">{{ $post->title }}</div>
    @endforeach
    {{ $posts->links() }}
</div>
```

### 4. **Islands Architecture**

Isolated regions that update independently for better performance.

```blade
<div>
    <h1>Dashboard</h1>

    {{-- This island updates independently --}}
    @island(name: 'stats', lazy: true)
        <livewire:dashboard-stats />
    @endisland

    {{-- Infinite scroll with appending --}}
    @island(name: 'feed')
        <livewire:activity-feed />
    @endisland
</div>
```

### 5. **Traditional Class Component** (app/Livewire/PostList.php)

```php
<?php

namespace App\Livewire;

use App\Models\Post;
use Livewire\Component;
use Livewire\WithPagination;
use Livewire\Attributes\Title;
use Livewire\Attributes\Computed;

#[Title('Posts')]
class PostList extends Component
{
    use WithPagination;

    public string $search = '';
    public string $sortBy = 'created_at';
    public string $sortDirection = 'desc';

    #[Computed]
    public function posts()
    {
        return Post::query()
            ->when($this->search, fn ($query) =>
                $query->where('title', 'like', "%{$this->search}%")
            )
            ->orderBy($this->sortBy, $this->sortDirection)
            ->paginate(10);
    }

    public function updatedSearch()
    {
        $this->resetPage();
    }

    public function sortBy(string $field)
    {
        if ($this->sortBy === $field) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortBy = $field;
            $this->sortDirection = 'asc';
        }
    }

    public function delete(Post $post)
    {
        $this->authorize('delete', $post);

        $post->delete();

        $this->dispatch('post-deleted');
    }

    public function render()
    {
        return view('livewire.post-list');
    }
}
```

### 2. **Blade Template** (resources/views/livewire/post-list.blade.php)

```blade
<div>
    <div class="mb-4">
        <input
            type="search"
            wire:model.live.debounce.300ms="search"
            placeholder="Search posts..."
            class="w-full px-4 py-2 border rounded"
        >
    </div>

    <div class="space-y-4">
        @foreach ($this->posts as $post)
            <div class="p-4 border rounded" wire:key="post-{{ $post->id }}">
                <h3 class="text-lg font-bold">{{ $post->title }}</h3>
                <p class="text-gray-600">{{ $post->excerpt }}</p>

                <div class="mt-2 flex gap-2">
                    <a href="{{ route('posts.show', $post) }}" class="text-blue-600">
                        View
                    </a>
                    <button
                        wire:click="delete({{ $post->id }})"
                        wire:confirm="Are you sure?"
                        class="text-red-600"
                    >
                        Delete
                    </button>
                </div>
            </div>
        @endforeach
    </div>

    {{ $this->posts->links() }}
</div>
```

### 3. **Livewire 4 Features**

**Reactive Properties**
```php
use Livewire\Attributes\Reactive;

#[Reactive]
public $postId;
```

**Computed Properties**
```php
use Livewire\Attributes\Computed;

#[Computed]
public function post()
{
    return Post::find($this->postId);
}

// Access in template: $this->post
```

**Locked Properties**
```php
use Livewire\Attributes\Locked;

#[Locked]
public $userId;
```

**Validation**
```php
use Livewire\Attributes\Validate;

#[Validate('required|min:3')]
public string $title = '';

#[Validate('required|email')]
public string $email = '';

public function save()
{
    $this->validate();

    // Save logic
}
```

**Events**
```php
// Dispatch event
$this->dispatch('post-created', postId: $post->id);

// Listen to event
use Livewire\Attributes\On;

#[On('post-created')]
public function handlePostCreated($postId)
{
    // Handle event
}
```

**Real-time Validation**
```php
public function updated($property)
{
    $this->validateOnly($property);
}
```

### 6. **Advanced Patterns**

**Lazy Loading & Deferred Loading**
```php
use Livewire\Attributes\Lazy;
use Livewire\Attributes\Defer;

#[Lazy]
class ExpensiveComponent extends Component
{
    public function placeholder()
    {
        return view('livewire.placeholders.loading');
    }

    #[Defer]  // Load immediately after initial page load
    public function loadData()
    {
        return $this->heavyQuery();
    }
}
```

**Async Actions (Parallel Execution)**
```php
use Livewire\Attributes\Async;

class Dashboard extends Component
{
    #[Async]  // Runs in parallel, doesn't block
    public function refreshStats() { }

    #[Async]
    public function refreshChart() { }
}
```

```blade
{{-- Both run in parallel --}}
<button wire:click.async="refreshStats">Refresh Stats</button>
<button wire:click.async="refreshChart">Refresh Chart</button>
```

**Polling (Non-blocking in v4)**
```blade
{{-- Polling no longer blocks other requests --}}
<div wire:poll.5s>
    Current time: {{ now() }}
</div>
```

**New Wire Directives**
```blade
{{-- Drag-and-drop sorting --}}
<ul wire:sort="reorder">
    @foreach ($items as $item)
        <li wire:key="{{ $item->id }}" wire:sort.item="{{ $item->id }}">
            {{ $item->name }}
        </li>
    @endforeach
</ul>

{{-- Viewport intersection --}}
<div wire:intersect="loadMore">Load more when visible</div>
<div wire:intersect.once="trackView">Track once</div>
<div wire:intersect.half="halfVisible">50% visible</div>

{{-- Element reference for JS --}}
<canvas wire:ref="myCanvas"></canvas>

{{-- Preserve scroll on navigation --}}
<div wire:navigate:scroll>Scrollable content</div>

{{-- Renderless action (no re-render) --}}
<button wire:click.renderless="trackClick">Track</button>
```

**Slots Support**
```blade
{{-- Parent --}}
<livewire:modal>
    <x-slot:title>My Modal</x-slot:title>
    Modal content here
</livewire:modal>

{{-- Modal component --}}
<div {{ $attributes->class(['modal']) }}>
    <header>{{ $title }}</header>
    <main>{{ $slot }}</main>
</div>
```

**$errors Magic Property in JavaScript**
```blade
<script>
    // Access validation errors from JS
    if (this.$errors.has('email')) {
        console.log(this.$errors.get('email'));
    }
</script>
```

**File Uploads**
```php
use Livewire\WithFileUploads;

class UploadPhoto extends Component
{
    use WithFileUploads;

    #[Validate('image|max:1024')]
    public $photo;

    public function save()
    {
        $this->validate();

        $this->photo->store('photos');
    }
}
```

Generate production-ready Livewire 4 components with modern patterns (SFC, MFC, or traditional).
