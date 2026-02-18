---
description: Generate an Angular standalone directive with host bindings and signal inputs
model: claude-sonnet-4-5
---

Create a new Angular standalone directive following modern Angular 21+ best practices.

## Directive Specification

$ARGUMENTS

## Angular 21+ Directive Standards

### 1. **Basic Attribute Directive with Signal Inputs**

```typescript
import { Directive, ElementRef, inject, input, effect } from '@angular/core';

@Directive({
  selector: '[appHighlight]',
})
export class HighlightDirective {
  private readonly el = inject(ElementRef<HTMLElement>);

  color = input('yellow', { alias: 'appHighlight' });

  constructor() {
    effect(() => {
      this.el.nativeElement.style.backgroundColor = this.color();
    });
  }
}

// Usage: <p appHighlight>Default yellow</p>
// Usage: <p appHighlight="lightblue">Custom color</p>
```

### 2. **Directive with Host Bindings**

```typescript
import { Directive, input, computed, signal } from '@angular/core';

@Directive({
  selector: '[appTooltip]',
  host: {
    '[attr.data-tooltip]': 'text()',
    '[class.has-tooltip]': 'text()',
    '(mouseenter)': 'onMouseEnter()',
    '(mouseleave)': 'onMouseLeave()',
    '[style.position]': '"relative"',
  },
})
export class TooltipDirective {
  text = input.required<string>({ alias: 'appTooltip' });
  position = input<'top' | 'bottom' | 'left' | 'right'>('top');

  private readonly isVisible = signal(false);

  onMouseEnter(): void {
    this.isVisible.set(true);
  }

  onMouseLeave(): void {
    this.isVisible.set(false);
  }
}

// Usage: <button appTooltip="Click to save" position="bottom">Save</button>
```

### 3. **Click Outside Directive**

```typescript
import { Directive, ElementRef, inject, output, afterNextRender, DestroyRef } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Directive({
  selector: '[appClickOutside]',
  host: {},
})
export class ClickOutsideDirective {
  private readonly el = inject(ElementRef<HTMLElement>);
  private readonly document = inject(DOCUMENT);

  clickOutside = output<void>({ alias: 'appClickOutside' });

  constructor() {
    afterNextRender(() => {
      this.document.addEventListener('click', this.handleClick);
    });

    inject(DestroyRef).onDestroy(() => {
      this.document.removeEventListener('click', this.handleClick);
    });
  }

  private handleClick = (event: MouseEvent): void => {
    if (!this.el.nativeElement.contains(event.target as Node)) {
      this.clickOutside.emit();
    }
  };
}

// Usage: <div (appClickOutside)="closeMenu()">...</div>
```

### 4. **Intersection Observer Directive (Lazy Loading)**

```typescript
import { Directive, ElementRef, inject, output, input, afterNextRender, DestroyRef } from '@angular/core';

@Directive({
  selector: '[appInView]',
})
export class InViewDirective {
  private readonly el = inject(ElementRef<HTMLElement>);

  inView = output<boolean>({ alias: 'appInView' });
  threshold = input(0.1);
  once = input(false);

  private observer: IntersectionObserver | null = null;

  constructor() {
    afterNextRender(() => {
      this.observer = new IntersectionObserver(
        ([entry]) => {
          this.inView.emit(entry.isIntersecting);
          if (entry.isIntersecting && this.once()) {
            this.observer?.disconnect();
          }
        },
        { threshold: this.threshold() }
      );
      this.observer.observe(this.el.nativeElement);
    });

    inject(DestroyRef).onDestroy(() => {
      this.observer?.disconnect();
    });
  }
}

// Usage: <div (appInView)="onVisible($event)" [once]="true">...</div>
```

### 5. **Permission Directive (Structural-Like)**

```typescript
import { Directive, inject, input, effect, TemplateRef, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[appIfPermission]',
})
export class IfPermissionDirective {
  private readonly templateRef = inject(TemplateRef<unknown>);
  private readonly vcRef = inject(ViewContainerRef);
  private readonly authService = inject(AuthService);

  permission = input.required<string>({ alias: 'appIfPermission' });

  private hasView = false;

  constructor() {
    effect(() => {
      const allowed = this.authService.hasPermission(this.permission());

      if (allowed && !this.hasView) {
        this.vcRef.createEmbeddedView(this.templateRef);
        this.hasView = true;
      } else if (!allowed && this.hasView) {
        this.vcRef.clear();
        this.hasView = false;
      }
    });
  }
}

// Usage: <button *appIfPermission="'admin.delete'">Delete</button>
// Note: prefer @if with a service call for simple cases
```

### 6. **Auto-Focus Directive**

```typescript
import { Directive, ElementRef, inject, input, afterNextRender, booleanAttribute } from '@angular/core';

@Directive({
  selector: '[appAutoFocus]',
})
export class AutoFocusDirective {
  private readonly el = inject(ElementRef<HTMLElement>);

  enabled = input(true, { alias: 'appAutoFocus', transform: booleanAttribute });
  delay = input(0);

  constructor() {
    afterNextRender(() => {
      if (this.enabled()) {
        setTimeout(() => {
          this.el.nativeElement.focus();
        }, this.delay());
      }
    });
  }
}

// Usage: <input appAutoFocus />
// Usage: <input [appAutoFocus]="shouldFocus()" [delay]="200" />
```

### 7. **Debounce Input Directive**

```typescript
import { Directive, output, input, DestroyRef, inject } from '@angular/core';
import { Subject, debounceTime } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Directive({
  selector: '[appDebounceInput]',
  host: {
    '(input)': 'onInput($event)',
  },
})
export class DebounceInputDirective {
  delay = input(300);
  debounced = output<string>({ alias: 'appDebounceInput' });

  private readonly input$ = new Subject<string>();

  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    // Read delay once at construction; for dynamic delay, use switchMap + timer
    const initialDelay = this.delay();
    this.input$.pipe(
      debounceTime(initialDelay),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(value => {
      this.debounced.emit(value);
    });
  }

  onInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.input$.next(target.value);
  }
}

// Usage: <input (appDebounceInput)="onSearch($event)" [delay]="500" />
```

### 8. **Long Press Directive**

```typescript
import { Directive, output, input, DestroyRef, inject } from '@angular/core';

@Directive({
  selector: '[appLongPress]',
  host: {
    '(pointerdown)': 'onPointerDown()',
    '(pointerup)': 'onPointerUp()',
    '(pointerleave)': 'onPointerUp()',
  },
})
export class LongPressDirective {
  duration = input(500);
  longPress = output<void>({ alias: 'appLongPress' });

  private timer: ReturnType<typeof setTimeout> | null = null;

  onPointerDown(): void {
    this.timer = setTimeout(() => {
      this.longPress.emit();
    }, this.duration());
  }

  onPointerUp(): void {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
}

// Usage: <button (appLongPress)="onLongPress()" [duration]="800">Hold me</button>
```

### 9. **Using Directives in Components**

```typescript
@Component({
  selector: 'app-dropdown',
  imports: [ClickOutsideDirective, AutoFocusDirective],
  template: `
    <div class="dropdown" (appClickOutside)="close()">
      <button (click)="toggle()">{{ label() }}</button>
      @if (isOpen()) {
        <div class="dropdown-menu">
          <input appAutoFocus placeholder="Search..." />
          <ng-content />
        </div>
      }
    </div>
  `
})
export class Dropdown {
  label = input('Select');
  isOpen = signal(false);

  toggle(): void {
    this.isOpen.update(v => !v);
  }

  close(): void {
    this.isOpen.set(false);
  }
}
```

## Best Practices

**Directive Design**
- ✓ Use signal-based `input()` and `output()` for all bindings
- ✓ Use `host` metadata for event bindings and class/style/attribute bindings
- ✓ Use `afterNextRender()` for DOM access that must run in the browser
- ✓ Clean up with `DestroyRef.onDestroy()` instead of `OnDestroy` lifecycle
- ✓ Prefer attribute directives over structural directives (use `@if` for conditional rendering)

**TypeScript**
- ✓ Properly type all inputs and outputs
- ✓ Use `booleanAttribute` / `numberAttribute` transforms for attribute coercion
- ✓ Alias inputs to match the directive selector for ergonomic usage
- ✓ No `any` types

**Naming**
- ✓ Use `app` prefix (or project-specific prefix) for selectors
- ✓ Use camelCase for selector names: `[appHighlight]`, `[appClickOutside]`
- ✓ PascalCase class name: `HighlightDirective` (or `Highlight` per 2025 style guide)
- ✓ File name: `highlight.ts` or `highlight.directive.ts`

**Performance**
- ✓ Use `effect()` for reactive host binding updates
- ✓ Avoid direct DOM manipulation where Angular bindings suffice
- ✓ Disconnect observers and remove event listeners on destroy
- ✓ Use `once` input pattern for one-time observers

**Accessibility**
- ✓ Ensure directives do not break keyboard navigation
- ✓ Add appropriate ARIA attributes via host bindings
- ✓ Maintain focus management when showing/hiding content

Generate production-ready, type-safe Angular standalone directives with modern signal-based APIs.
