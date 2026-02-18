---
name: angular-testing-patterns
description: Master Angular testing with Vitest (Angular 21 default), TestBed configuration, component testing with signal inputs/outputs, signal testing, httpResource testing, zoneless testing patterns, service testing, and E2E with Playwright.
category: angular
tags: [angular, testing, vitest, testbed, playwright, signals, zoneless, httpResource]
related_skills: [angular-signals-patterns, angular-dependency-injection, angular-blueprint, angular-performance-optimization]
---

# Angular Testing Patterns

Comprehensive guide to testing Angular 21+ applications with Vitest (the default test runner), covering TestBed configuration for standalone components, signal-based component testing, httpResource testing, zoneless change detection testing, service and pipe testing, and E2E testing with Playwright.

## When to Use This Skill

- Writing unit tests for Angular components with Vitest
- Testing signal-based inputs, outputs, and computed values
- Testing httpResource and data fetching patterns
- Configuring TestBed for standalone component testing
- Testing services with signal stores and HttpClient
- Testing functional guards, resolvers, and interceptors
- Writing E2E tests with Playwright
- Setting up CI/CD test pipelines for Angular projects
- Testing zoneless change detection behavior

## Core Concepts

### 1. Vitest as Default (Angular 21+)
- Replaces Karma/Jasmine for new Angular 21 projects
- Compatible with existing `describe`/`it`/`expect` syntax
- Faster test execution with Vite-based tooling
- Migration from Jasmine: `ng generate refactor-jasmine-vitest`

### 2. TestBed for Component Testing
- `configureTestingModule()` with standalone component `imports`
- `fixture.whenStable()` for zoneless change detection
- `fixture.componentRef.setInput()` for signal inputs
- Mock providers with `{ provide: Service, useValue: mock }`

### 3. Signal Testing
- Direct signal testing: `signal.set()` then assert `computed()`
- Component signal inputs via `setInput()`
- No special utilities needed -- signals are plain functions

### 4. httpResource Testing
- Use `provideHttpClientTesting()` and `HttpTestingController`
- Flush requests to resolve httpResource values
- Test loading, error, and success states

### 5. Zoneless Testing
- Use `await fixture.whenStable()` instead of `fixture.detectChanges()`
- Enable exhaustive change detection checking
- No Zone.js patches in test environment

## Quick Start

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UserCard } from './user-card';

describe('UserCard', () => {
  let fixture: ComponentFixture<UserCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserCard],
    }).compileComponents();

    fixture = TestBed.createComponent(UserCard);
  });

  it('should display user name', async () => {
    fixture.componentRef.setInput('user', { name: 'Alice', email: 'alice@test.com' });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Alice');
  });
});
```

## Fundamental Patterns

### Pattern 1: TestBed Configuration for Standalone Components

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ProductList } from './product-list';
import { CartService } from '../../core/services/cart.service';

describe('ProductList', () => {
  let fixture: ComponentFixture<ProductList>;
  let component: ProductList;
  let mockCartService: Record<string, unknown>;

  beforeEach(async () => {
    // Create mock service with signal support
    mockCartService = {
      items: signal([]),
      totalItems: computed(() => 0),
      addItem: vi.fn(),
      removeItem: vi.fn(),
    } as any;

    await TestBed.configureTestingModule({
      // Standalone components go in imports (not declarations)
      imports: [ProductList],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: CartService, useValue: mockCartService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductList);
    component = fixture.componentInstance;
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });

  it('should render product list heading', async () => {
    await fixture.whenStable();
    const heading = fixture.nativeElement.querySelector('h1');
    expect(heading?.textContent).toContain('Products');
  });
});
```

### Pattern 2: Testing Signal Inputs and Outputs

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProductCard } from './product-card';
import { Product } from '../../shared/models/product.model';

describe('ProductCard', () => {
  let fixture: ComponentFixture<ProductCard>;
  let component: ProductCard;

  const mockProduct: Product = {
    id: '1',
    name: 'Test Product',
    slug: 'test-product',
    description: 'A test product',
    price: 2999,
    images: [{ id: '1', url: '/test.jpg', alt: 'Test', width: 400, height: 400 }],
    category: { id: '1', name: 'Test', slug: 'test' },
    inStock: true,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductCard],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductCard);
    component = fixture.componentInstance;
  });

  it('should render product name', async () => {
    // Set signal input using ComponentRef.setInput()
    fixture.componentRef.setInput('product', mockProduct);
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('Test Product');
  });

  it('should render formatted price', async () => {
    fixture.componentRef.setInput('product', mockProduct);
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('$29.99');
  });

  it('should show sale badge when on sale', async () => {
    const saleProduct = { ...mockProduct, compareAtPrice: 3999 };
    fixture.componentRef.setInput('product', saleProduct);
    await fixture.whenStable();

    const badge = fixture.nativeElement.querySelector('.bg-red-500');
    expect(badge).toBeTruthy();
    expect(badge.textContent).toContain('Sale');
  });

  it('should not show sale badge when not on sale', async () => {
    fixture.componentRef.setInput('product', mockProduct);
    await fixture.whenStable();

    const badge = fixture.nativeElement.querySelector('.bg-red-500');
    expect(badge).toBeNull();
  });

  it('should emit addToCart when button clicked', async () => {
    fixture.componentRef.setInput('product', mockProduct);
    await fixture.whenStable();

    // Subscribe to output
    const emittedValues: Product[] = [];
    component.addToCart.subscribe(value => emittedValues.push(value));

    // Click add to cart button
    const button = fixture.nativeElement.querySelector('button');
    button.click();
    await fixture.whenStable();

    expect(emittedValues).toHaveLength(1);
    expect(emittedValues[0]).toEqual(mockProduct);
  });

  it('should disable button when out of stock', async () => {
    fixture.componentRef.setInput('product', { ...mockProduct, inStock: false });
    await fixture.whenStable();

    const button = fixture.nativeElement.querySelector('button');
    expect(button.disabled).toBe(true);
    expect(button.textContent).toContain('Out of Stock');
  });

  it('should respect showComparePrice input', async () => {
    const saleProduct = { ...mockProduct, compareAtPrice: 3999 };
    fixture.componentRef.setInput('product', saleProduct);
    fixture.componentRef.setInput('showComparePrice', false);
    await fixture.whenStable();

    const strikethrough = fixture.nativeElement.querySelector('.line-through');
    expect(strikethrough).toBeNull();
  });
});
```

### Pattern 3: Testing Signals Directly (Unit Tests)

```typescript
import { signal, computed } from '@angular/core';

describe('Signal Patterns', () => {
  it('should compute derived state', () => {
    const items = signal([
      { price: 100, quantity: 2 },
      { price: 200, quantity: 1 },
    ]);

    const total = computed(() =>
      items().reduce((sum, item) => sum + item.price * item.quantity, 0)
    );

    expect(total()).toBe(400);

    items.update(current => [...current, { price: 50, quantity: 3 }]);
    expect(total()).toBe(550);
  });

  it('should handle linkedSignal reset', async () => {
    const { linkedSignal } = await import('@angular/core');

    const options = signal(['Red', 'Blue', 'Green']);
    const selected = linkedSignal(() => options()[0]);

    expect(selected()).toBe('Red');

    // Manual override
    selected.set('Blue');
    expect(selected()).toBe('Blue');

    // Source change resets
    options.set(['Yellow', 'Purple']);
    expect(selected()).toBe('Yellow');
  });

  it('should respect custom equality', () => {
    interface Point { x: number; y: number; }

    const point = signal<Point>({ x: 0, y: 0 }, {
      equal: (a, b) => a.x === b.x && a.y === b.y,
    });

    let computeCount = 0;
    const label = computed(() => {
      computeCount++;
      return `(${point().x}, ${point().y})`;
    });

    // Initial read
    expect(label()).toBe('(0, 0)');
    expect(computeCount).toBe(1);

    // Same value: should not recompute
    point.set({ x: 0, y: 0 });
    expect(label()).toBe('(0, 0)');
    expect(computeCount).toBe(1); // Still 1
  });
});
```

### Pattern 4: Testing Services with Signal Stores

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { CartService } from './cart.service';
import { Product } from '../../shared/models/product.model';

describe('CartService', () => {
  let service: CartService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(CartService);
  });

  it('should initialize with empty cart', () => {
    expect(service.items()).toEqual([]);
    expect(service.isEmpty()).toBe(true);
    expect(service.totalItems()).toBe(0);
    expect(service.subtotal()).toBe(0);
  });

  it('should add item to cart', () => {
    const product = { id: '1', name: 'Shirt', price: 2999 } as Product;
    service.addItem(product, 2);

    expect(service.items()).toHaveLength(1);
    expect(service.items()[0]).toEqual({
      productId: '1',
      quantity: 2,
      price: 2999,
    });
    expect(service.totalItems()).toBe(2);
    expect(service.subtotal()).toBe(5998);
    expect(service.isEmpty()).toBe(false);
  });

  it('should increment quantity for existing item', () => {
    const product = { id: '1', price: 1000 } as Product;
    service.addItem(product, 1);
    service.addItem(product, 3);

    expect(service.items()).toHaveLength(1);
    expect(service.items()[0].quantity).toBe(4);
    expect(service.totalItems()).toBe(4);
  });

  it('should remove item', () => {
    const product1 = { id: '1', price: 1000 } as Product;
    const product2 = { id: '2', price: 2000 } as Product;
    service.addItem(product1);
    service.addItem(product2);

    service.removeItem('1');

    expect(service.items()).toHaveLength(1);
    expect(service.items()[0].productId).toBe('2');
  });

  it('should update quantity', () => {
    const product = { id: '1', price: 1000 } as Product;
    service.addItem(product, 1);

    service.updateQuantity('1', 5);
    expect(service.items()[0].quantity).toBe(5);
  });

  it('should remove item when quantity set to 0', () => {
    const product = { id: '1', price: 1000 } as Product;
    service.addItem(product, 1);

    service.updateQuantity('1', 0);
    expect(service.items()).toHaveLength(0);
  });

  it('should clear cart', () => {
    service.addItem({ id: '1', price: 1000 } as Product);
    service.addItem({ id: '2', price: 2000 } as Product);

    service.clearCart();

    expect(service.items()).toEqual([]);
    expect(service.isEmpty()).toBe(true);
  });
});
```

### Pattern 5: Testing httpResource

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { Component, Injector, signal } from '@angular/core';
import { httpResource } from '@angular/common/http';

describe('httpResource Testing', () => {
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should fetch user data', () => {
    const injector = TestBed.inject(Injector);
    const userResource = httpResource<{ id: number; name: string }>(
      () => '/api/users/1',
      { injector }
    );

    // Initially loading
    expect(userResource.isLoading()).toBe(true);
    expect(userResource.hasValue()).toBe(false);

    // Flush the request
    const req = httpTesting.expectOne('/api/users/1');
    expect(req.request.method).toBe('GET');
    req.flush({ id: 1, name: 'Alice' });

    // After flush
    expect(userResource.isLoading()).toBe(false);
    expect(userResource.hasValue()).toBe(true);
    expect(userResource.value()).toEqual({ id: 1, name: 'Alice' });
    expect(userResource.error()).toBeUndefined();
  });

  it('should handle error response', () => {
    const injector = TestBed.inject(Injector);
    const userResource = httpResource<{ id: number; name: string }>(
      () => '/api/users/999',
      { injector }
    );

    const req = httpTesting.expectOne('/api/users/999');
    req.flush('Not found', { status: 404, statusText: 'Not Found' });

    expect(userResource.isLoading()).toBe(false);
    expect(userResource.error()).toBeTruthy();
    expect(userResource.hasValue()).toBe(false);
  });

  it('should re-fetch when signal params change', () => {
    const injector = TestBed.inject(Injector);
    const userId = signal(1);

    const userResource = httpResource<{ id: number; name: string }>(
      () => `/api/users/${userId()}`,
      { injector }
    );

    // First request
    httpTesting.expectOne('/api/users/1').flush({ id: 1, name: 'Alice' });
    expect(userResource.value()!.name).toBe('Alice');

    // Change the signal
    userId.set(2);

    // Second request
    httpTesting.expectOne('/api/users/2').flush({ id: 2, name: 'Bob' });
    expect(userResource.value()!.name).toBe('Bob');
  });
});

// Testing a component that uses httpResource
describe('UserProfile Component', () => {
  let fixture: ComponentFixture<UserProfile>;
  let httpTesting: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserProfile],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(UserProfile);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  it('should show loading state', async () => {
    fixture.componentRef.setInput('userId', 1);
    await fixture.whenStable();

    // Request is pending
    expect(fixture.nativeElement.querySelector('.skeleton')).toBeTruthy();
  });

  it('should display user after data loads', async () => {
    fixture.componentRef.setInput('userId', 1);
    await fixture.whenStable();

    // Flush the httpResource request
    httpTesting.expectOne('/api/users/1').flush({
      id: 1,
      name: 'Alice',
      email: 'alice@test.com',
      posts: [],
    });
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('Alice');
    expect(fixture.nativeElement.textContent).toContain('alice@test.com');
  });

  it('should show error state on failure', async () => {
    fixture.componentRef.setInput('userId', 999);
    await fixture.whenStable();

    httpTesting.expectOne('/api/users/999').flush('', {
      status: 500,
      statusText: 'Server Error',
    });
    await fixture.whenStable();

    expect(fixture.nativeElement.querySelector('.error')).toBeTruthy();
  });
});
```

### Pattern 6: Zoneless Testing Patterns

```typescript
import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection, provideCheckNoChangesConfig } from '@angular/core';

describe('Zoneless Component Testing', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Counter],
      providers: [
        // Explicit zoneless (default in Angular 21 if zone.js is not loaded)
        provideZonelessChangeDetection(),
        // Enable exhaustive change detection checking
        provideCheckNoChangesConfig({ exhaustive: true }),
      ],
    }).compileComponents();
  });

  it('should update DOM after signal change', async () => {
    const fixture = TestBed.createComponent(Counter);
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('Count: 0');

    // Trigger signal update via button click
    fixture.nativeElement.querySelector('button').click();

    // IMPORTANT: Use whenStable() instead of detectChanges() for zoneless
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('Count: 1');
  });

  it('should handle async signal updates', async () => {
    const fixture = TestBed.createComponent(AsyncCounter);
    await fixture.whenStable();

    // Trigger async operation
    fixture.nativeElement.querySelector('[data-test="load-btn"]').click();
    await fixture.whenStable();

    // Verify loading state
    expect(fixture.nativeElement.querySelector('[data-test="loading"]')).toBeTruthy();

    // Resolve the async operation (e.g., flush HTTP)
    // ...

    await fixture.whenStable();

    // Verify completed state
    expect(fixture.nativeElement.querySelector('[data-test="loading"]')).toBeNull();
  });
});
```

### Pattern 7: Testing Functional Guards

```typescript
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';

describe('authGuard', () => {
  let router: Router;
  let authService: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([
          { path: 'protected', canActivate: [authGuard], component: ProtectedComponent },
          { path: 'login', component: LoginComponent },
        ]),
      ],
    });

    router = TestBed.inject(Router);
    authService = TestBed.inject(AuthService);
  });

  it('should allow access when authenticated', async () => {
    // Set authenticated state
    authService['_user'].set({ id: '1', name: 'Alice', role: 'user' } as any);
    authService['_token'].set('valid-token');

    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/protected');

    expect(TestBed.inject(Router).url).toBe('/protected');
  });

  it('should redirect to login when not authenticated', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/protected');

    expect(TestBed.inject(Router).url).toContain('/login');
  });

  it('should include returnUrl in redirect', async () => {
    const harness = await RouterTestingHarness.create();
    await harness.navigateByUrl('/protected');

    expect(TestBed.inject(Router).url).toBe('/login?returnUrl=%2Fprotected');
  });
});
```

### Pattern 8: Testing Pipes

```typescript
import { CurrencyFormatPipe } from './currency-format.pipe';

describe('CurrencyFormatPipe', () => {
  let pipe: CurrencyFormatPipe;

  beforeEach(() => {
    pipe = new CurrencyFormatPipe();
  });

  it('should format cents to dollars', () => {
    expect(pipe.transform(2999)).toBe('$29.99');
  });

  it('should handle zero', () => {
    expect(pipe.transform(0)).toBe('$0.00');
  });

  it('should handle negative values', () => {
    expect(pipe.transform(-500)).toBe('-$5.00');
  });

  it('should format with different currencies', () => {
    expect(pipe.transform(2999, 'EUR')).toBe('\u20AC29.99');
  });

  it('should handle large values', () => {
    expect(pipe.transform(1000000)).toBe('$10,000.00');
  });

  it('should handle null/undefined', () => {
    expect(pipe.transform(null as any)).toBe('');
    expect(pipe.transform(undefined as any)).toBe('');
  });
});
```

### Pattern 9: Testing with Mock Services

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal, computed } from '@angular/core';
import { CartPage } from './cart-page';
import { CartService } from '../services/cart.service';

describe('CartPage', () => {
  let fixture: ComponentFixture<CartPage>;
  let mockCartService: Partial<CartService>;

  const mockItems = signal([
    { productId: '1', quantity: 2, price: 1000 },
    { productId: '2', quantity: 1, price: 2500 },
  ]);

  beforeEach(async () => {
    mockCartService = {
      items: mockItems.asReadonly(),
      totalItems: computed(() => mockItems().reduce((s, i) => s + i.quantity, 0)),
      subtotal: computed(() => mockItems().reduce((s, i) => s + i.price * i.quantity, 0)),
      isEmpty: computed(() => mockItems().length === 0),
      loading: signal(false).asReadonly(),
      addItem: vi.fn(),
      removeItem: vi.fn(),
      updateQuantity: vi.fn(),
      clearCart: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [CartPage],
      providers: [
        { provide: CartService, useValue: mockCartService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CartPage);
  });

  it('should display cart items', async () => {
    await fixture.whenStable();

    const items = fixture.nativeElement.querySelectorAll('[data-test="cart-item"]');
    expect(items.length).toBe(2);
  });

  it('should display subtotal', async () => {
    await fixture.whenStable();

    const subtotal = fixture.nativeElement.querySelector('[data-test="subtotal"]');
    expect(subtotal.textContent).toContain('$45.00');
  });

  it('should call removeItem when remove button clicked', async () => {
    await fixture.whenStable();

    const removeBtn = fixture.nativeElement.querySelector('[data-test="remove-btn"]');
    removeBtn.click();
    await fixture.whenStable();

    expect(mockCartService.removeItem).toHaveBeenCalledWith('1');
  });

  it('should show empty state when cart is empty', async () => {
    mockItems.set([]);
    await fixture.whenStable();

    expect(fixture.nativeElement.textContent).toContain('Your cart is empty');
  });
});
```

## Advanced Patterns

### Pattern 10: Testing HTTP Interceptors

```typescript
import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { authInterceptor } from './auth.interceptor';
import { AuthService } from './auth.service';

describe('authInterceptor', () => {
  let httpClient: HttpClient;
  let httpTesting: HttpTestingController;
  let authService: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });

    httpClient = TestBed.inject(HttpClient);
    httpTesting = TestBed.inject(HttpTestingController);
    authService = TestBed.inject(AuthService);
  });

  afterEach(() => httpTesting.verify());

  it('should add Authorization header when token exists', () => {
    authService['_token'].set('my-jwt-token');

    httpClient.get('/api/data').subscribe();

    const req = httpTesting.expectOne('/api/data');
    expect(req.request.headers.get('Authorization')).toBe('Bearer my-jwt-token');
    req.flush({});
  });

  it('should not add Authorization header when no token', () => {
    httpClient.get('/api/public').subscribe();

    const req = httpTesting.expectOne('/api/public');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });
});
```

### Pattern 11: E2E Testing with Playwright

```typescript
// e2e/product-browse.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Product Browsing', () => {
  test('should display product list', async ({ page }) => {
    await page.goto('/products');

    // Wait for products to load
    await expect(page.locator('[data-test="product-card"]').first()).toBeVisible();

    // Verify multiple products rendered
    const products = page.locator('[data-test="product-card"]');
    await expect(products).toHaveCount(6); // Assuming 6 products per page
  });

  test('should filter products by search', async ({ page }) => {
    await page.goto('/products');

    // Type in search
    await page.fill('[data-test="search-input"]', 'laptop');
    await page.waitForTimeout(400); // Debounce

    // Verify filtered results
    const products = page.locator('[data-test="product-card"]');
    for (const product of await products.all()) {
      await expect(product).toContainText(/laptop/i);
    }
  });

  test('should navigate to product detail', async ({ page }) => {
    await page.goto('/products');

    // Click first product
    await page.locator('[data-test="product-card"] a').first().click();

    // Verify navigation to detail page
    await expect(page).toHaveURL(/\/products\/.+/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should add product to cart', async ({ page }) => {
    await page.goto('/products');

    // Click add to cart on first product
    await page.locator('[data-test="add-to-cart-btn"]').first().click();

    // Verify cart count updated
    await expect(page.locator('[data-test="cart-count"]')).toContainText('1');
  });
});

test.describe('Checkout Flow', () => {
  test('should require authentication for checkout', async ({ page }) => {
    await page.goto('/checkout');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });

  test('should complete checkout when authenticated', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[data-test="email"]', 'test@example.com');
    await page.fill('[data-test="password"]', 'password123');
    await page.click('[data-test="submit"]');
    await expect(page).toHaveURL('/products');

    // Add item to cart
    await page.locator('[data-test="add-to-cart-btn"]').first().click();

    // Navigate to checkout
    await page.goto('/checkout');
    await expect(page).toHaveURL('/checkout');

    // Fill checkout form
    await page.fill('[data-test="address"]', '123 Main St');
    await page.fill('[data-test="city"]', 'New York');
    await page.click('[data-test="place-order"]');

    // Verify order confirmation
    await expect(page.locator('[data-test="order-confirmation"]')).toBeVisible();
  });
});

// e2e/ssr.spec.ts - SSR-specific tests
test.describe('Server-Side Rendering', () => {
  test('should render product page without JavaScript', async ({ page }) => {
    // Disable JavaScript
    await page.context().route('**/*.js', route => route.abort());

    await page.goto('/products');

    // Content should be visible from server-rendered HTML
    await expect(page.locator('h1')).toContainText('Products');
  });

  test('should hydrate without DOM mismatch', async ({ page }) => {
    // Listen for hydration errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error' && msg.text().includes('hydration')) {
        errors.push(msg.text());
      }
    });

    await page.goto('/products');
    await page.waitForLoadState('networkidle');

    expect(errors).toHaveLength(0);
  });
});
```

### Pattern 12: Vitest Configuration for Angular 21

```typescript
// angular.json test configuration (Angular 21)
{
  "test": {
    "builder": "@angular/build:unit-test",
    "options": {
      "tsConfig": "tsconfig.spec.json",
      "codeCoverage": false
    }
  }
}
```

```typescript
// tsconfig.spec.json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["vitest/globals"]
  },
  "include": [
    "src/**/*.spec.ts",
    "src/**/*.d.ts"
  ]
}
```

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env['CI'],
  retries: process.env['CI'] ? 2 : 0,
  reporter: process.env['CI'] ? 'github' : 'html',
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'ng serve',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env['CI'],
  },
});
```

## Testing Strategies

### Test Distribution

| Layer | Coverage | Tool | Focus |
|-------|----------|------|-------|
| Unit | ~50% | Vitest + TestBed | Services, signals, pipes, utilities |
| Component | ~30% | Vitest + TestBed | Rendering, inputs/outputs, interactions |
| E2E | ~20% | Playwright | Critical user journeys |

### What to Test Checklist

**Components:**
- Signal inputs with various values (required, optional, edge cases)
- Output emissions on user interactions
- Conditional rendering (`@if`, `@for`, `@switch`)
- Loading, error, and empty states
- CSS class bindings and visibility

**Services:**
- Initial signal state
- State transitions via actions
- Computed signal derivations
- Error handling in async operations
- API calls with HttpTestingController

**Guards:**
- Allow access when conditions met
- Redirect when conditions not met
- Query parameter preservation on redirect

## Common Pitfalls

### Pitfall 1: Using detectChanges() Instead of whenStable()

```typescript
// WRONG: detectChanges() is unreliable with zoneless
fixture.detectChanges();
expect(fixture.nativeElement.textContent).toContain('data');

// CORRECT: use whenStable() for zoneless compatibility
await fixture.whenStable();
expect(fixture.nativeElement.textContent).toContain('data');
```

### Pitfall 2: Setting Inputs Directly on Component Instance

```typescript
// WRONG: bypasses Angular's input system
component.user = signal({ name: 'Alice' } as User) as any;

// CORRECT: use ComponentRef.setInput()
fixture.componentRef.setInput('user', { name: 'Alice' });
await fixture.whenStable();
```

### Pitfall 3: Not Verifying Outstanding HTTP Requests

```typescript
// WRONG: outstanding requests can cause test pollution
afterEach(() => {
  // Missing verification!
});

// CORRECT: verify no outstanding requests
afterEach(() => {
  httpTesting.verify();
});
```

### Pitfall 4: Testing Implementation Details Instead of Behavior

```typescript
// WRONG: testing internal signal value
expect(component['_loading']()).toBe(true);

// CORRECT: test what the user sees
expect(fixture.nativeElement.querySelector('.spinner')).toBeTruthy();
```

## Best Practices

1. **Use `await fixture.whenStable()`** for all DOM assertions in zoneless mode
2. **Use `fixture.componentRef.setInput()`** for setting signal inputs in tests
3. **Mock services with signals** to match the real service's signal API
4. **Verify outstanding HTTP requests** with `httpTesting.verify()` in `afterEach`
5. **Test behavior, not implementation** -- assert DOM content and user-visible outcomes
6. **Use `data-test` attributes** for reliable element selection in tests
7. **Keep tests isolated** -- each test should set up its own state
8. **Test error states** -- verify the component handles API failures gracefully
9. **Run tests in CI** with `ng test --code-coverage` for coverage reports
10. **Use Playwright** for critical user journeys that span multiple pages

## Resources

- **Angular Testing Guide**: https://angular.dev/guide/testing
- **Angular TestBed API**: https://angular.dev/api/core/testing/TestBed
- **Vitest Documentation**: https://vitest.dev
- **Playwright Documentation**: https://playwright.dev
- **Angular Component Testing**: https://angular.dev/guide/testing/components-scenarios
