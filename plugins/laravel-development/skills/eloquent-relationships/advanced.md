# Advanced Relationship Patterns

Advanced patterns for complex relationship scenarios.

## Default Models

Prevent null errors with default models:

```php
class Post extends Model
{
    /**
     * Get the author (with default if none exists).
     */
    public function author()
    {
        return $this->belongsTo(User::class, 'user_id')
            ->withDefault([
                'name' => 'Guest Author',
                'email' => 'guest@example.com'
            ]);
    }

    /**
     * Use callback for complex defaults.
     */
    public function category()
    {
        return $this->belongsTo(Category::class)
            ->withDefault(function ($category, $post) {
                $category->name = 'Uncategorized';
                $category->slug = 'uncategorized';
            });
    }
}

// Usage - No need to check if author exists
$post = Post::find(1);
echo $post->author->name; // Returns 'Guest Author' if no author
```

## Touching Parent Timestamps

Automatically update parent timestamps when child is modified:

```php
class Comment extends Model
{
    /**
     * All relationships to touch when comment is saved.
     */
    protected $touches = ['post', 'author'];

    public function post()
    {
        return $this->belongsTo(Post::class);
    }

    public function author()
    {
        return $this->belongsTo(User::class, 'user_id');
    }
}

// When a comment is created/updated, both post and author
// updated_at timestamps are automatically updated
$comment->save(); // Updates comment, post, and user timestamps
```

## Relationship Caching

Cache expensive relationship queries:

```php
class User extends Model
{
    /**
     * Get cached posts.
     */
    public function getCachedPostsAttribute()
    {
        return Cache::remember(
            "user.{$this->id}.posts",
            now()->addHour(),
            fn () => $this->posts()->get()
        );
    }

    /**
     * Clear posts cache when relationship changes.
     */
    protected static function booted(): void
    {
        static::saved(function ($user) {
            Cache::forget("user.{$user->id}.posts");
        });
    }

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }
}

class Post extends Model
{
    protected static function booted(): void
    {
        // Clear cache when post is created/updated/deleted
        static::saved(function ($post) {
            Cache::forget("user.{$post->user_id}.posts");
        });

        static::deleted(function ($post) {
            Cache::forget("user.{$post->user_id}.posts");
        });
    }
}

// Usage
$user->cachedPosts; // Cached for 1 hour
```

## Aggregate Queries

Load aggregates without loading relationships:

```php
// Basic aggregates
$users = User::withCount('posts')
    ->withSum('posts', 'views')
    ->withAvg('posts', 'rating')
    ->withMax('posts', 'created_at')
    ->withMin('posts', 'created_at')
    ->get();

// Access: $user->posts_count, $user->posts_sum_views, etc.

// Conditional aggregates
$users = User::withCount([
    'posts',
    'posts as published_posts_count' => function ($query) {
        $query->where('status', 'published');
    },
    'posts as draft_posts_count' => function ($query) {
        $query->where('status', 'draft');
    }
])
->withSum([
    'posts as total_views' => function ($query) {
        $query->where('status', 'published');
    }
], 'views')
->get();

// Load aggregates on existing collections
$users = User::all();
$users->loadCount('posts');
$users->loadSum('posts', 'views');
$users->loadAvg('posts', 'rating');
```

## Custom Intermediate Tables

For complex many-to-many with business logic:

```php
class Enrollment extends Pivot
{
    protected $table = 'enrollments';

    protected $casts = [
        'enrolled_at' => 'datetime',
        'completed_at' => 'datetime',
    ];

    public function isCompleted(): bool
    {
        return $this->completed_at !== null;
    }

    public function markAsCompleted(): void
    {
        $this->update(['completed_at' => now()]);
    }
}

class User extends Model
{
    public function courses(): BelongsToMany
    {
        return $this->belongsToMany(Course::class, 'enrollments')
            ->using(Enrollment::class)
            ->withPivot(['enrolled_at', 'completed_at', 'progress'])
            ->withTimestamps();
    }
}

// Access pivot methods
$user->courses->first()->pivot->isCompleted();
$user->courses->first()->pivot->markAsCompleted();
```

## Dynamic Relationships

Define relationships at runtime:

```php
class Post extends Model
{
    public function relatedContent()
    {
        // Dynamic based on post type
        return match($this->type) {
            'article' => $this->hasMany(ArticleSection::class),
            'gallery' => $this->hasMany(GalleryImage::class),
            'video' => $this->hasOne(VideoEmbed::class),
            default => $this->hasMany(Content::class),
        };
    }
}
```

## Global Relationship Scopes

Apply scopes to all relationship queries:

```php
class Comment extends Model
{
    protected static function booted(): void
    {
        // Only show approved comments globally
        static::addGlobalScope('approved', function ($query) {
            $query->where('approved', true);
        });
    }
}

// To include unapproved:
Comment::withoutGlobalScope('approved')->get();
$post->comments()->withoutGlobalScope('approved')->get();
```

## Testing Relationships

```php
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

it('has many posts', function () {
    $user = User::factory()->create();
    $posts = Post::factory()->count(3)->create(['user_id' => $user->id]);

    expect($user->posts)->toHaveCount(3);
    expect($user->posts->first())->toBeInstanceOf(Post::class);
});

it('eager loading prevents n+1', function () {
    User::factory()->count(10)->create()->each(
        fn($user) => Post::factory()->count(5)->create(['user_id' => $user->id])
    );

    DB::enableQueryLog();

    $posts = Post::with('author')->get();
    $posts->each(fn($post) => $post->author->name);

    // Should be 2 queries: 1 for posts, 1 for users
    expect(DB::getQueryLog())->toHaveCount(2);
});

it('syncs many-to-many relationships', function () {
    $user = User::factory()->create();
    $roles = Role::factory()->count(3)->create();

    $user->roles()->sync($roles->pluck('id'));

    expect($user->roles)->toHaveCount(3);
    expect($user->roles->first())->toBeInstanceOf(Role::class);
});
```

## Real-World Examples

### Blog with Categories and Tags
```php
class Post extends Model
{
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class)
            ->withDefault(['name' => 'Uncategorized']);
    }

    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class)->withTimestamps();
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    public function approvedComments(): HasMany
    {
        return $this->hasMany(Comment::class)
            ->where('approved', true)
            ->orderBy('created_at', 'desc');
    }

    public function scopeWithRelations($query)
    {
        return $query->with([
            'author:id,name,email',
            'category:id,name,slug',
            'tags:id,name,slug',
        ])->withCount(['comments', 'approvedComments']);
    }
}

// Usage
$posts = Post::published()->withRelations()->paginate(20);
```

### E-commerce with Products and Orders
```php
class Order extends Model
{
    public function customer(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function products(): BelongsToMany
    {
        return $this->belongsToMany(Product::class, 'order_items')
            ->withPivot('quantity', 'price', 'subtotal')
            ->withTimestamps();
    }

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class);
    }

    public function shippingAddress(): HasOne
    {
        return $this->hasOne(OrderAddress::class)
            ->where('type', 'shipping');
    }

    public function billingAddress(): HasOne
    {
        return $this->hasOne(OrderAddress::class)
            ->where('type', 'billing');
    }
}

// Optimized loading
$order = Order::with([
    'customer:id,name,email',
    'products.category',
    'items.product',
    'shippingAddress',
    'billingAddress',
])->findOrFail($orderId);
```
