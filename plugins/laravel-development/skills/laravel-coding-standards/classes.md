# Class Patterns

Controllers, models, actions, DTOs, and other class conventions.

## Controllers

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\StorePostRequest;
use App\Http\Requests\UpdatePostRequest;
use App\Actions\Posts\CreatePostAction;
use App\Actions\Posts\UpdatePostAction;
use App\Http\Resources\PostResource;
use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

final class PostController extends Controller
{
    public function __construct(
        private readonly CreatePostAction $createPostAction,
        private readonly UpdatePostAction $updatePostAction,
    ) {}

    public function index(): AnonymousResourceCollection
    {
        $this->authorize('viewAny', Post::class);

        return PostResource::collection(
            Post::with('author')->latest()->paginate()
        );
    }

    public function store(StorePostRequest $request): RedirectResponse
    {
        $this->authorize('create', Post::class);

        $post = $this->createPostAction->execute($request->toData());

        return redirect()->route('posts.show', $post)
            ->with('success', 'Post created successfully.');
    }

    public function show(Post $post): PostResource
    {
        $this->authorize('view', $post);

        return new PostResource($post->load('author', 'comments'));
    }

    public function update(UpdatePostRequest $request, Post $post): RedirectResponse
    {
        $this->authorize('update', $post);

        $this->updatePostAction->execute($post, $request->toData());

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

## Actions

Actions are the business logic layer. Named `{Verb}{Noun}Action`, they live in `app/Actions/{Domain}/`. Each action has a single `execute()` method that takes a typed DTO -- never `array $data`.

```php
<?php

declare(strict_types=1);

namespace App\Actions\Posts;

use App\Data\Posts\CreatePostData;
use App\Events\Posts\PostCreated;
use App\Models\Post;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

final class CreatePostAction
{
    public function execute(CreatePostData $data): Post
    {
        return DB::transaction(function () use ($data): Post {
            $post = Post::create([
                'user_id' => $data->user_id,
                'title' => $data->title,
                'slug' => Str::slug($data->title),
                'content' => $data->content,
                'status' => $data->status,
            ]);

            if ($data->tag_ids !== null) {
                $post->tags()->sync($data->tag_ids);
            }

            PostCreated::dispatch($post);

            return $post;
        });
    }
}

// Usage (from controller):
// $post = $this->createPostAction->execute($request->toData());
```

## DTOs

DTOs (Data Transfer Objects) are named `{Verb}{Noun}Data` and live in `app/Data/{Domain}/`. They are `final readonly class` with constructor-promoted properties. They carry IDs, not Eloquent models.

```php
<?php

declare(strict_types=1);

namespace App\Data\Posts;

final readonly class CreatePostData
{
    public function __construct(
        public int $user_id,
        public string $title,
        public string $content,
        public string $status = 'draft',
        /** @var array<int>|null */
        public ?array $tag_ids = null,
    ) {}
}
```

### Form Request `toData()` Bridge

Form requests map validated data to DTOs. Controllers never see raw request data.

```php
<?php

declare(strict_types=1);

namespace App\Http\Requests;

use App\Data\Posts\CreatePostData;
use Illuminate\Foundation\Http\FormRequest;

final class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'content' => ['required', 'string', 'max:50000'],
            'status' => ['sometimes', 'string', 'in:draft,published'],
            'tag_ids' => ['nullable', 'array'],
            'tag_ids.*' => ['integer', 'exists:tags,id'],
        ];
    }

    public function toData(): CreatePostData
    {
        $validated = $this->validated();

        return new CreatePostData(
            user_id: $this->user()->id,
            title: $validated['title'],
            content: $validated['content'],
            status: $validated['status'] ?? 'draft',
            tag_ids: $validated['tag_ids'] ?? null,
        );
    }
}
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
