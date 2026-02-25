# Runtime Memoization

Memoization caches the output of components that are rendered repeatedly with the same props on a single page. Ideal for icons, avatars, badges, and status indicators.

## How It Works

The output is cached based on the component name and the props passed to it. When a memoized component appears multiple times with the same props, it renders only once.

```blade
@blaze(memo: true)

@props(['name'])

<x-dynamic-component :component="'icon-' . $name" />
```

When included:

```blade
<x-icon :name="$task->status->icon" />
```

Blaze wraps the call in a cache check:

```php
<?php $key = Memo::key('icon', ['name' => $task->status->icon]); ?>

<?php if (! Memo::has($key)): ?>
    <!-- Render and store into cache: -->
    <x-icon :name="$task->status->icon">
<?php endif; ?>

<?php echo Memo::get($key); ?>
```

## Enabling Memoization

### Per-Component

```blade
@blaze(memo: true)

@props(['name'])

<svg class="w-5 h-5">
    <use href="#icon-{{ $name }}" />
</svg>
```

### Per-Directory

```php
Blaze::optimize()
    ->in(resource_path('views/components/icons'), memo: true);
```

## Ideal Candidates

Components that benefit most from memoization:

| Component Type | Why |
|---------------|-----|
| Icons | Same icon name renders identical SVG |
| Avatar placeholders | Same initials produce same output |
| Status badges | Limited set of statuses |
| Rating stars | Same rating = same output |
| Country flags | Same country code = same flag |

## Constraint: No Slots

Memoization only works on components **without slots**. Slots make the output depend on caller context, which breaks cache validity.

```blade
{{-- Works with memo --}}
<x-icon name="check" />

{{-- Cannot use memo (has slot) --}}
<x-badge>Active</x-badge>
```

## Example: Icon System

```blade
{{-- resources/views/components/icon.blade.php --}}
@blaze(memo: true)

@props(['name', 'size' => 'md'])

@php
$sizeClass = match($size) {
    'sm' => 'w-4 h-4',
    'md' => 'w-5 h-5',
    'lg' => 'w-6 h-6',
    'xl' => 'w-8 h-8',
};
@endphp

<svg {{ $attributes->class([$sizeClass]) }}>
    <use href="/icons.svg#{{ $name }}" />
</svg>
```

Usage in a table with 100 rows:

```blade
@foreach($tasks as $task)
    <tr>
        <td><x-icon :name="$task->status->icon" /></td>
        <td>{{ $task->title }}</td>
        <td><x-icon :name="$task->priority->icon" /></td>
    </tr>
@endforeach
```

If 50 tasks share the same status, the icon renders only once for that status — the rest are served from the memo cache.

## Example: Avatar Component

```blade
{{-- resources/views/components/avatar.blade.php --}}
@blaze(memo: true)

@props(['name', 'size' => 'md'])

@php
$initials = collect(explode(' ', $name))
    ->map(fn ($word) => strtoupper($word[0]))
    ->take(2)
    ->join('');

$colors = ['bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-purple-500'];
$color = $colors[crc32($name) % count($colors)];

$sizeClass = match($size) {
    'sm' => 'w-6 h-6 text-xs',
    'md' => 'w-8 h-8 text-sm',
    'lg' => 'w-10 h-10 text-base',
};
@endphp

<span {{ $attributes->class(["inline-flex items-center justify-center rounded-full text-white {$color} {$sizeClass}"]) }}>
    {{ $initials }}
</span>
```

## Combining with Directory Configuration

```php
Blaze::optimize()
    ->in(resource_path('views/components'))
    ->in(resource_path('views/components/icons'), memo: true)
    ->in(resource_path('views/components/avatars'), memo: true);
```

## Limitations

- Only works on slot-less components
- Cache is per-request (not persisted across requests)
- Cache key is based on component name + all props — large prop objects increase key size
- Does not help if every invocation has unique props
