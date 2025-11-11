---
name: nuxt-modules-integration
description: Master Nuxt 4 modules integration including essential modules (@nuxtjs/tailwindcss, @pinia/nuxt), module configuration, auto-imports, creating custom modules, runtime config, plugin system, middleware registration, server routes, build hooks, and layer architecture. Use when extending Nuxt functionality or building reusable module packages.
category: frontend
tags: [nuxt4, modules, plugins, configuration, layers]
related_skills: [nuxt4-ssr-optimization, vue3-composition-api-patterns, pinia-state-patterns]
---

# Nuxt Modules Integration

Comprehensive guide to integrating and creating Nuxt 4 modules, covering essential module ecosystem (@nuxtjs/tailwindcss, @pinia/nuxt, etc.), module configuration, auto-imports, custom module development, runtime vs app config, plugin system, middleware registration, server middleware, build hooks, and layer architecture for code sharing.

## When to Use This Skill

- Integrating popular Nuxt modules into your project
- Configuring modules for optimal performance and features
- Creating custom Nuxt modules for reusable functionality
- Setting up auto-imports for components and composables
- Managing runtime configuration and environment variables
- Implementing Vue plugins through Nuxt plugin system
- Registering middleware for route protection
- Adding server middleware for request/response handling
- Using build hooks for custom build processes
- Implementing layer architecture for multi-project code sharing

## Core Concepts

### 1. Module System
- **Official modules**: Maintained by Nuxt team
- **Community modules**: Third-party integrations
- **Module hooks**: Lifecycle for customization
- **Module composition**: Modules using other modules
- **Module publishing**: Share as npm packages

### 2. Configuration
- **Runtime config**: Environment-based configuration
- **App config**: Static application configuration
- **Public vs private**: Client vs server-only config
- **Type safety**: TypeScript configuration types
- **Environment variables**: .env file support

### 3. Auto-imports
- **Component auto-import**: Automatic component registration
- **Composable auto-import**: Use composables without imports
- **Utility auto-import**: Helper functions globally available
- **Custom directories**: Configure import sources
- **Type generation**: Automatic TypeScript types

### 4. Plugin System
- **Vue plugins**: Integrate Vue ecosystem plugins
- **Client/server plugins**: Target-specific plugins
- **Plugin order**: Control initialization sequence
- **Parallel plugins**: Non-blocking plugin loading
- **Plugin hooks**: Access Nuxt context

### 5. Build Hooks
- **Vite hooks**: Customize Vite build
- **Webpack hooks**: Legacy webpack configuration
- **Nitro hooks**: Server build customization
- **Module hooks**: Extend module functionality
- **Build-time optimization**: Tree-shaking, minification

## Quick Start

```typescript
// nuxt.config.ts - Basic module integration
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxt/image'
  ],

  // Runtime config
  runtimeConfig: {
    apiSecret: '', // Server-only
    public: {
      apiBase: '' // Client and server
    }
  },

  // Auto-imports
  components: [
    { path: '~/components', pathPrefix: false }
  ],

  imports: {
    dirs: ['composables', 'utils']
  }
})
```

## Fundamental Patterns

### Pattern 1: Essential Nuxt Modules

```typescript
// nuxt.config.ts - Popular module configuration
export default defineNuxtConfig({
  modules: [
    // Styling
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',

    // State management
    '@pinia/nuxt',

    // SEO
    '@nuxtjs/seo',

    // Images
    '@nuxt/image',

    // Icons
    'nuxt-icon',

    // Forms
    '@vee-validate/nuxt',

    // UI
    '@nuxt/ui',

    // Analytics
    '@nuxtjs/google-analytics',

    // I18n
    '@nuxtjs/i18n',

    // PWA
    '@vite-pwa/nuxt'
  ],

  // Tailwind configuration
  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
    configPath: 'tailwind.config',
    exposeConfig: false,
    viewer: true
  },

  // Color mode (dark mode)
  colorMode: {
    preference: 'system',
    fallback: 'light',
    classSuffix: '',
    storageKey: 'nuxt-color-mode'
  },

  // Pinia configuration
  pinia: {
    autoImports: [
      'defineStore',
      'storeToRefs'
    ]
  },

  // Image optimization
  image: {
    format: ['webp', 'avif'],
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      xxl: 1536
    },
    provider: 'ipx'
  },

  // Nuxt UI configuration
  ui: {
    global: true,
    icons: ['heroicons', 'lucide']
  },

  // I18n configuration
  i18n: {
    locales: [
      { code: 'en', iso: 'en-US', file: 'en.json' },
      { code: 'es', iso: 'es-ES', file: 'es.json' }
    ],
    defaultLocale: 'en',
    langDir: 'locales',
    strategy: 'prefix_except_default',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root'
    }
  },

  // PWA configuration
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'My Nuxt App',
      short_name: 'NuxtApp',
      theme_color: '#ffffff',
      icons: [
        {
          src: 'icon-192x192.png',
          sizes: '192x192',
          type: 'image/png'
        },
        {
          src: 'icon-512x512.png',
          sizes: '512x512',
          type: 'image/png'
        }
      ]
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico}']
    }
  }
})
```

### Pattern 2: Runtime Configuration

```typescript
// nuxt.config.ts - Runtime and app config
export default defineNuxtConfig({
  // Runtime config (can use environment variables)
  runtimeConfig: {
    // Private (server-only)
    apiSecret: process.env.API_SECRET,
    databaseUrl: process.env.DATABASE_URL,
    jwtSecret: process.env.JWT_SECRET,

    // Public (client and server)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'https://api.example.com',
      appVersion: '1.0.0',
      googleAnalyticsId: process.env.NUXT_PUBLIC_GA_ID,
      stripePublicKey: process.env.NUXT_PUBLIC_STRIPE_KEY
    }
  },

  // App config (static, type-safe)
  appConfig: {
    title: 'My Nuxt App',
    theme: {
      primary: '#007bff',
      secondary: '#6c757d'
    },
    nav: {
      links: [
        { label: 'Home', to: '/' },
        { label: 'About', to: '/about' }
      ]
    }
  }
})
```

```vue
<!-- Using runtime config in components -->
<script setup lang="ts">
const config = useRuntimeConfig()

// Access public config (client and server)
const apiBase = config.public.apiBase
const version = config.public.appVersion

// Server-only usage
const fetchData = async () => {
  // apiSecret is only available server-side
  const data = await $fetch('/api/data')
  return data
}
</script>

<template>
  <div>
    <p>API Base: {{ apiBase }}</p>
    <p>Version: {{ version }}</p>
  </div>
</template>
```

```typescript
// server/api/data.get.ts - Using runtime config in server route
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  // Access private config (server-only)
  const apiSecret = config.apiSecret

  const response = await fetch('https://external-api.com/data', {
    headers: {
      'Authorization': `Bearer ${apiSecret}`
    }
  })

  return response.json()
})
```

```typescript
// app.config.ts - Define app config
export default defineAppConfig({
  title: 'My Application',
  theme: {
    primary: '#007bff',
    secondary: '#6c757d',
    dark: false
  },
  ui: {
    primary: 'blue',
    gray: 'slate',
    notifications: {
      position: 'top-0 bottom-auto' as const
    }
  }
})
```

### Pattern 3: Auto-imports Configuration

```typescript
// nuxt.config.ts - Advanced auto-imports
export default defineNuxtConfig({
  // Component auto-imports
  components: [
    {
      path: '~/components',
      pathPrefix: false
    },
    {
      path: '~/components/ui',
      prefix: 'Ui',
      pathPrefix: false
    },
    {
      path: '~/components/forms',
      prefix: 'Form',
      extensions: ['vue']
    },
    {
      path: '~/components/layout',
      global: true // Always imported
    }
  ],

  // Composables and utilities auto-import
  imports: {
    dirs: [
      'composables/**',
      'utils/**',
      'stores/**'
    ],
    presets: [
      {
        from: 'vue-i18n',
        imports: ['useI18n', 'useLocalePath']
      },
      {
        from: '@vueuse/core',
        imports: ['useMouse', 'useWindowSize', 'useLocalStorage']
      }
    ]
  },

  // Auto-import configuration
  autoImport: {
    // Disable if you want explicit imports
    enabled: true,
    // Add type declarations
    dts: '.nuxt/types/auto-imports.d.ts'
  }
})
```

```vue
<!-- Components are auto-imported -->
<template>
  <div>
    <!-- From ~/components/Button.vue -->
    <Button>Click me</Button>

    <!-- From ~/components/ui/Card.vue with prefix -->
    <UiCard>
      <template #header>Title</template>
      Content
    </UiCard>

    <!-- From ~/components/forms/Input.vue with prefix -->
    <FormInput v-model="value" />
  </div>
</template>

<script setup lang="ts">
// Composables are auto-imported
const { data } = await useFetch('/api/data')

// Utilities are auto-imported
const formatted = formatDate(new Date())

// Stores are auto-imported
const userStore = useUserStore()

// Vue functions are auto-imported
const count = ref(0)
const doubled = computed(() => count.value * 2)

// VueUse composables are auto-imported (if configured)
const { x, y } = useMouse()
const { width, height } = useWindowSize()
</script>
```

### Pattern 4: Creating Custom Plugins

```typescript
// plugins/vue-toast.client.ts - Client-only plugin
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(Toast, {
    position: 'top-right',
    timeout: 3000,
    closeOnClick: true,
    pauseOnHover: true
  })

  // Make toast available globally
  return {
    provide: {
      toast: nuxtApp.vueApp.config.globalProperties.$toast
    }
  }
})

// Usage in components
const { $toast } = useNuxtApp()
$toast.success('Success message!')
```

```typescript
// plugins/api.ts - API client plugin (both client and server)
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  class ApiClient {
    private baseUrl: string

    constructor(baseUrl: string) {
      this.baseUrl = baseUrl
    }

    async get<T>(endpoint: string): Promise<T> {
      return $fetch<T>(`${this.baseUrl}${endpoint}`)
    }

    async post<T>(endpoint: string, data: any): Promise<T> {
      return $fetch<T>(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        body: data
      })
    }
  }

  const api = new ApiClient(config.public.apiBase)

  return {
    provide: {
      api
    }
  }
})

// Usage
const { $api } = useNuxtApp()
const data = await $api.get('/users')
```

```typescript
// plugins/error-handler.ts - Error handling plugin
export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.config.errorHandler = (error, instance, info) => {
    console.error('Global error:', error)
    console.error('Component:', instance)
    console.error('Error info:', info)

    // Send to error tracking service
    if (process.client) {
      // Sentry, Bugsnag, etc.
      logErrorToService(error)
    }
  }

  // Handle Nuxt errors
  nuxtApp.hook('vue:error', (error, instance, info) => {
    console.error('Nuxt error:', error)
  })
})
```

```typescript
// plugins/01.auth.ts - Plugin with order control (runs first)
export default defineNuxtPlugin(async (nuxtApp) => {
  const userStore = useUserStore()
  const token = useCookie('auth-token')

  // Restore authentication on app initialization
  if (token.value) {
    try {
      await userStore.fetchUser()
    } catch (error) {
      console.error('Failed to restore auth:', error)
      token.value = null
    }
  }
})
```

### Pattern 5: Creating Custom Nuxt Modules

```typescript
// modules/my-module/index.ts - Custom module
import { defineNuxtModule, createResolver, addComponent, addImports } from '@nuxt/kit'

export interface ModuleOptions {
  enabled?: boolean
  apiKey?: string
}

export default defineNuxtModule<ModuleOptions>({
  meta: {
    name: 'my-module',
    configKey: 'myModule',
    compatibility: {
      nuxt: '^3.0.0'
    }
  },
  defaults: {
    enabled: true,
    apiKey: ''
  },
  setup(options, nuxt) {
    if (!options.enabled) return

    const resolver = createResolver(import.meta.url)

    // Add runtime config
    nuxt.options.runtimeConfig.public.myModule = {
      apiKey: options.apiKey
    }

    // Add components
    addComponent({
      name: 'MyModuleButton',
      filePath: resolver.resolve('./runtime/components/Button.vue')
    })

    // Add composables
    addImports({
      name: 'useMyModule',
      as: 'useMyModule',
      from: resolver.resolve('./runtime/composables/useMyModule')
    })

    // Add plugin
    nuxt.hook('app:resolve', () => {
      nuxt.options.plugins.push(
        resolver.resolve('./runtime/plugin')
      )
    })

    // Add CSS
    nuxt.options.css.push(
      resolver.resolve('./runtime/styles/main.css')
    )

    // Add server middleware
    nuxt.hook('nitro:config', (nitroConfig) => {
      nitroConfig.middleware = nitroConfig.middleware || []
      nitroConfig.middleware.push(
        resolver.resolve('./runtime/server/middleware/logger')
      )
    })

    console.log('My module initialized with API key:', options.apiKey)
  }
})
```

```typescript
// modules/my-module/runtime/composables/useMyModule.ts
export const useMyModule = () => {
  const config = useRuntimeConfig()

  const apiKey = config.public.myModule.apiKey

  const fetchData = async (endpoint: string) => {
    return await $fetch(endpoint, {
      headers: {
        'X-API-Key': apiKey
      }
    })
  }

  return {
    apiKey,
    fetchData
  }
}
```

```typescript
// Using custom module in nuxt.config.ts
export default defineNuxtConfig({
  modules: [
    '~/modules/my-module'
  ],

  myModule: {
    enabled: true,
    apiKey: process.env.MY_MODULE_API_KEY
  }
})
```

### Pattern 6: Middleware Registration

```typescript
// middleware/auth.ts - Route middleware
export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore()

  // Redirect to login if not authenticated
  if (!userStore.isAuthenticated) {
    return navigateTo('/login')
  }

  // Check role permissions
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    return abortNavigation({
      statusCode: 403,
      message: 'Forbidden'
    })
  }
})
```

```typescript
// middleware/logging.global.ts - Global middleware
export default defineNuxtRouteMiddleware((to, from) => {
  console.log('Navigating from', from.path, 'to', to.path)

  // Track page views
  if (process.client) {
    // Analytics
    trackPageView(to.path)
  }
})
```

```typescript
// server/middleware/logger.ts - Server middleware
export default defineEventHandler((event) => {
  const start = Date.now()

  console.log(`[${new Date().toISOString()}] ${event.method} ${event.path}`)

  event.node.res.on('finish', () => {
    const duration = Date.now() - start
    console.log(`[${new Date().toISOString()}] ${event.method} ${event.path} - ${event.node.res.statusCode} (${duration}ms)`)
  })
})
```

### Pattern 7: Server Routes and Utilities

```typescript
// server/api/users/index.get.ts
import { defineEventHandler, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)

  const users = await prisma.user.findMany({
    take: parseInt(query.limit as string) || 10,
    skip: parseInt(query.offset as string) || 0
  })

  return {
    data: users,
    total: await prisma.user.count()
  }
})
```

```typescript
// server/utils/auth.ts - Server utility (auto-imported)
import jwt from 'jsonwebtoken'

export const verifyToken = (token: string) => {
  const config = useRuntimeConfig()

  try {
    return jwt.verify(token, config.jwtSecret)
  } catch (error) {
    throw createError({
      statusCode: 401,
      message: 'Invalid token'
    })
  }
}

export const generateToken = (userId: number) => {
  const config = useRuntimeConfig()

  return jwt.sign({ userId }, config.jwtSecret, {
    expiresIn: '7d'
  })
}
```

```typescript
// server/api/protected.get.ts - Using server utilities
export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'auth-token')

  if (!token) {
    throw createError({
      statusCode: 401,
      message: 'Unauthorized'
    })
  }

  // Auto-imported server utility
  const payload = verifyToken(token)

  const user = await prisma.user.findUnique({
    where: { id: payload.userId }
  })

  return user
})
```

### Pattern 8: Build Hooks and Optimization

```typescript
// nuxt.config.ts - Build hooks
export default defineNuxtConfig({
  hooks: {
    // Build hooks
    'build:before': () => {
      console.log('Build starting...')
    },
    'build:done': () => {
      console.log('Build complete!')
    },

    // Page hooks
    'pages:extend': (pages) => {
      // Add custom routes
      pages.push({
        name: 'custom-page',
        path: '/custom',
        file: '~/pages/custom.vue'
      })
    },

    // Component hooks
    'components:extend': (components) => {
      // Filter or modify auto-imported components
      console.log(`Found ${components.length} components`)
    }
  },

  // Vite configuration
  vite: {
    plugins: [],
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            // Separate vendor chunks
            'vue-vendor': ['vue', 'vue-router'],
            'pinia-vendor': ['pinia']
          }
        }
      }
    },
    optimizeDeps: {
      include: ['vue', 'vue-router', 'pinia']
    }
  },

  // Nitro configuration
  nitro: {
    compressPublicAssets: true,
    minify: true,
    prerender: {
      crawlLinks: true,
      routes: ['/sitemap.xml']
    }
  }
})
```

### Pattern 9: Layer Architecture

```typescript
// base-layer/nuxt.config.ts - Shared base layer
export default defineNuxtConfig({
  components: [
    { path: '~/components', prefix: 'Base' }
  ],

  css: ['~/assets/css/base.css'],

  runtimeConfig: {
    public: {
      baseUrl: process.env.BASE_URL
    }
  }
})
```

```typescript
// main-app/nuxt.config.ts - Main app extends base layer
export default defineNuxtConfig({
  extends: [
    '../base-layer' // Relative path
    // Or published layer: '@my-org/base-layer'
  ],

  // Override or extend base layer config
  components: [
    { path: '~/components' }
  ],

  modules: [
    '@nuxtjs/tailwindcss'
  ]
})
```

## Advanced Patterns

### Pattern 10: Module Development Best Practices

```typescript
// modules/analytics/index.ts - Production-ready module
import { defineNuxtModule, createResolver, addPlugin, addImports, useLogger } from '@nuxt/kit'
import { defu } from 'defu'

export interface ModuleOptions {
  enabled?: boolean
  trackingId?: string
  debug?: boolean
  router?: {
    trackPageView?: boolean
    trackEvents?: boolean
  }
}

export default defineNuxtModule<ModuleOptions>({
  meta: {
    name: '@my-org/analytics',
    configKey: 'analytics',
    compatibility: {
      nuxt: '^3.0.0 || ^4.0.0'
    }
  },
  defaults: {
    enabled: true,
    debug: false,
    router: {
      trackPageView: true,
      trackEvents: true
    }
  },
  async setup(options, nuxt) {
    const logger = useLogger('analytics')

    // Validate required options
    if (!options.trackingId) {
      logger.warn('No tracking ID provided, module disabled')
      return
    }

    if (!options.enabled) {
      logger.info('Module disabled')
      return
    }

    const resolver = createResolver(import.meta.url)

    // Merge with user options
    nuxt.options.runtimeConfig.public.analytics = defu(
      nuxt.options.runtimeConfig.public.analytics,
      {
        trackingId: options.trackingId,
        debug: options.debug,
        router: options.router
      }
    )

    // Add plugin
    addPlugin({
      src: resolver.resolve('./runtime/plugin'),
      mode: 'client' // Client-only
    })

    // Add composable
    addImports({
      name: 'useAnalytics',
      from: resolver.resolve('./runtime/composables/useAnalytics')
    })

    // Add types
    nuxt.hook('prepare:types', ({ references }) => {
      references.push({
        path: resolver.resolve('./runtime/types.d.ts')
      })
    })

    logger.success('Module initialized')
  }
})
```

## Testing Strategies

```typescript
// Testing custom modules
import { describe, it, expect } from 'vitest'
import { setup, $fetch } from '@nuxt/test-utils'

describe('My Module', async () => {
  await setup({
    rootDir: fileURLToPath(new URL('../playground', import.meta.url)),
    server: true
  })

  it('adds runtime config', () => {
    const config = useRuntimeConfig()
    expect(config.public.myModule).toBeDefined()
  })

  it('registers components', async () => {
    const html = await $fetch('/')
    expect(html).toContain('my-module-button')
  })
})
```

## Common Pitfalls

### Pitfall 1: Runtime Config Confusion

```typescript
// WRONG: Accessing private config on client
const config = useRuntimeConfig()
console.log(config.apiSecret) // Undefined on client!

// CORRECT: Use public config for client
const apiBase = config.public.apiBase
```

### Pitfall 2: Module Order Matters

```typescript
// WRONG: Order can cause issues
modules: [
  '@nuxtjs/tailwindcss',
  '@nuxt/ui', // Depends on Tailwind
]

// CORRECT: Dependencies first
modules: [
  '@nuxtjs/tailwindcss', // Must be before @nuxt/ui
  '@nuxt/ui',
]
```

### Pitfall 3: Auto-import Name Collisions

```typescript
// WRONG: Conflicting names
// utils/fetch.ts
export const fetch = () => {} // Conflicts with global fetch!

// CORRECT: Use unique names
export const fetchData = () => {}
export const customFetch = () => {}
```

## Best Practices

1. **Use runtime config** for environment-dependent values
2. **Leverage auto-imports** for cleaner code
3. **Create custom modules** for reusable functionality
4. **Use typed configuration** with TypeScript
5. **Order modules correctly** based on dependencies
6. **Document module options** clearly
7. **Test modules** in playground directory
8. **Use layers** for multi-project code sharing
9. **Configure build optimization** for production
10. **Version modules** with semantic versioning

## Resources

- **Nuxt Modules**: https://nuxt.com/modules
- **Nuxt Kit**: https://nuxt.com/docs/guide/going-further/kit
- **Module Author Guide**: https://nuxt.com/docs/guide/going-further/modules
- **UnJS Ecosystem**: https://unjs.io
- **Nuxt Community**: https://github.com/nuxt-community
