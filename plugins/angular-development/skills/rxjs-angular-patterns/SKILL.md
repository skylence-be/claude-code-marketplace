---
name: rxjs-angular-patterns
description: Master RxJS in Angular covering operators for HTTP, signal interop (toSignal, toObservable), takeUntilDestroyed for cleanup, switchMap/concatMap/exhaustMap patterns, error handling, HTTP interceptors, and testing observables.
category: angular
tags: [angular, rxjs, observables, operators, toSignal, toObservable, takeUntilDestroyed, http]
related_skills: [angular-signals-patterns, angular-dependency-injection, angular-testing-patterns, angular-performance-optimization]
---

# RxJS in Angular Patterns

Comprehensive guide to using RxJS effectively in Angular 21+ applications, covering the right operators for HTTP requests, signal interop with toSignal and toObservable, automatic cleanup with takeUntilDestroyed, flattening strategies (switchMap, concatMap, exhaustMap, mergeMap), error handling patterns, HTTP interceptor composition, and testing observables.

## When to Use This Skill

- Making HTTP requests with HttpClient (which returns Observables)
- Converting between RxJS observables and Angular signals
- Implementing search-as-you-type with debounce and switchMap
- Building real-time features with WebSocket streams
- Composing complex async workflows with operators
- Handling errors in observable chains
- Cleaning up subscriptions to prevent memory leaks
- Testing components and services that use observables

## Core Concepts

### 1. When to Use RxJS vs Signals
- **Signals**: Synchronous state, computed values, component state, template binding
- **RxJS**: Async streams, HTTP requests, WebSockets, complex async composition
- **Bridge**: `toSignal()` and `toObservable()` for interop
- Angular 21+ favors signals for state, RxJS for async streams

### 2. Flattening Operators
- **switchMap**: Cancel previous, use latest (search, navigation)
- **concatMap**: Queue in order (form submissions, sequential writes)
- **exhaustMap**: Ignore new while busy (button clicks, login)
- **mergeMap**: Run all concurrently (independent batch operations)

### 3. Cleanup Patterns
- **takeUntilDestroyed()**: Auto-unsubscribe on component/service destroy
- **DestroyRef**: Manual cleanup registration
- **toSignal()**: Manages subscription lifecycle automatically
- **AsyncPipe**: Auto-subscribe/unsubscribe in templates (legacy)

### 4. Error Handling
- **catchError**: Handle error and return fallback
- **retry / retryWhen**: Automatic retry on failure
- **EMPTY / of()**: Return empty or default on error
- Never let errors propagate unhandled in observable chains

## Quick Start

```typescript
import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { toSignal, toObservable, takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { switchMap, debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-search',
  template: `
    <input (input)="query.set($any($event.target).value)" />
    @for (result of results(); track result.id) {
      <div>{{ result.name }}</div>
    }
  `,
})
export class SearchComponent {
  private readonly http = inject(HttpClient);
  readonly query = signal('');

  readonly results = toSignal(
    toObservable(this.query).pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(q => q ? this.http.get<Result[]>(`/api/search?q=${q}`) : of([])),
    ),
    { initialValue: [] }
  );
}
```

## Fundamental Patterns

### Pattern 1: switchMap for Search-as-You-Type

```typescript
import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { switchMap, debounceTime, distinctUntilChanged, catchError, of, startWith } from 'rxjs';

interface SearchResult {
  id: string;
  name: string;
  description: string;
}

interface SearchState {
  results: SearchResult[];
  loading: boolean;
  error: string | null;
}

@Component({
  selector: 'app-product-search',
  template: `
    <input
      type="text"
      [value]="query()"
      (input)="query.set($any($event.target).value)"
      placeholder="Search products..."
    />

    @if (searchState().loading) {
      <div class="loading">Searching...</div>
    } @else if (searchState().error) {
      <div class="error">{{ searchState().error }}</div>
    } @else {
      @for (result of searchState().results; track result.id) {
        <div class="result">
          <h3>{{ result.name }}</h3>
          <p>{{ result.description }}</p>
        </div>
      } @empty {
        @if (query()) {
          <p>No results found for "{{ query() }}"</p>
        }
      }
    }
  `,
})
export class ProductSearch {
  private readonly http = inject(HttpClient);
  readonly query = signal('');

  // Convert signal to observable, apply RxJS operators, convert back to signal
  readonly searchState = toSignal<SearchState>(
    toObservable(this.query).pipe(
      debounceTime(300),          // Wait 300ms after last keystroke
      distinctUntilChanged(),      // Only emit if value changed
      switchMap(query => {         // Cancel previous request, start new one
        if (!query.trim()) {
          return of<SearchState>({ results: [], loading: false, error: null });
        }
        return this.http.get<SearchResult[]>('/api/search', { params: { q: query } }).pipe(
          map(results => ({ results, loading: false, error: null } as SearchState)),
          startWith({ results: [], loading: true, error: null } as SearchState),
          catchError(err => of<SearchState>({
            results: [],
            loading: false,
            error: 'Search failed. Please try again.',
          })),
        );
      }),
    ),
    { initialValue: { results: [], loading: false, error: null } }
  );
}
```

### Pattern 2: concatMap for Sequential Operations

```typescript
import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject } from 'rxjs';
import { concatMap, takeUntilDestroyed, tap, catchError, of } from 'rxjs';

interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'complete' | 'error';
}

@Component({
  selector: 'app-file-uploader',
  template: `
    <input type="file" multiple (change)="onFilesSelected($event)" />

    @for (upload of uploads(); track upload.file.name) {
      <div class="upload-item">
        <span>{{ upload.file.name }}</span>
        <span class="status">{{ upload.status }}</span>
        @if (upload.status === 'uploading') {
          <progress [value]="upload.progress" max="100"></progress>
        }
      </div>
    }
  `,
})
export class FileUploader {
  private readonly http = inject(HttpClient);
  private readonly uploadQueue$ = new Subject<File>();

  readonly uploads = signal<FileUpload[]>([]);

  constructor() {
    // concatMap: upload files one at a time, in order
    this.uploadQueue$.pipe(
      concatMap(file => {
        this.updateUploadStatus(file.name, 'uploading');

        const formData = new FormData();
        formData.append('file', file);

        return this.http.post('/api/upload', formData, {
          reportProgress: true,
          observe: 'events',
        }).pipe(
          tap(event => {
            if (event.type === HttpEventType.UploadProgress && event.total) {
              const progress = Math.round(100 * event.loaded / event.total);
              this.updateUploadProgress(file.name, progress);
            }
            if (event.type === HttpEventType.Response) {
              this.updateUploadStatus(file.name, 'complete');
            }
          }),
          catchError(() => {
            this.updateUploadStatus(file.name, 'error');
            return of(null); // Continue with next file
          }),
        );
      }),
      takeUntilDestroyed(),
    ).subscribe();
  }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;

    for (const file of Array.from(input.files)) {
      this.uploads.update(uploads => [
        ...uploads,
        { file, progress: 0, status: 'pending' },
      ]);
      this.uploadQueue$.next(file);
    }
  }

  private updateUploadStatus(fileName: string, status: FileUpload['status']): void {
    this.uploads.update(uploads =>
      uploads.map(u => u.file.name === fileName ? { ...u, status } : u)
    );
  }

  private updateUploadProgress(fileName: string, progress: number): void {
    this.uploads.update(uploads =>
      uploads.map(u => u.file.name === fileName ? { ...u, progress } : u)
    );
  }
}
```

### Pattern 3: exhaustMap for Button Click Protection

```typescript
import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject } from 'rxjs';
import { exhaustMap, takeUntilDestroyed, tap, finalize, catchError, of } from 'rxjs';

@Component({
  selector: 'app-checkout',
  template: `
    <div class="order-summary">
      <h2>Order Summary</h2>
      <p>Total: {{ total() | currency }}</p>

      <button
        (click)="placeOrder$.next()"
        [disabled]="submitting()"
      >
        {{ submitting() ? 'Processing...' : 'Place Order' }}
      </button>

      @if (error()) {
        <p class="error">{{ error() }}</p>
      }

      @if (orderConfirmation()) {
        <p class="success">Order #{{ orderConfirmation() }} placed successfully!</p>
      }
    </div>
  `,
})
export class Checkout {
  private readonly http = inject(HttpClient);
  private readonly cartService = inject(CartService);

  readonly total = this.cartService.subtotal;
  readonly submitting = signal(false);
  readonly error = signal<string | null>(null);
  readonly orderConfirmation = signal<string | null>(null);

  // Subject for button clicks
  readonly placeOrder$ = new Subject<void>();

  constructor() {
    // exhaustMap: ignore clicks while order is processing
    this.placeOrder$.pipe(
      tap(() => {
        this.submitting.set(true);
        this.error.set(null);
      }),
      exhaustMap(() =>
        this.http.post<{ orderId: string }>('/api/orders', {
          items: this.cartService.items(),
        }).pipe(
          tap(response => {
            this.orderConfirmation.set(response.orderId);
            this.cartService.clearCart();
          }),
          catchError(err => {
            this.error.set('Failed to place order. Please try again.');
            return of(null);
          }),
          finalize(() => this.submitting.set(false)),
        ),
      ),
      takeUntilDestroyed(),
    ).subscribe();
  }
}
```

### Pattern 4: mergeMap for Concurrent Operations

```typescript
import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { from, mergeMap, toArray, takeUntilDestroyed, tap, finalize } from 'rxjs';

@Component({
  selector: 'app-batch-processor',
  template: `
    <button (click)="processAll()" [disabled]="processing()">
      {{ processing() ? 'Processing...' : 'Process All Items' }}
    </button>
    <p>Progress: {{ completedCount() }} / {{ totalCount() }}</p>
    <progress [value]="completedCount()" [max]="totalCount()"></progress>
  `,
})
export class BatchProcessor {
  private readonly http = inject(HttpClient);

  readonly processing = signal(false);
  readonly completedCount = signal(0);
  readonly totalCount = signal(0);

  processAll(): void {
    const items = ['item-1', 'item-2', 'item-3', 'item-4', 'item-5'];
    this.totalCount.set(items.length);
    this.completedCount.set(0);
    this.processing.set(true);

    // mergeMap with concurrency limit: process 3 at a time
    from(items).pipe(
      mergeMap(
        item => this.http.post(`/api/process/${item}`, {}).pipe(
          tap(() => this.completedCount.update(c => c + 1)),
          catchError(err => {
            console.error(`Failed to process ${item}:`, err);
            this.completedCount.update(c => c + 1); // Count as completed
            return of(null);
          }),
        ),
        3, // concurrency limit
      ),
      toArray(), // Collect all results
      finalize(() => this.processing.set(false)),
      takeUntilDestroyed(),
    ).subscribe(results => {
      console.log('All items processed:', results.filter(Boolean).length, 'successful');
    });
  }
}
```

### Pattern 5: takeUntilDestroyed for Cleanup

```typescript
import { Component, inject, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval, fromEvent, merge } from 'rxjs';
import { map, filter, scan } from 'rxjs';

@Component({
  selector: 'app-activity-monitor',
  template: `
    <p>Active: {{ isActive() }}</p>
    <p>Idle time: {{ idleSeconds() }}s</p>
  `,
})
export class ActivityMonitor {
  readonly isActive = signal(true);
  readonly idleSeconds = signal(0);

  constructor() {
    // PATTERN 1: takeUntilDestroyed() in constructor (no arguments needed)
    interval(1000).pipe(
      takeUntilDestroyed(), // Auto-unsubscribes when component is destroyed
    ).subscribe(() => {
      this.idleSeconds.update(s => s + 1);
    });

    // PATTERN 2: Multiple subscriptions, all auto-cleaned up
    const clicks$ = fromEvent(document, 'click');
    const keydowns$ = fromEvent(document, 'keydown');
    const mouseMoves$ = fromEvent(document, 'mousemove');

    merge(clicks$, keydowns$, mouseMoves$).pipe(
      takeUntilDestroyed(),
    ).subscribe(() => {
      this.isActive.set(true);
      this.idleSeconds.set(0);
    });

    interval(30000).pipe(
      takeUntilDestroyed(),
    ).subscribe(() => {
      if (this.idleSeconds() > 300) {
        this.isActive.set(false);
      }
    });
  }
}

// PATTERN 3: takeUntilDestroyed outside constructor (requires DestroyRef)
@Component({
  selector: 'app-data-poller',
  template: `<p>Data: {{ data() | json }}</p>`,
})
export class DataPoller {
  private readonly destroyRef = inject(DestroyRef);
  private readonly http = inject(HttpClient);
  readonly data = signal<unknown>(null);

  startPolling(): void {
    // Can use takeUntilDestroyed outside constructor by passing DestroyRef
    interval(5000).pipe(
      switchMap(() => this.http.get('/api/data')),
      takeUntilDestroyed(this.destroyRef), // Pass DestroyRef explicitly
    ).subscribe(data => this.data.set(data));
  }
}
```

### Pattern 6: toSignal and toObservable Interop

```typescript
import { Component, inject, signal } from '@angular/core';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { map, switchMap, filter, combineLatest } from 'rxjs';

@Component({
  selector: 'app-user-dashboard',
  template: `
    <h1>Welcome, {{ userName() }}</h1>
    <p>Tab: {{ activeTab() }}</p>
    <p>Notifications: {{ notificationCount() }}</p>
  `,
})
export class UserDashboard {
  private readonly route = inject(ActivatedRoute);
  private readonly http = inject(HttpClient);

  // Observable -> Signal: route params
  readonly userId = toSignal(
    this.route.paramMap.pipe(map(params => params.get('userId'))),
    { initialValue: null }
  );

  // Observable -> Signal: route query params
  readonly activeTab = toSignal(
    this.route.queryParamMap.pipe(map(params => params.get('tab') ?? 'overview')),
    { initialValue: 'overview' }
  );

  // Observable -> Signal: derived HTTP request
  readonly userName = toSignal(
    this.route.paramMap.pipe(
      map(params => params.get('userId')),
      filter((id): id is string => id !== null),
      switchMap(id => this.http.get<{ name: string }>(`/api/users/${id}`)),
      map(user => user.name),
    ),
    { initialValue: 'Loading...' }
  );

  // Signal -> Observable -> Signal: reactive chain
  readonly searchQuery = signal('');

  readonly searchResults = toSignal(
    toObservable(this.searchQuery).pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query =>
        query ? this.http.get<SearchResult[]>('/api/search', { params: { q: query } }) : of([])
      ),
    ),
    { initialValue: [] }
  );

  // Combining multiple observables into a signal
  readonly notificationCount = toSignal(
    combineLatest([
      this.http.get<number>('/api/notifications/count'),
      interval(30000).pipe(
        switchMap(() => this.http.get<number>('/api/notifications/count')),
      ),
    ]).pipe(
      map(([initial, polled]) => polled ?? initial),
    ),
    { initialValue: 0 }
  );
}
```

### Pattern 7: Error Handling Patterns

```typescript
import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, retry, retryWhen, delay, take, throwError, of, timer } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);

  // Pattern 1: catchError with fallback
  getProducts() {
    return this.http.get<Product[]>('/api/products').pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Failed to fetch products:', error.message);
        return of([]); // Return empty array as fallback
      }),
    );
  }

  // Pattern 2: retry with count
  getProductWithRetry(id: string) {
    return this.http.get<Product>(`/api/products/${id}`).pipe(
      retry(3), // Retry up to 3 times on failure
      catchError(error => {
        return throwError(() => new Error(`Failed after 3 retries: ${error.message}`));
      }),
    );
  }

  // Pattern 3: retry with exponential backoff
  getProductWithBackoff(id: string) {
    return this.http.get<Product>(`/api/products/${id}`).pipe(
      retry({
        count: 3,
        delay: (error, retryCount) => {
          // Exponential backoff: 1s, 2s, 4s
          const delayMs = Math.pow(2, retryCount - 1) * 1000;
          console.log(`Retry ${retryCount} after ${delayMs}ms`);
          return timer(delayMs);
        },
        resetOnSuccess: true,
      }),
      catchError(error => {
        return throwError(() => new Error('Service unavailable. Please try again later.'));
      }),
    );
  }

  // Pattern 4: Different handling based on error type
  getUser(id: string) {
    return this.http.get<User>(`/api/users/${id}`).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 404) {
          return throwError(() => new Error('User not found'));
        }
        if (error.status === 403) {
          return throwError(() => new Error('You do not have permission to view this user'));
        }
        if (error.status >= 500) {
          return throwError(() => new Error('Server error. Please try again later.'));
        }
        return throwError(() => new Error('An unexpected error occurred'));
      }),
    );
  }

  // Pattern 5: Error handling with signals
  private readonly _error = signal<string | null>(null);
  readonly error = this._error.asReadonly();

  fetchData() {
    this._error.set(null);
    return this.http.get<Data>('/api/data').pipe(
      catchError(error => {
        this._error.set(error.message ?? 'Failed to fetch data');
        return of(null);
      }),
    );
  }
}
```

### Pattern 8: WebSocket Streams

```typescript
import { Injectable, inject, signal, computed } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { retry, delay, takeUntilDestroyed } from 'rxjs';

interface ChatMessage {
  id: string;
  userId: string;
  text: string;
  timestamp: string;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private socket$: WebSocketSubject<ChatMessage> | null = null;
  private readonly _messages = signal<ChatMessage[]>([]);
  private readonly _connected = signal(false);

  readonly messages = this._messages.asReadonly();
  readonly connected = this._connected.asReadonly();
  readonly messageCount = computed(() => this._messages().length);

  connect(roomId: string): void {
    this.socket$ = webSocket({
      url: `wss://chat.example.com/rooms/${roomId}`,
      openObserver: {
        next: () => this._connected.set(true),
      },
      closeObserver: {
        next: () => this._connected.set(false),
      },
    });

    this.socket$.pipe(
      retry({ delay: 3000 }), // Reconnect on disconnect
    ).subscribe({
      next: (message) => {
        this._messages.update(msgs => [...msgs, message]);
      },
      error: (err) => {
        console.error('WebSocket error:', err);
        this._connected.set(false);
      },
    });
  }

  sendMessage(text: string): void {
    if (this.socket$ && this.connected()) {
      this.socket$.next({
        id: crypto.randomUUID(),
        userId: 'current-user',
        text,
        timestamp: new Date().toISOString(),
      });
    }
  }

  disconnect(): void {
    this.socket$?.complete();
    this.socket$ = null;
    this._connected.set(false);
  }
}
```

## Advanced Patterns

### Pattern 9: Combining Multiple HTTP Requests

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { forkJoin, combineLatest, concat, zip, switchMap, map, toArray } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);

  // forkJoin: wait for ALL requests to complete
  getDashboardData() {
    return forkJoin({
      stats: this.http.get<Stats>('/api/stats'),
      recentOrders: this.http.get<Order[]>('/api/orders/recent'),
      notifications: this.http.get<Notification[]>('/api/notifications'),
      topProducts: this.http.get<Product[]>('/api/products/top'),
    });
    // Result: { stats, recentOrders, notifications, topProducts }
  }

  // combineLatest: emit when ANY source emits (all must have emitted at least once)
  getLiveStats() {
    return combineLatest({
      visitors: interval(5000).pipe(switchMap(() => this.http.get<number>('/api/stats/visitors'))),
      sales: interval(10000).pipe(switchMap(() => this.http.get<number>('/api/stats/sales'))),
    });
  }

  // Sequential dependent requests
  getUserWithPosts(userId: string) {
    return this.http.get<User>(`/api/users/${userId}`).pipe(
      switchMap(user =>
        this.http.get<Post[]>(`/api/users/${userId}/posts`).pipe(
          map(posts => ({ ...user, posts }))
        )
      ),
    );
  }

  // Parallel requests for a list of items
  getProductDetails(productIds: string[]) {
    return from(productIds).pipe(
      mergeMap(
        id => this.http.get<Product>(`/api/products/${id}`),
        5 // max 5 concurrent requests
      ),
      toArray(),
    );
  }
}
```

### Pattern 10: Custom Operators

```typescript
import { Observable, MonoTypeOperatorFunction, pipe } from 'rxjs';
import { tap, retry, catchError, throwError, delay, filter, map } from 'rxjs';

// Custom operator: log with context
export function debug<T>(tag: string): MonoTypeOperatorFunction<T> {
  return pipe(
    tap({
      next: value => console.log(`[${tag}] Next:`, value),
      error: err => console.error(`[${tag}] Error:`, err),
      complete: () => console.log(`[${tag}] Complete`),
    }),
  );
}

// Custom operator: retry with exponential backoff
export function retryWithBackoff<T>(maxRetries: number, baseDelay = 1000): MonoTypeOperatorFunction<T> {
  return pipe(
    retry({
      count: maxRetries,
      delay: (error, retryCount) => {
        const delayMs = baseDelay * Math.pow(2, retryCount - 1);
        console.log(`Retrying (${retryCount}/${maxRetries}) after ${delayMs}ms`);
        return timer(delayMs);
      },
    }),
  );
}

// Custom operator: filter and map (compact)
export function filterMap<T, R>(
  predicate: (value: T) => boolean,
  mapper: (value: T) => R,
) {
  return pipe(
    filter(predicate),
    map(mapper),
  );
}

// Usage
this.http.get<Product[]>('/api/products').pipe(
  debug('products'),
  retryWithBackoff(3),
  filterMap(
    (products: Product[]) => products.length > 0,
    (products: Product[]) => products.map(p => p.name),
  ),
);
```

## Testing Strategies

### Testing Observable Services

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { firstValueFrom } from 'rxjs';
import { DashboardService } from './dashboard.service';

describe('DashboardService', () => {
  let service: DashboardService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(DashboardService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('should fetch dashboard data', async () => {
    const promise = firstValueFrom(service.getDashboardData());

    httpTesting.expectOne('/api/stats').flush({ visitors: 100 });
    httpTesting.expectOne('/api/orders/recent').flush([{ id: '1' }]);
    httpTesting.expectOne('/api/notifications').flush([]);
    httpTesting.expectOne('/api/products/top').flush([{ id: 'p1' }]);

    const result = await promise;
    expect(result.stats).toEqual({ visitors: 100 });
    expect(result.recentOrders).toHaveLength(1);
    expect(result.notifications).toHaveLength(0);
    expect(result.topProducts).toHaveLength(1);
  });

  it('should fetch user with posts', async () => {
    const promise = firstValueFrom(service.getUserWithPosts('user-1'));

    httpTesting.expectOne('/api/users/user-1').flush({ id: 'user-1', name: 'Alice' });
    httpTesting.expectOne('/api/users/user-1/posts').flush([
      { id: 'post-1', title: 'Hello' },
    ]);

    const result = await promise;
    expect(result.name).toBe('Alice');
    expect(result.posts).toHaveLength(1);
  });
});
```

### Testing toSignal Patterns

```typescript
import { TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { Subject, BehaviorSubject } from 'rxjs';

describe('toSignal patterns', () => {
  it('should convert observable to signal', () => {
    TestBed.runInInjectionContext(() => {
      const subject = new BehaviorSubject<string>('initial');
      const sig = toSignal(subject, { requireSync: true });

      expect(sig()).toBe('initial');

      subject.next('updated');
      expect(sig()).toBe('updated');
    });
  });

  it('should handle observable with initialValue', () => {
    TestBed.runInInjectionContext(() => {
      const subject = new Subject<number>();
      const sig = toSignal(subject, { initialValue: 0 });

      expect(sig()).toBe(0);

      subject.next(42);
      expect(sig()).toBe(42);
    });
  });
});
```

## Common Pitfalls

### Pitfall 1: Nested Subscriptions

```typescript
// WRONG: nested subscriptions
this.route.params.subscribe(params => {
  this.userService.getUser(params['id']).subscribe(user => {
    this.postService.getPosts(user.id).subscribe(posts => {
      this.posts = posts;
    });
  });
});

// CORRECT: use flattening operators
this.route.params.pipe(
  map(params => params['id']),
  switchMap(id => this.userService.getUser(id)),
  switchMap(user => this.postService.getPosts(user.id)),
  takeUntilDestroyed(),
).subscribe(posts => this.posts.set(posts));
```

### Pitfall 2: Missing Error Handling

```typescript
// WRONG: unhandled error kills the stream
this.http.get('/api/data').pipe(
  takeUntilDestroyed(),
).subscribe(data => this.data.set(data));

// CORRECT: handle errors
this.http.get('/api/data').pipe(
  catchError(err => {
    this.error.set(err.message);
    return of(null);
  }),
  takeUntilDestroyed(),
).subscribe(data => {
  if (data) this.data.set(data);
});
```

### Pitfall 3: Wrong Flattening Operator

```typescript
// WRONG: mergeMap for search (old requests not cancelled)
toObservable(this.query).pipe(
  mergeMap(q => this.http.get(`/api/search?q=${q}`)),
);

// CORRECT: switchMap cancels previous (latest wins)
toObservable(this.query).pipe(
  switchMap(q => this.http.get(`/api/search?q=${q}`)),
);
```

### Pitfall 4: Memory Leaks from Missing Unsubscribe

```typescript
// WRONG: no cleanup
interval(1000).subscribe(() => this.tick());

// CORRECT: auto-cleanup
interval(1000).pipe(takeUntilDestroyed()).subscribe(() => this.tick());
```

## Best Practices

1. **Use `toSignal()`** to convert observables for template binding instead of async pipe
2. **Always use `takeUntilDestroyed()`** for manual subscriptions
3. **Use `switchMap`** for search/autocomplete (cancel previous)
4. **Use `exhaustMap`** for form submissions (ignore while processing)
5. **Use `concatMap`** for ordered sequential operations
6. **Always handle errors** in observable chains with `catchError`
7. **Use `firstValueFrom()`** when you only need one emission
8. **Prefer signals for state** and RxJS for async streams/events
9. **Create custom operators** for reusable observable transformations
10. **Test with `HttpTestingController`** and `firstValueFrom`

## Resources

- **RxJS Documentation**: https://rxjs.dev
- **Angular RxJS Interop**: https://angular.dev/guide/signals/rxjs-interop
- **Angular HttpClient**: https://angular.dev/guide/http
- **RxJS Operator Decision Tree**: https://rxjs.dev/operator-decision-tree
- **takeUntilDestroyed**: https://angular.dev/api/core/rxjs-interop/takeUntilDestroyed
