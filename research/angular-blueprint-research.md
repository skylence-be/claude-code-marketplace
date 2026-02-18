# Angular Blueprint Best Practices Research

> Compiled from official Angular documentation, Angular blog announcements, and community best practices (February 2026)

## Table of Contents

1. [Angular Version History and Current State](#1-angular-version-history-and-current-state)
2. [Signals and Reactive Primitives](#2-signals-and-reactive-primitives)
3. [Standalone Components](#3-standalone-components)
4. [New Control Flow Syntax](#4-new-control-flow-syntax)
5. [Zoneless Change Detection](#5-zoneless-change-detection)
6. [Server-Side Rendering and Hydration](#6-server-side-rendering-and-hydration)
7. [Resource API and httpResource](#7-resource-api-and-httpresource)
8. [Project Structure and File Conventions](#8-project-structure-and-file-conventions)
9. [Angular Style Guide (2025 Update)](#9-angular-style-guide-2025-update)
10. [Dependency Injection Best Practices](#10-dependency-injection-best-practices)
11. [Routing and Lazy Loading](#11-routing-and-lazy-loading)
12. [Performance Best Practices](#12-performance-best-practices)
13. [Testing Best Practices](#13-testing-best-practices)
14. [Angular CLI Commands and Configuration](#14-angular-cli-commands-and-configuration)
15. [Common Patterns and Anti-Patterns](#15-common-patterns-and-anti-patterns)
16. [Angular 20 and 21 Feature Summary](#16-angular-20-and-21-feature-summary)

---

## 1. Angular Version History and Current State

### Release Timeline

| Version | Release Date | Key Milestone |
|---------|-------------|---------------|
| Angular 17 | November 2023 | New control flow syntax, deferrable views, new logo/brand |
| Angular 18 | May 2024 | Experimental zoneless, stable control flow |
| Angular 19 | November 2024 | Standalone default, linkedSignal, resource API, incremental hydration |
| Angular 19.2 | March 2025 | httpResource, rxResource streaming |
| Angular 20 | May 2025 | Stable signals/effects/linkedSignal, zoneless developer preview, template literals |
| Angular 21 | November 2025 | Signal forms (experimental), zoneless by default, Vitest default, Angular Aria |

### Current Recommended Version

Angular 21 is the latest stable release (as of February 2026). New projects should target Angular 21 with zoneless change detection (now the default). Angular follows semantic versioning with major releases every 6 months.

### Support Policy

- **Active Support**: 18 months from release
- **Long-Term Support (LTS)**: 18 months after active support ends
- Angular 19 remains in active support; Angular 18 is in LTS

Sources:
- [Angular Versioning and Releases](https://angular.dev/reference/releases)
- [Angular 19.2 Announcement](https://blog.angular.dev/angular-19-2-is-now-available-673ec70aea12)
- [Angular Roadmap](https://angular.dev/roadmap)

---

## 2. Signals and Reactive Primitives

### Overview

Signals are Angular's next-generation reactivity model, providing fine-grained reactive state management. As of Angular 20, all fundamental signal APIs are **stable and production-ready**: `signal()`, `computed()`, `effect()`, `linkedSignal()`, signal-based queries, and signal-based inputs.

### Writable Signals

```typescript
import { signal } from '@angular/core';

// Create a writable signal with an initial value
const count = signal(0);

// Read the value by calling the signal as a getter
console.log('The count is: ' + count());

// Set a new value directly
count.set(3);

// Update based on the previous value
count.update(value => value + 1);
```

### Read-Only Signals with `asReadonly()`

```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  private _currentUser = signal<User | null>(null);

  // Expose read-only version publicly
  readonly currentUser = this._currentUser.asReadonly();

  setUser(user: User) {
    this._currentUser.set(user);
  }
}
```

### Computed Signals

Derived, read-only signals that automatically update when dependencies change. They are lazily evaluated and memoized.

```typescript
const count = signal(0);
const doubleCount = computed(() => count() * 2);

// Dependencies are tracked dynamically at runtime
const showCount = signal(false);
const conditionalCount = computed(() => {
  if (showCount()) {
    return `The count is ${count()}`;
  } else {
    return 'Nothing to see here';
  }
});
```

### Effects

Effects run side-effect code whenever one or more signals change. As of Angular 20, `effect()` is stable.

```typescript
effect(() => {
  console.log(`The current user is: ${currentUser()}`);
});
```

### linkedSignal

A writable signal that resets when a source signal changes. Stable as of Angular 20.

```typescript
const options = signal(['apple', 'banana', 'cherry']);
const selectedOption = linkedSignal(() => options()[0]);

// selectedOption resets to options()[0] whenever options changes
// But it can also be manually set:
selectedOption.set('banana');
```

### Signal Best Practices

1. **Use `computed()` for derived state**: Make code more declarative; never modify variables or DOM inside `computed()`
2. **Do not make async calls in `computed()`**: Signals are strictly synchronous -- no `setTimeout()`, Promises, or HTTP calls
3. **Use signals in templates instead of observables**: Signals schedule change detection without pipes, are glitch-free, and multiple reads of the same signal are "free"
4. **Minimize `effect()` usage**: Angular discourages overuse; prefer declarative patterns with `computed()` and `linkedSignal()`
5. **Use `untracked()` for reads that should not create dependencies**:
   ```typescript
   effect(() => {
     const user = currentUser();
     untracked(() => {
       this.loggingService.log(`User set to ${user}`);
     });
   });
   ```
6. **Avoid custom equality functions** unless you have a specific need; the default equality check works for most cases
7. **Be aware of deep mutation**: Read-only signals do not prevent deep mutation of their values; use defensive copying for complex objects when needed

### Converting Between Signals and Observables

As of Angular 20, `toSignal()` and `toObservable()` are stable:

```typescript
import { toSignal, toObservable } from '@angular/core/rxjs-interop';

// Observable to Signal
const data = toSignal(this.dataService.getData$());

// Signal to Observable
const count$ = toObservable(this.count);
```

Sources:
- [Angular Signals Overview](https://angular.dev/guide/signals)
- [Angular Signals Best Practices (Medium)](https://medium.com/@eugeniyoz/angular-signals-best-practices-9ac837ab1cec)
- [Angular Signals Guide (angular-university.io)](https://blog.angular-university.io/angular-signals/)

---

## 3. Standalone Components

### Overview

As of Angular 19, `standalone: true` is the **default** for components, directives, and pipes. NgModules are no longer required for new code. Angular 20+ fully embraces standalone components as the standard.

### Creating Standalone Components

```typescript
// Angular 19+: standalone is the default (no need to specify)
@Component({
  selector: 'app-user-profile',
  imports: [CommonModule, RouterLink],
  template: `
    <h2>{{ user().name }}</h2>
    <a routerLink="/settings">Settings</a>
  `,
  styles: [`h2 { color: #333; }`]
})
export class UserProfileComponent {
  user = input.required<User>();
}
```

### Standalone Application Bootstrapping

```typescript
// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

bootstrapApplication(AppComponent, appConfig);
```

```typescript
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
  ]
};
```

### Standalone Best Practices

1. **All new code should be standalone** (module-free) from 2025 onward
2. **Import only what you need** in each component to optimize bundle size
3. **Organize by feature** -- group related components, directives, and pipes in feature folders
4. **Use barrel files (`index.ts`)** to manage exports and simplify imports
5. **Leverage tree-shaking**: Standalone components enable more effective tree-shaking and lazy loading
6. **Incremental migration**: You can mix standalone and NgModule-based components during migration
7. **Prefer `providedIn: 'root'` for services** instead of adding to component-level providers

### Migration from NgModules

Angular provides automated migration schematics:

```bash
ng generate @angular/core:standalone
```

Sources:
- [The Future is Standalone (Angular Blog)](https://blog.angular.dev/the-future-is-standalone-475d7edbc706)
- [Angular 2025 Guide: Mastering Standalone Components](https://www.ismaelramos.dev/blog/angular-2025-guide-mastering-standalone-components/)
- [Angular 19 Standalone Components (Syncfusion)](https://www.syncfusion.com/blogs/post/angular19-standalone-components)

---

## 4. New Control Flow Syntax

### Overview

Angular's built-in control flow (introduced in v17, stable in v18+) replaces structural directives (`*ngIf`, `*ngFor`, `*ngSwitch`) with `@if`, `@for`, and `@switch` blocks. These are built into the template compiler -- no imports needed (not even `CommonModule`).

### @if / @else if / @else

```html
@if (user) {
  <h1>Welcome, {{ user.name }}</h1>
} @else if (isLoading) {
  <app-spinner />
} @else {
  <p>Please log in.</p>
}
```

**Capturing expression results with `as`:**

```html
@if (user$ | async; as user) {
  <app-user-card [user]="user" />
}
```

### @for with track

```html
@for (item of items; track item.id) {
  <app-item-card [item]="item" />
} @empty {
  <p>No items found.</p>
}
```

**Built-in contextual variables:**

| Variable | Purpose |
|----------|---------|
| `$count` | Total items in collection |
| `$index` | Current iteration position |
| `$first` | True for first item |
| `$last` | True for final item |
| `$even` | True when index is even |
| `$odd` | True when index is odd |

**Aliasing variables:**

```html
@for (item of items; track item.id; let idx = $index, isEven = $even) {
  <div [class.even]="isEven">{{ idx }}: {{ item.name }}</div>
}
```

### @switch / @case / @default

```html
@switch (userRole) {
  @case ('admin') {
    <app-admin-dashboard />
  }
  @case ('editor') {
    <app-editor-dashboard />
  }
  @default {
    <app-viewer-dashboard />
  }
}
```

Key characteristics:
- Uses triple-equals (`===`) comparison
- No fallthrough behavior (no `break` needed)
- `@default` block is optional

### Control Flow Best Practices

1. **Always provide a meaningful `track` expression**: Use unique identifiers (`id`, `uuid`); avoid tracking by object reference
2. **Use `$index` for static collections** only when items do not have unique IDs
3. **Use `@empty` blocks** for user-friendly empty state messages
4. **Prefer `@switch` over chained `@else if`** when dealing with more than 2-3 conditions
5. **Migrate from structural directives**: Use `ng generate @angular/core:control-flow` to automate migration

### Migration Schematic

```bash
# Migrate existing templates from *ngIf/*ngFor/*ngSwitch to @if/@for/@switch
ng generate @angular/core:control-flow
```

In Angular 21, the control flow migration runs automatically during `ng update`.

Sources:
- [Angular Control Flow Guide](https://angular.dev/guide/templates/control-flow)
- [Angular Control Flow Migration](https://angular.dev/reference/migrations/control-flow)
- [Angular @if Complete Guide (angular-university.io)](https://blog.angular-university.io/angular-if/)

---

## 5. Zoneless Change Detection

### Overview

Zoneless change detection removes the dependency on Zone.js, making applications faster and smaller. The progression:

- **Angular 18**: Introduced as experimental
- **Angular 20**: Promoted to developer preview; `ng new` prompts for zoneless
- **Angular 21**: Zoneless is the **default** for new applications; Zone.js is no longer included

### Benefits

- **Performance**: Up to 30% rendering speed improvement; up to 60% startup time improvement
- **Bundle Size**: Eliminates Zone.js payload (~13KB gzipped)
- **Debugging**: Cleaner stack traces without zone patching
- **Compatibility**: No conflicts with modern browser APIs and third-party libraries

### Enabling Zoneless (Angular 20)

```typescript
import { provideZonelessChangeDetection } from '@angular/core';

// In app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    provideRouter(routes),
  ]
};
```

### Angular 21+ (Default Behavior)

No configuration required for new applications. Existing applications that rely on Zone.js must explicitly add:

```typescript
import { provideZoneChangeDetection } from '@angular/core';

providers: [
  provideZoneChangeDetection(), // Opt-in to Zone.js
]
```

### Removing Zone.js from Existing Projects

1. Remove `zone.js` and `zone.js/testing` from the `polyfills` array in `angular.json` (both `build` and `test` targets)
2. Remove import statements from `polyfills.ts`
3. Uninstall: `npm uninstall zone.js`

### How Change Detection Works Without Zones

Angular requires explicit change notifications through:

- **Signal updates** read in templates
- **`ChangeDetectorRef.markForCheck()`** calls
- **`AsyncPipe`** usage in templates
- **Template event listeners** (click, input, etc.)
- **`ComponentRef.setInput()`** calls

### Compatibility Requirements

1. **Adopt `OnPush` strategy** on all components as a stepping stone:
   ```typescript
   @Component({
     changeDetection: ChangeDetectionStrategy.OnPush,
     // ...
   })
   ```
2. **Replace deprecated `NgZone` methods**:
   - Replace `NgZone.onMicrotaskEmpty`, `NgZone.onStable`, `NgZone.isStable` with `afterNextRender()` or `afterEveryRender()`
3. **Use `PendingTasks` for SSR** to prevent serialization before async operations complete:
   ```typescript
   const taskService = inject(PendingTasks);
   taskService.run(async () => {
     const result = await fetchData();
     this.state.set(result);
   });
   ```

### Testing with Zoneless

- `TestBed` defaults to zoneless when `zone.js` is not loaded
- Avoid `fixture.detectChanges()`; use `await fixture.whenStable()` instead
- Enable exhaustive checking:
  ```typescript
  providers: [provideCheckNoChangesConfig({ exhaustive: true })]
  ```

### Migration Tool

Angular provides a migration schematic:

```bash
ng generate @angular/core:onpush-zoneless-migration
```

Sources:
- [Angular Zoneless Guide](https://angular.dev/guide/zoneless)
- [Zoneless Change Detection (Syncfusion)](https://www.syncfusion.com/blogs/post/zoneless-change-detection-angular-18)
- [Angular 20 Zoneless Features (Kellton)](https://www.kellton.com/kellton-tech-blog/angular-20-new-features-guide)

---

## 6. Server-Side Rendering and Hydration

### Overview

Angular SSR has matured significantly. Incremental hydration is stable as of Angular 20, and Angular supports hybrid rendering strategies (SSR, SSG, CSR) with fine-grained route-level control.

### Setting Up SSR

```bash
ng add @angular/ssr
```

This adds server-side rendering support including:
- Server entry point
- Build configuration for server bundle
- Express server setup

### Hydration

Hydration reuses server-rendered DOM instead of re-creating it on the client. Enabled by default with SSR:

```typescript
// app.config.ts
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(),
    // ...
  ]
};
```

### Incremental Hydration (Stable in Angular 20)

Allows deferring hydration of specific template sections using `@defer`:

```html
@defer (hydrate on viewport) {
  <app-heavy-widget />
} @loading {
  <div>Loading widget...</div>
}
```

Hydration triggers:
- `hydrate on viewport` -- hydrates when element enters viewport
- `hydrate on interaction` -- hydrates on user interaction
- `hydrate on idle` -- hydrates during browser idle time
- `hydrate on hover` -- hydrates when user hovers
- `hydrate on timer(5s)` -- hydrates after timeout

### Route-Level Render Modes (Stable in Angular 20)

Configure rendering strategy per route:

```typescript
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },       // SSG
  { path: 'dashboard', renderMode: RenderMode.Server },  // SSR
  { path: 'settings', renderMode: RenderMode.Client },   // CSR
  { path: 'blog/:slug', renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      return [{ slug: 'post-1' }, { slug: 'post-2' }];
    }
  },
];
```

### HTTP Transfer Cache

Prevents duplicate HTTP requests during hydration:

```typescript
import { withHttpTransferCacheOptions } from '@angular/platform-browser';

provideClientHydration(
  withHttpTransferCacheOptions({
    includePostRequests: true,
    filter: (req) => !req.url.includes('/no-cache'),
  })
);
```

### Event Replay

Angular replays user events that occurred before hydration completes. Enabled by default in Angular 19+:

```typescript
provideClientHydration(withEventReplay());
```

### SSR Best Practices

1. **Use incremental hydration** for heavy components to reduce initial JavaScript payload
2. **Configure route-level render modes** to optimize each route's rendering strategy
3. **Use `PendingTasks`** to signal when async operations must complete before serialization
4. **Leverage HTTP transfer cache** to avoid duplicate API calls between server and client
5. **Guard browser-only APIs**: Use `afterNextRender()` or `isPlatformBrowser()` checks for `window`, `document`, etc.

Sources:
- [Angular SSR Guide](https://angular.dev/guide/ssr)
- [Angular Hydration Guide](https://angular.dev/guide/hydration)
- [State of SSR in Angular (fluin.io)](https://fluin.io/blog/state-of-angular-ssr-2025)
- [Angular Architects SSR Guide](https://www.angulararchitects.io/blog/guide-for-ssr/)

---

## 7. Resource API and httpResource

### resource() (Experimental)

The `resource()` API manages asynchronous data fetching within Angular's signal-based architecture, exposing async results as synchronous signals.

```typescript
import { resource } from '@angular/core';

const userId = signal(1);

const userResource = resource({
  params: () => ({ id: userId() }),
  loader: async ({ params, abortSignal }) => {
    const response = await fetch(`/api/users/${params.id}`, { signal: abortSignal });
    return response.json();
  }
});

// Access in template
// userResource.value()     -- the resolved data
// userResource.isLoading() -- boolean loading state
// userResource.error()     -- error if failed
// userResource.status()    -- 'idle' | 'loading' | 'reloading' | 'resolved' | 'error' | 'local'
// userResource.hasValue()  -- type guard for value
```

### httpResource (Experimental)

A signal-based reactive wrapper around `HttpClient`:

```typescript
import { httpResource } from '@angular/common/http';

// Simple usage
userId = input.required<string>();
user = httpResource<User>(() => `/api/user/${userId()}`);

// Advanced configuration
user = httpResource<User>(() => ({
  url: `/api/user/${userId()}`,
  method: 'GET',
  headers: { 'X-Special': 'true' },
  params: { fast: 'yes' },
}));

// With validation (e.g., Zod)
import { z } from 'zod';
const UserSchema = z.object({ id: z.number(), name: z.string() });

user = httpResource(() => `/api/user/${userId()}`, {
  parse: UserSchema.parse
});
```

**Response type variants:**

```typescript
httpResource.text(() => '/api/data');       // returns string
httpResource.blob(() => '/api/file');       // returns Blob
httpResource.arrayBuffer(() => '/api/bin'); // returns ArrayBuffer
```

**Template integration:**

```html
@if (user.hasValue()) {
  <app-user-details [user]="user.value()" />
} @else if (user.error()) {
  <div>Could not load user: {{ user.error() }}</div>
} @else if (user.isLoading()) {
  <app-spinner />
}
```

### rxResource (for RxJS Integration)

```typescript
import { rxResource } from '@angular/core/rxjs-interop';

const userResource = rxResource({
  params: () => ({ id: userId() }),
  loader: ({ params }) => this.http.get<User>(`/api/users/${params.id}`)
});
```

### Resource API Best Practices

1. **Use `httpResource` for GET queries only**; use `HttpClient` directly for mutations (POST, PUT, DELETE)
2. **Always guard value reads** with `hasValue()` before accessing `.value()`
3. **Leverage automatic cancellation**: Outstanding requests are cancelled when params change
4. **Use `parse` option** for runtime type validation with libraries like Zod
5. **Requires `provideHttpClient()`** in application providers (automatic in Angular 21)
6. **The API is still experimental** -- expect potential changes before stabilization

Sources:
- [Angular httpResource Guide](https://angular.dev/guide/http/http-resource)
- [Angular Resource API Guide](https://angular.dev/guide/signals/resource)
- [Angular Architects Resource API](https://www.angulararchitects.io/blog/asynchronous-resources-with-angulars-new-resource-api/)

---

## 8. Project Structure and File Conventions

### Recommended Project Structure (2025+)

```
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
│   ├── styles.css
│   └── app/
│       ├── app.ts                    # Root component (2025 style)
│       ├── app.config.ts             # Application configuration
│       ├── app.routes.ts             # Root route definitions
│       ├── core/
│       │   ├── auth/
│       │   │   ├── auth.service.ts
│       │   │   ├── auth.guard.ts
│       │   │   └── auth.interceptor.ts
│       │   ├── api/
│       │   │   └── api.service.ts
│       │   └── error/
│       │       └── error-handler.service.ts
│       ├── shared/
│       │   ├── components/
│       │   │   ├── button/
│       │   │   │   └── button.ts
│       │   │   └── modal/
│       │   │       └── modal.ts
│       │   ├── directives/
│       │   │   └── highlight.ts
│       │   ├── pipes/
│       │   │   └── truncate.ts
│       │   └── models/
│       │       └── user.model.ts
│       └── features/
│           ├── dashboard/
│           │   ├── dashboard.ts
│           │   ├── dashboard.routes.ts
│           │   └── widgets/
│           │       ├── stats-widget.ts
│           │       └── chart-widget.ts
│           ├── users/
│           │   ├── user-list.ts
│           │   ├── user-detail.ts
│           │   ├── users.routes.ts
│           │   └── services/
│           │       └── user.service.ts
│           └── settings/
│               ├── settings.ts
│               └── settings.routes.ts
```

### Core Principles (LIFT)

| Principle | Description |
|-----------|-------------|
| **L**ocate | Locate code quickly |
| **I**dentify | Identify the code at a glance |
| **F**lat | Keep a flat folder structure (avoid deeply nesting) |
| **T**ry DRY | Try to be DRY (Don't Repeat Yourself) |

### Folder Organization Rules

1. **`core/`**: Singleton services (provided in root), interceptors, guards. Should not be imported by feature modules -- only used application-wide.
2. **`shared/`**: Reusable components, pipes, directives used across multiple features. Everything here must be standalone.
3. **`features/`**: Organized by domain/feature. Each feature folder contains its own components, services, routes, and models. All feature routes should support lazy loading.

### File Naming Conventions (2025 Style Guide)

The Angular team's **2025 style guide** introduces changes to file naming:

- **No type suffixes required**: The guide makes no statements about "component", "directive", or "service" suffixes. Angular's own documentation and examples will **not** use these suffixes.
  - `user-profile.ts` instead of `user-profile.component.ts`
  - `auth.ts` instead of `auth.service.ts`
- **Hyphenated file names**: Use hyphens to separate words: `user-profile.ts`
- **Single-file components are acceptable**: Template and styles can be inline
- **Avoid generic file names**: Do not use `helpers.ts`, `utils.ts`, or `common.ts`; use descriptive names

**Note**: The CLI `ng new` command now supports `--style-guide=2025` (default) and `--style-guide=2016` (legacy with suffixes like `.component.ts`).

### Multi-Project Workspace

```bash
ng new my-workspace --no-create-application
cd my-workspace
ng generate application my-app
ng generate library my-lib
```

Structure:
```
my-workspace/
├── angular.json
├── projects/
│   ├── my-app/
│   │   └── src/
│   └── my-lib/
│       ├── src/lib/
│       └── src/public-api.ts
```

Sources:
- [Angular File Structure Reference](https://angular.dev/reference/configs/file-structure)
- [Angular Style Guide](https://angular.dev/style-guide)
- [Angular 2025 Project Structure (ismaelramos.dev)](https://www.ismaelramos.dev/blog/angular-2025-project-structure-with-the-features-approach/)
- [Angular v20+ Folder Structure Guide](https://www.angular.courses/blog/angular-folder-structure-guide)

---

## 9. Angular Style Guide (2025 Update)

### Key Changes from the 2024 RFC

The Angular team conducted two public RFCs (2024 and 2025) to modernize the style guide. Key updates:

#### Naming Conventions

1. **No mandatory type suffixes**: Class names like `UserProfileComponent` are still valid but `UserProfile` is equally acceptable. Angular docs will stop using suffixes.
2. **Descriptive file names**: Avoid `helpers.ts`, `utils.ts`, `common.ts`. Use names that reflect purpose.
3. **Hyphenated naming**: `user-profile.ts`, `auth-guard.ts`, `data-access.ts`

#### Architecture Conventions

1. **Standalone-first**: All new code should be module-free
2. **Signals for state**: Use signals as the primary mechanism for component-level state
3. **`inject()` over constructor injection**: Prefer the `inject()` function
4. **Feature-based structure**: Organize by feature/domain, not by type
5. **One thing per file**: Each file should define a single component, service, pipe, etc.

#### Template Conventions

1. **Use new control flow**: `@if`, `@for`, `@switch` instead of `*ngIf`, `*ngFor`, `*ngSwitch`
2. **Self-closing tags** for components without content: `<app-icon />`
3. **Use `@defer`** for heavy components that are below the fold

#### Code Conventions

1. **Prefer `readonly`** for properties that should not be reassigned
2. **Use strict TypeScript**: Enable `strict: true` in `tsconfig.json`
3. **Avoid `any` type**: Use proper typing to maintain TypeScript benefits
4. **Use `OnPush` change detection** as default (stepping stone to zoneless)

Sources:
- [Angular Coding Style Guide](https://angular.dev/style-guide)
- [RFC: Updated Style Guide 2025 (GitHub Discussion)](https://github.com/angular/angular/discussions/59522)
- [Angular's 2025 Style Guide Key Updates (Infosys)](https://blogs.infosys.com/digital-experience/web-ui-ux/angulars-2025-style-guide-key-updates-angular-style-upgrade-are-you-coding-the-2025-way.html)
- [Angular 2025 New Style Guide Standards (Medium)](https://medium.com/@sehban.alam/angular-2025-new-style-guide-standards-and-how-to-apply-them-3277eef541a3)

---

## 10. Dependency Injection Best Practices

### Prefer `inject()` Over Constructor Injection

The `inject()` function (introduced in Angular 14, widely adopted since Angular 16+) is the modern recommended approach:

```typescript
// Preferred: inject() function
@Component({ /* ... */ })
export class UserProfileComponent {
  private userService = inject(UserService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
}

// Legacy: constructor injection (still works but not recommended for new code)
@Component({ /* ... */ })
export class UserProfileComponent {
  constructor(
    private userService: UserService,
    private route: ActivatedRoute,
    private router: Router,
  ) {}
}
```

### Benefits of `inject()`

1. **No constructor boilerplate**: Cleaner class definitions
2. **Better type inference**: TypeScript infers types automatically
3. **Works with inheritance**: No need to pass dependencies through `super()`
4. **Supports options**: `inject(Service, { optional: true, skipSelf: true })`
5. **Works in functions**: Can be used in factory functions and `InjectionToken` factories

### Service Registration

```typescript
// Preferred: Tree-shakable, singleton service
@Injectable({ providedIn: 'root' })
export class DataService { }

// Feature-scoped: provide in route configuration
export const FEATURE_ROUTES: Routes = [
  {
    path: '',
    providers: [FeatureScopedService],
    children: [/* ... */]
  }
];
```

### Injection Tokens

```typescript
import { InjectionToken, inject } from '@angular/core';

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', {
  providedIn: 'root',
  factory: () => 'https://api.example.com'
});

// Usage
const apiUrl = inject(API_BASE_URL);
```

### DI Best Practices

1. **Use `providedIn: 'root'`** for singleton services (tree-shakable by default)
2. **Use route-level providers** for feature-scoped services rather than component-level `providers`
3. **Prefer `inject()` function** over constructor injection in all new code
4. **Use `InjectionToken`** for non-class dependencies (configuration, constants)
5. **Avoid providing services in multiple places** to prevent unintended multiple instances

Sources:
- [Angular Dependency Injection Overview](https://angular.dev/guide/di)
- [Why inject() is Better Than Constructor (Angular.love)](https://angular.love/why-is-inject-better-than-constructor/)
- [Mastering DI in Angular 2025 (JavaScript in Plain English)](https://javascript.plainenglish.io/mastering-dependency-injection-in-angular-2025-the-complete-developer-guide-e8c56af9dc55)

---

## 11. Routing and Lazy Loading

### Modern Route Configuration

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },

  // Lazy load standalone components
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard').then(m => m.Dashboard)
  },

  // Lazy load feature routes
  {
    path: 'users',
    loadChildren: () => import('./features/users/users.routes').then(m => m.USERS_ROUTES)
  },

  // Route with guards
  {
    path: 'admin',
    canActivate: [() => inject(AuthService).isAdmin()],
    loadComponent: () => import('./features/admin/admin').then(m => m.Admin)
  },

  // Wildcard
  { path: '**', redirectTo: 'dashboard' }
];
```

### Feature Route Files

```typescript
// features/users/users.routes.ts
import { Routes } from '@angular/router';

export const USERS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./user-list').then(m => m.UserList)
  },
  {
    path: ':id',
    loadComponent: () => import('./user-detail').then(m => m.UserDetail)
  }
];
```

### Functional Guards and Resolvers

```typescript
// Functional guard
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// Functional resolver
export const userResolver: ResolveFn<User> = (route) => {
  const userService = inject(UserService);
  return userService.getUser(route.paramMap.get('id')!);
};
```

### Async Redirects (Angular 20+)

```typescript
{
  path: 'old-path',
  redirectTo: async () => {
    const config = await inject(ConfigService).getRedirectConfig();
    return config.newPath;
  }
}
```

### Lazy Loading Best Practices

1. **Use `loadComponent`** for standalone components instead of `loadChildren` with modules
2. **Organize route files per feature**: Each feature folder has its own `*.routes.ts`
3. **Use functional guards** instead of class-based guards
4. **Minimize route-level providers**: Prefer `providedIn: 'root'`; use route providers only for truly scoped services
5. **Use preloading strategies** for frequently visited routes:
   ```typescript
   provideRouter(routes, withPreloading(PreloadAllModules))
   ```

Sources:
- [Angular Lazy Loading Routes](https://angular.dev/reference/migrations/route-lazy-loading)
- [Routing and Lazy Loading with Standalone Components (Angular Architects)](https://www.angulararchitects.io/en/blog/routing-and-lazy-loading-with-standalone-components/)
- [Angular Lazy Loading and Route Guards (Djamware)](https://www.djamware.com/post/687dbe89416fe15d8d95096e/angular-lazy-loading-and-route-guards-best-practices-and-examples)

---

## 12. Performance Best Practices

### Change Detection Optimization

1. **Use `OnPush` change detection** on all components:
   ```typescript
   @Component({
     changeDetection: ChangeDetectionStrategy.OnPush,
   })
   ```
2. **Migrate to zoneless** for best performance (default in Angular 21)
3. **Use signals** for reactive state to enable fine-grained updates

### Bundle Size Optimization

1. **Lazy load routes** to reduce initial bundle (can reduce by up to 80%)
2. **Use `@defer` blocks** for below-the-fold content (25-40% LCP improvement):
   ```html
   @defer (on viewport) {
     <app-heavy-chart />
   } @placeholder {
     <div class="skeleton"></div>
   }
   ```
3. **Analyze bundle size**: `ng build --stats-json` then use `webpack-bundle-analyzer`
4. **Remove Zone.js** when using zoneless to save ~13KB gzipped
5. **Tree-shake effectively**: Standalone components + `providedIn: 'root'` services

### Template Performance

1. **Never call methods in templates** that are not memoized; use `computed()` signals or pipes:
   ```typescript
   // BAD: called on every change detection cycle
   // <div>{{ getFullName() }}</div>

   // GOOD: computed signal, memoized
   fullName = computed(() => `${this.firstName()} ${this.lastName()}`);
   // <div>{{ fullName() }}</div>
   ```
2. **Use `trackBy` / `track` in loops** to minimize DOM operations
3. **Use `@defer` with appropriate triggers** to load heavy components lazily

### Image Optimization

```typescript
import { NgOptimizedImage } from '@angular/common';

@Component({
  imports: [NgOptimizedImage],
  template: `
    <img ngSrc="/hero.jpg" width="800" height="600" priority />
    <img ngSrc="/secondary.jpg" width="400" height="300" loading="lazy" />
  `
})
```

### Virtual Scrolling

```typescript
import { ScrollingModule } from '@angular/cdk/scrolling';

@Component({
  imports: [ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport itemSize="48" class="viewport">
      <div *cdkVirtualFor="let item of items">{{ item.name }}</div>
    </cdk-virtual-scroll-viewport>
  `
})
```

### HTTP Optimization

1. **Use HTTP interceptors** for caching, authentication, and error handling
2. **Leverage HTTP transfer cache** for SSR to avoid duplicate requests
3. **Use `httpResource`** for declarative, reactive data fetching with automatic cancellation
4. **Cancel unnecessary requests**: `httpResource` does this automatically; for manual subscriptions use `takeUntilDestroyed()`

### Performance Measurement

- Angular DevTools (Chrome extension) for component tree and change detection profiling
- Chrome DevTools with Angular-specific reporting (Angular 20+)
- Lighthouse for Core Web Vitals
- `ng build --stats-json` for bundle analysis

Sources:
- [10 Angular Performance Hacks (Syncfusion)](https://www.syncfusion.com/blogs/post/angular-performance-optimization)
- [Angular Zoneless Guide](https://angular.dev/guide/zoneless)
- [Angular 2025: Signals, Standalone, and Performance](https://blog.madrigan.com/en/blog/202602161006/)

---

## 13. Testing Best Practices

### Default Test Framework: Vitest (Angular 21+)

As of Angular 21, **Vitest** is the default test runner for new projects, replacing Karma/Jasmine. New projects include `vitest` and `jsdom` by default.

```typescript
// Minimal angular.json test configuration
"test": {
  "builder": "@angular/build:unit-test",
  "options": {}
}
```

### Migration from Jasmine to Vitest

```bash
ng generate refactor-jasmine-vitest
```

### Component Testing

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UserProfile } from './user-profile';

describe('UserProfile', () => {
  let component: UserProfile;
  let fixture: ComponentFixture<UserProfile>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserProfile], // Standalone components go in imports
      providers: [
        { provide: UserService, useValue: mockUserService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(UserProfile);
    component = fixture.componentInstance;
  });

  it('should display user name', async () => {
    fixture.componentRef.setInput('user', { name: 'Alice' });
    await fixture.whenStable(); // Preferred over fixture.detectChanges() for zoneless
    expect(fixture.nativeElement.textContent).toContain('Alice');
  });
});
```

### Testing Signals

```typescript
it('should update computed value', () => {
  const count = signal(0);
  const doubled = computed(() => count() * 2);

  expect(doubled()).toBe(0);
  count.set(5);
  expect(doubled()).toBe(10);
});
```

### Testing httpResource

```typescript
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

it('should fetch user data', () => {
  TestBed.configureTestingModule({
    providers: [provideHttpClient(), provideHttpClientTesting()]
  });

  const httpTesting = TestBed.inject(HttpTestingController);
  const userResource = httpResource<User>(() => '/api/user/1', {
    injector: TestBed.inject(Injector)
  });

  const req = httpTesting.expectOne('/api/user/1');
  req.flush({ id: 1, name: 'Alice' });

  expect(userResource.value()).toEqual({ id: 1, name: 'Alice' });
});
```

### Testing with Zoneless

```typescript
TestBed.configureTestingModule({
  providers: [
    provideZonelessChangeDetection(),
    provideCheckNoChangesConfig({ exhaustive: true })
  ]
});

// Use whenStable() instead of detectChanges()
await fixture.whenStable();
```

### E2E Testing

- **Cypress** is the preferred E2E framework (Protractor was removed in Angular 15)
- **Playwright** is also a popular choice with Angular
- Angular provides built-in Playwright integration through the `@angular/ssr` testing utilities

### Testing Best Practices

1. **Test behavior, not implementation**: Focus on what the component does, not how it does it
2. **Mock external dependencies**: Use `HttpTestingController` for HTTP, provide mock services
3. **Test edge cases and error handling**: Do not only test the happy path
4. **Use `await fixture.whenStable()`** instead of `fixture.detectChanges()` for zoneless compatibility
5. **Keep tests isolated**: Each test should be independent; clean up subscriptions in `afterEach`
6. **Automate in CI/CD**: Run unit tests in pipelines to detect regressions early
7. **Use `provideCheckNoChangesConfig({ exhaustive: true })`** to catch change detection issues

Sources:
- [Angular Testing Overview](https://angular.dev/guide/testing)
- [Angular Component Testing Scenarios](https://angular.dev/guide/testing/components-scenarios)
- [Angular 21 Announcement (Ninja Squad)](https://blog.ninja-squad.com/2025/11/20/what-is-new-angular-21.0)
- [Advanced Angular Testing in 2025 (Medium)](https://medium.com/@roshannavale7/advanced-angular-testing-in-2025-best-practices-for-robust-unit-and-e2e-testing-1a7e629e000b)

---

## 14. Angular CLI Commands and Configuration

### Project Creation

```bash
# Create a new project (Angular 21 defaults: standalone, zoneless, Vitest, 2025 style guide)
ng new my-app

# With specific options
ng new my-app --style=scss --ssr --routing

# Legacy style guide (with .component.ts suffixes)
ng new my-app --style-guide=2016

# Multi-project workspace
ng new my-workspace --no-create-application
```

### Code Generation

```bash
# Generate a component (standalone by default)
ng generate component features/users/user-list

# Generate a service
ng generate service core/auth/auth

# Generate a guard (functional by default)
ng generate guard core/auth/auth

# Generate a pipe
ng generate pipe shared/pipes/truncate

# Generate a directive
ng generate directive shared/directives/highlight

# Generate an interceptor
ng generate interceptor core/api/auth

# Generate environments
ng generate environments
```

### Development Server

```bash
# Start dev server
ng serve

# Open browser automatically
ng serve --open

# Specific port
ng serve --port 4201

# With SSL
ng serve --ssl

# Variable replacement (Angular 21+)
ng serve --define "API_URL=http://localhost:3000"
```

### Building

```bash
# Production build
ng build

# With bundle analysis
ng build --stats-json

# Development build
ng build --configuration development
```

### Testing

```bash
# Run unit tests (Vitest in Angular 21+)
ng test

# Run with code coverage
ng test --code-coverage

# Run specific test file
ng test --include='**/user-profile.spec.ts'
```

### Updates and Migrations

```bash
# Update Angular and dependencies
ng update @angular/core @angular/cli

# Run specific migration
ng generate @angular/core:control-flow          # Migrate to new control flow
ng generate @angular/core:standalone             # Migrate to standalone
ng generate @angular/core:onpush-zoneless-migration  # Migrate to zoneless
ng generate refactor-jasmine-vitest              # Migrate tests to Vitest
```

### angular.json Key Configuration

```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "my-app": {
      "projectType": "application",
      "root": "src",
      "architect": {
        "build": {
          "builder": "@angular/build:application",
          "options": {
            "outputPath": "dist/my-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "tsConfig": "tsconfig.app.json",
            "assets": ["{ \"glob\": \"**/*\", \"input\": \"public\" }"],
            "styles": ["src/styles.css"],
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
        "serve": {
          "builder": "@angular/build:dev-server",
          "configurations": {
            "production": { "buildTarget": "my-app:build:production" },
            "development": { "buildTarget": "my-app:build:development" }
          },
          "defaultConfiguration": "development"
        },
        "test": {
          "builder": "@angular/build:unit-test"
        }
      }
    }
  }
}
```

Sources:
- [Angular Workspace Configuration](https://angular.dev/reference/configs/workspace-config)
- [Angular CLI ng new](https://angular.dev/cli/new)
- [Angular CLI ng serve](https://angular.dev/cli/serve)
- [Angular Local Setup](https://angular.dev/tools/cli/setup-local)

---

## 15. Common Patterns and Anti-Patterns

### Recommended Patterns

#### State Management with Signals

```typescript
@Injectable({ providedIn: 'root' })
export class CartService {
  private _items = signal<CartItem[]>([]);
  readonly items = this._items.asReadonly();
  readonly total = computed(() =>
    this._items().reduce((sum, item) => sum + item.price * item.quantity, 0)
  );
  readonly itemCount = computed(() =>
    this._items().reduce((sum, item) => sum + item.quantity, 0)
  );

  addItem(item: CartItem) {
    this._items.update(items => [...items, item]);
  }

  removeItem(id: string) {
    this._items.update(items => items.filter(i => i.id !== id));
  }
}
```

#### Smart/Dumb Component Pattern

```typescript
// Smart (container) component -- handles data and logic
@Component({
  selector: 'app-user-page',
  template: `
    @if (userResource.hasValue()) {
      <app-user-card [user]="userResource.value()" (save)="onSave($event)" />
    }
  `
})
export class UserPage {
  private userService = inject(UserService);
  userResource = httpResource<User>(() => '/api/user/me');

  onSave(user: User) {
    this.userService.update(user);
  }
}

// Dumb (presentational) component -- pure display and events
@Component({
  selector: 'app-user-card',
  template: `
    <h2>{{ user().name }}</h2>
    <button (click)="save.emit(user())">Save</button>
  `
})
export class UserCard {
  user = input.required<User>();
  save = output<User>();
}
```

#### Cleanup with `takeUntilDestroyed()`

```typescript
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({ /* ... */ })
export class MyComponent {
  private destroyRef = inject(DestroyRef);

  constructor() {
    this.someObservable$.pipe(
      takeUntilDestroyed()  // Automatically unsubscribes on destroy
    ).subscribe(data => { /* ... */ });
  }
}
```

#### Typed Reactive Forms

```typescript
import { FormBuilder, Validators } from '@angular/forms';

@Component({ /* ... */ })
export class ProfileForm {
  private fb = inject(FormBuilder);

  form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    age: [null as number | null, [Validators.min(0)]],
  });
}
```

### Anti-Patterns to Avoid

#### 1. Calling Methods in Templates

```typescript
// BAD: method called on every change detection cycle
@Component({
  template: `<div>{{ getFullName() }}</div>`
})
export class Bad {
  getFullName() { return `${this.first} ${this.last}`; }
}

// GOOD: computed signal (memoized)
@Component({
  template: `<div>{{ fullName() }}</div>`
})
export class Good {
  first = signal('John');
  last = signal('Doe');
  fullName = computed(() => `${this.first()} ${this.last()}`);
}
```

#### 2. "God Components" (Too Many Responsibilities)

```typescript
// BAD: one component handles everything
@Component({ /* ... */ })
export class DashboardComponent {
  // Handles data fetching, user management, charts, notifications,
  // settings, and every piece of UI on the page
  // 500+ lines of code
}

// GOOD: decompose into focused components
// dashboard.ts (orchestrator)
// dashboard-stats.ts (stats display)
// dashboard-chart.ts (chart widget)
// notification-panel.ts (notifications)
```

#### 3. Nested Subscriptions

```typescript
// BAD: subscription within subscription
this.route.params.subscribe(params => {
  this.userService.getUser(params.id).subscribe(user => {
    this.postService.getPosts(user.id).subscribe(posts => {
      this.posts = posts;
    });
  });
});

// GOOD: use RxJS operators
this.route.params.pipe(
  switchMap(params => this.userService.getUser(params.id)),
  switchMap(user => this.postService.getPosts(user.id)),
  takeUntilDestroyed()
).subscribe(posts => this.posts = posts);

// BEST: use signals and httpResource
userId = toSignal(this.route.params.pipe(map(p => p['id'])));
user = httpResource<User>(() => `/api/users/${this.userId()}`);
```

#### 4. Missing Unsubscribe

```typescript
// BAD: memory leak
ngOnInit() {
  this.data$.subscribe(data => this.data = data);
}

// GOOD: use takeUntilDestroyed
constructor() {
  this.data$.pipe(takeUntilDestroyed()).subscribe(data => this.data = data);
}

// BEST: use signals (no subscriptions needed)
data = toSignal(this.data$);
```

#### 5. Excessive Use of `any`

```typescript
// BAD: loses TypeScript benefits
data: any;
processData(input: any): any { /* ... */ }

// GOOD: proper typing
data: UserData | null = null;
processData(input: UserInput): ProcessedResult { /* ... */ }
```

#### 6. Direct DOM Manipulation

```typescript
// BAD: bypasses Angular's rendering
document.getElementById('myDiv')!.style.display = 'none';

// GOOD: use Angular bindings
@Component({
  template: `<div [style.display]="isVisible() ? 'block' : 'none'">...</div>`
})
```

#### 7. Not Using OnPush / Zoneless

```typescript
// BAD: default change detection checks everything
@Component({
  // No changeDetection specified -- runs checks on every event
})

// GOOD: OnPush (stepping stone to zoneless)
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
})

// BEST: zoneless (Angular 21 default)
// No Zone.js, signals drive change detection
```

Sources:
- [9 Angular Anti-Patterns That Kill Performance (Medium)](https://medium.com/@satnammca/9-angular-anti-patterns-that-secretly-kill-performance-83c8df454569)
- [Angular Anti-Patterns (compilenrun.com)](https://www.compilenrun.com/docs/framework/angular/angular-best-practices/angular-anti-patterns/)
- [Angular Component Design Anti-Patterns (Medium)](https://medium.com/@amcdnl/angular-component-design-anti-patterns-14ed34c538a7)

---

## 16. Angular 20 and 21 Feature Summary

### Angular 20 (May 2025) -- Key Features

#### Stable APIs
- `signal()`, `computed()`, `effect()`, `linkedSignal()` -- all stable
- Signal-based inputs, queries, and outputs -- stable
- `toSignal()` and `toObservable()` -- stable
- `afterEveryRender()` and `afterNextRender()` -- stable
- `PendingTasks` API for SSR -- stable
- Incremental hydration -- stable
- Route-level render modes -- stable

#### Developer Preview
- Zoneless change detection (`provideZonelessChangeDetection()`)

#### Experimental
- `httpResource` -- signal-based HTTP data fetching
- Resource streaming with `rxResource`

#### Template Improvements
- Template string literals (tagged and untagged)
- Exponentiation operator (`**`)
- `in` keyword for property checking
- `void` operator

#### Routing Enhancements
- Async redirect functions (Promises and Observables)
- `Router.getCurrentNavigation()?.abort()` for cancelling navigations

#### Dynamic Components
- `NgComponentOutlet` improvements: `ngComponentOutletInputs`, `ngComponentOutletContent`, `ngComponentOutletInjector`
- New binding helpers: `inputBinding()`, `twoWayBinding()`, `outputBinding()`

#### Enhanced Diagnostics
- Type checking for host bindings with hover tooltips
- Detection of uninvoked track functions in `@for` loops
- Missing custom structural directive import detection

#### Breaking Changes
- Node.js: ^20.11.1, ^22.11.0, or ^24.0.0
- TypeScript: >=5.8.0 <5.9.0
- `ng-reflect-*` attributes removed in development mode
- `InjectFlags` API removed (migration schematic provided)
- HammerJS support deprecated

### Angular 21 (November 2025) -- Key Features

#### Signal Forms (Experimental)
- New `@angular/forms/signals` package for signal-based forms
- Compatibility bridge via `@angular/forms/signals/compat` for gradual migration from reactive forms

#### Zoneless by Default
- New applications use zoneless change detection by default
- Zone.js no longer included in new projects
- Existing apps must explicitly add `provideZoneChangeDetection()` to keep Zone.js
- Migration schematics provided

#### Vitest as Default Test Runner
- Vitest replaces Karma/Jasmine for new projects
- Migration tool: `ng generate refactor-jasmine-vitest`
- Simplified `angular.json` test configuration

#### Angular Aria (Developer Preview)
- New `@angular/aria` package providing headless ARIA directives
- Accessible UI component primitives

#### Core Improvements
- `SimpleChanges` is now generic for type-safe `ngOnChanges`
- `HttpClient` provided by default in root injector (no need for `provideHttpClient()`)
- New `FormArrayDirective` for top-level form arrays
- Router `scroll` navigation option
- RegExp literal support in templates
- `@defer` viewport trigger accepts `IntersectionObserver` options
- `typeCheckHostBindings` enabled by default

#### CLI Improvements
- Tailwind CSS schematic for quick setup
- `ng serve --define` for variable replacement
- Enhanced `ng version` with JSON output
- MCP server tools for AI-assisted development

Sources:
- [Announcing Angular v20 (Angular Blog)](https://blog.angular.dev/announcing-angular-v20-b5c9c06cf301)
- [Angular 20 What's New (Angular.love)](https://angular.love/angular-20-whats-new/)
- [Announcing Angular v21 (Angular Blog)](https://blog.angular.dev/announcing-angular-v21-57946c34f14b)
- [What's New in Angular 21.0 (Ninja Squad)](https://blog.ninja-squad.com/2025/11/20/what-is-new-angular-21.0)
- [Angular 21 What's New (Angular.love)](https://angular.love/angular-21-whats-new/)
- [Angular Summer Update 2025 (Angular Blog)](https://blog.angular.dev/angular-summer-update-2025-1987592a0b42)
- [Angular 20 vs Angular 21 (Nanobyte Technologies)](https://nanobytetechnologies.com/Blog/Angular-20-vs-Angular-21-2025-Key-Differences-New-Features-Performance-Upgrades)
