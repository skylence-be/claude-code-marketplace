---
description: Generate an Angular injectable service with signal-based state and inject() function
model: claude-sonnet-4-5
---

Create a new Angular injectable service following modern Angular 21+ best practices.

## Service Specification

$ARGUMENTS

## Angular 21+ Service Standards

### 1. **Basic Service with `providedIn: 'root'`**

```typescript
import { Injectable, inject, signal, computed } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly http = inject(HttpClient);

  private readonly _currentUser = signal<User | null>(null);
  readonly currentUser = this._currentUser.asReadonly();
  readonly isAuthenticated = computed(() => this._currentUser() !== null);

  async loadUser(): Promise<void> {
    const user = await firstValueFrom(this.http.get<User>('/api/me'));
    this._currentUser.set(user);
  }

  logout(): void {
    this._currentUser.set(null);
  }
}
```

### 2. **Signal-Based State Management**

```typescript
@Injectable({ providedIn: 'root' })
export class CartService {
  // Private writable signals
  private readonly _items = signal<CartItem[]>([]);
  private readonly _coupon = signal<string | null>(null);

  // Public read-only signals
  readonly items = this._items.asReadonly();
  readonly coupon = this._coupon.asReadonly();

  // Computed derived state
  readonly itemCount = computed(() =>
    this._items().reduce((sum, item) => sum + item.quantity, 0)
  );
  readonly subtotal = computed(() =>
    this._items().reduce((sum, item) => sum + item.price * item.quantity, 0)
  );
  readonly discount = computed(() => this._coupon() ? this.subtotal() * 0.1 : 0);
  readonly total = computed(() => this.subtotal() - this.discount());

  // Mutations through methods only
  addItem(item: CartItem): void {
    this._items.update(items => {
      const existing = items.find(i => i.id === item.id);
      if (existing) {
        return items.map(i =>
          i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      return [...items, { ...item, quantity: 1 }];
    });
  }

  removeItem(id: string): void {
    this._items.update(items => items.filter(i => i.id !== id));
  }

  applyCoupon(code: string): void {
    this._coupon.set(code);
  }

  clear(): void {
    this._items.set([]);
    this._coupon.set(null);
  }
}
```

### 3. **HTTP Data Service**

```typescript
@Injectable({ providedIn: 'root' })
export class ProductService {
  private readonly http = inject(HttpClient);

  getAll(): Observable<Product[]> {
    return this.http.get<Product[]>('/api/products');
  }

  getById(id: string): Observable<Product> {
    return this.http.get<Product>(`/api/products/${id}`);
  }

  create(product: CreateProductDto): Observable<Product> {
    return this.http.post<Product>('/api/products', product);
  }

  update(id: string, product: UpdateProductDto): Observable<Product> {
    return this.http.put<Product>(`/api/products/${id}`, product);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`/api/products/${id}`);
  }
}
```

### 4. **Service with `httpResource` (Experimental)**

```typescript
@Injectable({ providedIn: 'root' })
export class UserProfileService {
  private readonly userId = signal<string | null>(null);

  readonly profile = httpResource<UserProfile>(() =>
    this.userId() ? `/api/users/${this.userId()}` : undefined
  );

  loadProfile(id: string): void {
    this.userId.set(id);
  }
}
```

### 5. **Service with Effects**

```typescript
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly _theme = signal<'light' | 'dark'>('light');
  readonly theme = this._theme.asReadonly();
  readonly isDark = computed(() => this._theme() === 'dark');

  constructor() {
    // Load persisted theme on creation
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (saved) {
      this._theme.set(saved);
    }

    // Persist theme changes
    effect(() => {
      localStorage.setItem('theme', this._theme());
      document.documentElement.setAttribute('data-theme', this._theme());
    });
  }

  toggle(): void {
    this._theme.update(t => (t === 'light' ? 'dark' : 'light'));
  }

  setTheme(theme: 'light' | 'dark'): void {
    this._theme.set(theme);
  }
}
```

### 6. **Service with `linkedSignal`**

```typescript
@Injectable({ providedIn: 'root' })
export class PaginationService {
  private readonly _items = signal<Item[]>([]);
  private readonly _pageSize = signal(10);

  // Resets to 0 whenever items or pageSize changes
  readonly currentPage = linkedSignal(() => {
    this._items();
    this._pageSize();
    return 0;
  });

  readonly totalPages = computed(() =>
    Math.ceil(this._items().length / this._pageSize())
  );
  readonly paginatedItems = computed(() => {
    const start = this.currentPage() * this._pageSize();
    return this._items().slice(start, start + this._pageSize());
  });

  setItems(items: Item[]): void {
    this._items.set(items);
  }

  setPageSize(size: number): void {
    this._pageSize.set(size);
  }

  goToPage(page: number): void {
    if (page >= 0 && page < this.totalPages()) {
      this.currentPage.set(page);
    }
  }
}
```

### 7. **Service with RxJS Interop**

```typescript
import { toSignal, toObservable } from '@angular/core/rxjs-interop';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);
  private readonly _query = signal('');

  readonly query = this._query.asReadonly();

  // Convert signal to observable for RxJS operators
  readonly results = toSignal(
    toObservable(this._query).pipe(
      debounceTime(300),
      distinctUntilChanged(),
      filter(q => q.length >= 2),
      switchMap(q => this.http.get<SearchResult[]>(`/api/search?q=${q}`)),
      catchError(() => of([] as SearchResult[]))
    ),
    { initialValue: [] as SearchResult[] }
  );

  search(query: string): void {
    this._query.set(query);
  }
}
```

### 8. **Injection Tokens for Configuration**

```typescript
import { InjectionToken, inject } from '@angular/core';

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
}

export const API_CONFIG = new InjectionToken<ApiConfig>('API_CONFIG', {
  providedIn: 'root',
  factory: () => ({
    baseUrl: '/api',
    timeout: 30000,
    retryAttempts: 3,
  }),
});

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly config = inject(API_CONFIG);

  get<T>(path: string): Observable<T> {
    return this.http.get<T>(`${this.config.baseUrl}${path}`).pipe(
      timeout(this.config.timeout),
      retry(this.config.retryAttempts)
    );
  }
}
```

### 9. **Feature-Scoped Service**

```typescript
// Provide in route configuration for feature-level scope
@Injectable()
export class FeatureStateService {
  private readonly _data = signal<FeatureData | null>(null);
  readonly data = this._data.asReadonly();

  initialize(data: FeatureData): void {
    this._data.set(data);
  }

  reset(): void {
    this._data.set(null);
  }
}

// In feature routes:
export const FEATURE_ROUTES: Routes = [
  {
    path: '',
    providers: [FeatureStateService],
    children: [
      { path: '', loadComponent: () => import('./feature-list').then(m => m.FeatureList) },
    ],
  },
];
```

## Best Practices

**Service Design**
- ✓ Single Responsibility -- one service per domain concern
- ✓ Use `providedIn: 'root'` for singleton services (tree-shakable)
- ✓ Use route-level `providers` for feature-scoped services
- ✓ Use `inject()` function instead of constructor injection
- ✓ Private writable signals, public readonly signals

**TypeScript**
- ✓ Strict typing for all parameters and return values
- ✓ No `any` types
- ✓ Use generics for reusable services
- ✓ Define interfaces/types for all data shapes

**State Management**
- ✓ `signal()` for mutable state (private)
- ✓ `asReadonly()` for public exposure
- ✓ `computed()` for derived values
- ✓ `effect()` sparingly for side effects (persistence, logging)
- ✓ `linkedSignal()` for dependent-reset state
- ✓ Immutable updates with `update()` and spread operators

**Error Handling**
- ✓ Try/catch for async operations
- ✓ Return error state in signals
- ✓ Use RxJS `catchError` for observable pipelines
- ✓ Provide meaningful error types

Generate production-ready, type-safe Angular services with signal-based reactive state management.
