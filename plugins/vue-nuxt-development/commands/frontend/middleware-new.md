---
description: Create Nuxt route middleware
model: claude-sonnet-4-5
---

Create Nuxt route middleware.

## Middleware Specification

$ARGUMENTS

## Middleware Patterns

### 1. **Named Middleware**

```ts
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
```

### 2. **Global Middleware**

```ts
// middleware/log.global.ts
export default defineNuxtRouteMiddleware((to, from) => {
  console.log(`Navigating from ${from.path} to ${to.path}`)
})
```

### 3. **With Async Logic**

```ts
export default defineNuxtRouteMiddleware(async (to, from) => {
  const user = await fetchUser()

  if (!user.hasPermission(to.meta.permission)) {
    return abortNavigation()
  }
})
```

Generate complete, type-safe Nuxt middleware.
