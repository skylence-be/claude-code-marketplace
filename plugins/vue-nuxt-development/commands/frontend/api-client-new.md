---
description: Create API client/service for backend integration
model: claude-sonnet-4-5
---

Create an API client or service for backend integration.

## API Specification

$ARGUMENTS

## API Client Patterns

### 1. **Composable-Based API Client**

```ts
// composables/useApi.ts
export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase

  const get = async <T>(endpoint: string) => {
    return await $fetch<T>(`${baseURL}${endpoint}`)
  }

  const post = async <T>(endpoint: string, data: any) => {
    return await $fetch<T>(`${baseURL}${endpoint}`, {
      method: 'POST',
      body: data
    })
  }

  const put = async <T>(endpoint: string, data: any) => {
    return await $fetch<T>(`${baseURL}${endpoint}`, {
      method: 'PUT',
      body: data
    })
  }

  const del = async <T>(endpoint: string) => {
    return await $fetch<T>(`${baseURL}${endpoint}`, {
      method: 'DELETE'
    })
  }

  return { get, post, put, del }
}
```

### 2. **Resource-Specific Service**

```ts
// services/userService.ts
export const userService = {
  async getUser(id: string): Promise<User> {
    return await $fetch(`/api/users/${id}`)
  },

  async createUser(data: CreateUserDto): Promise<User> {
    return await $fetch('/api/users', {
      method: 'POST',
      body: data
    })
  },

  async updateUser(id: string, data: UpdateUserDto): Promise<User> {
    return await $fetch(`/api/users/${id}`, {
      method: 'PUT',
      body: data
    })
  },

  async deleteUser(id: string): Promise<void> {
    await $fetch(`/api/users/${id}`, {
      method: 'DELETE'
    })
  }
}
```

### 3. **With Authentication**

```ts
export function useAuthenticatedApi() {
  const token = useCookie('auth-token')

  const fetchWithAuth = async <T>(url: string, options: any = {}) => {
    return await $fetch<T>(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token.value}`
      }
    })
  }

  return { fetchWithAuth }
}
```

### 4. **Error Handling**

```ts
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public data?: any
  ) {
    super(message)
  }
}

export async function apiRequest<T>(url: string, options: any = {}): Promise<T> {
  try {
    return await $fetch<T>(url, options)
  } catch (error: any) {
    throw new ApiError(
      error.statusCode || 500,
      error.message || 'An error occurred',
      error.data
    )
  }
}
```

Generate a complete, type-safe API client with error handling.
