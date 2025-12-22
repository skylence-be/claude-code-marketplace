# Query Caching

Cache Eloquent queries and results.

## Basic Query Caching

```php
use Illuminate\Support\Facades\Cache;

// Cache query results
$posts = Cache::remember('published_posts', 3600, function () {
    return Post::where('status', 'published')
        ->with('author')
        ->latest()
        ->get();
});

// Cache with dynamic key
$posts = Cache::remember("posts:category:{$categoryId}", 3600, function () use ($categoryId) {
    return Post::where('category_id', $categoryId)->get();
});

// Cache paginated results
$page = request('page', 1);
$posts = Cache::remember("posts:page:{$page}", 3600, function () {
    return Post::paginate(20);
});
```

## Model-Level Caching

```php
class Post extends Model
{
    /**
     * Get cached post with relationships.
     */
    public static function findCached(int $id): ?self
    {
        return Cache::remember("post:{$id}", 3600, function () use ($id) {
            return static::with(['author', 'category', 'tags'])->find($id);
        });
    }

    /**
     * Get cached published posts.
     */
    public static function published(): Collection
    {
        return Cache::remember('posts:published', 3600, function () {
            return static::where('status', 'published')
                ->orderBy('published_at', 'desc')
                ->get();
        });
    }

    /**
     * Clear cache on model changes.
     */
    protected static function booted(): void
    {
        static::saved(fn($post) => static::clearCache($post));
        static::deleted(fn($post) => static::clearCache($post));
    }

    protected static function clearCache(Post $post): void
    {
        Cache::forget("post:{$post->id}");
        Cache::forget('posts:published');
    }
}
```

## Repository Pattern

```php
class PostRepository
{
    private int $ttl = 3600;

    public function find(int $id): ?Post
    {
        return Cache::remember("post:{$id}", $this->ttl, function () use ($id) {
            return Post::with('author')->find($id);
        });
    }

    public function all(): Collection
    {
        return Cache::remember('posts:all', $this->ttl, function () {
            return Post::all();
        });
    }

    public function byCategory(int $categoryId): Collection
    {
        return Cache::remember(
            "posts:category:{$categoryId}",
            $this->ttl,
            fn() => Post::where('category_id', $categoryId)->get()
        );
    }

    public function save(Post $post): Post
    {
        $post->save();
        $this->invalidate($post);
        return $post;
    }

    public function invalidate(Post $post): void
    {
        Cache::forget("post:{$post->id}");
        Cache::forget('posts:all');
        Cache::forget("posts:category:{$post->category_id}");
    }
}
```

## Aggregate Caching

```php
class StatsService
{
    public function getUserStats(User $user): array
    {
        return Cache::remember("user:{$user->id}:stats", 3600, function () use ($user) {
            return [
                'posts_count' => $user->posts()->count(),
                'comments_count' => $user->comments()->count(),
                'total_views' => $user->posts()->sum('views'),
                'avg_rating' => $user->posts()->avg('rating'),
            ];
        });
    }

    public function getGlobalStats(): array
    {
        return Cache::remember('stats:global', 3600, function () {
            return [
                'total_posts' => Post::count(),
                'total_users' => User::count(),
                'posts_today' => Post::whereDate('created_at', today())->count(),
            ];
        });
    }
}
```

## Relationship Caching

```php
class User extends Model
{
    /**
     * Get cached posts for user.
     */
    public function getCachedPostsAttribute(): Collection
    {
        return Cache::remember(
            "user:{$this->id}:posts",
            3600,
            fn() => $this->posts()->with('category')->get()
        );
    }

    /**
     * Get cached post count.
     */
    public function getPostsCountAttribute(): int
    {
        return Cache::remember(
            "user:{$this->id}:posts_count",
            3600,
            fn() => $this->posts()->count()
        );
    }
}
```
