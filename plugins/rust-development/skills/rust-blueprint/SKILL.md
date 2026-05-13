---
name: rust-blueprint
description: Structured planning format for Rust crates and workspaces. Bridges requirements to production-ready code by specifying every decision before writing. Use when planning new Rust projects, designing crate APIs, specifying async service architecture, or generating code from requirements. Blueprint ensures vague plans don't lead to vague code.
---

# Rust Blueprint

Rust Blueprint is a structured planning format that helps AI agents create detailed, accurate implementation plans for Rust projects. It specifies every decision (edition, toolchain, crate layout, error strategy, async runtime, dependencies, public API) before a single line is written.

## When to Use This Skill

- Planning a new Rust crate or multi-crate workspace from scratch
- Creating detailed specifications before writing code
- Generating a project architecture with explicit crate boundaries
- Documenting public API surface and error contracts upfront
- Ensuring toolchain, edition, and dependency choices are locked before coding starts
- Avoiding vague plans that lead to inconsistent or non-idiomatic code

## Blueprint Plan Structure

A complete Blueprint has these numbered sections:

### 1. Overview and Key Decisions

```markdown
# Payment Webhook Processor

An async service that receives, validates, and persists Stripe webhook events.

## Key Decisions
- Rust 1.85+ / Edition 2024
- Async runtime: Tokio multi-thread
- HTTP server: axum 0.8
- Database: sqlx 0.8 with PostgreSQL, compile-time verified queries
- Error strategy: thiserror in lib crates, anyhow in binary entry point
- Serialization: serde + serde_json
- Workspace: crates/webhook-core (lib), crates/webhook-server (bin)
- Lints: clippy all + pedantic via [workspace.lints]
- Testing: cargo-nextest, insta for snapshot tests, testcontainers for Postgres
```

### 2. Crate Layout

```markdown
## Crate Layout

webhook-processor/
├── Cargo.toml            # workspace root
├── crates/
│   ├── webhook-core/     # pure library: validation, domain types, DB queries
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── event.rs       # Event, EventKind enums
│   │       ├── validation.rs  # signature verification
│   │       └── db.rs          # sqlx queries
│   └── webhook-server/   # binary: axum routes, middleware, startup
│       └── src/
│           ├── main.rs        # thin: build router, bind, serve
│           ├── routes.rs      # axum handler functions
│           └── middleware.rs  # auth, logging
```

### 3. Public API Design

```markdown
## Public API (webhook-core)

### Types
- `Event` -- parsed, validated webhook event
- `EventKind` -- enum: PaymentSucceeded | PaymentFailed | RefundCreated
- `WebhookError` -- thiserror enum: SignatureInvalid | UnknownEvent | DbError

### Functions
- `fn verify_signature(payload: &[u8], sig: &str, secret: &str) -> Result<(), WebhookError>`
- `async fn persist(event: &Event, pool: &PgPool) -> Result<(), WebhookError>`
- `fn parse_event(body: &[u8]) -> Result<Event, WebhookError>`
```

### 4. Error Strategy

```markdown
## Error Strategy

- `webhook-core`: typed errors with thiserror
  ```rust
  #[derive(Debug, thiserror::Error)]
  pub enum WebhookError {
      #[error("invalid signature")]
      SignatureInvalid,
      #[error("unknown event type: {kind}")]
      UnknownEvent { kind: String },
      #[error("database error")]
      Db(#[from] sqlx::Error),
  }
  ```
- `webhook-server/main.rs`: anyhow for startup errors
- HTTP handlers return `Result<Response, StatusCode>` and map WebhookError to status codes
```

### 5. Async and Concurrency Model

```markdown
## Async Model

- Single Tokio multi-thread runtime in main.rs
- All handlers are async; no blocking I/O on the executor
- `sqlx::PgPool` shared via axum State (Arc-wrapped internally by sqlx)
- No Rayon; CPU-bound signature verification is fast enough inline
- Graceful shutdown via tokio::signal::ctrl_c
```

### 6. Dependencies

```markdown
## Dependencies

[workspace.dependencies]
tokio       = { version = "1",   features = ["full"] }
axum        = "0.8"
sqlx        = { version = "0.8", features = ["postgres", "runtime-tokio", "macros"] }
serde       = { version = "1",   features = ["derive"] }
serde_json  = "1"
thiserror   = "2"
anyhow      = "1"
tracing     = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

[dev-dependencies]
insta            = "1"
testcontainers   = "0.23"
cargo-nextest    # (install separately)
```

### 7. Testing Plan

```markdown
## Testing Plan

- Unit tests inline in webhook-core (validation, parsing logic)
- Integration tests in crates/webhook-core/tests/ using testcontainers-postgres
- Snapshot tests with insta for serialized Event JSON output
- HTTP integration tests in crates/webhook-server/tests/ spinning up the full axum app
- cargo-nextest for all test runs; CI runs `cargo nextest run`
- No std::env::set_var in tests (edition 2024); inject config via function parameters
```

### 8. File Map

```markdown
## File Map (files to create, in order)

1. Cargo.toml (workspace root)
2. crates/webhook-core/Cargo.toml
3. crates/webhook-core/src/lib.rs
4. crates/webhook-core/src/event.rs
5. crates/webhook-core/src/validation.rs
6. crates/webhook-core/src/db.rs
7. crates/webhook-server/Cargo.toml
8. crates/webhook-server/src/main.rs
9. crates/webhook-server/src/routes.rs
10. crates/webhook-server/src/middleware.rs
11. rustfmt.toml (workspace root)
```

## Blueprint Rules

1. **Lock the edition.** Always specify `edition = "2024"` (or the target edition) in Key Decisions. Edition affects `std::env::set_var`, match ergonomics, and other behavior.
2. **Name all public types upfront.** Changing a public type name after writing code cascades through tests and serialization fixtures.
3. **Specify the error strategy per crate.** The library/binary split for thiserror/anyhow must be decided before coding; retrofitting is expensive.
4. **List dependencies with versions.** Vague "use serde" instructions lead to version mismatches; pin major versions in the blueprint.
5. **File Map last.** Writing the file list forces you to think through what needs to exist before you start; it also serves as a checklist during implementation.

## Common Blueprint Mistakes

| Mistake | Fix |
|---------|-----|
| "Use async" without naming the runtime | Specify `tokio multi-thread` or `tokio current-thread` explicitly |
| "Handle errors" without specifying the type | Write the `thiserror` enum variants in section 4 before coding |
| No crate boundary decision | Decide library vs binary before writing any code; mixing concerns makes testing harder |
| Missing feature flags on dependencies | `tokio = "1"` without `features = ["full"]` won't compile for most async code |
| No testing plan | Specify which tests are unit, integration, and snapshot; otherwise tests get written inconsistently |
