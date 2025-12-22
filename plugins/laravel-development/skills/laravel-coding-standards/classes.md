# Class Patterns

Controllers, models, services, and other class conventions.

## Controllers

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\StorePostRequest;
use App\Http\Requests\UpdatePostRequest;
use App\Http\Resources\PostResource;
use App\Models\Post;
use App\Services\PostService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

final class PostController extends Controller
{
    public function __construct(
        private readonly PostService $posts
    ) {}

    public function index(): AnonymousResourceCollection
    {
        return PostResource::collection(
            Post::with('author')->latest()->paginate()
        );
    }

    public function store(StorePostRequest $request): RedirectResponse
    {
        $post = $this->posts->create($request->validated());

        return redirect()->route('posts.show', $post)
            ->with('success', 'Post created successfully.');
    }

    public function show(Post $post): PostResource
    {
        return new PostResource($post->load('author', 'comments'));
    }

    public function update(UpdatePostRequest $request, Post $post): RedirectResponse
    {
        $this->posts->update($post, $request->validated());

        return redirect()->route('posts.show', $post)
            ->with('success', 'Post updated successfully.');
    }

    public function destroy(Post $post): RedirectResponse
    {
        $this->authorize('delete', $post);

        $post->delete();

        return redirect()->route('posts.index')
            ->with('success', 'Post deleted successfully.');
    }
}
```

## Models

```php
<?php

declare(strict_types=1);

namespace App\Models;

use App\Enums\PostStatus;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

final class Post extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'title',
        'slug',
        'content',
        'status',
        'published_at',
    ];

    protected function casts(): array
    {
        return [
            'status' => PostStatus::class,
            'published_at' => 'datetime',
            'metadata' => 'array',
        ];
    }

    // Relationships
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    // Scopes
    public function scopePublished($query)
    {
        return $query->where('status', PostStatus::Published)
            ->whereNotNull('published_at')
            ->where('published_at', '<=', now());
    }

    public function scopeDraft($query)
    {
        return $query->where('status', PostStatus::Draft);
    }

    // Accessors & Mutators
    protected function title(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
            set: fn (string $value) => strtolower($value),
        );
    }

    // Methods
    public function publish(): void
    {
        $this->update([
            'status' => PostStatus::Published,
            'published_at' => now(),
        ]);
    }

    public function isPublished(): bool
    {
        return $this->status === PostStatus::Published
            && $this->published_at?->isPast();
    }
}
```

## Services

```php
<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Post;
use App\Repositories\PostRepository;
use Illuminate\Support\Facades\DB;

final class PostService
{
    public function __construct(
        private readonly PostRepository $repository
    ) {}

    public function create(array $data): Post
    {
        return DB::transaction(function () use ($data) {
            $post = $this->repository->create($data);

            if (isset($data['tags'])) {
                $post->tags()->sync($data['tags']);
            }

            return $post;
        });
    }

    public function update(Post $post, array $data): Post
    {
        return DB::transaction(function () use ($post, $data) {
            $post->update($data);

            if (isset($data['tags'])) {
                $post->tags()->sync($data['tags']);
            }

            return $post->fresh();
        });
    }
}
```

## Actions

```php
<?php

declare(strict_types=1);

namespace App\Actions;

use App\Models\Post;
use App\Models\User;
use Illuminate\Support\Str;

final class CreatePost
{
    public function execute(User $user, array $data): Post
    {
        return $user->posts()->create([
            'title' => $data['title'],
            'slug' => Str::slug($data['title']),
            'content' => $data['content'],
            'status' => $data['status'] ?? 'draft',
        ]);
    }
}

// Usage
$action = app(CreatePost::class);
$post = $action->execute($user, $validated);
```

## Enums

```php
<?php

declare(strict_types=1);

namespace App\Enums;

enum PostStatus: string
{
    case Draft = 'draft';
    case Published = 'published';
    case Archived = 'archived';

    public function label(): string
    {
        return match($this) {
            self::Draft => 'Draft',
            self::Published => 'Published',
            self::Archived => 'Archived',
        };
    }

    public function color(): string
    {
        return match($this) {
            self::Draft => 'gray',
            self::Published => 'green',
            self::Archived => 'red',
        };
    }
}
```
