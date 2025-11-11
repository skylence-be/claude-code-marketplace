---
description: Create a new Vue composable for reusable logic
model: claude-sonnet-4-5
---

Create a new Vue composable following best practices.

## Composable Specification

$ARGUMENTS

## Vue Composable Standards

### 1. **Naming Convention**

- Prefix with `use`: `useAuth`, `useApi`, `useFetch`
- Describe what it does: `useLocalStorage`, `useDebounce`
- Place in `composables/` directory (auto-imported in Nuxt)

### 2. **Basic Structure**

```ts
// composables/useCounter.ts
import { ref, computed } from 'vue'

export function useCounter(initial = 0) {
  const count = ref(initial)

  const doubled = computed(() => count.value * 2)

  const increment = () => {
    count.value++
  }

  const decrement = () => {
    count.value--
  }

  return {
    count: readonly(count),
    doubled,
    increment,
    decrement
  }
}
```

### 3. **TypeScript Typing**

```ts
interface UseCounterOptions {
  initial?: number
  step?: number
}

interface UseCounterReturn {
  count: Readonly<Ref<number>>
  increment: () => void
  decrement: () => void
}

export function useCounter(
  options: UseCounterOptions = {}
): UseCounterReturn {
  // implementation
}
```

### 4. **Async Composables**

```ts
export function useAsyncData<T>(url: string) {
  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)

  const fetch = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<T>(url)
      data.value = response
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return { data, error, loading, fetch, refetch: fetch }
}
```

### 5. **Lifecycle Hooks**

```ts
export function useInterval(callback: () => void, delay: number) {
  let intervalId: NodeJS.Timeout | null = null

  const start = () => {
    if (intervalId) return
    intervalId = setInterval(callback, delay)
  }

  const stop = () => {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  onMounted(start)
  onUnmounted(stop)

  return { start, stop }
}
```

### 6. **State Management**

```ts
// Shared state across components
const count = ref(0)

export function useSharedCounter() {
  const increment = () => count.value++
  const decrement = () => count.value--

  return {
    count: readonly(count),
    increment,
    decrement
  }
}
```

### 7. **Nuxt-Specific Patterns**

**SSR-Safe State**
```ts
export function useState<T>(key: string, init: () => T) {
  return useState(key, init)
}
```

**API Composable**
```ts
export function useApi() {
  const get = <T>(url: string) => $fetch<T>(url)
  const post = <T>(url: string, body: any) =>
    $fetch<T>(url, { method: 'POST', body })

  return { get, post }
}
```

### 8. **Common Composable Patterns**

**useLocalStorage**
```ts
export function useLocalStorage<T>(
  key: string,
  defaultValue: T
) {
  const data = ref<T>(defaultValue)

  onMounted(() => {
    const stored = localStorage.getItem(key)
    if (stored) {
      data.value = JSON.parse(stored)
    }
  })

  watch(data, (value) => {
    localStorage.setItem(key, JSON.stringify(value))
  }, { deep: true })

  return data
}
```

**useDebounce**
```ts
export function useDebounce<T>(
  value: Ref<T>,
  delay: number
): Readonly<Ref<T>> {
  const debouncedValue = ref(value.value) as Ref<T>

  watch(value, (newValue) => {
    setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })

  return readonly(debouncedValue)
}
```

## Best Practices

**Composable Design**
- ✓ Single Responsibility
- ✓ Return reactive values
- ✓ Accept reactive parameters
- ✓ Clean up in `onUnmounted`

**TypeScript**
- ✓ Type all parameters
- ✓ Type return values
- ✓ Use generics for flexibility
- ✓ No `any` types

**Reactivity**
- ✓ Use `ref`/`reactive` for state
- ✓ Use `computed` for derived values
- ✓ Use `readonly` to prevent mutations
- ✓ Clean up watchers

**Error Handling**
- ✓ Try/catch for async operations
- ✓ Return error state
- ✓ Provide retry mechanisms
- ✓ Handle edge cases

Generate production-ready, reusable Vue composables with proper TypeScript types.
