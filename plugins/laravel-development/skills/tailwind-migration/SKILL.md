---
name: tailwind-migration
description: Tailwind CSS v3 to v4 migration patterns including CSS-first configuration, replaced utilities, import syntax changes, and deprecated class replacements. Use when upgrading Tailwind, fixing deprecated utilities, or choosing between v3 and v4 patterns.
category: frontend
tags: [tailwind, css, migration, v4, styling]
related_skills: [livewire-forms-validation, vue3-composition-api-patterns]
---

# Tailwind CSS v3 → v4 Migration

Tailwind CSS v4 is a ground-up rewrite with CSS-first configuration, new import syntax, and deprecated utility replacements. This skill covers the key differences and migration patterns.

## When to Use This Skill

- Upgrading a project from Tailwind v3 to v4
- Writing Tailwind classes and unsure which version the project uses
- Fixing "unknown utility" errors after a Tailwind upgrade
- Setting up Tailwind configuration in a new project

## Version Detection

Check the project's Tailwind version:
- `package.json` → `tailwindcss` version in `devDependencies`
- If `tailwind.config.js` exists → likely v3
- If CSS file uses `@import "tailwindcss"` → v4
- If CSS file uses `@tailwind base/components/utilities` → v3

## Key Differences

### Import Syntax

```css
/* v3 — directive-based */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* v4 — standard CSS import */
@import "tailwindcss";
```

### Configuration

```css
/* v3 — JavaScript config file (tailwind.config.js) */
module.exports = {
  theme: {
    extend: {
      colors: { brand: '#1a73e8' }
    }
  }
}

/* v4 — CSS-first with @theme directive (no config file needed) */
@theme {
  --color-brand: oklch(0.72 0.11 178);
}
```

**Note:** `corePlugins` is not supported in Tailwind v4.

### Replaced Utilities

Tailwind v4 removed deprecated utilities. Use these replacements:

| Deprecated (v3) | Replacement (v4) |
|------------------|-----------------|
| `bg-opacity-*` | `bg-black/*` (e.g., `bg-black/50`) |
| `text-opacity-*` | `text-black/*` |
| `border-opacity-*` | `border-black/*` |
| `divide-opacity-*` | `divide-black/*` |
| `ring-opacity-*` | `ring-black/*` |
| `placeholder-opacity-*` | `placeholder-black/*` |
| `flex-shrink-*` | `shrink-*` |
| `flex-grow-*` | `grow-*` |
| `overflow-ellipsis` | `text-ellipsis` |
| `decoration-slice` | `box-decoration-slice` |
| `decoration-clone` | `box-decoration-clone` |

Opacity values remain numeric (e.g., `bg-black/50` for 50% opacity).

## Common Patterns (Both Versions)

### Spacing — Use Gap, Not Margins

```html
<!-- Good: gap for sibling spacing -->
<div class="flex gap-8">
    <div>Item 1</div>
    <div>Item 2</div>
</div>

<!-- Avoid: margins between siblings -->
<div class="flex">
    <div class="mr-8">Item 1</div>
    <div>Item 2</div>
</div>
```

### Responsive Grid

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div>Card 1</div>
    <div>Card 2</div>
    <div>Card 3</div>
</div>
```

### Dark Mode

If the project uses dark mode, all new components must include `dark:` variants:

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
    Content adapts to color scheme
</div>
```

## Migration Checklist

1. Update `package.json` to Tailwind v4
2. Replace `@tailwind` directives with `@import "tailwindcss"`
3. Move `tailwind.config.js` settings to `@theme` in CSS
4. Search and replace deprecated utilities (see table above)
5. Remove `corePlugins` configuration (not supported in v4)
6. Test responsive breakpoints and dark mode
7. Verify no "unknown utility" warnings in build output

## Common Pitfalls

- Using deprecated v3 utilities (`bg-opacity-*`, `flex-shrink-*`) in a v4 project
- Using `@tailwind` directives instead of `@import "tailwindcss"` in v4
- Creating `tailwind.config.js` instead of using CSS `@theme` directive in v4
- Using margins for spacing between siblings instead of gap utilities
- Forgetting dark mode variants when the project uses dark mode
