---
description: Scaffold a new idiomatic Rust project with edition 2024, workspace lints, Makefile, rustfmt.toml, clippy.toml, and a .gitignore
---

# New Rust Project

Scaffold a new idiomatic Rust project following Cargo conventions with module setup, edition 2024, linting configuration, and a working Makefile.

## Specification

$ARGUMENTS

## Process

1. **Determine the crate name and type** from the specification (e.g., `my-tool --bin` or `my-lib --lib`)
2. **Create the project** with `cargo new <name>` (binary) or `cargo new --lib <name>` (library)
3. **Set edition 2024** in `Cargo.toml` and add `[lints]` table inheriting from workspace, or configure directly if not in a workspace
4. **Write the thin `src/main.rs`** (binary) that wires up `src/lib.rs`, or a starter `src/lib.rs` with doc comments (library)
5. **Create `rustfmt.toml`** with recommended formatting options
6. **Create `clippy.toml`** or workspace lints with `clippy::all`, `pedantic`, and `nursery` warnings
7. **Write `Makefile`** with `build`, `test`, `lint`, `fmt`, `check`, and `clean` targets
8. **Add `.gitignore`** with Rust-specific patterns

## Examples

### Binary CLI application

```bash
# Arguments: my-tool
cargo new my-tool
cd my-tool
```

Resulting structure:
```
my-tool/
├── src/
│   ├── main.rs          # thin: parse args, call lib
│   └── lib.rs           # business logic
├── tests/
│   └── integration.rs   # optional starter
├── rustfmt.toml
├── clippy.toml
├── Makefile
├── .gitignore
└── Cargo.toml           # edition = "2024", [lints] table
```

### Library crate

```bash
# Arguments: my-lib --lib
cargo new --lib my-lib
```

Resulting structure:
```
my-lib/
├── src/
│   └── lib.rs           # public API with doc comments
├── tests/
│   └── integration.rs   # public API integration tests
├── rustfmt.toml
├── clippy.toml
├── Makefile
├── .gitignore
└── Cargo.toml           # edition = "2024", [lints] table
```

### Generated Cargo.toml

```toml
[package]
name    = "my-tool"
version = "0.1.0"
edition = "2024"

[lints.rust]
unsafe_code = "warn"
unused_must_use = "warn"

[lints.clippy]
all      = "warn"
pedantic = "warn"
nursery  = "warn"
module_name_repetitions = "allow"
```

### Generated Makefile targets

```makefile
.PHONY: build test lint fmt check clean

build:
    cargo build --release

test:
    cargo nextest run

lint:
    cargo clippy -- -D warnings

fmt:
    cargo fmt --check

check:
    cargo check && cargo fmt --check && cargo clippy -- -D warnings

clean:
    cargo clean
```

Scaffold the project following Cargo conventions, edition 2024 idioms, and idiomatic error handling from the start.
