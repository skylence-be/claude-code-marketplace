---
description: Generate an Angular standalone pipe with pure flag and proper typing
model: claude-sonnet-4-5
---

Create a new Angular standalone pipe following modern Angular 21+ best practices.

## Pipe Specification

$ARGUMENTS

## Angular 21+ Pipe Standards

### 1. **Basic Pure Pipe**

```typescript
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'truncate',
  pure: true, // Default; recalculates only when input reference changes
})
export class TruncatePipe implements PipeTransform {
  transform(value: string, maxLength: number = 100, suffix: string = '...'): string {
    if (!value || value.length <= maxLength) {
      return value ?? '';
    }
    return value.substring(0, maxLength).trimEnd() + suffix;
  }
}

// Usage: {{ description | truncate:50:'...' }}
```

### 2. **Typed Pipe with Generics**

```typescript
@Pipe({ name: 'filterBy', pure: true })
export class FilterByPipe implements PipeTransform {
  transform<T>(items: T[] | null, predicate: (item: T) => boolean): T[] {
    if (!items) {
      return [];
    }
    return items.filter(predicate);
  }
}

// Usage: @for (user of users() | filterBy:isActive; track user.id) { ... }
```

### 3. **Pipe with Multiple Overloads**

```typescript
@Pipe({ name: 'fileSize', pure: true })
export class FileSizePipe implements PipeTransform {
  private readonly units = ['B', 'KB', 'MB', 'GB', 'TB'];

  transform(bytes: number | null | undefined, decimals?: number): string;
  transform(bytes: number | null | undefined, decimals: number = 1): string {
    if (bytes === null || bytes === undefined || isNaN(bytes)) {
      return '0 B';
    }
    if (bytes === 0) {
      return '0 B';
    }

    const k = 1024;
    const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));
    const unitIndex = Math.min(i, this.units.length - 1);
    const value = bytes / Math.pow(k, unitIndex);

    return `${value.toFixed(decimals)} ${this.units[unitIndex]}`;
  }
}

// Usage: {{ file.size | fileSize }} => "2.5 MB"
// Usage: {{ file.size | fileSize:2 }} => "2.50 MB"
```

### 4. **Date/Time Relative Pipe**

```typescript
@Pipe({ name: 'timeAgo', pure: true })
export class TimeAgoPipe implements PipeTransform {
  transform(value: string | Date | null): string {
    if (!value) {
      return '';
    }

    const date = value instanceof Date ? value : new Date(value);
    const now = Date.now();
    const diffMs = now - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSeconds < 60) return 'just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
  }
}

// Usage: {{ post.createdAt | timeAgo }} => "3h ago"
```

### 5. **Currency/Number Formatting Pipe**

```typescript
@Pipe({ name: 'compactNumber', pure: true })
export class CompactNumberPipe implements PipeTransform {
  transform(value: number | null | undefined, decimals: number = 1): string {
    if (value === null || value === undefined) {
      return '0';
    }

    const absValue = Math.abs(value);
    const sign = value < 0 ? '-' : '';

    if (absValue >= 1_000_000_000) {
      return `${sign}${(absValue / 1_000_000_000).toFixed(decimals)}B`;
    }
    if (absValue >= 1_000_000) {
      return `${sign}${(absValue / 1_000_000).toFixed(decimals)}M`;
    }
    if (absValue >= 1_000) {
      return `${sign}${(absValue / 1_000).toFixed(decimals)}K`;
    }
    return `${sign}${absValue}`;
  }
}

// Usage: {{ followers | compactNumber }} => "12.5K"
```

### 6. **String Transformation Pipes**

```typescript
@Pipe({ name: 'highlight', pure: true })
export class HighlightPipe implements PipeTransform {
  transform(text: string | null, searchTerm: string): string {
    if (!text || !searchTerm) {
      return text ?? '';
    }

    const escaped = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }
}

// Usage: <span [innerHTML]="item.name | highlight:searchQuery()"></span>

@Pipe({ name: 'initials', pure: true })
export class InitialsPipe implements PipeTransform {
  transform(name: string | null, maxInitials: number = 2): string {
    if (!name) {
      return '';
    }

    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, maxInitials)
      .map(word => word[0].toUpperCase())
      .join('');
  }
}

// Usage: {{ user.name | initials }} => "JD"
```

### 7. **Safe Resource URL Pipe (with Validation)**

```typescript
import { inject } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Pipe({ name: 'safeUrl', pure: true })
export class SafeUrlPipe implements PipeTransform {
  private readonly sanitizer = inject(DomSanitizer);

  // WARNING: bypassSecurityTrustResourceUrl disables Angular's XSS protection.
  // Always validate URLs against a trusted allowlist before bypassing sanitization.
  private readonly allowedPatterns = [
    /^https:\/\/(www\.)?youtube\.com\/embed\//,
    /^https:\/\/(www\.)?vimeo\.com\/video\//,
    /^https:\/\/player\.vimeo\.com\//,
  ];

  transform(url: string): SafeResourceUrl {
    const isAllowed = this.allowedPatterns.some(pattern => pattern.test(url));
    if (!isAllowed) {
      throw new Error(`SafeUrlPipe: URL not in allowlist: ${url}`);
    }
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}

// Usage: <iframe [src]="videoUrl | safeUrl"></iframe>
// Customize allowedPatterns for your trusted domains
```

### 8. **Pipe with Injection**

```typescript
import { inject } from '@angular/core';

@Pipe({ name: 'translate', pure: true })
export class TranslatePipe implements PipeTransform {
  private readonly i18nService = inject(I18nService);

  transform(key: string, params?: Record<string, string>): string {
    return this.i18nService.translate(key, params);
  }
}

// Usage: {{ 'greeting.hello' | translate:{ name: user().name } }}
```

### 9. **Using Pipes in Components**

```typescript
// Import pipes in the component's imports array
@Component({
  selector: 'app-user-list',
  imports: [TruncatePipe, TimeAgoPipe, CompactNumberPipe],
  template: `
    @for (user of users(); track user.id) {
      <div class="user-row">
        <span>{{ user.bio | truncate:80 }}</span>
        <span>{{ user.followers | compactNumber }}</span>
        <span>{{ user.lastSeen | timeAgo }}</span>
      </div>
    }
  `
})
export class UserList {
  users = input.required<User[]>();
}
```

### 10. **When to Use Pipes vs. Computed Signals**

```typescript
// USE PIPE: Reusable formatting across multiple components
// {{ value | fileSize }}
// {{ date | timeAgo }}

// USE COMPUTED: Component-specific derived state
// fullName = computed(() => `${this.firstName()} ${this.lastName()}`);
// isOverBudget = computed(() => this.total() > this.budget());

// AVOID: Impure pipes that re-evaluate on every change detection cycle
// @Pipe({ name: 'sort', pure: false }) -- use computed() instead
```

## Best Practices

**Pipe Design**
- ✓ Always use `pure: true` (the default) for predictable performance
- ✓ Pipes should be stateless and side-effect-free
- ✓ Handle `null` and `undefined` inputs gracefully
- ✓ Keep transform logic simple and fast
- ✓ One pipe per file with a descriptive name

**TypeScript**
- ✓ Properly type all `transform` parameters and return values
- ✓ Use overloads for multiple signatures
- ✓ Use generics when the pipe works with various types
- ✓ No `any` types

**Naming**
- ✓ Use camelCase for the pipe `name` property
- ✓ Use PascalCase + `Pipe` suffix for the class name (or no suffix per 2025 style guide)
- ✓ File name: `truncate.ts` or `truncate.pipe.ts`

**Performance**
- ✓ Pure pipes are memoized by Angular -- preferred for all formatting
- ✓ Avoid impure pipes; use `computed()` signals for reactive derived state
- ✓ Do not perform heavy computation or async work in pipes

**Testing**
- ✓ Test edge cases: empty strings, null, undefined, boundary values
- ✓ Test with various parameter combinations
- ✓ Pipes are simple to unit test -- no TestBed required

Generate production-ready, type-safe Angular standalone pipes with proper typing and null safety.
