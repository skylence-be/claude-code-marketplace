---
name: livewire4-reactive-patterns
description: Master Livewire 4 reactive patterns including single-file components, islands architecture, attributes (#[Reactive], #[Computed], #[Locked], #[Modelable], #[Defer], #[Async]), wire directives, lifecycle hooks, and component communication. Use when building interactive components, managing state, or implementing real-time features.
---

# Livewire 4 Reactive Patterns

Comprehensive guide to implementing reactive patterns in Livewire 4.

## When to Use This Skill

- Building single-file (⚡) or multi-file components
- Using islands architecture for isolated, independently-updating regions
- Building real-time interactive components with reactive state management
- Implementing computed properties that automatically update
- Creating reusable components with locked properties for security
- Building parent-child component communication patterns
- Managing component lifecycle with hooks
- Dispatching and listening to events between components
- Using Route::livewire() for page routing

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Reactive Attributes | [reactive-attributes.md](reactive-attributes.md) | #[Reactive], #[Computed], #[Locked], #[Modelable], #[Defer], #[Async] |
| Wire Directives | [wire-directives.md](wire-directives.md) | wire:model, wire:click, wire:loading, wire:sort, wire:intersect, wire:ref |
| Lifecycle Hooks | [lifecycle-hooks.md](lifecycle-hooks.md) | mount, hydrate, updating, updated, booted |
| Component Communication | [component-communication.md](component-communication.md) | Events, dispatch, listen, parent-child, slots |
| Polling Patterns | [polling-patterns.md](polling-patterns.md) | wire:poll, auto-refresh, visibility |

## Quick Reference

### Component Formats (NEW in v4)

```php
// Single-File Component (⚡) - resources/views/livewire/counter.blade.php
<?php
use Livewire\Component;

new class extends Component {
    public int $count = 0;
    public function increment() { $this->count++; }
}
?>

<div>
    <button wire:click="increment">+</button>
    <span>{{ $count }}</span>
</div>

// Create with: php artisan make:livewire counter
// Convert formats: php artisan livewire:convert counter --mfc
```

### Islands Architecture (NEW in v4)

```blade
{{-- Isolated regions that update independently --}}
@island(name: 'stats', lazy: true)
    <div>{{ $this->expensiveStats }}</div>
@endisland

@island
    <livewire:comment-feed />
@endisland
```

### Route::livewire() (NEW in v4)

```php
// Preferred routing method
Route::livewire('/dashboard', 'pages::dashboard');
Route::livewire('/users/{user}', 'pages::user-profile');

// Component namespaces: pages::, layouts::
```

### Reactive Attributes

```php
use Livewire\Attributes\Reactive;
use Livewire\Attributes\Computed;
use Livewire\Attributes\Locked;
use Livewire\Attributes\Modelable;
use Livewire\Attributes\Defer;  // NEW in v4
use Livewire\Attributes\Async;  // NEW in v4

class MyComponent extends Component
{
    #[Reactive]
    public $userId;           // Updates when parent changes

    #[Locked]
    public $orderId;          // Cannot be modified from frontend

    #[Modelable]
    public $searchQuery = ''; // Two-way binding with parent

    #[Computed]
    public function user()    // Cached computed property
    {
        return User::find($this->userId);
    }

    #[Defer]                  // Load after initial page load
    public function loadData() { }

    #[Async]                  // Run in parallel, non-blocking
    public function fetchStats() { }
}
```

### Wire Directives

```blade
{{-- Data binding (BREAKING: use .deep for child element events) --}}
<input wire:model.live="search">
<input wire:model.blur="email">
<input wire:model.live.debounce.500ms="query">
<input wire:model.deep="nested">  {{-- NEW: captures child events --}}

{{-- Actions with new modifiers --}}
<button wire:click="save">Save</button>
<button wire:click.async="heavyTask">Async</button>  {{-- NEW --}}
<button wire:click.renderless="track">Track</button> {{-- NEW: no re-render --}}

{{-- Loading states --}}
<span wire:loading>Loading...</span>
<button wire:loading.attr="disabled">Submit</button>

{{-- NEW directives --}}
<ul wire:sort="reorder">...</ul>                     {{-- Drag-and-drop --}}
<div wire:intersect="loadMore">...</div>             {{-- Viewport intersection --}}
<div wire:intersect.once="trackView">...</div>       {{-- Once only --}}
<canvas wire:ref="canvas"></canvas>                  {{-- Element reference --}}
<div wire:navigate:scroll>...</div>                  {{-- Preserve scroll --}}
```

### Colocated JavaScript/CSS (NEW in v4)

```blade
<div>
    <button @click="handleClick">Click</button>
</div>

<script>
    // Access component via 'this' keyword
    function handleClick() {
        console.log('Component:', this);
    }
</script>

<style>
    /* Automatically scoped to this component */
    button { background: blue; }
</style>
```

### Slots Support (NEW in v4)

```blade
{{-- Parent component --}}
<livewire:card>
    <x-slot:header>My Header</x-slot:header>
    Card content here
</livewire:card>

{{-- Card component --}}
<div {{ $attributes }}>
    <header>{{ $header }}</header>
    {{ $slot }}
</div>
```

### Lifecycle Hooks

```php
public function mount($id)     { } // First instantiation
public function hydrate()      { } // Every request
public function updating($name, $value) { }
public function updated($name, $value)  { }
public function updatedEmail($value)    { } // Specific property
```

### Events

```php
// Dispatch
$this->dispatch('user-saved', userId: $user->id);
$this->dispatch('refresh')->to('other-component');
$this->dispatch('notify')->up(); // Parent only

// Listen
#[On('user-saved')]
public function handleUserSaved($userId) { }
```

## Best Practices

1. **Choose the right component format** - SFC for simple, MFC for complex
2. **Use islands** for dashboard widgets that should update independently
3. **Use Route::livewire()** for page components (required for SFC/MFC)
4. **Use #[Reactive]** for child component properties receiving parent data
5. **Use #[Computed]** for expensive operations that should be cached
6. **Use #[Locked]** for security-sensitive properties
7. **Use #[Defer]** for data that doesn't need to load with the page
8. **Use #[Async]** for parallel, non-blocking operations
9. **Debounce user input** to reduce server requests
10. **Use lifecycle hooks** appropriately for initialization
11. **Use wire:model.deep** when you need to capture child element events

## Common Pitfalls

1. **wire:model breaking change** - Now only captures direct element events, use .deep for child events
2. **wire:scroll renamed** - Use wire:navigate:scroll instead
3. **Forgetting #[Reactive]** - Child won't see parent changes
4. **Not using #[Computed]** - Query runs every render
5. **Overusing wire:model.live** - Too many requests
6. **Missing event handlers** - Events dispatch but nothing listens
7. **Not closing component tags** - Required for slots support in v4

## Breaking Changes from v3

```php
// wire:model behavior - only captures direct element events now
<input wire:model="value">           // Only this element
<div wire:model.deep="value">...</div> // Child elements too

// wire:model modifiers control client-side sync timing now
<input wire:model.blur="email">      // v3: sent on blur, synced immediately
<input wire:model.live.blur="email"> // v4: synced AND sent on blur

// JavaScript hooks
Livewire.hook('request', ...)        // v3 - deprecated
Livewire.interceptRequest(...)       // v4 - new API
```
