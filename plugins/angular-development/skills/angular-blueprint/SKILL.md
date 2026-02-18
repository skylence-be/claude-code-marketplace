---
name: angular-blueprint
description: Master Angular Blueprint - the AI planning format for generating accurate, production-ready Angular 21+ code. Use when planning complex frontend implementations, creating detailed specifications, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
category: angular
tags: [angular, blueprint, ai, planning, architecture, specification, signals, zoneless, ssr]
related_skills: [angular-signals-patterns, angular-dependency-injection, angular-testing-patterns, angular-ssr-hydration, angular-routing-patterns, rxjs-angular-patterns, angular-performance-optimization]
---

# Angular Blueprint

Angular Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Angular 21+ projects. It bridges the gap between high-level requirements and production-ready code using modern Angular APIs: signals, zoneless change detection, standalone components, and hybrid rendering.

## When to Use This Skill

- Planning complex Angular 21+ application architectures
- Creating detailed specifications before writing code
- Generating comprehensive component, service, and route architectures
- Documenting data flows, rendering strategies, and state management
- Ensuring all details are captured (directory structure, types, DI, signals)
- Avoiding vague plans that lead to vague code
- Migrating existing Angular applications to modern patterns

## Core Concepts

### 1. Angular 21+ Defaults
- **Standalone components** are the default (no NgModules)
- **Zoneless change detection** is the default (no Zone.js)
- **Vitest** is the default test runner
- **2025 style guide** naming (no `.component.ts` suffixes required)
- **Signals** are the primary reactivity model
- **`inject()` function** replaces constructor injection

### 2. Blueprint Completeness
- Every route has a defined render mode (SSR/SSG/CSR)
- Every component has typed inputs/outputs
- Every service has a defined provider scope
- Every data fetch uses the correct API (httpResource/HttpClient/toSignal)
- Every state holder uses signals

### 3. Signal-First Architecture
- `signal()` for writable state
- `computed()` for derived state
- `linkedSignal()` for dependent-resettable state
- `httpResource()` for declarative HTTP data
- `toSignal()` / `toObservable()` for RxJS interop

## Quick Start

```markdown
# Project Blueprint: [Project Name]

## Key Decisions
- Angular 21 with zoneless change detection (default)
- Standalone components throughout
- Signal-based state management (no NgRx)
- Hybrid rendering: SSR for public pages, CSR for authenticated
- Vitest for unit testing, Playwright for E2E
- SCSS for styling with Angular Material or Tailwind CSS

## Architecture Tier
**Tier**: Feature-Based Modular
**Justification**: 5+ developer team, 20+ routes, clear feature boundaries
```

## Blueprint Plan Structure

A complete Angular Blueprint includes the following sections:

### 1. Overview and Key Decisions

```markdown
# E-Commerce Product Catalog

An Angular 21 application for browsing, searching, and purchasing products.

## Key Decisions
- Angular 21 with zoneless change detection (default)
- Standalone components; no NgModules
- Hybrid rendering: SSR for product pages (SEO), CSR for checkout/admin
- Signal-based state management via services with signal stores
- TypeScript strict mode throughout
- httpResource for GET queries, HttpClient for mutations
- Vitest for unit tests, Playwright for E2E
- Tailwind CSS for styling
- 2025 style guide (no type suffixes in file names)
```

### 2. Architecture Tier

Select the architecture based on project scope:

```markdown
## Architecture

**Tier**: Feature-Based Modular
**Justification**: 5+ developer team, 20+ routes, clear feature boundaries

### Directory Structure (Angular 21 / 2025 Style Guide)

my-app/
├── angular.json
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.spec.json
├── public/
│   └── favicon.ico
├── src/
│   ├── index.html
│   ├── main.ts
│   ├── styles.scss
│   └── app/
│       ├── app.ts                     # Root component
│       ├── app.config.ts              # Application providers
│       ├── app.routes.ts              # Root route definitions
│       ├── server.routes.ts           # SSR route-level render modes
│       ├── core/
│       │   ├── auth/
│       │   │   ├── auth.service.ts
│       │   │   ├── auth.guard.ts
│       │   │   └── auth.interceptor.ts
│       │   ├── api/
│       │   │   └── api.service.ts
│       │   └── error/
│       │       └── error-handler.ts
│       ├── shared/
│       │   ├── components/
│       │   │   ├── button/
│       │   │   │   └── button.ts
│       │   │   ├── modal/
│       │   │   │   └── modal.ts
│       │   │   └── spinner/
│       │   │       └── spinner.ts
│       │   ├── directives/
│       │   │   └── highlight.ts
│       │   ├── pipes/
│       │   │   └── currency-format.ts
│       │   └── models/
│       │       ├── product.model.ts
│       │       ├── cart.model.ts
│       │       └── user.model.ts
│       └── features/
│           ├── products/
│           │   ├── product-list.ts
│           │   ├── product-detail.ts
│           │   ├── product-card.ts
│           │   ├── product-filters.ts
│           │   ├── products.routes.ts
│           │   └── services/
│           │       └── product.service.ts
│           ├── cart/
│           │   ├── cart-page.ts
│           │   ├── cart-item.ts
│           │   ├── cart-summary.ts
│           │   ├── cart.routes.ts
│           │   └── services/
│           │       └── cart.service.ts
│           ├── checkout/
│           │   ├── checkout.ts
│           │   ├── checkout.routes.ts
│           │   └── services/
│           │       └── checkout.service.ts
│           └── admin/
│               ├── admin-dashboard.ts
│               ├── admin.routes.ts
│               └── services/
│                   └── admin.service.ts
└── server.ts                          # SSR entry point (if using @angular/ssr)
```

### 3. Rendering Strategy

Define per-route rendering modes using `@angular/ssr` `ServerRoute`:

```markdown
## Rendering Strategy

### Route Render Modes
| Route Pattern | Mode | Justification |
|---------------|------|---------------|
| `/` | Prerender (SSG) | Static landing page, maximum performance |
| `/products` | Server | SEO required, dynamic product data |
| `/products/:slug` | Prerender | SEO required, enumerable via getPrerenderParams |
| `/cart` | Client | Authenticated, no SEO needed |
| `/checkout` | Client | Authenticated, no SEO needed |
| `/admin/**` | Client | Internal tool, no SEO needed |

### Server Route Configuration

```typescript
// server.routes.ts
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'products', renderMode: RenderMode.Server },
  {
    path: 'products/:slug',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      const res = await fetch('https://api.example.com/products/slugs');
      const slugs: string[] = await res.json();
      return slugs.map(slug => ({ slug }));
    }
  },
  { path: 'cart', renderMode: RenderMode.Client },
  { path: 'checkout', renderMode: RenderMode.Client },
  { path: 'admin/**', renderMode: RenderMode.Client },
  { path: '**', renderMode: RenderMode.Server },
];
```

### 4. TypeScript Interfaces

Define all shared interfaces and types:

```markdown
## Types

### Product
**File**: shared/models/product.model.ts

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Primary key |
| name | string | yes | Display name |
| slug | string | yes | URL-safe identifier |
| description | string | yes | Full description |
| price | number | yes | Price in cents |
| compareAtPrice | number | no | Original price for sale display |
| images | ProductImage[] | yes | At least one image |
| category | Category | yes | Product category |
| inStock | boolean | yes | Availability flag |
| variants | ProductVariant[] | no | Size/color variants |

### CartItem
**File**: shared/models/cart.model.ts

| Field | Type | Required |
|-------|------|----------|
| productId | string | yes |
| variantId | string | no |
| quantity | number | yes |
| price | number | yes |
```

```typescript
// shared/models/product.model.ts
export interface Product {
  id: string;
  name: string;
  slug: string;
  description: string;
  price: number;
  compareAtPrice?: number;
  images: ProductImage[];
  category: Category;
  inStock: boolean;
  variants?: ProductVariant[];
}

export interface ProductImage {
  id: string;
  url: string;
  alt: string;
  width: number;
  height: number;
}

export interface ProductVariant {
  id: string;
  name: string;
  sku: string;
  price: number;
  inStock: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
}
```

```typescript
// shared/models/cart.model.ts
export interface CartItem {
  productId: string;
  variantId?: string;
  quantity: number;
  price: number;
}

export interface Cart {
  items: CartItem[];
  total: number;
  itemCount: number;
}
```

```typescript
// shared/models/user.model.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  avatarUrl?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}
```

### 5. Signal Store Services

Specify services with full signal-based state management:

```markdown
## Signal Store Services

### CartService
**File**: features/cart/services/cart.service.ts
**Pattern**: Signal Store (private writable, public readonly)
**Scope**: providedIn: 'root'

**State (Signals)**:
| Signal | Type | Default |
|--------|------|---------|
| _items | WritableSignal<CartItem[]> | [] |
| _loading | WritableSignal<boolean> | false |

**Derived (Computed)**:
| Computed | Return Type | Logic |
|----------|-------------|-------|
| items | Signal<CartItem[]> | _items.asReadonly() |
| totalItems | Signal<number> | Sum of all item quantities |
| subtotal | Signal<number> | Sum of (item.price * item.quantity) |
| isEmpty | Signal<boolean> | items().length === 0 |

**Actions (Methods)**:
| Action | Parameters | Description |
|--------|-----------|-------------|
| addItem | product: Product, quantity: number | Add or increment item |
| removeItem | productId: string | Remove item from cart |
| updateQuantity | productId: string, quantity: number | Set item quantity |
| clearCart | none | Empty the cart |
```

```typescript
// features/cart/services/cart.service.ts
import { Injectable, signal, computed } from '@angular/core';
import { CartItem } from '../../../shared/models/cart.model';
import { Product } from '../../../shared/models/product.model';

@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly _items = signal<CartItem[]>([]);
  private readonly _loading = signal(false);

  readonly items = this._items.asReadonly();
  readonly loading = this._loading.asReadonly();

  readonly totalItems = computed(() =>
    this._items().reduce((sum, item) => sum + item.quantity, 0)
  );

  readonly subtotal = computed(() =>
    this._items().reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  readonly isEmpty = computed(() => this._items().length === 0);

  addItem(product: Product, quantity = 1): void {
    this._items.update(items => {
      const existing = items.find(item => item.productId === product.id);
      if (existing) {
        return items.map(item =>
          item.productId === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }
      return [...items, { productId: product.id, quantity, price: product.price }];
    });
  }

  removeItem(productId: string): void {
    this._items.update(items => items.filter(item => item.productId !== productId));
  }

  updateQuantity(productId: string, quantity: number): void {
    if (quantity <= 0) {
      this.removeItem(productId);
      return;
    }
    this._items.update(items =>
      items.map(item =>
        item.productId === productId ? { ...item, quantity } : item
      )
    );
  }

  clearCart(): void {
    this._items.set([]);
  }
}
```

### 6. Component Specification

Include inputs, outputs, template structure, and change detection:

```markdown
## Components

### ProductCard
**File**: features/products/product-card.ts
**Purpose**: Display a single product in a grid
**Change Detection**: OnPush (default with zoneless)

**Inputs (signal-based)**:
| Input | Type | Required | Default |
|-------|------|----------|---------|
| product | Product | yes | - |
| showComparePrice | boolean | no | true |

**Outputs (signal-based)**:
| Output | Payload | Description |
|--------|---------|-------------|
| addToCart | Product | User clicked add to cart |

**Template Structure**:
- Product image with NgOptimizedImage
- Product name as link to detail page
- Price display with optional compare-at price
- Add to cart button (disabled when out of stock)
```

```typescript
// features/products/product-card.ts
import { Component, input, output, computed, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgOptimizedImage, CurrencyPipe } from '@angular/common';
import { Product } from '../../shared/models/product.model';

@Component({
  selector: 'app-product-card',
  imports: [RouterLink, NgOptimizedImage, CurrencyPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="group relative rounded-lg border bg-white p-4 transition hover:shadow-md">
      @if (isOnSale()) {
        <span class="absolute right-2 top-2 rounded bg-red-500 px-2 py-1 text-xs text-white">
          Sale
        </span>
      }

      <a [routerLink]="['/products', product().slug]">
        <img
          [ngSrc]="product().images[0]?.url"
          [alt]="product().images[0]?.alt ?? product().name"
          width="400"
          height="400"
          class="aspect-square w-full rounded object-cover"
          loading="lazy"
        />
      </a>

      <div class="mt-3">
        <a [routerLink]="['/products', product().slug]" class="font-medium hover:underline">
          {{ product().name }}
        </a>

        <div class="mt-1 flex items-center gap-2">
          <span class="text-lg font-bold">{{ product().price / 100 | currency }}</span>
          @if (showComparePrice() && product().compareAtPrice) {
            <span class="text-sm text-gray-400 line-through">
              {{ product().compareAtPrice! / 100 | currency }}
            </span>
          }
        </div>

        <button
          [disabled]="!product().inStock"
          class="mt-3 w-full rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-300"
          (click)="addToCart.emit(product())"
        >
          {{ product().inStock ? 'Add to Cart' : 'Out of Stock' }}
        </button>
      </div>
    </div>
  `,
})
export class ProductCard {
  readonly product = input.required<Product>();
  readonly showComparePrice = input(true);
  readonly addToCart = output<Product>();

  protected readonly isOnSale = computed(() => {
    const p = this.product();
    return p.compareAtPrice != null && p.compareAtPrice > p.price;
  });
}
```

### 7. Route Configuration

Define lazy-loaded routes with guards and resolvers:

```markdown
## Routes

### Root Routes (app.routes.ts)
| Path | Load | Guard | Description |
|------|------|-------|-------------|
| `` | redirect to /products | - | Default redirect |
| `products` | loadChildren -> products.routes | - | Product feature |
| `cart` | loadComponent -> cart-page | - | Cart page |
| `checkout` | loadComponent -> checkout | authGuard | Checkout page |
| `admin/**` | loadChildren -> admin.routes | adminGuard | Admin feature |
| `**` | redirect to /products | - | Wildcard |
```

```typescript
// app.routes.ts
import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';
import { adminGuard } from './core/auth/admin.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'products', pathMatch: 'full' },
  {
    path: 'products',
    loadChildren: () =>
      import('./features/products/products.routes').then(m => m.PRODUCTS_ROUTES),
  },
  {
    path: 'cart',
    loadComponent: () =>
      import('./features/cart/cart-page').then(m => m.CartPage),
  },
  {
    path: 'checkout',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/checkout/checkout').then(m => m.Checkout),
  },
  {
    path: 'admin',
    canActivate: [adminGuard],
    loadChildren: () =>
      import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES),
  },
  { path: '**', redirectTo: 'products' },
];
```

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
    path: ':slug',
    loadComponent: () =>
      import('./product-detail').then(m => m.ProductDetail),
  },
];
```

### 8. Application Configuration

```markdown
## Configuration

### app.config.ts
**Providers**: provideRouter, provideHttpClient, provideClientHydration, provideAnimationsAsync
**Features**: withComponentInputBinding, withPreloading, withEventReplay, withHttpTransferCacheOptions
```

```typescript
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withComponentInputBinding, withPreloading, PreloadAllModules } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideClientHydration, withEventReplay, withHttpTransferCacheOptions } from '@angular/platform-browser';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { routes } from './app.routes';
import { authInterceptor } from './core/auth/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),
      withPreloading(PreloadAllModules),
    ),
    provideHttpClient(
      withInterceptors([authInterceptor]),
    ),
    provideClientHydration(
      withEventReplay(),
      withHttpTransferCacheOptions({
        includePostRequests: false,
      }),
    ),
    provideAnimationsAsync(),
  ],
};
```

```typescript
// angular.json (key sections)
{
  "projects": {
    "my-app": {
      "architect": {
        "build": {
          "builder": "@angular/build:application",
          "options": {
            "outputPath": "dist/my-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "server": "src/main.server.ts",
            "tsConfig": "tsconfig.app.json",
            "assets": [{ "glob": "**/*", "input": "public" }],
            "styles": ["src/styles.scss"],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                { "type": "initial", "maximumWarning": "500kB", "maximumError": "1MB" },
                { "type": "anyComponentStyle", "maximumWarning": "4kB", "maximumError": "8kB" }
              ],
              "outputHashing": "all"
            },
            "development": {
              "optimization": false,
              "extractLicenses": false,
              "sourceMap": true
            }
          },
          "defaultConfiguration": "production"
        },
        "test": {
          "builder": "@angular/build:unit-test"
        }
      }
    }
  }
}
```

### 9. Data Fetching Strategy

```markdown
## Data Fetching

### The Three Fetching Tools
| Tool | Use For | Reactive | Cancellation | Mutations |
|------|---------|----------|-------------|-----------|
| `httpResource` | Declarative GET queries bound to signals | Yes (signal-based) | Automatic on param change | No (GET only) |
| `HttpClient` | Mutations (POST/PUT/DELETE), complex requests | Via RxJS | Manual (takeUntilDestroyed) | Yes |
| `toSignal(observable)` | Convert existing RxJS streams to signals | Yes | Via takeUntilDestroyed | N/A |

### Data Fetching Per Page
| Page | Fetching Approach | Caching |
|------|------------------|---------|
| Product List | httpResource with search/filter params | HTTP transfer cache (SSR) |
| Product Detail | httpResource with slug param | HTTP transfer cache (SSR) |
| Cart | CartService signals (client-side state) | localStorage persistence |
| Checkout | HttpClient POST for order creation | None |
| Admin | httpResource for data, HttpClient for mutations | None |
```

```typescript
// features/products/product-list.ts
import { Component, signal, computed, inject, ChangeDetectionStrategy } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Product } from '../../shared/models/product.model';
import { ProductCard } from './product-card';
import { ProductFilters } from './product-filters';

@Component({
  selector: 'app-product-list',
  imports: [FormsModule, ProductCard, ProductFilters],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6">Products</h1>

      <app-product-filters
        [categories]="categories()"
        (searchChange)="searchQuery.set($event)"
        (categoryChange)="selectedCategory.set($event)"
      />

      @if (productsResource.isLoading()) {
        <div class="grid grid-cols-3 gap-6">
          @for (i of skeletonItems; track i) {
            <div class="h-64 animate-pulse rounded-lg bg-gray-200"></div>
          }
        </div>
      } @else if (productsResource.error()) {
        <p class="text-red-600">Failed to load products. Please try again.</p>
      } @else if (productsResource.hasValue()) {
        @if (productsResource.value()!.length === 0) {
          <p class="text-gray-500">No products found.</p>
        } @else {
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            @for (product of productsResource.value()!; track product.id) {
              <app-product-card
                [product]="product"
                (addToCart)="onAddToCart($event)"
              />
            }
          </div>
        }
      }
    </div>
  `,
})
export class ProductList {
  private readonly cartService = inject(CartService);

  readonly searchQuery = signal('');
  readonly selectedCategory = signal<string | null>(null);
  readonly skeletonItems = Array.from({ length: 6 }, (_, i) => i);

  readonly productsResource = httpResource<Product[]>(() => {
    const params: Record<string, string> = {};
    const q = this.searchQuery();
    const cat = this.selectedCategory();
    if (q) params['q'] = q;
    if (cat) params['category'] = cat;
    return { url: '/api/products', params };
  });

  readonly categories = signal<string[]>([
    'Electronics', 'Clothing', 'Home', 'Sports',
  ]);

  onAddToCart(product: Product): void {
    this.cartService.addItem(product);
  }
}
```

### 10. Dependency Injection Plan

```markdown
## Dependency Injection

### Services
| Service | Scope | Purpose |
|---------|-------|---------|
| AuthService | providedIn: 'root' | Authentication state and operations |
| CartService | providedIn: 'root' | Shopping cart state management |
| ProductService | providedIn: 'root' | Product data fetching utilities |
| CheckoutService | providedIn: 'root' | Order processing |
| AdminService | route-level provider | Admin-specific operations |

### Injection Tokens
| Token | Type | Default | Purpose |
|-------|------|---------|---------|
| API_BASE_URL | string | '/api' | Base URL for API requests |
| APP_CONFIG | AppConfig | production defaults | Application configuration |

### Interceptors
| Interceptor | Purpose |
|------------|---------|
| authInterceptor | Attach Bearer token to requests |
| errorInterceptor | Global HTTP error handling |
```

```typescript
// core/auth/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.token();

  if (token) {
    const cloned = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
    return next(cloned);
  }

  return next(req);
};
```

```typescript
// core/auth/auth.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

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

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  return authService.isAdmin();
};
```

### 11. Testing Strategy

```markdown
## Testing

### Test Distribution
| Layer | Coverage | Tool | Focus |
|-------|----------|------|-------|
| Unit | ~50% | Vitest + TestBed | Services, signals, computed, pipes |
| Component | ~30% | Vitest + TestBed | Component rendering, inputs/outputs, interactions |
| E2E | ~20% | Playwright | Critical user journeys |

### Test Files
- features/cart/services/cart.service.spec.ts
- features/products/product-card.spec.ts
- features/products/product-list.spec.ts
- core/auth/auth.service.spec.ts
- core/auth/auth.guard.spec.ts
- shared/pipes/currency-format.spec.ts
- e2e/checkout.spec.ts
- e2e/product-browse.spec.ts
```

```typescript
// features/cart/services/cart.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { CartService } from './cart.service';
import { Product } from '../../../shared/models/product.model';

describe('CartService', () => {
  let service: CartService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CartService);
  });

  it('should start with empty cart', () => {
    expect(service.items()).toEqual([]);
    expect(service.isEmpty()).toBe(true);
    expect(service.totalItems()).toBe(0);
  });

  it('should add item to cart', () => {
    const product = { id: '1', name: 'Shirt', price: 2999 } as Product;
    service.addItem(product, 2);

    expect(service.items()).toHaveLength(1);
    expect(service.items()[0].quantity).toBe(2);
    expect(service.totalItems()).toBe(2);
    expect(service.subtotal()).toBe(5998);
  });

  it('should increment quantity for existing item', () => {
    const product = { id: '1', name: 'Shirt', price: 2999 } as Product;
    service.addItem(product, 1);
    service.addItem(product, 2);

    expect(service.items()).toHaveLength(1);
    expect(service.items()[0].quantity).toBe(3);
  });
});
```

### 12. Verification Checklist

```markdown
## Verification

### Manual Testing
1. [ ] Landing page renders via SSG at /products
2. [ ] Product listing loads with SSR and search filters work
3. [ ] Product detail page prerenders at /products/:slug
4. [ ] Add to cart updates cart state reactively
5. [ ] Cart persists across page navigations
6. [ ] Checkout redirects to /login if unauthenticated
7. [ ] Admin panel renders as CSR at /admin
8. [ ] Images serve via NgOptimizedImage with lazy loading
9. [ ] Hydration completes without DOM mismatch errors
10. [ ] Lighthouse Performance score > 90

### Automated
ng test
npx playwright test
npx tsc --noEmit
ng build --configuration production
```

## Architecture Tier Decision Framework

| Criterion | Flat | Feature-Based | Domain-Driven |
|-----------|------|---------------|---------------|
| Team size | 1-2 | 3-10 | 10+ |
| Routes | <10 | 10-50 | 50+ |
| Component count | <20 | 20-100 | 100+ |
| Feature boundaries | Blurred | Clear | Strict |
| Onboarding complexity | Trivial | Medium | High |
| Refactor cost (later) | High | Low | Low |

### When to Choose Each

**Flat**: Prototype, hackathon, landing page. Everything directly in `app/`.

**Feature-Based**: Group by feature domain: `features/products/`, `features/cart/`. Best default for most Angular apps.

**Domain-Driven**: Strict layered architecture with core/shared/features separation, library boundaries enforced via Nx or workspace projects. For complex enterprise apps.

## Rendering Strategy Decision Matrix

| Need SEO? | Data changes frequently? | Authenticated? | Use |
|-----------|------------------------|----------------|-----|
| Yes | No | No | **Prerender** (SSG) |
| Yes | Yes | No | **Server** (SSR) |
| No | Any | Yes | **Client** (CSR) |
| Yes | Enumerable | No | **Prerender** with `getPrerenderParams` |

### Configuration Reference

```typescript
// server.routes.ts
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // SSG - prerendered at build time
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'about', renderMode: RenderMode.Prerender },

  // SSR - server-rendered per request
  { path: 'products', renderMode: RenderMode.Server },

  // SSG with dynamic params
  {
    path: 'blog/:slug',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      return [{ slug: 'post-1' }, { slug: 'post-2' }];
    },
  },

  // CSR - client-side only
  { path: 'dashboard/**', renderMode: RenderMode.Client },
];
```

**CRITICAL**: Never use Client render mode for public content that needs SEO. Search engines index SSR/SSG content reliably; CSR content requires JavaScript execution.

## Signal Store Pattern Reference

### Service with Signal Store

```typescript
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly _user = signal<User | null>(null);
  private readonly _token = signal<string | null>(null);
  private readonly _loading = signal(false);
  private readonly http = inject(HttpClient);

  readonly user = this._user.asReadonly();
  readonly token = this._token.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly isAuthenticated = computed(() => this._user() !== null && this._token() !== null);
  readonly isAdmin = computed(() => this._user()?.role === 'admin');

  async login(email: string, password: string): Promise<boolean> {
    this._loading.set(true);
    try {
      const response = await firstValueFrom(
        this.http.post<{ user: User; token: string }>('/api/auth/login', { email, password })
      );
      this._user.set(response.user);
      this._token.set(response.token);
      return true;
    } catch {
      return false;
    } finally {
      this._loading.set(false);
    }
  }

  logout(): void {
    this._user.set(null);
    this._token.set(null);
  }
}
```

## Data Fetching Decision Tree

| Question | YES | NO |
|----------|-----|-----|
| Is it a GET query bound to component state? | **httpResource** | Next question |
| Is it a mutation (POST/PUT/DELETE)? | **HttpClient** | Next question |
| Is it an existing RxJS observable? | **toSignal()** | Next question |
| Do you need complex RxJS operators? | **rxResource** or **toSignal(pipe(...))** | Use **httpResource** |

## Component Design Decision Tree

| Question | YES | NO |
|----------|-----|-----|
| Does it render UI? | **Component** | Next question |
| Does it manage global shared state? | **Service with signals** | Next question |
| Is it reusable reactive logic? | **Service or utility function** | Next question |
| Is it a pure transformation? | **Pipe** | Reconsider design |

## Common Planning Mistakes Checklist

| Mistake | Impact | Fix |
|---------|--------|-----|
| No rendering strategy per route | All routes default to SSR or CSR | Define `ServerRoute[]` per route |
| Using NgModules in new code | Unnecessary complexity | Use standalone components |
| Constructor injection | Verbose, inheritance issues | Use `inject()` function |
| `*ngIf` / `*ngFor` in templates | Legacy syntax, needs CommonModule | Use `@if` / `@for` control flow |
| Methods in templates | Re-executed every change detection cycle | Use `computed()` signals |
| Missing `track` in `@for` | Poor rendering performance | Always provide `track` expression |
| Bare subscriptions | Memory leaks | Use `takeUntilDestroyed()` or `toSignal()` |
| Zone.js in Angular 21 | Unnecessary bundle size | Remove Zone.js (default is zoneless) |
| `httpResource` for mutations | httpResource is GET-only | Use `HttpClient` for POST/PUT/DELETE |
| No typed inputs/outputs | Runtime errors, no IDE support | Use `input()` and `output()` signal APIs |

## Best Practices

1. **Be explicit** -- Include file paths, TypeScript interfaces, exact component configurations
2. **Define rendering per route** -- Never leave rendering mode as implicit default
3. **Show complete code** -- Full component class with imports, inputs, outputs, template
4. **Specify data fetching** -- Which tool (httpResource vs HttpClient vs toSignal) and why
5. **Document component contracts** -- Signal inputs with types and defaults, outputs with payloads
6. **Map state ownership** -- Which data lives in root services vs feature services vs component signals
7. **Include TypeScript interfaces** -- Every API response, every input type, every state shape
8. **Use signal-first approach** -- Prefer signals over observables for new state management
9. **Plan DI hierarchy** -- Which services are root-level, which are route-scoped
10. **Test with zoneless** -- Use `await fixture.whenStable()` instead of `fixture.detectChanges()`
11. **Specify guards and interceptors** -- Auth guards per route, interceptors for cross-cutting concerns
12. **Plan in order** -- Types -> Config -> Services -> Components -> Routes -> Tests
13. **Include file inventory** -- Categorized list of all files to create

## File Inventory Template

Every Blueprint should end with a categorized file list:

```markdown
## Files

### Models (3)
- shared/models/product.model.ts
- shared/models/cart.model.ts
- shared/models/user.model.ts

### Configuration (4)
- app.config.ts
- app.routes.ts
- server.routes.ts
- angular.json

### Core Services (3)
- core/auth/auth.service.ts
- core/auth/auth.guard.ts
- core/auth/auth.interceptor.ts

### Feature Services (3)
- features/products/services/product.service.ts
- features/cart/services/cart.service.ts
- features/checkout/services/checkout.service.ts

### Components (10)
- app.ts
- shared/components/button/button.ts
- shared/components/modal/modal.ts
- shared/components/spinner/spinner.ts
- features/products/product-list.ts
- features/products/product-detail.ts
- features/products/product-card.ts
- features/products/product-filters.ts
- features/cart/cart-page.ts
- features/cart/cart-item.ts

### Feature Routes (3)
- features/products/products.routes.ts
- features/cart/cart.routes.ts
- features/admin/admin.routes.ts

### Pipes (1)
- shared/pipes/currency-format.ts

### Tests (8)
- features/cart/services/cart.service.spec.ts
- features/products/product-card.spec.ts
- features/products/product-list.spec.ts
- core/auth/auth.service.spec.ts
- core/auth/auth.guard.spec.ts
- shared/pipes/currency-format.spec.ts
- e2e/checkout.spec.ts
- e2e/product-browse.spec.ts
```

## Resources

- **Angular Documentation**: https://angular.dev
- **Angular Signals Guide**: https://angular.dev/guide/signals
- **Angular SSR Guide**: https://angular.dev/guide/ssr
- **Angular Style Guide (2025)**: https://angular.dev/style-guide
- **Angular Routing**: https://angular.dev/guide/routing
- **Angular Testing**: https://angular.dev/guide/testing
