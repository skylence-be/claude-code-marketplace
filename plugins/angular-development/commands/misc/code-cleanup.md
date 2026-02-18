---
description: Clean up and refactor Angular code to modern patterns
model: claude-sonnet-4-5
---

Clean up and refactor the following Angular code following modern Angular 21+ best practices.

## Code to Clean

$ARGUMENTS

## Angular Code Cleanup Guide

### 1. **Migrate to Standalone Components**

```typescript
// BEFORE: NgModule-based
@NgModule({
  declarations: [UserListComponent, UserCardComponent],
  imports: [CommonModule, RouterModule],
  exports: [UserListComponent],
})
export class UsersModule {}

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
})
export class UserListComponent {}

// AFTER: Standalone
@Component({
  selector: 'app-user-list',
  imports: [UserCard, RouterLink],
  template: `
    @for (user of users(); track user.id) {
      <app-user-card [user]="user" />
    }
  `,
})
export class UserList {}
```

### 2. **Migrate to Signal Inputs/Outputs**

```typescript
// BEFORE: Decorator-based
@Component({ /* ... */ })
export class UserCard implements OnChanges {
  @Input() user!: User;
  @Input() showActions = true;
  @Output() edit = new EventEmitter<User>();

  ngOnChanges(changes: SimpleChanges) {
    if (changes['user']) {
      this.updateDisplayName();
    }
  }

  private updateDisplayName() {
    this.displayName = `${this.user.firstName} ${this.user.lastName}`;
  }
}

// AFTER: Signal-based
@Component({ /* ... */ })
export class UserCard {
  user = input.required<User>();
  showActions = input(true);
  edit = output<User>();

  // Replaces ngOnChanges -- automatically updates when user() changes
  displayName = computed(() => `${this.user().firstName} ${this.user().lastName}`);
}
```

### 3. **Migrate to New Control Flow**

```html
<!-- BEFORE: Structural directives -->
<div *ngIf="user; else loadingTpl">
  <h2>{{ user.name }}</h2>
  <div *ngFor="let item of items; trackBy: trackById">
    {{ item.name }}
  </div>
</div>
<ng-template #loadingTpl>
  <app-spinner></app-spinner>
</ng-template>

<div [ngSwitch]="status">
  <div *ngSwitchCase="'active'">Active</div>
  <div *ngSwitchCase="'inactive'">Inactive</div>
  <div *ngSwitchDefault>Unknown</div>
</div>

<!-- AFTER: Built-in control flow -->
@if (user()) {
  <h2>{{ user().name }}</h2>
  @for (item of items(); track item.id) {
    {{ item.name }}
  } @empty {
    <p>No items found.</p>
  }
} @else {
  <app-spinner />
}

@switch (status()) {
  @case ('active') { <span>Active</span> }
  @case ('inactive') { <span>Inactive</span> }
  @default { <span>Unknown</span> }
}
```

### 4. **Migrate to `inject()` Function**

```typescript
// BEFORE: Constructor injection
@Component({ /* ... */ })
export class DashboardComponent {
  constructor(
    private userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    @Optional() private analyticsService?: AnalyticsService,
  ) {}
}

// AFTER: inject() function
@Component({ /* ... */ })
export class Dashboard {
  private readonly userService = inject(UserService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly analyticsService = inject(AnalyticsService, { optional: true });
}
```

### 5. **Migrate to Signals from RxJS State**

```typescript
// BEFORE: BehaviorSubject-based state
@Injectable({ providedIn: 'root' })
export class CartService {
  private items$ = new BehaviorSubject<CartItem[]>([]);
  items = this.items$.asObservable();
  itemCount$ = this.items$.pipe(map(items => items.length));

  addItem(item: CartItem) {
    this.items$.next([...this.items$.value, item]);
  }
}

// AFTER: Signal-based state
@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly _items = signal<CartItem[]>([]);
  readonly items = this._items.asReadonly();
  readonly itemCount = computed(() => this._items().length);

  addItem(item: CartItem): void {
    this._items.update(items => [...items, item]);
  }
}
```

### 6. **Replace Template Method Calls with Computed Signals**

```typescript
// BEFORE: Method calls in template (recalculated every change detection cycle)
@Component({
  template: `
    <div>{{ getFullName() }}</div>
    <div>{{ getFormattedPrice() }}</div>
    <div *ngIf="isExpired()">Expired!</div>
  `
})
export class ProductCard {
  @Input() product!: Product;

  getFullName() { return `${this.product.brand} ${this.product.name}`; }
  getFormattedPrice() { return `$${this.product.price.toFixed(2)}`; }
  isExpired() { return new Date(this.product.expiryDate) < new Date(); }
}

// AFTER: Computed signals (memoized, efficient)
@Component({
  template: `
    <div>{{ fullName() }}</div>
    <div>{{ formattedPrice() }}</div>
    @if (isExpired()) { <span>Expired!</span> }
  `
})
export class ProductCard {
  product = input.required<Product>();

  fullName = computed(() => `${this.product().brand} ${this.product().name}`);
  formattedPrice = computed(() => `$${this.product().price.toFixed(2)}`);
  isExpired = computed(() => new Date(this.product().expiryDate) < new Date());
}
```

### 7. **Replace Lifecycle Hooks with Signals and Effects**

```typescript
// BEFORE: ngOnInit, ngOnChanges, ngOnDestroy
@Component({ /* ... */ })
export class DataComponent implements OnInit, OnChanges, OnDestroy {
  @Input() userId!: string;
  private subscription!: Subscription;
  userData: User | null = null;

  ngOnInit() {
    this.loadUser();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['userId']) {
      this.loadUser();
    }
  }

  ngOnDestroy() {
    this.subscription?.unsubscribe();
  }

  private loadUser() {
    this.subscription?.unsubscribe();
    this.subscription = this.userService
      .getUser(this.userId)
      .subscribe(user => this.userData = user);
  }
}

// AFTER: Signals + httpResource (no lifecycle hooks needed)
@Component({ /* ... */ })
export class DataComponent {
  userId = input.required<string>();

  userResource = httpResource<User>(() => `/api/users/${this.userId()}`);
  // Automatically re-fetches when userId changes
  // Automatically cancels previous requests
  // No manual cleanup needed
}
```

### 8. **Clean Up Subscriptions**

```typescript
// BEFORE: Manual subscription management
@Component({ /* ... */ })
export class MyComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.dataService.data$.pipe(takeUntil(this.destroy$)).subscribe(/*...*/);
    this.authService.user$.pipe(takeUntil(this.destroy$)).subscribe(/*...*/);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// AFTER: takeUntilDestroyed (when RxJS is still needed)
@Component({ /* ... */ })
export class MyComponent {
  constructor() {
    this.dataService.data$.pipe(takeUntilDestroyed()).subscribe(/*...*/);
    this.authService.user$.pipe(takeUntilDestroyed()).subscribe(/*...*/);
  }
}

// BEST: Convert to signals (no subscriptions at all)
@Component({ /* ... */ })
export class MyComponent {
  data = toSignal(inject(DataService).data$);
  user = toSignal(inject(AuthService).user$);
}
```

### 9. **Add OnPush Change Detection**

```typescript
// BEFORE: Default change detection
@Component({
  selector: 'app-widget',
  template: `...`,
})
export class WidgetComponent {}

// AFTER: OnPush (stepping stone to zoneless)
@Component({
  selector: 'app-widget',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `...`,
})
export class Widget {}
```

### 10. **Remove Unused Imports and Dead Code**

- Remove unused `import` statements
- Remove commented-out code blocks
- Remove unused variables and methods
- Remove `CommonModule` import when using new control flow syntax
- Remove NgModule files that are no longer needed
- Remove Zone.js polyfill imports for zoneless applications

### 11. **File and Class Naming (2025 Style Guide)**

```
BEFORE:
  user-list.component.ts  -> export class UserListComponent
  auth.service.ts         -> export class AuthService
  auth.guard.ts           -> export class AuthGuard (class-based)
  truncate.pipe.ts        -> export class TruncatePipe

AFTER (2025 style guide):
  user-list.ts            -> export class UserList
  auth.ts                 -> export class AuthService (service suffix optional)
  auth.guard.ts           -> export const authGuard: CanActivateFn (functional)
  truncate.ts             -> export class TruncatePipe (or Truncate)
```

## Cleanup Checklist

**Architecture**
- ✓ Standalone components (no NgModules)
- ✓ Feature-based folder structure
- ✓ Smart/dumb component separation
- ✓ Single responsibility per file

**Signals & Reactivity**
- ✓ `input()` / `output()` instead of `@Input()` / `@Output()`
- ✓ `computed()` instead of method calls in templates
- ✓ `signal()` instead of `BehaviorSubject` for state
- ✓ `toSignal()` for converting remaining observables
- ✓ `httpResource` for HTTP GET data fetching

**Templates**
- ✓ `@if` / `@for` / `@switch` instead of `*ngIf` / `*ngFor` / `*ngSwitch`
- ✓ `track` by unique identifier in `@for`
- ✓ Self-closing tags for void components (`<app-icon />`)
- ✓ No method calls in templates

**Dependency Injection**
- ✓ `inject()` function instead of constructor injection
- ✓ `providedIn: 'root'` for singleton services
- ✓ Functional guards and interceptors

**Change Detection**
- ✓ `ChangeDetectionStrategy.OnPush` on all components
- ✓ Remove Zone.js dependency where possible
- ✓ Use `afterNextRender()` instead of `NgZone` methods

**Code Quality**
- ✓ No `any` types
- ✓ Remove unused imports and dead code
- ✓ Consistent naming conventions
- ✓ Proper error handling with typed errors

Provide specific refactoring recommendations with before/after code examples.
