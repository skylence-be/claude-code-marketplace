---
name: livewire-performance-optimization
description: Master Livewire 4 performance optimization including query optimization, N+1 prevention, lazy loading, computed properties, polling strategies, wire:navigate, database queries, and performance testing. Use when building high-performance applications, optimizing slow components, or scaling Livewire applications.
---

# Livewire Performance Optimization

Comprehensive guide to optimizing Livewire 4 applications for maximum performance.

## When to Use This Skill

- Optimizing slow-loading Livewire components and pages
- Preventing N+1 query problems in component relationships
- Implementing lazy loading for heavy components and data
- Optimizing database queries and reducing query counts
- Implementing efficient polling strategies for real-time updates
- Using wire:navigate for SPA-like navigation performance

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Query Optimization | `query-optimization.md` | Eager loading, N+1, select columns |
| Computed Caching | `computed-caching.md` | #[Computed], cache invalidation |
| Lazy Loading | `lazy-loading.md` | #[Lazy], conditional loading |
| Wire Navigate | `wire-navigate.md` | SPA navigation, prefetching |

## Quick Reference

### Computed Properties for Query Caching

```php
use Livewire\Attributes\Computed;

class Dashboard extends Component
{
    public $userId;

    #[Computed]
    public function user()
    {
        return User::with('profile')->find($this->userId);
    }

    #[Computed]
    public function orders()
    {
        return $this->user->orders()->latest()->limit(10)->get();
    }

    // Invalidate cache manually
    public function refresh()
    {
        unset($this->user);
    }
}
```

### Eager Loading (N+1 Prevention)

```php
// BAD: N+1 queries
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name; // N additional queries
}

// GOOD: 2 queries total
$posts = Post::with('author')->get();
foreach ($posts as $post) {
    echo $post->author->name; // No additional query
}
```

### Lazy Component Loading

```php
use Livewire\Attributes\Lazy;

#[Lazy]
class HeavyWidget extends Component
{
    public function placeholder()
    {
        return view('loading-placeholder');
    }
}
```

```blade
<livewire:heavy-widget lazy />
```

### Wire Navigate

```blade
{{-- SPA-like navigation --}}
<a href="/dashboard" wire:navigate>Dashboard</a>

{{-- Prefetch on hover --}}
<a href="/products" wire:navigate.hover>Products</a>
```

## Best Practices

1. **Always eager load** relationships with `with()`
2. **Use computed properties** for expensive operations
3. **Paginate large datasets** instead of loading all
4. **Lazy load** heavy components
5. **Debounce** user input to reduce requests
6. **Use wire:navigate** for instant navigation

## Common Pitfalls

1. **Not using #[Computed]** - Query runs every render
2. **Forgetting eager loading** - N+1 queries
3. **Loading all data** - No pagination
4. **Polling too frequently** - Excessive server load
5. **Large component state** - Slow serialization
