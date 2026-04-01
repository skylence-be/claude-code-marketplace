# Livewire Review Rules

Technology-specific review rules for Livewire 4+ components. Loaded when `livewire/livewire` is detected in `composer.json`.

## Detection
- `composer.json` contains `livewire/livewire` in `require`
- `.blade.php` files containing `wire:` directives
- PHP classes extending `Livewire\Component`

## Anti-Patterns to Flag

### Missing Validation on Public Properties
Public properties that accept user input without `#[Validate]` attributes.
- **Severity:** High (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** Public property bound via `wire:model` without `#[Validate(...)]`
- **Fix:** Add `#[Validate('required|string|max:255')]` attribute

### Missing #[Locked] on Sensitive Properties
Properties like IDs, prices, or roles that should not be tampered with via Livewire's wire protocol.
- **Severity:** High (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** Public properties named `$id`, `$userId`, `$price`, `$role`, `$total` without `#[Locked]`
- **Fix:** Add `#[Locked]` attribute to prevent client-side tampering

### N+1 in Render Methods
Database queries or relation access inside `render()` without computed property caching.
- **Severity:** High (performance)
- **Pattern:** `$this->model->relation` or query calls inside `render()` without `#[Computed]`
- **Fix:** Use a computed property: `#[Computed] public function items() { return ...; }`

### Heavy Computation in render()
Expensive operations in render that execute on every re-render.
- **Severity:** Medium (performance)
- **Pattern:** Complex array transformations, API calls, or file operations inside `render()`
- **Fix:** Move to `#[Computed]` property which caches for the request lifecycle

### Incorrect wire:model Usage
Using `wire:model` without `.live` when real-time validation is intended, or using `.live` unnecessarily.
- **Severity:** Medium
- **Pattern:** Form with validation feedback but `wire:model` without `.live` modifier
- **Note:** `.live` sends a request on every keystroke — only use when needed

### Large Payloads in wire:model
Binding large arrays or objects directly to public properties.
- **Severity:** Medium (performance)
- **Pattern:** `wire:model="largeArray"` where the property holds 50+ items
- **Fix:** Use Form Objects or paginate the data

### Missing #[Url] on Filter Properties
Searchable/filterable properties that should be bookmarkable but lack URL binding.
- **Severity:** Low
- **Pattern:** Public property used for search/filter (e.g., `$search`, `$filter`, `$sortBy`) without `#[Url]`
- **Fix:** Add `#[Url]` attribute for URL state persistence

### Missing #[Throttle] on Data-Modifying Actions
Actions that create, update, or delete data without throttling.
- **Severity:** Medium (security)
- **Pattern:** Public methods that call `->save()`, `->create()`, `->delete()` without `#[Throttle]`
- **Fix:** Add `#[Throttle(5, 60)]` to limit to 5 calls per 60 seconds

### Form Objects Without Validation
Livewire Form Objects that don't define validation rules.
- **Severity:** Medium
- **Pattern:** Class extending `Livewire\Form` without `#[Validate]` attributes on properties
- **Fix:** Add validation attributes to all form properties
