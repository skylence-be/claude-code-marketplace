---
name: nuxt4-ssr-optimization
description: Master Nuxt 4 server-side rendering including data fetching (useAsyncData, useFetch), route middleware, server routes, Nitro optimization, caching strategies, SEO, and performance monitoring. Use when building SSR applications, optimizing Core Web Vitals, or implementing edge rendering.
category: frontend
tags: [nuxt4, ssr, performance, seo, nitro, edge]
related_skills: [vue3-composition-api-patterns, nuxt-modules-integration, vitest-testing-patterns]
---

# Nuxt 4 SSR Optimization

Comprehensive guide to server-side rendering optimization in Nuxt 4, covering data fetching strategies, server routes, Nitro engine configuration, caching patterns, SEO optimization, performance monitoring, and deployment strategies for high-performance applications.

## When to Use This Skill

- Building server-side rendered applications with Nuxt 4
- Implementing efficient data fetching with useAsyncData and useFetch
- Creating protected routes with server and route middleware
- Building API endpoints with Nuxt server routes
- Optimizing application performance with caching strategies
- Implementing SEO-friendly meta tags and structured data
- Monitoring Core Web Vitals and performance metrics
- Configuring Nitro server for optimal performance
- Implementing static site generation (SSG) for specific routes
- Deploying to edge networks for global performance

## Core Concepts

### 1. Data Fetching
- **useAsyncData()**: Fetch data with SSR support and caching
- **useFetch()**: Simplified data fetching with automatic URL handling
- **useLazyFetch()**: Client-side lazy loading after hydration
- **useLazyAsyncData()**: Lazy version of useAsyncData
- **$fetch**: Universal fetch with server/client isomorphic support

### 2. Rendering Modes
- **SSR (Server-Side Rendering)**: Render on server for each request
- **SSG (Static Site Generation)**: Pre-render at build time
- **CSR (Client-Side Rendering)**: Render only on client
- **Hybrid Rendering**: Mix SSR, SSG, and CSR per route
- **Edge Rendering**: Render at CDN edge for global performance

### 3. Route Middleware
- **Anonymous middleware**: Inline route protection
- **Named middleware**: Reusable middleware functions
- **Global middleware**: Applied to all routes
- **Server middleware**: Runs on Nitro server for all requests

### 4. Nitro Server Engine
- Hot module replacement in development
- Universal JavaScript runtime (Node.js, Deno, Workers)
- Built-in caching with multiple storage layers
- API routes with file-based routing
- Server plugins for extension

### 5. Caching Strategies
- **Route rules**: Per-route caching configuration
- **Payload extraction**: Cache rendered HTML
- **Data caching**: Cache API responses
- **CDN caching**: Browser and proxy caching
- **SWR (Stale-While-Revalidate)**: Background updates

## Quick Start

```vue
<script setup lang="ts">
// Simple data fetching with SSR
const { data: user } = await useFetch('/api/user')

// With options
const { data: posts, pending, error, refresh } = await useFetch('/api/posts', {
  query: { limit: 10 },
  lazy: false
})

// SEO optimization
useSeoMeta({
  title: 'My Page',
  description: 'Page description',
  ogImage: '/og-image.jpg'
})
</script>

<template>
  <div>
    <h1>Welcome {{ user?.name }}</h1>

    <div v-if="pending">Loading...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <ul v-else>
      <li v-for="post in posts" :key="post.id">
        {{ post.title }}
      </li>
    </ul>
  </div>
</template>
```

## Fundamental Patterns

### Pattern 1: Data Fetching with useAsyncData

```vue
<script setup lang="ts">
import type { Post } from '@/types'

// Basic useAsyncData
const { data: posts, pending, error, refresh } = await useAsyncData(
  'posts', // Unique key for deduplication
  () => $fetch<Post[]>('/api/posts')
)

// With transform
const { data: formattedPosts } = await useAsyncData(
  'posts-formatted',
  () => $fetch<Post[]>('/api/posts'),
  {
    transform: (posts) => {
      return posts.map(post => ({
        ...post,
        formattedDate: new Date(post.createdAt).toLocaleDateString()
      }))
    }
  }
)

// With reactive parameters
const page = ref(1)
const limit = ref(10)

const { data: paginatedPosts, refresh: refreshPosts } = await useAsyncData(
  'posts-paginated',
  () => $fetch<Post[]>('/api/posts', {
    query: {
      page: page.value,
      limit: limit.value
    }
  }),
  {
    // Re-fetch when dependencies change
    watch: [page, limit]
  }
)

// Lazy loading (doesn't block navigation)
const { data: comments, pending: loadingComments } = await useAsyncData(
  'comments',
  () => $fetch('/api/comments'),
  {
    lazy: true, // Don't block during SSR
    server: false // Only fetch on client
  }
)

// Pick specific fields from response
const { data: userData } = await useAsyncData(
  'user-data',
  () => $fetch('/api/user'),
  {
    pick: ['id', 'name', 'email'] // Only these fields in state
  }
)

// Default value while loading
const { data: settings } = await useAsyncData(
  'settings',
  () => $fetch('/api/settings'),
  {
    default: () => ({
      theme: 'light',
      notifications: true
    })
  }
)

// Manual refresh
const loadMorePosts = () => {
  page.value++
  refreshPosts()
}

// Conditional fetching
const shouldFetch = ref(true)

const { data: conditionalData } = await useAsyncData(
  'conditional',
  () => shouldFetch.value ? $fetch('/api/data') : null,
  {
    watch: [shouldFetch]
  }
)
</script>

<template>
  <div>
    <div v-if="pending">Loading posts...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <div v-else>
      <article v-for="post in posts" :key="post.id">
        <h2>{{ post.title }}</h2>
        <p>{{ post.excerpt }}</p>
      </article>

      <button @click="loadMorePosts" :disabled="loadingComments">
        Load More
      </button>
    </div>
  </div>
</template>
```

### Pattern 2: Simplified Data Fetching with useFetch

```vue
<script setup lang="ts">
import type { User, Post } from '@/types'

// Basic useFetch (wrapper around useAsyncData + $fetch)
const { data: user } = await useFetch<User>('/api/user')

// With query parameters
const searchQuery = ref('')
const category = ref('all')

const { data: posts, pending, error } = await useFetch<Post[]>('/api/posts', {
  query: {
    search: searchQuery,
    category: category
  },
  watch: [searchQuery, category]
})

// With headers (e.g., authentication)
const token = useCookie('auth-token')

const { data: protectedData } = await useFetch('/api/protected', {
  headers: {
    Authorization: `Bearer ${token.value}`
  }
})

// POST request
const createPost = async (postData: Partial<Post>) => {
  const { data, error } = await useFetch('/api/posts', {
    method: 'POST',
    body: postData
  })

  if (error.value) {
    console.error('Failed to create post:', error.value)
    return null
  }

  return data.value
}

// Lazy fetch (client-side only)
const { data: analytics, pending: loadingAnalytics } = useLazyFetch(
  '/api/analytics',
  {
    server: false // Skip during SSR
  }
)

// Computed URL
const userId = ref(1)
const userUrl = computed(() => `/api/users/${userId.value}`)

const { data: selectedUser } = await useFetch(userUrl, {
  watch: [userId]
})

// Interceptors with onRequest/onResponse
const { data: apiData } = await useFetch('/api/data', {
  onRequest({ request, options }) {
    // Modify request before sending
    options.headers = {
      ...options.headers,
      'X-Custom-Header': 'value'
    }
  },
  onResponse({ response }) {
    // Process response
    console.log('Response received:', response.status)
  },
  onResponseError({ response }) {
    // Handle errors
    console.error('Error:', response.status)
  }
})

// Retry on failure
const { data: retryData } = await useFetch('/api/unstable', {
  retry: 3,
  retryDelay: 500
})

// Timeout configuration
const { data: timeoutData } = await useFetch('/api/slow', {
  timeout: 5000 // 5 seconds
})
</script>

<template>
  <div>
    <div v-if="pending">Loading...</div>
    <div v-else-if="error">{{ error.message }}</div>
    <div v-else>
      <h1>{{ user?.name }}</h1>

      <input v-model="searchQuery" placeholder="Search posts">

      <article v-for="post in posts" :key="post.id">
        <h2>{{ post.title }}</h2>
      </article>
    </div>
  </div>
</template>
```

### Pattern 3: Route Middleware

```typescript
// middleware/auth.ts - Named middleware
export default defineNuxtRouteMiddleware((to, from) => {
  const user = useState('user')

  // Redirect to login if not authenticated
  if (!user.value) {
    return navigateTo('/login')
  }

  // Check permissions
  if (to.meta.requiresAdmin && !user.value.isAdmin) {
    return abortNavigation('Unauthorized')
  }
})

// middleware/logging.global.ts - Global middleware
export default defineNuxtRouteMiddleware((to, from) => {
  console.log(`Navigating from ${from.path} to ${to.path}`)

  // Track page views
  if (process.client) {
    // Analytics tracking
    trackPageView(to.path)
  }
})

// middleware/redirect.ts - Redirect middleware
export default defineNuxtRouteMiddleware((to) => {
  // Redirect old URLs
  const redirects: Record<string, string> = {
    '/old-path': '/new-path',
    '/blog': '/articles'
  }

  if (to.path in redirects) {
    return navigateTo(redirects[to.path], { redirectCode: 301 })
  }
})

// middleware/locale.global.ts - Locale detection
export default defineNuxtRouteMiddleware((to) => {
  const locale = useCookie('locale')

  if (!locale.value) {
    // Detect from browser
    const browserLocale = process.client
      ? navigator.language.split('-')[0]
      : 'en'

    locale.value = browserLocale
  }

  // Set i18n locale
  const { locale: i18nLocale } = useI18n()
  i18nLocale.value = locale.value
})
```

```vue
<!-- pages/dashboard.vue - Using middleware in page -->
<script setup lang="ts">
// Apply specific middleware to this page
definePageMeta({
  middleware: ['auth'],
  requiresAdmin: true // Custom meta for middleware
})

const { data: dashboardData } = await useFetch('/api/dashboard')
</script>

<template>
  <div>
    <h1>Dashboard</h1>
    <p>Welcome to the admin dashboard</p>
  </div>
</template>
```

```vue
<!-- Inline middleware -->
<script setup lang="ts">
definePageMeta({
  middleware: [
    // Anonymous inline middleware
    function (to, from) {
      const user = useState('user')

      if (!user.value?.isVerified) {
        return navigateTo('/verify-email')
      }
    }
  ]
})
</script>
```

### Pattern 4: Server Routes and API Endpoints

```typescript
// server/api/users/index.get.ts - GET /api/users
export default defineEventHandler(async (event) => {
  // Get query parameters
  const query = getQuery(event)
  const page = parseInt(query.page as string) || 1
  const limit = parseInt(query.limit as string) || 10

  // Database query
  const users = await prisma.user.findMany({
    skip: (page - 1) * limit,
    take: limit,
    select: {
      id: true,
      name: true,
      email: true
    }
  })

  const total = await prisma.user.count()

  return {
    data: users,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit)
    }
  }
})

// server/api/users/[id].get.ts - GET /api/users/:id
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')

  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'User ID is required'
    })
  }

  const user = await prisma.user.findUnique({
    where: { id: parseInt(id) }
  })

  if (!user) {
    throw createError({
      statusCode: 404,
      message: 'User not found'
    })
  }

  return user
})

// server/api/users/index.post.ts - POST /api/users
export default defineEventHandler(async (event) => {
  // Get request body
  const body = await readBody(event)

  // Validate
  if (!body.name || !body.email) {
    throw createError({
      statusCode: 400,
      message: 'Name and email are required'
    })
  }

  // Check authentication
  const session = await getServerSession(event)
  if (!session) {
    throw createError({
      statusCode: 401,
      message: 'Unauthorized'
    })
  }

  // Create user
  const user = await prisma.user.create({
    data: {
      name: body.name,
      email: body.email
    }
  })

  // Set response status
  setResponseStatus(event, 201)

  return user
})

// server/api/users/[id].patch.ts - PATCH /api/users/:id
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const body = await readBody(event)

  const user = await prisma.user.update({
    where: { id: parseInt(id!) },
    data: body
  })

  return user
})

// server/api/users/[id].delete.ts - DELETE /api/users/:id
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')

  await prisma.user.delete({
    where: { id: parseInt(id!) }
  })

  setResponseStatus(event, 204)
  return null
})

// server/api/auth/login.post.ts - Authentication endpoint
export default defineEventHandler(async (event) => {
  const { email, password } = await readBody(event)

  // Verify credentials
  const user = await verifyCredentials(email, password)

  if (!user) {
    throw createError({
      statusCode: 401,
      message: 'Invalid credentials'
    })
  }

  // Create session
  const session = await createSession(user.id)

  // Set cookie
  setCookie(event, 'session', session.token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7 // 7 days
  })

  return {
    user: {
      id: user.id,
      name: user.name,
      email: user.email
    }
  }
})

// server/middleware/auth.ts - Server middleware
export default defineEventHandler(async (event) => {
  // Skip auth for public routes
  const publicRoutes = ['/api/auth/login', '/api/auth/register']
  if (publicRoutes.some(route => event.path.startsWith(route))) {
    return
  }

  // Check session
  const sessionToken = getCookie(event, 'session')

  if (!sessionToken) {
    throw createError({
      statusCode: 401,
      message: 'Unauthorized'
    })
  }

  // Verify session and attach user
  const session = await verifySession(sessionToken)

  if (!session) {
    throw createError({
      statusCode: 401,
      message: 'Invalid session'
    })
  }

  // Attach user to event context
  event.context.user = session.user
})
```

### Pattern 5: Caching Strategies with Route Rules

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    // Static pages (SSG at build time)
    '/': { prerender: true },
    '/about': { prerender: true },
    '/privacy': { prerender: true },

    // ISR (Incremental Static Regeneration)
    '/blog/**': {
      swr: 3600, // Cache for 1 hour, revalidate in background
      prerender: true
    },

    // Dynamic SSR with caching
    '/products/**': {
      swr: 60 * 60, // 1 hour
      cache: {
        maxAge: 60 * 60,
        staleMaxAge: 60 * 60 * 24 // Serve stale for 24 hours if revalidating
      }
    },

    // API routes with caching
    '/api/products': {
      cache: {
        maxAge: 60 * 5 // 5 minutes
      }
    },

    // Client-side only (SPA mode)
    '/dashboard/**': { ssr: false },

    // Redirect
    '/old-blog/**': { redirect: '/blog/**' },

    // CORS for API
    '/api/**': {
      cors: true,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    },

    // Security headers
    '/**': {
      headers: {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
      }
    }
  },

  // Nitro caching configuration
  nitro: {
    storage: {
      // Redis cache
      redis: {
        driver: 'redis',
        host: 'localhost',
        port: 6379,
        db: 0
      },
      // File system cache
      cache: {
        driver: 'fs',
        base: './.cache'
      }
    },
    devStorage: {
      cache: {
        driver: 'fs',
        base: './.cache/dev'
      }
    },
    prerender: {
      crawlLinks: true,
      routes: ['/sitemap.xml', '/robots.txt']
    }
  }
})
```

### Pattern 6: SEO Optimization

```vue
<script setup lang="ts">
import type { Post } from '@/types'

const route = useRoute()
const { data: post } = await useFetch<Post>(`/api/posts/${route.params.slug}`)

if (!post.value) {
  throw createError({
    statusCode: 404,
    message: 'Post not found'
  })
}

// Basic SEO meta tags
useSeoMeta({
  title: post.value.title,
  description: post.value.excerpt,
  ogTitle: post.value.title,
  ogDescription: post.value.excerpt,
  ogImage: post.value.image,
  ogUrl: `https://example.com${route.path}`,
  twitterCard: 'summary_large_image',
  twitterTitle: post.value.title,
  twitterDescription: post.value.excerpt,
  twitterImage: post.value.image
})

// Advanced head management
useHead({
  title: post.value.title,
  meta: [
    { name: 'description', content: post.value.excerpt },
    { name: 'author', content: post.value.author.name },
    { name: 'publish-date', content: post.value.publishedAt },
    { property: 'article:published_time', content: post.value.publishedAt },
    { property: 'article:modified_time', content: post.value.updatedAt },
    { property: 'article:author', content: post.value.author.name },
    { property: 'article:section', content: post.value.category }
  ],
  link: [
    { rel: 'canonical', href: `https://example.com${route.path}` }
  ],
  script: [
    // JSON-LD structured data
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: post.value.title,
        description: post.value.excerpt,
        image: post.value.image,
        datePublished: post.value.publishedAt,
        dateModified: post.value.updatedAt,
        author: {
          '@type': 'Person',
          name: post.value.author.name,
          url: `https://example.com/authors/${post.value.author.slug}`
        },
        publisher: {
          '@type': 'Organization',
          name: 'Your Company',
          logo: {
            '@type': 'ImageObject',
            url: 'https://example.com/logo.png'
          }
        },
        mainEntityOfPage: {
          '@type': 'WebPage',
          '@id': `https://example.com${route.path}`
        }
      })
    }
  ]
})

// Dynamic title with suffix
useHead({
  titleTemplate: (title) => {
    return title ? `${title} | My Blog` : 'My Blog'
  }
})

// Server-only head (for performance)
useServerHead({
  link: [
    { rel: 'preconnect', href: 'https://api.example.com' },
    { rel: 'dns-prefetch', href: 'https://cdn.example.com' }
  ]
})
</script>

<template>
  <article>
    <h1>{{ post.title }}</h1>
    <p>{{ post.excerpt }}</p>
    <div v-html="post.content"></div>
  </article>
</template>
```

```typescript
// composables/useSeo.ts - Reusable SEO composable
export function useSeo(options: {
  title: string
  description: string
  image?: string
  type?: 'website' | 'article'
  author?: string
  publishedAt?: string
}) {
  const route = useRoute()
  const config = useRuntimeConfig()
  const baseUrl = config.public.baseUrl || 'https://example.com'
  const fullUrl = `${baseUrl}${route.path}`

  useSeoMeta({
    title: options.title,
    description: options.description,
    ogTitle: options.title,
    ogDescription: options.description,
    ogImage: options.image || `${baseUrl}/og-default.jpg`,
    ogUrl: fullUrl,
    ogType: options.type || 'website',
    twitterCard: 'summary_large_image',
    twitterTitle: options.title,
    twitterDescription: options.description,
    twitterImage: options.image || `${baseUrl}/og-default.jpg`
  })

  if (options.type === 'article' && options.author && options.publishedAt) {
    useHead({
      script: [
        {
          type: 'application/ld+json',
          children: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: options.title,
            description: options.description,
            image: options.image,
            datePublished: options.publishedAt,
            author: {
              '@type': 'Person',
              name: options.author
            }
          })
        }
      ]
    })
  }
}
```

### Pattern 7: Performance Monitoring

```vue
<script setup lang="ts">
import { onMounted } from 'vue'

// Core Web Vitals monitoring
onMounted(() => {
  if (process.client && 'PerformanceObserver' in window) {
    // Largest Contentful Paint (LCP)
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const lastEntry = entries[entries.length - 1]
      console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime)

      // Send to analytics
      trackMetric('LCP', lastEntry.renderTime || lastEntry.loadTime)
    })
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })

    // First Input Delay (FID)
    const fidObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach((entry: any) => {
        console.log('FID:', entry.processingStart - entry.startTime)
        trackMetric('FID', entry.processingStart - entry.startTime)
      })
    })
    fidObserver.observe({ entryTypes: ['first-input'] })

    // Cumulative Layout Shift (CLS)
    let clsScore = 0
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries() as any[]) {
        if (!entry.hadRecentInput) {
          clsScore += entry.value
          console.log('CLS:', clsScore)
        }
      }
    })
    clsObserver.observe({ entryTypes: ['layout-shift'] })

    // Time to First Byte (TTFB)
    const navigationEntry = performance.getEntriesByType('navigation')[0] as any
    if (navigationEntry) {
      const ttfb = navigationEntry.responseStart - navigationEntry.requestStart
      console.log('TTFB:', ttfb)
      trackMetric('TTFB', ttfb)
    }
  }
})

// Custom performance markers
const measureDataFetch = async () => {
  performance.mark('fetch-start')

  const { data } = await useFetch('/api/data')

  performance.mark('fetch-end')
  performance.measure('data-fetch', 'fetch-start', 'fetch-end')

  const measure = performance.getEntriesByName('data-fetch')[0]
  console.log('Data fetch duration:', measure.duration)
  trackMetric('data-fetch-duration', measure.duration)
}

// Track to analytics service
const trackMetric = (name: string, value: number) => {
  // Send to Google Analytics, Plausible, etc.
  if (window.gtag) {
    window.gtag('event', 'web_vitals', {
      event_category: 'Performance',
      event_label: name,
      value: Math.round(value),
      non_interaction: true
    })
  }
}
</script>
```

## Advanced Patterns

### Pattern 8: Hybrid Rendering Strategies

```typescript
// nuxt.config.ts - Per-route rendering configuration
export default defineNuxtConfig({
  routeRules: {
    // Homepage: SSG
    '/': {
      prerender: true
    },

    // Blog posts: ISR with 1-hour revalidation
    '/blog/**': {
      swr: 3600,
      prerender: true
    },

    // Product pages: SSR with cache
    '/products/**': {
      ssr: true,
      cache: {
        maxAge: 300 // 5 minutes
      }
    },

    // Dashboard: CSR only (client-side)
    '/dashboard/**': {
      ssr: false
    },

    // API: Server routes with cache
    '/api/**': {
      cache: {
        maxAge: 60
      }
    }
  },

  // Experimental features
  experimental: {
    payloadExtraction: true, // Extract payload for faster hydration
    renderJsonPayloads: true
  }
})
```

### Pattern 9: State Management Across SSR

```typescript
// composables/useState.ts - SSR-safe state
export const useUser = () => useState<User | null>('user', () => null)

export const useCart = () => useState<CartItem[]>('cart', () => [])

export const useSettings = () => useState('settings', () => ({
  theme: 'light',
  locale: 'en'
}))
```

```vue
<script setup lang="ts">
// Access SSR-safe state
const user = useUser()
const cart = useCart()

// Fetch user on server and client
if (!user.value) {
  const { data } = await useFetch('/api/user')
  user.value = data.value
}

// Client-only operations
onMounted(() => {
  // Restore cart from localStorage
  const savedCart = localStorage.getItem('cart')
  if (savedCart) {
    cart.value = JSON.parse(savedCart)
  }
})

// Watch for changes and persist
watch(cart, (newCart) => {
  if (process.client) {
    localStorage.setItem('cart', JSON.stringify(newCart))
  }
}, { deep: true })
</script>
```

### Pattern 10: Error Handling

```vue
<script setup lang="ts">
// Error handling in data fetching
const { data, error, refresh } = await useFetch('/api/data', {
  onResponseError({ response }) {
    console.error('API Error:', response.status)

    if (response.status === 401) {
      // Redirect to login
      navigateTo('/login')
    } else if (response.status === 403) {
      // Show error message
      showNotification('Access denied', 'error')
    }
  }
})

// Custom error page
if (error.value) {
  throw createError({
    statusCode: error.value.statusCode || 500,
    message: error.value.message || 'An error occurred',
    fatal: true // Show error page
  })
}

// Try-catch for manual error handling
try {
  const result = await $fetch('/api/risky-operation')
  console.log('Success:', result)
} catch (err) {
  console.error('Failed:', err)
  // Handle error gracefully
}
</script>
```

```vue
<!-- error.vue - Custom error page -->
<script setup lang="ts">
const props = defineProps<{
  error: {
    statusCode: number
    message: string
  }
}>()

const handleError = () => clearError({ redirect: '/' })
</script>

<template>
  <div class="error-page">
    <h1>{{ error.statusCode }}</h1>
    <p>{{ error.message }}</p>
    <button @click="handleError">Go Home</button>
  </div>
</template>
```

## Testing Strategies

```typescript
// tests/ssr/data-fetching.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'

describe('SSR Data Fetching', () => {
  it('fetches data on server', async () => {
    const { useFetch } = await import('#app')

    mockNuxtImport('useFetch', () => {
      return vi.fn(() => ({
        data: ref({ id: 1, name: 'Test' }),
        pending: ref(false),
        error: ref(null)
      }))
    })

    const { data } = await useFetch('/api/test')
    expect(data.value).toEqual({ id: 1, name: 'Test' })
  })
})

// tests/e2e/ssr.spec.ts - E2E SSR testing
import { test, expect } from '@playwright/test'

test('page is server-rendered', async ({ page }) => {
  // Disable JavaScript to ensure SSR
  await page.context().route('**/*.js', route => route.abort())

  await page.goto('/')

  // Content should be visible without JavaScript
  await expect(page.locator('h1')).toContainText('Welcome')
})

test('hydration works correctly', async ({ page }) => {
  await page.goto('/')

  // Click should work after hydration
  await page.click('button.increment')
  await expect(page.locator('.count')).toContainText('1')
})
```

## Common Pitfalls

### Pitfall 1: Client-Only Code in SSR

```typescript
// WRONG: Accessing window during SSR
const width = window.innerWidth // Error on server!

// CORRECT: Check if on client
const width = process.client ? window.innerWidth : 0

// CORRECT: Use onMounted
onMounted(() => {
  const width = window.innerWidth
})
```

### Pitfall 2: Not Awaiting Data Fetching

```vue
<!-- WRONG: Not awaiting -->
<script setup>
const { data } = useFetch('/api/data') // Missing await!
</script>

<!-- CORRECT: Await in script setup -->
<script setup>
const { data } = await useFetch('/api/data')
</script>
```

### Pitfall 3: Duplicate Data Fetching

```typescript
// WRONG: Same data fetched multiple times
const { data: user1 } = await useFetch('/api/user')
const { data: user2 } = await useFetch('/api/user') // Duplicate!

// CORRECT: Use same key or share state
const { data: user } = await useFetch('/api/user', { key: 'user' })
```

## Best Practices

1. **Always await data fetching** in script setup for SSR
2. **Use unique keys** in useAsyncData to prevent collisions
3. **Implement proper caching** with route rules for better performance
4. **Add SEO meta tags** using useSeoMeta and useHead
5. **Monitor Core Web Vitals** in production
6. **Handle errors gracefully** with custom error pages
7. **Use server middleware** for authentication and logging
8. **Leverage Nitro caching** for API responses
9. **Implement hybrid rendering** for optimal performance
10. **Test SSR** with JavaScript disabled

## Resources

- **Nuxt 4 Documentation**: https://nuxt.com
- **Nitro Engine**: https://nitro.unjs.io
- **Core Web Vitals**: https://web.dev/vitals
- **Nuxt DevTools**: https://devtools.nuxt.com
- **UnJS Ecosystem**: https://unjs.io
