# Wire Navigate

Livewire 4 SPA-like navigation for instant page transitions.

## Basic Usage

```blade
{{-- Standard navigation with wire:navigate --}}
<nav>
    <a href="/" wire:navigate>Home</a>
    <a href="/dashboard" wire:navigate>Dashboard</a>
    <a href="/products" wire:navigate>Products</a>
    <a href="/about" wire:navigate>About</a>
</nav>
```

## How It Works

```blade
{{-- Without wire:navigate: Full page reload --}}
<a href="/products">Products</a>

{{-- With wire:navigate: --}}
{{-- 1. Intercepts click --}}
{{-- 2. Fetches new page via AJAX --}}
{{-- 3. Morphs DOM instead of full reload --}}
{{-- 4. Updates URL history --}}
<a href="/products" wire:navigate>Products</a>
```

## Prefetching

```blade
{{-- Prefetch on hover (loads in background) --}}
<a href="/dashboard" wire:navigate.hover>Dashboard</a>

{{-- Good for frequently accessed pages --}}
<nav>
    <a href="/" wire:navigate.hover>Home</a>
    <a href="/products" wire:navigate.hover>Products</a>
</nav>

{{-- Combine with regular navigate --}}
<a href="/profile" wire:navigate wire:navigate.hover>
    My Profile
</a>
```

## Progress Indicator

```blade
<!DOCTYPE html>
<html>
<head>
    <style>
        .progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: #3b82f6;
            z-index: 9999;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    {{-- Progress bar during navigation --}}
    <div
        x-data="{ show: false, progress: 0 }"
        x-on:livewire:navigate-start.window="show = true; progress = 0"
        x-on:livewire:navigate-end.window="progress = 100; setTimeout(() => show = false, 300)"
        x-show="show"
        class="progress-bar"
        :style="'width: ' + progress + '%'"
    ></div>

    <main>
        {{ $slot }}
    </main>
</body>
</html>
```

## Persistent Layouts

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Layout;
use Livewire\Attributes\Title;

#[Layout('layouts.app')]
#[Title('Dashboard')]
class Dashboard extends Component
{
    public function render()
    {
        return view('livewire.dashboard');
    }
}

#[Layout('layouts.app')]
#[Title('Products')]
class Products extends Component
{
    public function render()
    {
        return view('livewire.products');
    }
}
```

```blade
{{-- layouts/app.blade.php --}}
<!DOCTYPE html>
<html>
<head>
    <title>{{ $title ?? 'App' }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body>
    {{-- This layout persists across wire:navigate --}}
    <nav>
        <a href="/" wire:navigate>Home</a>
        <a href="/dashboard" wire:navigate>Dashboard</a>
    </nav>

    <main>
        {{ $slot }}
    </main>

    {{-- Scripts and Alpine state persist --}}
</body>
</html>
```

## Navigation Events

```blade
<div
    x-data
    x-on:livewire:navigating.window="console.log('Navigation starting...')"
    x-on:livewire:navigated.window="console.log('Navigation complete!')"
>
    {{-- Content --}}
</div>

<script>
document.addEventListener('livewire:navigating', () => {
    // Save scroll position
    // Show loading state
    // Cancel pending requests
});

document.addEventListener('livewire:navigated', () => {
    // Restore scroll position
    // Hide loading state
    // Initialize third-party scripts
});
</script>
```

## Preserving Scroll Position

```blade
{{-- By default, scroll resets to top --}}
<a href="/page-2" wire:navigate>Next Page</a>

{{-- Preserve scroll position --}}
<script>
let scrollPositions = {};

document.addEventListener('livewire:navigating', () => {
    scrollPositions[window.location.href] = window.scrollY;
});

document.addEventListener('livewire:navigated', () => {
    const savedPosition = scrollPositions[window.location.href];
    if (savedPosition !== undefined) {
        window.scrollTo(0, savedPosition);
    }
});
</script>
```

## Form Navigation

```blade
{{-- Navigate after form submission --}}
<form wire:submit="save">
    <input wire:model="title">
    <button type="submit">Save</button>
</form>

{{-- In component --}}
public function save()
{
    $post = Post::create([...]);

    // Redirect with wire:navigate behavior
    return $this->redirect(route('posts.show', $post), navigate: true);
}
```

## Conditional Navigation

```blade
{{-- Only use wire:navigate for internal links --}}
@if(Str::startsWith($url, config('app.url')))
    <a href="{{ $url }}" wire:navigate>{{ $text }}</a>
@else
    <a href="{{ $url }}" target="_blank">{{ $text }}</a>
@endif

{{-- Disable for downloads or external links --}}
<a href="/download/file.pdf">Download PDF</a>  {{-- No wire:navigate --}}
<a href="https://external.com">External</a>     {{-- No wire:navigate --}}
```

## Handling Third-Party Scripts

```blade
<script>
// Re-initialize scripts after navigation
document.addEventListener('livewire:navigated', () => {
    // Re-init analytics
    if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_ID', { page_path: window.location.pathname });
    }

    // Re-init other libraries
    initializeCharts();
    initializeTooltips();
});
</script>
```

## Route-Based Full Page Components

```php
// routes/web.php
use App\Livewire\Dashboard;
use App\Livewire\Products;
use App\Livewire\ProductShow;

Route::get('/', Dashboard::class);
Route::get('/products', Products::class);
Route::get('/products/{product}', ProductShow::class);
```

```php
// Full page component
class ProductShow extends Component
{
    public Product $product;

    public function mount(Product $product)
    {
        $this->product = $product;
    }

    public function render()
    {
        return view('livewire.product-show');
    }
}
```

## Performance Benefits

```
Without wire:navigate:
1. Click link
2. Browser requests full HTML page
3. Browser parses entire HTML
4. Browser downloads all CSS/JS again
5. Browser re-renders entire page
6. JavaScript re-initializes

With wire:navigate:
1. Click link
2. Livewire fetches just the new content
3. Livewire morphs only changed DOM
4. CSS/JS already loaded (cached)
5. Alpine state preserved
6. Much faster transition
```

## Best Practices

```blade
{{-- 1. Use for all internal navigation --}}
<a href="/dashboard" wire:navigate>Dashboard</a>

{{-- 2. Prefetch important pages --}}
<a href="/settings" wire:navigate.hover>Settings</a>

{{-- 3. Don't use for:
     - External links
     - File downloads
     - Pages that need full reload
--}}
<a href="/export/csv">Download CSV</a>
<a href="https://external.com" target="_blank">External</a>

{{-- 4. Handle navigation events for analytics --}}
<script>
document.addEventListener('livewire:navigated', () => {
    trackPageView(window.location.pathname);
});
</script>

{{-- 5. Show loading state during navigation --}}
<div wire:loading.delay class="loading-indicator">
    Loading...
</div>
```
