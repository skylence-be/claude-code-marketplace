---
name: php-modern-features
description: Modern PHP 8.4 and 8.5 language features including new array functions, pipe operator, clone-with-properties, and chaining on new instances. Use when writing PHP code that targets 8.4+ or when replacing manual loops with built-in functions.
category: php
tags: [php, 8.4, 8.5, modern, array-functions, pipe-operator]
related_skills: [laravel-coding-standards, laravel-blueprint]
---

# Modern PHP Features (8.4 / 8.5)

New language features in PHP 8.4 and 8.5 that replace common patterns with cleaner, more expressive code. Use these when the project targets the appropriate PHP version.

## When to Use This Skill

- Writing PHP code targeting 8.4+ or 8.5+
- Replacing manual loops with built-in array functions
- Chaining method calls on newly created objects
- Working with readonly classes that need modification on clone

## Version Detection

Check the project's PHP version:
- `composer.json` → `require.php` (e.g., `"php": "^8.4"`)
- `php -v` in the project environment

## PHP 8.4 Features

### New Array Functions

Use these instead of manual `foreach` loops when not using Laravel collections:

```php
// array_find — first element matching callback
$admin = array_find($users, fn(User $u) => $u->isAdmin());
// Before: foreach + break

// array_find_key — key of first matching element
$key = array_find_key($users, fn(User $u) => $u->isAdmin());
// Before: foreach + break with key tracking

// array_any — true if any element matches
$hasAdmin = array_any($users, fn(User $u) => $u->isAdmin());
// Before: foreach + flag variable

// array_all — true if all elements match
$allVerified = array_all($users, fn(User $u) => $u->isVerified());
// Before: foreach + flag with early return
```

### Chaining on New Instances

Chain methods directly on `new` without wrapping in parentheses:

```php
// PHP 8.4
$response = new JsonResponse(['data' => $data])->setStatusCode(201);

// Before PHP 8.4 (required parentheses)
$response = (new JsonResponse(['data' => $data]))->setStatusCode(201);
```

## PHP 8.5 Features

### Additional Array Functions

```php
// array_first — first value (or null if empty)
$first = array_first($items);
// Before: reset($items) or $items[array_key_first($items)]

// array_last — last value (or null if empty)
$last = array_last($items);
// Before: end($items) or $items[array_key_last($items)]
```

### Pipe Operator

Chain function calls left-to-right instead of nesting:

```php
// PHP 8.5 — reads left to right
$slug = $title
    |> trim(...)
    |> (fn($s) => str_replace(' ', '-', $s))
    |> strtolower(...);

// Before — reads inside-out
$slug = strtolower(str_replace(' ', '-', trim($title)));
```

The pipe operator passes the result of the left expression as the argument to the right expression. Use `...` for first-class callables or closures for functions needing extra arguments.

### Clone with Properties

Modify readonly properties during cloning:

```php
// PHP 8.5
$updated = clone($original, ['status' => 'published', 'updatedAt' => now()]);

// Before — required withers or reflection hacks
$updated = $original->withStatus('published')->withUpdatedAt(now());
```

Ideal for readonly classes and value objects where properties can't be set after construction.

## When to Use vs Laravel Collections

| Scenario | Use |
|----------|-----|
| Already have a Collection | Collection methods (`->first()`, `->contains()`, etc.) |
| Plain PHP array, simple check | PHP 8.4 array functions |
| Need chaining multiple operations | Collection or pipe operator |
| Performance-critical hot path | PHP native functions (no Collection overhead) |

## Common Pitfalls

- Using `array_find`/`array_any` in a project targeting PHP < 8.4 (check `composer.json`)
- Using pipe operator in PHP < 8.5
- Forgetting that `array_first`/`array_last` return `null` on empty arrays (not false)
- Using these array functions when Laravel Collections are already in scope (redundant)
