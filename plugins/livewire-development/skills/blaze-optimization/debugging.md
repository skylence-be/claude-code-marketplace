# Debugging & Profiling

Blaze includes a debug mode with an overlay and flame chart profiler for measuring rendering performance and comparing Blaze against standard Blade.

## Enabling Debug Mode

### From Service Provider

```php
use Livewire\Blaze\Blaze;

public function boot(): void
{
    Blaze::debug();

    // ...
}
```

### From Environment

```env
BLAZE_DEBUG=true
```

After enabling, clear compiled views:

```bash
php artisan view:clear
```

## The Debug Overlay

When active, a small overlay appears on every page showing the rendering time for the current request.

### Comparing Blaze vs Blade

Record baseline times by toggling Blaze on/off:

1. Set `BLAZE_ENABLED=false` in `.env`
2. Run `php artisan view:clear`
3. Visit the page — overlay records Blade rendering time
4. Remove `BLAZE_ENABLED=false` (or set to `true`)
5. Run `php artisan view:clear`
6. Visit same page — overlay shows Blaze time alongside Blade baseline with the difference

Refresh a few times in each mode to get accurate results — first load includes compilation overhead.

## The Profiler

The overlay includes an **Open Profiler** button that opens a flame chart trace.

### Workflow

1. Open the profiler window (can stay open)
2. Navigate to the page you want to profile
3. Refresh the profiler window — loads trace for that page

### What It Shows

- Every component rendered during the request
- Duration of each component render
- Nesting depth
- Which strategy was used: **compiled**, **folded**, **memoized**, or **blade**

### Requirements

The profiler stores trace data in your default cache store. It will not work if:

- `CACHE_STORE=array` (array cache doesn't persist between requests)
- Cache is otherwise unreachable

Use `file`, `redis`, `database`, or `memcached` cache driver for profiling.

## Debugging Folding Issues

### Throw Exceptions Instead of Falling Back

By default, when folding fails, Blaze silently falls back to function compilation. Enable exception throwing to catch issues:

```php
Blaze::throw();
```

This helps identify:
- Components accessing global state
- Dynamic props used in internal logic
- Misconfigured `safe`/`unsafe` boundaries

### Common Folding Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Component always shows default value | Dynamic prop used in `match()`/`if` | Remove `fold: true` or restructure |
| Stale auth/session data | Global state baked in at compile time | Remove `fold: true` |
| `@aware` values not propagating | Parent or child not using Blaze | Ensure both use Blaze |
| Component works in some places, not others | Folding with different dynamic props per usage | Check `safe`/`unsafe` config |

### Verifying a Component is Blazed

With debug mode on, the profiler shows which strategy each component uses. Look for:

- **compiled** — function compilation (default)
- **folded** — compile-time folding active
- **memoized** — runtime memoization active
- **blade** — standard Blade (not optimized by Blaze)

## Configuration Reference

### Methods

```php
Blaze::enable();    // Enable Blaze compilation
Blaze::debug();     // Enable debug bar and profiler
Blaze::throw();     // Throw exceptions during folding instead of fallback
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLAZE_ENABLED` | `true` | Enable or disable Blaze compilation |
| `BLAZE_DEBUG` | `false` | Enable debug mode |

### Config File

Publish with:

```bash
php artisan vendor:publish --tag=blaze-config
```

```php
// config/blaze.php
return [
    'enabled' => env('BLAZE_ENABLED', true),
    'debug' => env('BLAZE_DEBUG', false),
];
```

## Performance Testing Workflow

1. Enable debug mode
2. Disable Blaze (`BLAZE_ENABLED=false`) + `view:clear`
3. Visit target page 3-5 times, note Blade baseline
4. Enable Blaze + `view:clear`
5. Visit same page 3-5 times, note Blaze time
6. Open profiler for component-level breakdown
7. Identify slowest components
8. Apply `memo: true` to repeated slot-less components
9. Apply `fold: true` to safe static components
10. Re-measure to verify improvements
