---
name: angular-dependency-injection
description: Master Angular dependency injection patterns including inject() function, InjectionToken, providedIn options, hierarchical injectors, route-level providers, factory functions, functional interceptors, and testing DI configurations.
category: angular
tags: [angular, dependency-injection, inject, injection-token, providers, services, interceptors]
related_skills: [angular-blueprint, angular-signals-patterns, angular-routing-patterns, angular-testing-patterns]
---

# Angular Dependency Injection Patterns

Comprehensive guide to Angular's dependency injection system covering the modern `inject()` function, InjectionToken for non-class dependencies, provider scoping strategies, hierarchical injectors, route-level providers, factory functions, functional interceptors, and testing DI configurations in Angular 21+ applications.

## When to Use This Skill

- Registering and consuming services across an Angular application
- Choosing the right provider scope (root, route, component)
- Creating injectable configuration with InjectionToken
- Building functional HTTP interceptors
- Implementing factory providers for complex initialization
- Understanding the injector hierarchy for proper service isolation
- Testing components and services with mock dependencies
- Creating abstract service interfaces with injection tokens

## Core Concepts

### 1. The inject() Function
- Modern replacement for constructor injection
- Cleaner syntax, better TypeScript inference
- Works in constructors, field initializers, and factory functions
- Supports options: `optional`, `self`, `skipSelf`, `host`

### 2. Provider Scopes
- `providedIn: 'root'` for application-wide singletons (tree-shakable)
- `providedIn: 'platform'` for shared across Angular applications
- Route-level providers for feature-scoped services
- Component-level providers for per-component instances

### 3. InjectionToken
- Type-safe tokens for non-class dependencies
- Support factory defaults for tree-shaking
- Used for configuration, constants, and abstract interfaces

### 4. Hierarchical Injectors
- Root injector -> Route injector -> Component injector
- Child injectors inherit from parents
- Each level can override parent providers

### 5. Functional Patterns
- Functional interceptors with `HttpInterceptorFn`
- Functional guards with `CanActivateFn`
- Functional resolvers with `ResolveFn`
- Factory providers with `useFactory`

## Quick Start

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);

  getUser(id: string) {
    return this.http.get<User>(`/api/users/${id}`);
  }
}

// In a component
@Component({ /* ... */ })
export class UserProfile {
  private readonly userService = inject(UserService);
  readonly userId = input.required<string>();
  readonly user = httpResource<User>(() => `/api/users/${this.userId()}`);
}
```

## Fundamental Patterns

### Pattern 1: The inject() Function vs Constructor Injection

```typescript
import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../core/auth/auth.service';

// PREFERRED: inject() function
@Component({
  selector: 'app-user-settings',
  template: `<h1>Settings for {{ authService.user()?.name }}</h1>`,
})
export class UserSettings {
  // Field-level injection -- clean and concise
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  protected readonly authService = inject(AuthService);

  // inject() with options
  private readonly optionalLogger = inject(LoggerService, { optional: true });
}

// LEGACY: constructor injection (still works but not recommended for new code)
@Component({
  selector: 'app-user-settings-legacy',
  template: `<h1>Settings</h1>`,
})
export class UserSettingsLegacy {
  constructor(
    private readonly http: HttpClient,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly authService: AuthService,
  ) {}
}
```

### Pattern 2: Service Registration with providedIn

```typescript
import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

// Root-level singleton (most common, tree-shakable)
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly _user = signal<User | null>(null);

  readonly user = this._user.asReadonly();
  readonly isAuthenticated = computed(() => this._user() !== null);

  async login(email: string, password: string): Promise<boolean> {
    try {
      const response = await firstValueFrom(
        this.http.post<{ user: User }>('/api/auth/login', { email, password })
      );
      this._user.set(response.user);
      return true;
    } catch {
      return false;
    }
  }

  logout(): void {
    this._user.set(null);
  }
}

// Platform-level (shared across multiple Angular apps on same page)
@Injectable({ providedIn: 'platform' })
export class AnalyticsService {
  track(event: string, data: Record<string, unknown>): void {
    // Shared analytics across micro-frontends
  }
}

// No providedIn -- must be explicitly provided somewhere
// Use when service should only exist within a specific scope
@Injectable()
export class FeatureDataService {
  private readonly http = inject(HttpClient);

  getData() {
    return this.http.get('/api/feature-data');
  }
}
```

### Pattern 3: InjectionToken for Configuration and Constants

```typescript
import { InjectionToken, inject, Injectable } from '@angular/core';

// Simple value token with factory default
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => '/api',
});

// Complex configuration token
export interface AppConfig {
  apiUrl: string;
  environment: 'development' | 'staging' | 'production';
  features: {
    darkMode: boolean;
    analytics: boolean;
    beta: boolean;
  };
}

export const APP_CONFIG = new InjectionToken<AppConfig>('APP_CONFIG', {
  providedIn: 'root',
  factory: () => ({
    apiUrl: '/api',
    environment: 'production',
    features: {
      darkMode: true,
      analytics: true,
      beta: false,
    },
  }),
});

// Token for abstract interface (no factory -- must be provided)
export interface Logger {
  log(message: string): void;
  error(message: string, error?: Error): void;
  warn(message: string): void;
}

export const LOGGER = new InjectionToken<Logger>('LOGGER');

// Using tokens in services
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = inject(API_BASE_URL);
  private readonly config = inject(APP_CONFIG);
  private readonly logger = inject(LOGGER, { optional: true });
  private readonly http = inject(HttpClient);

  get<T>(endpoint: string) {
    const url = `${this.baseUrl}${endpoint}`;
    this.logger?.log(`GET ${url}`);
    return this.http.get<T>(url);
  }
}

// Providing tokens in app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: API_BASE_URL, useValue: 'https://api.example.com' },
    {
      provide: APP_CONFIG,
      useValue: {
        apiUrl: 'https://api.example.com',
        environment: 'production',
        features: { darkMode: true, analytics: true, beta: false },
      },
    },
    {
      provide: LOGGER,
      useClass: ConsoleLoggerService,
    },
  ],
};
```

### Pattern 4: Hierarchical Injectors and Provider Scope

```typescript
import { Component, Injectable, inject, signal } from '@angular/core';

// Scenario: each feature tab needs its own instance of a form state service

@Injectable() // No providedIn -- will be provided at route level
export class FormStateService {
  private readonly _isDirty = signal(false);
  private readonly _values = signal<Record<string, unknown>>({});

  readonly isDirty = this._isDirty.asReadonly();
  readonly values = this._values.asReadonly();

  setValue(key: string, value: unknown): void {
    this._values.update(v => ({ ...v, [key]: value }));
    this._isDirty.set(true);
  }

  reset(): void {
    this._values.set({});
    this._isDirty.set(false);
  }
}

// Route-level provider: each route gets its own FormStateService instance
// features/profile/profile.routes.ts
export const PROFILE_ROUTES: Routes = [
  {
    path: '',
    providers: [FormStateService], // New instance for this route tree
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./profile-page').then(m => m.ProfilePage),
      },
      {
        path: 'edit',
        loadComponent: () =>
          import('./profile-edit').then(m => m.ProfileEdit),
      },
    ],
  },
];

// Component-level provider: each component instance gets its own service
@Component({
  selector: 'app-inline-editor',
  providers: [FormStateService], // New instance per component
  template: `
    <input (input)="formState.setValue('text', $any($event.target).value)" />
    @if (formState.isDirty()) {
      <button (click)="formState.reset()">Reset</button>
    }
  `,
})
export class InlineEditor {
  protected readonly formState = inject(FormStateService);
}
```

### Pattern 5: Factory Providers

```typescript
import { InjectionToken, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

// Factory with dependencies
export const WINDOW = new InjectionToken<Window | null>('WINDOW', {
  providedIn: 'root',
  factory: () => {
    const platformId = inject(PLATFORM_ID);
    return isPlatformBrowser(platformId) ? window : null;
  },
});

export const LOCAL_STORAGE = new InjectionToken<Storage | null>('LOCAL_STORAGE', {
  providedIn: 'root',
  factory: () => {
    const win = inject(WINDOW);
    return win?.localStorage ?? null;
  },
});

// Usage in a service
@Injectable({ providedIn: 'root' })
export class StorageService {
  private readonly storage = inject(LOCAL_STORAGE);

  getItem(key: string): string | null {
    return this.storage?.getItem(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.storage?.setItem(key, value);
  }

  removeItem(key: string): void {
    this.storage?.removeItem(key);
  }
}

// useFactory in providers array
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: 'API_CLIENT',
      useFactory: () => {
        const config = inject(APP_CONFIG);
        const http = inject(HttpClient);
        return new ApiClient(http, config.apiUrl);
      },
    },
    // Factory with external configuration
    {
      provide: LOGGER,
      useFactory: () => {
        const config = inject(APP_CONFIG);
        if (config.environment === 'production') {
          return inject(RemoteLoggerService);
        }
        return inject(ConsoleLoggerService);
      },
    },
  ],
};
```

### Pattern 6: Functional HTTP Interceptors

```typescript
import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';

// Authentication interceptor
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.token();

  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(req);
};

// Error handling interceptor
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        authService.logout();
        router.navigate(['/login']);
      } else if (error.status === 403) {
        router.navigate(['/forbidden']);
      } else if (error.status >= 500) {
        console.error('Server error:', error.message);
      }
      return throwError(() => error);
    }),
  );
};

// Logging interceptor
export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const logger = inject(LOGGER, { optional: true });
  const startTime = performance.now();

  logger?.log(`HTTP ${req.method} ${req.url}`);

  return next(req).pipe(
    tap({
      next: () => {
        const duration = performance.now() - startTime;
        logger?.log(`HTTP ${req.method} ${req.url} completed in ${duration.toFixed(0)}ms`);
      },
      error: (error) => {
        const duration = performance.now() - startTime;
        logger?.error(`HTTP ${req.method} ${req.url} failed in ${duration.toFixed(0)}ms`, error);
      },
    }),
  );
};

// Caching interceptor
const cache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_TTL = 60_000; // 1 minute

export const cachingInterceptor: HttpInterceptorFn = (req, next) => {
  // Only cache GET requests
  if (req.method !== 'GET') return next(req);

  const cached = cache.get(req.urlWithParams);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return of(new HttpResponse({ body: cached.data }));
  }

  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(req.urlWithParams, {
          data: event.body,
          timestamp: Date.now(),
        });
      }
    }),
  );
};

// Register interceptors in app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        loggingInterceptor,
        authInterceptor,
        errorInterceptor,
        cachingInterceptor,
      ]),
    ),
  ],
};
```

### Pattern 7: inject() Options for Advanced Scenarios

```typescript
import { Component, inject, Optional, Self, SkipSelf, Host, forwardRef } from '@angular/core';

@Component({
  selector: 'app-child',
  template: `<p>Child component</p>`,
})
export class ChildComponent {
  // Optional: returns null if not found instead of throwing
  private readonly logger = inject(LoggerService, { optional: true });

  // Self: only look in this component's own injector
  private readonly localConfig = inject(LocalConfigService, { self: true, optional: true });

  // SkipSelf: skip this component's injector, look in parents only
  private readonly parentForm = inject(FormStateService, { skipSelf: true, optional: true });

  // Host: look up to the host component's injector (stops at host boundary)
  private readonly hostTheme = inject(ThemeService, { host: true, optional: true });
}

// Practical example: nested form groups
@Component({
  selector: 'app-address-form',
  providers: [FormStateService], // Each address form gets its own state
  template: `
    <div class="address-form">
      <input placeholder="Street" (input)="formState.setValue('street', $any($event.target).value)" />
      <input placeholder="City" (input)="formState.setValue('city', $any($event.target).value)" />
    </div>
  `,
})
export class AddressForm {
  // Gets the FormStateService provided by THIS component
  protected readonly formState = inject(FormStateService);

  // Gets the parent form's state service (skips own provider)
  private readonly parentForm = inject(FormStateService, { skipSelf: true, optional: true });
}
```

### Pattern 8: Abstract Service Pattern with InjectionToken

```typescript
import { InjectionToken, Injectable, inject } from '@angular/core';

// Define abstract interface
export interface DataStore<T> {
  getAll(): Promise<T[]>;
  getById(id: string): Promise<T | null>;
  create(item: Omit<T, 'id'>): Promise<T>;
  update(id: string, item: Partial<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

// Create typed token
export const USER_STORE = new InjectionToken<DataStore<User>>('USER_STORE');

// HTTP implementation
@Injectable()
export class HttpUserStore implements DataStore<User> {
  private readonly http = inject(HttpClient);

  async getAll(): Promise<User[]> {
    return firstValueFrom(this.http.get<User[]>('/api/users'));
  }

  async getById(id: string): Promise<User | null> {
    try {
      return await firstValueFrom(this.http.get<User>(`/api/users/${id}`));
    } catch {
      return null;
    }
  }

  async create(item: Omit<User, 'id'>): Promise<User> {
    return firstValueFrom(this.http.post<User>('/api/users', item));
  }

  async update(id: string, item: Partial<User>): Promise<User> {
    return firstValueFrom(this.http.patch<User>(`/api/users/${id}`, item));
  }

  async delete(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`/api/users/${id}`));
  }
}

// In-memory implementation (for testing or prototyping)
@Injectable()
export class InMemoryUserStore implements DataStore<User> {
  private users: User[] = [];

  async getAll(): Promise<User[]> {
    return [...this.users];
  }

  async getById(id: string): Promise<User | null> {
    return this.users.find(u => u.id === id) ?? null;
  }

  async create(item: Omit<User, 'id'>): Promise<User> {
    const user: User = { ...item, id: crypto.randomUUID() } as User;
    this.users.push(user);
    return user;
  }

  async update(id: string, item: Partial<User>): Promise<User> {
    const index = this.users.findIndex(u => u.id === id);
    if (index === -1) throw new Error('User not found');
    this.users[index] = { ...this.users[index], ...item };
    return this.users[index];
  }

  async delete(id: string): Promise<void> {
    this.users = this.users.filter(u => u.id !== id);
  }
}

// Provide the appropriate implementation
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: USER_STORE, useClass: HttpUserStore },
  ],
};

// In tests
TestBed.configureTestingModule({
  providers: [
    { provide: USER_STORE, useClass: InMemoryUserStore },
  ],
});

// Consumer does not know which implementation is used
@Component({ /* ... */ })
export class UserList {
  private readonly userStore = inject(USER_STORE);

  async loadUsers() {
    const users = await this.userStore.getAll();
    // Works with any implementation
  }
}
```

## Advanced Patterns

### Pattern 9: Multi Providers

```typescript
import { InjectionToken, inject, Injectable } from '@angular/core';

// Multi-provider token: collects all provided values into an array
export interface AppInitializer {
  name: string;
  initialize(): Promise<void>;
}

export const APP_INITIALIZERS = new InjectionToken<AppInitializer[]>('APP_INITIALIZERS');

@Injectable({ providedIn: 'root' })
export class AuthInitializer implements AppInitializer {
  name = 'auth';
  private readonly authService = inject(AuthService);

  async initialize(): Promise<void> {
    await this.authService.loadSession();
  }
}

@Injectable({ providedIn: 'root' })
export class ThemeInitializer implements AppInitializer {
  name = 'theme';
  private readonly themeService = inject(ThemeService);

  async initialize(): Promise<void> {
    this.themeService.loadSavedTheme();
  }
}

// Register as multi providers
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: APP_INITIALIZERS, useExisting: AuthInitializer, multi: true },
    { provide: APP_INITIALIZERS, useExisting: ThemeInitializer, multi: true },
  ],
};

// Consumer receives array of all initializers
@Component({ /* ... */ })
export class AppRoot {
  private readonly initializers = inject(APP_INITIALIZERS, { optional: true }) ?? [];

  constructor() {
    afterNextRender(async () => {
      for (const init of this.initializers) {
        console.log(`Running initializer: ${init.name}`);
        await init.initialize();
      }
    });
  }
}
```

### Pattern 10: Environment-Based Configuration

```typescript
import { InjectionToken, inject, isDevMode } from '@angular/core';

export interface Environment {
  production: boolean;
  apiUrl: string;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  features: Record<string, boolean>;
}

export const ENVIRONMENT = new InjectionToken<Environment>('ENVIRONMENT');

// environment.ts
export const environment: Environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  logLevel: 'debug',
  features: {
    newDashboard: true,
    betaCheckout: true,
  },
};

// environment.prod.ts
export const environment: Environment = {
  production: true,
  apiUrl: 'https://api.example.com',
  logLevel: 'error',
  features: {
    newDashboard: true,
    betaCheckout: false,
  },
};

// Provide in app.config.ts
import { environment } from '../environments/environment';

export const appConfig: ApplicationConfig = {
  providers: [
    { provide: ENVIRONMENT, useValue: environment },
  ],
};

// Feature flag service
@Injectable({ providedIn: 'root' })
export class FeatureFlagService {
  private readonly env = inject(ENVIRONMENT);

  isEnabled(featureName: string): boolean {
    return this.env.features[featureName] ?? false;
  }
}

// Usage in component
@Component({
  selector: 'app-dashboard',
  template: `
    @if (featureFlags.isEnabled('newDashboard')) {
      <app-new-dashboard />
    } @else {
      <app-legacy-dashboard />
    }
  `,
})
export class Dashboard {
  protected readonly featureFlags = inject(FeatureFlagService);
}
```

### Pattern 11: Functional Guards and Resolvers with DI

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, CanDeactivateFn, CanMatchFn, ResolveFn, Router } from '@angular/router';
import { map } from 'rxjs';

// Functional auth guard
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
    const user = auth.user();
    return user !== null && allowedRoles.includes(user.role);
  };
}

// Unsaved changes guard
export interface HasUnsavedChanges {
  hasUnsavedChanges(): boolean;
}

export const unsavedChangesGuard: CanDeactivateFn<HasUnsavedChanges> = (component) => {
  if (component.hasUnsavedChanges()) {
    return confirm('You have unsaved changes. Leave anyway?');
  }
  return true;
};

// canMatch guard (prevents route from matching)
export const featureGuard: CanMatchFn = (route) => {
  const features = inject(FeatureFlagService);
  const featureName = route.data?.['feature'] as string;
  return featureName ? features.isEnabled(featureName) : true;
};

// Functional resolver
export const userResolver: ResolveFn<User> = (route) => {
  const http = inject(HttpClient);
  const id = route.paramMap.get('id')!;
  return http.get<User>(`/api/users/${id}`);
};

// Usage in routes
export const routes: Routes = [
  {
    path: 'admin',
    canActivate: [authGuard, roleGuard('admin')],
    loadComponent: () => import('./admin').then(m => m.Admin),
  },
  {
    path: 'profile/edit',
    canDeactivate: [unsavedChangesGuard],
    loadComponent: () => import('./profile-edit').then(m => m.ProfileEdit),
  },
  {
    path: 'beta-feature',
    canMatch: [featureGuard],
    data: { feature: 'betaCheckout' },
    loadComponent: () => import('./beta-checkout').then(m => m.BetaCheckout),
  },
  {
    path: 'users/:id',
    resolve: { user: userResolver },
    loadComponent: () => import('./user-detail').then(m => m.UserDetail),
  },
];
```

### Pattern 12: Testing DI Configurations

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

describe('ApiService', () => {
  let service: ApiService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        // Override tokens for testing
        { provide: API_BASE_URL, useValue: 'http://test-api.com' },
        { provide: LOGGER, useValue: { log: vi.fn(), error: vi.fn(), warn: vi.fn() } },
      ],
    });

    service = TestBed.inject(ApiService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify(); // Verify no outstanding requests
  });

  it('should use configured base URL', () => {
    service.get<User[]>('/users').subscribe();
    const req = httpTesting.expectOne('http://test-api.com/users');
    expect(req.request.method).toBe('GET');
    req.flush([]);
  });

  it('should log requests', () => {
    const logger = TestBed.inject(LOGGER);
    service.get<User[]>('/users').subscribe();
    httpTesting.expectOne('http://test-api.com/users').flush([]);
    expect(logger.log).toHaveBeenCalledWith(expect.stringContaining('GET'));
  });
});

// Testing interceptors
describe('authInterceptor', () => {
  let httpTesting: HttpTestingController;
  let authService: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });

    httpTesting = TestBed.inject(HttpTestingController);
    authService = TestBed.inject(AuthService);
  });

  it('should add auth header when token exists', () => {
    // Set token on the auth service
    authService['_token'].set('test-token');

    const http = TestBed.inject(HttpClient);
    http.get('/api/data').subscribe();

    const req = httpTesting.expectOne('/api/data');
    expect(req.request.headers.get('Authorization')).toBe('Bearer test-token');
    req.flush({});
  });

  it('should not add auth header when no token', () => {
    const http = TestBed.inject(HttpClient);
    http.get('/api/data').subscribe();

    const req = httpTesting.expectOne('/api/data');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });
});

// Testing with mock services
describe('UserList component', () => {
  const mockUserStore: DataStore<User> = {
    getAll: vi.fn().mockResolvedValue([
      { id: '1', name: 'Alice', email: 'alice@example.com', role: 'admin' },
    ]),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserList],
      providers: [
        { provide: USER_STORE, useValue: mockUserStore },
      ],
    });
  });

  it('should load users from store', async () => {
    const fixture = TestBed.createComponent(UserList);
    await fixture.whenStable();
    expect(mockUserStore.getAll).toHaveBeenCalled();
  });
});
```

## Testing Strategies

### Testing Injection Hierarchy

```typescript
describe('FormStateService hierarchy', () => {
  it('should provide separate instances at route level', () => {
    TestBed.configureTestingModule({
      providers: [FormStateService],
    });

    const instance1 = TestBed.inject(FormStateService);
    const instance2 = TestBed.inject(FormStateService);

    // Same injector returns same instance
    expect(instance1).toBe(instance2);
  });

  it('should provide separate instances per component', () => {
    @Component({
      selector: 'test-host',
      providers: [FormStateService],
      template: '',
    })
    class TestHost {
      formState = inject(FormStateService);
    }

    TestBed.configureTestingModule({ imports: [TestHost] });

    const fixture1 = TestBed.createComponent(TestHost);
    const fixture2 = TestBed.createComponent(TestHost);

    // Different component instances get different service instances
    expect(fixture1.componentInstance.formState)
      .not.toBe(fixture2.componentInstance.formState);
  });
});
```

## Common Pitfalls

### Pitfall 1: inject() Outside Injection Context

```typescript
// WRONG: inject() called outside constructor or field initializer
@Component({ /* ... */ })
export class Bad {
  service!: MyService;

  ngOnInit() {
    this.service = inject(MyService); // ERROR: inject() must be in injection context
  }
}

// CORRECT: inject() in field initializer or constructor
@Component({ /* ... */ })
export class Good {
  private readonly service = inject(MyService); // Field initializer
}
```

### Pitfall 2: Providing Root Services in Components

```typescript
// WRONG: creates new instance per component, losing singleton behavior
@Component({
  providers: [AuthService], // AuthService should be root singleton!
})
export class Bad {}

// CORRECT: AuthService has providedIn: 'root', do not re-provide
@Component({ /* ... */ })
export class Good {
  private readonly auth = inject(AuthService);
}
```

### Pitfall 3: Circular Dependencies

```typescript
// WRONG: ServiceA depends on ServiceB and vice versa
@Injectable({ providedIn: 'root' })
export class ServiceA {
  private readonly b = inject(ServiceB); // Circular!
}

@Injectable({ providedIn: 'root' })
export class ServiceB {
  private readonly a = inject(ServiceA); // Circular!
}

// CORRECT: break cycle with InjectionToken or mediator service
@Injectable({ providedIn: 'root' })
export class MediatorService {
  readonly sharedState = signal<string>('');
}
```

### Pitfall 4: Not Using Optional for Truly Optional Dependencies

```typescript
// WRONG: throws error if LoggerService is not provided
private readonly logger = inject(LoggerService);

// CORRECT: returns null if not provided
private readonly logger = inject(LoggerService, { optional: true });
```

## Best Practices

1. **Use `inject()` function** for all new code instead of constructor injection
2. **Use `providedIn: 'root'`** for singleton services (tree-shakable by default)
3. **Use route-level providers** for feature-scoped services to enable lazy loading
4. **Use `InjectionToken`** for non-class dependencies (config, constants, abstract interfaces)
5. **Use functional interceptors** instead of class-based interceptors
6. **Use functional guards and resolvers** instead of class-based alternatives
7. **Avoid component-level providers** unless you specifically need per-component instances
8. **Use `{ optional: true }`** for dependencies that may not be available
9. **Keep the injector hierarchy shallow** -- avoid deeply nested provider overrides
10. **Test DI configurations** by overriding providers in TestBed

## Resources

- **Angular DI Guide**: https://angular.dev/guide/di
- **Angular inject() API**: https://angular.dev/api/core/inject
- **Angular InjectionToken**: https://angular.dev/api/core/InjectionToken
- **Angular HTTP Interceptors**: https://angular.dev/guide/http/interceptors
- **Angular Providers**: https://angular.dev/guide/di/dependency-injection-providers
