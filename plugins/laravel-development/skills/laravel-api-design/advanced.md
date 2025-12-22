# Advanced API Patterns

Versioning, pagination, filtering, and webhooks.

## API Versioning

```php
// routes/api.php

// URL-based versioning
Route::prefix('v1')->group(function () {
    Route::apiResource('posts', Api\V1\PostController::class);
});

Route::prefix('v2')->group(function () {
    Route::apiResource('posts', Api\V2\PostController::class);
});

// Version-specific resources
namespace App\Http\Resources\V1;

class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
        ];
    }
}

namespace App\Http\Resources\V2;

class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'author' => new UserResource($this->whenLoaded('author')),
            'metadata' => $this->metadata, // New in V2
        ];
    }
}
```

## Pagination and Filtering

```php
class PostController extends Controller
{
    public function index(Request $request)
    {
        $query = Post::query();

        // Filter by status
        if ($request->has('status')) {
            $query->where('status', $request->status);
        }

        // Filter by category
        if ($request->has('category_id')) {
            $query->where('category_id', $request->category_id);
        }

        // Search
        if ($request->has('search')) {
            $query->where(function ($q) use ($request) {
                $q->where('title', 'like', "%{$request->search}%")
                    ->orWhere('content', 'like', "%{$request->search}%");
            });
        }

        // Sort
        $sortBy = $request->get('sort_by', 'created_at');
        $sortOrder = $request->get('sort_order', 'desc');
        $query->orderBy($sortBy, $sortOrder);

        // Include relationships
        if ($request->has('include')) {
            $includes = explode(',', $request->include);
            $allowed = ['author', 'category', 'tags'];
            $query->with(array_intersect($includes, $allowed));
        }

        return PostResource::collection($query->paginate($request->get('per_page', 15)));
    }
}
```

## Cursor Pagination

```php
public function index(Request $request)
{
    $posts = Post::orderBy('id')
        ->cursorPaginate($request->get('per_page', 15));

    return PostResource::collection($posts);
}
```

## Batch Operations

```php
class PostBatchController extends Controller
{
    public function store(Request $request)
    {
        $request->validate([
            'posts' => 'required|array|min:1|max:100',
            'posts.*.title' => 'required|string',
            'posts.*.content' => 'required|string',
        ]);

        $posts = collect($request->posts)->map(function ($data) use ($request) {
            return Post::create([
                'user_id' => $request->user()->id,
                ...$data,
            ]);
        });

        return response()->json([
            'message' => 'Posts created successfully',
            'data' => PostResource::collection($posts),
        ], 201);
    }

    public function destroy(Request $request)
    {
        $request->validate([
            'ids' => 'required|array',
            'ids.*' => 'exists:posts,id',
        ]);

        Post::whereIn('id', $request->ids)->delete();

        return response()->json(['message' => 'Posts deleted']);
    }
}
```

## Webhooks

```php
class WebhookController extends Controller
{
    public function store(Request $request)
    {
        $request->validate([
            'url' => 'required|url',
            'events' => 'required|array',
            'events.*' => 'in:post.created,post.updated,post.deleted',
        ]);

        $webhook = $request->user()->webhooks()->create([
            'url' => $request->url,
            'events' => $request->events,
            'secret' => Str::random(40),
        ]);

        return response()->json($webhook, 201);
    }
}

// Trigger webhook job
class TriggerWebhook implements ShouldQueue
{
    public function __construct(
        public Webhook $webhook,
        public string $event,
        public array $payload
    ) {}

    public function handle()
    {
        $data = [
            'event' => $this->event,
            'payload' => $this->payload,
            'timestamp' => now()->timestamp,
        ];

        $signature = hash_hmac('sha256', json_encode($data), $this->webhook->secret);

        Http::withHeaders([
            'X-Webhook-Signature' => $signature,
        ])->post($this->webhook->url, $data);
    }
}
```
