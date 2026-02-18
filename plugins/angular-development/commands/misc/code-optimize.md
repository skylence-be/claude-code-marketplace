---
description: Optimize Angular code for performance with zoneless, @defer, lazy loading, and bundle analysis
model: claude-sonnet-4-5
---

Analyze and optimize the following Angular code for performance.

## Code to Optimize

$ARGUMENTS

## Angular Performance Optimization Guide

### 1. **Zoneless Change Detection**

Angular 21 defaults to zoneless. Ensure your application is compatible:

```typescript
// Angular 21 default -- no Zone.js, no configuration needed
// For Angular 20, enable explicitly:
import { provideZonelessChangeDetection } from '@angular/core';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    provideRouter(routes),
  ],
};
```

**Requirements for zoneless:**
- All components use `OnPush` or signals-driven change detection
- No reliance on `NgZone.run()` or `NgZone.onStable`
- Use `afterNextRender()` / `afterEveryRender()` instead of Zone-dependent timing
- Use `PendingTasks` for SSR async operations

**Benefits:**
- Up to 30% rendering speed improvement
- Up to 60% startup time improvement
- ~13KB smaller bundle (no Zone.js)
- Cleaner stack traces

### 2. **Replace Template Methods with Computed Signals**

```typescript
// BAD: Called on every change detection cycle
@Component({
  template: `
    <div>{{ getTotal() }}</div>
    <div>{{ formatDate(item.date) }}</div>
    <div *ngIf="isOverBudget()">Warning!</div>
  `
})
export class Bad {
  getTotal() { return this.items.reduce((s, i) => s + i.price, 0); }
  formatDate(d: Date) { return d.toLocaleDateString(); }
  isOverBudget() { return this.getTotal() > this.budget; }
}

// GOOD: Memoized computed signals
@Component({
  template: `
    <div>{{ total() }}</div>
    <div>{{ formattedDate() }}</div>
    @if (isOverBudget()) { <span>Warning!</span> }
  `
})
export class Good {
  items = input.required<Item[]>();
  budget = input(1000);
  date = input.required<Date>();

  total = computed(() => this.items().reduce((s, i) => s + i.price, 0));
  formattedDate = computed(() => this.date().toLocaleDateString());
  isOverBudget = computed(() => this.total() > this.budget());
}
```

### 3. **Deferrable Views with `@defer`**

Lazy load heavy components to reduce initial bundle and improve LCP:

```html
<!-- Defer until element enters viewport -->
@defer (on viewport) {
  <app-analytics-chart [data]="chartData()" />
} @placeholder {
  <div class="chart-placeholder" style="height: 400px">
    <p>Chart will load when scrolled into view</p>
  </div>
} @loading (minimum 200ms) {
  <app-skeleton height="400px" />
} @error {
  <p>Failed to load chart component.</p>
}

<!-- Defer on interaction -->
@defer (on interaction) {
  <app-comment-section [postId]="postId()" />
} @placeholder {
  <button>Load Comments</button>
}

<!-- Defer on idle (loads when browser is idle) -->
@defer (on idle) {
  <app-recommendations [userId]="userId()" />
} @placeholder {
  <div class="recommendations-skeleton"></div>
}

<!-- Defer with timer -->
@defer (on timer(3s)) {
  <app-newsletter-popup />
}

<!-- Defer with condition -->
@defer (when showAdvanced()) {
  <app-advanced-settings />
}

<!-- Incremental hydration for SSR -->
@defer (hydrate on viewport) {
  <app-heavy-widget />
}
```

### 4. **Lazy Loading Routes**

```typescript
// BAD: Eagerly loaded routes
import { Dashboard } from './features/dashboard/dashboard';
import { UserList } from './features/users/user-list';

const routes: Routes = [
  { path: 'dashboard', component: Dashboard },
  { path: 'users', component: UserList },
];

// GOOD: Lazy loaded routes (separate chunks)
const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard').then(m => m.Dashboard),
  },
  {
    path: 'users',
    loadChildren: () => import('./features/users/users.routes').then(m => m.USERS_ROUTES),
  },
];

// BETTER: With preloading strategy for frequently visited routes
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withPreloading(PreloadAllModules)),
  ],
};
```

### 5. **Image Optimization with NgOptimizedImage**

```typescript
import { NgOptimizedImage } from '@angular/common';

@Component({
  imports: [NgOptimizedImage],
  template: `
    <!-- LCP image: use priority attribute -->
    <img ngSrc="/hero.jpg" width="1200" height="600" priority />

    <!-- Below-the-fold images: lazy loaded by default -->
    <img ngSrc="/product.jpg" width="400" height="300" />

    <!-- With placeholder -->
    <img ngSrc="/avatar.jpg" width="80" height="80" placeholder />

    <!-- Responsive with srcset -->
    <img ngSrc="/banner.jpg" width="1200" height="400" sizes="100vw" />
  `
})
export class OptimizedImages {}
```

### 6. **Virtual Scrolling for Large Lists**

```typescript
import { ScrollingModule } from '@angular/cdk/scrolling';

@Component({
  imports: [ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport itemSize="48" class="list-viewport">
      <div *cdkVirtualFor="let item of items()" class="list-item">
        <span>{{ item.name }}</span>
        <span>{{ item.value }}</span>
      </div>
    </cdk-virtual-scroll-viewport>
  `,
  styles: [`
    .list-viewport { height: 500px; }
    .list-item { height: 48px; display: flex; align-items: center; }
  `]
})
export class LargeList {
  items = input.required<Item[]>();
}
```

### 7. **Bundle Size Optimization**

**Tree-shake imports:**
```typescript
// BAD: Imports entire library
import * as _ from 'lodash';
_.debounce(fn, 300);

// GOOD: Import only what you need
import { debounce } from 'lodash-es';
debounce(fn, 300);

// BEST: Use RxJS or native alternatives
import { debounceTime } from 'rxjs';
```

**Analyze bundle size:**
```bash
# Generate stats file
ng build --stats-json

# Analyze with webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/my-app/stats.json

# Or use source-map-explorer
npx source-map-explorer dist/my-app/browser/*.js
```

**Configure budgets in angular.json:**
```json
"budgets": [
  {
    "type": "initial",
    "maximumWarning": "500kB",
    "maximumError": "1MB"
  },
  {
    "type": "anyComponentStyle",
    "maximumWarning": "4kB",
    "maximumError": "8kB"
  }
]
```

### 8. **HTTP Optimization**

```typescript
// Use httpResource for automatic cancellation and caching
userProfile = httpResource<UserProfile>(() => `/api/users/${this.userId()}`);
// Automatically cancels previous request when userId changes

// Use HTTP transfer cache for SSR
provideClientHydration(
  withHttpTransferCacheOptions({
    includePostRequests: false,
    filter: (req) => !req.url.includes('/no-cache'),
  })
);

// Cancel subscriptions with takeUntilDestroyed
this.http.get<Data>('/api/data').pipe(
  takeUntilDestroyed()
).subscribe(data => { /* ... */ });
```

### 9. **Avoid Unnecessary Reactivity**

```typescript
// BAD: Everything is reactive
@Component({ /* ... */ })
export class OverlyReactive {
  apiUrl = signal('https://api.example.com');     // Never changes
  maxRetries = signal(3);                          // Never changes
  columns = signal(['name', 'email', 'role']);     // Static list
}

// GOOD: Only reactive state is signals
@Component({ /* ... */ })
export class Optimized {
  readonly API_URL = 'https://api.example.com';    // Constant
  readonly MAX_RETRIES = 3;                        // Constant
  readonly COLUMNS = ['name', 'email', 'role'] as const; // Constant

  // Only mutable/dynamic state is a signal
  selectedColumn = signal<string>('name');
  sortDirection = signal<'asc' | 'desc'>('asc');
}
```

### 10. **Efficient Change Detection**

```typescript
// Use track with unique identifiers in @for
@for (item of items(); track item.id) {
  <app-item-card [item]="item" />
}

// Use @defer for expensive child components
@defer (on viewport) {
  <app-expensive-visualization [data]="data()" />
} @placeholder {
  <div class="placeholder"></div>
}

// Use OnPush on ALL components
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
})
```

### 11. **SSR and Hydration Optimization**

```typescript
// Route-level render modes
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Static pages: prerender at build time
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'about', renderMode: RenderMode.Prerender },

  // Dynamic pages: server-side render
  { path: 'dashboard', renderMode: RenderMode.Server },

  // Interactive-only pages: client-side render
  { path: 'editor', renderMode: RenderMode.Client },
];

// Incremental hydration for heavy components
@defer (hydrate on viewport) {
  <app-interactive-map />
}

// Guard browser-only APIs
afterNextRender(() => {
  // Safe to access window, document, localStorage
  this.initializeChart();
});
```

### 12. **Preconnect and Resource Hints**

```html
<!-- index.html -->
<link rel="preconnect" href="https://api.example.com" />
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin />
<link rel="dns-prefetch" href="https://analytics.example.com" />
```

### 13. **Web Worker for Heavy Computation**

```bash
ng generate web-worker heavy-computation
```

```typescript
// heavy-computation.worker.ts
addEventListener('message', ({ data }) => {
  const result = performExpensiveCalculation(data);
  postMessage(result);
});

// In component
if (typeof Worker !== 'undefined') {
  const worker = new Worker(new URL('./heavy-computation.worker', import.meta.url));
  worker.onmessage = ({ data }) => {
    this.result.set(data);
  };
  worker.postMessage(this.inputData());
}
```

## Performance Checklist

**Change Detection**
- ✓ `ChangeDetectionStrategy.OnPush` on all components
- ✓ Zoneless change detection enabled (Angular 21 default)
- ✓ No method calls in templates (use `computed()` or pipes)
- ✓ `track` by unique identifier in all `@for` loops

**Bundle Size**
- ✓ All routes lazy loaded (`loadComponent` / `loadChildren`)
- ✓ `@defer` for heavy below-the-fold components
- ✓ Tree-shaken imports (no wildcard imports)
- ✓ Zone.js removed (zoneless)
- ✓ Bundle budgets configured in `angular.json`

**Rendering**
- ✓ `@defer` with `on viewport` for offscreen content
- ✓ Virtual scrolling for lists > 100 items
- ✓ `NgOptimizedImage` for all images
- ✓ `priority` attribute on LCP images

**Data Fetching**
- ✓ `httpResource` for declarative reactive fetching
- ✓ HTTP transfer cache for SSR
- ✓ Subscriptions cleaned up with `takeUntilDestroyed()`
- ✓ Preloading strategy for frequently visited routes

**State**
- ✓ `computed()` for all derived state (memoized)
- ✓ Constants are not wrapped in signals
- ✓ Avoid deep-nesting signals; flatten state or use separate signals for large objects
- ✓ Minimal `effect()` usage

**SSR**
- ✓ Route-level render modes configured
- ✓ Incremental hydration for heavy components
- ✓ Browser-only APIs guarded with `afterNextRender()`
- ✓ `PendingTasks` for async operations during SSR

Analyze the code and provide specific, actionable optimization recommendations with measurable impact estimates.
