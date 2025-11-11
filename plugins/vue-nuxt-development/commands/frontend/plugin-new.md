---
description: Create Nuxt plugin
model: claude-sonnet-4-5
---

Create a Nuxt plugin.

## Plugin Specification

$ARGUMENTS

## Nuxt Plugin Patterns

### 1. **Basic Plugin**

```ts
// plugins/myPlugin.ts
export default defineNuxtPlugin(() => {
  return {
    provide: {
      myFunction: () => 'Hello from plugin!'
    }
  }
})

// Use in components: const { $myFunction } = useNuxtApp()
```

### 2. **With External Library**

```ts
// plugins/analytics.client.ts
export default defineNuxtPlugin(() => {
  const analytics = initAnalytics()

  return {
    provide: {
      analytics
    }
  }
})
```

### 3. **Server-Only Plugin**

```ts
// plugins/server-only.server.ts
export default defineNuxtPlugin(() => {
  // Runs only on server
})
```

Generate a complete Nuxt plugin with proper typing.
