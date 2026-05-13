---
name: rust-testing-patterns
description: Rust testing patterns covering unit tests with #[cfg(test)], integration tests in tests/, cargo-nextest, insta snapshots, rstest parametric tests, mockito for HTTP, proptest for invariants, and edition 2024 env isolation (std::env::set_var is unsafe). Use when writing Rust tests, reviewing test quality, or setting up a test suite.
---

# Rust Testing Patterns

## When to Use This Skill

- Writing unit or integration tests for a Rust crate
- Reviewing tests for anti-patterns (env mutation, `.unwrap()` in helpers, flaky sleeps)
- Setting up `cargo-nextest` and snapshot testing with `insta`
- Choosing between unit, integration, and property-based testing
- Isolating tests that depend on environment variables (edition 2024 gotcha)

## Core Concepts

| Concept | Rule |
|---------|------|
| **Unit tests inline** | `#[cfg(test)] mod tests` at the bottom of each `.rs` file; test the module's invariants |
| **Integration tests separate** | `tests/<feature>.rs` files; one file per feature area; helpers in `tests/common/mod.rs` |
| **cargo-nextest over cargo test** | Faster, better output, per-test timeout, retry support |
| **insta for snapshots** | Snapshot tests catch unintended output changes without writing assertions by hand |
| **rstest for parametric** | `#[rstest]` replaces manual loop-based table tests with cleaner syntax |
| **No flaky sleeps** | Never `std::thread::sleep` for synchronization; use channels or condvars |
| **Tempfile for filesystem** | Always isolate filesystem tests with `tempfile::TempDir`; never write to `~` |
| **Edition 2024 gotcha** | `std::env::set_var` is `unsafe` in edition 2024. Inject env differently (see below) |

## Quick Reference

```rust
// Unit test
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_valid_input() {
        let result = parse("hello").unwrap();
        assert_eq!(result.value, "hello");
    }

    #[test]
    fn parse_empty_returns_error() {
        assert!(parse("").is_err());
    }
}

// Parametric with rstest
use rstest::rstest;

#[rstest]
#[case("hello", true)]
#[case("", false)]
#[case("  ", false)]
fn validate_input(#[case] input: &str, #[case] expected: bool) {
    assert_eq!(validate(input), expected);
}

// Snapshot with insta
#[test]
fn renders_output() {
    let output = render_report(&sample_data());
    insta::assert_snapshot!(output);
}

// Async test
#[tokio::test]
async fn fetch_returns_data() {
    let client = setup_client().await;
    let result = client.fetch("key").await.unwrap();
    assert_eq!(result, "expected");
}
```

## Env Isolation (Edition 2024)

`std::env::set_var` is now `unsafe` in edition 2024. Never call it from test code. Two patterns instead:

**Pattern 1: CLI integration tests.** Use `assert_cmd` and chain `.env(...)`:
```rust
use assert_cmd::Command;
use tempfile::TempDir;

#[test]
fn cli_uses_custom_home() {
    let home = TempDir::new().unwrap();
    Command::cargo_bin("my-app").unwrap()
        .env("MY_APP_HOME", home.path())
        .arg("init")
        .assert()
        .success();
}
```

**Pattern 2: Unit tests with injection.** Add an `_with(override)` variant to functions that read env:
```rust
// production
pub fn config_dir() -> PathBuf {
    config_dir_with(None)
}

// testable
pub fn config_dir_with(override_home: Option<&Path>) -> PathBuf {
    let home = override_home
        .map(|p| p.to_owned())
        .unwrap_or_else(|| dirs::home_dir().unwrap());
    home.join(".config").join("my-app")
}

#[test]
fn config_dir_uses_override() {
    let tmp = TempDir::new().unwrap();
    let dir = config_dir_with(Some(tmp.path()));
    assert!(dir.starts_with(tmp.path()));
}
```

## Best Practices

1. **Run tests with `cargo nextest run`.** Better output, parallel by default, per-test timeouts.
2. **Snapshot unstructured output.** Use `insta::assert_snapshot!` for anything you'd otherwise assert with a giant string literal.
3. **Parametric over loops.** `#[rstest]` cases are individually named in output; a loop produces a single test name.
4. **Never `#[ignore]` a flaky test.** Fix it or delete it; ignored tests rot.
5. **Use `proptest` for invariant checks.** Model-check functions like serialization round-trips with `proptest::proptest!`.
6. **Name helper functions with `assert_` prefix.** Signals they can fail a test; call `assert_*` helpers from test code only.
7. **Use `mockito` for HTTP.** Spin up a mock HTTP server per test; never hit real external services in unit/integration tests.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `std::env::set_var(...)` in tests | Edition 2024: this is `unsafe`; use `.env(...)` on `assert_cmd` or injection parameters |
| `thread::sleep` for async coordination | Use channels, `tokio::sync::Notify`, or test-specific sync primitives |
| Tests that depend on `$HOME` or `~/.config` | Isolate with `TempDir` and path injection |
| `HashMap` serialization asserted by exact string | Key order is non-deterministic; assert structure or use `insta` |
| Asserting on wall-clock timestamps | Use regex match or date-only comparison; exact timestamps are flaky |
| `.unwrap()` in test helpers without context | Use `.expect("context")` so failures are readable |

## Next Steps

- Review `rust-project-structure` for where to place test helpers and fixture files
- Review `rust-error-handling` for Result patterns in fallible test setup
