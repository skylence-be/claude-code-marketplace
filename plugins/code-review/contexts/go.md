# Go Review Rules

Technology-specific review rules for Go code. Loaded when `.go` files are in the changeset or `go.mod` exists.

## Detection
- `.go` files in the changeset
- `go.mod` exists in the project root
- `go.sum` exists alongside `go.mod`

## Anti-Patterns to Flag

### Unchecked Errors
Ignoring returned errors hides failures silently.
- **Severity:** High (correctness)
- **Confidence boost:** +3 (the most common Go bug)
- **Pattern:** `_ = someFunc()` without a comment, `someFunc()` on its own line when it returns `error`, `.Write(` or `.Close(` result discarded
- **Fix:** Handle the error: return it, log it, or add a comment explaining why it is safe to ignore
- **Exception:** `defer f.Close()` in non-critical paths (known accepted pattern); reduce confidence to Low

### Error Comparison With `==` Instead of `errors.Is`
Direct `==` comparison breaks when the error is wrapped.
- **Severity:** High (correctness)
- **Confidence boost:** +2
- **Pattern:** `err == io.EOF`, `err == ErrNotFound`, `err == sql.ErrNoRows` — any sentinel compared with `==`
- **Fix:** `errors.Is(err, io.EOF)` — works through `fmt.Errorf("%w", ...)` wrap chains

### Returning Concrete Error Type From Exported Function
Returning a concrete error type from an exported function causes a nil-interface bug.
- **Severity:** High (correctness)
- **Pattern:** `func Foo() *MyError { return nil }` — callers check `err != nil` and get `true` even for nil
- **Fix:** Return `error` interface; callers use `errors.As` to extract the concrete type

### Goroutine Without Exit Path (Goroutine Leak)
A goroutine that blocks forever without a cancellation mechanism is a leak.
- **Severity:** High (resource leak)
- **Confidence boost:** +2
- **Pattern:** `go func() { for { ... } }()` with no `ctx.Done()` or done-channel select; goroutine blocked on channel send/receive with no paired receiver/sender
- **Fix:** Add a `<-ctx.Done()` case in the select, or use `errgroup` with a cancellable context

### `t.Fatal` Called From a Goroutine in Tests
`t.Fatal` called from a goroutine that isn't the test goroutine panics after the test has returned.
- **Severity:** High (test correctness)
- **Pattern:** `go func() { ... t.Fatal(...) ... }()` or `go func() { ... t.Error(...) ... }()` where the call is inside a goroutine spawned during a test
- **Fix:** Collect the error in a channel and call `t.Fatal` in the test goroutine after `wg.Wait()`

### Storing `context.Context` in a Struct Field
Context is per-call, not per-object. Storing it breaks cancellation across calls.
- **Severity:** Medium
- **Pattern:** `type Foo struct { ctx context.Context }` or `type Foo struct { ... ctx context.Context ... }`
- **Fix:** Pass context as the first parameter on each method call

### Copying a `sync.Mutex`
Copying a mutex creates two independent mutexes from what was one, destroying synchronization.
- **Severity:** High (race condition)
- **Confidence boost:** +3
- **Pattern:** Struct with embedded `sync.Mutex` or `sync.RWMutex` passed by value; `go vet` reports this as `copylocks`
- **Fix:** Pass the struct by pointer, or embed `*sync.Mutex`

### Missing `context.Context` First Parameter
Functions that do I/O or block should accept `context.Context` as the first parameter for cancellation.
- **Severity:** Medium
- **Pattern:** Functions calling `http.`, `sql.`, `grpc.`, or channel operations without a `ctx context.Context` first parameter
- **Fix:** Add `ctx context.Context` as the first parameter and propagate it to all I/O calls

### Logging and Returning the Same Error
Handling an error in two places (log AND return) causes double-reporting in callers.
- **Severity:** Medium
- **Pattern:** `log.Printf("...", err); return ..., err` in the same error branch
- **Fix:** Choose one: return the error (let callers log at the right level), or log and return a sentinel/nil

### Table-Driven Tests Without Names
Unnamed test cases make failing test output unreadable.
- **Severity:** Low
- **Pattern:** Table-driven tests where the struct doesn't have a `name string` field, or `t.Run` uses an index `fmt.Sprintf("%d", i)`
- **Fix:** Add `name string` as the first struct field; use descriptive names that explain the case

### Missing `t.Helper()` in Test Helper Functions
Without `t.Helper()`, test failures point to the helper, not the call site.
- **Severity:** Low
- **Pattern:** Functions that accept `*testing.T` and call `t.Error` or `t.Fatal` without `t.Helper()` as the first line
- **Fix:** Add `t.Helper()` as the first statement

### `fmt.Sprintf` for Simple Numeric Conversion
`strconv` is significantly faster than `fmt.Sprintf` for primitive-to-string conversions.
- **Severity:** Low (only matters in hot paths)
- **Pattern:** `fmt.Sprintf("%d", n)`, `fmt.Sprintf("%f", f)`, `fmt.Sprintf("%s", s)` — single-value numeric conversions
- **Fix:** `strconv.Itoa(n)`, `strconv.FormatFloat(f, 'f', -1, 64)` — only flag when in a loop or hot path

### Pointer to Interface Parameter
Passing a pointer to an interface is almost always wrong — interfaces already hold a pointer internally.
- **Severity:** Medium
- **Pattern:** `func Foo(r *io.Reader)` or `func Foo(h *http.Handler)` — pointer to an interface type
- **Fix:** `func Foo(r io.Reader)` — interfaces don't need an extra pointer

## Security Checks

### `math/rand` for Security-Sensitive Values
`math/rand` is not cryptographically secure.
- **Severity:** High (security)
- **Confidence boost:** +3
- **Pattern:** `rand.Int()`, `rand.Intn()`, `rand.Read()` from `math/rand` used for tokens, passwords, session IDs, or nonces
- **Fix:** Use `crypto/rand` for all security-sensitive randomness

### Hardcoded Credentials or Secrets
Secrets in source code are leaked in version control history.
- **Severity:** High (security)
- **Pattern:** `password := "..."`, `apiKey := "sk-..."`, `secret := "..."` — literal strings assigned to secret-sounding variables
- **Fix:** Load from environment variables or a secrets manager; never commit secrets

### SQL Injection via String Concatenation
Building SQL queries with `+` or `fmt.Sprintf` allows injection attacks.
- **Severity:** High (security)
- **Pattern:** `fmt.Sprintf("SELECT * FROM users WHERE id = %d", id)` passed to `db.Query`; string concatenation in SQL calls
- **Fix:** Use parameterized queries: `db.QueryContext(ctx, "SELECT * FROM users WHERE id = $1", id)`

### Unbounded HTTP Client (No Timeout)
`http.DefaultClient` has no timeout — an attacker or misbehaving server can hold connections forever.
- **Severity:** Medium (security / availability)
- **Pattern:** `http.Get(url)`, `http.Post(...)`, `http.DefaultClient.Do(...)` without a custom client with `Timeout`
- **Fix:** Use a custom `&http.Client{Timeout: 30 * time.Second}`

## Confidence Scoring Adjustments

- **Generated code** (files with `// Code generated` header): reduce all findings to Low — these files are not manually maintained
- **Test files** (`_test.go`): reduce `gosec` findings by 2; some patterns are intentional in tests
- **`internal/` packages**: interface design issues are less critical — no external consumers to break
