---
description: Plan Vue/Nuxt feature implementation
model: claude-sonnet-4-5
---

Create a detailed implementation plan for the following Vue/Nuxt feature.

## Feature Description

$ARGUMENTS

## Planning Framework

### 1. **Feature Breakdown**

**User Stories**
- As a [user type], I want [goal] so that [benefit]

**Technical Requirements**
- Components needed
- Pages/Routes affected
- Data fetching requirements
- State management needs
- API endpoints (if applicable)

**Dependencies**
- External packages
- Existing components to reuse
- API integrations

### 2. **Technical Specification**

**Frontend Architecture**
```
Pages
├── Feature page(s)
│   └── Uses composables
│       └── Call API services
│
Components
├── Container components (data + logic)
└── Presentational components (UI only)
│
Composables
├── Business logic
├── Data fetching
└── State management
```

**File Structure**
```
pages/
  feature/
    index.vue
    [id].vue
components/
  feature/
    FeatureList.vue
    FeatureItem.vue
    FeatureForm.vue
composables/
  useFeature.ts
  useFeatureForm.ts
types/
  feature.ts
```

### 3. **Implementation Steps**

**Phase 1: Setup & Foundation** (Est: X hours)
- [ ] Install dependencies
- [ ] Create type definitions
- [ ] Set up routing
- [ ] Create base components

**Phase 2: Core Functionality** (Est: X hours)
- [ ] Implement composables
- [ ] Build main components
- [ ] Integrate data fetching
- [ ] Add state management

**Phase 3: User Interface** (Est: X hours)
- [ ] Style components
- [ ] Add transitions/animations
- [ ] Implement responsive design
- [ ] Add loading states

**Phase 4: Integration** (Est: X hours)
- [ ] Connect to API
- [ ] Add error handling
- [ ] Implement validation
- [ ] Test edge cases

**Phase 5: Polish** (Est: X hours)
- [ ] Accessibility improvements
- [ ] Performance optimization
- [ ] SEO metadata
- [ ] Documentation

### 4. **Data Flow**

```
User Interaction
    ↓
Component Event
    ↓
Composable (Business Logic)
    ↓
API Service ($fetch)
    ↓
Backend API
    ↓
Response
    ↓
Update Reactive State
    ↓
Re-render Component
```

### 5. **Type Definitions**

```ts
// types/feature.ts
export interface Feature {
  id: string
  name: string
  description: string
  createdAt: string
}

export interface FeatureFormData {
  name: string
  description: string
}

export interface UseFeatureReturn {
  features: Ref<Feature[]>
  loading: Ref<boolean>
  error: Ref<Error | null>
  fetchFeatures: () => Promise<void>
  createFeature: (data: FeatureFormData) => Promise<void>
}
```

### 6. **State Management Strategy**

**Local State** (component-level)
```ts
const isOpen = ref(false)
const selectedId = ref<string | null>(null)
```

**Shared State** (composable)
```ts
export function useFeatureStore() {
  const features = useState<Feature[]>('features', () => [])
  return { features }
}
```

**Global State** (Pinia, if complex)
```ts
export const useFeatureStore = defineStore('feature', () => {
  const features = ref<Feature[]>([])
  const addFeature = (feature: Feature) => {
    features.value.push(feature)
  }
  return { features, addFeature }
})
```

### 7. **API Integration**

```ts
// composables/useFeature.ts
export function useFeature() {
  const config = useRuntimeConfig()

  const { data, pending, error, refresh } = useFetch<Feature[]>(
    `${config.public.apiBase}/features`,
    {
      key: 'features',
      lazy: true
    }
  )

  const createFeature = async (data: FeatureFormData) => {
    await $fetch(`${config.public.apiBase}/features`, {
      method: 'POST',
      body: data
    })
    await refresh()
  }

  return {
    features: data,
    loading: pending,
    error,
    createFeature,
    refresh
  }
}
```

### 8. **Success Criteria**

**Functionality**
- ✓ All user stories implemented
- ✓ Features work as specified
- ✓ Error handling in place
- ✓ Loading states present

**Code Quality**
- ✓ TypeScript strict mode
- ✓ No `any` types
- ✓ Components under 200 lines
- ✓ Logic extracted to composables

**Performance**
- ✓ Lazy loading where appropriate
- ✓ Optimized re-renders
- ✓ Proper caching
- ✓ Bundle size acceptable

**UX/Accessibility**
- ✓ Responsive design
- ✓ Keyboard navigation
- ✓ Screen reader friendly
- ✓ Clear error messages

**SEO** (if public pages)
- ✓ Meta tags
- ✓ Open Graph tags
- ✓ Structured data
- ✓ Proper headings

### 9. **Testing Strategy**

**Unit Tests** (Vitest)
- Composables
- Utility functions
- Business logic

**Component Tests** (Vitest + Vue Test Utils)
- Component rendering
- User interactions
- Props/emits

**E2E Tests** (Playwright)
- Critical user flows
- Form submissions
- Navigation

### 10. **Deployment Checklist**

- [ ] Environment variables configured
- [ ] API endpoints tested
- [ ] Error tracking set up (Sentry, etc.)
- [ ] Performance monitoring
- [ ] SEO verified
- [ ] Analytics events tracked

Provide a clear, actionable implementation plan with realistic time estimates.
