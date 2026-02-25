# Function Compilation

The default Blaze optimization strategy. Compiles anonymous Blade components into optimized PHP functions, bypassing the standard rendering pipeline with 91-97% overhead reduction.

## How It Works

Blaze compiles templates into PHP functions that skip the standard rendering pipeline while maintaining Blade syntax compatibility.

### Before (Standard Blade Pipeline)

Each `<x-component>` invocation goes through:
1. Component resolution
2. View instantiation
3. Data binding
4. Blade compilation
5. Output buffering

### After (Blaze Function Compilation)

Each component becomes a direct PHP function call:

```blade
@blaze

@props(['type' => 'button'])

<button {{ $attributes->merge(['type' => $type]) }}>
    {{ $slot }}
</button>
```

Compiles to:

```php
function _c4f8e2a1($__data, $__slots) {
    $type = $__data['type'] ?? 'button';
    $attributes = new BlazeAttributeBag($__data);
    // ...
}
```

Usage:

```blade
<x-button type="submit">Send</x-button>
```

Becomes:

```php
_c4f8e2a1(['type' => 'submit'], ['default' => 'Send']);
```

## Enabling Function Compilation

### Option A: Per-Component with @blaze

Add `@blaze` to the top of any anonymous component:

```blade
@blaze

<button {{ $attributes }}>
    {{ $slot }}
</button>
```

### Option B: Per-Directory in AppServiceProvider

```php
use Livewire\Blaze\Blaze;

public function boot(): void
{
    Blaze::optimize()
        ->in(resource_path('views/components'));
}
```

### Gradual Rollout

Start specific, expand gradually:

```php
Blaze::optimize()
    ->in(resource_path('views/components/button'))
    ->in(resource_path('views/components/modal'))
    ->in(resource_path('views/components/card'));
```

### Excluding Directories

```php
Blaze::optimize()
    ->in(resource_path('views/components'))
    ->in(resource_path('views/components/legacy'), compile: false);
```

### Mixed Strategies

```php
Blaze::optimize()
    ->in(resource_path('views/components'))
    ->in(resource_path('views/components/icons'), memo: true)
    ->in(resource_path('views/components/cards'), fold: true);
```

Component-level `@blaze` directives override directory-level settings.

## Performance Benchmarks

Rendering 25,000 anonymous components in a loop:

| Scenario | Blade | Blaze | Reduction |
|----------|-------|-------|-----------|
| No attributes | 500ms | 13ms | 97.4% |
| Attributes only | 457ms | 26ms | 94.3% |
| Attributes + merge() | 546ms | 44ms | 91.9% |
| Props + attributes | 780ms | 40ms | 94.9% |
| Default slot | 460ms | 22ms | 95.1% |
| Named slots | 696ms | 49ms | 93.0% |
| @aware (nested) | 1,787ms | 129ms | 92.8% |

## Compatibility

Function compilation is a drop-in replacement that works with:

- `@props` declarations with defaults
- `$attributes` bag and `merge()`, `class()`, `style()`
- Default and named `$slot`
- `@aware` (both parent and child must be Blaze-compiled)
- Blade directives inside the template (`@if`, `@foreach`, `@php`, etc.)
- Nested component calls

## After Enabling

Always clear compiled views:

```bash
php artisan view:clear
```

## Environment Variables

```env
BLAZE_ENABLED=true    # Enable/disable Blaze (default: true)
BLAZE_DEBUG=false     # Enable debug mode (default: false)
```

Disable Blaze temporarily:

```env
BLAZE_ENABLED=false
```
