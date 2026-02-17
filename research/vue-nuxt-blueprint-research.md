# Vue 3 / Nuxt 3-4 Blueprint Best Practices Research

> Compiled from community best practices, official documentation, and developer blog posts (February 2026)

## Table of Contents

1. [Architecture Tiers and Planning](#1-architecture-tiers)
2. [Directory Structure Patterns](#2-directory-structure)
3. [Component Design Decision Tree](#3-component-decision-tree)
4. [Nuxt Module and Layers Patterns](#4-modules-and-layers)
5. [State Management: Pinia Patterns](#5-pinia-patterns)
6. [SSR vs CSR vs Hybrid Rendering](#6-rendering-decisions)
7. [TypeScript Integration Patterns](#7-typescript-patterns)
8. [Testing Strategy Patterns](#8-testing-strategy)
9. [API Layer Design](#9-api-layer)
10. [Performance Optimization](#10-performance)
11. [Authentication and Middleware](#11-auth-and-middleware)
12. [Deployment Strategies](#12-deployment)

---

## 1. Architecture Tiers and Planning

| Approach | Best For | Scalability | Team Size |
|----------|----------|-------------|-----------|
| **Flat Structure** | Small projects, PoCs | Low | Solo / 1-2 devs |
| **Atomic Design** | Medium projects needing component reuse | High | 3-8 devs |
| **Modular (Feature-Based)** | Growing projects preparing for scale | High | 5-15 devs |
| **Feature-Sliced Design** | Complex, long-term business apps | Very High | 10+ devs |
| **Micro Frontends** | Enterprise with multiple independent teams | Very High | Multiple teams |

**Key principle**: Choose the simplest structure that meets current needs, with room to grow.

Sources:
- [How to Structure Vue Projects - alexop.dev](https://alexop.dev/posts/how-to-structure-vue-projects/)
- [Vue 3 Blueprint for Medium-Sized Applications](https://medium.com/@mohandabdiche/building-efficient-frontends-a-vue-3-blueprint-for-modern-medium-sized-applications-671dd403ca62)

---

## 2. Directory Structure Patterns

### Nuxt 3/4 Standard Structure

```
project-root/
├── app/                    # (Nuxt 4 default) Application source
│   ├── assets/             # Build-processed assets
│   ├── components/         # Auto-imported Vue components
│   ├── composables/        # Auto-imported composable functions
│   ├── layouts/            # Page layout wrappers
│   ├── middleware/          # Route middleware
│   ├── pages/              # File-based routing
│   ├── plugins/            # App-level plugins
│   └── utils/              # Auto-imported utilities
├── layers/                 # Nuxt Layers for modular architecture
├── modules/                # Local Nuxt modules
├── public/                 # Static assets served as-is
├── server/                 # Nitro server
│   ├── api/                # API endpoints (auto-prefixed /api/)
│   ├── middleware/          # Server middleware
│   ├── plugins/            # Server plugins
│   ├── routes/             # Server routes (no /api/ prefix)
│   └── utils/              # Server utilities
├── stores/                 # Pinia stores
├── types/                  # TypeScript type definitions
├── nuxt.config.ts
└── app.config.ts           # Runtime app configuration
```

### Naming Conventions

- **Base components**: `BaseButton.vue`, `BaseTable.vue`
- **Related components**: `TodoList.vue`, `TodoListItem.vue`, `TodoListItemButton.vue`
- **Name word order** (highest-level first): `SearchButtonClear.vue`

Sources:
- [Nuxt Directory Structure (Official)](https://nuxt.com/docs/3.x/directory-structure)
- [Nuxt 4 Upgrade Guide (Official)](https://nuxt.com/docs/4.x/getting-started/upgrade)

---

## 3. Component Design Decision Tree

```
Does it render UI?
├── YES --> Use a COMPONENT
│   └── Base/primitive element? --> Base Component (BaseButton, BaseInput)
│   └── Complex UI block? --> Organism/Widget Component
│   └── Full page? --> Page Component (pages/ directory)
│
└── NO --> Does it manage GLOBAL state?
    ├── YES --> Use a PINIA STORE
    │   └── Shared across many components? --> Pinia Store
    │   └── Needs devtools inspection? --> Pinia Store
    │   └── Requires SSR hydration? --> Pinia Store
    │
    └── NO --> Does it need APP-WIDE availability?
        ├── YES --> Use a PLUGIN
        │   └── Third-party library? --> Plugin
        │   └── Global $api, $analytics? --> Plugin
        │   └── Runs before app mount? --> Plugin
        │
        └── NO --> Use a COMPOSABLE
            └── Reusable logic? --> Composable
            └── Encapsulates reactive state? --> Composable
            └── Wraps browser APIs? --> Composable
```

### Key Distinctions

- **Composables**: `useX()` functions. Each importer gets own reactive instance. Auto-imported in `composables/`.
- **Components**: UI building blocks. Auto-imported in `components/`.
- **Plugins**: App-level initialization, global instances (`$api`), third-party integrations.
- **Pinia Stores**: Centralized global state with devtools support.

Sources:
- [Vue.js Official - Composables](https://vuejs.org/guide/reusability/composables.html)
- [Coding Better Composables - Vue Mastery](https://www.vuemastery.com/blog/coding-better-composables-1-of-5/)

---

## 4. Nuxt Module and Layers Patterns

### Module Best Practices

- **Performance**: Defer heavy logic to Nuxt hooks (>1s setup triggers warnings)
- **Naming/Prefixing**: Components `<FooButton>`, composables `useFooData()`, routes `/api/_foo/`
- **TypeScript**: Develop with TypeScript and expose types
- **ESM**: Use native ES modules exclusively

### Nuxt Layers for Modular Architecture

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  extends: ['./layers/shared', './layers/products', './layers/cart'],
})
```

**When to use layers**:
- Distinct feature boundaries
- Multi-developer teams requiring clear ownership
- Long-term projects expecting 50+ features
- Code reuse across multiple applications

**Enforcement**: Use `eslint-plugin-nuxt-layers` for boundary rules.

Sources:
- [Nuxt Module Best Practices (Official)](https://nuxt.com/docs/3.x/guide/modules/best-practices)
- [Building a Modular Monolith with Nuxt Layers - alexop.dev](https://alexop.dev/posts/nuxt-layers-modular-monolith/)

---

## 5. State Management: Pinia Patterns

### When to Use Stores vs Composables

| Criterion | Pinia Store | Composable |
|-----------|-------------|------------|
| Scope | Global, app-wide | Local, scoped to importing components |
| Shared across unrelated components | Yes | No (each gets own instance) |
| DevTools integration | Full inspection, time-travel | Not built-in |
| SSR hydration | Automatic via `@pinia/nuxt` | Manual |

### Best Practices

1. **Use Setup Store syntax** (Composition API style):
   ```typescript
   export const useCounterStore = defineStore('counter', () => {
     const count = ref(0)
     const doubleCount = computed(() => count.value * 2)
     function increment() { count.value++ }
     return { count, doubleCount, increment }
   })
   ```

2. **Split into domain-specific stores**: `useAuthStore`, `useCartStore`, `useProductStore`
3. **Normalize state**: Avoid deeply nested objects
4. **SSR**: `@pinia/nuxt` handles serialization/hydration automatically

Sources:
- [Pinia Official - Composables](https://pinia.vuejs.org/cookbook/composables.html)
- [Global State Management with Pinia in Nuxt 3 - Vue School](https://vueschool.io/articles/vuejs-tutorials/global-state-management-with-pinia-in-nuxt-3/)

---

## 6. SSR vs CSR vs Hybrid Rendering

### Rendering Mode Decision Matrix

| Mode | SEO | Performance | Data Freshness | Best For |
|------|-----|-------------|----------------|----------|
| **SSR** (Universal) | Excellent | Good | Real-time | Dynamic apps, e-commerce |
| **SSG** (Prerender) | Excellent | Best (CDN) | Build-time only | Blogs, docs, marketing |
| **SPA** (CSR) | Poor | Fast after load | Real-time | Admin panels, internal tools |
| **SWR** | Excellent | Cached + fresh | Background refresh | Content sites |
| **ISR** | Excellent | CDN-cached | Periodic refresh | High-traffic sites |

### Configuration

```typescript
export default defineNuxtConfig({
  ssr: true,
  routeRules: {
    '/':            { prerender: true },     // SSG
    '/blog/**':     { isr: 3600 },           // ISR hourly
    '/admin/**':    { ssr: false },           // SPA
    '/api/**':      { cors: true },           // API
    '/products/**': { swr: 3600 },           // SWR
  },
})
```

### Decision Guide

- **Need SEO?** Use SSR, SSG, or ISR. Never SPA for public content.
- **Content rarely changes?** SSG for maximum performance.
- **Real-time data?** SSR.
- **Admin/internal tools?** SPA (`ssr: false`).

Sources:
- [Rendering Strategies with Nuxt 3 - Medium](https://medium.com/@enestalayy/rendering-strategies-with-nuxt-3-a4b29c5ba7c9)
- [Comparing Nuxt 3 Rendering Modes - RisingStack](https://blog.risingstack.com/nuxt-3-rendering-modes/)

---

## 7. TypeScript Integration Patterns

### Component Props (Vue 3.4+)

```typescript
<script setup lang="ts">
const { msg = 'hello', labels = ['one', 'two'] } = defineProps<{
  msg?: string
  labels?: string[]
}>()
</script>
```

### Component Emits (Vue 3.3+)

```typescript
<script setup lang="ts">
const emit = defineEmits<{
  change: [id: number]
  update: [value: string]
}>()
</script>
```

### Provide/Inject

```typescript
import type { InjectionKey } from 'vue'
const key = Symbol() as InjectionKey<string>
provide(key, 'value')
const value = inject(key) // type: string | undefined
```

### Template Refs (Vue 3.5+)

```typescript
const el = useTemplateRef<HTMLInputElement>('el')
```

### Best Practices

1. Use type-based declaration for `defineProps` and `defineEmits`
2. Be consistent: do not mix declaration styles
3. Run `vue-tsc --noEmit` in CI
4. Define shared interfaces in `types/` directory
5. Leverage Nuxt's auto-generated types

Sources:
- [Vue.js Official - TypeScript with Composition API](https://vuejs.org/guide/typescript/composition-api)
- [Nuxt TypeScript Concepts (Official)](https://nuxt.com/docs/3.x/guide/concepts/typescript)

---

## 8. Testing Strategy Patterns

### Inverted Testing Pyramid

| Layer | Percentage | Tool | Purpose |
|-------|-----------|------|---------|
| **Integration Tests** | ~70% | Vitest browser mode | User flows, component interactions |
| **Composable/Unit Tests** | ~20% | Vitest (Node) | Business logic, utilities |
| **A11y + Visual Tests** | ~10% | axe-core, screenshots | WCAG compliance |

### Test Organization

```
test/
├── unit/           # Node environment, fast
├── nuxt/           # Nuxt runtime environment
└── e2e/            # Playwright, full browser
```

### Key Nuxt Testing Utilities

- **`mountSuspended`**: Mount components in Nuxt environment
- **`renderSuspended`**: Testing Library patterns
- **`mockNuxtImport`**: Mock auto-imports
- **`mockComponent`**: Mock components
- **`registerEndpoint`**: Mock Nitro API endpoints

Sources:
- [Nuxt Testing Guide (Official)](https://nuxt.com/docs/3.x/getting-started/testing)
- [Vue 3 Testing Pyramid - alexop.dev](https://alexop.dev/posts/vue3_testing_pyramid_vitest_browser_mode/)

---

## 9. API Layer Design

### The Three Fetching Tools

| Tool | When to Use | SSR Safe | Auto-Dedup |
|------|------------|----------|------------|
| **`useFetch`** | Initial page data | Yes | Yes |
| **`useAsyncData`** | Custom async logic, SDKs | Yes | Yes |
| **`$fetch`** | Event handlers (form submit, clicks) | No (alone) | No |

**Critical**: Never use bare `$fetch` for initial page data in SSR -- causes double-fetching.

### Repository Pattern (Recommended for Scale)

```typescript
// repository/modules/auth.ts
class AuthModule extends HttpFactory {
  async login(credentials: ILoginInput): Promise<ILoginResponse> {
    return this.call<ILoginResponse>('POST', '/auth/login', credentials)
  }
}

// plugins/api.ts
export default defineNuxtPlugin((nuxtApp) => {
  const apiFetcher = $fetch.create({ baseURL: nuxtApp.$config.API_BASE_URL })
  return { provide: { api: { auth: new AuthModule(apiFetcher) } } }
})
```

### Server API Routes (Nitro/H3)

```typescript
// server/api/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  return { user: await fetchUser(id) }
})
```

- HTTP method suffixes: `.get.ts`, `.post.ts`, `.put.ts`, `.delete.ts`
- Use `defineCachedEventHandler()` for server-side caching
- `event.waitUntil()` for background tasks

Sources:
- [Nuxt Data Fetching (Official)](https://nuxt.com/docs/3.x/getting-started/data-fetching)
- [API Management in Nuxt 3 with TypeScript - Vue Mastery](https://www.vuemastery.com/blog/api-management-in-nuxt-3-with-typescript/)

---

## 10. Performance Optimization

### Built-in Nuxt Optimizations

1. **Automatic code-splitting**: Every route split by default
2. **Lazy components**: `<LazyHeavyChart />`
3. **Lazy hydration** (Nuxt 3.16+): `<LazyComponent hydrate-on-visible />`
4. **NuxtLink prefetching**: Auto-prefetch when visible
5. **useFetch deduplication**: No re-fetch on hydration
6. **Payload optimization**: `pick` option for needed fields only

### Performance Checklist

**Code and Assets**
- Use `nuxt analyze` to visualize bundles
- Import specific functions: `import isNull from 'lodash/isNull'`
- Tree-shakeable libraries only

**Images**
- Use `<NuxtImg>` for automatic optimization
- Serve WebP/AVIF formats
- Set explicit `width`/`height` to reduce CLS

**Reactivity**
- Use `shallowRef` for large objects
- Apply `v-memo` for expensive list rendering
- Use `v-once` for static content

**Web Vitals Targets**
- LCP: Image optimization, preloading critical assets
- CLS: Font fallback metrics, explicit dimensions
- INP: Efficient script loading, reduced hydration blocking

Sources:
- [Nuxt Performance Best Practices (Official)](https://nuxt.com/docs/3.x/guide/best-practices/performance)
- [Vue and Nuxt Performance Optimization Checklist - Alokai](https://alokai.com/blog/vue-and-nuxt-performance-optimization-checklist)

---

## 11. Authentication and Middleware

### Middleware Types

| Type | Definition | Scope |
|------|-----------|-------|
| **Named** | `middleware/auth.ts` | Per-page via `definePageMeta` |
| **Inline** | In `definePageMeta` | Single page |
| **Global** | `middleware/auth.global.ts` | Every route |

### Authentication Approaches

| Approach | Complexity | Best For |
|----------|-----------|----------|
| Nuxt Auth Utils | Low | Simple auth, OAuth |
| @sidebase/nuxt-auth | Medium | Production apps, JWT |
| Custom | High | Unique requirements |

### Navigation Control

```typescript
export default defineNuxtRouteMiddleware((to, from) => {
  const { loggedIn } = useUserSession()
  if (!loggedIn.value && to.path !== '/login') {
    return navigateTo('/login')
  }
})
```

Sources:
- [Minimalist Nuxt Authentication - Vue Mastery](https://www.vuemastery.com/blog/minimalist-nuxt-authentication/)
- [Nuxt Auth (sidebase)](https://auth.sidebase.io/guide/getting-started/introduction)

---

## 12. Deployment Strategies

### Platform Decision Matrix

| Platform | Best For | Edge Support | Zero-Config |
|----------|----------|--------------|-------------|
| **Vercel** | Full SSR + ISR | Yes | Yes |
| **Netlify** | SSG + SSR | Yes | Yes |
| **Cloudflare Workers** | Edge-first | Native | Preset needed |
| **Node.js Server** | Full control | No | Manual |

### Configuration

```typescript
export default defineNuxtConfig({
  nitro: { preset: 'vercel' }           // or 'netlify', 'cloudflare', 'node-server'
})
```

Sources:
- [Deploy Nuxt to Vercel (Official)](https://nuxt.com/deploy/vercel)
- [Nuxt on the Edge (Official Blog)](https://nuxt.com/blog/nuxt-on-the-edge)

---

## Blueprint Planning Checklist

1. **Architecture tier**: Flat, Atomic, Modular, Feature-Sliced, or Micro Frontend?
2. **Rendering strategy**: SSR, SSG, SPA, or Hybrid? Configure `routeRules`.
3. **Directory structure**: Nuxt 4 `app/` convention? Feature-based grouping?
4. **TypeScript**: Strict mode, type-based macros, `vue-tsc` in CI.
5. **State management**: Pinia stores vs composables vs local state?
6. **API layer**: Repository pattern? `useFetch` vs `useAsyncData` vs `$fetch`?
7. **Authentication**: Nuxt Auth Utils, @sidebase/nuxt-auth, or custom?
8. **Middleware plan**: Which routes need guards? Global vs named?
9. **Module strategy**: Which modules? Custom modules? Nuxt Layers?
10. **Testing strategy**: Inverted pyramid (70/20/10).
11. **Performance budget**: Lazy components, image optimization, bundle analysis.
12. **Deployment target**: Vercel, Netlify, Cloudflare, or Node server?
