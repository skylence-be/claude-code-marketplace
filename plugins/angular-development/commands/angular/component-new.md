---
description: Generate a new Angular standalone component with signals, OnPush/zoneless, and typed inputs/outputs
model: claude-sonnet-4-5
---

Create a new Angular standalone component following modern Angular 21+ best practices.

## Component Specification

$ARGUMENTS

## Angular 21+ Component Standards

### 1. **Standalone Component with Signals**

All components are standalone by default. Use signal-based inputs and outputs:

```typescript
import { Component, input, output, computed, signal, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-user-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [],
  template: `
    <article class="user-card">
      <h2>{{ fullName() }}</h2>
      <p>{{ user().email }}</p>
      @if (showActions()) {
        <button (click)="edit.emit(user())">Edit</button>
      }
    </article>
  `,
  styles: [`
    .user-card { padding: 1rem; border: 1px solid #e0e0e0; border-radius: 8px; }
  `]
})
export class UserCard {
  // Signal-based inputs with required and optional variants
  user = input.required<User>();
  showActions = input(true);

  // Signal-based outputs
  edit = output<User>();

  // Computed signals for derived state
  fullName = computed(() => `${this.user().firstName} ${this.user().lastName}`);
}
```

### 2. **Signal Inputs and Outputs**

**Required Input**
```typescript
user = input.required<User>();
```

**Optional Input with Default**
```typescript
variant = input<'primary' | 'secondary'>('primary');
disabled = input(false);
```

**Input with Transform**
```typescript
import { booleanAttribute, numberAttribute } from '@angular/core';

disabled = input(false, { transform: booleanAttribute });
size = input(0, { transform: numberAttribute });
```

**Aliased Input**
```typescript
label = input.required<string>({ alias: 'buttonLabel' });
```

**Output**
```typescript
save = output<User>();
close = output<void>();
```

**Model (Two-Way Binding)**
```typescript
import { model } from '@angular/core';

value = model<string>('');
// Parent: <app-input [(value)]="name" />
```

### 3. **New Control Flow Syntax**

```html
@if (isLoading()) {
  <app-spinner />
} @else if (error()) {
  <div class="error">{{ error() }}</div>
} @else {
  <div class="content">
    @for (item of items(); track item.id) {
      <app-item-card [item]="item" />
    } @empty {
      <p>No items found.</p>
    }
  </div>
}

@switch (status()) {
  @case ('active') {
    <span class="badge active">Active</span>
  }
  @case ('inactive') {
    <span class="badge inactive">Inactive</span>
  }
  @default {
    <span class="badge">Unknown</span>
  }
}
```

### 4. **Presentational Component**

```typescript
@Component({
  selector: 'app-data-table',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [],
  template: `
    @if (loading()) {
      <div class="skeleton" aria-busy="true">Loading...</div>
    } @else {
      <table role="grid">
        <thead>
          <tr>
            @for (col of columns(); track col.key) {
              <th scope="col">{{ col.label }}</th>
            }
          </tr>
        </thead>
        <tbody>
          @for (row of data(); track row.id) {
            <tr (click)="rowClick.emit(row)">
              @for (col of columns(); track col.key) {
                <td>{{ row[col.key] }}</td>
              }
            </tr>
          } @empty {
            <tr><td [attr.colspan]="columns().length">No data available.</td></tr>
          }
        </tbody>
      </table>
    }
  `
})
export class DataTable<T extends { id: string | number }> {
  data = input.required<T[]>();
  columns = input.required<Column[]>();
  loading = input(false);

  rowClick = output<T>();
}
```

### 5. **Container Component with Service**

```typescript
@Component({
  selector: 'app-user-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [UserCard, RouterLink],
  template: `
    @if (userResource.hasValue()) {
      <app-user-card [user]="userResource.value()" (edit)="onEdit($event)" />
    } @else if (userResource.isLoading()) {
      <app-spinner />
    } @else if (userResource.error()) {
      <p>Error loading user.</p>
    }
  `
})
export class UserPage {
  private userService = inject(UserService);
  private router = inject(Router);

  userResource = httpResource<User>(() => '/api/user/me');

  onEdit(user: User) {
    this.router.navigate(['/users', user.id, 'edit']);
  }
}
```

### 6. **Deferrable Views**

```html
@defer (on viewport) {
  <app-heavy-chart [data]="chartData()" />
} @placeholder {
  <div class="chart-skeleton">Chart loading area</div>
} @loading (minimum 300ms) {
  <app-spinner />
} @error {
  <p>Failed to load chart.</p>
}
```

### 7. **Styling Approach**

Leave styling flexible. The component should work with:
- Tailwind CSS (utility classes)
- Angular Material
- Scoped styles (`styles` metadata)
- CSS custom properties for theming

Provide `class` input for customization:
```typescript
@Component({
  selector: 'app-card',
  host: { '[class]': 'cssClass()' },
  template: `<ng-content />`
})
export class Card {
  cssClass = input('', { alias: 'class' });
}
```

### 8. **Accessibility**

- Semantic HTML elements (`<article>`, `<nav>`, `<section>`, `<header>`)
- ARIA attributes where needed (`aria-label`, `aria-busy`, `role`)
- Keyboard navigation support (focusable elements, tabindex)
- Focus management with `afterNextRender()`
- Screen reader friendly content

### 9. **Component Structure**

Generate:

1. **Component file** - `.ts` file with full implementation (single-file component with inline template/styles)
2. **Input/Output types** - Fully typed interfaces
3. **Computed signals** - For all derived state
4. **Usage example** - How to use the component in a parent template
5. **Props documentation** - What each input/output does

## Code Quality Standards

**Component Design**
- ✓ Single Responsibility Principle
- ✓ Extract services for complex logic
- ✓ Keep components small (<200 lines)
- ✓ Reusable and composable
- ✓ Smart/Dumb component separation

**TypeScript**
- ✓ Strict typing throughout
- ✓ No `any` types
- ✓ Proper generics where needed
- ✓ Type inference where possible

**Template**
- ✓ Use `@if` / `@for` / `@switch` control flow
- ✓ Use `track` in `@for` loops with unique identifiers
- ✓ Avoid calling methods in templates (use `computed()`)
- ✓ Use `@defer` for heavy below-the-fold content

**Signals & Reactivity**
- ✓ `input()` / `input.required()` for typed inputs
- ✓ `output()` for typed outputs
- ✓ `computed()` for derived state
- ✓ `signal()` for local mutable state
- ✓ `model()` for two-way binding

**Performance**
- ✓ `ChangeDetectionStrategy.OnPush` (or zoneless)
- ✓ `@defer` for lazy-loaded heavy content
- ✓ `NgOptimizedImage` for images
- ✓ No unnecessary subscriptions

Generate production-ready, accessible, and type-safe Angular standalone components following Angular 21+ conventions.
