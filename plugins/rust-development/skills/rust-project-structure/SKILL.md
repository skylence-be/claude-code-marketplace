---
name: rust-project-structure
description: Rust project structure covering src/lib.rs vs src/main.rs, examples/, benches/, tests/, Cargo workspace layout with shared [workspace.dependencies] and [workspace.lints], feature flag hygiene, and Cargo.toml best practices. Use when scaffolding a new crate, setting up a multi-crate workspace, or publishing a library.
---

# Rust Project Structure

## When to Use This Skill

- Scaffolding a new Rust binary, library, or workspace
- Deciding between a single crate and a multi-crate workspace
- Setting up shared dependencies and lints across a workspace
- Publishing a library to crates.io with a stable API
- Organizing feature flags without combinatorial explosion

## Core Concepts

| Concept | Rule |
|---------|------|
| **`src/lib.rs` for libraries** | Public API lives here; `main.rs` (thin) wires up the library if both are needed |
| **`src/main.rs` for binaries** | `main` only wires and calls into `src/lib.rs` or `internal/`; no business logic in `main` |
| **Workspace for multi-crate** | `crates/<name>/` per crate; root `Cargo.toml` holds `[workspace]`, shared deps, and lints |
| **`[workspace.dependencies]`** | Declare dependency versions once in the root; member crates inherit with `dep = { workspace = true }` |
| **`[workspace.lints]`** | Lint config in root; member crates inherit with `lints.workspace = true` |
| **`[lints]` not `[features]` for CI** | Don't use features to enable stricter lints; use `[workspace.lints]` so CI and local dev share the same configuration |
| **Feature flag hygiene** | Avoid `default = ["everything"]`; each feature should be genuinely optional |

## Quick Reference

```
# Single binary crate
my-tool/
├── src/
│   ├── main.rs           # thin: parse args, call lib
│   ├── lib.rs            # public API (optional but recommended)
│   ├── config.rs         # module
│   └── handler.rs        # module
├── tests/
│   └── integration.rs    # integration tests
├── examples/
│   └── basic.rs          # runnable examples (cargo run --example basic)
├── benches/
│   └── throughput.rs     # criterion benchmarks
├── Cargo.toml
├── Cargo.lock            # commit for binaries, .gitignore for libraries
├── rustfmt.toml
└── .clippy.toml

# Multi-crate workspace
my-project/
├── Cargo.toml            # [workspace] root only
├── crates/
│   ├── my-core/          # pure library: no I/O, no async
│   │   └── src/lib.rs
│   ├── my-cli/           # binary: thin wrapper around my-core
│   │   └── src/main.rs
│   └── my-server/        # binary: axum/tokio service
│       └── src/main.rs
└── Cargo.lock
```

## Workspace Root Cargo.toml

```toml
[workspace]
members = ["crates/*"]
resolver = "2"

[workspace.package]
version = "0.1.0"
edition = "2024"
authors  = ["Your Name <you@example.com>"]
license  = "MIT OR Apache-2.0"
repository = "https://github.com/org/repo"

[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
thiserror = "2"
anyhow = "1"

[workspace.lints.rust]
unsafe_code = "warn"
unused_must_use = "warn"

[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
# narrow exceptions with justification:
module_name_repetitions = "allow"   # io::IoError is fine in small crates
```

## Member Crate Cargo.toml

```toml
[package]
name    = "my-core"
version.workspace = true
edition.workspace = true

[lints]
workspace = true   # inherit all workspace lints

[dependencies]
thiserror = { workspace = true }
serde = { workspace = true }
```

## Best Practices

1. **Commit `Cargo.lock` for binaries, add to `.gitignore` for libraries.** Lockfile gives binaries reproducible builds; libraries should test against the latest compatible versions.
2. **`resolver = "2"` in workspace root.** The version 2 resolver handles feature unification correctly for large workspaces.
3. **One crate per responsibility.** `my-core` (pure logic), `my-cli` (user interface), `my-server` (HTTP layer) are naturally separate; merging them creates circular dependency pressure.
4. **Put integration tests in `tests/`.** They run as a separate binary and can only access your public API, which is the correct test surface.
5. **`examples/` for demonstration.** Examples are compiled and checked by `cargo test --examples`; they serve as living documentation.
6. **Feature flags: additive only.** Features should add optional capabilities; never use them to remove items from the default API.
7. **Run `cargo deny check` in CI.** Catches license violations, banned crates, and duplicate dependency versions.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| Business logic in `main.rs` | Move to `lib.rs` or a named module; `main` wires and exits |
| One giant crate | Split into focused crates in a workspace; enables incremental compilation |
| `default-features = false` everywhere | Fine for libraries; binaries should usually enable the features they need explicitly |
| `[patch.crates-io]` in published crates | Only use `[patch]` locally; strip before publishing to crates.io |
| Duplicate dependency versions | Use `[workspace.dependencies]` so all crates pull the same version |
| `Cargo.lock` absent for a deployed binary | Commit the lockfile; it pins exact versions for reproducible deployments |

## Next Steps

- Review `rust-coding-standards` for workspace lints and naming conventions
- Review `rust-testing-patterns` for integration test layout and `tests/common/mod.rs` helpers
