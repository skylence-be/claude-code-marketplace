---
description: Generate a functional Angular route guard with CanActivateFn, CanDeactivateFn, and inject()
model: claude-sonnet-4-5
---

Create a new Angular functional route guard following modern Angular 21+ best practices.

## Guard Specification

$ARGUMENTS

## Angular 21+ Functional Guard Standards

### 1. **CanActivate Guard**

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

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
```

### 2. **Role-Based Guard**

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    const userRole = authService.currentUser()?.role;

    if (userRole && allowedRoles.includes(userRole)) {
      return true;
    }

    return router.createUrlTree(['/unauthorized']);
  };
};

// Usage in routes:
// { path: 'admin', canActivate: [roleGuard(['admin', 'superadmin'])], ... }
```

### 3. **Async Guard**

```typescript
export const subscriptionGuard: CanActivateFn = async (route, state) => {
  const subscriptionService = inject(SubscriptionService);
  const router = inject(Router);

  try {
    const hasAccess = await subscriptionService.checkAccess(route.data['feature']);
    if (hasAccess) {
      return true;
    }
    return router.createUrlTree(['/upgrade']);
  } catch {
    return router.createUrlTree(['/error']);
  }
};
```

### 4. **CanDeactivate Guard (Unsaved Changes)**

```typescript
import { CanDeactivateFn } from '@angular/router';

export interface HasUnsavedChanges {
  hasUnsavedChanges: () => boolean;
}

export const unsavedChangesGuard: CanDeactivateFn<HasUnsavedChanges> = (
  component,
  currentRoute,
  currentState,
  nextState
) => {
  if (component.hasUnsavedChanges()) {
    return window.confirm(
      'You have unsaved changes. Are you sure you want to leave?'
    );
  }
  return true;
};

// Component implementing the interface:
@Component({ /* ... */ })
export class EditForm implements HasUnsavedChanges {
  private readonly form = inject(FormBuilder).group({
    name: [''],
    email: [''],
  });

  hasUnsavedChanges(): boolean {
    return this.form.dirty;
  }
}
```

### 5. **CanMatch Guard (Conditional Route Matching)**

```typescript
import { CanMatchFn, Route, UrlSegment } from '@angular/router';

export const featureFlagGuard = (flag: string): CanMatchFn => {
  return (route: Route, segments: UrlSegment[]) => {
    const featureFlags = inject(FeatureFlagService);
    return featureFlags.isEnabled(flag);
  };
};

// Usage in routes -- conditionally match routes:
// {
//   path: 'new-dashboard',
//   canMatch: [featureFlagGuard('new-dashboard')],
//   loadComponent: () => import('./new-dashboard').then(m => m.NewDashboard)
// },
// {
//   path: 'new-dashboard',
//   loadComponent: () => import('./old-dashboard').then(m => m.OldDashboard)
// }
```

### 6. **Resolver Function**

```typescript
import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';

export const userResolver: ResolveFn<User> = (route) => {
  const userService = inject(UserService);
  return userService.getById(route.paramMap.get('id')!);
};

// Async resolver
export const dashboardResolver: ResolveFn<DashboardData> = async (route) => {
  const dashboardService = inject(DashboardService);
  return dashboardService.loadDashboard();
};

// Usage in routes:
// {
//   path: 'users/:id',
//   resolve: { user: userResolver },
//   loadComponent: () => import('./user-detail').then(m => m.UserDetail)
// }
//
// In component: route.data['user'] or input('user')
```

### 7. **Composing Multiple Guards**

```typescript
// Route configuration with multiple guards
export const ADMIN_ROUTES: Routes = [
  {
    path: 'admin',
    canActivate: [authGuard, roleGuard(['admin'])],
    children: [
      {
        path: 'settings',
        loadComponent: () => import('./admin-settings').then(m => m.AdminSettings),
        canDeactivate: [unsavedChangesGuard],
      },
      {
        path: 'users/:id',
        resolve: { user: userResolver },
        loadComponent: () => import('./admin-user-detail').then(m => m.AdminUserDetail),
      },
    ],
  },
];
```

### 8. **Guard with Redirect and State**

```typescript
export const onboardingGuard: CanActivateFn = (route, state) => {
  const userService = inject(UserService);
  const router = inject(Router);

  const user = userService.currentUser();

  if (!user) {
    return router.createUrlTree(['/login'], {
      queryParams: { returnUrl: state.url },
    });
  }

  if (!user.onboardingComplete) {
    return router.createUrlTree(['/onboarding'], {
      queryParams: { step: user.onboardingStep },
    });
  }

  return true;
};
```

## Best Practices

**Guard Design**
- ✓ Use functional guards (`CanActivateFn`, `CanDeactivateFn`, `CanMatchFn`)
- ✓ Use `inject()` to access services inside guard functions
- ✓ Return `UrlTree` for redirects instead of calling `router.navigate()`
- ✓ Use factory functions for configurable guards (e.g., `roleGuard(['admin'])`)
- ✓ Keep guards focused on a single concern

**TypeScript**
- ✓ Properly type all guard function parameters
- ✓ Type the component in `CanDeactivateFn<T>`
- ✓ Use `ResolveFn<T>` with proper return types
- ✓ No `any` types

**Error Handling**
- ✓ Wrap async guards in try/catch
- ✓ Provide fallback redirects on error
- ✓ Log guard failures for debugging

**Route Configuration**
- ✓ Apply guards at the appropriate route level
- ✓ Compose multiple guards for layered access control
- ✓ Use `canMatch` for feature flags and A/B testing
- ✓ Use resolvers to pre-fetch data before route activation

Generate production-ready, type-safe Angular functional route guards.
