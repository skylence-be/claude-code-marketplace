---
description: Generate a signal-based store service with computed(), effect(), and readonly patterns
model: claude-sonnet-4-5
---

Create a new Angular signal-based store service following modern Angular 21+ best practices.

## Store Specification

$ARGUMENTS

## Angular 21+ Signal Store Standards

### 1. **Basic Signal Store**

```typescript
import { Injectable, signal, computed } from '@angular/core';

interface TodoItem {
  id: string;
  title: string;
  completed: boolean;
  createdAt: Date;
}

type TodoFilter = 'all' | 'active' | 'completed';

@Injectable({ providedIn: 'root' })
export class TodoStore {
  // Private writable state
  private readonly _todos = signal<TodoItem[]>([]);
  private readonly _filter = signal<TodoFilter>('all');
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);

  // Public read-only state
  readonly todos = this._todos.asReadonly();
  readonly filter = this._filter.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  // Computed derived state
  readonly filteredTodos = computed(() => {
    const todos = this._todos();
    const filter = this._filter();

    switch (filter) {
      case 'active': return todos.filter(t => !t.completed);
      case 'completed': return todos.filter(t => t.completed);
      default: return todos;
    }
  });

  readonly activeCount = computed(() =>
    this._todos().filter(t => !t.completed).length
  );

  readonly completedCount = computed(() =>
    this._todos().filter(t => t.completed).length
  );

  readonly allCompleted = computed(() =>
    this._todos().length > 0 && this._todos().every(t => t.completed)
  );

  // Actions
  addTodo(title: string): void {
    const newTodo: TodoItem = {
      id: crypto.randomUUID(),
      title: title.trim(),
      completed: false,
      createdAt: new Date(),
    };
    this._todos.update(todos => [...todos, newTodo]);
  }

  toggleTodo(id: string): void {
    this._todos.update(todos =>
      todos.map(t => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  }

  removeTodo(id: string): void {
    this._todos.update(todos => todos.filter(t => t.id !== id));
  }

  setFilter(filter: TodoFilter): void {
    this._filter.set(filter);
  }

  clearCompleted(): void {
    this._todos.update(todos => todos.filter(t => !t.completed));
  }
}
```

### 2. **Entity Store with CRUD Operations**

```typescript
interface EntityState<T extends { id: string }> {
  entities: T[];
  selectedId: string | null;
  loading: boolean;
  error: string | null;
}

@Injectable({ providedIn: 'root' })
export class ProductStore {
  private readonly http = inject(HttpClient);

  // State signals
  private readonly _products = signal<Product[]>([]);
  private readonly _selectedId = signal<string | null>(null);
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);

  // Public read-only state
  readonly products = this._products.asReadonly();
  readonly selectedId = this._selectedId.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  // Computed selectors
  readonly selectedProduct = computed(() => {
    const id = this._selectedId();
    return id ? this._products().find(p => p.id === id) ?? null : null;
  });

  readonly productCount = computed(() => this._products().length);

  readonly productsByCategory = computed(() => {
    const grouped = new Map<string, Product[]>();
    for (const product of this._products()) {
      const list = grouped.get(product.category) ?? [];
      list.push(product);
      grouped.set(product.category, list);
    }
    return grouped;
  });

  // Async actions
  async loadAll(): Promise<void> {
    this._loading.set(true);
    this._error.set(null);

    try {
      const products = await firstValueFrom(
        this.http.get<Product[]>('/api/products')
      );
      this._products.set(products);
    } catch (e) {
      this._error.set('Failed to load products');
    } finally {
      this._loading.set(false);
    }
  }

  async create(dto: CreateProductDto): Promise<Product | null> {
    this._loading.set(true);
    this._error.set(null);

    try {
      const product = await firstValueFrom(
        this.http.post<Product>('/api/products', dto)
      );
      this._products.update(list => [...list, product]);
      return product;
    } catch (e) {
      this._error.set('Failed to create product');
      return null;
    } finally {
      this._loading.set(false);
    }
  }

  async update(id: string, dto: UpdateProductDto): Promise<void> {
    this._loading.set(true);
    this._error.set(null);

    try {
      const updated = await firstValueFrom(
        this.http.put<Product>(`/api/products/${id}`, dto)
      );
      this._products.update(list =>
        list.map(p => (p.id === id ? updated : p))
      );
    } catch (e) {
      this._error.set('Failed to update product');
    } finally {
      this._loading.set(false);
    }
  }

  async delete(id: string): Promise<void> {
    this._loading.set(true);
    this._error.set(null);

    try {
      await firstValueFrom(this.http.delete(`/api/products/${id}`));
      this._products.update(list => list.filter(p => p.id !== id));
      if (this._selectedId() === id) {
        this._selectedId.set(null);
      }
    } catch (e) {
      this._error.set('Failed to delete product');
    } finally {
      this._loading.set(false);
    }
  }

  select(id: string | null): void {
    this._selectedId.set(id);
  }
}
```

### 3. **Store with Pagination and Search**

```typescript
@Injectable({ providedIn: 'root' })
export class UserStore {
  private readonly http = inject(HttpClient);

  // State
  private readonly _users = signal<User[]>([]);
  private readonly _total = signal(0);
  private readonly _page = signal(1);
  private readonly _pageSize = signal(20);
  private readonly _search = signal('');
  private readonly _sortField = signal<keyof User>('name');
  private readonly _sortDirection = signal<'asc' | 'desc'>('asc');
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);

  // Read-only public state
  readonly users = this._users.asReadonly();
  readonly total = this._total.asReadonly();
  readonly page = this._page.asReadonly();
  readonly pageSize = this._pageSize.asReadonly();
  readonly search = this._search.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();

  // Derived state
  readonly totalPages = computed(() =>
    Math.ceil(this._total() / this._pageSize())
  );
  readonly hasNextPage = computed(() => this._page() < this.totalPages());
  readonly hasPreviousPage = computed(() => this._page() > 1);
  readonly isEmpty = computed(() => this._users().length === 0 && !this._loading());

  // Reset page when search changes
  readonly currentPage = linkedSignal(() => {
    this._search();
    return 1;
  });

  constructor() {
    // Auto-fetch when search, page, or sort changes
    effect(() => {
      const search = this._search();
      const page = this.currentPage();
      const pageSize = this._pageSize();
      const sort = this._sortField();
      const dir = this._sortDirection();

      // Use untracked to avoid recursive tracking
      untracked(() => this.fetchUsers(search, page, pageSize, sort, dir));
    });
  }

  private async fetchUsers(
    search: string,
    page: number,
    pageSize: number,
    sort: keyof User,
    direction: 'asc' | 'desc'
  ): Promise<void> {
    this._loading.set(true);
    this._error.set(null);

    try {
      const response = await firstValueFrom(
        this.http.get<PaginatedResponse<User>>('/api/users', {
          params: {
            q: search,
            page: page.toString(),
            limit: pageSize.toString(),
            sort,
            direction,
          },
        })
      );
      this._users.set(response.data);
      this._total.set(response.total);
    } catch {
      this._error.set('Failed to load users');
    } finally {
      this._loading.set(false);
    }
  }

  setSearch(query: string): void {
    this._search.set(query);
  }

  setPage(page: number): void {
    this.currentPage.set(page);
  }

  nextPage(): void {
    if (this.hasNextPage()) {
      this.currentPage.update(p => p + 1);
    }
  }

  previousPage(): void {
    if (this.hasPreviousPage()) {
      this.currentPage.update(p => p - 1);
    }
  }

  setSort(field: keyof User, direction: 'asc' | 'desc'): void {
    this._sortField.set(field);
    this._sortDirection.set(direction);
  }
}
```

### 4. **Store with Persistence (localStorage)**

```typescript
@Injectable({ providedIn: 'root' })
export class PreferencesStore {
  // State with initial values from localStorage
  private readonly _theme = signal<'light' | 'dark'>(
    this.load('theme', 'light')
  );
  private readonly _language = signal<string>(
    this.load('language', 'en')
  );
  private readonly _sidebarCollapsed = signal<boolean>(
    this.load('sidebarCollapsed', false)
  );

  // Public read-only state
  readonly theme = this._theme.asReadonly();
  readonly language = this._language.asReadonly();
  readonly sidebarCollapsed = this._sidebarCollapsed.asReadonly();

  // Computed
  readonly isDark = computed(() => this._theme() === 'dark');

  constructor() {
    // Persist changes to localStorage
    effect(() => this.save('theme', this._theme()));
    effect(() => this.save('language', this._language()));
    effect(() => this.save('sidebarCollapsed', this._sidebarCollapsed()));
  }

  setTheme(theme: 'light' | 'dark'): void {
    this._theme.set(theme);
  }

  toggleTheme(): void {
    this._theme.update(t => (t === 'light' ? 'dark' : 'light'));
  }

  setLanguage(lang: string): void {
    this._language.set(lang);
  }

  toggleSidebar(): void {
    this._sidebarCollapsed.update(v => !v);
  }

  private load<T>(key: string, fallback: T): T {
    try {
      const stored = localStorage.getItem(`prefs:${key}`);
      return stored ? JSON.parse(stored) : fallback;
    } catch {
      return fallback;
    }
  }

  private save<T>(key: string, value: T): void {
    localStorage.setItem(`prefs:${key}`, JSON.stringify(value));
  }
}
```

### 5. **Store with httpResource Integration**

```typescript
@Injectable({ providedIn: 'root' })
export class NotificationStore {
  private readonly _page = signal(1);
  private readonly _unreadOnly = signal(false);

  // httpResource automatically fetches when signals change
  readonly notifications = httpResource<PaginatedResponse<Notification>>(() => ({
    url: '/api/notifications',
    params: {
      page: this._page().toString(),
      unread: this._unreadOnly().toString(),
    },
  }));

  readonly unreadCount = httpResource<{ count: number }>(() => '/api/notifications/unread-count');

  // Derived state from resources
  readonly items = computed(() => this.notifications.value()?.data ?? []);
  readonly total = computed(() => this.notifications.value()?.total ?? 0);
  readonly badge = computed(() => this.unreadCount.value()?.count ?? 0);

  setPage(page: number): void {
    this._page.set(page);
  }

  toggleUnreadFilter(): void {
    this._unreadOnly.update(v => !v);
  }
}
```

### 6. **Using the Store in Components**

```typescript
@Component({
  selector: 'app-todo-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [FormsModule],
  template: `
    <h1>Todos</h1>

    <form (ngSubmit)="addTodo()">
      <input [(ngModel)]="newTitle" name="title" placeholder="What needs to be done?" />
      <button type="submit" [disabled]="!newTitle.trim()">Add</button>
    </form>

    <nav>
      <button (click)="store.setFilter('all')" [class.active]="store.filter() === 'all'">
        All
      </button>
      <button (click)="store.setFilter('active')" [class.active]="store.filter() === 'active'">
        Active ({{ store.activeCount() }})
      </button>
      <button (click)="store.setFilter('completed')" [class.active]="store.filter() === 'completed'">
        Completed ({{ store.completedCount() }})
      </button>
    </nav>

    @for (todo of store.filteredTodos(); track todo.id) {
      <div class="todo-item">
        <input type="checkbox" [checked]="todo.completed" (change)="store.toggleTodo(todo.id)" />
        <span [class.completed]="todo.completed">{{ todo.title }}</span>
        <button (click)="store.removeTodo(todo.id)" aria-label="Remove todo">X</button>
      </div>
    } @empty {
      <p>No todos found.</p>
    }

    @if (store.completedCount() > 0) {
      <button (click)="store.clearCompleted()">Clear completed</button>
    }
  `
})
export class TodoPage {
  readonly store = inject(TodoStore);
  newTitle = '';

  addTodo(): void {
    if (this.newTitle.trim()) {
      this.store.addTodo(this.newTitle);
      this.newTitle = '';
    }
  }
}
```

## Best Practices

**Store Design**
- ✓ Private writable `signal()` for state (prefixed with `_`)
- ✓ Public `asReadonly()` for external consumption
- ✓ `computed()` for all derived/filtered/aggregated state
- ✓ Named action methods for all state mutations
- ✓ Single Responsibility -- one store per domain entity or feature

**State Immutability**
- ✓ Use `update()` with spread operators for immutable updates
- ✓ Never mutate signal values directly (e.g., no `array.push()`)
- ✓ Return new references from update functions
- ✓ Use `linkedSignal()` for dependent state that resets

**Async Operations**
- ✓ Track `loading` and `error` state for all async operations
- ✓ Use try/catch/finally for error handling
- ✓ Set loading to false in `finally` block
- ✓ Clear errors before new operations start

**TypeScript**
- ✓ Define interfaces for all state shapes and DTOs
- ✓ Type all signals explicitly
- ✓ No `any` types
- ✓ Use generics for reusable store patterns

**Performance**
- ✓ `computed()` signals are memoized -- use them freely
- ✓ Use `untracked()` to prevent unwanted dependencies in effects
- ✓ Prefer `httpResource` for declarative reactive data fetching
- ✓ Minimize the number of `effect()` calls; prefer declarative patterns

Generate production-ready, type-safe Angular signal-based store services.
