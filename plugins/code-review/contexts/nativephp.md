# NativePHP Review Rules

Technology-specific review rules for NativePHP desktop and mobile applications. Loaded when `nativephp/electron` or `nativephp/mobile` is detected in `composer.json`.

## Detection
- `composer.json` contains `nativephp/electron` or `nativephp/mobile` in `require`
- `NativeAppServiceProvider` class exists
- Files using `Native\Laravel\` namespace imports

## Anti-Patterns to Flag

### Windows Without Size Constraints
Creating windows without minimum size constraints, allowing unusable UI states.
- **Severity:** Medium (UX)
- **Pattern:** `Window::open()` without `->minWidth()` and `->minHeight()`
- **Fix:** Add `->minWidth(800)->minHeight(600)` (or appropriate minimums for the content)

### Missing Menu Keyboard Shortcuts
Menu items without keyboard accelerators reduce discoverability and accessibility.
- **Severity:** Low (UX)
- **Pattern:** `Menu::make()` with items that lack `->accelerator('CmdOrCtrl+X')` for common actions
- **Fix:** Add keyboard shortcuts for frequent actions (Save, Copy, Paste, etc.)

### Window Close Events Not Handled
Not handling window close events can leave processes running or data unsaved.
- **Severity:** Medium (correctness)
- **Pattern:** Windows without `WindowClosed` event listener when the app has unsaved state
- **Fix:** Listen for `WindowClosed` event and handle cleanup/confirmation

### Mobile Bridge Functions Without Error Handling
NativePHP mobile plugin bridge functions that don't handle native API failures.
- **Severity:** Medium (error-handling)
- **Pattern:** Bridge function calls without try-catch or error callbacks
- **Fix:** Wrap native API calls in try-catch and provide user-facing error messages

### Missing Permission Checks
Accessing native APIs (camera, location, contacts) without checking/requesting permissions first.
- **Severity:** High (correctness)
- **Pattern:** Direct camera/location/biometric API usage without prior permission check
- **Fix:** Check permission status before accessing the API, request if not granted

### Direct Class Instantiation Instead of Facades
Using NativePHP classes directly instead of the provided facades.
- **Severity:** Low (maintainability)
- **Pattern:** `new \Native\Laravel\Windows\Window(...)` instead of `Window::open(...)`
- **Fix:** Use facades: `Window::`, `Menu::`, `Dialog::`, `Notification::`, etc.
