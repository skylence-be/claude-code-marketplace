---
name: angular-signals-patterns
description: Complete guide to Angular signals including signal(), computed(), effect(), linkedSignal(), model signals, signal-based inputs/outputs/queries, toSignal(), toObservable(), and real-world patterns for state management, form handling, and component communication.
category: angular
tags: [angular, signals, reactivity, computed, effect, linkedSignal, toSignal, state-management]
related_skills: [angular-blueprint, angular-dependency-injection, rxjs-angular-patterns, angular-performance-optimization]
---

# Angular Signals Patterns

Comprehensive guide to Angular's signal-based reactivity system covering writable signals, computed signals, effects, linkedSignal, signal-based component APIs (inputs, outputs, model, queries), RxJS interop with toSignal/toObservable, and production patterns for state management in Angular 21+ applications.

## When to Use This Skill

- Managing component-level reactive state with signals
- Building signal store services for global state management
- Creating derived state with computed signals
- Implementing dependent-resettable state with linkedSignal
- Converting between signals and RxJS observables
- Building reactive component APIs with signal inputs and outputs
- Implementing fine-grained change detection without Zone.js
- Creating declarative data fetching with httpResource
- Testing signal-based components and services

## Core Concepts

### 1. Writable Signals
- `signal(initialValue)` creates reactive mutable state
- Read by calling as a function: `count()`
- Write with `set()`, `update()`, or mutate patterns
- `asReadonly()` creates a read-only view for public APIs

### 2. Computed Signals
- `computed(() => expression)` creates derived read-only state
- Lazily evaluated and memoized
- Dependencies tracked automatically at runtime
- Never trigger side effects inside computed

### 3. Effects
- `effect(() => sideEffect)` runs code when dependencies change
- Runs at least once (initial execution)
- Auto-cleanup on component/service destroy
- Use sparingly; prefer declarative patterns

### 4. Signal Component APIs
- `input()` / `input.required()` for signal-based inputs
- `output()` for type-safe event emitters
- `model()` for two-way binding signals
- `viewChild()` / `viewChildren()` / `contentChild()` / `contentChildren()` for signal-based queries

### 5. RxJS Interop
- `toSignal()` converts Observable to Signal
- `toObservable()` converts Signal to Observable
- `takeUntilDestroyed()` for automatic unsubscription

## Quick Start

```typescript
import { Component, signal, computed, effect } from '@angular/core';

@Component({
  selector: 'app-counter',
  template: `
    <h2>Count: {{ count() }}</h2>
    <h3>Doubled: {{ doubled() }}</h3>
    <button (click)="increment()">Increment</button>
  `,
})
export class Counter {
  readonly count = signal(0);
  readonly doubled = computed(() => this.count() * 2);

  constructor() {
    effect(() => {
      console.log(`Count changed to: ${this.count()}`);
    });
  }

  increment(): void {
    this.count.update(c => c + 1);
  }
}
```

## Fundamental Patterns

### Pattern 1: Writable Signals and State Management

```typescript
import { Component, signal } from '@angular/core';

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

@Component({
  selector: 'app-todo-list',
  template: `
    <input #input (keyup.enter)="addTodo(input.value); input.value = ''">

    @for (todo of todos(); track todo.id) {
      <div [class.completed]="todo.completed">
        <input
          type="checkbox"
          [checked]="todo.completed"
          (change)="toggleTodo(todo.id)"
        />
        <span>{{ todo.text }}</span>
        <button (click)="removeTodo(todo.id)">Remove</button>
      </div>
    } @empty {
      <p>No todos yet. Add one above.</p>
    }
  `,
})
export class TodoList {
  readonly todos = signal<Todo[]>([]);
  private nextId = 1;

  addTodo(text: string): void {
    if (!text.trim()) return;
    this.todos.update(todos => [
      ...todos,
      { id: this.nextId++, text: text.trim(), completed: false },
    ]);
  }

  toggleTodo(id: number): void {
    this.todos.update(todos =>
      todos.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  }

  removeTodo(id: number): void {
    this.todos.update(todos => todos.filter(todo => todo.id !== id));
  }
}
```

### Pattern 2: Computed Signals for Derived State

```typescript
import { Component, signal, computed } from '@angular/core';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

@Component({
  selector: 'app-cart-summary',
  template: `
    <div class="cart-summary">
      <p>Items: {{ itemCount() }}</p>
      <p>Subtotal: {{ subtotal() | currency }}</p>
      <p>Tax ({{ taxRate() * 100 }}%): {{ tax() | currency }}</p>
      <p class="total">Total: {{ total() | currency }}</p>

      @if (hasDiscount()) {
        <p class="discount">Discount applied: {{ discountAmount() | currency }} off</p>
      }
    </div>
  `,
})
export class CartSummary {
  readonly items = signal<CartItem[]>([]);
  readonly taxRate = signal(0.08);
  readonly discountCode = signal<string | null>(null);

  // Simple derived state
  readonly itemCount = computed(() =>
    this.items().reduce((sum, item) => sum + item.quantity, 0)
  );

  readonly subtotal = computed(() =>
    this.items().reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  // Derived from another computed
  readonly tax = computed(() => this.subtotal() * this.taxRate());

  // Conditional computed -- dependencies tracked dynamically
  readonly hasDiscount = computed(() => this.discountCode() !== null);

  readonly discountAmount = computed(() => {
    const code = this.discountCode();
    if (!code) return 0;
    // Discount logic based on code
    if (code === 'SAVE10') return this.subtotal() * 0.1;
    if (code === 'SAVE20') return this.subtotal() * 0.2;
    return 0;
  });

  // Chained computed: subtotal - discount + tax
  readonly total = computed(() =>
    this.subtotal() - this.discountAmount() + this.tax()
  );
}
```

### Pattern 3: Effects for Side Effects

```typescript
import { Component, signal, effect, inject, Injector, runInInjectionContext } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-theme-manager',
  template: `
    <select (change)="theme.set($any($event.target).value)">
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="system">System</option>
    </select>
    <p>Current theme: {{ theme() }}</p>
  `,
})
export class ThemeManager {
  private readonly document = inject(DOCUMENT);
  readonly theme = signal<'light' | 'dark' | 'system'>('system');

  constructor() {
    // Effect: sync theme to DOM and localStorage (browser only)
    effect(() => {
      const currentTheme = this.theme();
      this.document.documentElement.setAttribute('data-theme', currentTheme);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('theme', currentTheme);
      }
    });

    // Effect with cleanup
    effect((onCleanup) => {
      const currentTheme = this.theme();
      console.log(`Theme changed to: ${currentTheme}`);

      const timer = setTimeout(() => {
        console.log(`Theme ${currentTheme} has been active for 5 seconds`);
      }, 5000);

      onCleanup(() => {
        clearTimeout(timer);
      });
    });

    // Initialize from localStorage
    const saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark' || saved === 'system') {
      this.theme.set(saved);
    }
  }
}
```

### Pattern 4: LinkedSignal for Dependent Resettable State

```typescript
import { Component, signal, computed, linkedSignal } from '@angular/core';

interface Product {
  id: string;
  name: string;
  variants: string[];
  sizes: string[];
}

@Component({
  selector: 'app-product-configurator',
  template: `
    <h2>{{ selectedProduct().name }}</h2>

    <label>Variant:</label>
    <select (change)="selectedVariant.set($any($event.target).value)">
      @for (variant of selectedProduct().variants; track variant) {
        <option [value]="variant" [selected]="variant === selectedVariant()">
          {{ variant }}
        </option>
      }
    </select>

    <label>Size:</label>
    <select (change)="selectedSize.set($any($event.target).value)">
      @for (size of selectedProduct().sizes; track size) {
        <option [value]="size" [selected]="size === selectedSize()">
          {{ size }}
        </option>
      }
    </select>

    <label>Quantity:</label>
    <input
      type="number"
      [value]="quantity()"
      (input)="quantity.set(+$any($event.target).value)"
      min="1"
    />

    <p>Configuration: {{ selectedVariant() }}, {{ selectedSize() }}, qty {{ quantity() }}</p>
  `,
})
export class ProductConfigurator {
  readonly products = signal<Product[]>([
    { id: '1', name: 'T-Shirt', variants: ['Red', 'Blue', 'Green'], sizes: ['S', 'M', 'L', 'XL'] },
    { id: '2', name: 'Hoodie', variants: ['Black', 'Gray'], sizes: ['M', 'L', 'XL', 'XXL'] },
  ]);

  readonly selectedProductId = signal('1');

  readonly selectedProduct = computed(() =>
    this.products().find(p => p.id === this.selectedProductId())!
  );

  // linkedSignal: resets to first variant when product changes, but user can override
  readonly selectedVariant = linkedSignal(() => this.selectedProduct().variants[0]);

  // linkedSignal: resets to first size when product changes
  readonly selectedSize = linkedSignal(() => this.selectedProduct().sizes[0]);

  // linkedSignal with transform: resets quantity to 1 when product changes
  readonly quantity = linkedSignal({
    source: this.selectedProductId,
    computation: () => 1,
  });

  selectProduct(id: string): void {
    this.selectedProductId.set(id);
    // selectedVariant, selectedSize, and quantity all automatically reset
  }
}
```

### Pattern 5: Signal-Based Inputs and Outputs

```typescript
import { Component, input, output, computed, ChangeDetectionStrategy } from '@angular/core';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'editor' | 'viewer';
}

@Component({
  selector: 'app-user-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="user-card" [class]="cardClass()">
      <div class="avatar">{{ initials() }}</div>
      <div class="info">
        <h3>{{ user().name }}</h3>
        <p>{{ user().email }}</p>
        @if (showRole()) {
          <span class="badge">{{ user().role }}</span>
        }
      </div>
      <div class="actions">
        <button (click)="edit.emit(user())">Edit</button>
        @if (deletable()) {
          <button (click)="delete.emit(user().id)" class="danger">Delete</button>
        }
      </div>
    </div>
  `,
})
export class UserCard {
  // Required input -- must be provided by parent
  readonly user = input.required<User>();

  // Optional inputs with defaults
  readonly showRole = input(true);
  readonly deletable = input(false);
  readonly variant = input<'compact' | 'full'>('full');

  // Typed outputs
  readonly edit = output<User>();
  readonly delete = output<string>();

  // Computed from inputs (auto-updates when inputs change)
  protected readonly initials = computed(() => {
    const name = this.user().name;
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  });

  protected readonly cardClass = computed(() =>
    `user-card--${this.variant()}`
  );
}
```

### Pattern 6: Model Signals for Two-Way Binding

```typescript
import { Component, model, input, computed, signal } from '@angular/core';

@Component({
  selector: 'app-star-rating',
  template: `
    <div class="stars">
      @for (star of starArray(); track star) {
        <button
          class="star"
          [class.filled]="star <= value()"
          [class.readonly]="readonly()"
          [disabled]="readonly()"
          (click)="onStarClick(star)"
        >
          &#9733;
        </button>
      }
    </div>
    <span class="label">{{ value() }} / {{ max() }}</span>
  `,
})
export class StarRating {
  // model() creates a two-way bindable signal
  // Parent uses: <app-star-rating [(value)]="rating" />
  readonly value = model(0);

  readonly max = input(5);
  readonly readonly = input(false);

  protected readonly starArray = computed(() =>
    Array.from({ length: this.max() }, (_, i) => i + 1)
  );

  onStarClick(star: number): void {
    if (!this.readonly()) {
      this.value.set(star);
    }
  }
}

// Parent component usage
@Component({
  selector: 'app-review-form',
  imports: [StarRating],
  template: `
    <h3>Leave a Review</h3>
    <app-star-rating [(value)]="rating" [max]="5" />
    <p>Your rating: {{ rating() }}</p>
  `,
})
export class ReviewForm {
  readonly rating = signal(0);
}
```

### Pattern 7: Signal-Based Queries (viewChild, viewChildren, contentChild, contentChildren)

```typescript
import { Component, viewChild, viewChildren, contentChild, contentChildren, signal, effect, ElementRef, afterNextRender } from '@angular/core';

@Component({
  selector: 'app-tab-panel',
  template: `
    <div class="tab-header">
      @for (tab of tabLabels(); track $index) {
        <button
          [class.active]="$index === activeIndex()"
          (click)="activeIndex.set($index)"
        >
          {{ tab }}
        </button>
      }
    </div>
    <div class="tab-content">
      <ng-content />
    </div>
  `,
})
export class TabPanel {
  // Query content children projected via ng-content
  readonly tabs = contentChildren(TabItem);

  readonly activeIndex = signal(0);

  readonly tabLabels = computed(() =>
    this.tabs().map(tab => tab.label())
  );
}

@Component({
  selector: 'app-tab-item',
  template: `<div [hidden]="!active()"><ng-content /></div>`,
})
export class TabItem {
  readonly label = input.required<string>();
  readonly active = input(false);
}

@Component({
  selector: 'app-search-form',
  template: `
    <input #searchInput type="text" placeholder="Search..." />
    <div #resultsContainer class="results">
      @for (result of results(); track result.id) {
        <div #resultItem class="result-item">{{ result.name }}</div>
      }
    </div>
  `,
})
export class SearchForm {
  // Single element query
  readonly searchInput = viewChild.required<ElementRef<HTMLInputElement>>('searchInput');
  readonly resultsContainer = viewChild<ElementRef>('resultsContainer');

  // Multiple element query
  readonly resultItems = viewChildren<ElementRef>('resultItem');

  readonly results = signal<{ id: number; name: string }[]>([]);

  constructor() {
    // Focus input after render
    afterNextRender(() => {
      this.searchInput().nativeElement.focus();
    });

    // React to query changes
    effect(() => {
      const items = this.resultItems();
      console.log(`Rendered ${items.length} result items`);
    });
  }
}
```

### Pattern 8: toSignal and toObservable for RxJS Interop

```typescript
import { Component, signal, inject, computed } from '@angular/core';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { switchMap, map, debounceTime, distinctUntilChanged } from 'rxjs';

interface SearchResult {
  id: string;
  title: string;
}

@Component({
  selector: 'app-search-page',
  template: `
    <input
      type="text"
      [value]="searchQuery()"
      (input)="searchQuery.set($any($event.target).value)"
      placeholder="Search..."
    />

    @if (results()?.length) {
      @for (result of results()!; track result.id) {
        <div class="result">{{ result.title }}</div>
      }
    } @else if (searchQuery()) {
      <p>No results found.</p>
    }

    <p>Route ID: {{ routeId() }}</p>
  `,
})
export class SearchPage {
  private readonly route = inject(ActivatedRoute);
  private readonly http = inject(HttpClient);

  // Convert route params observable to signal
  readonly routeId = toSignal(
    this.route.paramMap.pipe(map(params => params.get('id'))),
    { initialValue: null }
  );

  // Writable signal for search query
  readonly searchQuery = signal('');

  // Convert signal to observable, apply RxJS operators, convert back to signal
  readonly results = toSignal<SearchResult[] | undefined>(
    toObservable(this.searchQuery).pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => {
        if (!query.trim()) return [undefined];
        return this.http.get<SearchResult[]>('/api/search', {
          params: { q: query },
        });
      }),
    ),
    { initialValue: undefined }
  );

  // toSignal with requireSync for BehaviorSubject-like observables
  readonly currentRoute = toSignal(
    this.route.url.pipe(map(segments => segments.join('/'))),
    { requireSync: true } // no initialValue needed if observable emits synchronously
  );
}
```

### Pattern 9: Signal Store Service Pattern

```typescript
import { Injectable, signal, computed, inject, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface Notification {
  id: string;
  message: string;
  type: 'info' | 'warning' | 'error';
  read: boolean;
  createdAt: Date;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly http = inject(HttpClient);

  // Private writable signals
  private readonly _notifications = signal<Notification[]>([]);
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);
  private readonly _filter = signal<'all' | 'unread'>('all');

  // Public readonly signals
  readonly notifications = this._notifications.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();
  readonly filter = this._filter.asReadonly();

  // Computed derived state
  readonly unreadCount = computed(() =>
    this._notifications().filter(n => !n.read).length
  );

  readonly hasUnread = computed(() => this.unreadCount() > 0);

  readonly filteredNotifications = computed(() => {
    const all = this._notifications();
    if (this._filter() === 'unread') {
      return all.filter(n => !n.read);
    }
    return all;
  });

  readonly notificationsByType = computed(() => {
    const grouped = new Map<string, Notification[]>();
    for (const n of this._notifications()) {
      const existing = grouped.get(n.type) ?? [];
      grouped.set(n.type, [...existing, n]);
    }
    return grouped;
  });

  // Actions
  async loadNotifications(): Promise<void> {
    this._loading.set(true);
    this._error.set(null);
    try {
      const data = await firstValueFrom(
        this.http.get<Notification[]>('/api/notifications')
      );
      this._notifications.set(data);
    } catch (e) {
      this._error.set('Failed to load notifications');
    } finally {
      this._loading.set(false);
    }
  }

  markAsRead(id: string): void {
    this._notifications.update(notifications =>
      notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      )
    );
    // Fire-and-forget API call
    firstValueFrom(
      this.http.patch(`/api/notifications/${id}`, { read: true })
    ).catch(() => {
      // Rollback on failure
      this._notifications.update(notifications =>
        notifications.map(n =>
          n.id === id ? { ...n, read: false } : n
        )
      );
    });
  }

  markAllAsRead(): void {
    this._notifications.update(notifications =>
      notifications.map(n => ({ ...n, read: true }))
    );
  }

  setFilter(filter: 'all' | 'unread'): void {
    this._filter.set(filter);
  }

  dismiss(id: string): void {
    this._notifications.update(notifications =>
      notifications.filter(n => n.id !== id)
    );
  }
}
```

### Pattern 10: httpResource for Declarative Data Fetching

```typescript
import { Component, signal, input, computed, inject, ChangeDetectionStrategy } from '@angular/core';
import { httpResource } from '@angular/common/http';

interface User {
  id: number;
  name: string;
  email: string;
  posts: Post[];
}

interface Post {
  id: number;
  title: string;
  body: string;
}

@Component({
  selector: 'app-user-profile',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (userResource.isLoading()) {
      <div class="skeleton animate-pulse">
        <div class="h-8 w-48 bg-gray-200 rounded mb-4"></div>
        <div class="h-4 w-64 bg-gray-200 rounded mb-2"></div>
      </div>
    } @else if (userResource.error()) {
      <div class="error">
        <p>Failed to load user profile.</p>
        <button (click)="userResource.reload()">Retry</button>
      </div>
    } @else if (userResource.hasValue()) {
      <div class="profile">
        <h2>{{ userResource.value()!.name }}</h2>
        <p>{{ userResource.value()!.email }}</p>

        <h3>Posts ({{ postCount() }})</h3>
        @for (post of userResource.value()!.posts; track post.id) {
          <article>
            <h4>{{ post.title }}</h4>
            <p>{{ post.body }}</p>
          </article>
        }
      </div>
    }
  `,
})
export class UserProfile {
  readonly userId = input.required<number>();

  // httpResource automatically re-fetches when userId input changes
  readonly userResource = httpResource<User>(() => `/api/users/${this.userId()}`);

  readonly postCount = computed(() =>
    this.userResource.hasValue() ? this.userResource.value()!.posts.length : 0
  );
}
```

### Pattern 11: Untracked Reads to Avoid Unwanted Dependencies

```typescript
import { Component, signal, computed, effect, untracked, inject } from '@angular/core';

@Component({
  selector: 'app-analytics-tracker',
  template: `
    <input
      type="text"
      [value]="searchQuery()"
      (input)="searchQuery.set($any($event.target).value)"
    />
    <p>Results for: {{ searchQuery() }}</p>
  `,
})
export class AnalyticsTracker {
  private readonly analytics = inject(AnalyticsService);

  readonly searchQuery = signal('');
  readonly sessionId = signal('session-123');
  readonly userId = signal('user-456');

  constructor() {
    // Only re-run when searchQuery changes, NOT when sessionId or userId change
    effect(() => {
      const query = this.searchQuery();

      // Read sessionId and userId without creating dependencies
      untracked(() => {
        this.analytics.track('search', {
          query,
          sessionId: this.sessionId(),
          userId: this.userId(),
        });
      });
    });
  }
}
```

### Pattern 12: Equality Functions and Signal Options

```typescript
import { signal, computed } from '@angular/core';

// Custom equality for deep comparison
interface Coordinates {
  lat: number;
  lng: number;
}

// Only emit when coordinates actually change (not on every object creation)
const location = signal<Coordinates>(
  { lat: 0, lng: 0 },
  {
    equal: (a, b) => a.lat === b.lat && a.lng === b.lng,
  }
);

// This will NOT trigger subscribers because the values are equal
location.set({ lat: 0, lng: 0 });

// This WILL trigger subscribers
location.set({ lat: 1.5, lng: 2.5 });

// Practical example: prevent unnecessary re-renders for array results
const items = signal<string[]>([], {
  equal: (a, b) =>
    a.length === b.length && a.every((val, idx) => val === b[idx]),
});

// Computed with custom equality
interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

const rawData = signal({ page: 1, pageSize: 10, total: 100 });

const pagination = computed<PaginationState>(
  () => ({
    page: rawData().page,
    pageSize: rawData().pageSize,
    total: rawData().total,
  }),
  {
    equal: (a, b) =>
      a.page === b.page && a.pageSize === b.pageSize && a.total === b.total,
  }
);
```

## Advanced Patterns

### Pattern 13: Composing Signals Across Services

```typescript
import { Injectable, signal, computed, inject } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class UserPreferencesService {
  private readonly _currency = signal<'USD' | 'EUR' | 'GBP'>('USD');
  private readonly _locale = signal('en-US');
  private readonly _timezone = signal('America/New_York');

  readonly currency = this._currency.asReadonly();
  readonly locale = this._locale.asReadonly();
  readonly timezone = this._timezone.asReadonly();

  setCurrency(currency: 'USD' | 'EUR' | 'GBP'): void {
    this._currency.set(currency);
  }

  setLocale(locale: string): void {
    this._locale.set(locale);
  }
}

@Injectable({ providedIn: 'root' })
export class PricingService {
  private readonly prefs = inject(UserPreferencesService);
  private readonly _exchangeRates = signal<Record<string, number>>({
    USD: 1,
    EUR: 0.92,
    GBP: 0.79,
  });

  readonly currentRate = computed(() =>
    this._exchangeRates()[this.prefs.currency()] ?? 1
  );

  formatPrice(priceUSD: number): string {
    const converted = priceUSD * this.currentRate();
    return new Intl.NumberFormat(this.prefs.locale(), {
      style: 'currency',
      currency: this.prefs.currency(),
    }).format(converted);
  }

  // Computed that depends on signals from another service
  readonly currencySymbol = computed(() => {
    const formatter = new Intl.NumberFormat(this.prefs.locale(), {
      style: 'currency',
      currency: this.prefs.currency(),
    });
    const parts = formatter.formatToParts(0);
    return parts.find(p => p.type === 'currency')?.value ?? '$';
  });
}
```

### Pattern 14: Signal-Based Form Patterns

```typescript
import { Component, signal, computed, effect } from '@angular/core';

@Component({
  selector: 'app-signup-form',
  template: `
    <form (submit)="onSubmit($event)">
      <div>
        <label>Name</label>
        <input
          [value]="name()"
          (input)="name.set($any($event.target).value)"
        />
        @if (nameError()) {
          <span class="error">{{ nameError() }}</span>
        }
      </div>

      <div>
        <label>Email</label>
        <input
          type="email"
          [value]="email()"
          (input)="email.set($any($event.target).value)"
        />
        @if (emailError()) {
          <span class="error">{{ emailError() }}</span>
        }
      </div>

      <div>
        <label>Password</label>
        <input
          type="password"
          [value]="password()"
          (input)="password.set($any($event.target).value)"
        />
        <div class="password-strength">
          Strength: {{ passwordStrength() }}
        </div>
      </div>

      <button type="submit" [disabled]="!isValid() || submitting()">
        {{ submitting() ? 'Submitting...' : 'Sign Up' }}
      </button>
    </form>
  `,
})
export class SignupForm {
  readonly name = signal('');
  readonly email = signal('');
  readonly password = signal('');
  readonly submitting = signal(false);

  // Validation as computed signals
  readonly nameError = computed(() => {
    const n = this.name();
    if (!n) return 'Name is required';
    if (n.length < 2) return 'Name must be at least 2 characters';
    return null;
  });

  readonly emailError = computed(() => {
    const e = this.email();
    if (!e) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)) return 'Invalid email format';
    return null;
  });

  readonly passwordStrength = computed(() => {
    const p = this.password();
    if (p.length < 6) return 'weak';
    if (p.length < 10) return 'medium';
    if (/[A-Z]/.test(p) && /[0-9]/.test(p) && /[^A-Za-z0-9]/.test(p)) return 'strong';
    return 'medium';
  });

  readonly isValid = computed(() =>
    !this.nameError() && !this.emailError() && this.password().length >= 6
  );

  onSubmit(event: Event): void {
    event.preventDefault();
    if (!this.isValid()) return;

    this.submitting.set(true);
    // Submit logic...
  }
}
```

### Pattern 15: Pagination with Signals

```typescript
import { Component, signal, computed, inject, linkedSignal } from '@angular/core';
import { httpResource } from '@angular/common/http';

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

interface Product {
  id: string;
  name: string;
  price: number;
}

@Component({
  selector: 'app-product-table',
  template: `
    <div class="controls">
      <select (change)="pageSize.set(+$any($event.target).value)">
        <option value="10">10 per page</option>
        <option value="25">25 per page</option>
        <option value="50">50 per page</option>
      </select>
      <input
        placeholder="Search..."
        (input)="searchQuery.set($any($event.target).value)"
      />
    </div>

    @if (productsResource.hasValue()) {
      <table>
        <thead>
          <tr>
            <th (click)="toggleSort('name')">Name {{ sortIndicator('name') }}</th>
            <th (click)="toggleSort('price')">Price {{ sortIndicator('price') }}</th>
          </tr>
        </thead>
        <tbody>
          @for (product of productsResource.value()!.data; track product.id) {
            <tr>
              <td>{{ product.name }}</td>
              <td>{{ product.price | currency }}</td>
            </tr>
          }
        </tbody>
      </table>

      <div class="pagination">
        <button [disabled]="currentPage() <= 1" (click)="currentPage.set(currentPage() - 1)">
          Previous
        </button>
        <span>Page {{ currentPage() }} of {{ totalPages() }}</span>
        <button [disabled]="currentPage() >= totalPages()" (click)="currentPage.set(currentPage() + 1)">
          Next
        </button>
      </div>
    }
  `,
})
export class ProductTable {
  readonly searchQuery = signal('');
  readonly pageSize = signal(10);
  readonly sortField = signal<'name' | 'price'>('name');
  readonly sortDirection = signal<'asc' | 'desc'>('asc');

  // Reset page to 1 when search, pageSize, or sort changes
  readonly currentPage = linkedSignal({
    source: () => ({
      search: this.searchQuery(),
      size: this.pageSize(),
      field: this.sortField(),
      dir: this.sortDirection(),
    }),
    computation: () => 1,
  });

  readonly productsResource = httpResource<PaginatedResponse<Product>>(() => ({
    url: '/api/products',
    params: {
      page: this.currentPage().toString(),
      pageSize: this.pageSize().toString(),
      q: this.searchQuery(),
      sortBy: this.sortField(),
      sortDir: this.sortDirection(),
    },
  }));

  readonly totalPages = computed(() => {
    if (!this.productsResource.hasValue()) return 1;
    const response = this.productsResource.value()!;
    return Math.ceil(response.total / response.pageSize);
  });

  toggleSort(field: 'name' | 'price'): void {
    if (this.sortField() === field) {
      this.sortDirection.update(dir => dir === 'asc' ? 'desc' : 'asc');
    } else {
      this.sortField.set(field);
      this.sortDirection.set('asc');
    }
  }

  sortIndicator(field: string): string {
    if (this.sortField() !== field) return '';
    return this.sortDirection() === 'asc' ? '\u25B2' : '\u25BC';
  }
}
```

## Testing Strategies

### Testing Signals Directly

```typescript
import { signal, computed, effect } from '@angular/core';
import { TestBed } from '@angular/core/testing';

describe('Signal Patterns', () => {
  it('should update computed when signal changes', () => {
    const count = signal(0);
    const doubled = computed(() => count() * 2);

    expect(doubled()).toBe(0);
    count.set(5);
    expect(doubled()).toBe(10);
  });

  it('should reset linkedSignal when source changes', () => {
    const options = signal(['a', 'b', 'c']);
    const selected = linkedSignal(() => options()[0]);

    expect(selected()).toBe('a');
    selected.set('b');
    expect(selected()).toBe('b');

    options.set(['x', 'y', 'z']);
    expect(selected()).toBe('x'); // Reset to first
  });
});
```

### Testing Signal Store Services

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { NotificationService } from './notification.service';

describe('NotificationService', () => {
  let service: NotificationService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(NotificationService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  it('should start with empty state', () => {
    expect(service.notifications()).toEqual([]);
    expect(service.unreadCount()).toBe(0);
    expect(service.hasUnread()).toBe(false);
  });

  it('should load notifications', async () => {
    const mockData = [
      { id: '1', message: 'Test', type: 'info', read: false, createdAt: new Date() },
    ];

    const promise = service.loadNotifications();
    expect(service.loading()).toBe(true);

    httpTesting.expectOne('/api/notifications').flush(mockData);
    await promise;

    expect(service.loading()).toBe(false);
    expect(service.notifications()).toEqual(mockData);
    expect(service.unreadCount()).toBe(1);
  });

  it('should mark notification as read', () => {
    // Pre-populate
    service['_notifications'].set([
      { id: '1', message: 'Test', type: 'info', read: false, createdAt: new Date() },
    ]);

    service.markAsRead('1');

    expect(service.notifications()[0].read).toBe(true);
    expect(service.unreadCount()).toBe(0);
  });
});
```

## Common Pitfalls

### Pitfall 1: Async Operations Inside Computed

```typescript
// WRONG: async operations in computed
const data = computed(async () => {
  const response = await fetch('/api/data');
  return response.json();
});

// CORRECT: use httpResource or toSignal
const dataResource = httpResource<MyData>(() => '/api/data');

// Or with toSignal
const data = toSignal(this.http.get<MyData>('/api/data'));
```

### Pitfall 2: Side Effects in Computed

```typescript
// WRONG: side effects in computed
const fullName = computed(() => {
  console.log('Computing...'); // Side effect!
  this.analytics.track('name-computed'); // Side effect!
  return `${firstName()} ${lastName()}`;
});

// CORRECT: pure computation in computed, side effects in effect
const fullName = computed(() => `${firstName()} ${lastName()}`);

effect(() => {
  console.log(`Name is now: ${fullName()}`);
  this.analytics.track('name-changed');
});
```

### Pitfall 3: Mutating Signal Values Directly

```typescript
// WRONG: mutating array in place
const items = signal<string[]>(['a', 'b']);
items().push('c'); // Mutates but does NOT trigger reactivity

// CORRECT: use update() with immutable patterns
items.update(current => [...current, 'c']);
```

### Pitfall 4: Missing untracked() for Non-Dependent Reads

```typescript
// WRONG: effect re-runs when loggingEnabled changes (unwanted)
effect(() => {
  const query = this.searchQuery();
  if (this.loggingEnabled()) {  // Creates unwanted dependency
    console.log('Search:', query);
  }
});

// CORRECT: use untracked for reads that should not create dependencies
effect(() => {
  const query = this.searchQuery();
  untracked(() => {
    if (this.loggingEnabled()) {
      console.log('Search:', query);
    }
  });
});
```

### Pitfall 5: Overusing Effects

```typescript
// WRONG: using effect to sync derived state
effect(() => {
  this.fullName.set(`${this.firstName()} ${this.lastName()}`);
});

// CORRECT: use computed for derived state
readonly fullName = computed(() => `${this.firstName()} ${this.lastName()}`);
```

## Best Practices

1. **Use `computed()` for all derived state** -- never use `effect()` to sync state that can be expressed declaratively
2. **Expose `asReadonly()`** on service signals to prevent external mutation
3. **Use `input()` / `output()` signal APIs** instead of `@Input()` / `@Output()` decorators
4. **Use `linkedSignal()`** when a writable signal should reset when a source changes
5. **Minimize `effect()` usage** -- effects are for side effects only (DOM, localStorage, analytics, logging)
6. **Use `untracked()`** to read signals without creating dependencies in effects
7. **Use immutable update patterns** with `signal.update()` for arrays and objects
8. **Prefer `httpResource`** for declarative GET queries over manual HttpClient subscriptions
9. **Use `toSignal()` with `initialValue`** when converting observables to avoid `undefined` types
10. **Test signals directly** -- they are plain functions, no special test utilities needed

## Resources

- **Angular Signals Guide**: https://angular.dev/guide/signals
- **Angular Signal Inputs**: https://angular.dev/guide/signals/inputs
- **Angular httpResource**: https://angular.dev/guide/http/http-resource
- **Angular RxJS Interop**: https://angular.dev/guide/signals/rxjs-interop
- **Angular linkedSignal**: https://angular.dev/api/core/linkedSignal
