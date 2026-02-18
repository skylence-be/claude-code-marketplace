---
description: Generate a functional Angular HTTP interceptor with HttpInterceptorFn
model: claude-sonnet-4-5
---

Create a new Angular functional HTTP interceptor following modern Angular 21+ best practices.

## Interceptor Specification

$ARGUMENTS

## Angular 21+ Functional Interceptor Standards

### 1. **Basic Auth Token Interceptor**

```typescript
import { HttpInterceptorFn, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.token();

  if (token) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
    return next(cloned);
  }

  return next(req);
};
```

### 2. **Error Handling Interceptor**

```typescript
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const notificationService = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
          router.navigate(['/login']);
          break;
        case 403:
          notificationService.error('You do not have permission to perform this action.');
          break;
        case 404:
          notificationService.error('The requested resource was not found.');
          break;
        case 500:
          notificationService.error('An unexpected server error occurred.');
          break;
        default:
          notificationService.error('A network error occurred. Please try again.');
      }
      return throwError(() => error);
    })
  );
};
```

### 3. **Loading Indicator Interceptor**

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { finalize } from 'rxjs';

export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loadingService = inject(LoadingService);

  // Skip loading indicator for specific requests
  if (req.headers.has('X-Skip-Loading')) {
    const cleaned = req.clone({
      headers: req.headers.delete('X-Skip-Loading'),
    });
    return next(cleaned);
  }

  loadingService.show();

  return next(req).pipe(
    finalize(() => loadingService.hide())
  );
};
```

### 4. **Retry Interceptor**

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { retry, timer } from 'rxjs';

export const retryInterceptor: HttpInterceptorFn = (req, next) => {
  // Only retry GET requests (safe to retry)
  if (req.method !== 'GET') {
    return next(req);
  }

  return next(req).pipe(
    retry({
      count: 3,
      delay: (error, retryCount) => {
        // Exponential backoff: 1s, 2s, 4s
        const delayMs = Math.pow(2, retryCount - 1) * 1000;
        console.warn(`Retry attempt ${retryCount} for ${req.url} in ${delayMs}ms`);
        return timer(delayMs);
      },
      resetOnSuccess: true,
    })
  );
};
```

### 5. **Caching Interceptor**

```typescript
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { of, tap } from 'rxjs';

interface CacheEntry {
  response: HttpResponse<unknown>;
  expiry: number;
}

@Injectable({ providedIn: 'root' })
export class HttpCacheService {
  private readonly cache = new Map<string, CacheEntry>();

  get(url: string): HttpResponse<unknown> | null {
    const entry = this.cache.get(url);
    if (entry && entry.expiry > Date.now()) {
      return entry.response;
    }
    this.cache.delete(url);
    return null;
  }

  set(url: string, response: HttpResponse<unknown>, ttlMs: number): void {
    this.cache.set(url, { response, expiry: Date.now() + ttlMs });
  }

  clear(): void {
    this.cache.clear();
  }
}

export const cachingInterceptor: HttpInterceptorFn = (req, next) => {
  const cache = inject(HttpCacheService);

  // Only cache GET requests
  if (req.method !== 'GET') {
    return next(req);
  }

  // Check if a custom cache header is present
  const cacheTtl = req.headers.get('X-Cache-TTL');
  if (!cacheTtl) {
    return next(req);
  }

  const cached = cache.get(req.urlWithParams);
  if (cached) {
    return of(cached.clone());
  }

  const cleaned = req.clone({
    headers: req.headers.delete('X-Cache-TTL'),
  });

  return next(cleaned).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(req.urlWithParams, event, parseInt(cacheTtl, 10));
      }
    })
  );
};
```

### 6. **Logging Interceptor**

```typescript
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { tap } from 'rxjs';

export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const startTime = performance.now();

  return next(req).pipe(
    tap({
      next: (event) => {
        if (event instanceof HttpResponse) {
          const elapsed = Math.round(performance.now() - startTime);
          console.log(
            `[HTTP] ${req.method} ${req.urlWithParams} => ${event.status} (${elapsed}ms)`
          );
        }
      },
      error: (error) => {
        const elapsed = Math.round(performance.now() - startTime);
        console.error(
          `[HTTP] ${req.method} ${req.urlWithParams} => ERROR ${error.status} (${elapsed}ms)`
        );
      },
    })
  );
};
```

### 7. **Content-Type Interceptor**

```typescript
import { HttpInterceptorFn } from '@angular/common/http';

export const contentTypeInterceptor: HttpInterceptorFn = (req, next) => {
  // Skip if Content-Type is already set or if it is a FormData request
  if (req.headers.has('Content-Type') || req.body instanceof FormData) {
    return next(req);
  }

  // Add JSON content type for requests with a body
  if (req.body !== null && req.body !== undefined) {
    const cloned = req.clone({
      setHeaders: { 'Content-Type': 'application/json' },
    });
    return next(cloned);
  }

  return next(req);
};
```

### 8. **Registering Interceptors**

```typescript
// app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([
        authInterceptor,
        contentTypeInterceptor,
        loadingInterceptor,
        retryInterceptor,
        cachingInterceptor,
        errorInterceptor,
        loggingInterceptor,
      ])
    ),
  ],
};
```

**Interceptor execution order:**
- **Request**: Top to bottom (authInterceptor runs first)
- **Response**: Bottom to top (loggingInterceptor runs first on response)

### 9. **Configurable Interceptor Factory**

```typescript
import { HttpInterceptorFn } from '@angular/common/http';

interface ApiPrefixConfig {
  baseUrl: string;
  excludePatterns?: RegExp[];
}

export const apiPrefixInterceptor = (config: ApiPrefixConfig): HttpInterceptorFn => {
  return (req, next) => {
    // Skip excluded patterns and absolute URLs
    if (
      req.url.startsWith('http') ||
      config.excludePatterns?.some(p => p.test(req.url))
    ) {
      return next(req);
    }

    const cloned = req.clone({
      url: `${config.baseUrl}${req.url}`,
    });
    return next(cloned);
  };
};

// Usage:
// withInterceptors([apiPrefixInterceptor({ baseUrl: 'https://api.example.com' })])
```

## Best Practices

**Interceptor Design**
- ✓ Use functional interceptors (`HttpInterceptorFn`) over class-based
- ✓ Use `inject()` to access services inside interceptor functions
- ✓ Clone requests before modifying (requests are immutable)
- ✓ Keep interceptors focused on a single concern
- ✓ Use factory functions for configurable interceptors

**TypeScript**
- ✓ Properly type all interceptor parameters
- ✓ Type error handling with `HttpErrorResponse`
- ✓ No `any` types

**Error Handling**
- ✓ Always return `throwError()` after handling errors to allow downstream handling
- ✓ Differentiate between HTTP status codes
- ✓ Provide user-friendly error messages via a notification service

**Performance**
- ✓ Use conditional logic to skip unnecessary processing
- ✓ Implement caching for repeated GET requests
- ✓ Use exponential backoff for retries
- ✓ Minimize cloning when no modifications are needed

**Registration**
- ✓ Register interceptors in `provideHttpClient(withInterceptors([...]))`
- ✓ Order interceptors logically (auth first, logging last)
- ✓ Use `withInterceptorsFromDi()` only for legacy class-based interceptors

Generate production-ready, type-safe Angular functional HTTP interceptors.
