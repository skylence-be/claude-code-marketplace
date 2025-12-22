# Query Optimization

Livewire 4 database query optimization and N+1 prevention.

## Eager Loading Basics

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use App\Models\Post;

class EagerLoadingExample extends Component
{
    /**
     * BAD: N+1 Problem
     * 1 query for posts + N queries for authors + N queries for comments
     */
    public function badExample()
    {
        $posts = Post::all(); // 1 query

        foreach ($posts as $post) {
            echo $post->author->name; // N queries
            foreach ($post->comments as $comment) { // N queries
                echo $comment->author->name; // N * M queries
            }
        }
    }

    /**
     * GOOD: Eager Loading
     * Only 4 queries total regardless of data size
     */
    #[Computed]
    public function posts()
    {
        return Post::with([
            'author:id,name,email',
            'comments.author:id,name',
            'tags:id,name',
            'category:id,name',
        ])
        ->select('id', 'title', 'user_id', 'category_id', 'created_at')
        ->latest()
        ->get();
    }
}
```

## Select Specific Columns

```php
class OptimizedQueries extends Component
{
    /**
     * BAD: Loading all columns
     */
    public function badSelectAll()
    {
        return User::all(); // SELECT * FROM users
    }

    /**
     * GOOD: Select only needed columns
     */
    #[Computed]
    public function users()
    {
        return User::select('id', 'name', 'email', 'created_at')
            ->get();
    }

    /**
     * GOOD: With relationships
     */
    #[Computed]
    public function posts()
    {
        return Post::select('id', 'title', 'user_id')
            ->with('author:id,name') // Only id and name from author
            ->get();
    }
}
```

## withCount for Relationship Counts

```php
class PostsWithCounts extends Component
{
    /**
     * BAD: Loading full relationships just for count
     */
    public function badCounting()
    {
        $posts = Post::with('comments')->get();
        foreach ($posts as $post) {
            echo $post->comments->count(); // Loaded all comment data
        }
    }

    /**
     * GOOD: Count without loading
     */
    #[Computed]
    public function posts()
    {
        return Post::withCount([
            'comments',
            'comments as approved_comments_count' => fn($q) => $q->where('approved', true),
            'likes',
        ])
        ->with('author:id,name')
        ->get();
    }
}
```

```blade
@foreach($this->posts as $post)
    <div>
        {{ $post->title }}
        <span>{{ $post->comments_count }} comments</span>
        <span>{{ $post->approved_comments_count }} approved</span>
        <span>{{ $post->likes_count }} likes</span>
    </div>
@endforeach
```

## Conditional Eager Loading

```php
class ConditionalLoading extends Component
{
    public $showComments = false;
    public $selectedTag = null;

    #[Computed]
    public function posts()
    {
        $query = Post::query()
            ->select('id', 'title', 'user_id', 'created_at')
            ->with('author:id,name');

        // Only load comments if displayed
        if ($this->showComments) {
            $query->with('comments.author:id,name');
        }

        // Only load tags if filtering
        if ($this->selectedTag) {
            $query->with('tags')
                ->whereHas('tags', fn($q) => $q->where('id', $this->selectedTag));
        }

        return $query->get();
    }
}
```

## Lazy Eager Loading

```php
class LazyEagerLoading extends Component
{
    public $posts;

    public function mount()
    {
        // Initial load without heavy relationships
        $this->posts = Post::select('id', 'title')->get();
    }

    public function loadComments()
    {
        // Load relationships later when needed
        $this->posts->load([
            'comments' => fn($q) => $q->latest()->limit(5),
            'comments.author:id,name',
        ]);
    }
}
```

## Optimized Aggregates

```php
class OptimizedAggregates extends Component
{
    /**
     * BAD: Multiple separate queries
     */
    public function badAggregates()
    {
        $totalUsers = User::count();      // Query 1
        $totalPosts = Post::count();      // Query 2
        $activeUsers = User::where('active', true)->count(); // Query 3
    }

    /**
     * GOOD: Single query with subqueries
     */
    #[Computed]
    public function statistics()
    {
        return \DB::select("
            SELECT
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM posts) as total_posts,
                (SELECT COUNT(*) FROM users WHERE active = 1) as active_users
        ")[0];
    }
}
```

## Query Caching

```php
use Illuminate\Support\Facades\Cache;

class CachedQueries extends Component
{
    #[Computed]
    public function categories()
    {
        return Cache::remember('categories', 3600, function () {
            return Category::with('children')->whereNull('parent_id')->get();
        });
    }

    #[Computed]
    public function popularPosts()
    {
        $cacheKey = "popular_posts_{$this->category}";

        return Cache::remember($cacheKey, 600, function () {
            return Post::where('category_id', $this->category)
                ->orderBy('views', 'desc')
                ->limit(10)
                ->get();
        });
    }

    public function refreshCache()
    {
        Cache::forget('categories');
        unset($this->categories);
    }
}
```

## Pagination for Large Datasets

```php
use Livewire\WithPagination;

class OptimizedPagination extends Component
{
    use WithPagination;

    public $search = '';
    public $perPage = 20;

    #[Computed]
    public function products()
    {
        return Product::query()
            ->select('id', 'name', 'price', 'category_id')
            ->with('category:id,name')
            ->when($this->search, fn($q) => $q->where('name', 'like', "%{$this->search}%"))
            ->paginate($this->perPage);
    }

    public function updatingSearch()
    {
        $this->resetPage();
    }
}
```

## Index Optimization

```php
// Ensure indexes exist on frequently queried columns
Schema::table('posts', function (Blueprint $table) {
    $table->index('user_id');
    $table->index('category_id');
    $table->index('created_at');
    $table->index(['status', 'published_at']); // Compound index
});

// Query using indexed columns
class IndexedQueries extends Component
{
    #[Computed]
    public function posts()
    {
        return Post::where('status', 'published')      // Uses index
            ->where('published_at', '<=', now())       // Uses compound index
            ->orderBy('created_at', 'desc')            // Uses index
            ->limit(20)
            ->get();
    }
}
```

## Chunking Large Operations

```php
class ChunkedProcessing extends Component
{
    public $progress = 0;

    public function processLarge()
    {
        $total = Product::count();
        $processed = 0;

        Product::chunk(100, function ($products) use (&$processed, $total) {
            foreach ($products as $product) {
                // Process
                $processed++;
            }
            $this->progress = ($processed / $total) * 100;
        });
    }
}
```

## Testing Query Performance

```php
use Illuminate\Support\Facades\DB;

class PerformanceTest extends TestCase
{
    public function test_prevents_n_plus_one()
    {
        User::factory()->count(10)->create()->each(function ($user) {
            Post::factory()->count(5)->create(['user_id' => $user->id]);
        });

        DB::enableQueryLog();

        Livewire::test(OptimizedPosts::class);

        $queries = DB::getQueryLog();

        // Should be less than 5 queries, not 50+
        $this->assertLessThan(5, count($queries));
    }
}
```
