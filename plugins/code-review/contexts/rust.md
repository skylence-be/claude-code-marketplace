# Rust Review Rules

Technology-specific review rules for Rust code. Loaded when `.rs` files are in the changeset or `Cargo.toml` exists.

## Detection
- `.rs` files in the changeset
- `Cargo.toml` exists in the project root
- `Cargo.lock` exists alongside `Cargo.toml`

## Anti-Patterns to Flag

### `.unwrap()` or `.expect()` in Non-Test Code
Calling `.unwrap()` in library or server code panics in production with no recovery path.
- **Severity:** High (correctness)
- **Confidence boost:** +3 (the most common Rust bug in LLM-generated code)
- **Pattern:** `.unwrap()` or `.expect(...)` outside `#[cfg(test)]` blocks, `tests/` files, `examples/`, or `benches/`
- **Fix:** Return `Result<_, E>` and use `?` to propagate; or use `.unwrap_or_default()` / `.unwrap_or_else(...)` when a fallback is intentional
- **Exception:** `.unwrap()` on infallible operations (`Mutex::lock()` in non-async single-thread code, `Regex::new(...)` in a `static`); reduce confidence to Low

### `std::sync::MutexGuard` Held Across `.await`
A `std::sync::MutexGuard` held across an `.await` point causes a deadlock on a Tokio multi-thread runtime.
- **Severity:** High (deadlock)
- **Confidence boost:** +3
- **Pattern:** `let guard = mutex.lock().unwrap();` followed by an `.await` before `drop(guard)` or the end of the guard's scope
- **Fix:** Drop the guard before awaiting (extract the needed value inside a block), or switch to `tokio::sync::Mutex` when the guard must span an await

### Blocking Call on the Tokio Executor
Calling synchronous blocking I/O or CPU-bound work directly inside an `async fn` starves the Tokio executor.
- **Severity:** High (performance / availability)
- **Confidence boost:** +3
- **Pattern:** `std::fs::read`, `std::fs::write`, `std::net::TcpStream`, `thread::sleep`, CPU-bound loops directly inside `async fn` without `spawn_blocking`
- **Fix:** `tokio::task::spawn_blocking(|| { ... }).await?`

### `unsafe` Block Without `// SAFETY:` Comment
Every `unsafe` block must have a `// SAFETY:` comment explaining why the invariants hold.
- **Severity:** High (soundness)
- **Confidence boost:** +3
- **Pattern:** `unsafe {` on a line not immediately preceded by a `// SAFETY:` comment
- **Fix:** Add `// SAFETY: <invariant explanation>` on the line directly above the `unsafe {`

### `panic!` in Library Code
`panic!` must not cross a library boundary; callers have no way to recover.
- **Severity:** High (correctness)
- **Confidence boost:** +2
- **Pattern:** `panic!(...)`, `unreachable!(...)`, `todo!(...)`, `unimplemented!(...)` in `src/lib.rs` or any non-test module that is not a binary entry point
- **Fix:** Return `Err(MyError::Unexpected(...))` instead; use `todo!()` only in WIP code that is never reached

### `mem::transmute` Without Proof
`mem::transmute` bypasses all type safety and is almost always replaceable.
- **Severity:** High (soundness)
- **Confidence boost:** +3
- **Pattern:** `std::mem::transmute(...)` or `mem::transmute(...)`
- **Fix:** Use `bytemuck::cast` (verifies layout compatibility at compile time) or restructure to avoid the transmute

### Manual `impl Send` or `impl Sync` Without a `// SAFETY:` Comment
Manually implementing `Send` or `Sync` asserts thread-safety; the assertion must be proven.
- **Severity:** High (soundness)
- **Confidence boost:** +2
- **Pattern:** `unsafe impl Send for` or `unsafe impl Sync for` without a preceding `// SAFETY:` comment
- **Fix:** Add a `// SAFETY:` comment citing the underlying contract (e.g., "The C library documents this handle as thread-safe")

### `Arc<Mutex<T>>` Where `&mut self` Would Suffice
Reflexive `Arc<Mutex<T>>` obscures ownership and adds unnecessary locking overhead.
- **Severity:** Medium
- **Pattern:** `Arc<Mutex<T>>` on a type that is only ever accessed from one call site or one task at a time
- **Fix:** Use `&mut self` if the caller can hold exclusive access; use message passing if concurrency is needed

### Reflexive `.clone()` to Silence the Borrow Checker
A `.clone()` that exists only to satisfy the borrow checker usually signals a design problem.
- **Severity:** Medium
- **Pattern:** `.clone()` on `String`, `Vec`, or large structs in a hot path; multiple `.clone()` calls on the same value within one function
- **Fix:** Use `&str` instead of `String`, `&[T]` instead of `Vec<T>`, or restructure the borrow to avoid the clone

### `anyhow::Error` in a Public Library API
Public library functions that return `anyhow::Error` force callers to downcast blindly.
- **Severity:** Medium
- **Pattern:** `pub fn ... -> anyhow::Result<...>` or `pub fn ... -> Result<..., anyhow::Error>` in a library crate
- **Fix:** Define a typed error enum with `thiserror`; callers can then match on variants

### Missing `#[must_use]` on an Important Return Value
Callers that silently discard a `Result` or a builder return value create silent bugs.
- **Severity:** Low
- **Pattern:** Exported functions that return `Result<_, _>` or a `Builder` type without `#[must_use]`
- **Fix:** Add `#[must_use]` to the function or return type; the compiler will warn callers who ignore it

### `#[allow(clippy::...)]` Without an Explanatory Comment
Blanket lint suppression hides real issues without a paper trail.
- **Severity:** Low
- **Pattern:** `#[allow(clippy::...)]` without a comment explaining why the suppression is intentional
- **Fix:** Add a comment: `// REASON: <justification>`

### `unwrap_or_default()` Masking a Real Error Path
`unwrap_or_default()` silently swallows errors that callers should see.
- **Severity:** Medium
- **Pattern:** `.unwrap_or_default()` on a `Result<_, E>` where `E` carries meaningful information
- **Fix:** Match on the error or propagate it; only use `unwrap_or_default()` when the error is truly irrelevant

## Security Checks

### Hardcoded Credentials or Secrets
Secrets in source code are leaked in version control history.
- **Severity:** High (security)
- **Confidence boost:** +3
- **Pattern:** `let password = "..."`, `let api_key = "sk-..."`, `const SECRET: &str = "..."` assigned to secret-sounding variables
- **Fix:** Load from environment variables or a secrets manager; never commit secrets

### `rand::thread_rng()` for Security-Sensitive Values
`rand::thread_rng()` is not cryptographically secure for secret generation.
- **Severity:** High (security)
- **Confidence boost:** +3
- **Pattern:** `rand::thread_rng().gen::<...>()` or `rand::random::<...>()` used for tokens, passwords, session IDs, or nonces
- **Fix:** Use `rand::rngs::OsRng` or `getrandom::getrandom()` for all security-sensitive randomness

### SQL Injection via `format!` or String Concatenation
Building SQL queries with `format!` allows injection attacks.
- **Severity:** High (security)
- **Confidence boost:** +3
- **Pattern:** `format!("SELECT * FROM users WHERE id = {}", id)` passed to a query function; string concatenation in SQL calls
- **Fix:** Use parameterized queries: `sqlx::query!("SELECT * FROM users WHERE id = $1", id)`

### Unbounded `reqwest::Client` Without Timeout
A `reqwest::Client` with no timeout allows a misbehaving server to hold connections forever.
- **Severity:** Medium (security / availability)
- **Pattern:** `reqwest::Client::new()` or `reqwest::get(url)` without a `.timeout(Duration::from_secs(...))` on the client builder
- **Fix:** `reqwest::Client::builder().timeout(Duration::from_secs(30)).build()?`

### `unsafe` FFI Without Input Validation
Calling C FFI functions with unvalidated pointer or length arguments leads to undefined behavior.
- **Severity:** High (security / soundness)
- **Pattern:** `extern "C"` function calls where pointer arguments are not checked for null and length arguments are not validated before the `unsafe` block
- **Fix:** Validate all inputs at the FFI boundary before entering `unsafe`; document the validation in the `// SAFETY:` comment

## Confidence Scoring Adjustments

- **Generated code** (files with `// @generated` or `// This file is auto-generated` header): reduce all findings to Low; these files are not manually maintained
- **Test files** (`#[cfg(test)]`, files under `tests/`, `benches/`, `examples/`): `.unwrap()`, `.expect()`, and `panic!` are expected and acceptable; reduce to Info
- **`*-sys` crates and FFI wrapper crates**: `unsafe` blocks are expected; require only the `// SAFETY:` comment check
- **`build.rs` files**: blocking I/O is intentional (runs before compilation); suppress executor-starvation findings
