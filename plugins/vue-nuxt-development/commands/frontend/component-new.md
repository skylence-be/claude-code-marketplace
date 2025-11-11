---
description: Create a new Vue 3 component with TypeScript and Composition API
model: claude-sonnet-4-5
---

Create a new Vue 3 component following modern best practices.

## Component Specification

$ARGUMENTS

## Vue 3 + TypeScript Standards

### 1. **Composition API with `<script setup>`**

Always use `<script setup>` syntax with TypeScript:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

const emit = defineEmits<{
  update: [value: number]
  close: []
}>()

const localCount = ref(props.count)
</script>
```

### 2. **TypeScript Best Practices**

- **Strict typing** - No `any` types
- **Props interface** - Define all props with types
- **Emits typing** - Type all events
- **Refs** - Explicit types for refs
- **Computed** - TypeScript infers return types
- **Template refs** - Type DOM element refs

### 3. **Component Patterns**

**Presentational Component**
```vue
<script setup lang="ts">
interface Props {
  data: MyData[]
  loading?: boolean
}

const props = defineProps<Props>()
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div v-for="item in data" :key="item.id">
        {{ item.name }}
      </div>
    </div>
  </div>
</template>
```

**Container Component with Composable**
```vue
<script setup lang="ts">
import { useMyFeature } from '~/composables/useMyFeature'

const { data, loading, error, fetchData } = useMyFeature()

onMounted(() => {
  fetchData()
})
</script>
```

### 4. **Styling Approach**

Leave styling flexible - component should work with:
- Tailwind CSS (utility classes)
- CSS Modules (`<style module>`)
- Scoped styles (`<style scoped>`)
- UnoCSS
- Plain CSS

Provide class bindings for customization:

```vue
<script setup lang="ts">
interface Props {
  class?: string
}

const props = defineProps<Props>()
</script>

<template>
  <div :class="props.class">
    <!-- content -->
  </div>
</template>
```

### 5. **Nuxt 4 Specific Features**

- **Auto-imports** - composables, components, utils
- **`<NuxtLink>`** - for navigation
- **`useFetch`/`useAsyncData`** - for data fetching
- **`useState`** - for shared state
- **`definePageMeta`** - for page metadata

### 6. **Accessibility**

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Screen reader friendly

### 7. **Component Structure**

Generate:

1. **Component file** - `.vue` file with full implementation
2. **Props/Emits types** - Fully typed interfaces
3. **Composable** (if complex logic) - Separate reusable logic
4. **Usage example** - How to import and use
5. **Props documentation** - What each prop does

## Code Quality Standards

**Component Design**
- ✓ Single Responsibility Principle
- ✓ Composables for complex logic
- ✓ Keep components small (<200 lines)
- ✓ Reusable and composable

**TypeScript**
- ✓ Strict typing throughout
- ✓ No `any` types
- ✓ Proper generics where needed
- ✓ Type inference where possible

**Template**
- ✓ Use `v-if` for conditional rendering
- ✓ Use `:key` in `v-for` loops
- ✓ Avoid inline functions in templates
- ✓ Use computed for derived data

**Performance**
- ✓ `computed` for expensive operations
- ✓ `v-once` for static content
- ✓ Lazy loading for heavy components
- ✓ Proper reactivity patterns

Generate production-ready, accessible, and type-safe Vue 3 components following Nuxt 4 conventions.
