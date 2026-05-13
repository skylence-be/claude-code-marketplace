---
description: Generate idiomatic Rust tests for a function, module, or integration scenario using rstest, insta snapshots, and cargo-nextest conventions
---

# New Rust Test

Generate idiomatic Rust tests following Rust testing conventions: inline unit tests with `#[cfg(test)]`, parametric cases with `rstest`, snapshot tests with `insta`, and integration tests in `tests/`.

## Specification

$ARGUMENTS

## Process

1. **Identify the target** from the specification (function, module, CLI command, or HTTP endpoint)
2. **Choose the test type**: unit (inline `#[cfg(test)]`), parametric (`rstest`), snapshot (`insta`), integration (`tests/`), or async (`#[tokio::test]`)
3. **Write the test struct or cases** covering the happy path, edge cases, error paths, and boundary conditions
4. **Apply edition 2024 env isolation** if the code under test reads environment variables (see injection pattern below)
5. **Add `insta::assert_snapshot!`** for unstructured output or large serialized values
6. **Register the test file** in `tests/` if writing an integration test (and add a `mod common;` helper if needed)

## Examples

### Unit test with rstest (parametric)

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use rstest::rstest;

    #[rstest]
    #[case("hello world", 2)]
    #[case("", 0)]
    #[case("  spaces  ", 1)]
    fn count_words_parametric(#[case] input: &str, #[case] expected: usize) {
        assert_eq!(count_words(input), expected);
    }

    #[test]
    fn parse_valid_input_returns_ok() {
        let result = parse("valid").unwrap();
        assert_eq!(result.value, "valid");
    }

    #[test]
    fn parse_empty_returns_error() {
        let err = parse("").unwrap_err();
        assert!(matches!(err, ParseError::Empty));
    }
}
```

### Async test with Tokio

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn fetch_data_returns_expected() {
        let client = TestClient::new();
        let result = fetch(&client, "key").await.unwrap();
        assert_eq!(result.id, "key");
    }

    #[tokio::test]
    async fn fetch_missing_key_returns_not_found() {
        let client = TestClient::new();
        let err = fetch(&client, "missing").await.unwrap_err();
        assert!(matches!(err, FetchError::NotFound(_)));
    }
}
```

### Snapshot test with insta

```rust
#[test]
fn report_format_matches_snapshot() {
    let data = sample_report_data();
    let output = render_report(&data);
    insta::assert_snapshot!(output);
}

#[test]
fn json_serialization_snapshot() {
    let event = Event { id: "evt_1".into(), kind: EventKind::Created };
    insta::assert_json_snapshot!(event);
}
```

### Integration test in tests/ with tempfile

```rust
// tests/cli.rs
use assert_cmd::Command;
use tempfile::TempDir;

#[test]
fn init_creates_config_file() {
    let home = TempDir::new().unwrap();
    Command::cargo_bin("my-app").unwrap()
        .env("MY_APP_HOME", home.path())
        .arg("init")
        .assert()
        .success();
    assert!(home.path().join("config.toml").exists());
}
```

### Edition 2024 env isolation (no set_var)

```rust
// production code with injectable override
pub fn data_dir() -> PathBuf { data_dir_with(None) }
pub fn data_dir_with(override_home: Option<&Path>) -> PathBuf {
    override_home
        .unwrap_or_else(|| Path::new(&std::env::var("HOME").unwrap()))
        .join(".local/share/my-app")
}

// test uses the _with variant -- no set_var needed
#[test]
fn data_dir_uses_custom_home() {
    let tmp = TempDir::new().unwrap();
    let dir = data_dir_with(Some(tmp.path()));
    assert!(dir.starts_with(tmp.path()));
}
```

Generate idiomatic Rust tests with descriptive case names, explicit error matching, and edition 2024 env isolation where needed.
