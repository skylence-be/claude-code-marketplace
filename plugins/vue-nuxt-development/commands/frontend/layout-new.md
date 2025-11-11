---
description: Create a new Nuxt layout
model: claude-sonnet-4-5
---

Create a new Nuxt layout.

## Layout Specification

$ARGUMENTS

## Nuxt Layout Pattern

```vue
<!-- layouts/custom.vue -->
<script setup lang="ts">
// Layout logic, shared state, etc.
</script>

<template>
  <div class="layout">
    <header>
      <slot name="header">
        <!-- Default header -->
      </slot>
    </header>

    <main>
      <slot />  <!-- Page content goes here -->
    </main>

    <footer>
      <slot name="footer">
        <!-- Default footer -->
      </slot>
    </footer>
  </div>
</template>
```

## Using the Layout

```vue
<!-- pages/some-page.vue -->
<script setup>
definePageMeta({
  layout: 'custom'
})
</script>
```

Generate a complete Nuxt layout with slots and proper structure.
