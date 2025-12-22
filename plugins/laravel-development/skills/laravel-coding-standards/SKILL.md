---
name: laravel-coding-standards
description: Comprehensive Laravel and PHP coding standards derived from Spatie guidelines. Use when writing Laravel code, refactoring, or reviewing code quality. Ensures PSR compliance, Laravel conventions, and modern PHP patterns.
---

# Laravel Coding Standards

Code style and best practices for Laravel applications.

## When to Use This Skill

- Writing new Laravel code
- Refactoring existing code
- Code review and quality checks
- Enforcing team conventions
- Learning Laravel best practices

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Code Style | [code-style.md](code-style.md) | Formatting, naming, structure |
| Classes | [classes.md](classes.md) | Controllers, models, services |
| PHP Patterns | [php-patterns.md](php-patterns.md) | Modern PHP 8+ features |
| Documentation | [documentation.md](documentation.md) | Comments, docblocks |

## Quick Reference

### Naming Conventions

```php
// Classes: PascalCase
class UserController {}
class CreatePostRequest {}
class PostResource {}

// Methods/Functions: camelCase
public function getFullName() {}
protected function calculateTotal() {}

// Variables: camelCase
$userName = 'John';
$postCount = 10;

// Constants: SCREAMING_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
public const STATUS_ACTIVE = 'active';

// Database: snake_case
// Tables: plural (users, blog_posts)
// Columns: singular (user_id, created_at)
// Pivot: singular alphabetical (post_tag, role_user)
```

### File Organization

```
app/
├── Http/
│   ├── Controllers/
│   ├── Requests/
│   ├── Resources/
│   └── Middleware/
├── Models/
├── Services/
├── Actions/
├── Enums/
├── Events/
├── Jobs/
├── Listeners/
├── Policies/
└── Traits/
```

### Code Style

```php
// Array syntax
$array = [
    'key' => 'value',
    'another' => 'item',
];

// Trailing commas in multiline
Route::middleware([
    'auth',
    'verified',
    'throttle:60,1',
]);

// Early returns
public function process($data)
{
    if (!$data) {
        return null;
    }

    if (!$data->isValid()) {
        return null;
    }

    return $this->doProcess($data);
}

// Ternary for simple conditions
$status = $user->isActive() ? 'active' : 'inactive';

// Null coalescing
$name = $user->name ?? 'Guest';
$value = $request->input('key') ?? $default;
```

## Best Practices

1. **Use strict types** - `declare(strict_types=1);`
2. **Type everything** - parameters, returns, properties
3. **Early returns** - reduce nesting
4. **Single responsibility** - one class, one purpose
5. **Dependency injection** - over facades when possible
6. **Named arguments** - for clarity
7. **Readonly properties** - when appropriate

## Common Patterns

### Controller Pattern
```php
class PostController extends Controller
{
    public function __construct(
        private readonly PostService $posts
    ) {}

    public function store(StorePostRequest $request): RedirectResponse
    {
        $post = $this->posts->create($request->validated());

        return redirect()->route('posts.show', $post)
            ->with('success', 'Post created.');
    }
}
```

### Service Pattern
```php
final class PostService
{
    public function __construct(
        private readonly PostRepository $repository
    ) {}

    public function create(array $data): Post
    {
        return $this->repository->create($data);
    }
}
```

### Action Pattern
```php
final class CreatePost
{
    public function __construct(
        private readonly PostRepository $repository
    ) {}

    public function execute(array $data): Post
    {
        return $this->repository->create([
            ...$data,
            'slug' => Str::slug($data['title']),
        ]);
    }
}
```
