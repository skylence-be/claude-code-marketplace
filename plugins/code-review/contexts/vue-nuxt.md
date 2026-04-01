# Vue / Nuxt Review Rules

Technology-specific review rules for Vue 3 and Nuxt 4 applications. Loaded when `vue` or `nuxt` is detected in `package.json`.

## Detection
- `package.json` contains `vue` or `nuxt` in `dependencies`/`devDependencies`
- `.vue` files in the changeset
- `nuxt.config.ts` exists

## Anti-Patterns to Flag

### Reactivity Loss from Destructuring
Destructuring a reactive object breaks reactivity — the destructured values become plain values.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `const { x, y } = reactive({ x: 1, y: 2 })` or `const { data } = useFetch(...)`
- **Fix:** Use `toRefs()`: `const { x, y } = toRefs(state)` or access properties directly

### Missing key on v-for
`v-for` without `:key` causes rendering bugs when list items change.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `v-for="item in items"` without `:key="item.id"` or similar unique key
- **Fix:** Add `:key` with a unique identifier (not array index for mutable lists)

### XSS via v-html
Using `v-html` with user-provided or unsanitized data.
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `v-html="userContent"` or `v-html="data.description"` where data comes from API
- **Fix:** Use text interpolation `{{ }}` or sanitize with DOMPurify before `v-html`

### Missing Watcher Cleanup
Watchers or event listeners created without cleanup on unmount.
- **Severity:** Medium (performance)
- **Pattern:** `watch()` with side effects (API calls, DOM manipulation) without corresponding `onUnmounted` cleanup, or `addEventListener` without `removeEventListener`
- **Fix:** Store the watcher stop handle or use `onUnmounted(() => cleanup())`

### Missing shallowRef for Large Objects
Using `ref()` for large non-reactive objects forces deep reactivity tracking.
- **Severity:** Medium (performance)
- **Pattern:** `ref(largeObject)` where the object has many nested properties that don't need individual reactivity
- **Fix:** Use `shallowRef()` if only the top-level reference changes

### useFetch/useAsyncData Outside Setup
Nuxt composables called outside the setup context or in nested functions.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `useFetch()` or `useAsyncData()` inside `onMounted()`, event handlers, or non-setup functions
- **Fix:** Call at the top level of `<script setup>` or the setup function

### Missing Error Handling on useFetch
Using `useFetch` without handling the `error` return value.
- **Severity:** Medium (error-handling)
- **Pattern:** `const { data } = useFetch(...)` without destructuring or checking `error`
- **Fix:** `const { data, error } = useFetch(...)` and handle error state in template

### Prop Drilling Instead of Provide/Inject
Passing props through 3+ component levels without using provide/inject or Pinia.
- **Severity:** Low (maintainability)
- **Pattern:** Same prop name passed through parent → child → grandchild → great-grandchild
- **Fix:** Use `provide()`/`inject()` or move to Pinia store

### Missing TypeScript on defineProps
Using `defineProps` without TypeScript generic for type safety.
- **Severity:** Low
- **Pattern:** `defineProps(['title', 'count'])` (runtime declaration)
- **Fix:** `defineProps<{ title: string; count: number }>()` (type-based declaration)

### Direct Array Index Mutation
Directly setting array index on reactive array doesn't trigger Vue 2 reactivity (Vue 3 handles it, but the pattern is still suspicious).
- **Severity:** Low
- **Pattern:** `state.items[index] = newValue` — works in Vue 3 but check if the intent is correct
- **Note:** Only flag if the code suggests Vue 2 migration or mixed patterns
