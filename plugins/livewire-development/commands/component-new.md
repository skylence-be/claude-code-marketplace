---
description: Create Livewire 4 component with reactive properties
model: claude-sonnet-4-5
---

Create a Livewire 4 component following modern patterns.

## Component Specification

$ARGUMENTS

## Livewire 4 Component Patterns

### 1. **Basic Component** (app/Livewire/PostList.php)

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

### 4. **Advanced Patterns**

**Lazy Loading**
```php
use Livewire\Attributes\Lazy;

#[Lazy]
class ExpensiveComponent extends Component
{
    public function placeholder()
    {
        return view('livewire.placeholders.loading');
    }
}
```

**Polling**
```blade
<div wire:poll.5s>
    Current time: {{ now() }}
</div>
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

Generate production-ready Livewire 4 components with modern patterns.
