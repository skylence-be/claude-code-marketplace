# PHP Review Rules

Technology-specific review rules for PHP 8.1+ code. Loaded when `.php` files are detected in the changeset.

## Detection
- File extension: `.php`
- `composer.json` exists

## Anti-Patterns to Flag

### Loose Comparison
Using `==` instead of `===` can cause type juggling bugs. PHP's loose comparison has well-documented unexpected behaviors (`"0" == false`, `"" == 0`, `null == false`).
- **Severity:** Medium
- **Confidence boost:** +2 (known anti-pattern)
- **Exception:** Comparison with `null` where both `null` and `false` should match

### Missing Type Declarations
Functions without parameter types and return types bypass PHP's type system.
- **Severity:** Low
- **Check:** Function declarations missing parameter types or return type
- **Exception:** If the codebase consistently omits types (reduce confidence by 2)

### Error Suppression Operator
Using `@` to suppress errors hides real problems and makes debugging difficult.
- **Severity:** Medium
- **Pattern:** `@function_call()`, `@$variable`
- **Fix:** Use try-catch or null coalescing instead

### Missing Strict Types
Files without `declare(strict_types=1)` allow implicit type coercion.
- **Severity:** Low
- **Check:** First line after `<?php` opening tag
- **Exception:** View/template files, config files

### Not Using Enums
Using class constants or magic strings for fixed value sets instead of PHP 8.1 enums.
- **Severity:** Low
- **Pattern:** Multiple string/int constants representing a set of valid values
- **Exception:** If project targets PHP < 8.1

### Missing Readonly Properties
Properties set once in constructor but not marked `readonly` (PHP 8.1+).
- **Severity:** Low
- **Check:** Constructor-promoted properties without `readonly` keyword
- **Exception:** Properties that are intentionally mutable

### Null-Safe Operator Missing
Long null check chains instead of `?->` operator (PHP 8.0+).
- **Severity:** Low
- **Pattern:** `if ($obj !== null && $obj->method() !== null && ...)`
- **Fix:** `$obj?->method()?->property`

### Named Arguments Missing for Booleans
Positional boolean arguments are unclear at the call site.
- **Severity:** Low
- **Pattern:** `function_call($data, true, false, true)`
- **Fix:** `function_call($data, validate: true, strict: false, throw: true)`
