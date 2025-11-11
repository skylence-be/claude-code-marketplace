---
description: Create a new Pinia store for state management
model: claude-sonnet-4-5
---

Create a new Pinia store following best practices.

## Store Specification

$ARGUMENTS

## Pinia Store Best Practices

### 1. **Setup Store (Recommended)**

```ts
// stores/useUserStore.ts
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => user.value !== null)

  // Actions
  const setUser = (newUser: User) => {
    user.value = newUser
  }

  const logout = () => {
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    setUser,
    logout
  }
})
```

### 2. **Options Store** (Alternative)

```ts
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null,
    userName: (state) => state.user?.name ?? 'Guest'
  },

  actions: {
    async fetchUser() {
      this.loading = true
      try {
        this.user = await $fetch('/api/user')
      } finally {
        this.loading = false
      }
    }
  }
})
```

### 3. **TypeScript Types**

```ts
interface User {
  id: string
  name: string
  email: string
}

interface UserState {
  user: User | null
  loading: boolean
  error: Error | null
}
```

### 4. **Persisted State**

```ts
import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref<'light' | 'dark'>('light')

  return { theme }
}, {
  persist: true  // Automatically persists to localStorage
})
```

### 5. **Async Actions**

```ts
export const useDataStore = defineStore('data', () => {
  const data = ref<Data[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const fetchData = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Data[]>('/api/data')
      data.value = response
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetchData }
})
```

Generate a complete, production-ready Pinia store with TypeScript.
