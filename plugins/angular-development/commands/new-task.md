---
description: Analyze task complexity and create actionable Angular implementation plan
model: claude-sonnet-4-5
---

Analyze the following task and create a detailed implementation plan for an Angular 21+ application.

## Task Description

$ARGUMENTS

## Analysis Framework

### 1. **Task Classification**
- Complexity: Simple / Medium / Complex
- Type: Feature / Bug Fix / Refactor / Optimization / Migration
- Estimated time: Hours / Days
- Dependencies: What needs to exist first?

### 2. **Technical Breakdown**

**Components**
- Which Angular components are affected?
- New standalone components needed?
- Smart vs. presentational component split?
- Signal inputs/outputs to define?

**Services & State**
- Services to create or modify?
- Signal-based store needed?
- Injection tokens or configuration?
- HTTP resources (`httpResource`) to define?

**Routing & Navigation**
- New routes or route modifications?
- Guards needed (auth, role, unsaved changes)?
- Resolvers for data pre-fetching?
- Lazy loading configuration?

**Shared Artifacts**
- Pipes, directives to create?
- Interfaces/types/models to define?
- Interceptors needed?

### 3. **Implementation Steps**

Break down into sequential, testable tasks:

**Phase 1: Foundation**
- [ ] Define TypeScript interfaces and types
- [ ] Create or update services with signal-based state
- [ ] Set up injection tokens if needed
- [ ] Configure route definitions

**Phase 2: Core Implementation**
- [ ] Build presentational (dumb) components
- [ ] Build container (smart) components
- [ ] Implement signal-based data flow
- [ ] Wire up `httpResource` or HTTP calls

**Phase 3: Integration**
- [ ] Connect route configuration with guards and resolvers
- [ ] Add interceptors if needed
- [ ] Implement cross-component communication via stores
- [ ] Add form validation (typed reactive forms or signal forms)

**Phase 4: Polish**
- [ ] Error handling and error states
- [ ] Loading states and skeletons
- [ ] Accessibility (ARIA, keyboard navigation, focus management)
- [ ] `@defer` blocks for heavy below-the-fold content
- [ ] Responsive design considerations

**Phase 5: Testing**
- [ ] Unit tests with Vitest and TestBed
- [ ] Test signals and computed values
- [ ] Test guards and interceptors
- [ ] Test component behavior (not implementation details)

### 4. **Angular 21+ Patterns to Apply**

**Component Architecture**
- ✓ Standalone components (no NgModules)
- ✓ `ChangeDetectionStrategy.OnPush` on all components
- ✓ Signal-based `input()`, `output()`, `model()`
- ✓ `computed()` for derived template values
- ✓ `@if` / `@for` / `@switch` control flow

**State Management**
- ✓ Signal-based stores with private/public pattern
- ✓ `httpResource` for declarative data fetching
- ✓ `linkedSignal` for dependent state resets
- ✓ `effect()` only for side effects (persistence, logging)

**Dependency Injection**
- ✓ `inject()` function (not constructor injection)
- ✓ `providedIn: 'root'` for singleton services
- ✓ Route-level `providers` for feature-scoped services

**Routing**
- ✓ Lazy load all routes with `loadComponent` / `loadChildren`
- ✓ Functional guards and resolvers
- ✓ `withComponentInputBinding()` for route data as inputs

**Performance**
- ✓ Zoneless change detection (Angular 21 default)
- ✓ `@defer` for heavy content
- ✓ `NgOptimizedImage` for images
- ✓ No method calls in templates (use `computed()` or pipes)

### 5. **Project Structure**

```
src/app/
├── app.ts                 # Root component
├── app.config.ts          # Application config
├── app.routes.ts          # Root routes
├── core/                  # Singleton services, guards, interceptors
│   ├── auth/
│   ├── api/
│   └── error/
├── shared/                # Reusable components, pipes, directives
│   ├── components/
│   ├── pipes/
│   ├── directives/
│   └── models/
└── features/              # Feature-based organization
    └── [feature-name]/
        ├── [feature].ts
        ├── [feature].routes.ts
        ├── services/
        └── components/
```

### 6. **Success Criteria**

Define "done":
- ✓ Functionality works as specified
- ✓ TypeScript strict mode passes (no `any`)
- ✓ All components use OnPush / zoneless
- ✓ Signal-based inputs, outputs, and state throughout
- ✓ New control flow syntax (`@if`, `@for`, `@switch`)
- ✓ Routes are lazy loaded
- ✓ Components are accessible (ARIA, keyboard)
- ✓ Error and loading states are handled
- ✓ No console errors or warnings
- ✓ Unit tests pass

### 7. **Risk Assessment**

- **State complexity**: Does this feature require cross-feature state sharing?
- **Third-party dependencies**: Are all libraries compatible with zoneless Angular?
- **Migration concerns**: Does this touch legacy NgModule or Zone.js-dependent code?
- **Performance**: Are there large lists, complex forms, or heavy components that need `@defer` / virtual scrolling?

Provide a clear, actionable plan that can be followed step-by-step with Angular 21+ best practices applied throughout.
