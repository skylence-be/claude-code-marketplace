---
description: Create Laravel middleware for request filtering
model: claude-sonnet-4-5
---

Create a Laravel middleware.

## Middleware Specification

$ARGUMENTS

## Laravel Middleware Patterns

### 1. **Basic Middleware**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class CheckUserRole
{
    public function handle(Request $request, Closure $next, string $role): Response
    {
        if (!$request->user() || $request->user()->role !== $role) {
            abort(403, 'Unauthorized action.');
        }

        return $next($request);
    }
}
```

### 2. **Middleware with Before & After Actions**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\Response;

class LogRequests
{
    public function handle(Request $request, Closure $next): Response
    {
        // Before the request
        Log::info('Request started', [
            'url' => $request->fullUrl(),
            'method' => $request->method(),
            'ip' => $request->ip(),
        ]);

        $response = $next($request);

        // After the request
        Log::info('Request completed', [
            'status' => $response->getStatusCode(),
        ]);

        return $response;
    }
}
```

### 3. **Terminable Middleware**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Symfony\Component\HttpFoundation\Response;

class TrackPageViews
{
    public function handle(Request $request, Closure $next): Response
    {
        return $next($request);
    }

    public function terminate(Request $request, Response $response): void
    {
        // Execute after response sent to browser
        if ($response->isSuccessful()) {
            Cache::increment('page_views:' . $request->path());
        }
    }
}
```

### 4. **Rate Limiting Middleware**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Symfony\Component\HttpFoundation\Response;

class CustomRateLimit
{
    public function handle(Request $request, Closure $next, int $maxAttempts = 60): Response
    {
        $key = 'rate-limit:' . $request->ip();

        if (RateLimiter::tooManyAttempts($key, $maxAttempts)) {
            $seconds = RateLimiter::availableIn($key);

            return response()->json([
                'message' => 'Too many requests. Please try again later.',
                'retry_after' => $seconds,
            ], 429);
        }

        RateLimiter::hit($key, 60); // Decay in 60 seconds

        $response = $next($request);

        return $response->withHeaders([
            'X-RateLimit-Limit' => $maxAttempts,
            'X-RateLimit-Remaining' => RateLimiter::remaining($key, $maxAttempts),
        ]);
    }
}
```

### 5. **API Key Authentication Middleware**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class ValidateApiKey
{
    public function handle(Request $request, Closure $next): Response
    {
        $apiKey = $request->header('X-API-Key');

        if (!$apiKey) {
            return response()->json([
                'message' => 'API key is required',
            ], 401);
        }

        $validKeys = config('api.keys', []);

        if (!in_array($apiKey, $validKeys)) {
            return response()->json([
                'message' => 'Invalid API key',
            ], 401);
        }

        return $next($request);
    }
}
```

### 6. **Request Modification Middleware**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class SanitizeInput
{
    public function handle(Request $request, Closure $next): Response
    {
        $input = $request->all();

        array_walk_recursive($input, function (&$value) {
            if (is_string($value)) {
                $value = strip_tags($value);
                $value = trim($value);
            }
        });

        $request->merge($input);

        return $next($request);
    }
}
```

### 7. **Response Modification Middleware**

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AddSecurityHeaders
{
    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);

        $response->headers->set('X-Frame-Options', 'SAMEORIGIN');
        $response->headers->set('X-Content-Type-Options', 'nosniff');
        $response->headers->set('X-XSS-Protection', '1; mode=block');
        $response->headers->set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');

        return $response;
    }
}
```

## Best Practices
- Keep middleware focused on single responsibility
- Use parameters for flexibility
- Register in app/Http/Kernel.php
- Use terminate() for post-response tasks
- Return proper HTTP status codes
- Add descriptive error messages
- Consider performance impact
- Test middleware thoroughly

Generate complete Laravel middleware with proper structure.
