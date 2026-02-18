---
name: angular-ssr-hydration
description: Master Angular SSR with @angular/ssr, incremental hydration with @defer hydrate triggers, route-level render modes (Server/Client/Prerender), HTTP transfer cache, event replay, and deployment strategies for high-performance Angular applications.
category: angular
tags: [angular, ssr, hydration, incremental-hydration, prerender, ssg, defer, render-modes]
related_skills: [angular-blueprint, angular-performance-optimization, angular-routing-patterns, angular-signals-patterns]
---

# Angular SSR and Hydration

Comprehensive guide to server-side rendering in Angular 21+ covering SSR setup with `@angular/ssr`, client hydration, incremental hydration with `@defer` hydrate triggers, route-level render modes (Server, Client, Prerender), HTTP transfer cache to prevent duplicate requests, event replay for user interactions during hydration, and deployment strategies.

## When to Use This Skill

- Setting up server-side rendering for SEO and performance
- Configuring route-level render modes (SSR, SSG, CSR per route)
- Implementing incremental hydration for large component trees
- Preventing duplicate HTTP requests between server and client
- Handling browser-only APIs (window, document, localStorage) in SSR
- Optimizing Core Web Vitals (LCP, FID, CLS) with SSR
- Deploying Angular SSR applications to various platforms
- Prerendering static pages at build time

## Core Concepts

### 1. Server-Side Rendering
- Server renders HTML for each request
- Client receives fully rendered HTML (fast First Contentful Paint)
- Angular hydrates the server-rendered DOM instead of recreating it
- Improves SEO, perceived performance, and social sharing

### 2. Hydration
- Reuses server-rendered DOM nodes on the client
- Attaches event listeners and Angular bindings to existing DOM
- Avoids the "flash of unstyled content" (FOUC)
- Event replay captures user interactions before hydration completes

### 3. Incremental Hydration
- Defers hydration of specific template regions
- Uses `@defer` blocks with `hydrate` triggers
- Reduces initial JavaScript execution on the client
- Server-rendered content is visible immediately, hydrated on demand

### 4. Route-Level Render Modes
- `RenderMode.Server` -- SSR per request
- `RenderMode.Client` -- CSR (no server rendering)
- `RenderMode.Prerender` -- SSG at build time
- Configured via `ServerRoute[]` in `server.routes.ts`

### 5. HTTP Transfer Cache
- Caches HTTP responses made during server rendering
- Transfers cached responses to the client
- Client reuses cached responses instead of re-fetching
- Prevents duplicate API calls during hydration

## Quick Start

```bash
# Add SSR to an existing Angular project
ng add @angular/ssr

# Create a new project with SSR
ng new my-app --ssr
```

```typescript
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideClientHydration(withEventReplay()),
  ],
};
```

## Fundamental Patterns

### Pattern 1: Basic SSR Setup

```typescript
// main.ts (browser entry point)
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app';
import { appConfig } from './app/app.config';

bootstrapApplication(AppComponent, appConfig);
```

```typescript
// main.server.ts (server entry point)
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app';
import { serverConfig } from './app/app.config.server';

const bootstrap = () => bootstrapApplication(AppComponent, serverConfig);
export default bootstrap;
```

```typescript
// app.config.server.ts
import { mergeApplicationConfig, ApplicationConfig } from '@angular/core';
import { provideServerRendering } from '@angular/platform-server';
import { provideServerRouting } from '@angular/ssr';
import { appConfig } from './app.config';
import { serverRoutes } from './server.routes';

const serverAppConfig: ApplicationConfig = {
  providers: [
    provideServerRendering(),
    provideServerRouting(serverRoutes),
  ],
};

export const serverConfig = mergeApplicationConfig(appConfig, serverAppConfig);
```

### Pattern 2: Route-Level Render Modes

```typescript
// server.routes.ts
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Static landing page -- prerendered at build time (SSG)
  {
    path: '',
    renderMode: RenderMode.Prerender,
  },

  // About page -- prerendered at build time
  {
    path: 'about',
    renderMode: RenderMode.Prerender,
  },

  // Product listing -- server-rendered per request (SSR)
  {
    path: 'products',
    renderMode: RenderMode.Server,
  },

  // Product detail -- prerendered with dynamic params
  {
    path: 'products/:slug',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      // Fetch all product slugs at build time
      const response = await fetch('https://api.example.com/products/slugs');
      const slugs: string[] = await response.json();
      return slugs.map(slug => ({ slug }));
    },
  },

  // Blog posts -- prerendered with dynamic params
  {
    path: 'blog/:slug',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      const response = await fetch('https://api.example.com/posts');
      const posts: { slug: string }[] = await response.json();
      return posts.map(post => ({ slug: post.slug }));
    },
  },

  // Dashboard -- client-side only (no SSR needed, authenticated)
  {
    path: 'dashboard/**',
    renderMode: RenderMode.Client,
  },

  // Settings -- client-side only
  {
    path: 'settings/**',
    renderMode: RenderMode.Client,
  },

  // Fallback -- server-rendered
  {
    path: '**',
    renderMode: RenderMode.Server,
  },
];
```

### Pattern 3: Incremental Hydration with @defer

```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-product-page',
  template: `
    <!-- Critical above-the-fold content: hydrated immediately -->
    <header>
      <h1>{{ product().name }}</h1>
      <p class="price">{{ product().price | currency }}</p>
      <button (click)="addToCart()">Add to Cart</button>
    </header>

    <!-- Reviews: hydrated when visible in viewport -->
    @defer (hydrate on viewport) {
      <app-product-reviews [productId]="product().id" />
    } @loading {
      <div class="reviews-skeleton">Loading reviews...</div>
    } @placeholder {
      <div class="reviews-placeholder">Scroll to see reviews</div>
    }

    <!-- Recommendations: hydrated on user interaction -->
    @defer (hydrate on interaction) {
      <app-product-recommendations [category]="product().category" />
    } @placeholder {
      <div class="recommendations-placeholder">
        <h3>You might also like</h3>
        <div class="skeleton-grid">...</div>
      </div>
    }

    <!-- Chat widget: hydrated when browser is idle -->
    @defer (hydrate on idle) {
      <app-chat-widget />
    } @placeholder {
      <div class="chat-placeholder">
        <button disabled>Chat with us</button>
      </div>
    }

    <!-- Analytics: hydrated on a timer -->
    @defer (hydrate on timer(5s)) {
      <app-analytics-tracker [pageId]="product().id" />
    }

    <!-- Heavy chart: hydrated on hover -->
    @defer (hydrate on hover) {
      <app-price-history-chart [productId]="product().id" />
    } @placeholder {
      <div class="chart-placeholder">
        <p>Hover to load price history chart</p>
      </div>
    }
  `,
})
export class ProductPage {
  // ...
}
```

### Pattern 4: HTTP Transfer Cache

```typescript
// app.config.ts
import { provideClientHydration, withEventReplay, withHttpTransferCacheOptions } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    provideClientHydration(
      withEventReplay(),
      withHttpTransferCacheOptions({
        // Cache POST requests too (default is GET only)
        includePostRequests: false,
        // Include request headers in cache key
        includeRequestHeaders: ['Accept-Language'],
        // Exclude specific URLs from caching
        filter: (req) => {
          // Don't cache real-time data
          if (req.url.includes('/api/realtime')) return false;
          // Don't cache authenticated endpoints
          if (req.url.includes('/api/user/me')) return false;
          return true;
        },
      }),
    ),
  ],
};
```

```typescript
// How HTTP transfer cache works in a component
@Component({
  selector: 'app-product-detail',
  template: `
    @if (productResource.hasValue()) {
      <h1>{{ productResource.value()!.name }}</h1>
      <p>{{ productResource.value()!.description }}</p>
    }
  `,
})
export class ProductDetail {
  private readonly route = inject(ActivatedRoute);
  readonly slug = toSignal(
    this.route.paramMap.pipe(map(params => params.get('slug'))),
    { initialValue: '' }
  );

  // This httpResource request:
  // 1. Executes on the server during SSR
  // 2. Response is serialized into the HTML transfer state
  // 3. On the client, the cached response is used (no duplicate request)
  readonly productResource = httpResource<Product>(
    () => `/api/products/${this.slug()}`
  );
}
```

### Pattern 5: Handling Browser-Only APIs

```typescript
import { Component, inject, PLATFORM_ID, afterNextRender, afterEveryRender } from '@angular/core';
import { isPlatformBrowser, DOCUMENT } from '@angular/common';

@Component({
  selector: 'app-analytics',
  template: `<div #container></div>`,
})
export class AnalyticsComponent {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly document = inject(DOCUMENT);

  constructor() {
    // PATTERN 1: afterNextRender -- runs once after first render (client only)
    afterNextRender(() => {
      // Safe to use window, document, localStorage
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) {
        this.document.documentElement.setAttribute('data-theme', savedTheme);
      }

      // Initialize third-party library
      this.initializeAnalytics();
    });

    // PATTERN 2: afterEveryRender -- runs after every render (client only)
    afterEveryRender(() => {
      // Synchronize DOM measurements, scroll position, etc.
      this.updateScrollPosition();
    });
  }

  // PATTERN 3: Platform check for conditional code
  private initializeAnalytics(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Only runs in browser
      window.addEventListener('scroll', this.onScroll);
    }
  }

  // PATTERN 4: Use DOCUMENT token instead of direct document access
  private setMetaTag(name: string, content: string): void {
    const meta = this.document.querySelector(`meta[name="${name}"]`)
      ?? this.document.createElement('meta');
    meta.setAttribute('name', name);
    meta.setAttribute('content', content);
    this.document.head.appendChild(meta);
  }

  private updateScrollPosition(): void {
    // Only meaningful in browser
  }

  private onScroll = (): void => {
    // Scroll handler
  };
}
```

### Pattern 6: PendingTasks for SSR Async Operations

```typescript
import { Component, inject, signal } from '@angular/core';
import { PendingTasks } from '@angular/core';

@Component({
  selector: 'app-dynamic-data',
  template: `
    @if (data()) {
      <div>{{ data()!.title }}</div>
    } @else {
      <div>Loading...</div>
    }
  `,
})
export class DynamicData {
  private readonly pendingTasks = inject(PendingTasks);
  readonly data = signal<{ title: string } | null>(null);

  constructor() {
    // PendingTasks tells Angular SSR to wait for this async operation
    // before serializing the HTML
    this.pendingTasks.run(async () => {
      const response = await fetch('/api/data');
      const result = await response.json();
      this.data.set(result);
    });
  }
}
```

### Pattern 7: Event Replay

```typescript
// app.config.ts
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(
      withEventReplay(), // Enabled by default in Angular 19+
    ),
  ],
};

// How event replay works:
// 1. User clicks a button before hydration completes
// 2. Angular captures the click event in a queue
// 3. After hydration, Angular replays the queued events
// 4. The event handler executes as if the user clicked after hydration

@Component({
  selector: 'app-product-card',
  template: `
    <div class="product-card">
      <h3>{{ product().name }}</h3>
      <!-- If user clicks before hydration, the event is queued and replayed -->
      <button (click)="addToCart()">Add to Cart</button>
    </div>
  `,
})
export class ProductCard {
  readonly product = input.required<Product>();
  private readonly cartService = inject(CartService);

  addToCart(): void {
    this.cartService.addItem(this.product());
  }
}
```

### Pattern 8: SEO Optimization with SSR

```typescript
import { Component, inject } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { httpResource } from '@angular/common/http';
import { map } from 'rxjs';

@Component({
  selector: 'app-blog-post',
  template: `
    @if (postResource.hasValue()) {
      <article>
        <h1>{{ postResource.value()!.title }}</h1>
        <div class="meta">
          <span>By {{ postResource.value()!.author }}</span>
          <time [dateTime]="postResource.value()!.publishedAt">
            {{ postResource.value()!.publishedAt | date:'longDate' }}
          </time>
        </div>
        <div [innerHTML]="postResource.value()!.content"></div>
      </article>
    }
  `,
})
export class BlogPost {
  private readonly route = inject(ActivatedRoute);
  private readonly title = inject(Title);
  private readonly meta = inject(Meta);

  private readonly slug = toSignal(
    this.route.paramMap.pipe(map(p => p.get('slug'))),
    { initialValue: '' }
  );

  readonly postResource = httpResource<BlogPostData>(() => `/api/posts/${this.slug()}`);

  constructor() {
    effect(() => {
      const post = this.postResource.value();
      if (post) {
        this.updateSeoMeta(post);
      }
    });
  }

  private updateSeoMeta(post: BlogPostData): void {
    this.title.setTitle(`${post.title} | My Blog`);

    this.meta.updateTag({ name: 'description', content: post.excerpt });
    this.meta.updateTag({ property: 'og:title', content: post.title });
    this.meta.updateTag({ property: 'og:description', content: post.excerpt });
    this.meta.updateTag({ property: 'og:image', content: post.imageUrl });
    this.meta.updateTag({ property: 'og:type', content: 'article' });
    this.meta.updateTag({ property: 'article:published_time', content: post.publishedAt });
    this.meta.updateTag({ property: 'article:author', content: post.author });
    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.meta.updateTag({ name: 'twitter:title', content: post.title });
    this.meta.updateTag({ name: 'twitter:description', content: post.excerpt });
    this.meta.updateTag({ name: 'twitter:image', content: post.imageUrl });
  }
}

interface BlogPostData {
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  author: string;
  publishedAt: string;
  imageUrl: string;
}
```

## Advanced Patterns

### Pattern 9: Hybrid Rendering Strategy

```typescript
// server.routes.ts - Complete hybrid rendering configuration
import { ServerRoute, RenderMode } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // Marketing pages: prerender for maximum speed
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'about', renderMode: RenderMode.Prerender },
  { path: 'pricing', renderMode: RenderMode.Prerender },
  { path: 'contact', renderMode: RenderMode.Prerender },

  // Blog: prerender all posts
  {
    path: 'blog',
    renderMode: RenderMode.Prerender,
  },
  {
    path: 'blog/:slug',
    renderMode: RenderMode.Prerender,
    async getPrerenderParams() {
      const res = await fetch('https://cms.example.com/api/posts?fields=slug');
      const posts = await res.json();
      return posts.map((p: { slug: string }) => ({ slug: p.slug }));
    },
  },

  // Product pages: SSR for fresh data
  { path: 'products', renderMode: RenderMode.Server },
  { path: 'products/:slug', renderMode: RenderMode.Server },

  // Search: SSR for SEO
  { path: 'search', renderMode: RenderMode.Server },

  // Authenticated areas: CSR only
  { path: 'dashboard/**', renderMode: RenderMode.Client },
  { path: 'account/**', renderMode: RenderMode.Client },
  { path: 'checkout/**', renderMode: RenderMode.Client },
  { path: 'admin/**', renderMode: RenderMode.Client },

  // Auth pages: SSR
  { path: 'login', renderMode: RenderMode.Server },
  { path: 'register', renderMode: RenderMode.Server },

  // Catch-all: server render
  { path: '**', renderMode: RenderMode.Server },
];
```

### Pattern 10: Custom SSR Caching with Express

```typescript
// server.ts - Custom Express server with caching
import { APP_BASE_HREF } from '@angular/common';
import { CommonEngine } from '@angular/ssr/node';
import express from 'express';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import bootstrap from './main.server';

const serverDir = dirname(fileURLToPath(import.meta.url));
const browserDir = resolve(serverDir, '../browser');
const indexHtml = join(serverDir, 'index.server.html');

const app = express();
const engine = new CommonEngine();

// In-memory cache for SSR responses
const ssrCache = new Map<string, { html: string; timestamp: number }>();
const CACHE_TTL = 60 * 1000; // 1 minute

// Serve static files
app.get('*.*', express.static(browserDir, { maxAge: '1y' }));

// SSR with caching
app.get('*', async (req, res, next) => {
  const url = req.originalUrl;

  // Check cache
  const cached = ssrCache.get(url);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    res.setHeader('X-SSR-Cache', 'HIT');
    return res.send(cached.html);
  }

  try {
    const html = await engine.render({
      bootstrap,
      documentFilePath: indexHtml,
      url: `${req.protocol}://${req.headers.host}${url}`,
      publicPath: browserDir,
      providers: [{ provide: APP_BASE_HREF, useValue: req.baseUrl }],
    });

    // Cache the response
    ssrCache.set(url, { html, timestamp: Date.now() });
    res.setHeader('X-SSR-Cache', 'MISS');
    res.send(html);
  } catch (err) {
    next(err);
  }
});

const port = process.env['PORT'] || 4000;
app.listen(port, () => {
  console.log(`Angular SSR server listening on http://localhost:${port}`);
});
```

### Pattern 11: Incremental Hydration with IntersectionObserver Options

```typescript
// Angular 21+: @defer viewport trigger accepts IntersectionObserver options
@Component({
  selector: 'app-infinite-feed',
  template: `
    @for (item of items(); track item.id) {
      <!-- Each feed item hydrates when it enters the viewport -->
      @defer (hydrate on viewport({ rootMargin: '200px' })) {
        <app-feed-item [item]="item" />
      } @placeholder {
        <div class="feed-item-skeleton" style="height: 200px;"></div>
      }
    }

    <!-- Load more trigger: hydrates when visible with margin -->
    @defer (hydrate on viewport({ rootMargin: '500px' })) {
      <app-load-more-trigger (loadMore)="loadNextPage()" />
    }
  `,
})
export class InfiniteFeed {
  readonly items = signal<FeedItem[]>([]);

  loadNextPage(): void {
    // Load more items...
  }
}
```

### Pattern 12: Deployment Configuration

```typescript
// For Vercel deployment
// angular.json
{
  "architect": {
    "build": {
      "options": {
        "outputPath": {
          "base": "dist/my-app"
        },
        "server": "src/main.server.ts",
        "prerender": true,
        "ssr": {
          "entry": "server.ts"
        }
      }
    }
  }
}

// For Docker deployment
// Dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS production
WORKDIR /app
COPY --from=build /app/dist/my-app ./dist
EXPOSE 4000
CMD ["node", "dist/server/server.mjs"]
```

## Testing Strategies

### Testing SSR Pages

```typescript
// e2e/ssr.spec.ts
import { test, expect } from '@playwright/test';

test.describe('SSR Verification', () => {
  test('product page is server-rendered', async ({ page }) => {
    // Intercept all JS to verify SSR content
    await page.context().route('**/*.js', route => route.abort());

    await page.goto('/products');

    // Content should be visible without JavaScript
    await expect(page.locator('h1')).toContainText('Products');
    await expect(page.locator('[data-test="product-card"]').first()).toBeVisible();
  });

  test('prerendered page loads instantly', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/about');
    const loadTime = Date.now() - startTime;

    // Prerendered pages should load very fast
    expect(loadTime).toBeLessThan(1000);
    await expect(page.locator('h1')).toContainText('About');
  });

  test('hydration completes without errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/products');
    await page.waitForLoadState('networkidle');

    const hydrationErrors = errors.filter(e =>
      e.includes('hydration') || e.includes('mismatch')
    );
    expect(hydrationErrors).toHaveLength(0);
  });

  test('event replay works', async ({ page }) => {
    await page.goto('/products');

    // Click immediately (before hydration might complete)
    await page.locator('[data-test="add-to-cart-btn"]').first().click();

    // Wait for hydration and event replay
    await page.waitForLoadState('networkidle');

    // Verify the event was processed
    await expect(page.locator('[data-test="cart-count"]')).toContainText('1');
  });

  test('client-only routes do not server-render', async ({ page }) => {
    // Dashboard should be client-rendered (no SSR content)
    await page.context().route('**/*.js', route => route.abort());
    await page.goto('/dashboard');

    // Should show loading or empty state, not full content
    const content = await page.textContent('body');
    expect(content).not.toContain('Dashboard Statistics');
  });
});
```

## Common Pitfalls

### Pitfall 1: Direct DOM Access Without Platform Check

```typescript
// WRONG: crashes on server
@Component({ /* ... */ })
export class Bad {
  constructor() {
    window.scrollTo(0, 0); // ReferenceError: window is not defined
  }
}

// CORRECT: use afterNextRender or platform check
@Component({ /* ... */ })
export class Good {
  constructor() {
    afterNextRender(() => {
      window.scrollTo(0, 0);
    });
  }
}
```

### Pitfall 2: Using localStorage During SSR

```typescript
// WRONG: localStorage is not available on server
const theme = localStorage.getItem('theme');

// CORRECT: guard with afterNextRender or isPlatformBrowser
afterNextRender(() => {
  const theme = localStorage.getItem('theme');
  this.themeService.setTheme(theme ?? 'light');
});
```

### Pitfall 3: DOM Mismatch Between Server and Client

```typescript
// WRONG: content differs between server and client
@Component({
  template: `<p>Rendered at {{ currentTime }}</p>`,
})
export class Bad {
  currentTime = new Date().toISOString(); // Different on server vs client!
}

// CORRECT: use consistent data or defer client-specific content
@Component({
  template: `
    <p>Welcome to our site</p>
    @defer (hydrate on idle) {
      <p>Current time: {{ currentTime }}</p>
    }
  `,
})
export class Good {
  currentTime = new Date().toISOString();
}
```

### Pitfall 4: Not Waiting for Async Operations in SSR

```typescript
// WRONG: SSR renders before data is loaded
@Component({ /* ... */ })
export class Bad {
  data = signal<Data | null>(null);

  constructor() {
    // fetch() is not tracked by Angular SSR
    fetch('/api/data').then(r => r.json()).then(d => this.data.set(d));
  }
}

// CORRECT: use PendingTasks or httpResource
@Component({ /* ... */ })
export class Good {
  private readonly pendingTasks = inject(PendingTasks);
  data = signal<Data | null>(null);

  constructor() {
    this.pendingTasks.run(async () => {
      const res = await fetch('/api/data');
      this.data.set(await res.json());
    });
  }
}

// BEST: use httpResource (automatically tracked)
@Component({ /* ... */ })
export class Best {
  dataResource = httpResource<Data>(() => '/api/data');
}
```

## Best Practices

1. **Use route-level render modes** to optimize each route's rendering strategy
2. **Use `@defer` with `hydrate` triggers** for below-the-fold content
3. **Enable HTTP transfer cache** to prevent duplicate API calls during hydration
4. **Enable event replay** to capture user interactions before hydration completes
5. **Guard browser-only APIs** with `afterNextRender()` or `isPlatformBrowser()`
6. **Use `PendingTasks`** for async operations that must complete before SSR serialization
7. **Use `httpResource`** for data fetching (automatically works with transfer cache)
8. **Prerender static pages** (`RenderMode.Prerender`) for marketing, blog, and landing pages
9. **Use Client render mode** only for authenticated routes that do not need SEO
10. **Test SSR** by disabling JavaScript in Playwright and verifying content is visible

## Resources

- **Angular SSR Guide**: https://angular.dev/guide/ssr
- **Angular Hydration Guide**: https://angular.dev/guide/hydration
- **Angular @defer Guide**: https://angular.dev/guide/defer
- **Angular Route-Level Render Modes**: https://angular.dev/guide/ssr#route-level-render-modes
- **Angular HTTP Transfer Cache**: https://angular.dev/guide/ssr#http-transfer-cache
