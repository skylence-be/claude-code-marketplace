---
name: laravel-caching-strategies
description: Master Laravel caching with Redis, File, Database drivers, cache tags, query caching, model caching, cache invalidation strategies, and Laravel Octane integration. Use when optimizing application performance, reducing database load, or scaling high-traffic applications.
---

# Laravel Caching Strategies

Comprehensive guide to implementing caching in Laravel.

## When to Use This Skill

- Reducing database query load
- Caching expensive computations
- Building high-performance applications
- Implementing cache invalidation
- Scaling with Redis

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Basic Operations | [basic-operations.md](basic-operations.md) | get, put, remember, forget |
| Cache Tags | [cache-tags.md](cache-tags.md) | Organized cache management |
| Query Caching | [query-caching.md](query-caching.md) | Eloquent query caching |
| Invalidation | [invalidation.md](invalidation.md) | Cache clearing strategies |

## Quick Start

```php
use Illuminate\Support\Facades\Cache;

// Store in cache (10 minutes)
Cache::put('key', 'value', 600);

// Retrieve from cache
$value = Cache::get('key');

// Remember pattern (get or store)
$users = Cache::remember('users', 3600, function () {
    return User::all();
});

// Remove from cache
Cache::forget('key');

// Configure in .env
CACHE_DRIVER=redis
```

## Core Concepts

### Cache Drivers
- **Redis**: Fast, in-memory, supports tags (production)
- **Memcached**: Fast, in-memory, no tags
- **Database**: Persistent, slower
- **File**: Simple, good for dev
- **Array**: Testing only

### Cache Operations
```php
// Store
Cache::put('key', $value, 3600);
Cache::forever('key', $value);

// Retrieve
$value = Cache::get('key');
$value = Cache::get('key', 'default');

// Remember (get or store)
$value = Cache::remember('key', 3600, fn() => expensiveOperation());

// Check and forget
Cache::has('key');
Cache::forget('key');
Cache::flush(); // Clear all
```

## Quick Reference

### Configuration

```php
// config/cache.php
'stores' => [
    'redis' => [
        'driver' => 'redis',
        'connection' => 'cache',
        'lock_connection' => 'default',
    ],
],
```

### Cache Tags (Redis/Memcached)

```php
// Tag cache items
Cache::tags(['posts', 'users'])->put('key', $value, 3600);

// Retrieve tagged items
$value = Cache::tags(['posts'])->get('key');

// Clear all items with tag
Cache::tags(['posts'])->flush();
```

### Model Caching

```php
class Post extends Model
{
    public function getCachedAttribute()
    {
        return Cache::remember("post.{$this->id}", 3600, function () {
            return $this->load(['author', 'comments']);
        });
    }

    protected static function booted(): void
    {
        static::saved(fn($post) => Cache::forget("post.{$post->id}"));
        static::deleted(fn($post) => Cache::forget("post.{$post->id}"));
    }
}
```

## Best Practices

1. **Use Redis** for production caching
2. **Set appropriate TTLs** for cached data
3. **Use cache tags** for organized invalidation
4. **Cache at the right level** (query, model, page)
5. **Implement cache warming** for critical data
6. **Monitor cache hit rates**

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Stale data | Set appropriate TTLs |
| Cache stampede | Use locks or cache::remember |
| Over-caching | Only cache expensive operations |
| No invalidation | Implement event-based invalidation |
