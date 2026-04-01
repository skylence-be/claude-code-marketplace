---
name: folio-routing
description: Laravel Folio file-based routing patterns including page creation, route parameters, model binding, named routes, middleware, and render hooks. Use when creating Folio pages, debugging 404s, or choosing between Folio and traditional routing.
category: laravel
tags: [folio, routing, file-based, pages, blade]
related_skills: [laravel-blueprint, laravel-security-patterns]
---

# Folio File-Based Routing

Laravel Folio is a file-based router that automatically creates routes from Blade templates in the `resources/views/pages/` directory.

## When to Use This Skill

- Creating new pages in a Folio-enabled project
- Setting up route parameters and model binding via filenames
- Defining named routes and middleware on Folio pages
- Debugging Folio 404 errors
- Choosing between Folio and `routes/web.php` for a new page

## File Structure → Routes

The directory structure determines routes automatically:

| File Path | Route |
|-----------|-------|
| `pages/index.blade.php` | `/` |
| `pages/about.blade.php` | `/about` |
| `pages/profile/index.blade.php` | `/profile` |
| `pages/auth/login.blade.php` | `/auth/login` |
| `pages/users/[id].blade.php` | `/users/{id}` |
| `pages/users/[User].blade.php` | `/users/{user}` (model binding) |

## Creating Pages

```bash
# Basic page
php artisan folio:page "products"
# → resources/views/pages/products.blade.php → /products

# With route parameter
php artisan folio:page "products/[id]"
# → resources/views/pages/products/[id].blade.php → /products/{id}

# With model binding
php artisan folio:page "users/[User]"
# → resources/views/pages/users/[User].blade.php → /users/{user}
```

## Route Parameters vs Model Binding

The filename token determines behavior:

| Token | Type | Variable |
|-------|------|----------|
| `[id]` | Plain string parameter | `$id` |
| `[User]` | Eloquent model binding (by ID) | `$user` |
| `[Post:slug]` | Model binding by custom key | `$post` |

**Case-sensitive:** `[User]` binds a User model, `[user]` is a plain string parameter.

```blade
{{-- pages/users/[id].blade.php — plain parameter --}}
<div>User ID: {{ $id }}</div>

{{-- pages/users/[User].blade.php — model binding --}}
<div>User: {{ $user->name }}</div>

{{-- pages/posts/[Post:slug].blade.php — custom key --}}
<div>Post: {{ $post->title }}</div>
```

## Named Routes

Add a `name` call at the top of each page for referencing elsewhere:

```php
<?php
use function Laravel\Folio\name;

name('products.index');
?>
```

## Middleware

```php
<?php
use function Laravel\Folio\{name, middleware};

name('admin.products');
middleware(['auth', 'verified']);
?>
```

## Render Hooks

Use `render()` to pass additional data to the view:

```php
<?php
use App\Models\Post;
use Illuminate\View\View;
use function Laravel\Folio\render;

render(function (View $view, Post $post) {
    return $view->with('photos', $post->author->photos);
});
?>
```

## Inline Queries

Folio pages can include data-loading logic directly:

```blade
@php
use App\Models\Post;

$posts = Post::query()
    ->whereNotNull('published_at')
    ->latest('published_at')
    ->get();
@endphp

<ul>
    @foreach ($posts as $post)
        <li>{{ $post->title }}</li>
    @endforeach
</ul>
```

## Listing Routes

```bash
php artisan folio:list
```

## 404 Debug Checklist

1. Run `php artisan folio:list` — is the route listed?
2. Verify Folio is mounted (`folio:install` + provider registration, or `Folio::path(...)`)
3. Confirm pages are under the mounted path (`resources/views/pages/`)
4. Check filename-to-route mapping (`index.blade.php`, `[id]` vs `[Model]`)
5. Verify model binding case sensitivity (`[User]` not `[user]`)

## When to Use Folio vs routes/web.php

| Use Folio | Use routes/web.php |
|-----------|-------------------|
| Content pages (about, contact, FAQ) | API endpoints |
| Blog posts, product pages | Complex middleware chains |
| Simple CRUD with model binding | Routes needing controller logic |
| Marketing/landing pages | Routes with multiple HTTP methods |

## Common Pitfalls

- Using `[user]` when model binding requires `[User]` (case-sensitive)
- Forgetting to add named routes to new pages
- Creating routes in `routes/web.php` when Folio handles the page
- Not running `folio:list` to verify route registration
