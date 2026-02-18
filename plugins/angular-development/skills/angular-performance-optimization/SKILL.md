---
name: angular-performance-optimization
description: Master Angular performance optimization including OnPush and zoneless change detection, @defer blocks for lazy loading, bundle optimization, NgOptimizedImage, virtual scrolling, HTTP caching, computed() vs methods in templates, and Core Web Vitals improvement strategies.
category: angular
tags: [angular, performance, zoneless, defer, lazy-loading, onpush, virtual-scrolling, optimization]
related_skills: [angular-blueprint, angular-signals-patterns, angular-ssr-hydration, angular-routing-patterns]
---

# Angular Performance Optimization

Comprehensive guide to optimizing Angular 21+ application performance covering change detection strategies (OnPush, zoneless), `@defer` blocks for component-level lazy loading, bundle size optimization, `NgOptimizedImage` for image performance, virtual scrolling for large lists, HTTP caching patterns, the critical difference between `computed()` and template methods, and strategies for improving Core Web Vitals.

## When to Use This Skill

- Improving Largest Contentful Paint (LCP) and other Core Web Vitals
- Reducing initial bundle size with lazy loading and code splitting
- Optimizing change detection for faster rendering
- Implementing deferred loading for below-the-fold content
- Optimizing image loading with NgOptimizedImage
- Rendering large lists efficiently with virtual scrolling
- Reducing unnecessary HTTP requests with caching
- Profiling and measuring Angular application performance
- Migrating to zoneless change detection for smaller bundles and faster startup

## Core Concepts

### 1. Change Detection
- **Default**: Check all components on every event (slow)
- **OnPush**: Check only when inputs change, events fire, or signals update
- **Zoneless**: No Zone.js, signals and events drive updates (Angular 21 default)
- Zoneless provides up to 30% rendering speed improvement and 60% faster startup

### 2. Code Splitting
- Route-level lazy loading with `loadComponent` / `loadChildren`
- Component-level lazy loading with `@defer` blocks
- Tree-shaking with standalone components and `providedIn: 'root'`

### 3. Rendering Optimization
- `computed()` signals for memoized derived values (never use methods in templates)
- `@for` with `track` for efficient list rendering
- `@defer` with appropriate triggers for below-the-fold content
- Virtual scrolling for lists with thousands of items

### 4. Asset Optimization
- `NgOptimizedImage` for automatic image optimization
- Font optimization with `@angular/fonts` or manual strategies
- Bundle analysis with `ng build --stats-json`

### 5. Caching
- HTTP transfer cache for SSR
- HTTP interceptor caching for API responses
- Service worker caching for offline support
- Route-level caching with SSG/prerender

## Quick Start

```typescript
// Immediate performance wins for any Angular 21 app

// 1. Zoneless (default in Angular 21)
// No configuration needed -- Zone.js is not included

// 2. OnPush on all components (redundant with zoneless but good practice)
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
})

// 3. Computed instead of methods
fullName = computed(() => `${this.firstName()} ${this.lastName()}`);

// 4. @defer for heavy components
// @defer (on viewport) { <app-heavy-chart /> }

// 5. Lazy load routes
// loadComponent: () => import('./heavy').then(m => m.Heavy)
```

## Fundamental Patterns

### Pattern 1: Zoneless Change Detection

```typescript
// Angular 21: Zoneless is the default for new applications
// No Zone.js means:
// - ~13KB less in bundle (gzipped)
// - Up to 60% faster startup
// - Cleaner stack traces
// - No monkey-patching of browser APIs

// What triggers change detection in zoneless mode:
// 1. Signal updates read in templates
// 2. Template event listeners (click, input, etc.)
// 3. AsyncPipe usage
// 4. ChangeDetectorRef.markForCheck()
// 5. ComponentRef.setInput()

@Component({
  selector: 'app-counter',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <!-- Signal reads automatically schedule change detection -->
    <p>Count: {{ count() }}</p>
    <p>Doubled: {{ doubled() }}</p>

    <!-- Event listener triggers change detection -->
    <button (click)="increment()">+</button>
  `,
})
export class Counter {
  readonly count = signal(0);
  readonly doubled = computed(() => this.count() * 2);

  increment(): void {
    this.count.update(c => c + 1);
    // Change detection runs automatically because:
    // 1. (click) event listener triggered
    // 2. Signal value changed and is read in template
  }
}

// For existing apps migrating to zoneless:
// app.config.ts
import { provideZonelessChangeDetection } from '@angular/core';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(), // Enable zoneless
    // Remove zone.js from polyfills in angular.json
  ],
};

// Migration schematic:
// ng generate @angular/core:onpush-zoneless-migration
```

### Pattern 2: computed() vs Methods in Templates

```typescript
// CRITICAL PERFORMANCE PATTERN
// Methods in templates are called on EVERY change detection cycle
// computed() signals are memoized and only recalculate when dependencies change

@Component({
  selector: 'app-product-list',
  template: `
    <!-- BAD: getFilteredProducts() called on every change detection cycle -->
    <!-- Even mouse movements, scrolls, or unrelated events trigger recalculation -->
    <!--
    @for (product of getFilteredProducts(); track product.id) {
      <app-product-card [product]="product" />
    }
    -->

    <!-- GOOD: filteredProducts() only recalculates when category or products change -->
    @for (product of filteredProducts(); track product.id) {
      <app-product-card [product]="product" />
    }

    <!-- BAD: formatPrice() called every cycle -->
    <!-- <span>{{ formatPrice(product.price) }}</span> -->

    <!-- GOOD: use a pipe (cached per input value) -->
    <span>{{ product.price | currency }}</span>

    <!-- GOOD: use computed for complex derivations -->
    <span>{{ formattedTotal() }}</span>
  `,
})
export class ProductList {
  readonly products = signal<Product[]>([]);
  readonly selectedCategory = signal<string | null>(null);

  // GOOD: computed is memoized -- only runs when dependencies change
  readonly filteredProducts = computed(() => {
    const cat = this.selectedCategory();
    const all = this.products();
    if (!cat) return all;
    return all.filter(p => p.category.slug === cat);
  });

  readonly formattedTotal = computed(() => {
    const total = this.filteredProducts()
      .reduce((sum, p) => sum + p.price, 0);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(total / 100);
  });

  // BAD: this would be called on every change detection cycle if used in template
  getFilteredProducts(): Product[] {
    // Expensive filtering logic runs unnecessarily
    return this.products().filter(p => p.category.slug === this.selectedCategory());
  }
}
```

### Pattern 3: @defer Blocks for Component-Level Lazy Loading

```typescript
@Component({
  selector: 'app-product-page',
  template: `
    <!-- Critical above-the-fold content: loaded immediately -->
    <app-product-hero [product]="product()" />
    <app-add-to-cart [product]="product()" />

    <!-- Below-the-fold: loads when visible in viewport -->
    @defer (on viewport) {
      <app-product-reviews [productId]="product().id" />
    } @placeholder {
      <div class="reviews-skeleton" style="height: 400px;">
        <div class="animate-pulse bg-gray-200 h-full rounded"></div>
      </div>
    } @loading (minimum 300ms) {
      <app-spinner />
    } @error {
      <p>Failed to load reviews.</p>
    }

    <!-- Loads on user interaction (click, keydown, etc.) -->
    @defer (on interaction) {
      <app-product-3d-viewer [model]="product().modelUrl" />
    } @placeholder {
      <button class="btn">Click to load 3D viewer</button>
    }

    <!-- Loads when browser is idle -->
    @defer (on idle) {
      <app-related-products [category]="product().category" />
    } @placeholder {
      <div class="h-48 bg-gray-100 rounded"></div>
    }

    <!-- Loads after a timer -->
    @defer (on timer(3s)) {
      <app-newsletter-signup />
    }

    <!-- Loads when a condition is true -->
    @defer (when showAnalytics()) {
      <app-analytics-dashboard />
    }

    <!-- Prefetch: load bundle on viewport, hydrate on interaction -->
    @defer (on interaction; prefetch on viewport) {
      <app-heavy-chart [data]="chartData()" />
    } @placeholder {
      <div class="chart-placeholder">Interact to load chart</div>
    }

    <!-- Multiple triggers: load on viewport OR timer -->
    @defer (on viewport; on timer(10s)) {
      <app-footer-widgets />
    }
  `,
})
export class ProductPage {
  readonly product = input.required<Product>();
  readonly showAnalytics = signal(false);
  readonly chartData = signal<number[]>([]);
}
```

### Pattern 4: NgOptimizedImage

```typescript
import { Component } from '@angular/core';
import { NgOptimizedImage } from '@angular/common';

@Component({
  selector: 'app-product-gallery',
  imports: [NgOptimizedImage],
  template: `
    <!-- Priority image: LCP candidate, loaded eagerly -->
    <img
      ngSrc="/products/hero.jpg"
      width="800"
      height="600"
      priority
      [alt]="product().name"
    />

    <!-- Below-the-fold images: lazy loaded by default -->
    @for (image of product().images; track image.id) {
      <img
        [ngSrc]="image.url"
        [width]="400"
        [height]="400"
        [alt]="image.alt"
        loading="lazy"
        [placeholder]="image.blurHash"
      />
    }

    <!-- Responsive image with srcset -->
    <img
      ngSrc="/products/banner.jpg"
      width="1200"
      height="400"
      sizes="(max-width: 768px) 100vw, 1200px"
      priority
      alt="Product banner"
    />

    <!-- Fill mode for CSS-sized containers -->
    <div class="aspect-square relative">
      <img
        ngSrc="/products/thumb.jpg"
        fill
        class="object-cover"
        alt="Thumbnail"
      />
    </div>
  `,
})
export class ProductGallery {
  readonly product = input.required<Product>();
}

// With a custom image loader (for CDN/image optimization service)
import { provideImageKitLoader } from '@angular/common';

// In app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideImageKitLoader('https://ik.imagekit.io/your_account'),
    // Or for Cloudinary:
    // provideCloudinaryLoader('https://res.cloudinary.com/your_cloud'),
  ],
};
```

### Pattern 5: Virtual Scrolling for Large Lists

```typescript
import { Component, signal } from '@angular/core';
import { ScrollingModule, CdkVirtualScrollViewport } from '@angular/cdk/scrolling';

@Component({
  selector: 'app-log-viewer',
  imports: [ScrollingModule],
  template: `
    <h2>Log Entries ({{ logs().length }} total)</h2>

    <!-- Fixed size virtual scroll: each item is 48px tall -->
    <cdk-virtual-scroll-viewport
      itemSize="48"
      class="h-[600px] border rounded"
    >
      <div
        *cdkVirtualFor="let log of logs(); trackBy: trackById"
        class="h-12 flex items-center px-4 border-b"
        [class.bg-red-50]="log.level === 'error'"
        [class.bg-yellow-50]="log.level === 'warn'"
      >
        <span class="w-24 font-mono text-sm">{{ log.timestamp }}</span>
        <span class="w-16 uppercase text-xs font-bold" [ngClass]="levelClassMap[log.level] ?? 'text-gray-600'">
          {{ log.level }}
        </span>
        <span class="flex-1 truncate">{{ log.message }}</span>
      </div>
    </cdk-virtual-scroll-viewport>
  `,
})
export class LogViewer {
  readonly logs = signal<LogEntry[]>([]);

  // Use a constant lookup map instead of a method call in the template
  readonly levelClassMap: Record<string, string> = {
    error: 'text-red-600',
    warn: 'text-yellow-600',
    info: 'text-blue-600',
    debug: 'text-gray-400',
  };

  trackById(index: number, item: LogEntry): string {
    return item.id;
  }

  constructor() {
    // Generate large dataset
    this.logs.set(
      Array.from({ length: 100_000 }, (_, i) => ({
        id: `log-${i}`,
        timestamp: new Date(Date.now() - i * 1000).toISOString().slice(11, 19),
        level: ['info', 'warn', 'error', 'debug'][i % 4],
        message: `Log entry #${i}: ${this.generateMessage()}`,
      }))
    );
  }

  private generateMessage(): string {
    const messages = [
      'Request processed successfully',
      'Cache miss for key user:123',
      'Database connection timeout',
      'Authentication token refreshed',
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  }
}

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  message: string;
}
```

### Pattern 6: Bundle Size Optimization

```typescript
// 1. Analyze bundle size
// ng build --stats-json
// npx webpack-bundle-analyzer dist/my-app/stats.json

// 2. Lazy load routes (most impactful)
export const routes: Routes = [
  {
    path: 'admin',
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES),
  },
];

// 3. Use @defer for heavy components
// Moves component code to a separate chunk, loaded on demand

// 4. Tree-shake with specific imports
// BAD: imports entire library
import * as _ from 'lodash';

// GOOD: import only what you need
import debounce from 'lodash-es/debounce';

// 5. Use providedIn: 'root' for tree-shakable services
@Injectable({ providedIn: 'root' }) // Tree-shaken if not injected anywhere
export class RarelyUsedService {}

// 6. angular.json budget configuration
{
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
}

// 7. Remove Zone.js (default in Angular 21)
// Saves ~13KB gzipped

// 8. Use dynamic imports for large dependencies
async loadChart(): Promise<void> {
  const { Chart } = await import('chart.js');
  new Chart(this.canvas.nativeElement, { /* ... */ });
}
```

### Pattern 7: HTTP Caching Patterns

```typescript
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { of, tap } from 'rxjs';

// In-memory cache interceptor
const cache = new Map<string, { response: HttpResponse<unknown>; timestamp: number }>();

export const cachingInterceptor: HttpInterceptorFn = (req, next) => {
  // Only cache GET requests
  if (req.method !== 'GET') {
    return next(req);
  }

  // Check for no-cache header
  if (req.headers.has('x-no-cache')) {
    return next(req);
  }

  const cacheKey = req.urlWithParams;
  const cached = cache.get(cacheKey);
  const maxAge = 60_000; // 1 minute

  if (cached && Date.now() - cached.timestamp < maxAge) {
    return of(cached.response.clone());
  }

  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(cacheKey, {
          response: event.clone(),
          timestamp: Date.now(),
        });
      }
    }),
  );
};

// Stale-while-revalidate interceptor
export const swrInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.method !== 'GET') return next(req);

  const cacheKey = req.urlWithParams;
  const cached = cache.get(cacheKey);
  const staleTime = 5 * 60_000; // 5 minutes

  if (cached) {
    // Return stale data immediately
    const response$ = of(cached.response.clone());

    // Revalidate in background if stale
    if (Date.now() - cached.timestamp > staleTime) {
      next(req).pipe(
        tap(event => {
          if (event instanceof HttpResponse) {
            cache.set(cacheKey, { response: event.clone(), timestamp: Date.now() });
          }
        }),
      ).subscribe(); // Fire-and-forget revalidation
    }

    return response$;
  }

  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(cacheKey, { response: event.clone(), timestamp: Date.now() });
      }
    }),
  );
};
```

### Pattern 8: Track Expression Optimization

```typescript
@Component({
  selector: 'app-user-list',
  template: `
    <!-- BAD: tracking by index causes full re-render on sort/filter -->
    <!--
    @for (user of users(); track $index) {
      <app-user-card [user]="user" />
    }
    -->

    <!-- GOOD: tracking by unique ID enables DOM reuse -->
    @for (user of users(); track user.id) {
      <app-user-card [user]="user" />
    }

    <!-- GOOD: for static collections without IDs, $index is acceptable -->
    @for (option of staticOptions; track $index) {
      <option [value]="option.value">{{ option.label }}</option>
    }

    <!-- GOOD: composite key for items without single unique ID -->
    @for (cell of gridCells(); track cell.row + '-' + cell.col) {
      <app-grid-cell [cell]="cell" />
    }
  `,
})
export class UserList {
  readonly users = signal<User[]>([]);
  readonly staticOptions = [
    { value: 'asc', label: 'Ascending' },
    { value: 'desc', label: 'Descending' },
  ];
  readonly gridCells = signal<GridCell[]>([]);
}
```

## Advanced Patterns

### Pattern 9: Performance Profiling

```typescript
// 1. Angular DevTools (Chrome Extension)
// - Component tree inspection
// - Change detection profiling
// - Signal dependency visualization (Angular 21+)

// 2. Chrome DevTools Performance tab
// Record a session and look for:
// - Long Tasks (>50ms)
// - Layout Thrashing
// - Excessive JavaScript execution

// 3. Lighthouse CI
// npm install -g @lhci/cli
// lhci autorun --config=lighthouserc.json

// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:4200/", "http://localhost:4200/products"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["warn", { "minScore": 0.9 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }]
      }
    }
  }
}

// 4. Bundle analysis
// ng build --stats-json
// npx webpack-bundle-analyzer dist/my-app/stats.json
```

### Pattern 10: Web Worker for Heavy Computation

```typescript
// Generate web worker:
// ng generate web-worker features/data-processing/heavy-computation

// heavy-computation.worker.ts
addEventListener('message', ({ data }) => {
  const { type, payload } = data;

  switch (type) {
    case 'sort-large-dataset': {
      const sorted = payload.sort((a: any, b: any) =>
        a.name.localeCompare(b.name)
      );
      postMessage({ type: 'sort-result', payload: sorted });
      break;
    }
    case 'aggregate-metrics': {
      const aggregated = aggregateMetrics(payload);
      postMessage({ type: 'aggregate-result', payload: aggregated });
      break;
    }
  }
});

function aggregateMetrics(data: any[]): Record<string, number> {
  // Heavy computation offloaded to worker thread
  return data.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] ?? 0) + item.value;
    return acc;
  }, {} as Record<string, number>);
}

// Using the worker in a service
@Injectable({ providedIn: 'root' })
export class DataProcessingService {
  private worker: Worker | null = null;
  private readonly _result = signal<unknown>(null);
  readonly result = this._result.asReadonly();

  constructor() {
    if (typeof Worker !== 'undefined') {
      this.worker = new Worker(
        new URL('./heavy-computation.worker', import.meta.url),
        { type: 'module' }
      );

      this.worker.onmessage = ({ data }) => {
        this._result.set(data.payload);
      };
    }
  }

  sortLargeDataset(data: unknown[]): void {
    if (this.worker) {
      this.worker.postMessage({ type: 'sort-large-dataset', payload: data });
    } else {
      // Fallback for SSR or unsupported environments
      const sorted = [...data].sort((a: any, b: any) => a.name.localeCompare(b.name));
      this._result.set(sorted);
    }
  }
}
```

### Pattern 11: Preloading Critical Resources

```typescript
// app.config.ts: preload frequently visited routes
import { provideRouter, withPreloading, PreloadAllModules } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withPreloading(PreloadAllModules)),
  ],
};

// In index.html: preload critical resources
// <link rel="preconnect" href="https://api.example.com">
// <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
// <link rel="preload" href="/api/products" as="fetch" crossorigin>

// In component: programmatic preloading
@Component({
  selector: 'app-product-card',
  template: `
    <a
      [routerLink]="['/products', product().slug]"
      (mouseenter)="preloadProduct()"
    >
      {{ product().name }}
    </a>
  `,
})
export class ProductCard {
  readonly product = input.required<Product>();
  private readonly http = inject(HttpClient);

  preloadProduct(): void {
    // Preload product detail data on hover
    this.http.get(`/api/products/${this.product().slug}`)
      .pipe(take(1))
      .subscribe(); // Response will be in HTTP cache when user navigates
  }
}
```

### Pattern 12: Performance Checklist

```markdown
## Pre-Launch Performance Checklist

### Bundle Size
- [ ] All routes are lazy loaded (loadComponent/loadChildren)
- [ ] Heavy components use @defer blocks
- [ ] No unnecessary dependencies in bundle (checked with webpack-bundle-analyzer)
- [ ] Zone.js removed (zoneless mode)
- [ ] Tree-shaking effective (providedIn: 'root' for services)
- [ ] Bundle budget configured in angular.json

### Rendering
- [ ] All components use OnPush change detection
- [ ] No methods called in templates (use computed() or pipes)
- [ ] All @for loops have meaningful track expressions
- [ ] @defer used for below-the-fold content
- [ ] Virtual scrolling for lists > 100 items

### Images
- [ ] NgOptimizedImage used for all images
- [ ] LCP image has priority attribute
- [ ] Below-fold images have loading="lazy"
- [ ] Image dimensions (width/height) specified
- [ ] Image CDN/optimization service configured

### Data Fetching
- [ ] httpResource or toSignal used for template-bound data
- [ ] HTTP transfer cache enabled for SSR
- [ ] API responses cached where appropriate
- [ ] No duplicate requests during hydration

### SSR
- [ ] Route-level render modes configured (SSR/SSG/CSR)
- [ ] Incremental hydration for heavy sections
- [ ] Event replay enabled
- [ ] No browser-only API usage during SSR

### Monitoring
- [ ] Lighthouse CI configured with score thresholds
- [ ] Core Web Vitals monitored in production
- [ ] Bundle size tracked across deployments
```

## Testing Strategies

### Performance Testing

```typescript
// e2e/performance.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Performance', () => {
  test('product page meets LCP threshold', async ({ page }) => {
    await page.goto('/products');

    const lcpMetric = await page.evaluate(() =>
      new Promise<number>(resolve => {
        new PerformanceObserver(list => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1] as any;
          resolve(lastEntry.renderTime || lastEntry.loadTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      })
    );

    expect(lcpMetric).toBeLessThan(2500); // LCP < 2.5s
  });

  test('initial bundle size is within budget', async ({ page }) => {
    const requests: number[] = [];

    page.on('response', response => {
      if (response.url().endsWith('.js')) {
        const size = parseInt(response.headers()['content-length'] ?? '0');
        requests.push(size);
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const totalJS = requests.reduce((sum, size) => sum + size, 0);
    expect(totalJS).toBeLessThan(500 * 1024); // < 500KB total JS
  });

  test('no layout shifts after load', async ({ page }) => {
    await page.goto('/products');

    const cls = await page.evaluate(() =>
      new Promise<number>(resolve => {
        let clsScore = 0;
        const observer = new PerformanceObserver(list => {
          for (const entry of list.getEntries() as any[]) {
            if (!entry.hadRecentInput) clsScore += entry.value;
          }
        });
        observer.observe({ entryTypes: ['layout-shift'] });
        setTimeout(() => resolve(clsScore), 3000);
      })
    );

    expect(cls).toBeLessThan(0.1); // CLS < 0.1
  });
});
```

## Common Pitfalls

### Pitfall 1: Methods in Templates

```typescript
// WRONG: called on every change detection cycle
template: `<p>{{ getFullName() }}</p>`
getFullName() { return `${this.first} ${this.last}`; }

// CORRECT: memoized, only recalculates when dependencies change
template: `<p>{{ fullName() }}</p>`
fullName = computed(() => `${this.first()} ${this.last()}`);
```

### Pitfall 2: Missing track in @for

```typescript
// WRONG: no track expression (compiler error in Angular 21)
// @for (item of items()) { ... }

// WRONG: tracking by index causes DOM recreation on reorder
// @for (item of items(); track $index) { ... }

// CORRECT: track by unique identifier
@for (item of items(); track item.id) { ... }
```

### Pitfall 3: Over-Fetching Data

```typescript
// WRONG: fetching everything
this.http.get<User[]>('/api/users'); // Returns 50 fields per user

// CORRECT: request only needed fields
this.http.get<UserSummary[]>('/api/users', {
  params: { fields: 'id,name,email,avatar' },
});
```

### Pitfall 4: Not Using @defer for Heavy Components

```typescript
// WRONG: chart loaded in initial bundle even if below the fold
<app-analytics-chart [data]="chartData()" />

// CORRECT: defer loading until visible
@defer (on viewport) {
  <app-analytics-chart [data]="chartData()" />
} @placeholder {
  <div class="h-64 bg-gray-100 rounded animate-pulse"></div>
}
```

### Pitfall 5: Eager Loading All Routes

```typescript
// WRONG: all components in initial bundle
import { AdminDashboard } from './admin/admin-dashboard';
{ path: 'admin', component: AdminDashboard }

// CORRECT: lazy load to reduce initial bundle
{ path: 'admin', loadComponent: () => import('./admin/admin-dashboard').then(m => m.AdminDashboard) }
```

## Best Practices

1. **Use zoneless change detection** (Angular 21 default) for best performance
2. **Never call methods in templates** -- use `computed()` signals or pipes
3. **Always provide `track` expressions** in `@for` loops with unique identifiers
4. **Use `@defer` blocks** for all below-the-fold and heavy components
5. **Lazy load all routes** with `loadComponent` or `loadChildren`
6. **Use `NgOptimizedImage`** with `priority` on LCP images
7. **Enable HTTP transfer cache** for SSR to prevent duplicate requests
8. **Set bundle budgets** in `angular.json` to catch regressions
9. **Use virtual scrolling** for lists with more than 100 items
10. **Profile regularly** with Angular DevTools, Lighthouse, and bundle analyzer

## Resources

- **Angular Performance Guide**: https://angular.dev/best-practices/runtime-performance
- **Angular @defer Guide**: https://angular.dev/guide/defer
- **Angular NgOptimizedImage**: https://angular.dev/guide/image-optimization
- **Angular Zoneless Guide**: https://angular.dev/guide/zoneless
- **Core Web Vitals**: https://web.dev/vitals
- **Angular DevTools**: https://angular.dev/tools/devtools
