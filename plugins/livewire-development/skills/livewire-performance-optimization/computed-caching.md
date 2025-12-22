# Computed Caching

Livewire 4 #[Computed] attribute for caching expensive operations.

## Basic Computed Properties

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use App\Models\User;

class ComputedExample extends Component
{
    public $userId;

    /**
     * Computed property caches query results.
     * Only re-runs when component re-renders or manually cleared.
     */
    #[Computed]
    public function user()
    {
        return User::with('profile')->findOrFail($this->userId);
    }

    /**
     * Computed properties can depend on other computed properties.
     */
    #[Computed]
    public function posts()
    {
        return $this->user->posts()->latest()->limit(10)->get();
    }

    /**
     * Complex calculations cached.
     */
    #[Computed]
    public function statistics()
    {
        return [
            'total_posts' => $this->user->posts()->count(),
            'total_likes' => $this->posts->sum('likes_count'),
            'avg_comments' => $this->posts->avg('comments_count'),
        ];
    }
}
```

```blade
<div>
    {{-- Access via $this->propertyName --}}
    <h2>{{ $this->user->name }}</h2>

    <div class="stats">
        <span>Posts: {{ $this->statistics['total_posts'] }}</span>
        <span>Likes: {{ $this->statistics['total_likes'] }}</span>
    </div>

    @foreach($this->posts as $post)
        <article>{{ $post->title }}</article>
    @endforeach
</div>
```

## Cache Invalidation

```php
class CacheInvalidation extends Component
{
    public $userId;
    public $dateRange = 'month';

    #[Computed]
    public function user()
    {
        return User::findOrFail($this->userId);
    }

    #[Computed]
    public function orders()
    {
        $startDate = match($this->dateRange) {
            'week' => now()->subWeek(),
            'month' => now()->subMonth(),
            'year' => now()->subYear(),
            default => now()->subMonth(),
        };

        return $this->user->orders()
            ->where('created_at', '>=', $startDate)
            ->get();
    }

    /**
     * Manual cache invalidation.
     */
    public function refreshData()
    {
        unset($this->user);   // Clear user cache
        unset($this->orders); // Clear orders cache
    }

    /**
     * Cache clears automatically when properties change.
     */
    public function updatedDateRange()
    {
        // Computed properties that depend on $dateRange
        // will automatically re-compute on next access
    }
}
```

## Computed vs Regular Methods

```php
class ComputedVsMethod extends Component
{
    public $search = '';

    /**
     * BAD: Regular method runs every time it's called in view.
     * If called 3 times in blade, runs 3 times.
     */
    public function getProducts()
    {
        return Product::where('name', 'like', "%{$this->search}%")->get();
    }

    /**
     * GOOD: Computed property runs once, cached for entire render.
     */
    #[Computed]
    public function products()
    {
        return Product::where('name', 'like', "%{$this->search}%")->get();
    }
}
```

```blade
{{-- With regular method: 3 queries --}}
Count: {{ $this->getProducts()->count() }}
First: {{ $this->getProducts()->first()->name }}
@foreach($this->getProducts() as $product)

{{-- With computed: 1 query, cached --}}
Count: {{ $this->products->count() }}
First: {{ $this->products->first()->name }}
@foreach($this->products as $product)
```

## Computed with Dependencies

```php
class ComputedDependencies extends Component
{
    public $category = 'all';
    public $sortBy = 'name';
    public $perPage = 20;

    /**
     * This computed property depends on multiple reactive properties.
     * Re-computes when any dependency changes.
     */
    #[Computed]
    public function products()
    {
        return Product::query()
            ->when($this->category !== 'all', fn($q) => $q->where('category', $this->category))
            ->orderBy($this->sortBy)
            ->paginate($this->perPage);
    }

    /**
     * Dependent computed property.
     */
    #[Computed]
    public function totalValue()
    {
        return $this->products->sum('price');
    }
}
```

## Computed for Aggregations

```php
class DashboardStats extends Component
{
    /**
     * Cache expensive aggregate queries.
     */
    #[Computed]
    public function metrics()
    {
        return [
            'users' => User::count(),
            'posts' => Post::count(),
            'comments' => Comment::count(),
            'revenue' => Order::sum('total'),
        ];
    }

    /**
     * Cache chart data.
     */
    #[Computed]
    public function chartData()
    {
        return Order::selectRaw('DATE(created_at) as date, SUM(total) as total')
            ->groupBy('date')
            ->orderBy('date')
            ->limit(30)
            ->get()
            ->map(fn($row) => [
                'date' => $row->date,
                'total' => $row->total,
            ]);
    }
}
```

## Computed with External Cache

```php
use Illuminate\Support\Facades\Cache;

class CombinedCaching extends Component
{
    public $userId;

    /**
     * Combine Livewire computed with Laravel cache.
     */
    #[Computed]
    public function user()
    {
        return Cache::remember("user.{$this->userId}", 3600, function () {
            return User::with(['profile', 'settings'])->findOrFail($this->userId);
        });
    }

    /**
     * Clear both caches when needed.
     */
    public function refreshUser()
    {
        Cache::forget("user.{$this->userId}");
        unset($this->user);
    }
}
```

## Computed Property Patterns

```php
class ComputedPatterns extends Component
{
    public $filters = [];

    /**
     * Pattern: Filtered list
     */
    #[Computed]
    public function filteredItems()
    {
        $query = Item::query();

        foreach ($this->filters as $key => $value) {
            if ($value) {
                $query->where($key, $value);
            }
        }

        return $query->get();
    }

    /**
     * Pattern: Derived state
     */
    #[Computed]
    public function hasItems()
    {
        return $this->filteredItems->isNotEmpty();
    }

    /**
     * Pattern: Formatted data
     */
    #[Computed]
    public function formattedTotal()
    {
        return '$' . number_format($this->filteredItems->sum('price'), 2);
    }

    /**
     * Pattern: Grouped data
     */
    #[Computed]
    public function itemsByCategory()
    {
        return $this->filteredItems->groupBy('category');
    }
}
```

## Performance Comparison

```php
class PerformanceComparison extends Component
{
    /**
     * Scenario: Display user dashboard
     *
     * Without computed (BAD):
     * - render() queries user
     * - View calls $this->getUser() 5 times = 5 queries
     * - Total: 5 queries per render
     *
     * With computed (GOOD):
     * - View calls $this->user 5 times = 1 query (cached)
     * - Total: 1 query per render
     */

    // BAD
    public function getUser()
    {
        return User::find($this->userId);
    }

    // GOOD
    #[Computed]
    public function user()
    {
        return User::find($this->userId);
    }
}
```
