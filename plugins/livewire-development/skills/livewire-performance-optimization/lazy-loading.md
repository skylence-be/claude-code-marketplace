# Lazy Loading

Livewire 4 lazy component loading for improved performance.

## Basic Lazy Loading

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Lazy;

/**
 * Lazy loaded component - only rendered when visible.
 * Shows placeholder until component is ready.
 */
#[Lazy]
class HeavyComponent extends Component
{
    /**
     * Placeholder shown while component loads.
     */
    public function placeholder()
    {
        return view('livewire.placeholders.loading');
    }

    public function render()
    {
        // Expensive operation
        $data = $this->loadExpensiveData();

        return view('livewire.heavy-component', ['data' => $data]);
    }

    private function loadExpensiveData()
    {
        // Complex queries or API calls
        sleep(2); // Simulate delay
        return [];
    }
}
```

```blade
{{-- Using lazy component --}}
<livewire:heavy-component lazy />

{{-- Or with the attribute on the class --}}
<livewire:heavy-component />
```

## Placeholder Templates

```blade
{{-- resources/views/livewire/placeholders/loading.blade.php --}}
<div class="placeholder">
    <div class="skeleton-loader">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
    </div>
    <p class="text-gray-400">Loading...</p>
</div>

{{-- Inline placeholder with Tailwind --}}
public function placeholder()
{
    return <<<'HTML'
    <div class="animate-pulse space-y-4">
        <div class="h-4 bg-gray-200 rounded w-3/4"></div>
        <div class="h-4 bg-gray-200 rounded"></div>
        <div class="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
    HTML;
}
```

## Conditional Lazy Loading

```php
class Dashboard extends Component
{
    public $showStatistics = false;
    public $showReports = false;

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
<div>
    <h1>Dashboard</h1>

    {{-- Load on button click --}}
    @if($showStatistics)
        <livewire:statistics-widget lazy />
    @else
        <button wire:click="loadStatistics">
            Load Statistics
        </button>
    @endif

    {{-- Load on scroll into view --}}
    <div x-data x-intersect="$wire.showReports = true">
        @if($showReports)
            <livewire:reports-widget lazy />
        @else
            <div class="placeholder">Reports will load when scrolled into view</div>
        @endif
    </div>
</div>
```

## Multiple Lazy Components

```blade
<div class="widgets-grid">
    {{-- All load independently and in parallel --}}
    <livewire:widget-sales lazy />
    <livewire:widget-users lazy />
    <livewire:widget-orders lazy />
    <livewire:widget-revenue lazy />
</div>
```

## Lazy Loading with Props

```php
#[Lazy]
class UserCard extends Component
{
    public $userId;

    public function mount($userId)
    {
        $this->userId = $userId;
    }

    public function placeholder()
    {
        return view('livewire.placeholders.user-card');
    }

    public function render()
    {
        $user = User::with('profile', 'stats')->find($this->userId);
        return view('livewire.user-card', ['user' => $user]);
    }
}
```

```blade
{{-- Props work normally with lazy --}}
<livewire:user-card :userId="$userId" lazy />

{{-- Can also use key for re-rendering --}}
<livewire:user-card :userId="$userId" :key="$userId" lazy />
```

## Progressive Loading Pattern

```php
class ProductCatalog extends Component
{
    public $initialLoad = true;
    public $loadedSections = [];

    public function mount()
    {
        // Load critical content first
        $this->loadedSections[] = 'featured';
    }

    public function loadSection($section)
    {
        $this->loadedSections[] = $section;
    }

    public function render()
    {
        return view('livewire.product-catalog');
    }
}
```

```blade
<div>
    {{-- Always loaded --}}
    <livewire:featured-products />

    {{-- Load on scroll --}}
    <div x-data x-intersect.once="$wire.loadSection('categories')">
        @if(in_array('categories', $loadedSections))
            <livewire:category-browser lazy />
        @else
            <div class="placeholder">Categories loading...</div>
        @endif
    </div>

    {{-- Load further down --}}
    <div x-data x-intersect.once="$wire.loadSection('reviews')">
        @if(in_array('reviews', $loadedSections))
            <livewire:recent-reviews lazy />
        @endif
    </div>
</div>
```

## Lazy with Alpine Intersection

```blade
<div>
    {{-- Load when scrolled 200px before visible --}}
    <div
        x-data="{ loaded: false }"
        x-intersect:enter.margin.-200px="loaded = true"
    >
        <template x-if="loaded">
            <livewire:heavy-widget lazy />
        </template>
        <template x-if="!loaded">
            <div class="placeholder">
                <p>Scroll down to load</p>
            </div>
        </template>
    </div>
</div>
```

## Loading States During Lazy Load

```blade
<div>
    {{-- Wrap lazy component with loading indicator --}}
    <div
        x-data="{ loading: true }"
        x-on:livewire:navigated.window="loading = false"
    >
        <livewire:dashboard-chart lazy />

        <div x-show="loading" class="loading-overlay">
            <svg class="spinner" ...></svg>
        </div>
    </div>
</div>
```

## Comparing Loading Strategies

```php
/**
 * Strategy 1: Eager (default)
 * - Component loads immediately with page
 * - Good for: Above-fold content, critical components
 */
<livewire:critical-content />

/**
 * Strategy 2: Lazy
 * - Component loads after initial page render
 * - Good for: Heavy components, below-fold content
 */
<livewire:heavy-widget lazy />

/**
 * Strategy 3: Conditional
 * - Component only loads when condition met
 * - Good for: Optional features, user-triggered content
 */
@if($showWidget)
    <livewire:optional-widget />
@endif

/**
 * Strategy 4: Intersection (manual)
 * - Component loads when scrolled into view
 * - Good for: Long pages, infinite scroll
 */
<div x-intersect="$wire.loadComponent()">
    @if($componentLoaded)
        <livewire:scroll-loaded-widget />
    @endif
</div>
```

## Performance Tips

```php
/**
 * 1. Use lazy for heavy components below the fold
 */
#[Lazy]
class HeavyAnalytics extends Component { }

/**
 * 2. Combine with computed properties
 */
#[Lazy]
class DataHeavyComponent extends Component
{
    #[Computed]
    public function data()
    {
        return $this->expensiveQuery();
    }
}

/**
 * 3. Use meaningful placeholders
 */
public function placeholder()
{
    return view('placeholders.analytics', [
        'title' => $this->title // Can pass props to placeholder
    ]);
}

/**
 * 4. Consider skeleton loaders over spinners
 */
public function placeholder()
{
    return <<<'HTML'
    <div class="animate-pulse">
        <div class="h-8 bg-gray-200 rounded mb-4"></div>
        <div class="h-32 bg-gray-200 rounded"></div>
    </div>
    HTML;
}
```
