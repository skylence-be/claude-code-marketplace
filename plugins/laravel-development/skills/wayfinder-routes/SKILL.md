---
name: wayfinder-routes
description: Laravel Wayfinder type-safe route generation for frontend code. Auto-generates TypeScript route functions from Laravel routes for tree-shakeable, type-safe URL building in Inertia, Vue, and React apps. Use when bridging backend routes to frontend code.
category: laravel
tags: [wayfinder, routes, typescript, type-safe, inertia, frontend]
related_skills: [laravel-api-design, inertia-patterns, typescript-vue-patterns]
---

# Wayfinder Type-Safe Routes

Laravel Wayfinder auto-generates TypeScript functions from your Laravel routes, giving frontend code type-safe URL building with tree-shaking support.

## When to Use This Skill

- Referencing Laravel routes from frontend JavaScript/TypeScript
- Building type-safe URLs in Inertia, Vue, or React components
- Replacing hardcoded URL strings in frontend code
- Setting up Wayfinder in a new project

## How It Works

After code changes, Wayfinder generates TypeScript files that mirror your Laravel routes:

```bash
# Regenerate route functions after changes
php artisan wayfinder:generate
```

## Import Patterns

**Always use named imports** for tree-shaking:

```typescript
// Good — tree-shakeable
import { index, show } from '@actions/App/Http/Controllers/PostController';

// Avoid — imports everything
import PostController from '@actions/App/Http/Controllers/PostController';
```

## Route Methods

Each generated function provides these methods:

```typescript
import { show } from '@actions/App/Http/Controllers/PostController';

// Get the URL string
show.url({ post: 1 })          // "/posts/1"

// Make a GET request (Inertia visit)
show.get({ post: 1 })

// Make a POST request
store.post({ title: 'Hello' })

// Get a form helper (Inertia useForm)
const form = store.form({ title: '', body: '' })
```

## Query Parameters

Pass query parameters as a second argument:

```typescript
import { index } from '@actions/App/Http/Controllers/PostController';

index.url({}, { page: 2, sort: 'title' })
// "/posts?page=2&sort=title"
```

## Inertia Integration

### With Links

```vue
<script setup lang="ts">
import { show } from '@actions/App/Http/Controllers/PostController';
</script>

<template>
  <Link :href="show.url({ post: post.id })">
    {{ post.title }}
  </Link>
</template>
```

### With Forms

```vue
<script setup lang="ts">
import { store } from '@actions/App/Http/Controllers/PostController';

const form = store.form({
    title: '',
    body: '',
});

const submit = () => form.post();
</script>
```

### With Router

```typescript
import { show } from '@actions/App/Http/Controllers/PostController';
import { router } from '@inertiajs/vue3';

router.visit(show.url({ post: 1 }));
```

## Common Pitfalls

- Using default imports instead of named imports (breaks tree-shaking)
- Forgetting to run `php artisan wayfinder:generate` after adding/changing routes
- Hardcoding URL strings instead of using generated route functions
- Not including route parameters when the route requires them (TypeScript will catch this)
