# Code Style

Formatting and style conventions.

## Formatting

```php
<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Repositories\UserRepository;
use Illuminate\Support\Collection;

final class UserService
{
    public function __construct(
        private readonly UserRepository $repository
    ) {}

    public function findActiveUsers(): Collection
    {
        return $this->repository->getActive();
    }
}
```

## Arrays

```php
// Short array syntax
$items = ['one', 'two', 'three'];

// Multiline with trailing comma
$config = [
    'driver' => 'redis',
    'host' => 'localhost',
    'port' => 6379,
];

// When to use multiline
$short = ['a', 'b', 'c'];
$long = [
    'first_item_with_long_name',
    'second_item_with_long_name',
    'third_item_with_long_name',
];
```

## Strings

```php
// Double quotes when interpolating
$greeting = "Hello, {$user->name}!";

// Single quotes for simple strings
$status = 'active';

// Concatenation vs interpolation
// Prefer interpolation
$message = "User {$user->name} created post {$post->title}";

// Use sprintf for complex formatting
$log = sprintf('[%s] User %d: %s', now(), $user->id, $message);
```

## Conditionals

```php
// Early returns to reduce nesting
public function process(Request $request): Response
{
    if (!$request->user()) {
        return response()->json(['error' => 'Unauthorized'], 401);
    }

    if (!$request->has('data')) {
        return response()->json(['error' => 'Missing data'], 422);
    }

    return $this->doProcess($request);
}

// Ternary for simple conditions
$status = $user->isActive() ? 'active' : 'inactive';

// Null coalescing
$name = $user->name ?? 'Guest';
$value = $request->input('key', 'default');

// Null safe operator
$country = $user->address?->country?->name;

// Match expressions (PHP 8+)
$result = match($status) {
    'pending' => 'Awaiting approval',
    'approved' => 'Approved',
    'rejected' => 'Rejected',
    default => 'Unknown',
};
```

## Comments

```php
// Single line for quick notes
$total = $subtotal + $tax; // Include shipping

// Block comments for explanations
/*
 * Calculate the total price including:
 * - Base product price
 * - Applicable taxes
 * - Shipping costs based on weight
 */
$total = $this->calculateTotal($order);

// TODO comments
// TODO: Refactor this to use the new pricing service
```

## Spacing

```php
// Space after keywords
if ($condition) {
    // ...
}

foreach ($items as $item) {
    // ...
}

// No space before parentheses in function calls
$result = someFunction($arg1, $arg2);

// Space around operators
$total = $price * $quantity;
$isValid = $status === 'active' && $count > 0;

// No trailing whitespace
// End files with single newline
```

## Line Length

```php
// Max 120 characters preferred

// Break long lines sensibly
$users = User::where('status', 'active')
    ->where('role', 'admin')
    ->orderBy('created_at', 'desc')
    ->get();

// Long strings
$message = 'This is a very long message that would exceed the line length limit, '
    . 'so we break it into multiple lines for readability.';

// Long arrays
$config = [
    'option_one' => 'value',
    'option_two' => 'value',
    'option_three' => 'value',
];
```
