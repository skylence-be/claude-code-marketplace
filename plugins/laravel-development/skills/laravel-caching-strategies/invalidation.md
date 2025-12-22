# Cache Invalidation

Strategies for clearing stale cache data.

## Time-Based (TTL)

```php
// Expire after 1 hour
Cache::put('key', $value, 3600);

// Expire at specific time
Cache::put('key', $value, now()->endOfDay());

// Short TTL for frequently changing data
Cache::put('active_users', $count, 60); // 1 minute

// Long TTL for stable data
Cache::put('site_settings', $settings, 86400); // 24 hours
```

## Event-Based Invalidation

```php
class Post extends Model
{
    protected static function booted(): void
    {
        // Clear cache when model changes
        static::saved(function ($post) {
            Cache::forget("post:{$post->id}");
            Cache::forget('posts:all');
            Cache::forget("posts:category:{$post->category_id}");
            Cache::forget("user:{$post->user_id}:posts");
        });

        static::deleted(function ($post) {
            Cache::forget("post:{$post->id}");
            Cache::forget('posts:all');
        });
    }
}
```

## Observer Pattern

```php
class PostObserver
{
    public function saved(Post $post): void
    {
        $this->invalidateCache($post);
    }

    public function deleted(Post $post): void
    {
        $this->invalidateCache($post);
    }

    protected function invalidateCache(Post $post): void
    {
        Cache::tags(['posts'])->flush();

        // Or selective invalidation
        Cache::forget("post:{$post->id}");
        Cache::forget("user:{$post->user_id}:posts");
    }
}

// Register in AppServiceProvider
Post::observe(PostObserver::class);
```

## Event Listener

```php
// Event
class PostUpdated
{
    public function __construct(public Post $post) {}
}

// Listener
class ClearPostCache
{
    public function handle(PostUpdated $event): void
    {
        Cache::forget("post:{$event->post->id}");
        Cache::forget('posts:featured');
    }
}

// Dispatch event
PostUpdated::dispatch($post);
```

## Cache Warmer

```php
class CacheWarmer
{
    public function warmPosts(): void
    {
        // Clear and rebuild cache
        Cache::forget('posts:all');

        Post::published()
            ->chunk(100, function ($posts) {
                foreach ($posts as $post) {
                    Cache::put("post:{$post->id}", $post, 3600);
                }
            });

        Cache::put('posts:all', Post::published()->get(), 3600);
    }
}

// Schedule cache warming
// app/Console/Kernel.php
$schedule->call(fn() => app(CacheWarmer::class)->warmPosts())
    ->hourly();
```

## Versioned Keys

```php
class VersionedCache
{
    public function version(string $type): int
    {
        return Cache::get("version:{$type}", 1);
    }

    public function incrementVersion(string $type): void
    {
        Cache::increment("version:{$type}");
    }

    public function key(string $type, string $key): string
    {
        $version = $this->version($type);
        return "{$type}:v{$version}:{$key}";
    }

    public function invalidateType(string $type): void
    {
        $this->incrementVersion($type);
        // Old versioned keys will naturally expire
    }
}

// Usage
$cache = new VersionedCache();
$key = $cache->key('posts', 'all'); // posts:v1:all
Cache::put($key, $posts, 3600);

// Invalidate all posts (no explicit deletion needed)
$cache->invalidateType('posts');
// New key becomes posts:v2:all
```

## Cascade Invalidation

```php
class CacheInvalidator
{
    protected array $dependencies = [
        'post' => ['posts:all', 'posts:featured', 'category:*:posts'],
        'user' => ['users:all', 'users:active'],
        'comment' => ['post:*:comments', 'user:*:comments'],
    ];

    public function invalidate(string $type, ?int $id = null): void
    {
        if ($id) {
            Cache::forget("{$type}:{$id}");
        }

        foreach ($this->dependencies[$type] ?? [] as $pattern) {
            if (str_contains($pattern, '*')) {
                // Use tags or pattern matching
                Cache::tags([$type])->flush();
            } else {
                Cache::forget($pattern);
            }
        }
    }
}
```
