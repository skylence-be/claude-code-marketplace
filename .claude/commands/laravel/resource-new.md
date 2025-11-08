---
description: Create Laravel API resource for data transformation
model: claude-sonnet-4-5
---

Create a Laravel API resource.

## Resource Specification

$ARGUMENTS

## Laravel Resource Patterns

### 1. **Basic Resource**

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'slug' => $this->slug,
            'excerpt' => $this->excerpt,
            'content' => $this->content,
            'status' => $this->status,
            'published_at' => $this->published_at?->toISOString(),
            'created_at' => $this->created_at->toISOString(),
            'updated_at' => $this->updated_at->toISOString(),
        ];
    }
}
```

### 2. **Resource with Relationships**

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'slug' => $this->slug,
            'content' => $this->content,
            'status' => $this->status,

            // Always include
            'author' => new UserResource($this->whenLoaded('user')),

            // Conditional relationships
            'category' => CategoryResource::make($this->whenLoaded('category')),
            'tags' => TagResource::collection($this->whenLoaded('tags')),
            'comments' => CommentResource::collection($this->whenLoaded('comments')),

            // Computed values
            'comments_count' => $this->whenCounted('comments'),
            'is_published' => $this->status === 'published',

            'published_at' => $this->published_at?->toISOString(),
            'created_at' => $this->created_at->toISOString(),
        ];
    }
}
```

### 3. **Resource with Conditional Attributes**

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'avatar' => $this->avatar_url,

            // Only for authenticated user viewing their own profile
            'phone' => $this->when(
                $request->user()?->id === $this->id,
                $this->phone
            ),

            // Admin-only fields
            $this->mergeWhen($request->user()?->isAdmin(), [
                'email_verified_at' => $this->email_verified_at,
                'last_login_at' => $this->last_login_at,
                'ip_address' => $this->last_login_ip,
            ]),

            // Conditional pivot data
            'role' => $this->when(
                $this->pivot,
                fn () => $this->pivot->role
            ),

            'created_at' => $this->created_at->toISOString(),
        ];
    }
}
```

### 4. **Resource Collection**

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;

class PostCollection extends ResourceCollection
{
    public function toArray(Request $request): array
    {
        return [
            'data' => $this->collection,
            'meta' => [
                'total' => $this->total(),
                'current_page' => $this->currentPage(),
                'last_page' => $this->lastPage(),
                'per_page' => $this->perPage(),
            ],
            'filters' => [
                'status' => $request->query('status'),
                'category' => $request->query('category'),
            ],
        ];
    }

    public function with(Request $request): array
    {
        return [
            'version' => '1.0.0',
            'api_url' => config('app.url') . '/api',
        ];
    }
}
```

### 5. **Resource with Custom Wrapping**

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class PostResource extends JsonResource
{
    public static $wrap = 'post';

    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'attributes' => [
                'title' => $this->title,
                'content' => $this->content,
                'published_at' => $this->published_at,
            ],
            'relationships' => [
                'author' => [
                    'data' => [
                        'id' => $this->user_id,
                        'type' => 'users',
                    ],
                ],
            ],
            'links' => [
                'self' => route('api.posts.show', $this->id),
                'author' => route('api.users.show', $this->user_id),
            ],
        ];
    }

    public function with(Request $request): array
    {
        return [
            'meta' => [
                'version' => '1.0',
            ],
        ];
    }
}
```

## Best Practices
- Use whenLoaded() for relationships to avoid N+1
- Use when() for conditional attributes
- Use mergeWhen() for multiple conditional fields
- Create separate resource collections for custom metadata
- Use resource wrapping consistently
- Don't expose sensitive data
- Use ISO 8601 format for dates
- Consider API versioning

Generate complete Laravel API resource with proper structure.
