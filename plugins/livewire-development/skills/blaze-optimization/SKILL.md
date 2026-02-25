---
name: blaze-optimization
description: Master Livewire Blaze - the Blade component performance optimizer. Covers function compilation, runtime memoization, compile-time folding, @blaze/@unblaze directives, safe/unsafe selective folding, debug profiling, and migration strategies. Use when optimizing Blade component performance, enabling Blaze on projects, or diagnosing folding issues.
category: livewire
tags: [blaze, blade, performance, optimization, folding, memoization, compilation]
related_skills: [livewire-performance-optimization, livewire-blueprint]
---

# Blaze Optimization

Comprehensive guide to optimizing anonymous Blade component rendering with Livewire Blaze. Blaze compiles templates into optimized PHP functions, eliminating 91-97% of rendering overhead.

## When to Use This Skill

- Enabling Blaze on a new or existing Laravel project
- Choosing the right optimization strategy per component (compile, memo, fold)
- Configuring compile-time folding with safe/unsafe boundaries
- Using @unblaze to preserve dynamic sections inside folded components
- Debugging Blaze compilation issues and folding failures
- Measuring performance improvements with the Blaze profiler
- Migrating existing Blade components to be Blaze-compatible

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Function Compilation | [function-compilation.md](function-compilation.md) | Default strategy, enabling Blaze, directory config |
| Folding Strategies | [folding-strategies.md](folding-strategies.md) | Compile-time folding, safe/unsafe, @unblaze |
| Memoization | [memoization.md](memoization.md) | Runtime caching for repeated components |
| Debugging & Profiling | [debugging.md](debugging.md) | Debug mode, profiler, performance comparison |

## Quick Reference

### Enable Blaze Per-Component

```blade
{{-- Default function compilation --}}
@blaze

{{-- With memoization --}}
@blaze(memo: true)

{{-- With compile-time folding --}}
@blaze(fold: true)

{{-- Folding with selective safety --}}
@blaze(fold: true, safe: ['level'], unsafe: ['slot'])
```

### Enable Blaze Per-Directory

```php
// AppServiceProvider::boot()
use Livewire\Blaze\Blaze;

Blaze::optimize()
    ->in(resource_path('views/components'))
    ->in(resource_path('views/components/icons'), memo: true)
    ->in(resource_path('views/components/ui'), fold: true)
    ->in(resource_path('views/components/legacy'), compile: false);
```

### @unblaze Escape Hatch

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

### Strategy Decision Tree

| Component Type | Strategy | Why |
|---------------|----------|-----|
| Any anonymous component | `@blaze` (default) | Safe, 91-97% reduction |
| Repeated slot-less (icons, badges) | `memo: true` | Renders once per unique props |
| Static-prop components | `fold: true` | Zero runtime cost |
| Mixed static/dynamic props | `fold: true` + `safe: [...]` | Fold safe parts |
| Components with $errors | `fold: true` + `@unblaze` | Isolate dynamic validation |
| Uses global state internally | Default compile only | Folding would produce stale HTML |
| Class-based components | Cannot use Blaze | Not supported |

### Performance Benchmarks

```
Rendering 25,000 anonymous components:

Without Blaze  ████████████████████████████████████████  500ms
With Blaze     █                                          13ms

Folded components (constant time):
25,000  components: 0.68ms
50,000  components: 0.68ms
100,000 components: 0.68ms
```

## Limitations

- Class-based components not supported
- `$component` variable not available
- View composers/creators/lifecycle events do not fire
- `View::share()` variables not auto-injected (use `$__env->shared('key')`)
- `@aware` only works between Blaze-compiled components
- Cannot render Blaze components via `view()` — must use `<x-component>` tags

## Best Practices

1. **Start with function compilation** — safe default for all anonymous components
2. **Expand gradually** — enable per-directory, verify compatibility before widening
3. **Always run `php artisan view:clear`** after any Blaze configuration change
4. **Audit for global state** before enabling folding (auth, session, request, errors, CSRF)
5. **Use `safe` sparingly** — only for props proven to be pass-through
6. **Prefer `@unblaze`** over disabling fold when only a small section is dynamic
7. **Use the profiler** to measure actual gains before and after
8. **Memoize icons and badges** — highest ROI for memo strategy

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Folding a component that uses `auth()` | Remove `fold: true`, use default compilation |
| Folding with dynamic prop used in `match()` | Blaze auto-aborts; if needed, restructure to pass-through |
| Forgot `view:clear` after config change | Always run `php artisan view:clear` |
| `@aware` not working across Blaze/Blade boundary | Both parent and child must use Blaze |
| Memoizing a component with slots | Memo only works on slot-less components |
| `@unblaze` without `scope` parameter | Variables must be explicitly passed via `scope: [...]` |
| Using `view('component')` to render | Blaze components must use `<x-component>` tag syntax |
