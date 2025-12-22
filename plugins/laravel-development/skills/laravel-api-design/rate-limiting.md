# API Rate Limiting

Throttling and protection for APIs.

## Configure Rate Limiters

```php
<?php

// app/Providers/RouteServiceProvider.php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Support\Facades\RateLimiter;

public function boot(): void
{
    // Default API limit
    RateLimiter::for('api', function (Request $request) {
        return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
    });

    // Custom limit for uploads
    RateLimiter::for('uploads', function (Request $request) {
        return Limit::perMinute(10)->by($request->user()->id);
    });

    // Different limits for auth/guest
    RateLimiter::for('posts', function (Request $request) {
        return $request->user()
            ? Limit::perMinute(100)->by($request->user()->id)
            : Limit::perMinute(10)->by($request->ip());
    });

    // Multiple limits
    RateLimiter::for('strict', function (Request $request) {
        return [
            Limit::perMinute(10)->by($request->user()->id),
            Limit::perDay(1000)->by($request->user()->id),
        ];
    });

    // Custom response
    RateLimiter::for('custom', function (Request $request) {
        return Limit::perMinute(60)
            ->by($request->user()->id)
            ->response(function (Request $request, array $headers) {
                return response()->json([
                    'message' => 'Too many requests. Please try again later.',
                ], 429, $headers);
            });
    });
}
```

## Apply to Routes

```php
// routes/api.php

// Default throttle
Route::middleware('throttle:api')->group(function () {
    Route::apiResource('posts', PostController::class);
});

// Custom throttle
Route::middleware(['auth:sanctum', 'throttle:uploads'])->group(function () {
    Route::post('files/upload', [FileController::class, 'upload']);
});

// Inline limit
Route::middleware('throttle:10,1')->group(function () {
    Route::post('login', [AuthController::class, 'login']);
});
```

## Custom Throttle Middleware

```php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;

class ThrottleApiRequests
{
    public function handle(Request $request, Closure $next, int $maxAttempts = 60)
    {
        $key = $request->user()?->id ?: $request->ip();

        if (RateLimiter::tooManyAttempts($key, $maxAttempts)) {
            $seconds = RateLimiter::availableIn($key);

            return response()->json([
                'message' => "Too many requests. Retry after {$seconds} seconds.",
            ], 429, [
                'Retry-After' => $seconds,
                'X-RateLimit-Limit' => $maxAttempts,
                'X-RateLimit-Remaining' => 0,
            ]);
        }

        RateLimiter::hit($key);

        $response = $next($request);

        $response->headers->add([
            'X-RateLimit-Limit' => $maxAttempts,
            'X-RateLimit-Remaining' => RateLimiter::remaining($key, $maxAttempts),
        ]);

        return $response;
    }
}
```
