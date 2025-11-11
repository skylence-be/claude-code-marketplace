---
description: Clean up and refactor Vue/Nuxt code
model: claude-sonnet-4-5
---

Clean up and refactor the following Vue/Nuxt code following best practices.

## Code to Clean

$ARGUMENTS

## Vue/Nuxt Code Cleanup Guide

### 1. **Component Structure**

**Proper SFC ordering**
```vue
<script setup lang="ts">
// 1. Imports
import { ref } from 'vue'

// 2. Props/Emits
interface Props {
  title: string
}
const props = defineProps<Props>()
const emit = defineEmits<{ update: [value: string] }>()

// 3. Composables
const { data } = useFetch('/api/data')

// 4. State
const count = ref(0)

// 5. Computed
const doubled = computed(() => count.value * 2)

// 6. Methods
const increment = () => count.value++

// 7. Lifecycle
onMounted(() => {
  console.log('mounted')
})
</script>

<template>
  <!-- Template -->
</template>

<style scoped>
/* Styles */
</style>
```

### 2. **TypeScript Improvements**

**Remove `any` types**
```ts
// ❌ Bad
const data: any = {}
const handler = (e: any) => {}

// ✅ Good
interface Data {
  id: number
  name: string
}
const data: Data = { id: 1, name: 'Test' }
const handler = (e: Event) => {}
```

**Use type inference**
```ts
// ❌ Unnecessary explicit type
const count: Ref<number> = ref(0)

// ✅ Type is inferred
const count = ref(0)
```

### 3. **Extract Complex Logic**

**Create composables**
```ts
// ❌ Complex logic in component
const users = ref([])
const loading = ref(false)
const fetchUsers = async () => {
  loading.value = true
  users.value = await $fetch('/api/users')
  loading.value = false
}

// ✅ Extract to composable
// composables/useUsers.ts
export function useUsers() {
  const { data: users, pending: loading } = useFetch('/api/users')
  return { users, loading }
}
```

### 4. **Template Cleanup**

**Remove unnecessary `v-bind`**
```vue
<!-- ❌ Redundant -->
<div :class="'container'">

<!-- ✅ Clean -->
<div class="container">
```

**Simplify conditional rendering**
```vue
<!-- ❌ Verbose -->
<div v-if="isLoading === true">

<!-- ✅ Clean -->
<div v-if="isLoading">
```

**Use shorthand syntax**
```vue
<!-- ❌ Verbose -->
<button v-on:click="handler" v-bind:disabled="isDisabled">

<!-- ✅ Shorthand -->
<button @click="handler" :disabled="isDisabled">
```

### 5. **Reactivity Best Practices**

**Use `computed` instead of methods**
```vue
<!-- ❌ Recalculates on every render -->
<template>
  <div>{{ filterItems() }}</div>
</template>

<!-- ✅ Cached with computed -->
<script setup>
const filteredItems = computed(() => items.value.filter(i => i.active))
</script>
<template>
  <div>{{ filteredItems }}</div>
</template>
```

**Proper ref unwrapping**
```ts
// ❌ Unnecessary .value in template
const count = ref(0)
<template>{{ count.value }}</template>

// ✅ Auto-unwrapped
<template>{{ count }}</template>
```

### 6. **Remove Unused Code**

- Remove unused imports
- Remove commented code
- Remove unused variables
- Remove unused props/emits

### 7. **Naming Conventions**

**Components**
```
PascalCase: MyComponent.vue
```

**Composables**
```
camelCase with 'use' prefix: useAuth, useFetch
```

**Constants**
```
SCREAMING_SNAKE_CASE: API_URL, MAX_RETRIES
```

**Functions/Variables**
```
camelCase: handleClick, userData
```

### 8. **Error Handling**

**Add try/catch for async operations**
```ts
// ❌ No error handling
const data = await $fetch('/api/data')

// ✅ Proper error handling
try {
  const data = await $fetch('/api/data')
} catch (error) {
  console.error('Failed to fetch data:', error)
  // Handle error appropriately
}
```

### 9. **Accessibility**

**Add ARIA labels**
```vue
<!-- ❌ Missing accessibility -->
<button @click="close">X</button>

<!-- ✅ Accessible -->
<button @click="close" aria-label="Close dialog">X</button>
```

**Semantic HTML**
```vue
<!-- ❌ Divs for everything -->
<div class="header">
  <div class="nav">...</div>
</div>

<!-- ✅ Semantic elements -->
<header>
  <nav>...</nav>
</header>
```

### 10. **Performance**

**Remove unnecessary reactivity**
```ts
// ❌ Reactive when not needed
const config = reactive({ apiUrl: 'https://api.example.com' })

// ✅ Constant
const API_URL = 'https://api.example.com'
```

**Cleanup side effects**
```ts
onMounted(() => {
  const interval = setInterval(() => {}, 1000)

  onUnmounted(() => {
    clearInterval(interval)  // Cleanup
  })
})
```

## Cleanup Checklist

**Structure**
- ✓ Consistent component ordering
- ✓ Logical file organization
- ✓ Proper imports grouping

**TypeScript**
- ✓ No `any` types
- ✓ Proper type annotations
- ✓ Type inference where possible

**Code Quality**
- ✓ Extract complex logic to composables
- ✓ Remove unused code
- ✓ Consistent naming conventions
- ✓ Proper error handling

**Template**
- ✓ Clean, readable markup
- ✓ Proper use of directives
- ✓ Shorthand syntax
- ✓ Semantic HTML

**Performance**
- ✓ `computed` for derived state
- ✓ Proper reactivity patterns
- ✓ Cleanup side effects

Provide specific refactoring recommendations with code examples.
