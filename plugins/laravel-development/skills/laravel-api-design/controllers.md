# API Controllers

RESTful controller patterns for Laravel APIs.

## Resource Controller

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\StorePostRequest;
use App\Http\Requests\UpdatePostRequest;
use App\Http\Resources\PostResource;
use App\Models\Post;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class PostController extends Controller
{
    /**
     * Display a listing of posts.
     */
    public function index(): AnonymousResourceCollection
    {
        $posts = Post::with(['author', 'category'])
            ->latest()
            ->paginate(20);

        return PostResource::collection($posts);
    }

    /**
     * Store a newly created post.
     */
    public function store(StorePostRequest $request): JsonResponse
    {
        $post = Post::create([
            'user_id' => $request->user()->id,
            ...$request->validated(),
        ]);

        return (new PostResource($post))
            ->response()
            ->setStatusCode(201);
    }

    /**
     * Display the specified post.
     */
    public function show(Post $post): PostResource
    {
        $post->load(['author', 'category', 'tags', 'comments']);

        return new PostResource($post);
    }

    /**
     * Update the specified post.
     */
    public function update(UpdatePostRequest $request, Post $post): PostResource
    {
        $this->authorize('update', $post);

        $post->update($request->validated());

        return new PostResource($post);
    }

    /**
     * Remove the specified post.
     */
    public function destroy(Post $post): JsonResponse
    {
        $this->authorize('delete', $post);

        $post->delete();

        return response()->json(null, 204);
    }
}
```

## Route Registration

```php
// routes/api.php
Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('posts', PostController::class);

    // Additional custom endpoints
    Route::post('posts/{post}/publish', [PostController::class, 'publish']);
    Route::get('posts/{post}/related', [PostController::class, 'related']);
});
```

## Response Trait

```php
namespace App\Traits;

trait ApiResponses
{
    protected function success($data = null, string $message = null, int $code = 200)
    {
        return response()->json([
            'success' => true,
            'message' => $message,
            'data' => $data,
        ], $code);
    }

    protected function error(string $message, int $code = 400, $errors = null)
    {
        $response = [
            'success' => false,
            'message' => $message,
        ];

        if ($errors) {
            $response['errors'] = $errors;
        }

        return response()->json($response, $code);
    }

    protected function created($data, string $message = 'Resource created')
    {
        return $this->success($data, $message, 201);
    }

    protected function noContent()
    {
        return response()->json(null, 204);
    }
}

// Usage
class PostController extends Controller
{
    use ApiResponses;

    public function store(StorePostRequest $request)
    {
        $post = Post::create($request->validated());

        return $this->created(new PostResource($post));
    }
}
```
