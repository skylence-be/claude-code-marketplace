---
description: Scaffold a new multi-crate Cargo workspace with shared [workspace.dependencies], [workspace.lints], a core library crate, and a CLI or server binary crate
---

# New Rust Workspace

Scaffold a multi-crate Cargo workspace following Cargo conventions with shared dependency versions, workspace-level lints, and a clean crate boundary between library logic and binary entry points.

## Specification

$ARGUMENTS

## Process

1. **Determine the workspace name and type** from the specification (e.g., `my-project --type=cli` or `my-service --type=server`)
2. **Create the workspace root** with a `Cargo.toml` containing `[workspace]`, `[workspace.package]`, `[workspace.dependencies]`, and `[workspace.lints]`
3. **Create `crates/<name>-core`** as a pure library: no I/O dependencies, no async runtime (or minimal), all domain logic
4. **Create `crates/<name>-cli`** (CLI type) or `crates/<name>-server`** (server type) as the binary crate wiring up the core
5. **Write `rustfmt.toml`** and `deny.toml` at the workspace root
6. **Add `.gitignore`** with Rust-specific patterns and commit `Cargo.lock`

## Examples

### CLI workspace

```bash
# Arguments: my-tool --type=cli
mkdir my-tool && cd my-tool
cargo new --lib crates/my-tool-core
cargo new crates/my-tool-cli
```

Resulting structure:
```
my-tool/
├── Cargo.toml              # workspace root only
├── Cargo.lock
├── rustfmt.toml
├── deny.toml
├── .gitignore
└── crates/
    ├── my-tool-core/       # pure library: domain logic, error types
    │   ├── Cargo.toml
    │   └── src/
    │       └── lib.rs
    └── my-tool-cli/        # binary: arg parsing, output formatting
        ├── Cargo.toml
        └── src/
            └── main.rs
```

### HTTP service workspace

```bash
# Arguments: my-service --type=server
mkdir my-service && cd my-service
cargo new --lib crates/my-service-core
cargo new crates/my-service-server
```

Resulting structure:
```
my-service/
├── Cargo.toml
├── Cargo.lock
├── rustfmt.toml
├── deny.toml
└── crates/
    ├── my-service-core/    # pure library: domain types, DB queries, business logic
    │   ├── Cargo.toml
    │   └── src/lib.rs
    └── my-service-server/  # binary: axum routes, middleware, startup
        ├── Cargo.toml
        └── src/main.rs
```

### Workspace root Cargo.toml

```toml
[workspace]
members  = ["crates/*"]
resolver = "2"

[workspace.package]
version    = "0.1.0"
edition    = "2024"
license    = "MIT OR Apache-2.0"
repository = "https://github.com/org/my-project"

[workspace.dependencies]
# async
tokio     = { version = "1", features = ["full"] }
# serialization
serde     = { version = "1", features = ["derive"] }
serde_json = "1"
# errors
thiserror = "2"
anyhow    = "1"
# observability
tracing   = "0.1"

[workspace.lints.rust]
unsafe_code     = "warn"
unused_must_use = "warn"

[workspace.lints.clippy]
all      = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
nursery  = { level = "warn", priority = -1 }
module_name_repetitions = "allow"
```

### Core library Cargo.toml

```toml
[package]
name    = "my-tool-core"
version.workspace = true
edition.workspace = true

[lints]
workspace = true

[dependencies]
thiserror = { workspace = true }
serde     = { workspace = true }
```

### Binary Cargo.toml

```toml
[package]
name    = "my-tool-cli"
version.workspace = true
edition.workspace = true

[lints]
workspace = true

[dependencies]
my-tool-core = { path = "../my-tool-core" }
anyhow       = { workspace = true }
clap         = { version = "4", features = ["derive"] }
```

Scaffold the workspace following Cargo conventions, clean crate boundaries (pure logic in core, I/O in binary), and idiomatic edition 2024 setup.
