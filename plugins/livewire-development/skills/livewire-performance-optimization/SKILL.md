---
name: livewire-performance-optimization
description: Master Livewire 4 performance optimization including query optimization, N+1 prevention, lazy loading, computed properties, polling strategies, wire:navigate, database queries, and performance testing. Use when building high-performance applications, optimizing slow components, or scaling Livewire applications.
---

# Livewire Performance Optimization

Comprehensive guide to optimizing Livewire 4 applications for maximum performance, covering database query optimization, N+1 problem prevention, lazy loading strategies, computed property caching, efficient polling, wire:navigate implementation, and performance testing methodologies.

## When to Use This Skill

- Optimizing slow-loading Livewire components and pages
- Preventing N+1 query problems in component relationships
- Implementing lazy loading for heavy components and data
- Optimizing database queries and reducing query counts
- Implementing efficient polling strategies for real-time updates
- Using wire:navigate for SPA-like navigation performance
- Caching computed properties and expensive operations
- Reducing component payload sizes and render times
- Optimizing file uploads and large data transfers
- Implementing performance monitoring and testing

## Core Concepts

### 1. Query Optimization
- **Eager loading**: Load relationships upfront with `with()`
- **Select specific columns**: Only load required database fields
- **Query caching**: Cache expensive database queries
- **Chunking**: Process large datasets in batches
- **Indexing**: Ensure proper database indexes exist

### 2. N+1 Prevention
- **Eager loading relationships**: Use `with()` and `load()`
- **withCount()**: Count relationships without loading data
- **Lazy eager loading**: Load relationships after initial query
- **Query monitoring**: Use Laravel Debugbar or Telescope
- **Relationship preloading**: Load nested relationships efficiently

### 3. Lazy Loading
- **Component lazy loading**: Load components on demand
- **Data pagination**: Paginate large datasets
- **Infinite scrolling**: Load data progressively
- **Deferred loading**: Delay component initialization
- **Conditional rendering**: Load components only when needed

### 4. Computed Properties
- **#[Computed] attribute**: Cache expensive calculations
- **Property dependencies**: Automatic cache invalidation
- **Memory efficiency**: Reduce redundant computations
- **Query reduction**: Cache database queries in computed properties

### 5. Wire:Navigate
- **SPA-like navigation**: Navigate without full page reload
- **Persistent layouts**: Keep layout components alive
- **Prefetching**: Load pages before user clicks
- **Progress indicators**: Show navigation progress
- **State preservation**: Maintain component state across navigation

## Quick Start

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use Livewire\WithPagination;
use App\Models\Post;

class OptimizedPosts extends Component
{
    use WithPagination;

    public $search = '';

    /**
     * Computed property with automatic caching.
     * Only re-queries when $search or page changes.
     */
    #[Computed]
    public function posts()
    {
        return Post::with('author:id,name') // Eager load, select specific columns
            ->select('id', 'title', 'user_id', 'created_at') // Only needed columns
            ->when($this->search, fn($q) => $q->where('title', 'like', "%{$this->search}%"))
            ->latest()
            ->paginate(20);
    }

    public function render()
    {
        return view('livewire.optimized-posts');
    }
}
```

```blade
<div>
    <input type="text" wire:model.live.debounce.500ms="search" placeholder="Search...">

    @foreach($this->posts as $post)
        <article>
            <h3>{{ $post->title }}</h3>
            <p>By {{ $post->author->name }}</p>
        </article>
    @endforeach

    {{ $this->posts->links() }}
</div>
```

## Fundamental Patterns

### Pattern 1: Eager Loading and N+1 Prevention

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
     * This will execute 1 query for posts + N queries for authors
     */
    public function badExample()
    {
        $posts = Post::all(); // 1 query

        foreach ($posts as $post) {
            echo $post->author->name; // N additional queries
            foreach ($post->comments as $comment) { // N more queries
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
            'author:id,name,email', // Eager load with specific columns
            'comments.author:id,name', // Nested eager loading
            'tags:id,name', // Many-to-many relationship
            'category:id,name', // BelongsTo relationship
        ])
        ->select('id', 'title', 'user_id', 'category_id', 'created_at')
        ->latest()
        ->get();
    }

    /**
     * GOOD: Conditional Eager Loading
     * Load relationships only when needed
     */
    #[Computed]
    public function postsWithConditionalLoading()
    {
        $query = Post::query();

        // Only load comments if we'll display them
        if ($this->showComments) {
            $query->with('comments.author');
        }

        // Only load tags if filtering by tag
        if ($this->selectedTag) {
            $query->with('tags');
        }

        return $query->get();
    }

    /**
     * GOOD: Count relationships without loading
     */
    #[Computed]
    public function postsWithCounts()
    {
        return Post::withCount([
            'comments', // Adds comments_count attribute
            'comments as approved_comments_count' => function ($query) {
                $query->where('approved', true);
            },
            'likes' // Adds likes_count attribute
        ])
        ->with('author:id,name')
        ->get();
    }

    /**
     * GOOD: Lazy Eager Loading
     * Load relationships after initial query
     */
    public function lazyEagerLoading()
    {
        $posts = Post::all();

        // Later, decide to load relationships
        $posts->load([
            'author:id,name',
            'comments' => function ($query) {
                $query->latest()->limit(5);
            }
        ]);

        return $posts;
    }

    public function render()
    {
        return view('livewire.eager-loading-example');
    }
}
```

```blade
<div>
    {{-- Efficient rendering with eager-loaded data --}}
    @foreach($this->posts as $post)
        <article>
            <h3>{{ $post->title }}</h3>
            <p>By {{ $post->author->name }}</p>
            <span>{{ $post->comments_count }} comments</span>

            @if($showComments)
                <div class="comments">
                    @foreach($post->comments as $comment)
                        <div>
                            {{ $comment->author->name }}: {{ $comment->content }}
                        </div>
                    @endforeach
                </div>
            @endif
        </article>
    @endforeach
</div>
```

### Pattern 2: Computed Properties for Query Caching

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use App\Models\User;
use App\Models\Order;
use Illuminate\Support\Facades\DB;

class ComputedCaching extends Component
{
    public $userId;
    public $dateRange = 'month';

    /**
     * Computed property caches query results.
     * Only re-runs when $userId changes.
     */
    #[Computed]
    public function user()
    {
        return User::with('profile')->findOrFail($this->userId);
    }

    /**
     * Depends on user() computed property.
     * Cached until $userId changes.
     */
    #[Computed]
    public function orders()
    {
        return $this->user->orders()
            ->with('items.product')
            ->latest()
            ->limit(10)
            ->get();
    }

    /**
     * Complex calculation cached in computed property.
     * Re-calculates only when $userId or $dateRange changes.
     */
    #[Computed]
    public function statistics()
    {
        $startDate = match($this->dateRange) {
            'week' => now()->subWeek(),
            'month' => now()->subMonth(),
            'year' => now()->subYear(),
            default => now()->subMonth(),
        };

        return [
            'total_orders' => $this->user->orders()
                ->where('created_at', '>=', $startDate)
                ->count(),

            'total_spent' => $this->user->orders()
                ->where('created_at', '>=', $startDate)
                ->sum('total'),

            'average_order' => $this->user->orders()
                ->where('created_at', '>=', $startDate)
                ->avg('total'),

            'top_products' => DB::table('order_items')
                ->join('orders', 'order_items.order_id', '=', 'orders.id')
                ->join('products', 'order_items.product_id', '=', 'products.id')
                ->where('orders.user_id', $this->userId)
                ->where('orders.created_at', '>=', $startDate)
                ->select('products.name', DB::raw('SUM(order_items.quantity) as total'))
                ->groupBy('products.id', 'products.name')
                ->orderBy('total', 'desc')
                ->limit(5)
                ->get(),
        ];
    }

    /**
     * Manual cache invalidation if needed.
     */
    public function refreshStats()
    {
        unset($this->statistics); // Clear computed cache
    }

    /**
     * BAD: Query runs on every render
     */
    public function badRender()
    {
        return view('livewire.dashboard', [
            'user' => User::find($this->userId), // Runs every render
            'stats' => $this->calculateStats(), // Runs every render
        ]);
    }

    /**
     * GOOD: Use cached computed properties
     */
    public function render()
    {
        return view('livewire.computed-caching');
    }
}
```

```blade
<div>
    <h2>{{ $this->user->name }}</h2>

    <select wire:model.live="dateRange">
        <option value="week">Last Week</option>
        <option value="month">Last Month</option>
        <option value="year">Last Year</option>
    </select>

    <div class="stats">
        <div class="stat-card">
            <h3>Total Orders</h3>
            <p>{{ $this->statistics['total_orders'] }}</p>
        </div>
        <div class="stat-card">
            <h3>Total Spent</h3>
            <p>${{ number_format($this->statistics['total_spent'], 2) }}</p>
        </div>
        <div class="stat-card">
            <h3>Average Order</h3>
            <p>${{ number_format($this->statistics['average_order'], 2) }}</p>
        </div>
    </div>

    <h3>Recent Orders</h3>
    @foreach($this->orders as $order)
        <div>Order #{{ $order->id }} - ${{ $order->total }}</div>
    @endforeach

    <button wire:click="refreshStats">Refresh</button>
</div>
```

### Pattern 3: Pagination and Chunking

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithPagination;
use Livewire\Attributes\Computed;
use App\Models\Product;

class OptimizedPagination extends Component
{
    use WithPagination;

    public $search = '';
    public $perPage = 20;
    public $sortBy = 'created_at';
    public $sortDirection = 'desc';

    /**
     * Optimized pagination with computed property.
     */
    #[Computed]
    public function products()
    {
        return Product::query()
            ->select('id', 'name', 'price', 'category_id', 'created_at')
            ->with('category:id,name')
            ->when($this->search, function ($query) {
                $query->where('name', 'like', "%{$this->search}%")
                      ->orWhere('description', 'like', "%{$this->search}%");
            })
            ->orderBy($this->sortBy, $this->sortDirection)
            ->paginate($this->perPage);
    }

    /**
     * Reset pagination when search changes.
     */
    public function updatingSearch()
    {
        $this->resetPage();
    }

    /**
     * Change items per page.
     */
    public function updatedPerPage()
    {
        $this->resetPage();
    }

    /**
     * Sort by column.
     */
    public function sortBy($field)
    {
        if ($this->sortBy === $field) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortBy = $field;
            $this->sortDirection = 'asc';
        }
    }

    public function render()
    {
        return view('livewire.optimized-pagination');
    }
}

class InfiniteScroll extends Component
{
    public $page = 1;
    public $perPage = 20;

    #[Computed]
    public function products()
    {
        return Product::query()
            ->select('id', 'name', 'price')
            ->latest()
            ->paginate($this->perPage, ['*'], 'page', $this->page);
    }

    public function loadMore()
    {
        $this->page++;
    }

    public function render()
    {
        return view('livewire.infinite-scroll');
    }
}

class ChunkedProcessing extends Component
{
    public $processing = false;
    public $progress = 0;
    public $total = 0;

    /**
     * Process large dataset in chunks.
     */
    public function processLargeDataset()
    {
        $this->processing = true;
        $this->total = Product::count();
        $processed = 0;

        Product::chunk(100, function ($products) use (&$processed) {
            foreach ($products as $product) {
                // Process product
                $product->update(['processed' => true]);
                $processed++;
            }

            $this->progress = ($processed / $this->total) * 100;
        });

        $this->processing = false;
        session()->flash('message', 'Processing complete!');
    }

    public function render()
    {
        return view('livewire.chunked-processing');
    }
}
```

```blade
{{-- optimized-pagination.blade.php --}}
<div>
    <input
        type="text"
        wire:model.live.debounce.500ms="search"
        placeholder="Search products..."
    >

    <select wire:model.live="perPage">
        <option value="10">10 per page</option>
        <option value="20">20 per page</option>
        <option value="50">50 per page</option>
        <option value="100">100 per page</option>
    </select>

    <table>
        <thead>
            <tr>
                <th wire:click="sortBy('name')" style="cursor: pointer">
                    Name
                    @if($sortBy === 'name')
                        {{ $sortDirection === 'asc' ? '↑' : '↓' }}
                    @endif
                </th>
                <th wire:click="sortBy('price')" style="cursor: pointer">
                    Price
                    @if($sortBy === 'price')
                        {{ $sortDirection === 'asc' ? '↑' : '↓' }}
                    @endif
                </th>
                <th>Category</th>
            </tr>
        </thead>
        <tbody>
            @foreach($this->products as $product)
                <tr>
                    <td>{{ $product->name }}</td>
                    <td>${{ $product->price }}</td>
                    <td>{{ $product->category->name }}</td>
                </tr>
            @endforeach
        </tbody>
    </table>

    {{ $this->products->links() }}
</div>

{{-- infinite-scroll.blade.php --}}
<div>
    <div class="products-grid">
        @foreach($this->products as $product)
            <div class="product-card">
                <h3>{{ $product->name }}</h3>
                <p>${{ $product->price }}</p>
            </div>
        @endforeach
    </div>

    @if($this->products->hasMorePages())
        <div
            x-data
            x-intersect="$wire.loadMore()"
            class="loading-trigger"
        >
            <span wire:loading wire:target="loadMore">Loading more...</span>
        </div>
    @endif
</div>
```

### Pattern 4: Lazy Loading Components

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Lazy;

/**
 * Lazy loaded component - only rendered when visible.
 */
#[Lazy]
class HeavyComponent extends Component
{
    public function placeholder()
    {
        return view('livewire.placeholders.loading');
    }

    public function render()
    {
        // Simulate expensive operation
        sleep(2);

        $data = $this->loadExpensiveData();

        return view('livewire.heavy-component', ['data' => $data]);
    }

    private function loadExpensiveData()
    {
        // Complex queries or calculations
        return [];
    }
}

class Dashboard extends Component
{
    public $showStatistics = false;
    public $showReports = false;

    /**
     * Conditionally load heavy components.
     */
    public function loadStatistics()
    {
        $this->showStatistics = true;
    }

    public function loadReports()
    {
        $this->showReports = true;
    }

    public function render()
    {
        return view('livewire.dashboard');
    }
}
```

```blade
{{-- dashboard.blade.php --}}
<div>
    <h1>Dashboard</h1>

    {{-- Lazy load heavy component --}}
    @if($showStatistics)
        <livewire:statistics-component lazy />
    @else
        <button wire:click="loadStatistics">Load Statistics</button>
    @endif

    {{-- Load component on scroll --}}
    <div x-data x-intersect="$wire.showReports = true">
        @if($showReports)
            <livewire:reports-component lazy />
        @endif
    </div>

    {{-- Multiple lazy components --}}
    <div class="widgets">
        <livewire:widget-sales lazy />
        <livewire:widget-users lazy />
        <livewire:widget-orders lazy />
    </div>
</div>

{{-- placeholders/loading.blade.php --}}
<div class="placeholder">
    <div class="skeleton-loader">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
    </div>
    <p>Loading...</p>
</div>
```

### Pattern 5: Optimized Polling

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use App\Models\Notification;

class OptimizedPolling extends Component
{
    public $isPolling = true;
    public $pollInterval = 5000; // milliseconds

    /**
     * Only query for new notifications.
     * Use timestamp to track last check.
     */
    public $lastChecked;

    public function mount()
    {
        $this->lastChecked = now();
    }

    /**
     * Efficient polling - only fetch new data.
     */
    #[Computed]
    public function notifications()
    {
        return Notification::where('user_id', auth()->id())
            ->where('created_at', '>', $this->lastChecked)
            ->latest()
            ->get();
    }

    /**
     * Poll for updates.
     */
    public function checkForUpdates()
    {
        $newNotifications = $this->notifications;

        if ($newNotifications->isNotEmpty()) {
            $this->lastChecked = now();
            $this->dispatch('new-notifications', count: $newNotifications->count());
        }
    }

    /**
     * Toggle polling on/off.
     */
    public function togglePolling()
    {
        $this->isPolling = !$this->isPolling;
    }

    /**
     * Dynamic polling interval based on activity.
     */
    public function adjustPollInterval()
    {
        // Slow down polling if no activity
        if ($this->notifications->isEmpty()) {
            $this->pollInterval = min($this->pollInterval * 1.5, 30000); // Max 30s
        } else {
            $this->pollInterval = 5000; // Reset to 5s
        }
    }

    public function render()
    {
        return view('livewire.optimized-polling');
    }
}

class SmartPolling extends Component
{
    public $activePolling = true;

    /**
     * Only poll when browser tab is active.
     */
    public function mount()
    {
        $this->loadData();
    }

    public function loadData()
    {
        if (!$this->activePolling) {
            return;
        }

        // Load fresh data
        $this->dispatch('data-updated');
    }

    public function render()
    {
        return view('livewire.smart-polling');
    }
}
```

```blade
{{-- optimized-polling.blade.php --}}
<div
    x-data="{
        polling: @entangle('isPolling'),
        interval: @entangle('pollInterval'),
    }"
    x-init="
        setInterval(() => {
            if (polling && !document.hidden) {
                $wire.checkForUpdates()
            }
        }, interval)
    "
>
    <button wire:click="togglePolling">
        {{ $isPolling ? 'Stop' : 'Start' }} Polling
    </button>

    <div class="notifications">
        @forelse($this->notifications as $notification)
            <div>{{ $notification->message }}</div>
        @empty
            <p>No new notifications</p>
        @endforelse
    </div>
</div>

{{-- smart-polling.blade.php --}}
<div
    x-data="{ isVisible: true }"
    x-init="
        document.addEventListener('visibilitychange', () => {
            isVisible = !document.hidden;
            $wire.activePolling = isVisible;
        });
    "
    wire:poll.5s.visible="loadData"
>
    {{-- Content that polls only when visible --}}
</div>
```

### Pattern 6: Wire:Navigate for SPA Performance

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Layout;
use Livewire\Attributes\Title;

#[Layout('layouts.app')]
#[Title('Products')]
class Products extends Component
{
    public function render()
    {
        $products = \App\Models\Product::paginate(20);
        return view('livewire.products', compact('products'));
    }
}

#[Layout('layouts.app')]
#[Title('Product Details')]
class ProductShow extends Component
{
    public $product;

    public function mount($id)
    {
        $this->product = \App\Models\Product::with('reviews')
            ->findOrFail($id);
    }

    public function render()
    {
        return view('livewire.product-show');
    }
}
```

```blade
{{-- layouts/app.blade.php --}}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title ?? 'App' }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body>
    <nav>
        <a href="/" wire:navigate>Home</a>
        <a href="/products" wire:navigate>Products</a>
        <a href="/about" wire:navigate>About</a>

        {{-- Prefetch on hover --}}
        <a href="/dashboard" wire:navigate.hover>Dashboard</a>
    </nav>

    <main>
        {{ $slot }}
    </main>

    {{-- Progress bar for navigation --}}
    <div
        x-data="{ show: false }"
        x-on:livewire:navigate.start="show = true"
        x-on:livewire:navigate.end="show = false"
        x-show="show"
        class="progress-bar"
    ></div>
</body>
</html>

{{-- products.blade.php --}}
<div>
    <h1>Products</h1>

    <div class="products-grid">
        @foreach($products as $product)
            <div class="product-card">
                <h3>{{ $product->name }}</h3>
                <p>${{ $product->price }}</p>

                {{-- Use wire:navigate for instant navigation --}}
                <a href="/products/{{ $product->id }}" wire:navigate>
                    View Details
                </a>
            </div>
        @endforeach
    </div>

    {{ $products->links() }}
</div>

{{-- product-show.blade.php --}}
<div>
    <a href="/products" wire:navigate>← Back to Products</a>

    <h1>{{ $product->name }}</h1>
    <p>${{ $product->price }}</p>

    <div class="reviews">
        @foreach($product->reviews as $review)
            <div>{{ $review->content }}</div>
        @endforeach
    </div>
</div>
```

### Pattern 7: Database Query Optimization

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Cache;

class QueryOptimization extends Component
{
    /**
     * BAD: Multiple separate queries
     */
    public function inefficientQueries()
    {
        $totalUsers = \App\Models\User::count();
        $totalPosts = \App\Models\Post::count();
        $totalComments = \App\Models\Comment::count();
        $activeUsers = \App\Models\User::where('active', true)->count();

        // 4 separate queries
        return compact('totalUsers', 'totalPosts', 'totalComments', 'activeUsers');
    }

    /**
     * GOOD: Single optimized query
     */
    #[Computed]
    public function statistics()
    {
        return Cache::remember('dashboard-stats', 3600, function () {
            return DB::select("
                SELECT
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM posts) as total_posts,
                    (SELECT COUNT(*) FROM comments) as total_comments,
                    (SELECT COUNT(*) FROM users WHERE active = 1) as active_users
            ")[0];
        });
    }

    /**
     * BAD: N+1 with aggregates
     */
    public function inefficientAggregates()
    {
        $users = \App\Models\User::all();

        foreach ($users as $user) {
            $user->post_count = $user->posts()->count(); // N queries
            $user->comment_count = $user->comments()->count(); // N queries
        }

        return $users;
    }

    /**
     * GOOD: Eager load counts
     */
    #[Computed]
    public function users()
    {
        return \App\Models\User::withCount(['posts', 'comments'])
            ->get();
    }

    /**
     * BAD: Loading unnecessary data
     */
    public function loadingTooMuchData()
    {
        return \App\Models\Post::with('author', 'comments', 'tags', 'category')
            ->get(); // Loads all columns and relationships
    }

    /**
     * GOOD: Select only needed columns
     */
    #[Computed]
    public function posts()
    {
        return \App\Models\Post::select('id', 'title', 'user_id')
            ->with('author:id,name') // Only author name
            ->withCount('comments') // Just the count
            ->get();
    }

    /**
     * BAD: Repeated queries in loop
     */
    public function repeatedQueries()
    {
        $posts = \App\Models\Post::all();

        foreach ($posts as $post) {
            $category = \App\Models\Category::find($post->category_id); // N queries
            $post->category_name = $category->name;
        }

        return $posts;
    }

    /**
     * GOOD: Join or eager load
     */
    #[Computed]
    public function postsWithCategories()
    {
        return \App\Models\Post::join('categories', 'posts.category_id', '=', 'categories.id')
            ->select('posts.*', 'categories.name as category_name')
            ->get();
    }

    /**
     * Query optimization with indexes
     */
    public function optimizedSearch($term)
    {
        // Ensure indexes exist on searchable columns
        return \App\Models\Post::select('id', 'title', 'created_at')
            ->where('title', 'like', "%{$term}%") // Index on title
            ->orWhere('content', 'like', "%{$term}%") // Index on content
            ->orderBy('created_at', 'desc') // Index on created_at
            ->limit(20)
            ->get();
    }

    public function render()
    {
        return view('livewire.query-optimization');
    }
}
```

### Pattern 8: Caching Strategies

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use Illuminate\Support\Facades\Cache;

class CachingStrategies extends Component
{
    public $category;

    /**
     * Cache expensive query results.
     */
    #[Computed]
    public function products()
    {
        $cacheKey = "products.category.{$this->category}";

        return Cache::remember($cacheKey, 3600, function () {
            return \App\Models\Product::with('category', 'reviews')
                ->where('category_id', $this->category)
                ->get();
        });
    }

    /**
     * Cache with tags for easy invalidation.
     */
    #[Computed]
    public function categorizedProducts()
    {
        return Cache::tags(['products', "category-{$this->category}"])
            ->remember('products-list', 3600, function () {
                return \App\Models\Product::all();
            });
    }

    /**
     * Invalidate cache when data changes.
     */
    public function updateProduct($productId, $data)
    {
        $product = \App\Models\Product::find($productId);
        $product->update($data);

        // Clear related caches
        Cache::forget("products.category.{$product->category_id}");
        Cache::tags(['products', "category-{$product->category_id}"])->flush();

        // Clear computed property cache
        unset($this->products);
    }

    /**
     * Fragment caching in views.
     */
    public function render()
    {
        return view('livewire.caching-strategies');
    }
}
```

```blade
<div>
    {{-- Cache expensive view fragments --}}
    @cache('header-menu', 3600)
        <nav>
            @foreach(\App\Models\Category::all() as $category)
                <a href="/category/{{ $category->slug }}">{{ $category->name }}</a>
            @endforeach
        </nav>
    @endcache

    {{-- Cache with dynamic key --}}
    @cache("products-{$category}", 3600)
        @foreach($this->products as $product)
            <div>{{ $product->name }}</div>
        @endforeach
    @endcache
</div>
```

### Pattern 9: Payload Size Optimization

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use Livewire\Attributes\Locked;

class PayloadOptimization extends Component
{
    /**
     * BAD: Large array in public property
     * This gets serialized and sent to client
     */
    public $allProducts = []; // Don't do this with large datasets

    /**
     * GOOD: Use computed property
     * Data stays on server
     */
    #[Computed]
    public function products()
    {
        return \App\Models\Product::all();
    }

    /**
     * BAD: Unnecessary data in component state
     */
    public $productDetails = []; // Full product data

    /**
     * GOOD: Only store IDs
     */
    public $selectedProductIds = [];

    #[Computed]
    public function selectedProducts()
    {
        return \App\Models\Product::whereIn('id', $this->selectedProductIds)->get();
    }

    /**
     * Use locked properties for IDs that shouldn't change
     */
    #[Locked]
    public $userId;

    /**
     * Minimize public properties
     */
    public $search = ''; // Small, frequently changing
    public $page = 1; // Small integer

    protected $queryString = [
        'search' => ['except' => ''],
        'page' => ['except' => 1],
    ];

    public function render()
    {
        return view('livewire.payload-optimization');
    }
}
```

### Pattern 10: Testing Performance

```php
<?php

namespace Tests\Feature\Livewire;

use App\Livewire\OptimizedPosts;
use App\Models\Post;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Livewire\Livewire;
use Tests\TestCase;

class PerformanceTest extends TestCase
{
    use RefreshDatabase;

    public function test_prevents_n_plus_one_queries()
    {
        $users = User::factory()->count(10)->create();
        $users->each(function ($user) {
            Post::factory()->count(5)->create(['user_id' => $user->id]);
        });

        DB::enableQueryLog();

        $component = Livewire::test(OptimizedPosts::class);

        $queries = DB::getQueryLog();

        // Should be only a few queries, not 50+
        $this->assertLessThan(5, count($queries), 'Too many queries detected');
    }

    public function test_computed_property_caching()
    {
        $component = Livewire::test(OptimizedPosts::class);

        DB::enableQueryLog();

        // Access computed property multiple times
        $posts1 = $component->viewData('posts');
        $posts2 = $component->viewData('posts');
        $posts3 = $component->viewData('posts');

        $queries = DB::getQueryLog();

        // Should only query once due to caching
        $this->assertEquals(1, count($queries), 'Computed property not cached');
    }

    public function test_pagination_performance()
    {
        Post::factory()->count(1000)->create();

        DB::enableQueryLog();

        $component = Livewire::test(OptimizedPosts::class);

        $queries = DB::getQueryLog();

        // Should use LIMIT/OFFSET, not load all 1000
        $this->assertStringContainsString('LIMIT', $queries[0]['query']);
    }

    public function test_component_render_time()
    {
        $start = microtime(true);

        Livewire::test(OptimizedPosts::class);

        $duration = microtime(true) - $start;

        // Component should render in under 100ms
        $this->assertLessThan(0.1, $duration, 'Component renders too slowly');
    }
}
```

## Advanced Patterns

### Pattern 11: Database Connection Pooling

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Illuminate\Support\Facades\DB;

class ConnectionManagement extends Component
{
    /**
     * Use transactions for multiple queries.
     */
    public function saveWithTransaction()
    {
        DB::transaction(function () {
            $user = \App\Models\User::create([...]);
            $user->profile()->create([...]);
            $user->settings()->create([...]);
        });
    }

    /**
     * Use cursor for memory-efficient iteration.
     */
    public function processCursor()
    {
        foreach (\App\Models\User::cursor() as $user) {
            // Process one at a time, low memory usage
            $this->processUser($user);
        }
    }

    /**
     * Close connections when done.
     */
    public function __destruct()
    {
        DB::disconnect();
    }

    public function render()
    {
        return view('livewire.connection-management');
    }
}
```

### Pattern 12: Asset Optimization

```blade
{{-- Defer non-critical JavaScript --}}
@push('scripts')
    <script defer src="/js/charts.js"></script>
@endpush

{{-- Lazy load images --}}
<img
    src="placeholder.jpg"
    data-src="{{ $product->image }}"
    loading="lazy"
    alt="{{ $product->name }}"
>

{{-- Optimize Livewire scripts --}}
@livewireScriptConfig([
    'progressBar' => true,
    'nonce' => csp_nonce(),
])
```

## Real-World Applications

### Application 1: High-Performance Dashboard

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use Livewire\Attributes\Lazy;
use Illuminate\Support\Facades\Cache;

class PerformantDashboard extends Component
{
    #[Computed]
    public function metrics()
    {
        return Cache::remember('dashboard-metrics', 300, function () {
            return [
                'users' => \App\Models\User::count(),
                'revenue' => \App\Models\Order::sum('total'),
                'orders_today' => \App\Models\Order::whereDate('created_at', today())->count(),
            ];
        });
    }

    public function render()
    {
        return view('livewire.performant-dashboard');
    }
}

#[Lazy]
class DashboardChart extends Component
{
    public function placeholder()
    {
        return <<<'HTML'
        <div class="chart-placeholder">Loading chart...</div>
        HTML;
    }

    #[Computed]
    public function chartData()
    {
        return Cache::remember('chart-data', 600, function () {
            return \App\Models\Order::selectRaw('DATE(created_at) as date, SUM(total) as total')
                ->groupBy('date')
                ->orderBy('date')
                ->limit(30)
                ->get();
        });
    }

    public function render()
    {
        return view('livewire.dashboard-chart');
    }
}
```

## Performance Best Practices

### Practice 1: Always Use Eager Loading

```php
// BAD
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name; // N+1 queries
}

// GOOD
$posts = Post::with('author')->all();
foreach ($posts as $post) {
    echo $post->author->name; // 2 queries total
}
```

### Practice 2: Use Computed Properties

```php
// BAD - queries every render
public function render()
{
    return view('livewire.posts', [
        'posts' => Post::all()
    ]);
}

// GOOD - cached in computed property
#[Computed]
public function posts()
{
    return Post::all();
}
```

### Practice 3: Paginate Large Datasets

```php
// BAD - loads everything
$products = Product::all();

// GOOD - paginate
$products = Product::paginate(20);
```

### Practice 4: Use Lazy Loading

```blade
{{-- Load heavy components lazily --}}
<livewire:heavy-widget lazy />
```

### Practice 5: Optimize Polling

```blade
{{-- Only poll when visible --}}
<div wire:poll.5s.visible="refresh"></div>
```

## Common Pitfalls

### Pitfall 1: Not Using Computed Properties

```php
// WRONG
public function render()
{
    $data = $this->expensiveQuery(); // Runs every render
    return view('livewire.component', ['data' => $data]);
}

// CORRECT
#[Computed]
public function data()
{
    return $this->expensiveQuery(); // Cached
}
```

### Pitfall 2: Polling Too Frequently

```blade
{{-- WRONG: Poll every second --}}
<div wire:poll.1s="refresh"></div>

{{-- CORRECT: Poll every 10s or only when visible --}}
<div wire:poll.10s.visible="refresh"></div>
```

### Pitfall 3: Loading Too Much Data

```php
// WRONG
public $allProducts; // Thousands of records

// CORRECT
#[Computed]
public function products()
{
    return Product::paginate(20); // Only 20 at a time
}
```

## Testing

```php
public function test_query_count()
{
    DB::enableQueryLog();

    Livewire::test(OptimizedComponent::class);

    $this->assertLessThan(5, count(DB::getQueryLog()));
}
```

## Resources

- **Laravel Query Optimization**: https://laravel.com/docs/queries
- **Livewire Performance**: https://livewire.laravel.com/docs/performance
- **Laravel Debugbar**: Debug N+1 queries
- **Laravel Telescope**: Monitor performance

## Best Practices Summary

1. **Always eager load** relationships to prevent N+1 queries
2. **Use computed properties** for expensive operations and queries
3. **Paginate large datasets** instead of loading everything
4. **Implement lazy loading** for heavy components
5. **Optimize polling** with longer intervals and visibility checks
6. **Use wire:navigate** for SPA-like performance
7. **Cache expensive queries** with appropriate TTLs
8. **Select only needed columns** from database
9. **Monitor query counts** with Debugbar or Telescope
10. **Test performance** regularly with automated tests
