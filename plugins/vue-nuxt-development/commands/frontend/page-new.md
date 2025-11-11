---
description: Create a new Nuxt 4 page with SSR/SSG support and TypeScript
model: claude-sonnet-4-5
---

Create a new Nuxt 4 page following modern conventions and best practices.

## Page Specification

$ARGUMENTS

## Nuxt 4 Page Standards

### 1. **File-Based Routing**

Pages in `pages/` directory automatically create routes:
- `pages/index.vue` → `/`
- `pages/about.vue` → `/about`
- `pages/users/[id].vue` → `/users/:id`
- `pages/blog/[...slug].vue` → `/blog/*` (catch-all)

### 2. **Page Component Structure**

```vue
<script setup lang="ts">
// Page metadata
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
  pageTransition: { name: 'fade' }
})

// SEO with useHead
useHead({
  title: 'Page Title',
  meta: [
    { name: 'description', content: 'Page description' }
  ]
})

// Data fetching with useFetch or useAsyncData
const { data, error, pending } = await useFetch('/api/data')

// Or with useAsyncData for more control
const { data: posts } = await useAsyncData('posts', () =>
  $fetch('/api/posts')
)
</script>

<template>
  <div>
    <h1>Page Content</h1>
    <div v-if="pending">Loading...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <div v-else>
      <!-- Page content -->
    </div>
  </div>
</template>
```

### 3. **Data Fetching Patterns**

**SSR Data Fetching** (runs on server)
```ts
const { data } = await useFetch('/api/endpoint', {
  key: 'unique-key',
  server: true,
  lazy: false
})
```

**Client-Side Only**
```ts
const { data } = await useFetch('/api/endpoint', {
  server: false
})
```

**Lazy Loading** (doesn't block navigation)
```ts
const { data, pending } = await useFetch('/api/endpoint', {
  lazy: true
})
```

**With Parameters**
```ts
const route = useRoute()
const { data } = await useFetch(`/api/posts/${route.params.id}`)
```

### 4. **Dynamic Routes**

**Single Parameter** `pages/users/[id].vue`
```vue
<script setup lang="ts">
const route = useRoute()
const userId = computed(() => route.params.id as string)

const { data: user } = await useFetch(`/api/users/${userId.value}`)
</script>
```

**Catch-All** `pages/blog/[...slug].vue`
```vue
<script setup lang="ts">
const route = useRoute()
const slug = computed(() => (route.params.slug as string[]).join('/'))
</script>
```

### 5. **Page Metadata with `definePageMeta`**

```ts
definePageMeta({
  // Layout
  layout: 'custom-layout',

  // Middleware (auth, guest, etc.)
  middleware: ['auth', 'admin'],

  // Custom properties
  requiresAuth: true,
  roles: ['admin'],

  // Transitions
  pageTransition: {
    name: 'slide',
    mode: 'out-in'
  },

  // Validate route params
  validate: async (route) => {
    return /^\d+$/.test(route.params.id as string)
  }
})
```

### 6. **SEO with `useHead` / `useSeoMeta`**

```ts
// Basic SEO
useHead({
  title: 'Page Title',
  meta: [
    { name: 'description', content: 'Description' },
    { property: 'og:title', content: 'OG Title' },
    { property: 'og:description', content: 'OG Description' }
  ]
})

// Or use useSeoMeta for better DX
useSeoMeta({
  title: 'Page Title',
  description: 'Description',
  ogTitle: 'OG Title',
  ogDescription: 'OG Description',
  ogImage: '/og-image.jpg',
  twitterCard: 'summary_large_image'
})
```

### 7. **Error Handling**

```vue
<script setup lang="ts">
const { data, error } = await useFetch('/api/data')

if (error.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Data not found',
    fatal: true
  })
}
</script>
```

### 8. **Loading States**

```vue
<template>
  <div>
    <NuxtLoadingIndicator />

    <div v-if="pending">
      <SkeletonLoader />
    </div>

    <div v-else-if="error">
      <ErrorDisplay :error="error" />
    </div>

    <div v-else>
      <!-- Content -->
    </div>
  </div>
</template>
```

### 9. **TypeScript Types**

```ts
interface PageData {
  id: number
  title: string
  content: string
}

interface PageParams {
  id: string
}

// Typed fetch
const { data } = await useFetch<PageData>('/api/data')
```

## Code Quality Standards

**Page Design**
- ✓ Clear data fetching strategy (SSR/CSR)
- ✓ Proper error handling
- ✓ Loading states
- ✓ SEO metadata
- ✓ TypeScript types

**Performance**
- ✓ Use `lazy: true` for non-critical data
- ✓ Optimize images with `<NuxtImg>`
- ✓ Code splitting with `defineAsyncComponent`
- ✓ Proper caching strategies

**Accessibility**
- ✓ Semantic HTML
- ✓ Proper heading hierarchy
- ✓ Skip to content links
- ✓ Focus management

**SEO**
- ✓ Title and meta tags
- ✓ Open Graph tags
- ✓ Structured data where relevant
- ✓ Canonical URLs

Generate production-ready, SEO-friendly Nuxt 4 pages with proper SSR/SSG support.
