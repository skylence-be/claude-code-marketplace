---
name: laravel-security-patterns
description: Master Laravel security with CSRF protection, XSS prevention, SQL injection defense, mass assignment protection, rate limiting, authentication, authorization, input validation, and comprehensive security best practices. Use when securing applications, preventing attacks, or implementing defense-in-depth strategies.
---

# Laravel Security Patterns

Comprehensive guide to securing Laravel applications.

## When to Use This Skill

- Protecting against common vulnerabilities
- Implementing authentication/authorization
- Preventing CSRF, XSS, SQL injection
- Validating and sanitizing input
- Setting up rate limiting

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| CSRF & XSS | `csrf-xss.md` | Cross-site protection |
| SQL Injection | `sql-injection.md` | Database security |
| Authentication | `authentication.md` | Login, passwords, 2FA |
| Authorization | `authorization.md` | Gates, policies, roles |
| Input Validation | `input-validation.md` | Sanitization, validation |

## Quick Start

```php
// CSRF Protection
<form method="POST">
    @csrf
    <!-- form fields -->
</form>

// XSS Prevention (auto-escaped)
{{ $userInput }}

// SQL Injection Prevention (use Eloquent)
User::where('email', $email)->first();

// Mass Assignment Protection
protected $fillable = ['name', 'email'];

// Authorization
$this->authorize('update', $post);

// Rate Limiting
Route::middleware('throttle:60,1')->group(fn() => /* routes */);
```

## Core Concepts

### OWASP Top 10 in Laravel
- **Injection**: Eloquent ORM, prepared statements
- **Broken Auth**: Built-in auth system
- **XSS**: Blade auto-escaping
- **CSRF**: Token verification
- **Misconfiguration**: Environment configs

### Defense in Depth
- Multiple security layers
- Input validation + output encoding
- Secure defaults
- Least privilege principle

## Quick Reference

### CSRF Protection
```php
// In forms
@csrf

// In AJAX
$.ajaxSetup({
    headers: { 'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content') }
});

// Exclude routes (rarely needed)
protected $except = ['/webhook'];
```

### XSS Prevention
```php
{{ $userInput }}          // Escaped (safe)
{!! $trustedHtml !!}      // Unescaped (dangerous)
@{{ $vueVariable }}       // Vue/Alpine syntax
```

### Mass Assignment
```php
// Whitelist approach (recommended)
protected $fillable = ['name', 'email', 'bio'];

// Blacklist approach
protected $guarded = ['id', 'role', 'is_admin'];

// Fill only validated data
$user->fill($request->validated());
```

### Authorization
```php
// Gates
Gate::define('update-post', fn(User $user, Post $post) =>
    $user->id === $post->user_id
);
Gate::allows('update-post', $post);

// Policies
$this->authorize('update', $post);

// Blade
@can('update', $post)
    <button>Edit</button>
@endcan
```

## Best Practices

1. **Never trust user input** - validate everything
2. **Use prepared statements** - Eloquent does this
3. **Escape output** - Blade does this by default
4. **Apply HTTPS** - in production always
5. **Use strong passwords** - bcrypt/argon2
6. **Rate limit** - prevent brute force
7. **Keep secrets in .env** - never commit

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| {!! $input !!} | Use {{ }} for user input |
| DB::raw($input) | Use bindings or Eloquent |
| Missing @csrf | Always include in forms |
| $guarded = [] | Never leave guarded empty |
| Secrets in code | Use .env variables |
