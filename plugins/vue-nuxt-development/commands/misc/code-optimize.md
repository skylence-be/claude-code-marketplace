---
description: Optimize Vue/Nuxt code for performance
model: claude-sonnet-4-5
---

Analyze and optimize the following Vue/Nuxt code for performance.

## Code to Optimize

$ARGUMENTS

## Vue/Nuxt Performance Optimization

### 1. **Component Optimization**

**Use `computed` for derived values**
```vue
<!-- ❌ Bad -->
<template>
  <div>{{ items.filter(i => i.active).length }}</div>
</template>

<!-- ✅ Good -->
<script setup>
const activeCount = computed(() => items.value.filter(i => i.active).length)
</script>
<template>
  <div>{{ activeCount }}</div>
</template>
```

**Avoid inline functions in templates**
```vue
<!-- ❌ Bad -->
<button @click="() => handleClick(item.id)">

<!-- ✅ Good -->
<button @click="handleClick(item.id)">
```

**Use `v-once` for static content**
```vue
<div v-once>{{ staticContent }}</div>
```

**Use `v-memo` for expensive renders**
```vue
<div v-memo="[item.id, item.status]">
  <ExpensiveComponent :data="item" />
</div>
```

### 2. **List Rendering**

**Always use `:key`**
```vue
<div v-for="item in items" :key="item.id">
```

**Use `v-show` vs `v-if` appropriately**
- `v-if`: Conditional rendering (removes from DOM)
- `v-show`: Toggle visibility (CSS display)

```vue
<!-- Use v-show for frequent toggles -->
<div v-show="isVisible">

<!-- Use v-if for rarely changed conditions -->
<div v-if="userRole === 'admin'">
```

### 3. **Lazy Loading**

**Async Components**
```ts
const HeavyComponent = defineAsyncComponent(() =>
  import('~/components/HeavyComponent.vue')
)
```

**Route-Level Code Splitting** (automatic in Nuxt)
```ts
// pages/dashboard.vue loads only when visited
```

**Lazy Hydration**
```vue
<LazyMyComponent />  <!-- Auto-imports as lazy in Nuxt -->
```

### 4. **Data Fetching Optimization**

**Use `lazy: true` for non-critical data**
```ts
const { data, pending } = await useFetch('/api/data', {
  lazy: true  // Doesn't block navigation
})
```

**Deduplication with `key`**
```ts
const { data } = await useFetch('/api/users', {
  key: 'users',  // Deduplicates multiple calls
  getCachedData: (key) => useNuxtData(key).data
})
```

**Transform data early**
```ts
const { data } = await useFetch('/api/data', {
  transform: (data) => data.items  // Reduce payload size
})
```

### 5. **Bundle Size Optimization**

**Tree-Shaking**
```ts
// ❌ Bad - imports entire library
import _ from 'lodash'

// ✅ Good - imports only what's needed
import { debounce } from 'lodash-es'
```

**Analyze Bundle**
```bash
nuxt build --analyze
```

**Dynamic Imports**
```ts
const loadChart = async () => {
  const { Chart } = await import('chart.js')
  return new Chart(...)
}
```

### 6. **Image Optimization**

**Use `<NuxtImg>` and `<NuxtPicture>`**
```vue
<NuxtImg
  src="/image.jpg"
  width="800"
  height="600"
  format="webp"
  loading="lazy"
  placeholder
/>
```

**Lazy load images**
```vue
<img loading="lazy" src="...">
```

### 7. **State Management**

**Avoid deep reactivity when not needed**
```ts
// ❌ Unnecessary deep reactivity
const state = reactive({ deep: { nested: { data: {} } } })

// ✅ Shallow when appropriate
const state = shallowReactive({ items: [] })
```

**Use `shallowRef` for large objects**
```ts
const largeData = shallowRef({ /* large object */ })
```

### 8. **Watchers**

**Lazy watchers**
```ts
watch(source, callback, { lazy: true })
```

**Flush timing**
```ts
watch(source, callback, { flush: 'post' })  // After DOM updates
```

**Stop watchers when done**
```ts
const stop = watch(source, callback)
// Later...
stop()
```

### 9. **SSR Optimization**

**Prefetch critical data only**
```ts
definePageMeta({
  middleware: ['auth']  // Run only necessary middleware
})
```

**Use `server: false` for client-only data**
```ts
const { data } = await useFetch('/api/data', {
  server: false  // Skip on SSR
})
```

### 10. **Virtual Scrolling**

For long lists, use virtual scrolling:
```bash
npm install vue-virtual-scroller
```

```vue
<RecycleScroller
  :items="items"
  :item-size="50"
  key-field="id"
>
  <template #default="{ item }">
    <div>{{ item.name }}</div>
  </template>
</RecycleScroller>
```

## Performance Checklist

**Rendering**
- ✓ Use `computed` for derived state
- ✓ Avoid inline functions in templates
- ✓ Use `v-once` for static content
- ✓ Use `v-memo` for conditional re-renders
- ✓ Proper `v-if` vs `v-show` usage

**Data Fetching**
- ✓ Use `lazy: true` for non-critical data
- ✓ Deduplicate with `key` option
- ✓ Transform data to reduce payload
- ✓ Cache responses appropriately

**Bundle**
- ✓ Tree-shake imports
- ✓ Lazy load heavy components
- ✓ Code-split routes
- ✓ Optimize images

**State**
- ✓ Avoid unnecessary deep reactivity
- ✓ Use `shallowRef`/`shallowReactive` when appropriate
- ✓ Clean up watchers

Analyze the code and provide specific, actionable optimization recommendations.
