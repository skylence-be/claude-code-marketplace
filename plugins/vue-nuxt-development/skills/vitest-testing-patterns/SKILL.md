---
name: vitest-testing-patterns
description: Master Vitest testing for Vue 3 and Nuxt 4 including component testing (@vue/test-utils), composable testing, mocking strategies, Pinia store testing, snapshot testing, async operations, code coverage, SSR testing, and E2E with Playwright. Use when writing comprehensive test suites for Vue applications.
category: frontend
tags: [vitest, testing, vue-test-utils, mocking, coverage]
related_skills: [vue3-composition-api-patterns, typescript-vue-patterns, pinia-state-patterns]
---

# Vitest Testing Patterns

Comprehensive guide to testing Vue 3 and Nuxt 4 applications with Vitest, covering component testing with @vue/test-utils, composable testing strategies, mocking API calls and modules, Pinia store testing, snapshot testing, async operation handling, code coverage configuration, SSR testing, and E2E testing with Playwright.

## When to Use This Skill

- Writing unit tests for Vue 3 components with Vitest
- Testing composables and reusable logic independently
- Mocking API calls, modules, and external dependencies
- Testing Pinia stores with state and action verification
- Creating snapshot tests for component output
- Testing async operations and loading states
- Configuring code coverage reports
- Testing server-side rendering in Nuxt applications
- Implementing E2E tests with Playwright
- Setting up CI/CD test pipelines

## Core Concepts

### 1. Vitest Basics
- **describe/it blocks**: Test organization
- **expect assertions**: Test expectations
- **beforeEach/afterEach**: Setup and teardown
- **vi.mock**: Module mocking
- **vi.fn**: Function mocking

### 2. Vue Test Utils
- **mount**: Render component for testing
- **shallowMount**: Render without child components
- **wrapper**: Component instance for testing
- **trigger**: Simulate user interactions
- **emitted**: Check emitted events

### 3. Mocking Strategies
- **API mocking**: Mock fetch and $fetch calls
- **Module mocking**: Mock external modules
- **Composable mocking**: Mock custom composables
- **Timer mocking**: Fast-forward time
- **Store mocking**: Mock Pinia stores

### 4. Async Testing
- **async/await**: Handle promises in tests
- **waitFor**: Wait for conditions
- **nextTick**: Wait for Vue updates
- **flushPromises**: Resolve all promises
- **Testing loading states**: Verify UI during async

### 5. Coverage Configuration
- Istanbul for code coverage
- Coverage thresholds
- Ignoring files from coverage
- HTML coverage reports
- CI/CD integration

## Quick Start

```typescript
// Component test example
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Counter from '@/components/Counter.vue'

describe('Counter', () => {
  it('renders initial count', () => {
    const wrapper = mount(Counter, {
      props: { initialCount: 5 }
    })

    expect(wrapper.text()).toContain('Count: 5')
  })

  it('increments on button click', async () => {
    const wrapper = mount(Counter)

    await wrapper.find('button').trigger('click')

    expect(wrapper.text()).toContain('Count: 1')
  })
})
```

## Fundamental Patterns

### Pattern 1: Component Testing Basics

```typescript
// components/UserCard.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import UserCard from '@/components/UserCard.vue'
import type { User } from '@/types'

describe('UserCard', () => {
  const mockUser: User = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'admin'
  }

  let wrapper: VueWrapper

  beforeEach(() => {
    wrapper = mount(UserCard, {
      props: {
        user: mockUser
      }
    })
  })

  it('renders user information', () => {
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
  })

  it('displays admin badge for admin users', () => {
    const badge = wrapper.find('[data-test="admin-badge"]')
    expect(badge.exists()).toBe(true)
  })

  it('does not display admin badge for regular users', () => {
    wrapper = mount(UserCard, {
      props: {
        user: { ...mockUser, role: 'user' }
      }
    })

    const badge = wrapper.find('[data-test="admin-badge"]')
    expect(badge.exists()).toBe(false)
  })

  it('emits edit event when edit button is clicked', async () => {
    await wrapper.find('[data-test="edit-button"]').trigger('click')

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0]).toEqual([mockUser])
  })

  it('emits delete event with user id', async () => {
    await wrapper.find('[data-test="delete-button"]').trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')?.[0]).toEqual([mockUser.id])
  })

  it('applies correct CSS classes', () => {
    expect(wrapper.classes()).toContain('user-card')
    expect(wrapper.find('.user-info').exists()).toBe(true)
  })

  it('renders with custom props', () => {
    wrapper = mount(UserCard, {
      props: {
        user: mockUser,
        showEmail: false
      }
    })

    expect(wrapper.text()).not.toContain('john@example.com')
  })
})
```

### Pattern 2: Testing User Interactions

```typescript
// components/SearchBox.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchBox from '@/components/SearchBox.vue'

describe('SearchBox', () => {
  it('updates model value on input', async () => {
    const wrapper = mount(SearchBox)
    const input = wrapper.find('input')

    await input.setValue('test query')

    expect((input.element as HTMLInputElement).value).toBe('test query')
  })

  it('emits search event on submit', async () => {
    const wrapper = mount(SearchBox)

    await wrapper.find('input').setValue('test')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')?.[0]).toEqual(['test'])
  })

  it('debounces input changes', async () => {
    vi.useFakeTimers()

    const onSearch = vi.fn()
    const wrapper = mount(SearchBox, {
      props: {
        debounce: 300,
        onSearch
      }
    })

    await wrapper.find('input').setValue('test')

    // Should not call immediately
    expect(onSearch).not.toHaveBeenCalled()

    // Fast-forward time
    vi.advanceTimersByTime(300)

    expect(onSearch).toHaveBeenCalledWith('test')

    vi.useRealTimers()
  })

  it('clears input when clear button is clicked', async () => {
    const wrapper = mount(SearchBox)

    await wrapper.find('input').setValue('test')
    await wrapper.find('[data-test="clear-button"]').trigger('click')

    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('')
    expect(wrapper.emitted('clear')).toBeTruthy()
  })

  it('disables submit when input is empty', async () => {
    const wrapper = mount(SearchBox)

    const submitButton = wrapper.find('button[type="submit"]')
    expect((submitButton.element as HTMLButtonElement).disabled).toBe(true)

    await wrapper.find('input').setValue('test')
    expect((submitButton.element as HTMLButtonElement).disabled).toBe(false)
  })
})
```

### Pattern 3: Testing Composables

```typescript
// composables/useCounter.test.ts
import { describe, it, expect } from 'vitest'
import { useCounter } from '@/composables/useCounter'

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { count } = useCounter()
    expect(count.value).toBe(0)
  })

  it('initializes with custom value', () => {
    const { count } = useCounter(10)
    expect(count.value).toBe(10)
  })

  it('increments count', () => {
    const { count, increment } = useCounter()

    increment()
    expect(count.value).toBe(1)

    increment()
    expect(count.value).toBe(2)
  })

  it('decrements count', () => {
    const { count, decrement } = useCounter(5)

    decrement()
    expect(count.value).toBe(4)
  })

  it('resets to initial value', () => {
    const { count, increment, reset } = useCounter(10)

    increment()
    increment()
    expect(count.value).toBe(12)

    reset()
    expect(count.value).toBe(10)
  })

  it('computes doubled value', () => {
    const { count, doubled, increment } = useCounter(3)

    expect(doubled.value).toBe(6)

    increment()
    expect(doubled.value).toBe(8)
  })
})

// composables/useFetch.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useFetch } from '@/composables/useFetch'

describe('useFetch', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('fetches data successfully', async () => {
    const mockData = { id: 1, name: 'Test' }

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    } as Response)

    const { data, loading, error, execute } = useFetch('/api/test', {
      immediate: false
    })

    expect(loading.value).toBe(false)
    expect(data.value).toBeNull()

    await execute()

    expect(data.value).toEqual(mockData)
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('handles errors', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))

    const { data, error, execute } = useFetch('/api/test', {
      immediate: false
    })

    await execute()

    expect(data.value).toBeNull()
    expect(error.value).toBeInstanceOf(Error)
    expect(error.value?.message).toBe('Network error')
  })

  it('sets loading state correctly', async () => {
    vi.mocked(fetch).mockImplementationOnce(
      () => new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({})
      } as Response), 100))
    )

    const { loading, execute } = useFetch('/api/test', {
      immediate: false
    })

    expect(loading.value).toBe(false)

    const promise = execute()
    expect(loading.value).toBe(true)

    await promise
    expect(loading.value).toBe(false)
  })

  it('calls onSuccess callback', async () => {
    const onSuccess = vi.fn()
    const mockData = { id: 1 }

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    } as Response)

    const { execute } = useFetch('/api/test', {
      immediate: false,
      onSuccess
    })

    await execute()

    expect(onSuccess).toHaveBeenCalledWith(mockData)
  })
})
```

### Pattern 4: Mocking API Calls

```typescript
// components/UserList.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import UserList from '@/components/UserList.vue'

// Mock the $fetch function
vi.mock('#app', () => ({
  $fetch: vi.fn()
}))

describe('UserList', () => {
  const mockUsers = [
    { id: 1, name: 'John', email: 'john@example.com' },
    { id: 2, name: 'Jane', email: 'jane@example.com' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays loading state initially', () => {
    vi.mocked($fetch).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    const wrapper = mount(UserList)
    expect(wrapper.text()).toContain('Loading')
  })

  it('displays users after fetching', async () => {
    vi.mocked($fetch).mockResolvedValueOnce(mockUsers)

    const wrapper = mount(UserList)

    await flushPromises()

    expect(wrapper.text()).toContain('John')
    expect(wrapper.text()).toContain('Jane')
    expect(wrapper.findAll('[data-test="user-item"]')).toHaveLength(2)
  })

  it('displays error message on fetch failure', async () => {
    vi.mocked($fetch).mockRejectedValueOnce(new Error('API Error'))

    const wrapper = mount(UserList)

    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load users')
  })

  it('refetches data when refresh is clicked', async () => {
    vi.mocked($fetch).mockResolvedValue(mockUsers)

    const wrapper = mount(UserList)
    await flushPromises()

    expect($fetch).toHaveBeenCalledTimes(1)

    await wrapper.find('[data-test="refresh-button"]').trigger('click')
    await flushPromises()

    expect($fetch).toHaveBeenCalledTimes(2)
  })
})
```

### Pattern 5: Testing Pinia Stores

```typescript
// stores/user.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types'

// Mock $fetch
vi.mock('#app', () => ({
  $fetch: vi.fn()
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default state', () => {
    const store = useUserStore()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('logs in successfully', async () => {
    const store = useUserStore()
    const mockUser: User = {
      id: 1,
      name: 'John',
      email: 'john@example.com',
      role: 'user'
    }
    const mockToken = 'mock-token'

    vi.mocked($fetch).mockResolvedValueOnce({
      user: mockUser,
      token: mockToken
    })

    const result = await store.login('john@example.com', 'password')

    expect(result.success).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe(mockToken)
    expect(store.isAuthenticated).toBe(true)
    expect(store.loading).toBe(false)
  })

  it('handles login failure', async () => {
    const store = useUserStore()

    vi.mocked($fetch).mockRejectedValueOnce(new Error('Invalid credentials'))

    const result = await store.login('wrong@example.com', 'wrong')

    expect(result.success).toBe(false)
    expect(result.error).toBe('Invalid credentials')
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('logs out correctly', async () => {
    const store = useUserStore()

    // Set up authenticated state
    store.user = {
      id: 1,
      name: 'John',
      email: 'john@example.com',
      role: 'user'
    }
    store.token = 'mock-token'

    await store.logout()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('computes isAdmin correctly', () => {
    const store = useUserStore()

    store.user = {
      id: 1,
      name: 'Admin',
      email: 'admin@example.com',
      role: 'admin'
    }

    expect(store.isAdmin).toBe(true)

    store.user = {
      id: 2,
      name: 'User',
      email: 'user@example.com',
      role: 'user'
    }

    expect(store.isAdmin).toBe(false)
  })

  it('handles $patch updates', () => {
    const store = useUserStore()

    store.$patch({
      user: {
        id: 1,
        name: 'John',
        email: 'john@example.com',
        role: 'user'
      },
      token: 'test-token'
    })

    expect(store.user?.name).toBe('John')
    expect(store.token).toBe('test-token')
  })

  it('resets to initial state', () => {
    const store = useUserStore()

    store.user = {
      id: 1,
      name: 'John',
      email: 'john@example.com',
      role: 'user'
    }
    store.token = 'test-token'

    store.$reset()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
  })
})
```

### Pattern 6: Snapshot Testing

```typescript
// components/Card.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Card from '@/components/Card.vue'

describe('Card', () => {
  it('matches snapshot with default props', () => {
    const wrapper = mount(Card, {
      props: {
        title: 'Test Card',
        content: 'This is test content'
      }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })

  it('matches snapshot with custom variant', () => {
    const wrapper = mount(Card, {
      props: {
        title: 'Warning Card',
        content: 'Warning message',
        variant: 'warning'
      }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })

  it('matches snapshot with slot content', () => {
    const wrapper = mount(Card, {
      props: {
        title: 'Slot Card'
      },
      slots: {
        default: '<p>Custom slot content</p>',
        footer: '<button>Action</button>'
      }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })

  it('matches inline snapshot', () => {
    const wrapper = mount(Card, {
      props: {
        title: 'Test',
        content: 'Content'
      }
    })

    expect(wrapper.html()).toMatchInlineSnapshot(`
      "<div class="card">
        <h3 class="card-title">Test</h3>
        <div class="card-content">Content</div>
      </div>"
    `)
  })
})
```

### Pattern 7: Testing Async Operations

```typescript
// components/AsyncComponent.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AsyncComponent from '@/components/AsyncComponent.vue'

describe('AsyncComponent', () => {
  it('handles async data loading', async () => {
    const mockData = { id: 1, name: 'Test' }

    vi.mocked($fetch).mockResolvedValueOnce(mockData)

    const wrapper = mount(AsyncComponent)

    // Initially loading
    expect(wrapper.text()).toContain('Loading')

    // Wait for promises to resolve
    await flushPromises()

    // Data loaded
    expect(wrapper.text()).toContain('Test')
    expect(wrapper.text()).not.toContain('Loading')
  })

  it('handles async errors', async () => {
    vi.mocked($fetch).mockRejectedValueOnce(new Error('Load failed'))

    const wrapper = mount(AsyncComponent)

    await flushPromises()

    expect(wrapper.text()).toContain('Error')
    expect(wrapper.text()).toContain('Load failed')
  })

  it('waits for Vue updates with nextTick', async () => {
    const wrapper = mount(AsyncComponent)

    wrapper.vm.someReactiveProperty = 'new value'

    // Wait for Vue to update DOM
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('new value')
  })

  it('handles multiple async operations', async () => {
    vi.mocked($fetch)
      .mockResolvedValueOnce({ users: [] })
      .mockResolvedValueOnce({ posts: [] })

    const wrapper = mount(AsyncComponent)

    await flushPromises()

    expect(wrapper.vm.users).toEqual([])
    expect(wrapper.vm.posts).toEqual([])
  })
})
```

### Pattern 8: Testing with Provide/Inject

```typescript
// components/ChildWithInject.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChildWithInject from '@/components/ChildWithInject.vue'

describe('ChildWithInject', () => {
  it('receives injected values', () => {
    const wrapper = mount(ChildWithInject, {
      global: {
        provide: {
          theme: 'dark',
          user: {
            id: 1,
            name: 'John'
          }
        }
      }
    })

    expect(wrapper.text()).toContain('dark')
    expect(wrapper.text()).toContain('John')
  })

  it('uses default values when not provided', () => {
    const wrapper = mount(ChildWithInject)

    expect(wrapper.text()).toContain('light') // default theme
  })
})
```

### Pattern 9: Testing Slots

```typescript
// components/Modal.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '@/components/Modal.vue'

describe('Modal', () => {
  it('renders default slot content', () => {
    const wrapper = mount(Modal, {
      slots: {
        default: '<p>Modal content</p>'
      }
    })

    expect(wrapper.html()).toContain('<p>Modal content</p>')
  })

  it('renders multiple slots', () => {
    const wrapper = mount(Modal, {
      slots: {
        header: '<h1>Title</h1>',
        default: '<p>Content</p>',
        footer: '<button>Close</button>'
      }
    })

    expect(wrapper.html()).toContain('<h1>Title</h1>')
    expect(wrapper.html()).toContain('<p>Content</p>')
    expect(wrapper.html()).toContain('<button>Close</button>')
  })

  it('renders scoped slots', () => {
    const wrapper = mount(Modal, {
      slots: {
        default: `
          <template #default="{ data }">
            <p>{{ data.message }}</p>
          </template>
        `
      }
    })

    expect(wrapper.text()).toContain('message')
  })
})
```

### Pattern 10: Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    // Test environment
    environment: 'jsdom',

    // Global setup
    globals: true,
    setupFiles: ['./tests/setup.ts'],

    // Coverage configuration
    coverage: {
      provider: 'istanbul',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.ts',
        '**/*.spec.ts',
        'src/types/**'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    },

    // Reporters
    reporters: ['verbose'],

    // Test timeout
    testTimeout: 10000,

    // Mock reset
    mockReset: true,
    clearMocks: true,
    restoreMocks: true
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '~': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

```typescript
// tests/setup.ts
import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// Global test setup

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
}

// Configure Vue Test Utils
config.global.stubs = {
  // Stub out Nuxt components
  NuxtLink: true,
  ClientOnly: true
}

// Add custom matchers if needed
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling
    return {
      pass,
      message: () =>
        `expected ${received} to be within range ${floor} - ${ceiling}`
    }
  }
})
```

## Advanced Patterns

### Pattern 11: E2E Testing with Playwright

```typescript
// tests/e2e/user-flow.spec.ts
import { test, expect } from '@playwright/test'

test.describe('User Authentication Flow', () => {
  test('user can login', async ({ page }) => {
    await page.goto('/')

    // Navigate to login
    await page.click('text=Login')
    await expect(page).toHaveURL(/.*login/)

    // Fill form
    await page.fill('[data-test="email"]', 'user@example.com')
    await page.fill('[data-test="password"]', 'password123')

    // Submit
    await page.click('[data-test="submit"]')

    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/)
    await expect(page.locator('text=Welcome')).toBeVisible()
  })

  test('displays error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-test="email"]', 'wrong@example.com')
    await page.fill('[data-test="password"]', 'wrong')
    await page.click('[data-test="submit"]')

    await expect(page.locator('.error-message')).toContainText('Invalid credentials')
  })
})

test.describe('Product Search', () => {
  test('searches and filters products', async ({ page }) => {
    await page.goto('/products')

    // Search
    await page.fill('[data-test="search"]', 'laptop')
    await page.waitForTimeout(300) // debounce

    // Verify results
    const products = page.locator('[data-test="product-item"]')
    await expect(products).toHaveCount(5)

    // Apply filter
    await page.click('[data-test="filter-category"]')
    await page.click('text=Electronics')

    // Verify filtered results
    await expect(products).toHaveCount(3)
  })
})

// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
})
```

## Testing Strategies

### Component Testing Checklist

- Render with different prop combinations
- Test user interactions (click, input, submit)
- Verify emitted events with correct payloads
- Test conditional rendering (v-if, v-show)
- Test computed properties
- Test watchers and their side effects
- Test slots (default, named, scoped)
- Test CSS classes and styling
- Test accessibility attributes
- Test error states and loading states

### Composable Testing Checklist

- Test with default parameters
- Test with custom parameters
- Test return values and their types
- Test reactive state updates
- Test side effects (localStorage, API calls)
- Test error handling
- Test cleanup on unmount
- Test with different timing scenarios

### Store Testing Checklist

- Test initial state
- Test all actions with success cases
- Test all actions with error cases
- Test getters with different states
- Test state mutations
- Test $patch functionality
- Test $reset functionality
- Test store composition

## Common Pitfalls

### Pitfall 1: Not Waiting for Async Operations

```typescript
// WRONG: Not waiting
it('loads data', () => {
  const wrapper = mount(Component)
  expect(wrapper.text()).toContain('Data') // Fails - data not loaded yet
})

// CORRECT: Wait for promises
it('loads data', async () => {
  const wrapper = mount(Component)
  await flushPromises()
  expect(wrapper.text()).toContain('Data')
})
```

### Pitfall 2: Not Mocking External Dependencies

```typescript
// WRONG: Real API calls in tests
it('fetches users', async () => {
  const wrapper = mount(UserList)
  // Calls real API - slow and unreliable
})

// CORRECT: Mock API calls
it('fetches users', async () => {
  vi.mocked($fetch).mockResolvedValueOnce([{ id: 1, name: 'John' }])
  const wrapper = mount(UserList)
  await flushPromises()
  expect(wrapper.text()).toContain('John')
})
```

### Pitfall 3: Testing Implementation Details

```typescript
// WRONG: Testing internal state
it('updates internalCounter', () => {
  const wrapper = mount(Component)
  expect(wrapper.vm.internalCounter).toBe(0) // Fragile
})

// CORRECT: Test behavior
it('displays updated count', async () => {
  const wrapper = mount(Component)
  await wrapper.find('button').trigger('click')
  expect(wrapper.text()).toContain('Count: 1')
})
```

## Best Practices

1. **Test behavior, not implementation** - Focus on what users see
2. **Use data-test attributes** for selecting elements
3. **Mock external dependencies** for speed and reliability
4. **Write descriptive test names** that explain what's being tested
5. **Use beforeEach for common setup** to keep tests DRY
6. **Test edge cases and error states** not just happy paths
7. **Keep tests independent** - no shared state between tests
8. **Use async/await consistently** for async operations
9. **Configure coverage thresholds** to maintain quality
10. **Run tests in CI/CD** for automated quality checks

## Resources

- **Vitest Documentation**: https://vitest.dev
- **Vue Test Utils**: https://test-utils.vuejs.org
- **Playwright**: https://playwright.dev
- **Testing Library**: https://testing-library.com/docs/vue-testing-library/intro
- **Pinia Testing**: https://pinia.vuejs.org/cookbook/testing.html
