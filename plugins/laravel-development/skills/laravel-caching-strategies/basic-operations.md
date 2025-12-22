# Basic Cache Operations

Core caching methods in Laravel.

## Store Data

```php
use Illuminate\Support\Facades\Cache;

// Store with TTL (seconds)
Cache::put('user:1', $user, 3600);

// Store with Carbon time
Cache::put('posts', $posts, now()->addHours(1));

// Store forever (until manually removed)
Cache::forever('settings', $settings);

// Store if doesn't exist
Cache::add('key', 'value', 3600); // Returns true if added

// Increment/Decrement
Cache::increment('page_views');
Cache::increment('page_views', 5);
Cache::decrement('stock', 1);
```

## Retrieve Data

```php
// Basic get
$value = Cache::get('key');

// With default
$value = Cache::get('key', 'default');

// With closure for default
$value = Cache::get('key', function () {
    return computeDefault();
});

// Get and delete
$value = Cache::pull('key');

// Check existence
if (Cache::has('key')) {
    // Key exists
}

// Missing check
if (Cache::missing('key')) {
    // Key doesn't exist
}
```

## Remember Pattern

```php
// Most common pattern - get or store
$users = Cache::remember('users', 3600, function () {
    return User::all();
});

// Remember forever
$settings = Cache::rememberForever('settings', function () {
    return Setting::all()->pluck('value', 'key');
});

// Flexible remember
$posts = Cache::flexible('posts', [3600, 7200], function () {
    return Post::published()->get();
});
```

## Remove Data

```php
// Remove single key
Cache::forget('key');

// Remove multiple keys
collect(['key1', 'key2', 'key3'])->each(fn($k) => Cache::forget($k));

// Flush entire cache
Cache::flush();
```

## Atomic Locks

```php
// Prevent race conditions
$lock = Cache::lock('processing', 10);

if ($lock->get()) {
    try {
        // Process...
    } finally {
        $lock->release();
    }
}

// Block until lock is available
Cache::lock('processing', 10)->block(5, function () {
    // Process with exclusive access
});
```

## Multiple Cache Stores

```php
// Use specific store
Cache::store('file')->put('key', 'value', 600);
Cache::store('redis')->get('key');

// Configure multiple stores
// config/cache.php
'stores' => [
    'redis' => ['driver' => 'redis', 'connection' => 'cache'],
    'file' => ['driver' => 'file', 'path' => storage_path('framework/cache')],
],
```
