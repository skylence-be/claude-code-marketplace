---
name: inertia-patterns
description: Inertia.js v2 patterns for Laravel + Vue/React SPAs including deferred props, infinite scroll with WhenVisible, polling with usePoll, prefetching, useForm composable, and client-side navigation with Link. Use when building Inertia apps or upgrading from v1 to v2.
category: frontend
tags: [inertia, vue, react, spa, laravel, deferred-props, polling]
related_skills: [vue3-composition-api-patterns, pinia-state-patterns, nuxt4-ssr-optimization]
---

# Inertia.js v2 Patterns

Inertia creates fully client-side rendered SPAs without modern SPA complexity, leveraging existing Laravel server-side patterns. Components live in `resources/js/Pages/` and are rendered via `Inertia::render()`.

## When to Use This Skill

- Building Inertia v2 apps with Vue or React
- Using deferred props for performance
- Implementing infinite scroll with `WhenVisible`
- Adding real-time polling with `usePoll`
- Working with `useForm` for form handling
- Upgrading from Inertia v1 to v2

## Server-Side (Laravel)

### Rendering Pages

```php
use Inertia\Inertia;

class PostController extends Controller
{
    public function show(Post $post)
    {
        return Inertia::render('Posts/Show', [
            'post' => $post->load('author'),
            'comments' => fn () => $post->comments()->paginate(10),
        ]);
    }
}
```

### Deferred Props (v2)

Props wrapped in `Inertia::defer()` load asynchronously after the initial page render:

```php
return Inertia::render('Dashboard', [
    'user' => $user,
    // These load after the page is visible
    'stats' => Inertia::defer(fn () => $this->calculateStats()),
    'notifications' => Inertia::defer(fn () => $user->unreadNotifications),
]);
```

**Important:** When using deferred props, add an empty state with a pulsing or animated skeleton on the frontend.

## Client-Side (Vue)

### Navigation with Link

```vue
<script setup>
import { Link } from '@inertiajs/vue3';
</script>

<template>
  <Link href="/posts" class="text-blue-600">All Posts</Link>
  <Link :href="`/posts/${post.id}`" method="delete" as="button">Delete</Link>
</template>
```

### Prefetching (v2)

```vue
<!-- Prefetch on hover for instant navigation -->
<Link href="/posts" prefetch>All Posts</Link>

<!-- Prefetch with stale-while-revalidate -->
<Link href="/posts" prefetch cacheFor="30s">All Posts</Link>
```

### Deferred Props in Components

```vue
<script setup>
import { Deferred } from '@inertiajs/vue3';

defineProps({
    user: Object,
    stats: Object,       // Deferred — may be null initially
    notifications: Array, // Deferred — may be null initially
});
</script>

<template>
  <h1>{{ user.name }}</h1>

  <!-- Shows skeleton while loading -->
  <Deferred data="stats">
    <template #fallback>
      <div class="animate-pulse h-20 bg-gray-200 rounded" />
    </template>
    <StatsPanel :stats="stats" />
  </Deferred>
</template>
```

### Infinite Scroll with WhenVisible (v2)

```vue
<script setup>
import { WhenVisible } from '@inertiajs/vue3';

defineProps({
    posts: Object, // Paginated
});
</script>

<template>
  <div v-for="post in posts.data" :key="post.id">
    {{ post.title }}
  </div>

  <!-- Load more when this element becomes visible -->
  <WhenVisible
    :data="['posts']"
    :params="{ page: posts.current_page + 1 }"
    v-if="posts.next_page_url"
  >
    <template #fallback>
      <div class="animate-pulse">Loading more...</div>
    </template>
  </WhenVisible>
</template>
```

### Polling with usePoll (v2)

```vue
<script setup>
import { usePoll } from '@inertiajs/vue3';

defineProps({ notifications: Array });

// Refresh notifications every 15 seconds
usePoll(15000, { only: ['notifications'] });

// With visibility control — pause when tab is hidden
usePoll(15000, {
    only: ['notifications'],
    keepAlive: false, // Stop polling when tab is hidden
});
</script>
```

### Forms with useForm

```vue
<script setup>
import { useForm } from '@inertiajs/vue3';

const form = useForm({
    title: '',
    body: '',
    published: false,
});

const submit = () => {
    form.post('/posts', {
        onSuccess: () => form.reset(),
    });
};
</script>

<template>
  <form @submit.prevent="submit">
    <input v-model="form.title" />
    <div v-if="form.errors.title" class="text-red-500">{{ form.errors.title }}</div>

    <textarea v-model="form.body" />

    <button :disabled="form.processing">
      {{ form.processing ? 'Saving...' : 'Save' }}
    </button>
  </form>
</template>
```

### Form Reset Props (v2)

```vue
<script setup>
import { useForm } from '@inertiajs/vue3';

const form = useForm({
    title: props.post.title,
    body: props.post.body,
});

// Reset to current values (not initial)
form.defaults({ title: props.post.title, body: props.post.body });
</script>
```

## v1 → v2 Key Differences

| Feature | v1 | v2 |
|---------|----|----|
| Deferred props | Not available | `Inertia::defer()` + `<Deferred>` |
| Infinite scroll | Manual implementation | `<WhenVisible>` component |
| Polling | Not available | `usePoll()` composable |
| Prefetching | Not available | `<Link prefetch>` |
| Lazy props | `Inertia::lazy()` | Still supported, but `defer` is preferred |

**Do not use v2 features in v1 projects:** deferred props, `WhenVisible`, `usePoll`, and prefetching are v2-only.

## Common Pitfalls

- Using deferred props without a loading skeleton (bad UX — content jumps)
- Using `usePoll` with too short an interval (< 5s causes server load)
- Forgetting `keepAlive: false` on polls (continues polling in background tabs)
- Using v2 features (`defer`, `WhenVisible`, `usePoll`) in a v1 project
- Not wrapping closures in server-side props (causes eager evaluation)
