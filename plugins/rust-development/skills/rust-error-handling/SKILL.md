---
name: rust-error-handling
description: Idiomatic Rust error handling covering thiserror for libraries, anyhow for binaries, the ? operator, error wrapping, custom error types, and the library/binary split. Use when implementing error handling, designing crate error contracts, reviewing code for .unwrap() misuse, or deciding between error strategies.
---

# Rust Error Handling

## When to Use This Skill

- Implementing error handling for a new crate or service
- Reviewing Rust code for `.unwrap()` in library code or double-handling
- Designing the error contract for a public crate API
- Deciding between `thiserror`, `anyhow`, and custom error types
- Adding error context without losing the original error chain

## Core Concepts

| Concept | Rule |
|---------|------|
| **Libraries use `thiserror`** | Typed errors let callers match on variants; never expose `anyhow::Error` from a library |
| **Binaries use `anyhow`** | `anyhow::Result<()>` is fine in `main`, CLI handlers, and integration test harnesses |
| **`?` operator everywhere** | Use `?` to propagate errors; explicit `.unwrap()` belongs only in tests and examples |
| **No `.unwrap()` in lib code** | Use `expect("invariant explanation")` only when the invariant is documented; return `Result` otherwise |
| **No `panic!` in libraries** | `panic!` must not cross a library boundary; return `Result` or `Option` |
| **Wrap with context** | Add context when propagating: `map_err(|e| MyError::Io { path: path.clone(), source: e })` |
| **Single point of handling** | Log OR return an error, not both; double-handling creates duplicate log noise |

## Quick Reference

```rust
// Library error (thiserror)
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("not found: {0}")]
    NotFound(String),

    #[error("IO error at {path}")]
    Io {
        path: PathBuf,
        #[source]
        source: io::Error,
    },

    #[error("invalid input: {message}")]
    InvalidInput { message: String },
}

// Function returning typed Result
pub fn load(path: &Path) -> Result<Config, AppError> {
    let text = fs::read_to_string(path).map_err(|e| AppError::Io {
        path: path.to_owned(),
        source: e,
    })?;
    parse(&text)
}

// Binary entry point (anyhow)
fn main() -> anyhow::Result<()> {
    let cfg = load(Path::new("config.toml"))?;
    run(cfg)?;
    Ok(())
}
```

## Optional: Stable Error Codes

For projects that surface errors to users or external systems, a stable code pattern prevents breaking changes when error messages are reworded:

```rust
#[derive(Debug, Error)]
pub enum AppError {
    #[error("[PROJ-DATA-001] record not found: {id}")]
    NotFound { id: String },

    #[error("[PROJ-IO-001] failed to read {path}")]
    ReadFailed { path: PathBuf, #[source] source: io::Error },
}
```

Pattern: `PROJ-{DOMAIN}-{NNN}` where `PROJ` is your project prefix, `DOMAIN` groups errors by subsystem, and `NNN` is a monotonically increasing number. Codes are additive; never reuse or renumber.

## Best Practices

1. **Return `Result`, not panics.** Every fallible operation in a library must return `Result`.
2. **Use `#[source]` on wrapped errors.** This enables `.source()` traversal and `anyhow` chain display.
3. **Error strings are lowercase.** No trailing punctuation; they compose into larger messages.
4. **`expect()` over `unwrap()`.** If you must use an infallible unwrap, write `expect("why this can never fail")`.
5. **Avoid `Box<dyn Error>` in library APIs.** It erases type information; callers cannot match on variants.
6. **Document your error variants.** Add a `///` doc comment on each variant explaining when it is returned.
7. **`Must*` functions only at program startup.** `Regex::new(...).unwrap()` in a `const` or `OnceLock` is fine; never in a request handler.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `.unwrap()` in library code | Return `Result<_, MyError>` and use `?` |
| `panic!("not found")` in a library | Return `Err(MyError::NotFound(...))` |
| `anyhow::Error` in a public API | Use `thiserror` so callers can match on error variants |
| Log and return the same error | Choose one: return the error so callers log at the right level |
| `Box<dyn std::error::Error>` in API | Define a concrete error enum with `thiserror` |
| Converting errors with `.to_string()` | Use `.map_err(MyError::from)` or `#[from]` to preserve the chain |

## Next Steps

- Review `rust-coding-standards` for the `.unwrap()` no-go list and workspace lint setup
- Review `rust-async-tokio` for error propagation across `spawn_blocking` and async boundaries
