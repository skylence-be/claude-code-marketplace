---
name: typescript-vue-patterns
description: Master TypeScript integration with Vue 3 including component prop types (defineProps<T>), emit types (defineEmits<T>), template refs, composable types, generic components, type-safe routing, API client types, and tsconfig optimization. Use when building type-safe Vue applications with full IDE support.
category: frontend
tags: [typescript, vue3, type-safety, generics, inference]
related_skills: [vue3-composition-api-patterns, pinia-state-patterns, vitest-testing-patterns]
---

# TypeScript Vue Patterns

Comprehensive guide to implementing type-safe Vue 3 applications with TypeScript, covering component prop and emit types, template ref typing, composable return types, generic components, type-safe routing, API client patterns, discriminated unions, type guards, and tsconfig optimization for maximum type safety and developer experience.

## When to Use This Skill

- Building type-safe Vue 3 components with full IDE autocomplete
- Defining prop and emit types with defineProps<T> and defineEmits<T>
- Creating reusable generic components with type parameters
- Implementing type-safe composables with proper return types
- Working with template refs and DOM element types
- Building type-safe API clients with request/response types
- Implementing discriminated unions for complex state management
- Using type guards for runtime type narrowing
- Optimizing tsconfig.json for Vue 3 and Nuxt 4 projects
- Ensuring type safety across component hierarchy and state

## Core Concepts

### 1. Component Types
- **defineProps<T>**: Type-safe props with generics
- **defineEmits<T>**: Type-safe event emissions
- **withDefaults()**: Props with default values and types
- **Component instances**: InstanceType for component refs
- **Slots typing**: Type-safe slot definitions

### 2. Reactivity Types
- **Ref<T>**: Reference type with value access
- **Reactive<T>**: Reactive object proxy type
- **ComputedRef<T>**: Computed property type
- **UnwrapRef<T>**: Unwrap nested ref types
- **ToRefs<T>**: Convert reactive object to refs

### 3. Composable Types
- Return type inference for composables
- Generic composables with type parameters
- Async composable return types
- Type-safe state management patterns
- Conditional types for flexibility

### 4. Advanced Types
- **Generic components**: Components with type parameters
- **Discriminated unions**: Type-safe state variants
- **Type guards**: Runtime type checking
- **Utility types**: Partial, Pick, Omit, Required
- **Template literal types**: Dynamic string types

### 5. Configuration
- tsconfig.json optimization for Vue/Nuxt
- Strict mode configuration
- Path aliases and module resolution
- Type checking performance
- Vue TypeScript plugin

## Quick Start

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

// Define prop types
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// Define emit types
interface Emits {
  (e: 'update:count', value: number): void
  (e: 'submit'): void
}

const emit = defineEmits<Emits>()

// Type-safe refs
const message = ref<string>('Hello')
const isActive = ref<boolean>(true)

// Computed with type inference
const doubled = computed(() => props.count * 2)

// Type-safe methods
const increment = (): void => {
  emit('update:count', props.count + 1)
}
</script>

<template>
  <div>
    <h1>{{ title }}</h1>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>
```

## Fundamental Patterns

### Pattern 1: Component Props with TypeScript

```vue
<script setup lang="ts">
// Simple props with interface
interface Props {
  title: string
  subtitle?: string
  count: number
  items: string[]
  config: {
    theme: 'light' | 'dark'
    size: 'sm' | 'md' | 'lg'
  }
}

const props = defineProps<Props>()

// Props with defaults
interface PropsWithDefaults {
  title: string
  count?: number
  isActive?: boolean
  items?: string[]
  variant?: 'primary' | 'secondary' | 'danger'
}

const propsWithDefaults = withDefaults(defineProps<PropsWithDefaults>(), {
  count: 0,
  isActive: true,
  items: () => [],
  variant: 'primary'
})

// Complex nested types
interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'user' | 'guest'
  permissions: string[]
  metadata?: Record<string, any>
}

interface UserCardProps {
  user: User
  showEmail?: boolean
  onEdit?: (user: User) => void
  onDelete?: (id: number) => Promise<void>
}

const userProps = defineProps<UserCardProps>()

// Using type imports
import type { Product, Category } from '@/types'

interface ProductProps {
  product: Product
  category: Category
  relatedProducts?: Product[]
}

const productProps = defineProps<ProductProps>()

// Union types for flexibility
interface FlexibleProps {
  value: string | number | boolean
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  status: 'idle' | 'loading' | 'success' | 'error'
}

const flexProps = defineProps<FlexibleProps>()

// Readonly and Required utilities
interface ConfigProps {
  config: Readonly<{
    apiUrl: string
    timeout: number
  }>
  settings: Required<{
    theme: string
    locale: string
  }>
}

const configProps = defineProps<ConfigProps>()
</script>

<template>
  <div>
    <h1>{{ title }}</h1>
    <p>{{ subtitle }}</p>
    <p>Count: {{ count }}</p>
  </div>
</template>
```

### Pattern 2: Event Emits with TypeScript

```vue
<script setup lang="ts">
import type { User, ValidationError } from '@/types'

// Simple emit types
interface SimpleEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'submit'): void
}

const emitSimple = defineEmits<SimpleEmits>()

// Complex emit types with multiple parameters
interface ComplexEmits {
  (e: 'update:user', user: User): void
  (e: 'delete', id: number, confirmed: boolean): void
  (e: 'error', error: Error, context: string): void
  (e: 'validate', field: string, isValid: boolean): void
}

const emitComplex = defineEmits<ComplexEmits>()

// Generic emit types
interface GenericEmits<T> {
  (e: 'update:value', value: T): void
  (e: 'change', oldValue: T, newValue: T): void
}

// With validation (object syntax)
const emitWithValidation = defineEmits({
  submit: (payload: { name: string; email: string }) => {
    // Validation logic
    return payload.name.length > 0 && payload.email.includes('@')
  },
  delete: (id: number) => {
    return typeof id === 'number' && id > 0
  },
  'update:modelValue': (value: string) => {
    return typeof value === 'string'
  }
})

// Usage in methods
const handleSubmit = () => {
  emitSimple('submit')
}

const handleUserUpdate = (user: User) => {
  emitComplex('update:user', user)
}

const handleDelete = (id: number) => {
  emitComplex('delete', id, true)
}

const handleError = (error: Error) => {
  emitComplex('error', error, 'form-validation')
}

// v-model implementation with types
interface ModelEmits {
  (e: 'update:modelValue', value: string): void
}

const modelEmit = defineEmits<ModelEmits>()

const props = defineProps<{
  modelValue: string
}>()

const localValue = computed({
  get: () => props.modelValue,
  set: (value: string) => modelEmit('update:modelValue', value)
})
</script>

<template>
  <div>
    <input v-model="localValue" @change="handleSubmit">
    <button @click="handleDelete(1)">Delete</button>
  </div>
</template>
```

### Pattern 3: Template Refs with TypeScript

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ComponentPublicInstance } from 'vue'
import ChildComponent from './ChildComponent.vue'

// DOM element refs
const inputRef = ref<HTMLInputElement | null>(null)
const divRef = ref<HTMLDivElement | null>(null)
const buttonRef = ref<HTMLButtonElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)

// Component refs
const childRef = ref<InstanceType<typeof ChildComponent> | null>(null)

// Array of refs for v-for
const itemRefs = ref<HTMLElement[]>([])

// Generic element ref
const genericRef = ref<HTMLElement | null>(null)

// SVG element refs
const svgRef = ref<SVGSVGElement | null>(null)
const pathRef = ref<SVGPathElement | null>(null)

onMounted(() => {
  // Type-safe DOM access
  if (inputRef.value) {
    inputRef.value.focus()
    const value: string = inputRef.value.value
    console.log('Input value:', value)
  }

  if (divRef.value) {
    const rect: DOMRect = divRef.value.getBoundingClientRect()
    console.log('Div dimensions:', rect.width, rect.height)
  }

  if (buttonRef.value) {
    buttonRef.value.disabled = false
    buttonRef.value.classList.add('active')
  }

  if (canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    if (ctx) {
      ctx.fillRect(0, 0, 100, 100)
    }
  }

  // Access child component methods
  if (childRef.value) {
    childRef.value.someMethod()
    const childData = childRef.value.someProperty
  }

  // Array of refs
  itemRefs.value.forEach((el, index) => {
    el.style.order = index.toString()
  })
})

// Type-safe method using refs
const focusInput = (): void => {
  inputRef.value?.focus()
}

const measureElement = (): { width: number; height: number } | null => {
  if (!divRef.value) return null

  const rect = divRef.value.getBoundingClientRect()
  return {
    width: rect.width,
    height: rect.height
  }
}

// Custom ref type with methods
interface CustomElement extends HTMLElement {
  customMethod(): void
}

const customRef = ref<CustomElement | null>(null)
</script>

<template>
  <div>
    <input ref="inputRef" type="text">
    <div ref="divRef">Content</div>
    <button ref="buttonRef">Click</button>
    <canvas ref="canvasRef"></canvas>

    <ChildComponent ref="childRef" />

    <div
      v-for="(item, index) in items"
      :key="item.id"
      :ref="(el) => { itemRefs[index] = el as HTMLElement }"
    >
      {{ item.name }}
    </div>
  </div>
</template>
```

### Pattern 4: Composable Types

```typescript
// composables/useCounter.ts
import { ref, computed, type Ref, type ComputedRef } from 'vue'

// Explicit return type
export interface UseCounterReturn {
  count: Ref<number>
  doubled: ComputedRef<number>
  increment: () => void
  decrement: () => void
  reset: () => void
}

export function useCounter(initialValue = 0): UseCounterReturn {
  const count = ref(initialValue)
  const doubled = computed(() => count.value * 2)

  const increment = (): void => {
    count.value++
  }

  const decrement = (): void => {
    count.value--
  }

  const reset = (): void => {
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

// composables/useFetch.ts
import { ref, type Ref } from 'vue'

export interface UseFetchOptions {
  immediate?: boolean
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

export interface UseFetchReturn<T> {
  data: Ref<T | null>
  error: Ref<Error | null>
  loading: Ref<boolean>
  execute: () => Promise<void>
  refresh: () => Promise<void>
}

export function useFetch<T>(
  url: string | Ref<string>,
  options: UseFetchOptions = {}
): UseFetchReturn<T> {
  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)

  const execute = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(typeof url === 'string' ? url : url.value)
      const json = await response.json()
      data.value = json

      options.onSuccess?.(json)
    } catch (e) {
      error.value = e as Error
      options.onError?.(e as Error)
    } finally {
      loading.value = false
    }
  }

  if (options.immediate !== false) {
    execute()
  }

  return {
    data,
    error,
    loading,
    execute,
    refresh: execute
  }
}

// composables/useLocalStorage.ts
export function useLocalStorage<T>(
  key: string,
  defaultValue: T
): {
  data: Ref<T>
  remove: () => void
  reset: () => void
} {
  const data = ref<T>(defaultValue) as Ref<T>

  // Initialize from localStorage
  if (process.client) {
    const stored = localStorage.getItem(key)
    if (stored) {
      try {
        data.value = JSON.parse(stored)
      } catch (e) {
        console.error('Failed to parse localStorage:', e)
      }
    }
  }

  // Watch and persist
  watch(
    data,
    (newValue) => {
      if (process.client) {
        localStorage.setItem(key, JSON.stringify(newValue))
      }
    },
    { deep: true }
  )

  const remove = (): void => {
    if (process.client) {
      localStorage.removeItem(key)
    }
  }

  const reset = (): void => {
    data.value = defaultValue
  }

  return { data, remove, reset }
}

// composables/useAuth.ts
import type { User } from '@/types'

export interface UseAuthReturn {
  user: Ref<User | null>
  token: Ref<string | null>
  isAuthenticated: ComputedRef<boolean>
  isAdmin: ComputedRef<boolean>
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => Promise<void>
  fetchUser: () => Promise<void>
}

export function useAuth(): UseAuthReturn {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isAuthenticated = computed((): boolean => {
    return !!user.value && !!token.value
  })

  const isAdmin = computed((): boolean => {
    return user.value?.role === 'admin'
  })

  const login = async (
    email: string,
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      user.value = data.user
      token.value = data.token

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: (error as Error).message
      }
    }
  }

  const logout = async (): Promise<void> => {
    user.value = null
    token.value = null
  }

  const fetchUser = async (): Promise<void> => {
    // Implementation
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

### Pattern 5: Generic Components

```vue
<!-- components/DataList.vue - Generic list component -->
<script setup lang="ts" generic="T extends { id: number | string }">
interface Props {
  items: T[]
  loading?: boolean
  emptyMessage?: string
}

interface Emits {
  (e: 'select', item: T): void
  (e: 'delete', id: T['id']): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  emptyMessage: 'No items found'
})

const emit = defineEmits<Emits>()

const handleSelect = (item: T): void => {
  emit('select', item)
}

const handleDelete = (id: T['id']): void => {
  emit('delete', id)
}
</script>

<template>
  <div class="data-list">
    <div v-if="loading">Loading...</div>
    <div v-else-if="items.length === 0">{{ emptyMessage }}</div>
    <ul v-else>
      <li v-for="item in items" :key="item.id" @click="handleSelect(item)">
        <slot :item="item" :delete="() => handleDelete(item.id)">
          {{ item }}
        </slot>
      </li>
    </ul>
  </div>
</template>
```

```vue
<!-- Usage of generic component -->
<script setup lang="ts">
import DataList from '@/components/DataList.vue'
import type { User, Product } from '@/types'

const users: User[] = [
  { id: 1, name: 'John', email: 'john@example.com' },
  { id: 2, name: 'Jane', email: 'jane@example.com' }
]

const products: Product[] = [
  { id: 1, name: 'Product 1', price: 10 },
  { id: 2, name: 'Product 2', price: 20 }
]

const handleUserSelect = (user: User): void => {
  console.log('Selected user:', user.name)
}

const handleProductSelect = (product: Product): void => {
  console.log('Selected product:', product.name)
}

const handleDelete = (id: number): void => {
  console.log('Delete item:', id)
}
</script>

<template>
  <div>
    <!-- Type-safe with User[] -->
    <DataList :items="users" @select="handleUserSelect" @delete="handleDelete">
      <template #default="{ item, delete: deleteItem }">
        <div>
          <span>{{ item.name }}</span>
          <span>{{ item.email }}</span>
          <button @click="deleteItem">Delete</button>
        </div>
      </template>
    </DataList>

    <!-- Type-safe with Product[] -->
    <DataList :items="products" @select="handleProductSelect" @delete="handleDelete">
      <template #default="{ item }">
        <div>
          <span>{{ item.name }}</span>
          <span>${{ item.price }}</span>
        </div>
      </template>
    </DataList>
  </div>
</template>
```

### Pattern 6: Type-Safe API Client

```typescript
// types/api.ts
export interface ApiResponse<T> {
  data: T
  message: string
  status: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    perPage: number
    total: number
    totalPages: number
  }
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
  status: number
}

// api/client.ts
import type { ApiResponse, PaginatedResponse, ApiError } from '@/types/api'

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  setToken(token: string): void {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers
    })

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.message)
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<ApiResponse<T>>(endpoint, {
      method: 'GET'
    })
  }

  async post<T, D = any>(
    endpoint: string,
    data: D
  ): Promise<ApiResponse<T>> {
    return this.request<ApiResponse<T>>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async put<T, D = any>(
    endpoint: string,
    data: D
  ): Promise<ApiResponse<T>> {
    return this.request<ApiResponse<T>>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async patch<T, D = any>(
    endpoint: string,
    data: D
  ): Promise<ApiResponse<T>> {
    return this.request<ApiResponse<T>>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<ApiResponse<T>>(endpoint, {
      method: 'DELETE'
    })
  }

  async getPaginated<T>(
    endpoint: string,
    page = 1,
    perPage = 10
  ): Promise<PaginatedResponse<T>> {
    return this.request<PaginatedResponse<T>>(
      `${endpoint}?page=${page}&per_page=${perPage}`,
      { method: 'GET' }
    )
  }
}

export const apiClient = new ApiClient('https://api.example.com')

// api/users.ts
import { apiClient } from './client'
import type { User, ApiResponse, PaginatedResponse } from '@/types'

export interface CreateUserData {
  name: string
  email: string
  password: string
}

export interface UpdateUserData {
  name?: string
  email?: string
}

export const usersApi = {
  getAll: (page = 1, perPage = 10): Promise<PaginatedResponse<User>> => {
    return apiClient.getPaginated<User>('/users', page, perPage)
  },

  getById: (id: number): Promise<ApiResponse<User>> => {
    return apiClient.get<User>(`/users/${id}`)
  },

  create: (data: CreateUserData): Promise<ApiResponse<User>> => {
    return apiClient.post<User, CreateUserData>('/users', data)
  },

  update: (id: number, data: UpdateUserData): Promise<ApiResponse<User>> => {
    return apiClient.patch<User, UpdateUserData>(`/users/${id}`, data)
  },

  delete: (id: number): Promise<ApiResponse<void>> => {
    return apiClient.delete<void>(`/users/${id}`)
  }
}
```

### Pattern 7: Discriminated Unions

```typescript
// types/state.ts
export type LoadingState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error }

export type FormState =
  | { type: 'editing'; data: Record<string, any>; isDirty: boolean }
  | { type: 'submitting'; data: Record<string, any> }
  | { type: 'submitted'; id: number }
  | { type: 'error'; error: string; data: Record<string, any> }

export type AuthState =
  | { status: 'unauthenticated' }
  | { status: 'authenticating'; provider: 'google' | 'github' | 'email' }
  | { status: 'authenticated'; user: User; token: string }
  | { status: 'error'; message: string }
```

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { LoadingState, FormState } from '@/types/state'
import type { User } from '@/types'

// Using LoadingState
const userState = ref<LoadingState<User>>({ status: 'idle' })

const fetchUser = async (id: number): Promise<void> => {
  userState.value = { status: 'loading' }

  try {
    const response = await fetch(`/api/users/${id}`)
    const data = await response.json()

    userState.value = { status: 'success', data }
  } catch (error) {
    userState.value = { status: 'error', error: error as Error }
  }
}

// Type guards for narrowing
const isLoading = (state: LoadingState<User>): state is { status: 'loading' } => {
  return state.status === 'loading'
}

const isSuccess = (state: LoadingState<User>): state is { status: 'success'; data: User } => {
  return state.status === 'success'
}

const isError = (state: LoadingState<User>): state is { status: 'error'; error: Error } => {
  return state.status === 'error'
}

// Using FormState
const formState = ref<FormState>({
  type: 'editing',
  data: {},
  isDirty: false
})

const submitForm = async (): Promise<void> => {
  if (formState.value.type !== 'editing') return

  formState.value = {
    type: 'submitting',
    data: formState.value.data
  }

  try {
    const response = await fetch('/api/submit', {
      method: 'POST',
      body: JSON.stringify(formState.value.data)
    })

    const result = await response.json()

    formState.value = {
      type: 'submitted',
      id: result.id
    }
  } catch (error) {
    formState.value = {
      type: 'error',
      error: (error as Error).message,
      data: formState.value.data
    }
  }
}
</script>

<template>
  <div>
    <!-- Type-safe state rendering -->
    <div v-if="userState.status === 'loading'">Loading...</div>
    <div v-else-if="userState.status === 'success'">
      <h1>{{ userState.data.name }}</h1>
      <p>{{ userState.data.email }}</p>
    </div>
    <div v-else-if="userState.status === 'error'">
      Error: {{ userState.error.message }}
    </div>

    <!-- Form state -->
    <form v-if="formState.type === 'editing'" @submit.prevent="submitForm">
      <input v-model="formState.data.name">
      <button :disabled="!formState.isDirty">Submit</button>
    </form>
    <div v-else-if="formState.type === 'submitting'">
      Submitting...
    </div>
    <div v-else-if="formState.type === 'submitted'">
      Success! ID: {{ formState.id }}
    </div>
    <div v-else-if="formState.type === 'error'">
      Error: {{ formState.error }}
    </div>
  </div>
</template>
```

### Pattern 8: Type Guards

```typescript
// utils/type-guards.ts
import type { User, Admin, Guest } from '@/types'

// Primitive type guards
export function isString(value: unknown): value is string {
  return typeof value === 'string'
}

export function isNumber(value: unknown): value is number {
  return typeof value === 'number'
}

export function isArray<T>(value: unknown): value is T[] {
  return Array.isArray(value)
}

// Object type guards
export function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value &&
    'name' in value
  )
}

export function isAdmin(user: User): user is Admin {
  return 'role' in user && user.role === 'admin'
}

export function hasPermission(
  user: User,
  permission: string
): user is User & { permissions: string[] } {
  return (
    'permissions' in user &&
    Array.isArray(user.permissions) &&
    user.permissions.includes(permission)
  )
}

// Nullable type guards
export function isDefined<T>(value: T | undefined | null): value is T {
  return value !== undefined && value !== null
}

export function isNonNullable<T>(value: T): value is NonNullable<T> {
  return value !== null && value !== undefined
}

// Error type guards
export function isError(value: unknown): value is Error {
  return value instanceof Error
}

export function isApiError(value: unknown): value is { message: string; status: number } {
  return (
    typeof value === 'object' &&
    value !== null &&
    'message' in value &&
    'status' in value
  )
}

// Usage in component
const handleValue = (value: unknown): string => {
  if (isString(value)) {
    return value.toUpperCase()
  }

  if (isNumber(value)) {
    return value.toFixed(2)
  }

  if (isArray<string>(value)) {
    return value.join(', ')
  }

  return 'Unknown type'
}

const processUser = (user: User): void => {
  if (isAdmin(user)) {
    // TypeScript knows user is Admin here
    console.log('Admin user:', user.adminLevel)
  }

  if (hasPermission(user, 'write')) {
    // TypeScript knows user has permissions array
    console.log('User can write:', user.permissions)
  }
}
```

## Advanced Patterns

### Pattern 9: Utility Types and Transformations

```typescript
// types/utilities.ts

// Make all properties optional recursively
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// Make specific properties required
export type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>

// Make specific properties optional
export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

// Extract function return type
export type AsyncReturnType<T extends (...args: any) => Promise<any>> =
  T extends (...args: any) => Promise<infer R> ? R : never

// Ensure at least one property is present
export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> =
  Pick<T, Exclude<keyof T, Keys>> &
  {
    [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>>
  }[Keys]

// Usage examples
interface User {
  id: number
  name: string
  email: string
  age?: number
  address?: {
    street: string
    city: string
  }
}

// Make all fields optional recursively
type PartialUser = DeepPartial<User>

// Require specific fields
type UserWithEmail = RequireFields<User, 'email'>

// Make specific fields optional
type UserWithOptionalName = OptionalFields<User, 'name'>

// Extract async function return
async function fetchUser(): Promise<User> {
  return {} as User
}

type FetchedUser = AsyncReturnType<typeof fetchUser> // User

// Require at least one field for update
type UserUpdate = RequireAtLeastOne<Partial<User>>
```

### Pattern 10: tsconfig.json Optimization

```jsonc
// tsconfig.json for Vue 3 / Nuxt 4
{
  "compilerOptions": {
    // Language and Environment
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "jsx": "preserve",

    // Module Resolution
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowImportingTsExtensions": true,
    "types": ["node", "@types/node", "vite/client"],

    // Type Checking - Strict Mode
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,

    // Additional Checks
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    // Emit
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "removeComments": false,
    "noEmit": true,

    // Interop Constraints
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,

    // Performance
    "skipLibCheck": true,
    "incremental": true,

    // Path Aliases
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"],
      "~/*": ["./*"],
      "#app": ["node_modules/nuxt/dist/app"],
      "#imports": [".nuxt/imports"]
    }
  },
  "include": [
    "**/*.ts",
    "**/*.tsx",
    "**/*.vue",
    ".nuxt/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    ".nuxt",
    ".output"
  ],
  // Vue specific
  "vueCompilerOptions": {
    "target": 3,
    "strictTemplates": true
  }
}
```

## Testing Strategies

```typescript
// Component type testing
import { describe, it, expectTypeOf } from 'vitest'
import type { ComponentPublicInstance } from 'vue'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent Types', () => {
  it('has correct prop types', () => {
    type Props = InstanceType<typeof MyComponent>['$props']

    expectTypeOf<Props>().toMatchTypeOf<{
      title: string
      count?: number
    }>()
  })

  it('has correct emit types', () => {
    type Emits = InstanceType<typeof MyComponent>['$emit']

    expectTypeOf<Emits>().toBeFunction()
  })
})

// Composable type testing
describe('useCounter Types', () => {
  it('returns correct types', () => {
    const result = useCounter()

    expectTypeOf(result.count).toEqualTypeOf<Ref<number>>()
    expectTypeOf(result.doubled).toEqualTypeOf<ComputedRef<number>>()
    expectTypeOf(result.increment).toEqualTypeOf<() => void>()
  })
})
```

## Common Pitfalls

### Pitfall 1: Losing Type Safety with Any

```typescript
// WRONG: Using any
const data: any = await fetchData()
data.nonexistent.property // No error!

// CORRECT: Use unknown and type guards
const data: unknown = await fetchData()
if (isUser(data)) {
  console.log(data.name) // Type-safe
}
```

### Pitfall 2: Not Using Generic Constraints

```typescript
// WRONG: No constraint
function getValue<T>(obj: T, key: string) {
  return obj[key] // Error!
}

// CORRECT: Use constraint
function getValue<T extends object, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}
```

### Pitfall 3: Ignoring Null/Undefined

```typescript
// WRONG: Assuming value exists
const user = users.find(u => u.id === 1)
console.log(user.name) // Possible undefined!

// CORRECT: Check before use
const user = users.find(u => u.id === 1)
if (user) {
  console.log(user.name)
}

// Or use optional chaining
console.log(user?.name)
```

## Best Practices

1. **Enable strict mode** in tsconfig.json for maximum type safety
2. **Use generic types** for reusable components and composables
3. **Define explicit return types** for functions and methods
4. **Leverage discriminated unions** for complex state management
5. **Create type guards** for runtime type checking
6. **Use utility types** (Partial, Pick, Omit) for transformations
7. **Avoid any** - use unknown with type guards instead
8. **Type template refs** correctly for DOM access
9. **Use path aliases** for cleaner imports
10. **Test types** with expectTypeOf in Vitest

## Resources

- **TypeScript Documentation**: https://www.typescriptlang.org/docs
- **Vue TypeScript Guide**: https://vuejs.org/guide/typescript/overview.html
- **Nuxt TypeScript**: https://nuxt.com/docs/guide/concepts/typescript
- **TypeScript Playground**: https://www.typescriptlang.org/play
- **Type Challenges**: https://github.com/type-challenges/type-challenges
