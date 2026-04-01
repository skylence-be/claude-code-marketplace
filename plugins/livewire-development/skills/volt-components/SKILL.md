---
name: volt-components
description: Laravel Volt single-file Livewire component patterns including functional and class-based styles, state management, computed properties, and testing with Volt::test(). Use when creating Volt components or converting Livewire to single-file format.
category: livewire
tags: [volt, livewire, single-file, components, functional]
related_skills: [livewire4-reactive-patterns, livewire-forms-validation, livewire-blueprint]
---

# Volt Single-File Components

Laravel Volt enables single-file Livewire components where PHP logic and Blade template coexist in one file. Supports both functional and class-based styles.

## When to Use This Skill

- Creating single-file Livewire components with `@volt` directive
- Converting traditional Livewire components to Volt
- Choosing between functional vs class-based Volt style
- Testing Volt components with `Volt::test()`

## Creating Components

```bash
php artisan make:volt counter
php artisan make:volt counter --test        # with test file
php artisan make:volt counter --pest        # with Pest test
```

## Functional Style

The functional API uses imported functions for state and computed properties:

```blade
@volt
<?php
use function Livewire\Volt\{state, computed};

state(['count' => 0]);

$increment = fn () => $this->count++;
$double = computed(fn () => $this->count * 2);
?>

<div>
    <h1>Count: {{ $count }} (Double: {{ $this->double }})</h1>
    <button wire:click="increment">+</button>
</div>
@endvolt
```

### Functional API Reference

```php
use function Livewire\Volt\{state, computed, mount, rules, on};

// State with default values
state(['name' => '', 'email' => '']);

// State with initial value from closure
state(['user' => fn () => auth()->user()]);

// Computed property (cached per request)
$fullName = computed(fn () => $this->firstName . ' ' . $this->lastName);

// Mount lifecycle hook
mount(function () {
    $this->count = cache('initial-count', 0);
});

// Validation rules
rules(['name' => 'required|min:3', 'email' => 'required|email']);

// Event listener
on(['order-created' => function ($orderId) {
    $this->orders = Order::latest()->get();
}]);
```

## Class-Based Style

For more complex components, use an anonymous class:

```blade
@volt
<?php

use Livewire\Volt\Component;

new class extends Component {
    public int $count = 0;

    public function increment(): void
    {
        $this->count++;
    }

    public function with(): array
    {
        return [
            'double' => $this->count * 2,
        ];
    }
} ?>

<div>
    <h1>{{ $count }}</h1>
    <button wire:click="increment">+</button>
</div>
@endvolt
```

## Choosing a Style

**Check existing components first** — match the project's convention.

| Functional | Class-Based |
|------------|-------------|
| Simple state + actions | Complex lifecycle hooks |
| Few properties | Many properties with types |
| Quick prototyping | Full Livewire features |
| Blade-first developers | PHP-first developers |

## Testing

```php
use Livewire\Volt\Volt;

test('counter increments', function () {
    Volt::test('counter')
        ->assertSee('Count: 0')
        ->call('increment')
        ->assertSee('Count: 1');
});

test('form validates', function () {
    Volt::test('contact-form')
        ->set('name', '')
        ->call('submit')
        ->assertHasErrors(['name' => 'required']);
});
```

## Common Pitfalls

- Not checking existing style (functional vs class-based) before creating new components
- Forgetting the `@volt` / `@endvolt` directive wrapper
- Mixing functional and class-based styles in the same project (pick one)
- Missing `--test` or `--pest` flag when tests are expected
- Using full Livewire component class when Volt would be simpler
