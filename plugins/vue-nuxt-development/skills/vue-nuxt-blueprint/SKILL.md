---
name: vue-nuxt-blueprint
description: Master Vue/Nuxt Blueprint - the AI planning format for generating accurate, production-ready Vue 3 and Nuxt 3-4 code. Use when planning complex frontend implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: vue-nuxt
tags: [vue3, nuxt, blueprint, ai, planning, architecture, specification]
related_skills: [vue3-composition-api-patterns, pinia-state-patterns, nuxt4-ssr-optimization, nuxt-modules-integration, typescript-vue-patterns, vitest-testing-patterns]
---

# Vue/Nuxt Blueprint

Vue/Nuxt Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Vue 3 and Nuxt 3-4 projects. It bridges the gap between high-level requirements and production-ready code.

## When to Use This Skill

- Planning complex Vue 3 / Nuxt 3-4 application architectures
- Creating detailed specifications before writing code
- Generating comprehensive page, component, and composable architectures
- Documenting user flows, data fetching strategies, and rendering modes
- Ensuring all details are captured (directory structure, types, API layer, state)
- Avoiding vague plans that lead to vague code

## Blueprint Plan Structure

A complete Blueprint includes these sections:

### 1. Overview & Key Decisions

```markdown
# E-Commerce Product Catalog

A Nuxt 4 application for browsing, searching, and purchasing products.

## Key Decisions
- Nuxt 4 with `app/` directory convention
- Hybrid rendering: SSR for product pages (SEO), SPA for checkout/admin
- Pinia for cart and auth state, composables for UI logic
- TypeScript strict mode throughout
- Server API routes for BFF (Backend-for-Frontend) layer
- @nuxtjs/tailwindcss for styling
```

### 2. Architecture Tier

Select the architecture based on project scope:

```markdown
## Architecture

**Tier**: Modular (Feature-Based)
**Justification**: 5+ developer team, 20+ pages, clear feature boundaries

### Directory Structure (Nuxt 4)

project-root/
├── app/
│   ├── assets/
│   │   └── css/
│   │       └── main.css
│   ├── components/
│   │   ├── base/              # BaseButton, BaseInput, BaseModal
│   │   ├── product/           # ProductCard, ProductGrid, ProductFilters
│   │   ├── cart/              # CartDrawer, CartItem, CartSummary
│   │   └── layout/            # AppHeader, AppFooter, AppSidebar
│   ├── composables/
│   │   ├── useProductSearch.ts
│   │   ├── useCartActions.ts
│   │   └── usePagination.ts
│   ├── layouts/
│   │   ├── default.vue
│   │   └── checkout.vue
│   ├── middleware/
│   │   ├── auth.ts
│   │   └── guest.ts
│   ├── pages/
│   │   ├── index.vue
│   │   ├── products/
│   │   │   ├── index.vue
│   │   │   └── [slug].vue
│   │   ├── cart.vue
│   │   ├── checkout.vue
│   │   └── admin/
│   │       └── products/
│   │           ├── index.vue
│   │           └── [id].vue
│   ├── plugins/
│   │   └── api.ts
│   └── utils/
│       ├── formatCurrency.ts
│       └── validators.ts
├── layers/                     # Optional: feature layers
├── modules/                    # Custom Nuxt modules
├── public/
│   └── favicon.ico
├── server/
│   ├── api/
│   │   ├── products/
│   │   │   ├── index.get.ts
│   │   │   └── [id].get.ts
│   │   ├── cart/
│   │   │   ├── index.get.ts
│   │   │   └── index.post.ts
│   │   └── auth/
│   │       ├── login.post.ts
│   │       └── me.get.ts
│   ├── middleware/
│   │   └── auth.ts
│   └── utils/
│       └── db.ts
├── stores/
│   ├── auth.ts
│   ├── cart.ts
│   └── product.ts
├── types/
│   ├── product.ts
│   ├── cart.ts
│   └── api.ts
├── nuxt.config.ts
├── app.config.ts
└── tsconfig.json
```

### 3. Rendering Strategy

Define per-route rendering modes:

```markdown
## Rendering Strategy

### Route Rules
| Route Pattern | Mode | Justification |
|---------------|------|---------------|
| `/` | SSG (prerender) | Static landing page, maximum performance |
| `/products/**` | SWR (3600s) | SEO required, hourly freshness sufficient |
| `/products/[slug]` | ISR (3600s) | SEO + dynamic, CDN-cached with revalidation |
| `/cart` | SSR | Needs real-time cart data |
| `/checkout` | SPA | Authenticated, no SEO needed |
| `/admin/**` | SPA | Internal tool, no SEO needed |
| `/api/**` | N/A | Server routes with CORS |

### Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  ssr: true,
  routeRules: {
    '/':              { prerender: true },
    '/products':      { swr: 3600 },
    '/products/**':   { isr: 3600 },
    '/cart':          { ssr: true },
    '/checkout':      { ssr: false },
    '/admin/**':      { ssr: false },
    '/api/**':        { cors: true },
  },
})
```

### 4. TypeScript Types

Define all shared interfaces and types:

```markdown
## Types

### Product
**File**: types/product.ts

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | number | yes | Primary key |
| name | string | yes | Display name |
| slug | string | yes | URL-safe identifier |
| description | string | yes | Full description |
| price | number | yes | Price in cents |
| compareAtPrice | number | no | Original price for sale display |
| images | ProductImage[] | yes | At least one image |
| category | Category | yes | Product category |
| inStock | boolean | yes | Availability flag |
| variants | ProductVariant[] | no | Size/color variants |

### CartItem
**File**: types/cart.ts

| Field | Type | Required |
|-------|------|----------|
| productId | number | yes |
| variantId | number | no |
| quantity | number | yes |
| price | number | yes |
```

```typescript
// types/product.ts
export interface Product {
  id: number
  name: string
  slug: string
  description: string
  price: number
  compareAtPrice?: number
  images: ProductImage[]
  category: Category
  inStock: boolean
  variants?: ProductVariant[]
}

export interface ProductImage {
  id: number
  url: string
  alt: string
  width: number
  height: number
}

export interface ProductVariant {
  id: number
  name: string
  sku: string
  price: number
  inStock: boolean
}

export interface Category {
  id: number
  name: string
  slug: string
}
```

### 5. Pinia Stores

Specify stores with full implementation details:

```markdown
## Stores

### useCartStore
**File**: stores/cart.ts
**Pattern**: Setup Store (Composition API)

**State**:
| Property | Type | Default |
|----------|------|---------|
| items | CartItem[] | [] |
| loading | boolean | false |

**Getters**:
| Getter | Return Type | Logic |
|--------|-------------|-------|
| totalItems | number | Sum of all item quantities |
| subtotal | number | Sum of (item.price * item.quantity) |
| isEmpty | boolean | items.length === 0 |

**Actions**:
| Action | Parameters | Description |
|--------|-----------|-------------|
| addItem | product: Product, quantity: number | Add or increment item |
| removeItem | productId: number | Remove item from cart |
| updateQuantity | productId: number, quantity: number | Set item quantity |
| clearCart | none | Empty the cart |
```

```typescript
// stores/cart.ts
import type { CartItem } from '~/types/cart'
import type { Product } from '~/types/product'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const loading = ref(false)

  const totalItems = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const subtotal = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  const isEmpty = computed(() => items.value.length === 0)

  function addItem(product: Product, quantity = 1) {
    const existing = items.value.find(item => item.productId === product.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({
        productId: product.id,
        quantity,
        price: product.price,
      })
    }
  }

  function removeItem(productId: number) {
    items.value = items.value.filter(item => item.productId !== productId)
  }

  function updateQuantity(productId: number, quantity: number) {
    const item = items.value.find(item => item.productId === productId)
    if (item) {
      item.quantity = Math.max(0, quantity)
      if (item.quantity === 0) removeItem(productId)
    }
  }

  function clearCart() {
    items.value = []
  }

  return { items, loading, totalItems, subtotal, isEmpty, addItem, removeItem, updateQuantity, clearCart }
})
```

### 6. Composables

Document reusable logic with full signatures:

```markdown
## Composables

### useProductSearch
**File**: composables/useProductSearch.ts
**Purpose**: Debounced product search with category filtering

**Parameters**:
| Param | Type | Default |
|-------|------|---------|
| options.debounce | number | 300 |

**Returns**:
| Property | Type | Description |
|----------|------|-------------|
| query | `Ref<string>` | Search input binding |
| category | `Ref<string \| null>` | Active category filter |
| results | `Ref<Product[]>` | Filtered product list |
| pending | `Ref<boolean>` | Loading state |
| error | `Ref<Error \| null>` | Error state |
```

```typescript
// composables/useProductSearch.ts
import type { Product } from '~/types/product'

export function useProductSearch(options: { debounce?: number } = {}) {
  const query = ref('')
  const category = ref<string | null>(null)

  const { data: results, pending, error } = useFetch<Product[]>('/api/products', {
    query: {
      q: query,
      category,
    },
    debounce: options.debounce ?? 300,
    default: () => [],
  })

  return { query, category, results, pending, error }
}
```

### 7. Components Specification

Include props, emits, slots, and template structure:

```markdown
## Components

### ProductCard
**File**: components/product/ProductCard.vue
**Purpose**: Display a single product in a grid

**Props**:
| Prop | Type | Required | Default |
|------|------|----------|---------|
| product | Product | yes | - |
| showComparePrice | boolean | no | true |

**Emits**:
| Event | Payload | Description |
|-------|---------|-------------|
| add-to-cart | Product | User clicked add to cart |

**Slots**:
| Slot | Props | Description |
|------|-------|-------------|
| badge | { product } | Custom badge overlay |
```

```vue
<!-- components/product/ProductCard.vue -->
<script setup lang="ts">
import type { Product } from '~/types/product'

const { product, showComparePrice = true } = defineProps<{
  product: Product
  showComparePrice?: boolean
}>()

const emit = defineEmits<{
  'add-to-cart': [product: Product]
}>()

const formattedPrice = computed(() => formatCurrency(product.price))
const formattedComparePrice = computed(() =>
  product.compareAtPrice ? formatCurrency(product.compareAtPrice) : null
)
const isOnSale = computed(() =>
  product.compareAtPrice != null && product.compareAtPrice > product.price
)
</script>

<template>
  <div class="group relative rounded-lg border bg-white p-4 transition hover:shadow-md">
    <slot name="badge" :product="product">
      <span v-if="isOnSale" class="absolute right-2 top-2 rounded bg-red-500 px-2 py-1 text-xs text-white">
        Sale
      </span>
    </slot>

    <NuxtLink :to="`/products/${product.slug}`">
      <NuxtImg
        :src="product.images[0]?.url"
        :alt="product.images[0]?.alt ?? product.name"
        :width="400"
        :height="400"
        class="aspect-square w-full rounded object-cover"
        loading="lazy"
      />
    </NuxtLink>

    <div class="mt-3">
      <NuxtLink :to="`/products/${product.slug}`" class="font-medium hover:underline">
        {{ product.name }}
      </NuxtLink>

      <div class="mt-1 flex items-center gap-2">
        <span class="text-lg font-bold">{{ formattedPrice }}</span>
        <span v-if="showComparePrice && formattedComparePrice" class="text-sm text-gray-400 line-through">
          {{ formattedComparePrice }}
        </span>
      </div>

      <button
        :disabled="!product.inStock"
        class="mt-3 w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        @click="emit('add-to-cart', product)"
      >
        {{ product.inStock ? 'Add to Cart' : 'Out of Stock' }}
      </button>
    </div>
  </div>
</template>
```

### 8. Pages & Data Fetching

Specify data fetching strategy per page:

```markdown
## Pages

### Product Listing - pages/products/index.vue
**Rendering**: SWR (cached 1 hour)
**Data Fetching**: useFetch with query params
**SEO**: useSeoMeta with dynamic title

### Product Detail - pages/products/[slug].vue
**Rendering**: ISR (revalidate 1 hour)
**Data Fetching**: useFetch by slug
**SEO**: useSeoMeta with product name, description, OG image
**Error**: showError(404) if product not found
```

```vue
<!-- pages/products/[slug].vue -->
<script setup lang="ts">
import type { Product } from '~/types/product'

const route = useRoute()
const cartStore = useCartStore()

const { data: product, error } = await useFetch<Product>(`/api/products/${route.params.slug}`)

if (error.value || !product.value) {
  throw createError({ statusCode: 404, statusMessage: 'Product not found' })
}

useSeoMeta({
  title: product.value.name,
  description: product.value.description,
  ogTitle: product.value.name,
  ogDescription: product.value.description,
  ogImage: product.value.images[0]?.url,
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="grid gap-8 md:grid-cols-2">
      <NuxtImg
        :src="product!.images[0]?.url"
        :alt="product!.images[0]?.alt ?? product!.name"
        :width="600"
        :height="600"
        class="w-full rounded-lg"
      />

      <div>
        <h1 class="text-3xl font-bold">{{ product!.name }}</h1>
        <p class="mt-2 text-2xl font-semibold">{{ formatCurrency(product!.price) }}</p>
        <p class="mt-4 text-gray-600">{{ product!.description }}</p>

        <button
          :disabled="!product!.inStock"
          class="mt-6 rounded bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:bg-gray-300"
          @click="cartStore.addItem(product!)"
        >
          {{ product!.inStock ? 'Add to Cart' : 'Out of Stock' }}
        </button>
      </div>
    </div>
  </div>
</template>
```

### 9. Server API Routes

Define Nitro server endpoints:

```markdown
## Server API Routes

### GET /api/products
**File**: server/api/products/index.get.ts
**Query Params**: q (search), category (filter), page, limit
**Caching**: defineCachedEventHandler, maxAge: 3600
**Response**: { products: Product[], total: number }

### GET /api/products/:id
**File**: server/api/products/[id].get.ts
**Params**: id (number)
**Response**: Product
**Error**: 404 if not found

### POST /api/cart
**File**: server/api/cart/index.post.ts
**Body**: { productId: number, quantity: number }
**Auth**: Required (server middleware)
**Response**: CartItem
```

```typescript
// server/api/products/index.get.ts
export default defineCachedEventHandler(async (event) => {
  const query = getQuery(event)
  const { q, category, page = '1', limit = '20' } = query

  const products = await fetchProductsFromDB({
    search: q as string | undefined,
    category: category as string | undefined,
    page: Number(page),
    limit: Number(limit),
  })

  return products
}, { maxAge: 3600 })
```

```typescript
// server/api/products/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const product = await fetchProductById(Number(id))

  if (!product) {
    throw createError({ statusCode: 404, statusMessage: 'Product not found' })
  }

  return product
})
```

### 10. Middleware

```markdown
## Middleware

### auth.ts (Named)
**File**: middleware/auth.ts
**Applied to**: /checkout, /admin/**
**Logic**: Redirect to /login if not authenticated

### guest.ts (Named)
**File**: middleware/guest.ts
**Applied to**: /login, /register
**Logic**: Redirect to / if already authenticated
```

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  const { loggedIn } = useUserSession()
  if (!loggedIn.value) {
    return navigateTo('/login', { redirectCode: 302 })
  }
})
```

```vue
<!-- pages/checkout.vue -->
<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})
</script>
```

### 11. Nuxt Configuration

```markdown
## Configuration

### nuxt.config.ts
**Modules**: @nuxtjs/tailwindcss, @pinia/nuxt, @nuxt/image, @nuxt/fonts
**Runtime Config**: apiBaseUrl (private), appName (public)
**App Head**: Default meta tags, favicon
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  future: { compatibilityVersion: 4 },
  ssr: true,

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxt/image',
    '@nuxt/fonts',
  ],

  routeRules: {
    '/':              { prerender: true },
    '/products':      { swr: 3600 },
    '/products/**':   { isr: 3600 },
    '/checkout':      { ssr: false },
    '/admin/**':      { ssr: false },
    '/api/**':        { cors: true },
  },

  runtimeConfig: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:3001',
    public: {
      appName: 'My Store',
    },
  },

  app: {
    head: {
      title: 'My Store',
      meta: [
        { name: 'description', content: 'E-commerce product catalog' },
      ],
    },
  },

  image: {
    quality: 80,
    formats: ['webp', 'avif'],
  },

  typescript: {
    strict: true,
  },
})
```

### 12. Testing Strategy

```markdown
## Testing

### Inverted Pyramid Distribution
| Layer | Coverage | Tool | Focus |
|-------|----------|------|-------|
| Integration | ~70% | Vitest + @nuxt/test-utils | Component interactions, pages, data flow |
| Unit | ~20% | Vitest (Node) | Composables, stores, utilities |
| A11y + Visual | ~10% | axe-core, Playwright | WCAG compliance, visual regressions |

### Test Files
- tests/unit/stores/cart.test.ts
- tests/unit/composables/useProductSearch.test.ts
- tests/unit/utils/formatCurrency.test.ts
- tests/nuxt/components/ProductCard.test.ts
- tests/nuxt/pages/products.test.ts
- tests/e2e/checkout.spec.ts
```

### 13. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Landing page renders via SSG at /
2. [ ] Product listing loads with SWR at /products
3. [ ] Product detail page renders with ISR at /products/[slug]
4. [ ] Add to cart updates CartDrawer reactively
5. [ ] Cart persists across page navigations
6. [ ] Checkout redirects to /login if unauthenticated
7. [ ] Admin panel renders as SPA at /admin
8. [ ] Search debounces and filters correctly
9. [ ] SEO meta tags render in page source
10. [ ] Images serve in WebP/AVIF via NuxtImg

### Automated
npx vitest run
npx playwright test
npx vue-tsc --noEmit
```

## Vague Plan vs Blueprint: Critical Differences

A vague plan answers "what to build" but leaves "how" to interpretation. A Blueprint provides **implementation-ready specifications** with exact code patterns.

### Vague Plan (Before Blueprint)

```markdown
## Product Catalog
- Product listing page with search
- Product detail page
- Shopping cart
- Checkout flow
- Admin panel
```

**Problems:**
- No rendering strategy per route
- No TypeScript interfaces for data shapes
- No data fetching approach (`useFetch` vs `useAsyncData` vs `$fetch`)
- No state management design (Pinia vs composable vs local)
- No component prop/emit contracts
- No SEO strategy
- No directory structure

### Blueprint (Implementation-Ready)

**Product Listing Page**
- **File**: `pages/products/index.vue`
- **Rendering**: SWR (3600s) via routeRules
- **Data Fetching**: `useProductSearch({ debounce: 300 })` composable
- **SEO**: `useSeoMeta()` with dynamic title from category filter

```typescript
const { query, category, results, pending } = useProductSearch({ debounce: 300 })

useSeoMeta({
  title: () => category.value ? `${category.value} Products` : 'All Products',
  description: 'Browse our product catalog',
})
```

**Components Used**:

| Component | Props | Events |
|-----------|-------|--------|
| ProductGrid | `products: Product[], loading: boolean` | - |
| ProductCard | `product: Product` | `add-to-cart: Product` |
| ProductFilters | `categories: Category[]` | `update:category: string` |
| BaseSearchInput | `modelValue: string, placeholder: string` | `update:modelValue: string` |

**State**: Cart via `useCartStore`, search via `useProductSearch` composable

## Architecture Tier Decision Framework

| Criterion | Flat | Atomic Design | Modular (Feature-Based) | Feature-Sliced Design |
|-----------|------|---------------|------------------------|-----------------------|
| Team size | 1-2 | 3-8 | 5-15 | 10+ |
| Pages | <10 | 10-30 | 20-100 | 50+ |
| Component count | <20 | 20-80 | 50-200 | 100+ |
| Reuse requirements | Low | High | Medium | High |
| Feature boundaries | Blurred | By component type | By feature | By business domain |
| Onboarding complexity | Trivial | Medium | Medium | High |
| Refactor cost (later) | High | Medium | Low | Low |

### When to Choose Each

**Flat**: Prototype, hackathon, landing page. Everything in `components/`, `composables/`, `pages/`.

**Atomic Design**: Design-system-heavy projects. Organize by atoms/molecules/organisms/templates.

**Modular (Feature-Based)**: Group by feature domain. `components/product/`, `components/cart/`, `composables/useProduct*`. Best default for most Nuxt apps.

**Feature-Sliced Design**: Strict layered architecture (shared -> entities -> features -> widgets -> pages -> app). For complex enterprise apps with strict dependency rules.

## Component Design Decision Tree

| Question | YES | NO |
|----------|-----|-----|
| Does it render UI? | **Component** | Next question |
| Does it manage global shared state? | **Pinia Store** | Next question |
| Does it need app-wide availability before mount? | **Plugin** | Next question |
| Is it reusable reactive logic? | **Composable** | Next question |
| Is it a pure function with no reactivity? | **Utility** (in `utils/`) | Reconsider design |

### Composables vs Pinia Stores

| Criterion | Composable | Pinia Store |
|-----------|------------|-------------|
| Scope | Per-importer instance | Global singleton |
| Shared state across components | No (each gets own copy) | Yes |
| DevTools integration | None | Full (time-travel, inspection) |
| SSR hydration | Manual | Automatic via `@pinia/nuxt` |
| Testing | Import and call directly | `createPinia()` + `setActivePinia()` |
| Use for | UI logic, API wrappers, browser APIs | Auth, cart, global settings |

## Rendering Strategy Decision Matrix

| Need SEO? | Data changes frequently? | Authenticated? | High traffic? | Use |
|-----------|------------------------|----------------|---------------|-----|
| Yes | No | No | Any | **SSG** (`prerender: true`) |
| Yes | Hourly | No | Yes | **ISR** (`isr: 3600`) |
| Yes | Hourly | No | Medium | **SWR** (`swr: 3600`) |
| Yes | Real-time | No | Any | **SSR** (`ssr: true`) |
| No | Any | Yes | Any | **SPA** (`ssr: false`) |
| No | Any | No | Any | **SPA** (`ssr: false`) |

### Configuration Reference

```typescript
export default defineNuxtConfig({
  routeRules: {
    // SSG - prerendered at build time
    '/about': { prerender: true },

    // ISR - CDN cached, revalidated in background
    '/blog/**': { isr: 3600 },

    // SWR - serve stale, revalidate in background
    '/products/**': { swr: 3600 },

    // SPA - client-side only
    '/admin/**': { ssr: false },
  },
})
```

**CRITICAL**: Never use SPA (`ssr: false`) for public content that needs SEO. Search engines index SSR/SSG/ISR content reliably; SPA content requires JavaScript execution.

## Pinia State Management Patterns

### Setup Store (Recommended)

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isLoggedIn = computed(() => user.value !== null)
  const displayName = computed(() => user.value?.name ?? 'Guest')

  async function login(credentials: LoginInput) {
    const response = await $fetch<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: credentials,
    })
    user.value = response.user
    token.value = response.token
  }

  function logout() {
    user.value = null
    token.value = null
    navigateTo('/login')
  }

  return { user, token, isLoggedIn, displayName, login, logout }
})
```

### Store with API Integration

```typescript
// stores/product.ts
export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const featured = computed(() =>
    products.value.filter(p => p.featured).slice(0, 8)
  )

  async function fetchProducts(params?: ProductQueryParams) {
    loading.value = true
    error.value = null
    try {
      const data = await $fetch<{ products: Product[]; total: number }>('/api/products', {
        query: params,
      })
      products.value = data.products
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch products'
    } finally {
      loading.value = false
    }
  }

  return { products, loading, error, featured, fetchProducts }
})
```

**CRITICAL**: Use `$fetch` inside Pinia actions (event-driven), not `useFetch` (which is for component setup context only).

## API Layer Design

### The Three Fetching Tools

| Tool | Context | SSR Safe | Auto-Dedup | Reactive | Use For |
|------|---------|----------|------------|----------|---------|
| `useFetch` | Component setup | Yes | Yes | Yes | Initial page data |
| `useAsyncData` | Component setup | Yes | Yes | Yes | Custom async logic, SDKs |
| `$fetch` | Anywhere | No (alone) | No | No | Event handlers, store actions |

**CRITICAL**: Never use bare `$fetch` in component `<script setup>` for initial data -- it causes double-fetching (server + client). Always wrap in `useFetch` or `useAsyncData`.

### useFetch Patterns

```typescript
// Basic fetch with type safety
const { data: products, pending, error, refresh } = await useFetch<Product[]>('/api/products')

// With reactive query params (auto-refetches on change)
const page = ref(1)
const category = ref<string | null>(null)

const { data, pending } = await useFetch<ProductListResponse>('/api/products', {
  query: { page, category, limit: 20 },
})

// Pick only needed fields (reduces payload)
const { data } = await useFetch('/api/products', {
  pick: ['products', 'total'],
})

// Transform response
const { data: productNames } = await useFetch<Product[]>('/api/products', {
  transform: (products) => products.map(p => p.name),
})
```

### useAsyncData Patterns

```typescript
// When you need custom logic beyond simple fetch
const { data: product } = await useAsyncData(
  `product-${route.params.slug}`,
  () => $fetch<Product>(`/api/products/${route.params.slug}`)
)

// Combining multiple requests
const { data } = await useAsyncData('product-page', async () => {
  const [product, reviews] = await Promise.all([
    $fetch<Product>(`/api/products/${route.params.slug}`),
    $fetch<Review[]>(`/api/products/${route.params.slug}/reviews`),
  ])
  return { product, reviews }
})
```

### $fetch in Event Handlers

```typescript
// Correct: $fetch in event handlers / store actions
async function handleAddToCart(product: Product) {
  await $fetch('/api/cart', {
    method: 'POST',
    body: { productId: product.id, quantity: 1 },
  })
  cartStore.addItem(product)
}
```

### Repository Pattern (For Large Apps)

```typescript
// plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const apiFetcher = $fetch.create({
    baseURL: config.public.apiBaseUrl,
    onRequest({ options }) {
      const token = useCookie('auth-token')
      if (token.value) {
        options.headers = { ...options.headers, Authorization: `Bearer ${token.value}` }
      }
    },
  })

  return {
    provide: {
      api: {
        products: {
          list: (params?: ProductQueryParams) =>
            apiFetcher<ProductListResponse>('/products', { query: params }),
          get: (slug: string) =>
            apiFetcher<Product>(`/products/${slug}`),
        },
        cart: {
          get: () => apiFetcher<Cart>('/cart'),
          addItem: (body: AddCartItemInput) =>
            apiFetcher<CartItem>('/cart/items', { method: 'POST', body }),
        },
      },
    },
  }
})
```

## TypeScript Integration Patterns

### Component Props (Vue 3.4+ Destructure)

```typescript
<script setup lang="ts">
// Destructured with defaults -- reactive in Vue 3.4+
const { product, showBadge = true } = defineProps<{
  product: Product
  showBadge?: boolean
}>()
</script>
```

### Component Emits (Vue 3.3+ Tuple Syntax)

```typescript
<script setup lang="ts">
const emit = defineEmits<{
  'add-to-cart': [product: Product]
  'update:quantity': [value: number]
  close: []
}>()
</script>
```

### Typed Provide/Inject

```typescript
// types/injection-keys.ts
import type { InjectionKey, Ref } from 'vue'
import type { Theme } from '~/types/theme'

export const ThemeKey: InjectionKey<Ref<Theme>> = Symbol('theme')

// In parent component
provide(ThemeKey, theme)

// In child component
const theme = inject(ThemeKey) // type: Ref<Theme> | undefined
```

### Typed Template Refs (Vue 3.5+)

```typescript
<script setup lang="ts">
const inputRef = useTemplateRef<HTMLInputElement>('input')

function focus() {
  inputRef.value?.focus()
}
</script>

<template>
  <input ref="input" />
</template>
```

### Typed Composable Return

```typescript
interface UseProductSearchReturn {
  query: Ref<string>
  category: Ref<string | null>
  results: Ref<Product[]>
  pending: Ref<boolean>
  error: Ref<Error | null>
}

export function useProductSearch(): UseProductSearchReturn {
  // implementation
}
```

### Nuxt Auto-Generated Types

```typescript
// Nuxt generates types for routes, middleware, layouts
definePageMeta({
  layout: 'checkout',    // type-checked against layouts/
  middleware: 'auth',     // type-checked against middleware/
})

// Runtime config is typed
const config = useRuntimeConfig()
config.apiBaseUrl       // typed from nuxt.config.ts runtimeConfig
config.public.appName   // typed from nuxt.config.ts runtimeConfig.public
```

**CRITICAL**: Run `nuxi prepare` after adding new pages, middleware, or layouts to regenerate types. Run `vue-tsc --noEmit` in CI to catch type errors.

## Nuxt Modules and Layers Patterns

### Essential Module Stack

| Module | Purpose | Configuration |
|--------|---------|---------------|
| `@nuxtjs/tailwindcss` | Utility CSS framework | Auto-configured |
| `@pinia/nuxt` | State management | Auto-imports stores |
| `@nuxt/image` | Image optimization | WebP/AVIF, responsive |
| `@nuxt/fonts` | Font optimization | Auto-fallback metrics |
| `@vueuse/nuxt` | Composable utilities | Auto-imported |
| `@nuxtjs/seo` | SEO toolkit | Sitemap, robots, OG |

### Custom Module Pattern

```typescript
// modules/analytics/index.ts
import { defineNuxtModule, addPlugin, createResolver } from '@nuxt/kit'

export default defineNuxtModule({
  meta: {
    name: 'analytics',
    configKey: 'analytics',
  },
  defaults: {
    trackingId: '',
    debug: false,
  },
  setup(options, nuxt) {
    const resolver = createResolver(import.meta.url)

    addPlugin(resolver.resolve('./runtime/plugin'))

    nuxt.options.runtimeConfig.public.analytics = {
      trackingId: options.trackingId,
      debug: options.debug,
    }
  },
})
```

### Nuxt Layers for Feature Boundaries

```
layers/
├── shared/              # Base layer: design system, utilities
│   ├── components/
│   │   ├── BaseButton.vue
│   │   └── BaseInput.vue
│   ├── composables/
│   │   └── useNotification.ts
│   └── nuxt.config.ts
├── products/            # Product catalog feature
│   ├── components/
│   ├── composables/
│   ├── pages/
│   ├── server/
│   └── nuxt.config.ts
└── cart/                # Shopping cart feature
    ├── components/
    ├── stores/
    ├── pages/
    ├── server/
    └── nuxt.config.ts
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  extends: [
    './layers/shared',
    './layers/products',
    './layers/cart',
  ],
})
```

**When to use Layers**:
- 50+ components with clear feature boundaries
- Multiple developers needing clear ownership
- Code reuse across multiple Nuxt applications
- Long-term projects expecting significant growth

## Testing Strategy

### Inverted Pyramid

| Layer | % | Tool | What to Test |
|-------|---|------|-------------|
| Integration | 70% | Vitest + `@nuxt/test-utils` | Pages, component trees, data flow |
| Unit | 20% | Vitest (Node) | Composables, stores, utilities |
| E2E | 10% | Playwright | Critical user journeys |

### Store Tests

```typescript
// tests/unit/stores/cart.test.ts
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '~/stores/cart'

describe('useCartStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('adds item to cart', () => {
    const store = useCartStore()
    const product = { id: 1, name: 'Shirt', price: 2999 } as Product

    store.addItem(product, 2)

    expect(store.items).toHaveLength(1)
    expect(store.items[0].quantity).toBe(2)
    expect(store.totalItems).toBe(2)
    expect(store.subtotal).toBe(5998)
  })

  it('increments quantity for existing item', () => {
    const store = useCartStore()
    const product = { id: 1, name: 'Shirt', price: 2999 } as Product

    store.addItem(product, 1)
    store.addItem(product, 2)

    expect(store.items).toHaveLength(1)
    expect(store.items[0].quantity).toBe(3)
  })

  it('removes item and recalculates', () => {
    const store = useCartStore()
    store.addItem({ id: 1, price: 1000 } as Product)
    store.addItem({ id: 2, price: 2000 } as Product)

    store.removeItem(1)

    expect(store.items).toHaveLength(1)
    expect(store.subtotal).toBe(2000)
  })
})
```

### Composable Tests

```typescript
// tests/unit/composables/useProductSearch.test.ts
import { useProductSearch } from '~/composables/useProductSearch'

describe('useProductSearch', () => {
  it('initializes with empty query', () => {
    const { query, category, results } = useProductSearch()

    expect(query.value).toBe('')
    expect(category.value).toBeNull()
    expect(results.value).toEqual([])
  })
})
```

### Component Tests with @nuxt/test-utils

```typescript
// tests/nuxt/components/ProductCard.test.ts
import { mountSuspended } from '@nuxt/test-utils/runtime'
import ProductCard from '~/components/product/ProductCard.vue'

describe('ProductCard', () => {
  const mockProduct: Product = {
    id: 1,
    name: 'Test Product',
    slug: 'test-product',
    description: 'A test product',
    price: 2999,
    images: [{ id: 1, url: '/test.jpg', alt: 'Test', width: 400, height: 400 }],
    category: { id: 1, name: 'Test', slug: 'test' },
    inStock: true,
  }

  it('renders product name and price', async () => {
    const wrapper = await mountSuspended(ProductCard, {
      props: { product: mockProduct },
    })

    expect(wrapper.text()).toContain('Test Product')
    expect(wrapper.text()).toContain('$29.99')
  })

  it('emits add-to-cart when button clicked', async () => {
    const wrapper = await mountSuspended(ProductCard, {
      props: { product: mockProduct },
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('add-to-cart')).toHaveLength(1)
    expect(wrapper.emitted('add-to-cart')![0]).toEqual([mockProduct])
  })

  it('disables button when out of stock', async () => {
    const wrapper = await mountSuspended(ProductCard, {
      props: { product: { ...mockProduct, inStock: false } },
    })

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    expect(wrapper.find('button').text()).toBe('Out of Stock')
  })
})
```

### Page Tests with Mocked API

```typescript
// tests/nuxt/pages/products.test.ts
import { mountSuspended, registerEndpoint } from '@nuxt/test-utils/runtime'
import ProductsPage from '~/pages/products/index.vue'

describe('Products Page', () => {
  beforeEach(() => {
    registerEndpoint('/api/products', {
      method: 'GET',
      handler: () => [
        { id: 1, name: 'Product A', slug: 'product-a', price: 1999, inStock: true },
        { id: 2, name: 'Product B', slug: 'product-b', price: 3999, inStock: false },
      ],
    })
  })

  it('renders product list from API', async () => {
    const wrapper = await mountSuspended(ProductsPage)

    expect(wrapper.text()).toContain('Product A')
    expect(wrapper.text()).toContain('Product B')
  })
})
```

## Performance Optimization Checklist

### Code & Bundle

| Check | Action | Impact |
|-------|--------|--------|
| Bundle analysis | Run `npx nuxi analyze` | Identify large dependencies |
| Tree shaking | Import specific functions: `import debounce from 'lodash-es/debounce'` | Reduce bundle size |
| Lazy components | Use `<LazyHeavyChart />` prefix | Code-split heavy components |
| Lazy hydration | `<LazyComponent hydrate-on-visible />` (Nuxt 3.16+) | Defer hydration |
| Dynamic imports | `const Modal = defineAsyncComponent(() => import('./Modal.vue'))` | On-demand loading |

### Data Fetching

| Check | Action | Impact |
|-------|--------|--------|
| Pick fields | `useFetch('/api/products', { pick: ['id', 'name'] })` | Smaller payloads |
| Server caching | `defineCachedEventHandler` with appropriate `maxAge` | Reduce DB queries |
| Route rules | Configure `swr` / `isr` for cacheable routes | CDN caching |
| No double fetch | Always use `useFetch`/`useAsyncData` in setup, never bare `$fetch` | Prevent SSR+CSR double request |

### Images & Assets

| Check | Action | Impact |
|-------|--------|--------|
| NuxtImg | Use `<NuxtImg>` instead of `<img>` | Auto WebP/AVIF, responsive |
| Explicit dimensions | Set `width` and `height` on images | Reduce CLS |
| Lazy loading | `loading="lazy"` for below-fold images | Faster LCP |
| Font optimization | Use `@nuxt/fonts` for automatic fallback metrics | Reduce CLS |

### Reactivity

| Check | Action | Impact |
|-------|--------|--------|
| Large lists | Use `shallowRef` for large arrays/objects | Reduce reactivity overhead |
| Static content | Use `v-once` for content that never changes | Skip re-renders |
| Expensive lists | Use `v-memo` for complex list items | Memoize rendering |
| Computed caching | Prefer `computed` over methods in templates | Cache derived values |

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| No rendering strategy | Entire app defaults to SSR or SPA | Define `routeRules` per route pattern |
| Bare `$fetch` in setup | Double data fetching (server + client) | Use `useFetch` or `useAsyncData` |
| Missing TypeScript interfaces | Props/emits untyped, runtime errors | Define interfaces in `types/` directory |
| Store for everything | Over-engineered, hard to test | Use composables for local state, stores for global only |
| No SEO plan | Product pages not indexed | Configure `useSeoMeta` per page, correct rendering mode |
| Flat structure at scale | Unmaintainable at 50+ components | Choose architecture tier upfront |
| No error handling for data | Blank pages on API failure | Handle `error` from `useFetch`, use `createError` for 404s |
| Missing `nuxi prepare` | Type errors in IDE, CI failures | Run after adding pages/middleware/layouts |
| SPA for public content | Zero SEO for marketing/product pages | Use SSR/SSG/ISR for public routes |
| No component contracts | Implicit props, silent failures | Specify props, emits, slots in Blueprint |
| Ignoring payload size | Slow hydration, wasted bandwidth | Use `pick` option in `useFetch` |
| No middleware plan | Auth bypassed, unauthorized access | Document middleware per route |

## Best Practices

1. **Be explicit** -- Include file paths, TypeScript interfaces, exact component configurations
2. **Define rendering per route** -- Never leave rendering mode as implicit default
3. **Show complete code** -- Not just component names, but full `<script setup>` and `<template>`
4. **Specify data fetching** -- Which tool (`useFetch` vs `useAsyncData` vs `$fetch`) and why
5. **Document component contracts** -- Props with types and defaults, emits with payloads, named slots
6. **Map state ownership** -- Which data lives in Pinia stores vs composables vs local refs
7. **Include TypeScript interfaces** -- Every API response, every prop type, every store state shape
8. **Plan SEO per page** -- `useSeoMeta` with dynamic values, OG images, structured data
9. **Show server API routes** -- HTTP method suffix, params, response shape, caching strategy
10. **Define middleware** -- Auth guards, redirects, and which routes they apply to
11. **Specify Nuxt modules** -- Which modules, their configuration, and why
12. **Test with pyramid distribution** -- 70% integration, 20% unit, 10% E2E
13. **Plan in order** -- Types -> Config -> Stores -> Composables -> Components -> Pages -> Tests
14. **Include file inventory** -- Categorized list of all files to create

## Anti-Patterns to Avoid

| Vague | Blueprint |
|-------|-----------|
| "product listing page" | Page with `useFetch`, `ProductGrid` component, SWR rendering, SEO meta |
| "add search" | `useProductSearch` composable with debounce, reactive query params, loading state |
| "shopping cart" | Pinia `useCartStore` with typed state, computed totals, `$fetch` actions |
| "fetch products" | `useFetch<Product[]>('/api/products', { query: { page, category } })` |
| "needs auth" | Named middleware `auth.ts` applied via `definePageMeta`, redirect to `/login` |
| "use TypeScript" | Strict mode, interfaces in `types/`, type-based `defineProps<T>`, `vue-tsc` in CI |
| "make it fast" | `routeRules` with ISR/SWR, `<NuxtImg>`, lazy components, `pick` on fetches |
| "add state management" | Pinia setup store with typed state, computed getters, async actions |

## Common Patterns

### SEO Meta per Page

```typescript
useSeoMeta({
  title: () => product.value?.name ?? 'Product',
  description: () => product.value?.description ?? '',
  ogTitle: () => product.value?.name ?? 'Product',
  ogDescription: () => product.value?.description ?? '',
  ogImage: () => product.value?.images[0]?.url ?? '/default-og.jpg',
})
```

### Error Handling for Data Fetching

```typescript
const { data: product, error } = await useFetch<Product>(`/api/products/${route.params.slug}`)

if (error.value) {
  throw createError({
    statusCode: error.value.statusCode ?? 500,
    statusMessage: error.value.statusMessage ?? 'Something went wrong',
  })
}
```

### Reactive Route Query Params

```typescript
const route = useRoute()
const router = useRouter()

const page = computed({
  get: () => Number(route.query.page) || 1,
  set: (value) => router.push({ query: { ...route.query, page: value } }),
})

const { data } = await useFetch('/api/products', {
  query: { page },
})
```

### Optimistic UI Update

```typescript
async function handleAddToCart(product: Product) {
  // Optimistic: update UI immediately
  cartStore.addItem(product)

  try {
    await $fetch('/api/cart/items', {
      method: 'POST',
      body: { productId: product.id, quantity: 1 },
    })
  } catch {
    // Rollback on failure
    cartStore.removeItem(product.id)
    showError('Failed to add item to cart')
  }
}
```

### Debounced Search Input

```vue
<script setup lang="ts">
const search = ref('')
const debouncedSearch = refDebounced(search, 300) // requires @vueuse/nuxt module

const { data: results } = await useFetch('/api/products', {
  query: { q: debouncedSearch },
})
</script>

<template>
  <input v-model="search" placeholder="Search products..." />
</template>
```

### Global Error Handler

```typescript
// plugins/error-handler.ts
export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.config.errorHandler = (error, instance, info) => {
    console.error('Global error:', error, info)
    // Send to error tracking service
  }
})
```

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Types (3)
- types/product.ts
- types/cart.ts
- types/api.ts

### Configuration (3)
- nuxt.config.ts
- app.config.ts
- tsconfig.json

### Stores (3)
- stores/auth.ts
- stores/cart.ts
- stores/product.ts

### Composables (3)
- composables/useProductSearch.ts
- composables/useCartActions.ts
- composables/usePagination.ts

### Components (10)
- components/base/BaseButton.vue
- components/base/BaseInput.vue
- components/base/BaseModal.vue
- components/product/ProductCard.vue
- components/product/ProductGrid.vue
- components/product/ProductFilters.vue
- components/cart/CartDrawer.vue
- components/cart/CartItem.vue
- components/cart/CartSummary.vue
- components/layout/AppHeader.vue

### Layouts (2)
- layouts/default.vue
- layouts/checkout.vue

### Pages (6)
- pages/index.vue
- pages/products/index.vue
- pages/products/[slug].vue
- pages/cart.vue
- pages/checkout.vue
- pages/admin/products/index.vue

### Middleware (2)
- middleware/auth.ts
- middleware/guest.ts

### Server Routes (5)
- server/api/products/index.get.ts
- server/api/products/[id].get.ts
- server/api/cart/index.get.ts
- server/api/cart/index.post.ts
- server/api/auth/login.post.ts

### Server Utilities (1)
- server/utils/db.ts

### Plugins (2)
- plugins/api.ts
- plugins/error-handler.ts

### Tests (7)
- tests/unit/stores/cart.test.ts
- tests/unit/stores/auth.test.ts
- tests/unit/composables/useProductSearch.test.ts
- tests/unit/utils/formatCurrency.test.ts
- tests/nuxt/components/ProductCard.test.ts
- tests/nuxt/pages/products.test.ts
- tests/e2e/checkout.spec.ts
```

## Deployment Planning

### Platform Decision Matrix

| Platform | Best For | SSR Support | Edge | ISR/SWR | Zero-Config |
|----------|----------|-------------|------|---------|-------------|
| **Vercel** | Full SSR + ISR + SWR | Yes | Yes | Native | Yes |
| **Netlify** | SSG + SSR | Yes | Yes | Via config | Yes |
| **Cloudflare Workers** | Edge-first apps | Yes | Native | Via KV | Preset needed |
| **Node.js Server** | Full control, self-hosted | Yes | No | Manual | Manual |

### Nitro Preset Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  nitro: {
    preset: 'vercel',        // or 'netlify', 'cloudflare-pages', 'node-server'
  },
})
```

### Environment Variables

```markdown
## Environment Variables

### Private (server only)
| Variable | Description | Required |
|----------|-------------|----------|
| API_BASE_URL | Backend API URL | Yes |
| DATABASE_URL | Database connection string | Yes |
| AUTH_SECRET | JWT signing secret | Yes |

### Public (exposed to client)
| Variable | Description | Default |
|----------|-------------|---------|
| NUXT_PUBLIC_APP_NAME | Application name | 'My Store' |
| NUXT_PUBLIC_SITE_URL | Canonical site URL | 'http://localhost:3000' |
```

### Pre-Deployment Checklist

```markdown
1. [ ] `vue-tsc --noEmit` passes with zero errors
2. [ ] `npx vitest run` all tests pass
3. [ ] `npx nuxi build` completes without warnings
4. [ ] `npx nuxi analyze` shows no unexpected large bundles
5. [ ] Environment variables configured in deployment platform
6. [ ] Rendering modes verified (SSG pages prerendered, ISR routes cached)
7. [ ] SEO meta tags render correctly in page source
8. [ ] Images served via CDN with optimization
9. [ ] Error pages (404, 500) display correctly
10. [ ] Lighthouse score meets targets (Performance > 90)
```
