# Folding Strategies

Compile-time folding is Blaze's most aggressive optimization. Components are pre-rendered during compilation and embedded as static HTML — zero runtime cost, constant rendering time regardless of component count.

## Performance

| Components | Blade | Blaze (folded) |
|------------|-------|----------------|
| 25,000 | 500ms | 0.68ms |
| 50,000 | 1,000ms | 0.68ms |
| 100,000 | 2,000ms | 0.68ms |

## Enabling Folding

### Per-Component

```blade
@blaze(fold: true)

@props(['color'])

@php
$classes = match($color) {
    'red' => 'bg-red-500 hover:bg-red-400',
    'blue' => 'bg-blue-500 hover:bg-blue-400',
    default => 'bg-gray-500 hover:bg-gray-400',
};
@endphp

<button {{ $attributes->class($classes) }}>
    {{ $slot }}
</button>
```

### Per-Directory

```php
Blaze::optimize()
    ->in(resource_path('views/components/ui'), fold: true);
```

## How Folding Works

### Static Attributes (Safe)

With a static prop:

```blade
<x-button color="red">Submit</x-button>
```

Blaze pre-renders at compile time:

```blade
<button class="bg-red-500 hover:bg-red-400">
    Submit
</button>
```

The component disappears entirely — just static HTML remains.

### Dynamic Pass-Through Attributes (Safe)

Dynamic attributes that are not used in internal logic get placeholder substitution:

```blade
<x-button color="red" :id="Str::random()">Submit</x-button>
```

1. Blaze identifies dynamic attributes, stores values
2. Pre-renders with placeholder: `id="ATTR_PLACEHOLDER_1"`
3. Substitutes original expression back: `id="{{ Str::random() }}"`

Result:

```blade
<button class="bg-red-500 hover:bg-red-400" id="{{ Str::random() }}">
    Submit
</button>
```

### Dynamic Non-Pass-Through Props (Unsafe — Auto-Aborted)

When a dynamic attribute is also defined in `@props`, Blaze aborts folding automatically:

```blade
<x-button :color="$deleting ? 'red' : 'blue'" />
```

Blaze detects that `color` is in `@props` and used in internal logic (`match()`). Folding aborts, falls back to function compilation.

### Slots (Always Pass-Through)

Slots are replaced with placeholders and restored after folding:

```blade
<x-button>{{ $action }}</x-button>
```

Result:

```blade
<button class="bg-gray-500 hover:bg-gray-400">
    {{ $action }}
</button>
```

## Selective Folding with safe/unsafe

### `safe` — Mark Props as Pass-Through

Use for props that are not transformed or used in internal logic:

```blade
@blaze(fold: true, safe: ['level'])

@props(['level' => 1])

<h{{ $level }}>{{ $slot }}</h{{ $level }}>
```

Now dynamic values fold correctly:

```blade
<x-heading :level="$isFeaturedSection ? 1 : 2" />
```

Produces:

```blade
<h{{ $isFeaturedSection ? 1 : 2 }}></h{{ $isFeaturedSection ? 1 : 2 }}>
```

### `unsafe` — Mark Slots as Non-Pass-Through

Force folding to abort when a slot is used in internal logic:

```blade
@blaze(fold: true, unsafe: ['slot'])

@if ($slot->hasActualContent())
    <span>No results</span>
@else
    <div>{{ $slot }}</div>
@endif
```

Also works with named slots:

```blade
@blaze(fold: true, unsafe: ['footer'])

<div>
    @if($footer->hasActualContent())
        ...
    @endif
</div>
```

### `unsafe` — Mark Attributes as Non-Pass-Through

For attributes resolved dynamically via `$attributes`:

```blade
@blaze(fold: true, unsafe: ['href'])

@php
$active = $attributes->get('href') === url()->current();
@endphp

<a {{ $attributes->merge(['data-active' => $active]) }}>
    {{ $slot }}
</a>
```

Mark the entire attribute bag as unsafe:

```blade
@blaze(fold: true, unsafe: ['attributes'])
```

### Parameter Reference

| Value | Target |
|-------|--------|
| `*` | All props / attributes / slots |
| `slot` | The default slot |
| `[name]` | A specific property / attribute / slot |
| `attributes` | Attributes not defined in `@props` |

## Global State — Never Fold

Components using these patterns must NOT be folded:

| Category | Examples |
|----------|----------|
| Database | `User::get()`, any Eloquent queries |
| Authentication | `auth()->check()`, `@auth`, `@guest` |
| Session | `session('key')` |
| Request | `request()->path()`, `request()->is()` |
| Validation | `$errors->has()`, `$errors->first()` |
| Time | `now()`, `Carbon::now()` |
| Security | `@csrf` |

Blaze attempts to detect these and throws an exception, but cannot catch everything.

## @unblaze — Escape Hatch for Dynamic Sections

When a component is mostly foldable but has a small dynamic section, use `@unblaze`:

```blade
@blaze(fold: true)

@props(['name', 'label'])

<div>
    <label>{{ $label }}</label>
    <input name="{{ $name }}">

    @unblaze(scope: ['name' => $name])
        @if($errors->has($scope['name']))
            {{ $errors->first($scope['name']) }}
        @endif
    @endunblaze
</div>
```

### How @unblaze Works

1. Content between `@unblaze`/`@endunblaze` is extracted before Blaze compilation
2. The rest of the template folds normally
3. The dynamic content is restored after folding with scope isolation
4. Variables are accessed via `$scope['key']` — not by original name

### Scope Passing

Variables from the component must be explicitly passed:

```blade
@unblaze(scope: ['name' => $name, 'id' => $id])
    {{-- Use $scope['name'] and $scope['id'] here --}}
@endunblaze
```

### Dynamic Attributes with @unblaze

Dynamic attributes work correctly — if `:name="$field"` is passed, the `@unblaze` scope receives the runtime expression:

```blade
<x-input :name="$field" />
```

The `$scope['name']` inside `@unblaze` correctly resolves to `$field` at runtime, not a placeholder.

### Nesting

`@unblaze` blocks can be nested in folded components. Each block maintains its own `$scope` variable, with save/restore to handle nesting correctly.

## Debugging Folding

Enable exception throwing to catch folding issues during development:

```php
Blaze::throw(); // Throws instead of silently falling back
```

## Folding Decision Checklist

Before enabling `fold: true`, verify:

- [ ] Component has no internal global state access (auth, session, request, errors)
- [ ] All `@props` used in logic receive only static values, OR are marked `unsafe`
- [ ] Pass-through props receiving dynamic values are marked `safe`
- [ ] Slots used in logic (`hasActualContent()`, conditionals) are marked `unsafe`
- [ ] Dynamic sections are wrapped in `@unblaze` with explicit scope
- [ ] Tested with `Blaze::throw()` enabled to catch silent fallbacks
