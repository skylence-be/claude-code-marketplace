---
name: pinia-state-patterns
description: Master Pinia state management including store definition (setup stores, options API), getters, actions, plugins, TypeScript integration, SSR hydration, and testing patterns. Use when managing global state, implementing complex business logic, or building scalable state architecture.
category: frontend
tags: [pinia, state-management, vuex-alternative, typescript, ssr]
related_skills: [vue3-composition-api-patterns, nuxt4-ssr-optimization, vitest-testing-patterns]
---

# Pinia State Management Patterns

Comprehensive guide to implementing state management with Pinia in Vue 3 and Nuxt applications, covering store definition patterns, getters for derived state, actions for business logic, plugins for extensibility, TypeScript integration, SSR state hydration, and comprehensive testing strategies.

## When to Use This Skill

- Managing global application state across multiple components
- Implementing complex business logic with actions and getters
- Creating reusable state modules for different features
- Integrating authentication and authorization state
- Building shopping carts or complex data structures
- Implementing real-time updates with WebSocket integration
- Persisting state to localStorage or external storage
- Managing API request state (loading, error, data)
- Building undo/redo functionality with state history
- Testing state management logic independently from components

## Core Concepts

### 1. Store Definition
- **Setup Stores**: Composition API style (recommended)
- **Options Stores**: Object-based definition (Vue 2 style)
- **Store composition**: Reusing stores within other stores
- **Hot module replacement**: Development experience
- **DevTools integration**: Time-travel debugging

### 2. State Management
- **State**: Reactive data container
- **Getters**: Computed properties for derived state
- **Actions**: Methods for business logic and mutations
- **$patch**: Batch state updates for performance
- **$reset**: Reset store to initial state

### 3. Plugins
- **Persistence**: Save state to localStorage/sessionStorage
- **DevTools**: Enhanced debugging capabilities
- **Subscriptions**: React to state changes
- **Custom plugins**: Extend store functionality
- **Global plugins**: Applied to all stores

### 4. TypeScript Integration
- Type-safe stores with full inference
- Typed getters and actions
- Strict typing for state properties
- Generic store types for reusability

### 5. SSR Support
- Server-side state initialization
- State hydration on client
- Per-request state isolation
- Nuxt module integration

## Quick Start

```typescript
// stores/counter.ts
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0
  }),

  getters: {
    doubled: (state) => state.count * 2
  },

  actions: {
    increment() {
      this.count++
    }
  }
})
```

```vue
<!-- Using in component -->
<script setup lang="ts">
import { useCounterStore } from '@/stores/counter'

const counter = useCounterStore()
</script>

<template>
  <div>
    <p>Count: {{ counter.count }}</p>
    <p>Doubled: {{ counter.doubled }}</p>
    <button @click="counter.increment">Increment</button>
  </div>
</template>
```

## Fundamental Patterns

### Pattern 1: Setup Stores (Composition API Style)

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  // State (use ref for reactivity)
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters (use computed)
  const isAuthenticated = computed(() => !!user.value && !!token.value)

  const isAdmin = computed(() => user.value?.role === 'admin')

  const fullName = computed(() => {
    if (!user.value) return ''
    return `${user.value.firstName} ${user.value.lastName}`
  })

  // Actions (regular functions)
  async function login(email: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<{ user: User; token: string }>('/api/auth/login', {
        method: 'POST',
        body: { email, password }
      })

      user.value = response.user
      token.value = response.token

      // Store token
      if (process.client) {
        localStorage.setItem('auth-token', response.token)
      }

      return { success: true }
    } catch (e: any) {
      error.value = e.message || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await $fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })
    } catch (e) {
      console.error('Logout error:', e)
    } finally {
      user.value = null
      token.value = null
      if (process.client) {
        localStorage.removeItem('auth-token')
      }
    }
  }

  async function fetchUser() {
    if (!token.value) return

    loading.value = true

    try {
      const response = await $fetch<User>('/api/auth/user', {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      user.value = response
    } catch (e) {
      console.error('Failed to fetch user:', e)
      // Invalid token, logout
      await logout()
    } finally {
      loading.value = false
    }
  }

  function updateUser(updates: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...updates }
    }
  }

  // Return everything to expose
  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    fullName,
    // Actions
    login,
    logout,
    fetchUser,
    updateUser
  }
})
```

### Pattern 2: Options API Stores

```typescript
// stores/todos.ts
import { defineStore } from 'pinia'
import type { Todo } from '@/types'

interface TodosState {
  todos: Todo[]
  filter: 'all' | 'active' | 'completed'
  loading: boolean
}

export const useTodosStore = defineStore('todos', {
  state: (): TodosState => ({
    todos: [],
    filter: 'all',
    loading: false
  }),

  getters: {
    // Automatically typed from return value
    filteredTodos: (state) => {
      if (state.filter === 'active') {
        return state.todos.filter(todo => !todo.completed)
      }
      if (state.filter === 'completed') {
        return state.todos.filter(todo => todo.completed)
      }
      return state.todos
    },

    // Access other getters
    completedCount(): number {
      return this.todos.filter(todo => todo.completed).length
    },

    activeCount(): number {
      return this.todos.filter(todo => !todo.completed).length
    },

    // Getter with parameters (return a function)
    getTodoById: (state) => {
      return (id: number) => state.todos.find(todo => todo.id === id)
    }
  },

  actions: {
    async fetchTodos() {
      this.loading = true

      try {
        const response = await $fetch<Todo[]>('/api/todos')
        this.todos = response
      } catch (error) {
        console.error('Failed to fetch todos:', error)
      } finally {
        this.loading = false
      }
    },

    async addTodo(text: string) {
      const newTodo = await $fetch<Todo>('/api/todos', {
        method: 'POST',
        body: { text, completed: false }
      })

      this.todos.push(newTodo)
    },

    async toggleTodo(id: number) {
      const todo = this.todos.find(t => t.id === id)
      if (!todo) return

      todo.completed = !todo.completed

      await $fetch(`/api/todos/${id}`, {
        method: 'PATCH',
        body: { completed: todo.completed }
      })
    },

    async removeTodo(id: number) {
      await $fetch(`/api/todos/${id}`, {
        method: 'DELETE'
      })

      this.todos = this.todos.filter(t => t.id !== id)
    },

    setFilter(filter: 'all' | 'active' | 'completed') {
      this.filter = filter
    },

    async clearCompleted() {
      const completedIds = this.todos
        .filter(todo => todo.completed)
        .map(todo => todo.id)

      await Promise.all(
        completedIds.map(id => this.removeTodo(id))
      )
    }
  }
})
```

### Pattern 3: Store Composition

```typescript
// stores/cart.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import type { CartItem, Product } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const userStore = useUserStore() // Compose other stores

  const items = ref<CartItem[]>([])
  const loading = ref(false)

  // Computed with dependency on other store
  const total = computed(() => {
    return items.value.reduce((sum, item) => {
      return sum + (item.price * item.quantity)
    }, 0)
  })

  const itemCount = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const discount = computed(() => {
    // Use user store state
    if (userStore.isAuthenticated && userStore.user?.isPremium) {
      return total.value * 0.1 // 10% discount for premium users
    }
    return 0
  })

  const finalTotal = computed(() => total.value - discount.value)

  async function addItem(product: Product, quantity = 1) {
    const existingItem = items.value.find(item => item.productId === product.id)

    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.value.push({
        productId: product.id,
        name: product.name,
        price: product.price,
        quantity,
        image: product.image
      })
    }

    // Sync with server if authenticated
    if (userStore.isAuthenticated) {
      await syncCart()
    }
  }

  async function removeItem(productId: number) {
    items.value = items.value.filter(item => item.productId !== productId)

    if (userStore.isAuthenticated) {
      await syncCart()
    }
  }

  async function updateQuantity(productId: number, quantity: number) {
    const item = items.value.find(item => item.productId === productId)

    if (item) {
      if (quantity <= 0) {
        await removeItem(productId)
      } else {
        item.quantity = quantity
        if (userStore.isAuthenticated) {
          await syncCart()
        }
      }
    }
  }

  async function syncCart() {
    if (!userStore.isAuthenticated) return

    loading.value = true

    try {
      await $fetch('/api/cart', {
        method: 'POST',
        body: { items: items.value },
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      })
    } catch (error) {
      console.error('Failed to sync cart:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadCart() {
    if (!userStore.isAuthenticated) return

    loading.value = true

    try {
      const response = await $fetch<CartItem[]>('/api/cart', {
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      })

      items.value = response
    } catch (error) {
      console.error('Failed to load cart:', error)
    } finally {
      loading.value = false
    }
  }

  function clearCart() {
    items.value = []
  }

  return {
    items,
    loading,
    total,
    itemCount,
    discount,
    finalTotal,
    addItem,
    removeItem,
    updateQuantity,
    syncCart,
    loadCart,
    clearCart
  }
})
```

### Pattern 4: State Updates with $patch

```typescript
// stores/settings.ts
import { defineStore } from 'pinia'

interface Settings {
  theme: 'light' | 'dark'
  language: string
  notifications: {
    email: boolean
    push: boolean
    sms: boolean
  }
  privacy: {
    profileVisible: boolean
    showEmail: boolean
  }
}

export const useSettingsStore = defineStore('settings', {
  state: (): Settings => ({
    theme: 'light',
    language: 'en',
    notifications: {
      email: true,
      push: false,
      sms: false
    },
    privacy: {
      profileVisible: true,
      showEmail: false
    }
  }),

  actions: {
    // Update single property
    setTheme(theme: 'light' | 'dark') {
      this.theme = theme
    },

    // Update multiple properties with $patch (object)
    updateNotifications(notifications: Partial<Settings['notifications']>) {
      this.$patch({
        notifications: {
          ...this.notifications,
          ...notifications
        }
      })
    },

    // Update with $patch (function) - better for complex logic
    toggleNotification(type: keyof Settings['notifications']) {
      this.$patch((state) => {
        state.notifications[type] = !state.notifications[type]
      })
    },

    // Batch updates for performance
    updateSettings(updates: Partial<Settings>) {
      this.$patch(updates)
    },

    // Reset to initial state
    resetSettings() {
      this.$reset()
    }
  }
})
```

```vue
<!-- Using $patch in component -->
<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'

const settings = useSettingsStore()

// Batch update multiple properties
const saveSettings = () => {
  settings.$patch({
    theme: 'dark',
    language: 'es',
    notifications: {
      email: true,
      push: true,
      sms: false
    }
  })
}

// Or use function form for complex updates
const toggleAllNotifications = () => {
  settings.$patch((state) => {
    const allEnabled = Object.values(state.notifications).every(v => v)
    state.notifications.email = !allEnabled
    state.notifications.push = !allEnabled
    state.notifications.sms = !allEnabled
  })
}
</script>
```

### Pattern 5: Plugins for Persistence

```typescript
// plugins/pinia-persistence.ts
import { PiniaPluginContext } from 'pinia'

export function createPersistedStatePlugin() {
  return ({ store, options }: PiniaPluginContext) => {
    // Only persist stores with persist option
    if (!options.persist) return

    const storageKey = `pinia-${store.$id}`

    // Restore state from localStorage
    if (process.client) {
      const saved = localStorage.getItem(storageKey)
      if (saved) {
        try {
          store.$patch(JSON.parse(saved))
        } catch (error) {
          console.error('Failed to restore state:', error)
        }
      }

      // Subscribe to changes and persist
      store.$subscribe((mutation, state) => {
        localStorage.setItem(storageKey, JSON.stringify(state))
      }, { detached: true })
    }
  }
}

// Use in Nuxt plugin
export default defineNuxtPlugin(({ $pinia }) => {
  $pinia.use(createPersistedStatePlugin())
})
```

```typescript
// stores/preferences.ts - Using persistence
import { defineStore } from 'pinia'

export const usePreferencesStore = defineStore('preferences', {
  state: () => ({
    theme: 'light',
    sidebarCollapsed: false,
    recentSearches: [] as string[]
  }),

  actions: {
    addRecentSearch(query: string) {
      this.recentSearches.unshift(query)
      this.recentSearches = this.recentSearches.slice(0, 10)
    }
  },

  // Enable persistence
  persist: true
})
```

### Pattern 6: Subscribing to State Changes

```typescript
// stores/analytics.ts
import { defineStore } from 'pinia'

export const useAnalyticsStore = defineStore('analytics', () => {
  const events = ref<any[]>([])

  function trackEvent(name: string, data: any) {
    events.value.push({
      name,
      data,
      timestamp: Date.now()
    })

    // Send to analytics service
    if (process.client) {
      sendToAnalytics(name, data)
    }
  }

  return {
    events,
    trackEvent
  }
})
```

```vue
<script setup lang="ts">
import { useCartStore } from '@/stores/cart'
import { useAnalyticsStore } from '@/stores/analytics'

const cart = useCartStore()
const analytics = useAnalyticsStore()

// Subscribe to cart changes
cart.$subscribe((mutation, state) => {
  console.log('Cart changed:', mutation.type)

  // Track analytics
  analytics.trackEvent('cart_updated', {
    itemCount: state.items.length,
    total: state.total
  })
})

// Subscribe to specific actions
cart.$onAction(({ name, args, after, onError }) => {
  console.log(`Action ${name} called with:`, args)

  after((result) => {
    console.log('Action completed:', result)
  })

  onError((error) => {
    console.error('Action failed:', error)
  })
})
</script>
```

### Pattern 7: TypeScript Integration

```typescript
// types/store.ts
export interface User {
  id: number
  email: string
  firstName: string
  lastName: string
  role: 'user' | 'admin' | 'moderator'
  isPremium: boolean
  createdAt: string
}

export interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
}

// stores/auth.ts
import { defineStore } from 'pinia'
import type { User, AuthState } from '@/types/store'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state): boolean => {
      return !!state.user && !!state.token
    },

    userRole: (state): User['role'] | null => {
      return state.user?.role ?? null
    },

    hasPermission: (state) => {
      return (permission: string): boolean => {
        if (!state.user) return false

        const permissions: Record<User['role'], string[]> = {
          admin: ['read', 'write', 'delete', 'manage'],
          moderator: ['read', 'write', 'delete'],
          user: ['read', 'write']
        }

        return permissions[state.user.role]?.includes(permission) ?? false
      }
    }
  },

  actions: {
    async login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
      this.loading = true
      this.error = null

      try {
        const response = await $fetch<{ user: User; token: string }>('/api/auth/login', {
          method: 'POST',
          body: { email, password }
        })

        this.user = response.user
        this.token = response.token

        return { success: true }
      } catch (e: any) {
        this.error = e.message
        return { success: false, error: e.message }
      } finally {
        this.loading = false
      }
    },

    logout(): void {
      this.$reset()
    }
  }
})

// Type-safe store access
export type AuthStore = ReturnType<typeof useAuthStore>
```

### Pattern 8: SSR State Hydration in Nuxt

```typescript
// stores/products.ts
import { defineStore } from 'pinia'
import type { Product } from '@/types'

export const useProductsStore = defineStore('products', () => {
  const products = ref<Product[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProducts() {
    // Skip if already loaded (for SSR hydration)
    if (products.value.length > 0) return

    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Product[]>('/api/products')
      products.value = response
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  function getProductById(id: number) {
    return products.value.find(p => p.id === id)
  }

  return {
    products,
    loading,
    error,
    fetchProducts,
    getProductById
  }
})
```

```vue
<!-- pages/products/[id].vue - SSR with Pinia -->
<script setup lang="ts">
import { useProductsStore } from '@/stores/products'

const route = useRoute()
const productsStore = useProductsStore()

// Fetch on server and client
await productsStore.fetchProducts()

// Get specific product
const product = computed(() => {
  const id = parseInt(route.params.id as string)
  return productsStore.getProductById(id)
})

if (!product.value) {
  throw createError({
    statusCode: 404,
    message: 'Product not found'
  })
}

useSeoMeta({
  title: product.value.name,
  description: product.value.description
})
</script>

<template>
  <div>
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    <p>${{ product.price }}</p>
  </div>
</template>
```

## Advanced Patterns

### Pattern 9: Generic Store Pattern

```typescript
// stores/generic-api.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export function createApiStore<T>(name: string, endpoint: string) {
  return defineStore(`api-${name}`, () => {
    const items = ref<T[]>([])
    const selectedItem = ref<T | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    const itemsById = computed(() => {
      return new Map(items.value.map((item: any) => [item.id, item]))
    })

    async function fetchAll() {
      loading.value = true
      error.value = null

      try {
        const response = await $fetch<T[]>(endpoint)
        items.value = response
      } catch (e: any) {
        error.value = e.message
      } finally {
        loading.value = false
      }
    }

    async function fetchOne(id: number) {
      loading.value = true
      error.value = null

      try {
        const response = await $fetch<T>(`${endpoint}/${id}`)
        selectedItem.value = response
        return response
      } catch (e: any) {
        error.value = e.message
        return null
      } finally {
        loading.value = false
      }
    }

    async function create(data: Partial<T>) {
      loading.value = true
      error.value = null

      try {
        const response = await $fetch<T>(endpoint, {
          method: 'POST',
          body: data
        })

        items.value.push(response)
        return response
      } catch (e: any) {
        error.value = e.message
        return null
      } finally {
        loading.value = false
      }
    }

    async function update(id: number, data: Partial<T>) {
      loading.value = true
      error.value = null

      try {
        const response = await $fetch<T>(`${endpoint}/${id}`, {
          method: 'PATCH',
          body: data
        })

        const index = items.value.findIndex((item: any) => item.id === id)
        if (index !== -1) {
          items.value[index] = response
        }

        return response
      } catch (e: any) {
        error.value = e.message
        return null
      } finally {
        loading.value = false
      }
    }

    async function remove(id: number) {
      loading.value = true
      error.value = null

      try {
        await $fetch(`${endpoint}/${id}`, {
          method: 'DELETE'
        })

        items.value = items.value.filter((item: any) => item.id !== id)
        return true
      } catch (e: any) {
        error.value = e.message
        return false
      } finally {
        loading.value = false
      }
    }

    return {
      items,
      selectedItem,
      loading,
      error,
      itemsById,
      fetchAll,
      fetchOne,
      create,
      update,
      remove
    }
  })
}

// Usage
import type { User, Post } from '@/types'

export const useUsersStore = createApiStore<User>('users', '/api/users')
export const usePostsStore = createApiStore<Post>('posts', '/api/posts')
```

### Pattern 10: Undo/Redo with State History

```typescript
// stores/history.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export function createHistoryStore<T>(baseStore: any) {
  return defineStore(`${baseStore.$id}-history`, () => {
    const history = ref<T[]>([])
    const currentIndex = ref(-1)

    const canUndo = computed(() => currentIndex.value > 0)
    const canRedo = computed(() => currentIndex.value < history.value.length - 1)

    function saveState(state: T) {
      // Remove any states after current index
      history.value = history.value.slice(0, currentIndex.value + 1)

      // Add new state
      history.value.push(JSON.parse(JSON.stringify(state)))
      currentIndex.value++

      // Limit history size
      if (history.value.length > 50) {
        history.value.shift()
        currentIndex.value--
      }
    }

    function undo() {
      if (canUndo.value) {
        currentIndex.value--
        const previousState = history.value[currentIndex.value]
        baseStore.$patch(previousState)
      }
    }

    function redo() {
      if (canRedo.value) {
        currentIndex.value++
        const nextState = history.value[currentIndex.value]
        baseStore.$patch(nextState)
      }
    }

    function clear() {
      history.value = []
      currentIndex.value = -1
    }

    return {
      history,
      currentIndex,
      canUndo,
      canRedo,
      saveState,
      undo,
      redo,
      clear
    }
  })
}
```

## Testing Strategies

```typescript
// stores/counter.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from '@/stores/counter'

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useCounterStore()
    expect(store.count).toBe(0)
    expect(store.doubled).toBe(0)
  })

  it('increments count', () => {
    const store = useCounterStore()
    store.increment()
    expect(store.count).toBe(1)
    expect(store.doubled).toBe(2)
  })

  it('handles $patch updates', () => {
    const store = useCounterStore()
    store.$patch({ count: 10 })
    expect(store.count).toBe(10)
  })

  it('resets to initial state', () => {
    const store = useCounterStore()
    store.increment()
    store.$reset()
    expect(store.count).toBe(0)
  })
})

// stores/user.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

// Mock $fetch
vi.mock('#app', () => ({
  $fetch: vi.fn()
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('logs in successfully', async () => {
    const store = useUserStore()
    const mockUser = { id: 1, name: 'John', email: 'john@example.com' }

    vi.mocked($fetch).mockResolvedValueOnce({
      user: mockUser,
      token: 'test-token'
    })

    const result = await store.login('john@example.com', 'password')

    expect(result.success).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe('test-token')
    expect(store.isAuthenticated).toBe(true)
  })

  it('handles login failure', async () => {
    const store = useUserStore()

    vi.mocked($fetch).mockRejectedValueOnce(
      new Error('Invalid credentials')
    )

    const result = await store.login('wrong@example.com', 'wrong')

    expect(result.success).toBe(false)
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('logs out correctly', async () => {
    const store = useUserStore()
    store.user = { id: 1, name: 'John', email: 'john@example.com' }
    store.token = 'test-token'

    await store.logout()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })
})
```

## Common Pitfalls

### Pitfall 1: Mutating State Outside Actions (Options API)

```typescript
// WRONG: Direct mutation in component
const store = useMyStore()
store.count++ // Don't do this with options API

// CORRECT: Use actions
store.increment()
```

### Pitfall 2: Not Using $patch for Multiple Updates

```typescript
// WRONG: Multiple individual updates (triggers multiple reactions)
store.firstName = 'John'
store.lastName = 'Doe'
store.age = 30

// CORRECT: Batch with $patch
store.$patch({
  firstName: 'John',
  lastName: 'Doe',
  age: 30
})
```

### Pitfall 3: Losing Reactivity with Destructuring

```typescript
// WRONG: Loses reactivity
const { count, doubled } = useCounterStore()

// CORRECT: Use storeToRefs
import { storeToRefs } from 'pinia'
const store = useCounterStore()
const { count, doubled } = storeToRefs(store)
const { increment } = store // Actions can be destructured
```

## Best Practices

1. **Use setup stores** for better TypeScript inference and flexibility
2. **Compose stores** to avoid duplication and build modular state
3. **Use $patch** for batch updates to improve performance
4. **Implement persistence** carefully (sensitive data, size limits)
5. **Test stores independently** from components
6. **Use TypeScript** for type-safe state management
7. **Leverage getters** for derived state instead of duplicating logic
8. **Handle errors** in actions and provide user feedback
9. **Use storeToRefs** when destructuring for reactivity
10. **Document store usage** for team collaboration

## Resources

- **Pinia Documentation**: https://pinia.vuejs.org
- **Pinia DevTools**: Browser extension for debugging
- **Pinia Plugins**: https://pinia.vuejs.org/core-concepts/plugins.html
- **VueUse integrations**: https://vueuse.org/integrations.html#pinia
- **Testing with Pinia**: https://pinia.vuejs.org/cookbook/testing.html
