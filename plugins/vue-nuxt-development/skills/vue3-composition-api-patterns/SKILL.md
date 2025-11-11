---
name: vue3-composition-api-patterns
description: Master Vue 3 Composition API including ref, reactive, computed, watch, composables, lifecycle hooks, template refs, provide/inject, and script setup syntax. Use when building reactive components, creating reusable composables, or implementing complex state logic.
category: frontend
tags: [vue3, composition-api, composables, reactivity, typescript]
related_skills: [typescript-vue-patterns, pinia-state-patterns, vitest-testing-patterns]
---

# Vue 3 Composition API Patterns

Comprehensive guide to implementing Vue 3 Composition API patterns, covering reactivity fundamentals, composable design, lifecycle management, dependency injection, and modern script setup syntax for building maintainable and scalable frontend applications.

## When to Use This Skill

- Building reactive components with Vue 3 Composition API
- Creating reusable composables for shared logic across components
- Managing complex state with ref, reactive, and computed properties
- Implementing lifecycle hooks for component initialization and cleanup
- Working with template refs for direct DOM manipulation
- Using provide/inject for dependency injection across component trees
- Building composables for external API integration (useAuth, useFetch)
- Implementing watchers for side effects and reactive updates
- Creating teleports for portal-style rendering (modals, tooltips)
- Using Suspense for async component loading and error boundaries

## Core Concepts

### 1. Reactivity System
- **ref()**: Creates reactive reference for primitive values
- **reactive()**: Creates reactive proxy for objects and arrays
- **computed()**: Creates cached computed property that auto-updates
- **readonly()**: Makes reactive object immutable
- **toRef()**: Creates ref from reactive object property

### 2. Composables
- Reusable functions that encapsulate stateful logic
- Follow naming convention: use* prefix (useCounter, useAuth)
- Return reactive state and methods for component consumption
- Can compose other composables for complex functionality
- Enable code sharing without component inheritance

### 3. Lifecycle Hooks
- **onMounted()**: Called after component is inserted into DOM
- **onUnmounted()**: Called before component is removed
- **onUpdated()**: Called after reactive update causes re-render
- **onBeforeMount()**: Called before mounting
- **onBeforeUnmount()**: Called before unmounting

### 4. Script Setup
- Simplified syntax for Composition API
- Variables and functions automatically exposed to template
- Props and emits with defineProps and defineEmits
- Improved TypeScript support with type inference
- Better performance with compile-time optimizations

### 5. Template Refs
- Access DOM elements directly from Composition API
- Use ref() and assign to template ref attribute
- Access after onMounted lifecycle hook
- Useful for focus management, animations, third-party libraries

## Quick Start

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Reactive state
const count = ref(0)

// Computed property
const doubled = computed(() => count.value * 2)

// Method
const increment = () => {
  count.value++
}

// Lifecycle hook
onMounted(() => {
  console.log('Component mounted!')
})
</script>

<template>
  <div>
    <h2>Count: {{ count }}</h2>
    <h3>Doubled: {{ doubled }}</h3>
    <button @click="increment">Increment</button>
  </div>
</template>
```

## Fundamental Patterns

### Pattern 1: Ref vs Reactive

```vue
<script setup lang="ts">
import { ref, reactive, toRefs } from 'vue'

// Using ref for primitives (recommended)
const count = ref(0)
const message = ref('Hello')
const isActive = ref(true)

// Access/modify with .value
count.value++
console.log(message.value)

// Using reactive for objects
const state = reactive({
  user: {
    name: 'John',
    email: 'john@example.com'
  },
  settings: {
    theme: 'dark',
    notifications: true
  }
})

// No .value needed for reactive
state.user.name = 'Jane'
console.log(state.settings.theme)

// Destructuring reactive (loses reactivity)
// WRONG:
// const { user } = state // Not reactive!

// CORRECT: Use toRefs for destructuring
const { user, settings } = toRefs(state)
// Now user.value and settings.value are reactive refs

// Alternative: Keep reactive object intact
const updateUser = () => {
  state.user.name = 'Alice'
  state.user.email = 'alice@example.com'
}

// Ref for complex objects also works
const userData = ref({
  name: 'John',
  email: 'john@example.com'
})

// Access with .value
userData.value.name = 'Jane'

// When to use what:
// - ref(): Primitives, single values, DOM refs
// - reactive(): Objects, collections, nested structures
// - ref() with object: When you need to replace entire object
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <p>User: {{ state.user.name }}</p>
    <p>Destructured: {{ user.name }}</p>
  </div>
</template>
```

### Pattern 2: Computed Properties

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface User {
  firstName: string
  lastName: string
  age: number
}

const user = ref<User>({
  firstName: 'John',
  lastName: 'Doe',
  age: 25
})

// Simple computed (getter only)
const fullName = computed(() => {
  return `${user.value.firstName} ${user.value.lastName}`
})

// Writable computed (getter and setter)
const fullNameEditable = computed({
  get: () => `${user.value.firstName} ${user.value.lastName}`,
  set: (newValue: string) => {
    const [first, last] = newValue.split(' ')
    user.value.firstName = first
    user.value.lastName = last
  }
})

// Complex computed with multiple dependencies
const items = ref([
  { id: 1, name: 'Item 1', price: 10, quantity: 2 },
  { id: 2, name: 'Item 2', price: 20, quantity: 1 },
  { id: 3, name: 'Item 3', price: 15, quantity: 3 }
])

const searchQuery = ref('')
const minPrice = ref(0)

// Computed with filtering
const filteredItems = computed(() => {
  return items.value.filter(item => {
    const matchesSearch = item.name
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
    const matchesPrice = item.price >= minPrice.value
    return matchesSearch && matchesPrice
  })
})

// Computed with aggregation
const totalPrice = computed(() => {
  return items.value.reduce((sum, item) => {
    return sum + (item.price * item.quantity)
  }, 0)
})

const averagePrice = computed(() => {
  if (items.value.length === 0) return 0
  return totalPrice.value / items.value.length
})

// Computed with expensive operations (automatically cached)
const sortedItems = computed(() => {
  return [...filteredItems.value].sort((a, b) => b.price - a.price)
})

// Computed status based on multiple conditions
const userStatus = computed(() => {
  if (user.value.age < 18) return 'Minor'
  if (user.value.age < 65) return 'Adult'
  return 'Senior'
})

const isAdult = computed(() => user.value.age >= 18)
</script>

<template>
  <div>
    <h2>{{ fullName }}</h2>
    <p>Status: {{ userStatus }}</p>

    <input v-model="fullNameEditable" placeholder="Edit full name">

    <div>
      <input v-model="searchQuery" placeholder="Search items">
      <input v-model.number="minPrice" type="number" placeholder="Min price">
    </div>

    <ul>
      <li v-for="item in sortedItems" :key="item.id">
        {{ item.name }} - ${{ item.price }}
      </li>
    </ul>

    <p>Total: ${{ totalPrice }}</p>
    <p>Average: ${{ averagePrice.toFixed(2) }}</p>
  </div>
</template>
```

### Pattern 3: Watchers

```vue
<script setup lang="ts">
import { ref, reactive, watch, watchEffect } from 'vue'

const count = ref(0)
const message = ref('')

// Simple watch (single source)
watch(count, (newValue, oldValue) => {
  console.log(`Count changed from ${oldValue} to ${newValue}`)
})

// Watch with immediate execution
watch(count, (newValue) => {
  console.log(`Current count: ${newValue}`)
}, { immediate: true })

// Watch multiple sources
const firstName = ref('John')
const lastName = ref('Doe')

watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log(`Name changed from ${oldFirst} ${oldLast} to ${newFirst} ${newLast}`)
  message.value = `Hello, ${newFirst} ${newLast}!`
})

// Watch reactive object (deep by default)
const user = reactive({
  name: 'John',
  email: 'john@example.com',
  address: {
    city: 'New York',
    country: 'USA'
  }
})

watch(user, (newValue, oldValue) => {
  console.log('User changed:', newValue)
  // Save to localStorage or API
  localStorage.setItem('user', JSON.stringify(newValue))
})

// Watch specific property of reactive object
watch(() => user.name, (newName, oldName) => {
  console.log(`Name changed from ${oldName} to ${newName}`)
})

// Watch nested property
watch(() => user.address.city, (newCity) => {
  console.log(`City changed to ${newCity}`)
})

// Deep watch for ref object
const settings = ref({
  theme: 'dark',
  notifications: {
    email: true,
    push: false
  }
})

watch(settings, (newSettings) => {
  console.log('Settings changed:', newSettings)
}, { deep: true })

// watchEffect - automatically tracks dependencies
watchEffect(() => {
  // Automatically re-runs when count or message changes
  console.log(`Count is ${count.value}, message is "${message.value}"`)

  // Useful for side effects
  document.title = `Count: ${count.value}`
})

// watchEffect with cleanup
watchEffect((onCleanup) => {
  const timer = setInterval(() => {
    console.log('Polling...')
  }, 1000)

  // Cleanup function called before re-run and unmount
  onCleanup(() => {
    clearInterval(timer)
  })
})

// Watch with flush timing
watch(count, () => {
  // Access updated DOM
  console.log('DOM updated')
}, { flush: 'post' }) // 'pre' (default), 'post', 'sync'

// Stop watcher manually
const stopWatcher = watch(count, () => {
  console.log('Watching count')
})

// Later...
const stopWatching = () => {
  stopWatcher()
}
</script>

<template>
  <div>
    <button @click="count++">Increment</button>
    <input v-model="message" placeholder="Enter message">
    <button @click="stopWatching">Stop Watching</button>
  </div>
</template>
```

### Pattern 4: Lifecycle Hooks

```vue
<script setup lang="ts">
import {
  ref,
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
  onErrorCaptured,
  onActivated,
  onDeactivated
} from 'vue'

const count = ref(0)
const data = ref<any[]>([])

// Called before component is mounted
onBeforeMount(() => {
  console.log('Component is about to be mounted')
  // Initialize data, setup before DOM creation
})

// Called after component is mounted (most common)
onMounted(() => {
  console.log('Component mounted - DOM is available')

  // Perfect for:
  // - API calls
  // - DOM manipulation
  // - Third-party library initialization
  // - Event listeners setup

  fetchData()
  setupEventListeners()
})

// Called before component re-renders
onBeforeUpdate(() => {
  console.log('Component is about to update')
  // Access DOM before update
})

// Called after component re-renders
onUpdated(() => {
  console.log('Component updated - DOM is updated')
  // Access updated DOM
  // Be careful: can cause infinite loops if you modify state here
})

// Called before component is unmounted
onBeforeUnmount(() => {
  console.log('Component is about to be unmounted')
  // Cleanup preparations
})

// Called after component is unmounted (most common for cleanup)
onUnmounted(() => {
  console.log('Component unmounted')

  // Perfect for:
  // - Remove event listeners
  // - Cancel pending requests
  // - Clear timers
  // - Cleanup subscriptions

  cleanupEventListeners()
  cancelRequests()
})

// Error handling
onErrorCaptured((err, instance, info) => {
  console.error('Error captured:', err, info)
  // Return false to prevent error propagation
  return false
})

// For components inside <keep-alive>
onActivated(() => {
  console.log('Component activated (from cache)')
  // Refresh data when component is re-activated
})

onDeactivated(() => {
  console.log('Component deactivated (cached)')
  // Pause operations when component is cached
})

// Helper functions
const fetchData = async () => {
  try {
    const response = await fetch('/api/data')
    data.value = await response.json()
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }
}

let eventListenersCleanup: (() => void) | null = null

const setupEventListeners = () => {
  const handleResize = () => {
    console.log('Window resized')
  }

  const handleScroll = () => {
    console.log('Window scrolled')
  }

  window.addEventListener('resize', handleResize)
  window.addEventListener('scroll', handleScroll)

  // Store cleanup function
  eventListenersCleanup = () => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('scroll', handleScroll)
  }
}

const cleanupEventListeners = () => {
  if (eventListenersCleanup) {
    eventListenersCleanup()
  }
}

const cancelRequests = () => {
  // Cancel any pending API requests
  console.log('Cancelling requests')
}
</script>

<template>
  <div>
    <h2>Count: {{ count }}</h2>
    <button @click="count++">Increment</button>

    <ul>
      <li v-for="item in data" :key="item.id">
        {{ item.name }}
      </li>
    </ul>
  </div>
</template>
```

### Pattern 5: Template Refs

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Single element ref
const inputRef = ref<HTMLInputElement | null>(null)
const buttonRef = ref<HTMLButtonElement | null>(null)

// Component ref
const childComponentRef = ref<InstanceType<typeof ChildComponent> | null>(null)

// Dynamic refs (v-for)
const itemRefs = ref<HTMLElement[]>([])

// Focus input on mount
onMounted(() => {
  if (inputRef.value) {
    inputRef.value.focus()
  }
})

const focusInput = () => {
  inputRef.value?.focus()
}

const getInputValue = () => {
  return inputRef.value?.value ?? ''
}

const measureButton = () => {
  if (buttonRef.value) {
    const rect = buttonRef.value.getBoundingClientRect()
    console.log('Button dimensions:', rect.width, rect.height)
  }
}

// Access child component methods
const callChildMethod = () => {
  childComponentRef.value?.someMethod()
}

// Function refs for dynamic assignment
const setItemRef = (el: HTMLElement | null) => {
  if (el) {
    // Do something with element
    console.log('Item ref set:', el)
  }
}

// Refs in v-for
const focusItem = (index: number) => {
  itemRefs.value[index]?.focus()
}

// Example with third-party library
const chartRef = ref<HTMLCanvasElement | null>(null)

onMounted(() => {
  if (chartRef.value) {
    // Initialize chart library
    // new Chart(chartRef.value, { ... })
  }
})
</script>

<template>
  <div>
    <!-- Single element ref -->
    <input
      ref="inputRef"
      type="text"
      placeholder="This will be focused"
    >

    <button ref="buttonRef" @click="measureButton">
      Measure Me
    </button>

    <!-- Component ref -->
    <ChildComponent ref="childComponentRef" />

    <button @click="callChildMethod">
      Call Child Method
    </button>

    <!-- Dynamic refs in v-for -->
    <input
      v-for="(item, index) in items"
      :key="item.id"
      :ref="(el) => { itemRefs[index] = el as HTMLElement }"
      :value="item.name"
    >

    <!-- Canvas for third-party library -->
    <canvas ref="chartRef"></canvas>
  </div>
</template>
```

### Pattern 6: Props and Emits with TypeScript

```vue
<script setup lang="ts">
import { computed } from 'vue'

// Define prop types
interface Props {
  title: string
  count?: number
  items: string[]
  user: {
    id: number
    name: string
  }
  isActive?: boolean
  variant?: 'primary' | 'secondary' | 'danger'
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  count: 0,
  isActive: true,
  variant: 'primary'
})

// Define emit types
interface Emits {
  (e: 'update:count', value: number): void
  (e: 'submit', data: { name: string; value: string }): void
  (e: 'delete', id: number): void
  (e: 'change', value: string): void
}

const emit = defineEmits<Emits>()

// Or use object syntax with validation
const emitWithValidation = defineEmits({
  submit: (data: { name: string; value: string }) => {
    // Validation
    return data.name.length > 0 && data.value.length > 0
  },
  delete: (id: number) => {
    return typeof id === 'number' && id > 0
  }
})

// Use props
const doubleCount = computed(() => props.count * 2)

// Emit events
const incrementCount = () => {
  emit('update:count', props.count + 1)
}

const handleSubmit = () => {
  emit('submit', {
    name: 'example',
    value: 'data'
  })
}

const handleDelete = (id: number) => {
  emit('delete', id)
}

// v-model implementation
const localCount = computed({
  get: () => props.count,
  set: (value: number) => emit('update:count', value)
})
</script>

<template>
  <div :class="['component', `variant-${variant}`]">
    <h2>{{ title }}</h2>
    <p>Count: {{ count }} (Double: {{ doubleCount }})</p>

    <button @click="incrementCount">Increment</button>
    <button @click="handleSubmit">Submit</button>

    <ul>
      <li v-for="(item, index) in items" :key="index">
        {{ item }}
        <button @click="handleDelete(index)">Delete</button>
      </li>
    </ul>

    <p>User: {{ user.name }}</p>
  </div>
</template>
```

### Pattern 7: Composables for Reusable Logic

```typescript
// composables/useCounter.ts
import { ref, computed } from 'vue'

export function useCounter(initialValue = 0) {
  const count = ref(initialValue)

  const doubled = computed(() => count.value * 2)

  const increment = () => {
    count.value++
  }

  const decrement = () => {
    count.value--
  }

  const reset = () => {
    count.value = initialValue
  }

  return {
    count,
    doubled,
    increment,
    decrement,
    reset
  }
}

// composables/useLocalStorage.ts
import { ref, watch } from 'vue'

export function useLocalStorage<T>(key: string, defaultValue: T) {
  const storedValue = localStorage.getItem(key)
  const data = ref<T>(
    storedValue ? JSON.parse(storedValue) : defaultValue
  )

  watch(data, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue))
  }, { deep: true })

  const remove = () => {
    localStorage.removeItem(key)
    data.value = defaultValue
  }

  return {
    data,
    remove
  }
}

// composables/useFetch.ts
import { ref, isRef, unref, type Ref } from 'vue'

interface UseFetchOptions {
  immediate?: boolean
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

export function useFetch<T>(
  url: string | Ref<string>,
  options: UseFetchOptions = {}
) {
  const { immediate = true, onSuccess, onError } = options

  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)

  const execute = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(unref(url))

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const json = await response.json()
      data.value = json

      onSuccess?.(json)
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
    } finally {
      loading.value = false
    }
  }

  if (immediate) {
    execute()
  }

  // Re-fetch if URL changes (if URL is a ref)
  if (isRef(url)) {
    watch(url, execute)
  }

  return {
    data,
    error,
    loading,
    execute,
    refresh: execute
  }
}

// composables/useAuth.ts
import { ref, computed } from 'vue'
import type { Ref } from 'vue'

interface User {
  id: number
  name: string
  email: string
  role: string
}

export function useAuth() {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      user.value = data.user
      token.value = data.token
      localStorage.setItem('token', data.token)

      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const fetchUser = async () => {
    if (!token.value) return

    try {
      const response = await fetch('/api/user', {
        headers: { Authorization: `Bearer ${token.value}` }
      })

      user.value = await response.json()
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchUser
  }
}
```

```vue
<!-- Using composables in component -->
<script setup lang="ts">
import { useCounter } from '@/composables/useCounter'
import { useLocalStorage } from '@/composables/useLocalStorage'
import { useFetch } from '@/composables/useFetch'
import { useAuth } from '@/composables/useAuth'

// Use counter
const { count, doubled, increment, decrement, reset } = useCounter(10)

// Use localStorage
const { data: settings } = useLocalStorage('settings', {
  theme: 'dark',
  notifications: true
})

// Use fetch
const { data: posts, loading, error, refresh } = useFetch('/api/posts')

// Use auth
const { user, isAuthenticated, login, logout } = useAuth()
</script>

<template>
  <div>
    <div v-if="isAuthenticated">
      <p>Welcome, {{ user?.name }}!</p>
      <button @click="logout">Logout</button>
    </div>

    <div>
      <h2>Count: {{ count }}</h2>
      <p>Doubled: {{ doubled }}</p>
      <button @click="increment">+</button>
      <button @click="decrement">-</button>
      <button @click="reset">Reset</button>
    </div>

    <div v-if="loading">Loading posts...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <ul v-else>
      <li v-for="post in posts" :key="post.id">
        {{ post.title }}
      </li>
    </ul>
  </div>
</template>
```

### Pattern 8: Provide/Inject for Dependency Injection

```vue
<!-- ParentComponent.vue -->
<script setup lang="ts">
import { ref, provide, readonly, type InjectionKey } from 'vue'

// Define types for injection
interface Theme {
  primary: string
  secondary: string
  background: string
}

interface AppConfig {
  apiUrl: string
  version: string
}

// Create injection keys for type safety
export const ThemeKey: InjectionKey<Theme> = Symbol('theme')
export const ConfigKey: InjectionKey<AppConfig> = Symbol('config')
export const UserKey: InjectionKey<Ref<User | null>> = Symbol('user')

// Provide simple values
const theme: Theme = {
  primary: '#007bff',
  secondary: '#6c757d',
  background: '#ffffff'
}

const config: AppConfig = {
  apiUrl: 'https://api.example.com',
  version: '1.0.0'
}

provide(ThemeKey, theme)
provide(ConfigKey, config)

// Provide reactive data
const user = ref<User | null>(null)
provide(UserKey, readonly(user)) // readonly prevents child modification

// Provide methods
provide('updateUser', (newUser: User) => {
  user.value = newUser
})

// Provide reactive state with methods
const count = ref(0)
provide('count', readonly(count))
provide('increment', () => count.value++)
provide('decrement', () => count.value--)
</script>

<template>
  <div>
    <ChildComponent />
    <GrandchildComponent />
  </div>
</template>
```

```vue
<!-- ChildComponent.vue -->
<script setup lang="ts">
import { inject } from 'vue'
import { ThemeKey, ConfigKey, UserKey } from './ParentComponent.vue'

// Inject with type safety
const theme = inject(ThemeKey)
const config = inject(ConfigKey)
const user = inject(UserKey)

// Inject with default value
const apiUrl = inject('apiUrl', 'https://default.example.com')

// Inject methods
const updateUser = inject<(user: User) => void>('updateUser')

// Inject count and methods
const count = inject<Readonly<Ref<number>>>('count')
const increment = inject<() => void>('increment')
const decrement = inject<() => void>('decrement')
</script>

<template>
  <div :style="{ color: theme?.primary }">
    <p>API: {{ config?.apiUrl }}</p>
    <p>User: {{ user?.name }}</p>
    <p>Count: {{ count }}</p>

    <button @click="increment">+</button>
    <button @click="decrement">-</button>
  </div>
</template>
```

### Pattern 9: Teleport for Portal Rendering

```vue
<script setup lang="ts">
import { ref } from 'vue'

const showModal = ref(false)
const showTooltip = ref(false)

const openModal = () => {
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}
</script>

<template>
  <div class="component">
    <button @click="openModal">Open Modal</button>
    <button @mouseenter="showTooltip = true" @mouseleave="showTooltip = false">
      Hover for Tooltip
    </button>

    <!-- Teleport to body for modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h2>Modal Title</h2>
          <p>Modal content goes here</p>
          <button @click="closeModal">Close</button>
        </div>
      </div>
    </Teleport>

    <!-- Teleport to specific element -->
    <Teleport to="#tooltip-container">
      <div v-if="showTooltip" class="tooltip">
        Tooltip content
      </div>
    </Teleport>

    <!-- Conditional teleport -->
    <Teleport :to="isMobile ? '#mobile-menu' : '#desktop-menu'" :disabled="!shouldTeleport">
      <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
      </nav>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.tooltip {
  position: absolute;
  background: #333;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}
</style>
```

### Pattern 10: Suspense for Async Components

```vue
<!-- AsyncComponent.vue -->
<script setup lang="ts">
// Async setup - component waits for promise to resolve
const data = await fetch('/api/data').then(r => r.json())

// Multiple async operations
const [users, posts] = await Promise.all([
  fetch('/api/users').then(r => r.json()),
  fetch('/api/posts').then(r => r.json())
])
</script>

<template>
  <div>
    <h2>Loaded Data</h2>
    <pre>{{ data }}</pre>
  </div>
</template>
```

```vue
<!-- ParentComponent.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import AsyncComponent from './AsyncComponent.vue'

const showAsync = ref(true)
const error = ref<Error | null>(null)

const handleError = (err: Error) => {
  error.value = err
  console.error('Error loading component:', err)
}
</script>

<template>
  <div>
    <button @click="showAsync = !showAsync">Toggle Async</button>

    <Suspense v-if="showAsync" @error="handleError">
      <!-- Default slot: async component -->
      <template #default>
        <AsyncComponent />
      </template>

      <!-- Fallback slot: loading state -->
      <template #fallback>
        <div class="loading">Loading data...</div>
      </template>
    </Suspense>

    <!-- Error handling -->
    <div v-if="error" class="error">
      Failed to load: {{ error.message }}
    </div>

    <!-- Multiple async components -->
    <Suspense>
      <template #default>
        <div>
          <AsyncComponent />
          <AnotherAsyncComponent />
          <ThirdAsyncComponent />
        </div>
      </template>

      <template #fallback>
        <div>Loading multiple components...</div>
      </template>
    </Suspense>
  </div>
</template>
```

## Advanced Patterns

### Pattern 11: Composable Composition

```typescript
// composables/useApi.ts
import { ref } from 'vue'

export function useApi(baseUrl: string) {
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const get = async <T>(endpoint: string): Promise<T | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${baseUrl}${endpoint}`)
      return await response.json()
    } catch (e) {
      error.value = e as Error
      return null
    } finally {
      loading.value = false
    }
  }

  const post = async <T>(endpoint: string, data: any): Promise<T | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      return await response.json()
    } catch (e) {
      error.value = e as Error
      return null
    } finally {
      loading.value = false
    }
  }

  return { loading, error, get, post }
}

// composables/useUsers.ts - Composes useApi
import { ref } from 'vue'
import { useApi } from './useApi'

interface User {
  id: number
  name: string
  email: string
}

export function useUsers() {
  const api = useApi('/api')
  const users = ref<User[]>([])
  const selectedUser = ref<User | null>(null)

  const fetchUsers = async () => {
    const data = await api.get<User[]>('/users')
    if (data) users.value = data
  }

  const fetchUser = async (id: number) => {
    const data = await api.get<User>(`/users/${id}`)
    if (data) selectedUser.value = data
  }

  const createUser = async (userData: Omit<User, 'id'>) => {
    const data = await api.post<User>('/users', userData)
    if (data) {
      users.value.push(data)
      return data
    }
    return null
  }

  return {
    users,
    selectedUser,
    loading: api.loading,
    error: api.error,
    fetchUsers,
    fetchUser,
    createUser
  }
}

// composables/usePagination.ts - Can be composed with any data source
import { ref, computed } from 'vue'

export function usePagination<T>(items: Ref<T[]>, itemsPerPage = 10) {
  const currentPage = ref(1)

  const totalPages = computed(() =>
    Math.ceil(items.value.length / itemsPerPage)
  )

  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage
    const end = start + itemsPerPage
    return items.value.slice(start, end)
  })

  const nextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  return {
    currentPage,
    totalPages,
    paginatedItems,
    nextPage,
    prevPage,
    goToPage
  }
}

// Using composed composables
import { useUsers } from '@/composables/useUsers'
import { usePagination } from '@/composables/usePagination'

const { users, loading, error, fetchUsers } = useUsers()
const { paginatedItems, currentPage, totalPages, nextPage, prevPage } =
  usePagination(users, 20)

onMounted(fetchUsers)
```

### Pattern 12: Advanced Reactivity Patterns

```vue
<script setup lang="ts">
import {
  ref,
  reactive,
  shallowRef,
  shallowReactive,
  triggerRef,
  toRaw,
  markRaw,
  readonly
} from 'vue'

// shallowRef: Only .value is reactive, not nested properties
const shallowState = shallowRef({
  count: 0,
  nested: { value: 1 }
})

// This triggers reactivity
shallowState.value = { count: 1, nested: { value: 2 } }

// This does NOT trigger reactivity
shallowState.value.count = 2

// Manually trigger reactivity
triggerRef(shallowState)

// shallowReactive: Only root-level properties are reactive
const shallowObj = shallowReactive({
  count: 0,
  nested: { value: 1 }
})

// This triggers reactivity
shallowObj.count = 1

// This does NOT trigger reactivity
shallowObj.nested.value = 2

// toRaw: Get the original non-reactive object
const state = reactive({ count: 0 })
const raw = toRaw(state)
raw.count++ // Does not trigger reactivity

// markRaw: Mark object to never be made reactive
class ThirdPartyLibrary {
  // Large object that shouldn't be reactive
  data = new Array(10000).fill(0)
}

const lib = markRaw(new ThirdPartyLibrary())
const reactiveState = reactive({
  library: lib // Won't be made reactive
})

// readonly: Create read-only reactive object
const original = reactive({ count: 0 })
const readOnlyCopy = readonly(original)

// This works
original.count++

// This produces a warning in development
// readOnlyCopy.count++ // Warning: Set operation failed

// Performance optimization for large lists
const hugeList = shallowRef<any[]>([])

const updateHugeList = (newList: any[]) => {
  // Replace entire array instead of mutating
  hugeList.value = newList
}

// Custom ref with get/set interceptors
import { customRef } from 'vue'

function useDebouncedRef<T>(value: T, delay = 200) {
  let timeout: NodeJS.Timeout

  return customRef((track, trigger) => ({
    get() {
      track()
      return value
    },
    set(newValue: T) {
      clearTimeout(timeout)
      timeout = setTimeout(() => {
        value = newValue
        trigger()
      }, delay)
    }
  }))
}

const debouncedSearch = useDebouncedRef('', 500)
</script>
```

## Testing Strategies

### Testing Composables

```typescript
// composables/useCounter.test.ts
import { describe, it, expect } from 'vitest'
import { useCounter } from '@/composables/useCounter'

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { count } = useCounter()
    expect(count.value).toBe(0)
  })

  it('initializes with custom value', () => {
    const { count } = useCounter(10)
    expect(count.value).toBe(10)
  })

  it('increments count', () => {
    const { count, increment } = useCounter(0)
    increment()
    expect(count.value).toBe(1)
  })

  it('decrements count', () => {
    const { count, decrement } = useCounter(5)
    decrement()
    expect(count.value).toBe(4)
  })

  it('resets to initial value', () => {
    const { count, increment, reset } = useCounter(10)
    increment()
    increment()
    expect(count.value).toBe(12)
    reset()
    expect(count.value).toBe(10)
  })

  it('computes doubled value', () => {
    const { count, doubled, increment } = useCounter(3)
    expect(doubled.value).toBe(6)
    increment()
    expect(doubled.value).toBe(8)
  })
})

// composables/useFetch.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useFetch } from '@/composables/useFetch'

describe('useFetch', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('fetches data successfully', async () => {
    const mockData = { id: 1, name: 'Test' }
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    })

    const { data, loading, error, execute } = useFetch('/api/test', {
      immediate: false
    })

    expect(loading.value).toBe(false)

    await execute()

    expect(data.value).toEqual(mockData)
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('handles errors', async () => {
    ;(global.fetch as any).mockRejectedValueOnce(
      new Error('Network error')
    )

    const { data, error, execute } = useFetch('/api/test', {
      immediate: false
    })

    await execute()

    expect(data.value).toBeNull()
    expect(error.value).toBeInstanceOf(Error)
    expect(error.value?.message).toBe('Network error')
  })
})
```

### Testing Components with Composition API

```typescript
// components/Counter.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Counter from '@/components/Counter.vue'

describe('Counter', () => {
  it('renders initial count', () => {
    const wrapper = mount(Counter, {
      props: { initialCount: 5 }
    })

    expect(wrapper.text()).toContain('Count: 5')
  })

  it('increments on button click', async () => {
    const wrapper = mount(Counter)

    await wrapper.find('button.increment').trigger('click')

    expect(wrapper.text()).toContain('Count: 1')
  })

  it('emits update event', async () => {
    const wrapper = mount(Counter)

    await wrapper.find('button.increment').trigger('click')

    expect(wrapper.emitted()).toHaveProperty('update:count')
    expect(wrapper.emitted('update:count')?.[0]).toEqual([1])
  })

  it('displays doubled value', async () => {
    const wrapper = mount(Counter, {
      props: { initialCount: 3 }
    })

    expect(wrapper.text()).toContain('Doubled: 6')
  })
})

// Testing with composables
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UserList from '@/components/UserList.vue'
import { useUsers } from '@/composables/useUsers'

vi.mock('@/composables/useUsers')

describe('UserList', () => {
  it('displays loading state', () => {
    vi.mocked(useUsers).mockReturnValue({
      users: ref([]),
      loading: ref(true),
      error: ref(null),
      fetchUsers: vi.fn()
    })

    const wrapper = mount(UserList)
    expect(wrapper.text()).toContain('Loading')
  })

  it('displays users', () => {
    vi.mocked(useUsers).mockReturnValue({
      users: ref([
        { id: 1, name: 'John', email: 'john@example.com' },
        { id: 2, name: 'Jane', email: 'jane@example.com' }
      ]),
      loading: ref(false),
      error: ref(null),
      fetchUsers: vi.fn()
    })

    const wrapper = mount(UserList)
    expect(wrapper.text()).toContain('John')
    expect(wrapper.text()).toContain('Jane')
  })
})
```

## Common Pitfalls

### Pitfall 1: Forgetting .value with Refs

```typescript
// WRONG
const count = ref(0)
count++ // Error: Can't increment Ref object

// CORRECT
const count = ref(0)
count.value++
```

### Pitfall 2: Destructuring Reactive Objects

```typescript
// WRONG: Loses reactivity
const state = reactive({ count: 0, name: 'John' })
const { count, name } = state // Not reactive!

// CORRECT: Use toRefs
const state = reactive({ count: 0, name: 'John' })
const { count, name } = toRefs(state) // Reactive refs
```

### Pitfall 3: Mutating Props

```typescript
// WRONG
const props = defineProps<{ count: number }>()
props.count++ // Error: Props are readonly

// CORRECT: Use local state or emit event
const props = defineProps<{ count: number }>()
const localCount = ref(props.count)
localCount.value++

// Or emit to parent
const emit = defineEmits<{ (e: 'update:count', value: number): void }>()
const increment = () => emit('update:count', props.count + 1)
```

### Pitfall 4: Side Effects in Computed

```typescript
// WRONG: Side effects in computed
const doubled = computed(() => {
  console.log('Computing...') // Side effect
  apiCall() // Side effect
  return count.value * 2
})

// CORRECT: Use watchEffect for side effects
const doubled = computed(() => count.value * 2)

watchEffect(() => {
  console.log('Count changed:', count.value)
})
```

### Pitfall 5: Not Cleaning Up in onUnmounted

```typescript
// WRONG: Memory leak
onMounted(() => {
  const interval = setInterval(() => {
    console.log('Tick')
  }, 1000)
})

// CORRECT: Clean up
onMounted(() => {
  const interval = setInterval(() => {
    console.log('Tick')
  }, 1000)

  onUnmounted(() => {
    clearInterval(interval)
  })
})
```

## Best Practices

1. **Use script setup** for cleaner, more performant code
2. **Prefer ref() for primitives** and reactive() for objects
3. **Create composables** for reusable logic (use* naming convention)
4. **Use computed()** for derived state (automatically cached)
5. **Clean up side effects** in onUnmounted hook
6. **Use TypeScript** for type safety with defineProps/defineEmits
7. **Avoid mutating props** - emit events to parent instead
8. **Use provide/inject** sparingly - prefer props for direct parent-child
9. **Leverage template refs** for DOM access when needed
10. **Test composables independently** from components

## Resources

- **Vue 3 Documentation**: https://vuejs.org/guide/introduction.html
- **Composition API RFC**: https://vuejs.org/api/composition-api-setup.html
- **VueUse**: Collection of essential Vue composables
- **TypeScript with Vue**: https://vuejs.org/guide/typescript/overview.html
- **Testing Library**: https://testing-library.com/docs/vue-testing-library
