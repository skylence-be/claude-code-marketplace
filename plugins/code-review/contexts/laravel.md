# Laravel Review Rules

Technology-specific review rules for Laravel 11+ applications. Loaded when `laravel/framework` is detected in `composer.json`.

## Detection
- `composer.json` contains `laravel/framework` in `require`
- `artisan` file exists in project root
- `app/Http/Controllers` directory exists

## Anti-Patterns to Flag

### N+1 Query Pattern
Accessing relations in loops without eager loading. One of the most common Laravel performance issues.
- **Severity:** High
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `foreach ($users as $user) { $user->posts... }` without `->with('posts')` on the query
- **Fix:** Add `->with('relation')` to the query or use `$model->loadMissing('relation')`

### Mass Assignment Vulnerability
Models with `$guarded = []` or overly permissive `$fillable` that includes sensitive fields.
- **Severity:** Critical (security)
- **Pattern:** `protected $guarded = []` or `$fillable` containing `is_admin`, `role`, `password`, `email_verified_at`
- **Fix:** Use explicit `$fillable` with only user-submittable fields

### Raw Query with String Interpolation
SQL injection via `DB::raw()` or `DB::select()` with interpolated variables.
- **Severity:** Critical (security)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `DB::raw("... $variable ...")`, `DB::select("... {$var} ...")`
- **Fix:** Use parameter binding: `DB::raw('... ? ...', [$variable])`

### Missing Authorization
Controllers performing actions without checking permissions.
- **Severity:** High (security)
- **Check:** Controller methods that modify data without `$this->authorize()`, `Gate::allows()`, or policy checks
- **Exception:** Public-facing read-only endpoints

### Missing Form Request Validation
Controllers accepting input via `$request->input()` or `$request->all()` without FormRequest validation.
- **Severity:** High
- **Pattern:** `$request->input('field')` or `$request->all()` in controller methods without preceding `$request->validate()` or FormRequest type hint
- **Fix:** Create a FormRequest class with validation rules

### env() Outside Config Files
Using `env()` directly in application code. This breaks config caching (`php artisan config:cache`).
- **Severity:** Medium
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `env('KEY')` anywhere outside `config/*.php` files
- **Fix:** Reference via `config('key.name')` after defining in config file

### Missing Database Transactions
Multi-step database operations without transaction wrapping.
- **Severity:** Medium
- **Pattern:** Multiple `->save()`, `->create()`, `->update()`, `->delete()` calls in a single method without `DB::transaction()`
- **Fix:** Wrap in `DB::transaction(function () { ... })`

### Unbounded Model::all()
Using `Model::all()` on tables that could grow large, without pagination.
- **Severity:** Medium
- **Pattern:** `Model::all()` or `Model::get()` without `->limit()` or `->paginate()`
- **Exception:** Lookup tables with known small row counts

### Missing Rate Limiting
Authentication or API endpoints without rate limiting middleware.
- **Severity:** Medium (security)
- **Check:** Login, registration, password reset, and API routes without `throttle` middleware
- **Fix:** Add `->middleware('throttle:60,1')` or use RateLimiter

### Missing Migration Down Method
Migrations with `up()` but empty or missing `down()`, making rollback impossible.
- **Severity:** Low
- **Check:** Migration files where `down()` is empty or only contains `//`
- **Exception:** Drop-column migrations where down is complex

### Debug Statements
Laravel-specific debug functions left in code.
- **Severity:** Medium
- **Pattern:** `dd(`, `dump(`, `ray(`, `logger(` (when used for debugging, not actual logging)
- **Confidence:** Check if in a test file (reduce confidence) or production code (increase confidence)

### Route Model Binding Type Mismatch
Controller method type hints that don't match route model binding expectations.
- **Severity:** Medium
- **Pattern:** Route uses `{user}` but controller parameter is typed as `int` instead of `User`

### Missing Eager Loading on API Resources
API Resources that access relations without ensuring they're loaded.
- **Severity:** Medium
- **Pattern:** `$this->relation->field` in Resource without `whenLoaded('relation')`
- **Fix:** Use `$this->whenLoaded('relation', fn () => ...)`
