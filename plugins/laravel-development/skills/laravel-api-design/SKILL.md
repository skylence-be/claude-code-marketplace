---
name: laravel-api-design
description: Master RESTful API design with Laravel including API resources, Sanctum authentication, rate limiting, pagination, versioning, error handling, and comprehensive API development patterns. Use when building REST APIs, mobile backends, or third-party integrations.
---

# Laravel API Design

Comprehensive guide to building RESTful APIs in Laravel.

## When to Use This Skill

- Building RESTful APIs for mobile/web apps
- Creating backend services for SPAs
- Implementing API authentication (Sanctum)
- Rate limiting and throttling requests
- API versioning strategies

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Controllers | `controllers.md` | RESTful endpoints, responses |
| Resources | `resources.md` | Data transformation, JSON |
| Authentication | `authentication.md` | Sanctum, tokens, guards |
| Validation | `validation.md` | Form requests, error handling |
| Rate Limiting | `rate-limiting.md` | Throttling, protection |
| Advanced | `advanced.md` | Versioning, pagination, webhooks |

## Quick Start

```php
// Install Sanctum
composer require laravel/sanctum
php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"
php artisan migrate

// routes/api.php
Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('posts', PostController::class);
});

// API Controller
class PostController extends Controller
{
    public function index()
    {
        return PostResource::collection(Post::paginate());
    }

    public function store(StorePostRequest $request)
    {
        $post = Post::create($request->validated());
        return new PostResource($post);
    }
}
```

## Core Concepts

### RESTful Principles
- **Resources**: Endpoints represent resources (users, posts)
- **HTTP Methods**: GET, POST, PUT/PATCH, DELETE
- **Status Codes**: Proper codes for responses
- **Stateless**: Each request is self-contained

### API Resources
```php
class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'author' => new UserResource($this->whenLoaded('author')),
            'created_at' => $this->created_at->toIso8601String(),
        ];
    }
}
```

## Quick Reference

### HTTP Status Codes
```php
return response()->json($data);           // 200 OK
return response()->json($data, 201);      // Created
return response()->json(null, 204);       // No Content
return response()->json(['error' => '...'], 400); // Bad Request
return response()->json(['error' => '...'], 401); // Unauthorized
return response()->json(['error' => '...'], 403); // Forbidden
return response()->json(['error' => '...'], 404); // Not Found
return response()->json(['error' => '...'], 422); // Validation Error
return response()->json(['error' => '...'], 429); // Too Many Requests
```

### Sanctum Authentication
```php
// Login and get token
$token = $user->createToken('auth_token')->plainTextToken;

// Protect routes
Route::middleware('auth:sanctum')->group(function () {
    // Protected routes
});

// Get authenticated user
$user = $request->user();

// Logout (revoke token)
$request->user()->currentAccessToken()->delete();
```

### Rate Limiting
```php
// In RouteServiceProvider
RateLimiter::for('api', function (Request $request) {
    return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
});

// Apply to routes
Route::middleware('throttle:api')->group(function () {
    // Rate limited routes
});
```

## Best Practices

1. **Use API resources** for consistent data transformation
2. **Implement authentication** with Sanctum
3. **Apply rate limiting** to prevent abuse
4. **Version your APIs** for backward compatibility
5. **Validate all input** with Form Requests
6. **Use proper HTTP status codes**
7. **Paginate large datasets**

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Exposing sensitive data | Use API resources |
| No rate limiting | Configure throttle middleware |
| No input validation | Use Form Requests |
| Wrong status codes | Use proper HTTP codes |
| N+1 queries | Eager load relationships |
