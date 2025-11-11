---
description: Analyze task complexity and create actionable implementation plan
model: claude-sonnet-4-5
---

Analyze the following task and create a detailed implementation plan.

## Task Description

$ARGUMENTS

## Analysis Framework

### 1. **Task Classification**
- Complexity: Simple / Medium / Complex
- Type: Feature / Bug Fix / Refactor / Optimization
- Estimated time: Hours / Days
- Dependencies: What needs to exist first?

### 2. **Technical Breakdown**

**Frontend Components**
- Which Vue components affected?
- New components needed?
- Composables required?
- State management changes?

**Data Flow**
- API endpoints needed?
- Data models/types?
- Validation requirements?

**Routing & Navigation**
- New pages/routes?
- Middleware needed?
- Layout changes?

### 3. **Implementation Steps**

Break down into sequential, testable tasks:

**Phase 1: Setup**
- [ ] Dependencies/packages
- [ ] Type definitions
- [ ] Base structure

**Phase 2: Core Implementation**
- [ ] Component development
- [ ] Logic implementation
- [ ] State management

**Phase 3: Integration**
- [ ] API integration
- [ ] Routing
- [ ] Testing

**Phase 4: Polish**
- [ ] Error handling
- [ ] Loading states
- [ ] Accessibility
- [ ] Responsive design

### 4. **Success Criteria**

Define "done":
- ✓ Functionality works as specified
- ✓ TypeScript types are strict (no `any`)
- ✓ Components are accessible
- ✓ Responsive across devices
- ✓ Error handling implemented
- ✓ Loading states present
- ✓ No console errors/warnings

### 5. **Vue/Nuxt Best Practices**

- ✓ Use Composition API with `<script setup>`
- ✓ Proper TypeScript typing
- ✓ Composables for reusable logic
- ✓ Auto-imports where available
- ✓ SSR-compatible code
- ✓ Proper error handling

Provide a clear, actionable plan that can be followed step-by-step.
