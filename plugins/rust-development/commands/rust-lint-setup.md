---
description: Set up the Rust linting stack with rustfmt.toml, clippy.toml, workspace lints, cargo-deny deny.toml, and a GitHub Actions CI snippet
---

# Rust Lint Setup

Configure the Rust linting stack with `rustfmt`, `clippy`, `cargo-deny`, and optional `cargo-audit` for a production-ready codebase.

## Specification

$ARGUMENTS

## Process

1. **Detect workspace vs single crate** from the presence of a root `[workspace]` table in `Cargo.toml`
2. **Write `rustfmt.toml`** with recommended formatting options
3. **Write `clippy.toml`** for lint-level configuration that cannot go in `Cargo.toml`
4. **Add `[workspace.lints]` or `[lints]`** in `Cargo.toml` with `clippy::all`, `pedantic`, `nursery`, and narrow exceptions
5. **Write `deny.toml`** for `cargo-deny` with license, advisories, and duplicate-version checks
6. **Add CI step** in `.github/workflows/ci.yml` for lint, fmt, deny, and audit

## Linter selection rationale

| Tool | Catches |
|------|---------|
| `rustfmt` | Formatting (non-negotiable; CI fails on diff) |
| `clippy::all` | 600+ correctness and style lints |
| `clippy::pedantic` | Stricter style and API lints |
| `clippy::nursery` | Experimental but valuable lints |
| `cargo-deny` | License compliance, security advisories, duplicate crate versions |
| `cargo-audit` | Known CVEs in dependencies (`RustSec` advisory DB) |
| `cargo-machete` | Unused dependency detection |

## Generated rustfmt.toml

```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
```

## Generated Cargo.toml lints (workspace)

```toml
[workspace.lints.rust]
unsafe_code        = "warn"
unused_must_use    = "warn"
missing_docs       = "warn"

[workspace.lints.clippy]
all     = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
nursery  = { level = "warn", priority = -1 }
# narrow exceptions with justification:
module_name_repetitions = "allow"   # io::IoError acceptable in small crates
missing_errors_doc      = "allow"   # doc-enforced via missing_docs above
missing_panics_doc      = "allow"
```

Member crate `Cargo.toml` inherits with:
```toml
[lints]
workspace = true
```

## Generated deny.toml

```toml
[licenses]
allow = ["MIT", "Apache-2.0", "Apache-2.0 WITH LLVM-exception", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unicode-DFS-2016"]
deny  = ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]

[advisories]
ignore = []   # add advisory IDs here only with a justification comment

[bans]
multiple-versions = "warn"
deny = [
    # { name = "openssl", reason = "use rustls instead" },
]

[sources]
unknown-registry = "deny"
unknown-git      = "deny"
```

## Generated .github/workflows/ci.yml snippet

```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - run: cargo fmt --check
      - run: cargo clippy -- -D warnings
      - run: cargo deny check
      - run: cargo audit
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: taiki-e/install-action@nextest
      - run: cargo nextest run
      - run: cargo test --doc
```

Generate the lint configuration tailored to the project's edition and existing code patterns.
