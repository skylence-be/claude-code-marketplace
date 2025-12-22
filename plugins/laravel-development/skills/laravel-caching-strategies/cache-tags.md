# Cache Tags

Organize cache with tags for group invalidation.

**Note:** Cache tags are only supported by Redis and Memcached drivers.

## Basic Tag Usage

```php
use Illuminate\Support\Facades\Cache;

// Store with tags
Cache::tags(['posts', 'featured'])->put('post:1', $post, 3600);
Cache::tags(['posts'])->put('post:2', $post2, 3600);
Cache::tags(['users'])->put('user:1', $user, 3600);

// Retrieve tagged items
$post = Cache::tags(['posts'])->get('post:1');

// Remember with tags
$posts = Cache::tags(['posts'])->remember('all_posts', 3600, function () {
    return Post::all();
});
```

## Flush Tagged Items

```php
// Clear all items with 'posts' tag
Cache::tags(['posts'])->flush();

// Both post:1 and post:2 are cleared
// user:1 is unaffected

// Clear items with multiple tags
Cache::tags(['posts', 'featured'])->flush();
```

## Tag Strategies

### By Resource Type

```php
// Posts
Cache::tags(['posts'])->put("post:{$id}", $post, 3600);
Cache::tags(['posts', 'comments'])->put("post:{$id}:comments", $comments, 3600);

// Users
Cache::tags(['users'])->put("user:{$id}", $user, 3600);
Cache::tags(['users', 'posts'])->put("user:{$id}:posts", $userPosts, 3600);

// Clear all user-related cache
Cache::tags(['users'])->flush();
```

### By Feature

```php
// Dashboard widgets
Cache::tags(['dashboard', 'analytics'])->put('stats', $stats, 600);
Cache::tags(['dashboard', 'notifications'])->put('alerts', $alerts, 60);

// Clear entire dashboard cache
Cache::tags(['dashboard'])->flush();
```

### By User

```php
// User-specific cache
Cache::tags(["user:{$userId}"])->put('preferences', $prefs, 3600);
Cache::tags(["user:{$userId}", 'notifications'])->put('unread', $count, 60);

// Clear user's cache on logout
Cache::tags(["user:{$userId}"])->flush();
```

## Model Events with Tags

```php
class Post extends Model
{
    protected static function booted(): void
    {
        static::saved(function ($post) {
            // Clear post cache
            Cache::tags(['posts'])->forget("post:{$post->id}");
            Cache::tags(['posts'])->forget('all_posts');

            // Clear user's posts cache
            Cache::tags(["user:{$post->user_id}"])->forget("user:{$post->user_id}:posts");
        });

        static::deleted(function ($post) {
            Cache::tags(['posts'])->flush(); // Or selective invalidation
        });
    }
}
```

## Service Pattern

```php
class CacheService
{
    public function getPost(int $id): ?Post
    {
        return Cache::tags(['posts'])->remember(
            "post:{$id}",
            3600,
            fn() => Post::with('author')->find($id)
        );
    }

    public function invalidatePost(Post $post): void
    {
        Cache::tags(['posts'])->forget("post:{$post->id}");
        Cache::tags(['posts'])->forget('all_posts');
        Cache::tags(['posts'])->forget("category:{$post->category_id}:posts");
    }

    public function invalidateAllPosts(): void
    {
        Cache::tags(['posts'])->flush();
    }
}
```
