# PHP Patterns

Modern PHP 8+ patterns and features.

## Strict Types

```php
<?php

declare(strict_types=1);

// Always at the top of every file
// Enables strict type checking for function arguments and return values
```

## Type Declarations

```php
// Parameters
public function process(string $name, int $count, ?array $options = null): void
{
}

// Return types
public function getUser(int $id): ?User
{
    return User::find($id);
}

// Union types (PHP 8.0+)
public function handle(string|int $id): User|null
{
    return User::find($id);
}

// Intersection types (PHP 8.1+)
public function process(Countable&Traversable $items): void
{
}

// Never return type
public function fail(string $message): never
{
    throw new \Exception($message);
}
```

## Constructor Property Promotion

```php
// PHP 8.0+
class UserService
{
    public function __construct(
        private readonly UserRepository $repository,
        private readonly CacheService $cache,
        private readonly int $cacheTimeout = 3600
    ) {}
}

// With attributes
class CreateUserAction
{
    public function __construct(
        #[Autowire] private readonly UserRepository $users,
        #[Value('app.timezone')] private readonly string $timezone
    ) {}
}
```

## Readonly Properties

```php
// PHP 8.1+
class Post
{
    public function __construct(
        public readonly int $id,
        public readonly string $title,
        public readonly ?DateTimeImmutable $publishedAt = null
    ) {}
}

// Readonly class (PHP 8.2+)
readonly class PostData
{
    public function __construct(
        public string $title,
        public string $content,
        public array $tags = []
    ) {}
}
```

## Named Arguments

```php
// Clear intent for boolean/option arguments
User::create(
    name: 'John Doe',
    email: 'john@example.com',
    isAdmin: false,
    notifyOnCreate: true
);

// Skip optional parameters
$collection->sortBy(
    callback: fn($item) => $item->name,
    descending: true
);
```

## Null Safety

```php
// Null coalescing
$name = $user->name ?? 'Guest';
$value = $array['key'] ?? $default;

// Null coalescing assignment
$array['key'] ??= 'default';

// Null safe operator (PHP 8.0+)
$country = $user?->address?->country?->name;
$length = $user?->posts?->count() ?? 0;
```

## Match Expressions

```php
// PHP 8.0+
$message = match($status) {
    'pending' => 'Awaiting review',
    'approved', 'published' => 'Content is live',
    'rejected' => 'Content was rejected',
    default => 'Unknown status',
};

// With conditions
$result = match(true) {
    $age < 18 => 'minor',
    $age < 65 => 'adult',
    default => 'senior',
};
```

## Arrow Functions

```php
// Short closures for simple operations
$names = $users->map(fn($user) => $user->name);

$active = $users->filter(fn($user) => $user->isActive());

$sorted = $posts->sortBy(fn($post) => $post->published_at);

// With type hints
$transform = fn(User $user): string => $user->getFullName();
```

## Enums

```php
// Basic enum
enum Status
{
    case Pending;
    case Active;
    case Inactive;
}

// Backed enum
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

    public static function options(): array
    {
        return array_map(
            fn($case) => ['value' => $case->value, 'label' => $case->label()],
            self::cases()
        );
    }
}

// Usage
$status = PostStatus::Draft;
$post->status = PostStatus::Published;
```

## First-Class Callables

```php
// PHP 8.1+
$users->each($this->processUser(...));
$posts->map($this->formatPost(...));

// Instead of
$users->each([$this, 'processUser']);
$posts->map(fn($post) => $this->formatPost($post));
```

## Attributes

```php
use Attribute;

#[Attribute(Attribute::TARGET_PROPERTY)]
class Validate
{
    public function __construct(
        public string $rule,
        public ?string $message = null
    ) {}
}

class CreateUserRequest
{
    #[Validate('required|email')]
    public string $email;

    #[Validate('required|min:8')]
    public string $password;
}
```
