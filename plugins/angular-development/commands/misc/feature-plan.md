---
description: Plan and architect a new feature for an Angular application
model: claude-sonnet-4-5
---

Plan and architect a new feature for an Angular 21+ application.

## Feature Description

$ARGUMENTS

## Feature Planning Framework

### 1. **Feature Overview**

Summarize the feature:
- **Purpose**: What problem does this feature solve?
- **Users**: Who will use this feature?
- **Scope**: What is included and explicitly excluded?
- **Dependencies**: What existing features or services does it depend on?

### 2. **Data Model Design**

Define TypeScript interfaces and types:

```typescript
// Example: E-commerce order feature
interface Order {
  id: string;
  customerId: string;
  items: OrderItem[];
  status: OrderStatus;
  total: number;
  createdAt: Date;
  updatedAt: Date;
}

interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
}

type OrderStatus = 'draft' | 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';

interface CreateOrderDto {
  customerId: string;
  items: Array<{ productId: string; quantity: number }>;
}

interface OrderFilters {
  status?: OrderStatus;
  dateFrom?: Date;
  dateTo?: Date;
  search?: string;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}
```

### 3. **Component Architecture**

Design the component tree using smart/dumb separation:

```
Feature Root (smart)
├── Feature Layout
│   ├── Feature Header (dumb)
│   ├── Feature Sidebar / Filters (dumb)
│   └── Feature Content Area
│       ├── List View (smart)
│       │   ├── List Item Card (dumb)
│       │   ├── Empty State (dumb)
│       │   └── Pagination (dumb)
│       └── Detail View (smart)
│           ├── Detail Header (dumb)
│           ├── Detail Content (dumb)
│           └── Detail Actions (dumb)
```

**Smart Components (containers):**
- Inject services and stores
- Manage data fetching with `httpResource`
- Handle user actions and delegate to stores
- No complex template logic

**Dumb Components (presentational):**
- Receive data via `input()` signals
- Emit events via `output()`
- No injected services
- Pure rendering logic with `computed()`

### 4. **Service & Store Design**

```typescript
// Feature store for state management
@Injectable({ providedIn: 'root' })
export class OrderStore {
  private readonly http = inject(HttpClient);

  // State
  private readonly _orders = signal<Order[]>([]);
  private readonly _selectedId = signal<string | null>(null);
  private readonly _filters = signal<OrderFilters>({});
  private readonly _page = signal(1);
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);

  // Selectors
  readonly orders = this._orders.asReadonly();
  readonly selectedOrder = computed(() => { /* ... */ });
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  // Actions
  async loadOrders(): Promise<void> { /* ... */ }
  async createOrder(dto: CreateOrderDto): Promise<void> { /* ... */ }
  async updateStatus(id: string, status: OrderStatus): Promise<void> { /* ... */ }
  select(id: string | null): void { /* ... */ }
  setFilters(filters: OrderFilters): void { /* ... */ }
}

// Feature-specific HTTP service (if needed separately from store)
@Injectable({ providedIn: 'root' })
export class OrderApi {
  private readonly http = inject(HttpClient);

  getAll(params: OrderFilters & { page: number }): Observable<PaginatedResponse<Order>> { /* ... */ }
  getById(id: string): Observable<Order> { /* ... */ }
  create(dto: CreateOrderDto): Observable<Order> { /* ... */ }
  updateStatus(id: string, status: OrderStatus): Observable<Order> { /* ... */ }
  delete(id: string): Observable<void> { /* ... */ }
}
```

### 5. **Route Configuration**

```typescript
// features/orders/orders.routes.ts
export const ORDERS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./order-list').then(m => m.OrderList),
    title: 'Orders',
  },
  {
    path: 'new',
    loadComponent: () => import('./order-create').then(m => m.OrderCreate),
    title: 'New Order',
    canActivate: [authGuard],
    canDeactivate: [unsavedChangesGuard],
  },
  {
    path: ':id',
    loadComponent: () => import('./order-detail').then(m => m.OrderDetail),
    resolve: { order: orderResolver },
    title: orderTitleResolver,
    children: [
      { path: '', redirectTo: 'overview', pathMatch: 'full' },
      {
        path: 'overview',
        loadComponent: () => import('./order-overview').then(m => m.OrderOverview),
      },
      {
        path: 'history',
        loadComponent: () => import('./order-history').then(m => m.OrderHistory),
      },
    ],
  },
];

// Register in app.routes.ts
{
  path: 'orders',
  loadChildren: () => import('./features/orders/orders.routes').then(m => m.ORDERS_ROUTES),
  canActivate: [authGuard],
}
```

### 6. **File Structure**

```
src/app/features/orders/
├── orders.routes.ts              # Route configuration
├── order-list.ts                 # Smart: list page component
├── order-detail.ts               # Smart: detail page component
├── order-create.ts               # Smart: create form component
├── components/
│   ├── order-card.ts             # Dumb: single order display
│   ├── order-filters.ts          # Dumb: filter controls
│   ├── order-status-badge.ts     # Dumb: status display
│   └── order-form.ts             # Dumb: order form fields
├── services/
│   ├── order.store.ts            # Signal-based state store
│   └── order.api.ts              # HTTP service
├── guards/
│   └── order-access.guard.ts     # Feature-specific guard
├── resolvers/
│   └── order.resolver.ts         # Route resolver
└── models/
    ├── order.model.ts            # TypeScript interfaces
    └── order-status.ts           # Status enum/type
```

### 7. **Error Handling Strategy**

```typescript
// Component-level error handling
@Component({
  template: `
    @if (store.loading()) {
      <app-skeleton />
    } @else if (store.error()) {
      <app-error-state
        [message]="store.error()"
        (retry)="store.loadOrders()" />
    } @else if (store.orders().length === 0) {
      <app-empty-state
        title="No orders yet"
        description="Create your first order to get started."
        actionLabel="Create Order"
        (action)="navigateToCreate()" />
    } @else {
      @for (order of store.orders(); track order.id) {
        <app-order-card [order]="order" (click)="onSelect(order.id)" />
      }
    }
  `
})
```

### 8. **Forms Design**

```typescript
// Typed reactive form
@Component({ /* ... */ })
export class OrderCreate {
  private readonly fb = inject(FormBuilder);
  private readonly store = inject(OrderStore);
  private readonly router = inject(Router);

  form = this.fb.group({
    customerId: ['', [Validators.required]],
    items: this.fb.array<FormGroup<{
      productId: FormControl<string>;
      quantity: FormControl<number>;
    }>>([]),
    notes: [''],
  });

  addItem(): void {
    this.form.controls.items.push(
      this.fb.group({
        productId: ['', Validators.required],
        quantity: [1, [Validators.required, Validators.min(1)]],
      })
    );
  }

  async onSubmit(): Promise<void> {
    if (this.form.valid) {
      await this.store.createOrder(this.form.getRawValue());
      this.router.navigate(['/orders']);
    }
  }

  // For unsaved changes guard
  hasUnsavedChanges(): boolean {
    return this.form.dirty;
  }
}
```

### 9. **Accessibility Plan**

- **Keyboard Navigation**: All interactive elements reachable via Tab; actions triggered with Enter/Space
- **ARIA Labels**: Dynamic content announces changes with `aria-live`; form errors linked with `aria-describedby`
- **Focus Management**: Focus moves to new content after navigation; focus trapped in modals/dialogs
- **Semantic HTML**: Use `<main>`, `<nav>`, `<article>`, `<section>`, headings hierarchy
- **Color Contrast**: Status badges meet WCAG AA contrast requirements
- **Screen Reader**: Status changes announced; loading states communicated

### 10. **Performance Considerations**

- **Lazy Loading**: Feature routes loaded on demand
- **`@defer`**: Heavy components (charts, maps, rich editors) deferred until viewport/interaction
- **Virtual Scrolling**: If lists can exceed 100 items, use `cdk-virtual-scroll-viewport`
- **Image Optimization**: Use `NgOptimizedImage` for all images
- **Bundle Budget**: Monitor feature chunk size; target < 100KB per lazy chunk

### 11. **Testing Strategy**

```typescript
// Store tests
describe('OrderStore', () => {
  it('should load orders and update state', async () => { /* ... */ });
  it('should handle loading errors', async () => { /* ... */ });
  it('should filter orders by status', () => { /* ... */ });
  it('should compute selected order from ID', () => { /* ... */ });
});

// Component tests
describe('OrderList', () => {
  it('should display orders from store', async () => { /* ... */ });
  it('should show empty state when no orders', async () => { /* ... */ });
  it('should navigate to detail on card click', async () => { /* ... */ });
});

// Guard tests
describe('orderAccessGuard', () => {
  it('should allow access for authenticated users', () => { /* ... */ });
  it('should redirect to login for unauthenticated users', () => { /* ... */ });
});
```

### 12. **Implementation Phases**

**Phase 1: Foundation (Day 1)**
- [ ] Define data models and interfaces
- [ ] Create store service with signal state
- [ ] Create API service with HTTP methods
- [ ] Set up route configuration

**Phase 2: List View (Day 2)**
- [ ] Build order card (dumb) component
- [ ] Build order filters (dumb) component
- [ ] Build order list page (smart) component
- [ ] Implement pagination

**Phase 3: Detail View (Day 3)**
- [ ] Build order detail page (smart) component
- [ ] Build status badge component
- [ ] Build order history component
- [ ] Implement resolver for data pre-fetching

**Phase 4: Create/Edit (Day 4)**
- [ ] Build order form component with validation
- [ ] Implement unsaved changes guard
- [ ] Connect form submission to store

**Phase 5: Polish (Day 5)**
- [ ] Error handling and error states
- [ ] Loading states and skeletons
- [ ] Accessibility audit and fixes
- [ ] Write unit tests
- [ ] Performance audit (`@defer`, lazy loading, bundle size)

## Feature Checklist

**Architecture**
- ✓ Feature-based folder structure
- ✓ Smart/dumb component separation
- ✓ Signal-based store for state management
- ✓ Lazy loaded routes

**Angular 21+ Patterns**
- ✓ Standalone components throughout
- ✓ Signal inputs/outputs
- ✓ New control flow syntax
- ✓ `inject()` function
- ✓ `OnPush` change detection
- ✓ Functional guards and resolvers

**Quality**
- ✓ TypeScript strict mode (no `any`)
- ✓ Comprehensive error handling
- ✓ Loading and empty states
- ✓ Accessibility (ARIA, keyboard, screen reader)
- ✓ Unit tests for stores, guards, and components
- ✓ Performance optimized (`@defer`, lazy loading, virtual scrolling)

Provide a complete, actionable feature plan that follows Angular 21+ best practices throughout.
