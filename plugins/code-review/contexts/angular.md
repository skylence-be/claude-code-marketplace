# Angular Review Rules

Technology-specific review rules for Angular 19+ applications. Loaded when `@angular/core` is detected in `package.json`.

## Detection
- `package.json` contains `@angular/core` in `dependencies`
- `angular.json` exists in project root
- `.component.ts` files in changeset

## Anti-Patterns to Flag

### Missing Subscription Cleanup
Using `.subscribe()` without `takeUntilDestroyed()`, `async` pipe, or manual unsubscribe.
- **Severity:** High (performance)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `.subscribe(...)` in a component without `takeUntilDestroyed(this.destroyRef)` or `| async` in template
- **Fix:** Use `takeUntilDestroyed()` from `@angular/core/rxjs-interop` or convert to `| async` pipe

### Not Using Signals (Angular 19+)
Using BehaviorSubject or plain properties where signals would be more appropriate.
- **Severity:** Low
- **Pattern:** `BehaviorSubject` for simple local state, or `this.property = value` for reactive state
- **Fix:** Use `signal()`, `computed()`, `effect()` for modern Angular reactivity
- **Note:** Only flag in Angular 19+ projects (check `@angular/core` version)

### Missing OnPush Change Detection
Components without `ChangeDetectionStrategy.OnPush` perform unnecessary change detection cycles.
- **Severity:** Medium (performance)
- **Pattern:** `@Component({ ... })` without `changeDetection: ChangeDetectionStrategy.OnPush`
- **Exception:** Root component (`AppComponent`) or components with known Default requirements

### Missing trackBy on Loops
`@for` loops without `track` or `*ngFor` without `trackBy` cause full re-renders on list changes.
- **Severity:** Medium (performance)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `@for (item of items; track $index)` using `$index` instead of unique ID, or `*ngFor` without `trackBy`
- **Fix:** `@for (item of items; track item.id)` — track by a stable unique identifier

### Direct DOM Manipulation
Using `document.querySelector()`, `ElementRef.nativeElement`, or direct DOM APIs instead of Angular's renderer.
- **Severity:** Medium (correctness)
- **Pattern:** `document.querySelector(...)`, `this.elementRef.nativeElement.style.x = ...`
- **Fix:** Use `Renderer2`, signals, or template bindings for DOM updates

### Missing Input Validation on Route Params
Using route parameters directly without validation or type coercion.
- **Severity:** Medium (security)
- **Pattern:** `this.route.params.subscribe(p => this.id = p['id'])` without validation
- **Fix:** Validate and parse: `const id = Number(p['id']); if (isNaN(id)) { ... }`

### Heavy Computation in Templates
Calling methods or performing complex expressions directly in templates without memoization.
- **Severity:** Medium (performance)
- **Pattern:** `{{ calculateTotal(items) }}` in template — recalculates on every change detection
- **Fix:** Use a `computed()` signal or a pipe for memoization

### Barrel File Re-exports
Deep barrel file chains (`index.ts` re-exporting from other `index.ts`) that hurt tree-shaking.
- **Severity:** Low (performance)
- **Pattern:** `export * from './sub-module'` chains 3+ levels deep
- **Fix:** Import directly from the source file, not through barrel files

### Standalone Component in Module AND standalone: true
Declaring a standalone component in an NgModule's `declarations` array.
- **Severity:** High (correctness)
- **Pattern:** Component has `standalone: true` but is also listed in a module's `declarations`
- **Fix:** Remove from `declarations` — standalone components don't belong in modules

### Constructor DI Instead of inject()
Using constructor-based dependency injection instead of the modern `inject()` function.
- **Severity:** Low
- **Pattern:** `constructor(private service: MyService)` in Angular 19+ projects
- **Fix:** `private service = inject(MyService)` — more concise, works with functional guards/resolvers
- **Note:** Only suggest, don't require — both patterns are valid
