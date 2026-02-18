---
description: Generate Angular feature route configuration with lazy loading, guards, and resolvers
model: claude-sonnet-4-5
---

Create a new Angular route configuration following modern Angular 21+ best practices.

## Route Specification

$ARGUMENTS

## Angular 21+ Routing Standards

### 1. **Root Route Configuration**

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },

  // Lazy load standalone components
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard').then(m => m.Dashboard),
    title: 'Dashboard',
  },

  // Lazy load feature routes
  {
    path: 'users',
    loadChildren: () => import('./features/users/users.routes').then(m => m.USERS_ROUTES),
  },

  // Protected route with guard
  {
    path: 'admin',
    canActivate: [authGuard, roleGuard(['admin'])],
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES),
  },

  // Wildcard redirect
  { path: '**', redirectTo: 'dashboard' },
];
```

### 2. **Feature Route Configuration**

```typescript
// features/users/users.routes.ts
import { Routes } from '@angular/router';

export const USERS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./user-list').then(m => m.UserList),
    title: 'Users',
  },
  {
    path: 'new',
    loadComponent: () => import('./user-create').then(m => m.UserCreate),
    title: 'New User',
    canDeactivate: [unsavedChangesGuard],
  },
  {
    path: ':id',
    loadComponent: () => import('./user-detail').then(m => m.UserDetail),
    resolve: { user: userResolver },
    title: userTitleResolver,
    children: [
      { path: '', redirectTo: 'overview', pathMatch: 'full' },
      {
        path: 'overview',
        loadComponent: () => import('./user-overview').then(m => m.UserOverview),
      },
      {
        path: 'settings',
        loadComponent: () => import('./user-settings').then(m => m.UserSettings),
        canDeactivate: [unsavedChangesGuard],
      },
    ],
  },
];
```

### 3. **Route with Guards and Resolvers**

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, ResolveFn, Router } from '@angular/router';

// Functional guard
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });
};

// Functional resolver
export const userResolver: ResolveFn<User> = (route) => {
  const userService = inject(UserService);
  return userService.getById(route.paramMap.get('id')!);
};

// Dynamic title resolver
export const userTitleResolver: ResolveFn<string> = (route) => {
  const userService = inject(UserService);
  return userService.getById(route.paramMap.get('id')!).pipe(
    map(user => `${user.name} - Profile`)
  );
};
```

### 4. **Route with Feature-Scoped Providers**

```typescript
export const ORDERS_ROUTES: Routes = [
  {
    path: '',
    providers: [
      OrderService,        // Scoped to this feature only
      OrderFilterService,
    ],
    children: [
      {
        path: '',
        loadComponent: () => import('./order-list').then(m => m.OrderList),
        title: 'Orders',
      },
      {
        path: ':id',
        loadComponent: () => import('./order-detail').then(m => m.OrderDetail),
        resolve: { order: orderResolver },
      },
    ],
  },
];
```

### 5. **Nested Layout Routes**

```typescript
export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./admin-layout').then(m => m.AdminLayout),
    canActivate: [authGuard, roleGuard(['admin'])],
    children: [
      { path: '', redirectTo: 'overview', pathMatch: 'full' },
      {
        path: 'overview',
        loadComponent: () => import('./admin-overview').then(m => m.AdminOverview),
        title: 'Admin Overview',
      },
      {
        path: 'users',
        loadComponent: () => import('./admin-users').then(m => m.AdminUsers),
        title: 'Manage Users',
      },
      {
        path: 'settings',
        loadComponent: () => import('./admin-settings').then(m => m.AdminSettings),
        title: 'Admin Settings',
        canDeactivate: [unsavedChangesGuard],
      },
    ],
  },
];

// admin-layout.ts
@Component({
  selector: 'app-admin-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="admin-layout">
      <nav class="admin-sidebar">
        <a routerLink="overview" routerLinkActive="active">Overview</a>
        <a routerLink="users" routerLinkActive="active">Users</a>
        <a routerLink="settings" routerLinkActive="active">Settings</a>
      </nav>
      <main class="admin-content">
        <router-outlet />
      </main>
    </div>
  `
})
export class AdminLayout {}
```

### 6. **Dynamic and Parameterized Routes**

```typescript
export const PRODUCT_ROUTES: Routes = [
  // Simple parameter
  {
    path: ':id',
    loadComponent: () => import('./product-detail').then(m => m.ProductDetail),
  },

  // Multiple parameters
  {
    path: ':category/:id',
    loadComponent: () => import('./product-view').then(m => m.ProductView),
  },

  // Catch-all / wildcard
  {
    path: '**',
    loadComponent: () => import('./product-not-found').then(m => m.ProductNotFound),
  },
];

// Accessing params in component:
@Component({ /* ... */ })
export class ProductDetail {
  private readonly route = inject(ActivatedRoute);

  // Using toSignal for reactive route params
  private readonly params = toSignal(this.route.paramMap);
  readonly productId = computed(() => this.params()?.get('id') ?? '');

  // Or use input binding (enabled by withComponentInputBinding)
  id = input.required<string>();
}
```

### 7. **Route with Input Binding**

```typescript
// app.config.ts -- enable component input binding
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
  ],
};

// Route definition
{
  path: 'users/:id',
  resolve: { user: userResolver },
  loadComponent: () => import('./user-detail').then(m => m.UserDetail),
}

// Component receives route params and resolved data as inputs
@Component({ /* ... */ })
export class UserDetail {
  id = input.required<string>();       // From route param :id
  user = input.required<User>();       // From resolver
}
```

### 8. **Application Config with Router Features**

```typescript
// app.config.ts
import { provideRouter, withPreloading, PreloadAllModules, withComponentInputBinding, withRouterConfig } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withPreloading(PreloadAllModules),
      withComponentInputBinding(),
      withRouterConfig({
        onSameUrlNavigation: 'reload',
        paramsInheritanceStrategy: 'always',
      })
    ),
  ],
};
```

### 9. **SSR Route-Level Render Modes**

```typescript
// app.routes.server.ts
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'dashboard', renderMode: RenderMode.Server },
  { path: 'settings', renderMode: RenderMode.Client },
  {
    path: 'blog/:slug',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      const blogService = inject(BlogService);
      const posts = await blogService.getAllSlugs();
      return posts.map(slug => ({ slug }));
    },
  },
  { path: '**', renderMode: RenderMode.Server },
];
```

## Best Practices

**Route Architecture**
- ✓ Lazy load all feature routes with `loadComponent` / `loadChildren`
- ✓ Organize routes per feature in dedicated `*.routes.ts` files
- ✓ Use `SCREAMING_CASE` for route constant exports (e.g., `USERS_ROUTES`)
- ✓ Keep route definitions flat; avoid deeply nested children beyond 2-3 levels
- ✓ Define a wildcard route (`**`) at the end for 404 handling

**Guards and Resolvers**
- ✓ Use functional guards (`CanActivateFn`, `CanDeactivateFn`, `CanMatchFn`)
- ✓ Use `inject()` inside guard functions
- ✓ Return `UrlTree` for redirects instead of calling `router.navigate()`
- ✓ Use resolvers to pre-fetch data; bind resolved data via `withComponentInputBinding()`

**Performance**
- ✓ Lazy load all routes for optimal code splitting
- ✓ Use `withPreloading(PreloadAllModules)` for frequently visited routes
- ✓ Use route-level render modes for SSR optimization
- ✓ Avoid eagerly importing components in route files

**TypeScript**
- ✓ Type resolver return values with `ResolveFn<T>`
- ✓ Type guard components with `CanDeactivateFn<T>`
- ✓ Use `withComponentInputBinding()` for typed route params as inputs
- ✓ No `any` types

Generate production-ready Angular route configurations with lazy loading, guards, and type-safe resolvers.
