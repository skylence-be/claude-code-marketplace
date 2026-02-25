---
description: Enable Blaze optimization on Blade components
model: claude-sonnet-4-5
---

Enable Blaze optimization on Blade components or directories for improved rendering performance.

## Optimization Specification

$ARGUMENTS

## Blaze Optimization Patterns

### 1. **Enable on Individual Component**

Add `@blaze` to the top of an anonymous component:

```blade
{{-- resources/views/components/button.blade.php --}}
@blaze

@props(['type' => 'button', 'variant' => 'primary'])

@php
$classes = match($variant) {
    'primary' => 'bg-blue-500 hover:bg-blue-400 text-white',
    'secondary' => 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    'danger' => 'bg-red-500 hover:bg-red-400 text-white',
    default => 'bg-gray-500 hover:bg-gray-400 text-white',
};
@endphp

<button {{ $attributes->merge(['type' => $type])->class($classes) }}>
    {{ $slot }}
</button>
```

### 2. **Enable on Directories via AppServiceProvider**

```php
use Livewire\Blaze\Blaze;

public function boot(): void
{
    Blaze::optimize()
        ->in(resource_path('views/components'));
}
```

Gradual rollout with mixed strategies:

```php
Blaze::optimize()
    ->in(resource_path('views/components/button'))
    ->in(resource_path('views/components/card'))
    ->in(resource_path('views/components/modal'))
    ->in(resource_path('views/components/icons'), memo: true)
    ->in(resource_path('views/components/ui'), fold: true)
    ->in(resource_path('views/components/legacy'), compile: false);
```

### 3. **Enable Memoization for Repeated Components**

For slot-less components rendered many times with same props:

```blade
{{-- resources/views/components/icon.blade.php --}}
@blaze(memo: true)

@props(['name', 'size' => 'md'])

@php
$sizeClass = match($size) {
    'sm' => 'w-4 h-4',
    'md' => 'w-5 h-5',
    'lg' => 'w-6 h-6',
};
@endphp

<svg {{ $attributes->class([$sizeClass]) }}>
    <use href="/icons.svg#{{ $name }}" />
</svg>
```

### 4. **Enable Folding for Static Components**

For maximum performance on components with static or pass-through props:

```blade
{{-- resources/views/components/heading.blade.php --}}
@blaze(fold: true, safe: ['level'])

@props(['level' => 1])

<h{{ $level }} {{ $attributes }}>{{ $slot }}</h{{ $level }}>
```

### 5. **Folding with @unblaze for Validation**

For components that are mostly static but need dynamic error handling:

```blade
{{-- resources/views/components/input.blade.php --}}
@blaze(fold: true)

@props(['name', 'label', 'type' => 'text'])

<div>
    <label for="{{ $name }}">{{ $label }}</label>
    <input type="{{ $type }}" name="{{ $name }}" id="{{ $name }}" {{ $attributes }}>

    @unblaze(scope: ['name' => $name])
        @if($errors->has($scope['name']))
            <p class="text-red-500 text-sm mt-1">
                {{ $errors->first($scope['name']) }}
            </p>
        @endif
    @endunblaze
</div>
```

### 6. **Folding with Unsafe Slots**

When slot content is used in logic:

```blade
{{-- resources/views/components/empty-state.blade.php --}}
@blaze(fold: true, unsafe: ['slot'])

@if ($slot->hasActualContent())
    <div {{ $attributes->class('bg-white rounded-lg p-6') }}>
        {{ $slot }}
    </div>
@else
    <div class="text-gray-400 text-center p-6">
        No content available
    </div>
@endif
```

## Strategy Selection Guide

| Component | Recommended Strategy | Reason |
|-----------|---------------------|--------|
| Generic UI (buttons, cards) | `@blaze` (default) | Safe, significant improvement |
| Icons, badges, flags | `@blaze(memo: true)` | Same icon renders once |
| Static layout primitives | `@blaze(fold: true)` | Zero runtime cost |
| Form inputs with validation | `@blaze(fold: true)` + `@unblaze` | Fold structure, keep errors dynamic |
| Components using auth/session | `@blaze` only | Global state breaks folding |
| Class-based components | No Blaze | Not supported |

## Post-Enable Checklist

After enabling Blaze on any component or directory:

1. Run `php artisan view:clear`
2. Test affected pages manually
3. Enable `Blaze::debug()` temporarily to verify optimization is active
4. Check profiler to confirm strategy (compiled/folded/memoized)
5. Disable debug mode for production

Enable Blaze with the appropriate strategy for the specified components.
