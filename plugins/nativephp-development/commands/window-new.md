---
description: Create NativePHP window configuration
model: claude-sonnet-4-5
---

Create a NativePHP window configuration with proper sizing, positioning, and behavior.

## Window Specification

$ARGUMENTS

## Window Patterns

### 1. **Main Application Window**

```php
use Native\Laravel\Facades\Window;

Window::open('main')
    ->width(1200)->height(800)
    ->minWidth(800)->minHeight(600)
    ->route('dashboard')
    ->rememberState()
    ->resizable()
    ->closable()
    ->titleBarHidden();
```

### 2. **Settings / Modal Window**

```php
use Native\Laravel\Facades\Window;

Window::open('settings')
    ->width(600)->height(500)
    ->route('settings')
    ->resizable(false)
    ->focusable()
    ->alwaysOnTop();
```

### 3. **Multi-Window Application**

```php
use Native\Laravel\Facades\Window;

// Main window
Window::open('main')
    ->width(1200)->height(800)
    ->route('dashboard')
    ->rememberState();

// Floating panel
Window::open('inspector')
    ->width(350)->height(600)
    ->route('inspector')
    ->position(50, 50)
    ->alwaysOnTop()
    ->titleBarHidden();

// Window management in controllers
public function openEditor(int $documentId)
{
    Window::open("editor-{$documentId}")
        ->width(900)->height(700)
        ->route('documents.edit', ['document' => $documentId])
        ->rememberState();
}

public function closeEditor(int $documentId)
{
    Window::close("editor-{$documentId}");
}
```

### 4. **Fullscreen / Kiosk Window**

```php
use Native\Laravel\Facades\Window;

Window::open('presentation')
    ->fullscreen()
    ->route('presentation.show')
    ->frameless()
    ->focusable();
```

### 5. **Window with External URL**

```php
use Native\Laravel\Facades\Window;

Window::open('docs')
    ->width(1000)->height(700)
    ->url('https://docs.example.com')
    ->preventLeaveDomain();
```

### 6. **Window Event Handling**

```php
// In EventServiceProvider or Livewire component
use Native\Laravel\Events\Windows\WindowClosed;
use Native\Laravel\Events\Windows\WindowFocused;
use Native\Laravel\Events\Windows\WindowResized;

// Listen for window events
protected $listen = [
    WindowClosed::class => [HandleWindowClosed::class],
    WindowFocused::class => [HandleWindowFocused::class],
];

// Livewire integration
use Livewire\Attributes\On;

#[On('native:'.WindowFocused::class)]
public function onWindowFocused()
{
    $this->refreshData();
}
```

Generate a complete window configuration matching the specification. Include the Window facade call with all relevant options, any associated routes, and event listeners if window events need handling.
