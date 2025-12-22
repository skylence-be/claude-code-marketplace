---
name: livewire4-reactive-patterns
description: Master Livewire 4 reactive patterns including attributes (#[Reactive], #[Computed], #[Locked], #[Modelable]), wire directives, lifecycle hooks, and component communication. Use when building interactive components, managing state, or implementing real-time features.
---

# Livewire 4 Reactive Patterns

Comprehensive guide to implementing reactive patterns in Livewire 4.

## When to Use This Skill

- Building real-time interactive components with reactive state management
- Implementing computed properties that automatically update
- Creating reusable components with locked properties for security
- Building parent-child component communication patterns
- Managing component lifecycle with hooks
- Dispatching and listening to events between components

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Reactive Attributes | `reactive-attributes.md` | #[Reactive], #[Computed], #[Locked], #[Modelable] |
| Wire Directives | `wire-directives.md` | wire:model, wire:click, wire:loading, modifiers |
| Lifecycle Hooks | `lifecycle-hooks.md` | mount, hydrate, updating, updated, booted |
| Component Communication | `component-communication.md` | Events, dispatch, listen, parent-child |
| Polling Patterns | `polling-patterns.md` | wire:poll, auto-refresh, visibility |

## Quick Reference

### Reactive Attributes

```php
use Livewire\Attributes\Reactive;
use Livewire\Attributes\Computed;
use Livewire\Attributes\Locked;
use Livewire\Attributes\Modelable;

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
}
```

### Wire Directives

```blade
{{-- Data binding --}}
<input wire:model.live="search">
<input wire:model.blur="email">
<input wire:model.live.debounce.500ms="query">

{{-- Actions --}}
<button wire:click="save">Save</button>
<button wire:click="delete({{ $id }})">Delete</button>

{{-- Loading states --}}
<span wire:loading>Loading...</span>
<button wire:loading.attr="disabled">Submit</button>
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

1. **Use #[Reactive]** for child component properties receiving parent data
2. **Use #[Computed]** for expensive operations that should be cached
3. **Use #[Locked]** for security-sensitive properties
4. **Debounce user input** to reduce server requests
5. **Use lifecycle hooks** appropriately for initialization

## Common Pitfalls

1. **Forgetting #[Reactive]** - Child won't see parent changes
2. **Not using #[Computed]** - Query runs every render
3. **Overusing wire:model.live** - Too many requests
4. **Missing event handlers** - Events dispatch but nothing listens
