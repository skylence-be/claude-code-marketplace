---
name: rust-coding-standards
description: Rust standards: rustfmt, naming, edition 2024 idioms, workspace lints. Use when writing Rust or reviewing for style.
---

# Rust Coding Standards

## When to Use This Skill

- Writing new Rust packages and ensuring idiomatic style from the start
- Reviewing code for naming violations or formatting issues
- Onboarding to a codebase with unfamiliar Rust conventions
- Setting up a style guide for a Rust team
- Understanding why rustfmt decisions cannot be debated

## Core Concepts

| Concept | Rule |
|---------|------|
| **rustfmt** | Non-negotiable. All code must be rustfmt-formatted. No discussion. |
| **Naming** | `snake_case` for functions/variables/modules, `CamelCase` for types/traits, `SCREAMING_SNAKE_CASE` for constants/statics |
| **`Self`** | Use `Self` instead of repeating the type name inside `impl` blocks |
| **Doc comments** | Every exported `pub` type, function, method, and trait needs a `///` doc comment |
| **No `mod.rs`** | Edition 2018+ uses `module_name.rs` or `module_name/` with files inside; `mod.rs` is legacy |
| **`pub(crate)` first** | Default to the narrowest visibility. Use `pub(crate)` before `pub` for anything internal |
| **Error handling split** | `thiserror` in libraries, `anyhow` in binaries. Never expose `anyhow::Error` from a public library API |

## Quick Reference

```rust
// Naming: snake_case functions, CamelCase types
pub struct HttpClient {
    base_url: String,    // private field
    timeout_secs: u64,
}

// Use Self inside impl
impl HttpClient {
    pub fn new(base_url: impl Into<String>) -> Self {
        Self { base_url: base_url.into(), timeout_secs: 30 }
    }

    pub fn timeout_secs(&self) -> u64 { self.timeout_secs }
}

// Constants: SCREAMING_SNAKE_CASE
const MAX_RETRIES: u32 = 3;

// Module naming: no mod.rs; use http_client.rs directly
// pub mod http_client;  (in lib.rs)

// Workspace lints (in root Cargo.toml)
// [workspace.lints.rust]
// unsafe_code = "warn"
//
// [workspace.lints.clippy]
// all = "warn"
// pedantic = "warn"
// nursery = "warn"
```

## Best Practices

1. **Run rustfmt on save.** Configure your editor or CI to enforce it; never debate spacing.
2. **Use `clippy::all` + `pedantic`.** Set in `[workspace.lints]` so every crate inherits.
3. **Name variables by role, not type.** `user` not `user_string`, `count` not `int_count`.
4. **Short names for short scopes.** `i`, `n`, `v` are fine in iterators; use longer names in wider scope.
5. **Avoid redundant module qualification.** `http::Client` not `http::HttpClient`.
6. **Comment exported symbols.** Every exported item needs a `///` doc comment starting with a description.
7. **One concept per file.** Group by responsibility, not one file per type.

## LLM Anti-Patterns to Flag

These are patterns language models write reflexively that a human Rust developer would not:

| Anti-Pattern | Fix |
|-------------|-----|
| `.clone()` to silence the borrow checker | Reach for `&str`, `Cow<'_, str>`, or restructure borrows first |
| `String` everywhere | Use `&str` for read-only, `Cow<'_, str>` for sometimes-owned, `String` only when ownership is needed |
| `Box<dyn Trait>` as a default | Prefer generics `<T: Trait>` unless the impl set is open or you need object safety |
| `Arc<Mutex<T>>` by reflex | Ask if `&mut self` or message passing solves it first |
| `.unwrap()` in library code | Return `Result` or `Option`; `.unwrap()` belongs only in tests and `main` |
| `pub` on everything | Default to private; widen only when callers actually need it |
| `#[allow(clippy::...)]` everywhere | Fix the lint; suppress only with a `// SAFETY:` or `// REASON:` comment |

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `mod.rs` in new code | Use `module_name.rs` alongside a `module_name/` directory |
| Copying a `Mutex` or `RwLock` | Use `Arc<Mutex<T>>` or pass by reference; lock types are not `Copy` |
| `else` after `return` | Remove the `else`; code falls through naturally |
| `use super::*` in non-test modules | Explicit imports; glob imports hide where names come from |
| `panic!` in library code | Return `Result` or `Option`; never panic across a library boundary |

## Next Steps

- Review `rust-error-handling` for the thiserror/anyhow split and Result patterns
- Review `rust-ownership-borrowing` for borrow-checker strategies and `Cow` usage
