# Filament Review Rules

Technology-specific review rules for Filament 5 admin panels. Loaded when `filament/filament` is detected in `composer.json`.

## Detection
- `composer.json` contains `filament/filament` in `require`
- PHP classes using `Filament\` namespace imports
- `app/Filament/` directory exists

## Anti-Patterns to Flag

### Wrong Get/Set Namespace
Using the old Filament 4 namespace for closure injection utilities.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `use Filament\Forms\Get;` or `use Filament\Forms\Set;`
- **Fix:** `use Filament\Schemas\Components\Utilities\Get;` and `use Filament\Schemas\Components\Utilities\Set;`

### Using ->reactive() Instead of ->live()
`->reactive()` does not exist in Filament 5. This was renamed.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `->reactive()` on any form component
- **Fix:** `->live()` or `->live(onBlur: true)`

### Missing Deferred Loading on Tables
Tables without `->deferLoading()` block page load while fetching data.
- **Severity:** Medium (performance)
- **Pattern:** Table definition without `->deferLoading()` on tables with potentially many rows
- **Fix:** Add `->deferLoading()` to the table definition

### Too Many Visible Columns
Tables with more than 10 visible columns without `->toggleable()`.
- **Severity:** Low (maintainability)
- **Pattern:** Table with > 10 `TextColumn`/similar definitions without `->toggleable(isToggledHiddenByDefault: true)` on lower-priority columns
- **Fix:** Add `->toggleable(isToggledHiddenByDefault: true)` to less important columns

### Missing Eager Loading on Relation Columns
Relation columns without `->preload()` causing N+1 queries.
- **Severity:** High (performance)
- **Pattern:** `->relationship('relation', 'field')` on Select or other components without corresponding eager load
- **Fix:** Add relationship to `$table->query()` `with()` or use `->preload()` on Select

### Magic Strings Instead of Enums
Using string literals where Filament 5 provides enum classes.
- **Severity:** Low
- **Pattern:** `->weight('bold')` instead of `->weight(FontWeight::Bold)`, `->color('danger')` where Color enum exists
- **Fix:** Use the enum: `FontWeight::Bold`, `Color::Danger`, etc.

### String Icon Names Instead of Heroicon Enum
Using string icon identifiers instead of the Heroicon enum (Filament 5).
- **Severity:** Low
- **Pattern:** `->icon('heroicon-o-pencil')`
- **Fix:** `->icon(Heroicon::Pencil)` (Filament 5 uses the Heroicon enum)

### Missing Policies on Resources
Resources without corresponding Policy classes means no authorization.
- **Severity:** High (security)
- **Check:** Resource class exists but no matching Policy in `app/Policies/`
- **Fix:** Create a Policy class and register it in `AuthServiceProvider`

### Redundant ignoreRecord on Unique Validation
Specifying `ignoreRecord: true` on unique validation — this is already the default in Filament 5.
- **Severity:** Low
- **Pattern:** `->unique(ignoreRecord: true)` in form field validation
- **Fix:** Just use `->unique()` — `ignoreRecord` defaults to true

### Missing Searchable on Large Select Fields
Select fields with many options (> 10) without `->searchable()`.
- **Severity:** Medium (UX)
- **Pattern:** `Select::make('field')->options([...many items...])` without `->searchable()`
- **Fix:** Add `->searchable()` for better UX on large option sets
