# API Resources

Transform Eloquent models into JSON responses.

## Basic Resource

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
            'status' => $this->status,
            'published_at' => $this->published_at?->toIso8601String(),
            'created_at' => $this->created_at->toIso8601String(),
            'updated_at' => $this->updated_at->toIso8601String(),
        ];
    }
}
```

## Conditional Attributes

```php
class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,

            // Only on single post view
            'content' => $this->when($request->routeIs('posts.show'), $this->content),

            // Only if user can edit
            'can_edit' => $this->when(
                $request->user()?->can('update', $this->resource),
                true
            ),

            // Only if relationship is loaded
            'author' => new UserResource($this->whenLoaded('author')),
            'tags' => TagResource::collection($this->whenLoaded('tags')),

            // Only if count is loaded
            'comments_count' => $this->whenCounted('comments'),

            // Only if aggregate is loaded
            'average_rating' => $this->whenAggregated('reviews', 'rating', 'avg'),
        ];
    }
}
```

## Resource Collection

```php
namespace App\Http\Resources;

use Illuminate\Http\Resources\Json\ResourceCollection;

class PostCollection extends ResourceCollection
{
    public function toArray(Request $request): array
    {
        return [
            'data' => $this->collection,
            'links' => [
                'self' => route('posts.index'),
            ],
            'meta' => [
                'total' => $this->total(),
                'count' => $this->count(),
                'per_page' => $this->perPage(),
                'current_page' => $this->currentPage(),
                'total_pages' => $this->lastPage(),
            ],
        ];
    }
}

// Usage
public function index()
{
    $posts = Post::with('author')->paginate(20);
    return new PostCollection($posts);
}
```

## Nested Resources

```php
class UserResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->when($request->user()?->id === $this->id, $this->email),
            'avatar' => $this->avatar_url,
        ];
    }
}

class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'author' => new UserResource($this->whenLoaded('author')),
            'comments' => CommentResource::collection($this->whenLoaded('comments')),
        ];
    }
}
```

## Additional Data

```php
class PostResource extends JsonResource
{
    public function with(Request $request): array
    {
        return [
            'meta' => [
                'version' => '1.0',
                'api_docs' => route('api.docs'),
            ],
        ];
    }
}
```
