---
name: angular-routing-patterns
description: Master modern Angular routing including lazy loading with loadComponent/loadChildren, functional guards, functional resolvers, async redirects, preloading strategies, feature route files, route-level providers, and component input binding.
category: angular
tags: [angular, routing, lazy-loading, guards, resolvers, preloading, loadComponent, loadChildren]
related_skills: [angular-blueprint, angular-dependency-injection, angular-ssr-hydration, angular-performance-optimization]
---

# Angular Routing Patterns

Comprehensive guide to modern Angular 21+ routing covering lazy loading with `loadComponent` and `loadChildren`, functional guards and resolvers, async redirects, preloading strategies, feature route files, route-level providers for scoped services, component input binding, and navigation patterns.

## When to Use This Skill

- Configuring routes for Angular applications with lazy loading
- Implementing authentication and authorization guards
- Creating data resolvers for route-level data fetching
- Organizing routes in feature-based file structures
- Implementing preloading strategies for faster navigation
- Configuring route-level providers for feature-scoped services
- Using component input binding for route parameters
- Building complex navigation flows with nested routes

## Core Concepts

### 1. Lazy Loading
- `loadComponent` for standalone component lazy loading
- `loadChildren` for feature route file lazy loading
- Reduces initial bundle size by splitting code per route
- Each lazy-loaded route generates a separate chunk

### 2. Functional Guards
- `CanActivateFn` for route activation
- `CanDeactivateFn` for unsaved changes protection
- `CanMatchFn` for conditional route matching
- Use `inject()` inside guard functions for DI

### 3. Functional Resolvers
- `ResolveFn` for pre-fetching route data
- Data available via `ActivatedRoute.data` or input binding
- Executes before component is created

### 4. Route-Level Providers
- Provide services scoped to a route subtree
- Services are destroyed when leaving the route
- Enables feature-level service isolation

### 5. Component Input Binding
- Route params, query params, and resolver data bound to component inputs
- Enabled via `withComponentInputBinding()`
- Cleaner than injecting `ActivatedRoute`

## Quick Start

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'products', pathMatch: 'full' },
  {
    path: 'products',
    loadChildren: () =>
      import('./features/products/products.routes').then(m => m.PRODUCTS_ROUTES),
  },
  {
    path: 'admin',
    canActivate: [() => inject(AuthService).isAdmin()],
    loadChildren: () =>
      import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES),
  },
  { path: '**', redirectTo: 'products' },
];
```

## Fundamental Patterns

### Pattern 1: Lazy Loading Standalone Components

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  // Redirect
  { path: '', redirectTo: 'home', pathMatch: 'full' },

  // Eager-loaded component (small, frequently visited)
  {
    path: 'home',
    loadComponent: () => import('./features/home/home').then(m => m.Home),
  },

  // Lazy-loaded feature routes
  {
    path: 'products',
    loadChildren: () =>
      import('./features/products/products.routes').then(m => m.PRODUCTS_ROUTES),
  },

  // Lazy-loaded single component
  {
    path: 'about',
    loadComponent: () => import('./features/about/about').then(m => m.About),
  },

  // Lazy-loaded with guard
  {
    path: 'checkout',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/checkout/checkout').then(m => m.Checkout),
  },

  // Wildcard route
  {
    path: '**',
    loadComponent: () =>
      import('./features/not-found/not-found').then(m => m.NotFound),
  },
];
```

### Pattern 2: Feature Route Files

```typescript
// features/products/products.routes.ts
import { Routes } from '@angular/router';

export const PRODUCTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./product-list').then(m => m.ProductList),
  },
  {
    path: 'category/:categorySlug',
    loadComponent: () =>
      import('./product-list').then(m => m.ProductList),
  },
  {
    path: ':slug',
    loadComponent: () =>
      import('./product-detail').then(m => m.ProductDetail),
  },
];

// features/admin/admin.routes.ts
import { Routes } from '@angular/router';
import { AdminService } from './services/admin.service';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    // Route-level provider: AdminService only exists within admin routes
    providers: [AdminService],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./admin-dashboard').then(m => m.AdminDashboard),
      },
      {
        path: 'users',
        loadComponent: () =>
          import('./user-management').then(m => m.UserManagement),
      },
      {
        path: 'users/:id',
        loadComponent: () =>
          import('./user-detail').then(m => m.UserDetail),
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./admin-settings').then(m => m.AdminSettings),
      },
    ],
  },
];

// features/account/account.routes.ts
import { Routes } from '@angular/router';

export const ACCOUNT_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./account-layout').then(m => m.AccountLayout),
    children: [
      { path: '', redirectTo: 'profile', pathMatch: 'full' },
      {
        path: 'profile',
        loadComponent: () =>
          import('./profile').then(m => m.Profile),
      },
      {
        path: 'orders',
        loadComponent: () =>
          import('./order-history').then(m => m.OrderHistory),
      },
      {
        path: 'orders/:orderId',
        loadComponent: () =>
          import('./order-detail').then(m => m.OrderDetail),
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./account-settings').then(m => m.AccountSettings),
      },
    ],
  },
];
```

### Pattern 3: Functional Guards

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, CanDeactivateFn, CanMatchFn, Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';

// Basic authentication guard
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });
};

// Role-based guard factory
export function roleGuard(...allowedRoles: string[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const user = auth.user();

    if (user && allowedRoles.includes(user.role)) {
      return true;
    }

    return router.createUrlTree(['/forbidden']);
  };
}

// Admin guard (composed)
export const adminGuard: CanActivateFn = roleGuard('admin');

// Editor guard (composed)
export const editorGuard: CanActivateFn = roleGuard('admin', 'editor');

// Unsaved changes guard
export interface HasUnsavedChanges {
  hasUnsavedChanges(): boolean;
}

export const unsavedChangesGuard: CanDeactivateFn<HasUnsavedChanges> = (component) => {
  if (component.hasUnsavedChanges()) {
    return confirm('You have unsaved changes. Are you sure you want to leave?');
  }
  return true;
};

// Feature flag guard (canMatch)
export const featureGuard: CanMatchFn = (route) => {
  const featureFlags = inject(FeatureFlagService);
  const featureName = route.data?.['feature'] as string;
  return featureName ? featureFlags.isEnabled(featureName) : true;
};

// Rate limiting guard
export function rateLimitGuard(maxAttempts: number, windowMs: number): CanActivateFn {
  const attempts = new Map<string, number[]>();

  return (route, state) => {
    const now = Date.now();
    const key = state.url;
    const timestamps = attempts.get(key) ?? [];

    // Remove expired timestamps
    const valid = timestamps.filter(t => now - t < windowMs);

    if (valid.length >= maxAttempts) {
      return false; // Rate limited
    }

    valid.push(now);
    attempts.set(key, valid);
    return true;
  };
}

// Usage in routes
export const routes: Routes = [
  {
    path: 'admin',
    canActivate: [authGuard, adminGuard],
    loadChildren: () => import('./admin/admin.routes').then(m => m.ADMIN_ROUTES),
  },
  {
    path: 'editor',
    canActivate: [authGuard, editorGuard],
    canDeactivate: [unsavedChangesGuard],
    loadComponent: () => import('./editor/editor').then(m => m.Editor),
  },
  {
    path: 'beta-feature',
    canMatch: [featureGuard],
    data: { feature: 'betaDashboard' },
    loadComponent: () => import('./beta/beta-dashboard').then(m => m.BetaDashboard),
  },
];
```

### Pattern 4: Functional Resolvers

```typescript
import { inject } from '@angular/core';
import { ResolveFn, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { catchError, of } from 'rxjs';

interface Product {
  id: string;
  name: string;
  slug: string;
  price: number;
}

// Simple resolver
export const productResolver: ResolveFn<Product | null> = (route) => {
  const http = inject(HttpClient);
  const router = inject(Router);
  const slug = route.paramMap.get('slug')!;

  return http.get<Product>(`/api/products/${slug}`).pipe(
    catchError(() => {
      router.navigate(['/products']);
      return of(null);
    }),
  );
};

// Resolver with multiple data fetches
export const productPageResolver: ResolveFn<{
  product: Product;
  relatedProducts: Product[];
}> = async (route) => {
  const http = inject(HttpClient);
  const slug = route.paramMap.get('slug')!;

  const [product, relatedProducts] = await Promise.all([
    firstValueFrom(http.get<Product>(`/api/products/${slug}`)),
    firstValueFrom(http.get<Product[]>(`/api/products/${slug}/related`)),
  ]);

  return { product, relatedProducts };
};

// Title resolver
export const productTitleResolver: ResolveFn<string> = (route) => {
  const http = inject(HttpClient);
  const slug = route.paramMap.get('slug')!;

  return http.get<Product>(`/api/products/${slug}`).pipe(
    map(product => `${product.name} | My Store`),
    catchError(() => of('Product Not Found | My Store')),
  );
};

// Usage in routes
export const PRODUCTS_ROUTES: Routes = [
  {
    path: ':slug',
    resolve: {
      productData: productPageResolver,
    },
    title: productTitleResolver,
    loadComponent: () =>
      import('./product-detail').then(m => m.ProductDetail),
  },
];
```

### Pattern 5: Component Input Binding

```typescript
// app.config.ts - Enable component input binding
import { provideRouter, withComponentInputBinding } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
  ],
};

// Component that receives route params, query params, and resolver data as inputs
import { Component, input, computed } from '@angular/core';

@Component({
  selector: 'app-product-detail',
  template: `
    @if (productData()) {
      <h1>{{ productData()!.product.name }}</h1>
      <p>{{ productData()!.product.price | currency }}</p>

      <h2>Related Products</h2>
      @for (related of productData()!.relatedProducts; track related.id) {
        <app-product-card [product]="related" />
      }
    }
  `,
})
export class ProductDetail {
  // Route param :slug automatically bound to input
  readonly slug = input<string>();

  // Query param ?color=red automatically bound to input
  readonly color = input<string>();

  // Resolver data automatically bound to input
  readonly productData = input<{ product: Product; relatedProducts: Product[] }>();
}

// Route configuration
export const PRODUCTS_ROUTES: Routes = [
  {
    path: ':slug', // :slug maps to slug input
    resolve: { productData: productPageResolver }, // productData maps to productData input
    loadComponent: () => import('./product-detail').then(m => m.ProductDetail),
  },
];

// Navigation: /products/blue-shirt?color=red
// - slug input receives 'blue-shirt'
// - color input receives 'red'
// - productData input receives resolver result
```

### Pattern 6: Async Redirects (Angular 20+)

```typescript
import { Routes } from '@angular/router';
import { inject } from '@angular/core';

export const routes: Routes = [
  // Async redirect based on config
  {
    path: 'old-dashboard',
    redirectTo: async () => {
      const config = inject(AppConfigService);
      const newPath = await config.getRedirectPath('old-dashboard');
      return newPath;
    },
  },

  // Async redirect based on user role
  {
    path: 'portal',
    redirectTo: async () => {
      const auth = inject(AuthService);
      const user = auth.user();

      if (!user) return '/login';
      if (user.role === 'admin') return '/admin/dashboard';
      if (user.role === 'editor') return '/editor/workspace';
      return '/dashboard';
    },
  },

  // Async redirect with API call
  {
    path: 'short/:code',
    redirectTo: async (route) => {
      const http = inject(HttpClient);
      const code = route.paramMap.get('code');
      try {
        const result = await firstValueFrom(
          http.get<{ target: string }>(`/api/links/${code}`)
        );
        return result.target;
      } catch {
        return '/not-found';
      }
    },
  },
];
```

### Pattern 7: Preloading Strategies

```typescript
// app.config.ts
import { provideRouter, withPreloading, PreloadAllModules } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),
      // Strategy 1: Preload all lazy routes after initial load
      withPreloading(PreloadAllModules),
    ),
  ],
};

// Custom preloading strategy: only preload marked routes
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, timer } from 'rxjs';
import { mergeMap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class SelectivePreloadStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<unknown>): Observable<unknown> {
    if (route.data?.['preload']) {
      // Optional delay to not compete with initial page load
      const delay = route.data?.['preloadDelay'] ?? 2000;
      return timer(delay).pipe(mergeMap(() => load()));
    }
    return of(null);
  }
}

// Routes with preload hints
export const routes: Routes = [
  {
    path: 'products',
    data: { preload: true }, // Preload after 2s
    loadChildren: () => import('./features/products/products.routes').then(m => m.PRODUCTS_ROUTES),
  },
  {
    path: 'admin',
    data: { preload: false }, // Do not preload (admin is rarely visited)
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES),
  },
  {
    path: 'checkout',
    data: { preload: true, preloadDelay: 5000 }, // Preload after 5s
    loadComponent: () => import('./features/checkout/checkout').then(m => m.Checkout),
  },
];

// Use custom strategy
provideRouter(routes, withPreloading(SelectivePreloadStrategy));
```

### Pattern 8: Nested Routes with Layout Components

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layouts/public-layout').then(m => m.PublicLayout),
    children: [
      { path: '', loadComponent: () => import('./features/home/home').then(m => m.Home) },
      { path: 'products', loadChildren: () => import('./features/products/products.routes').then(m => m.PRODUCTS_ROUTES) },
      { path: 'about', loadComponent: () => import('./features/about/about').then(m => m.About) },
    ],
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./layouts/dashboard-layout').then(m => m.DashboardLayout),
    children: [
      { path: '', loadComponent: () => import('./features/dashboard/overview').then(m => m.Overview) },
      { path: 'analytics', loadComponent: () => import('./features/dashboard/analytics').then(m => m.Analytics) },
      { path: 'settings', loadComponent: () => import('./features/dashboard/settings').then(m => m.Settings) },
    ],
  },
  {
    path: 'auth',
    loadComponent: () => import('./layouts/auth-layout').then(m => m.AuthLayout),
    children: [
      { path: 'login', loadComponent: () => import('./features/auth/login').then(m => m.Login) },
      { path: 'register', loadComponent: () => import('./features/auth/register').then(m => m.Register) },
      { path: 'forgot-password', loadComponent: () => import('./features/auth/forgot-password').then(m => m.ForgotPassword) },
    ],
  },
];

// layouts/dashboard-layout.ts
@Component({
  selector: 'app-dashboard-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="dashboard-layout">
      <aside class="sidebar">
        <nav>
          <a routerLink="/dashboard" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Overview</a>
          <a routerLink="/dashboard/analytics" routerLinkActive="active">Analytics</a>
          <a routerLink="/dashboard/settings" routerLinkActive="active">Settings</a>
        </nav>
      </aside>
      <main class="content">
        <router-outlet />
      </main>
    </div>
  `,
})
export class DashboardLayout {}
```

## Advanced Patterns

### Pattern 9: Programmatic Navigation

```typescript
import { Component, inject } from '@angular/core';
import { Router, NavigationExtras } from '@angular/router';

@Component({
  selector: 'app-search',
  template: `
    <input #search (keyup.enter)="onSearch(search.value)" />
    <button (click)="goToProduct('widget-pro')">View Widget Pro</button>
    <button (click)="goBack()">Back</button>
  `,
})
export class SearchComponent {
  private readonly router = inject(Router);

  // Navigate with query params
  onSearch(query: string): void {
    this.router.navigate(['/products'], {
      queryParams: { q: query, page: 1 },
      queryParamsHandling: 'merge', // Preserve existing query params
    });
  }

  // Navigate with route params
  goToProduct(slug: string): void {
    this.router.navigate(['/products', slug]);
  }

  // Navigate with extras
  goToCheckout(): void {
    this.router.navigate(['/checkout'], {
      state: { fromCart: true }, // Pass state via navigation
    });
  }

  // Navigate back
  goBack(): void {
    const location = inject(Location);
    location.back();
  }

  // Navigate with replaceUrl (no browser history entry)
  redirectToLogin(): void {
    this.router.navigate(['/login'], { replaceUrl: true });
  }
}
```

### Pattern 10: Route Transition Animations

```typescript
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { trigger, transition, style, animate, query, group } from '@angular/animations';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  animations: [
    trigger('routeAnimations', [
      transition('* <=> *', [
        query(':enter, :leave', [
          style({ position: 'absolute', width: '100%' }),
        ], { optional: true }),
        group([
          query(':leave', [
            animate('300ms ease-out', style({ opacity: 0, transform: 'translateX(-20px)' })),
          ], { optional: true }),
          query(':enter', [
            style({ opacity: 0, transform: 'translateX(20px)' }),
            animate('300ms ease-out', style({ opacity: 1, transform: 'translateX(0)' })),
          ], { optional: true }),
        ]),
      ]),
    ]),
  ],
  template: `
    <div class="route-container" [@routeAnimations]="outlet.activatedRouteData">
      <router-outlet #outlet="outlet" />
    </div>
  `,
})
export class AppComponent {}
```

### Pattern 11: Router Events for Loading Indicators

```typescript
import { Component, inject, signal } from '@angular/core';
import { Router, NavigationStart, NavigationEnd, NavigationCancel, NavigationError } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  template: `
    @if (isNavigating()) {
      <div class="navigation-progress">
        <div class="progress-bar"></div>
      </div>
    }
    <router-outlet />
  `,
})
export class AppComponent {
  private readonly router = inject(Router);
  readonly isNavigating = signal(false);

  constructor() {
    this.router.events.pipe(
      takeUntilDestroyed(),
    ).subscribe(event => {
      if (event instanceof NavigationStart) {
        this.isNavigating.set(true);
      }
      if (
        event instanceof NavigationEnd ||
        event instanceof NavigationCancel ||
        event instanceof NavigationError
      ) {
        this.isNavigating.set(false);
      }
    });
  }
}
```

## Testing Strategies

### Testing Routes

```typescript
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { routes } from './app.routes';

describe('Application Routes', () => {
  let router: Router;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideRouter(routes)],
    });
    router = TestBed.inject(Router);
  });

  it('should navigate to products', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/products');
    expect(router.url).toBe('/products');
  });

  it('should redirect empty path to products', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/');
    expect(router.url).toBe('/products');
  });

  it('should lazy load product detail', async () => {
    const harness = await RouterTestingHarness.create();
    const component = await harness.navigateByUrl('/products/test-product');
    expect(component).toBeTruthy();
    expect(router.url).toBe('/products/test-product');
  });
});
```

## Common Pitfalls

### Pitfall 1: Missing pathMatch on Redirect Routes

```typescript
// WRONG: matches any path starting with ''
{ path: '', redirectTo: 'home' }

// CORRECT: only match exact empty path
{ path: '', redirectTo: 'home', pathMatch: 'full' }
```

### Pitfall 2: Eager Loading Everything

```typescript
// WRONG: imports component directly (added to main bundle)
import { ProductList } from './features/products/product-list';
{ path: 'products', component: ProductList }

// CORRECT: lazy load to reduce initial bundle
{ path: 'products', loadComponent: () => import('./features/products/product-list').then(m => m.ProductList) }
```

### Pitfall 3: Not Handling Guard Failures Gracefully

```typescript
// WRONG: guard returns false (user sees nothing)
export const authGuard: CanActivateFn = () => {
  return inject(AuthService).isAuthenticated();
};

// CORRECT: redirect to login with return URL
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) return true;
  return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};
```

## Best Practices

1. **Always lazy load** feature routes with `loadComponent` or `loadChildren`
2. **Use functional guards** instead of class-based guards
3. **Organize routes in feature files** (`*.routes.ts`) colocated with feature components
4. **Enable `withComponentInputBinding()`** for clean route parameter access
5. **Use preloading strategies** to preload frequently visited routes
6. **Use route-level providers** for feature-scoped services
7. **Handle guard failures** with redirects, not boolean returns
8. **Add `pathMatch: 'full'`** on redirect routes from empty paths
9. **Use `canMatch`** for feature flag routing instead of `canActivate`
10. **Test routes** with `RouterTestingHarness` for navigation behavior

## Resources

- **Angular Routing Guide**: https://angular.dev/guide/routing
- **Angular Lazy Loading**: https://angular.dev/reference/migrations/route-lazy-loading
- **Angular Route Guards**: https://angular.dev/guide/routing/route-guards
- **Angular Router API**: https://angular.dev/api/router
- **Angular Component Input Binding**: https://angular.dev/guide/routing/routing-with-input-binding
