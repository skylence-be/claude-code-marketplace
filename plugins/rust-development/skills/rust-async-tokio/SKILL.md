---
name: rust-async-tokio
description: Tokio: spawn_blocking, !Send across .await, lock-across-await, select!. Use when writing async Rust or debugging starvation.
---

# Rust Async with Tokio

## When to Use This Skill

- Writing async functions with Tokio
- Reviewing async code for executor starvation or deadlocks
- Deciding between `spawn_blocking`, `spawn`, and inline async
- Implementing fan-out with `join_all`, `FuturesUnordered`, or channels
- Adding cancellation and timeout to async operations
- Debugging `!Send` compile errors on async functions

## Core Concepts

| Concept | Rule |
|---------|------|
| **One multi-thread runtime** | Start one Tokio runtime in `main`; never nest runtimes |
| **No blocking on the async executor** | `std::fs`, `std::net`, `thread::sleep` starve Tokio; use `spawn_blocking` |
| **`!Send` types across `.await`**  | Types like raw DB connections that are `!Send` cannot be held across `.await`; use `spawn_blocking` |
| **No `std::sync::Mutex` across `.await`** | Holding a `MutexGuard` across an `.await` point deadlocks; restructure or use `tokio::sync::Mutex` |
| **Tokio and Rayon don't mix** | Never call `rayon::join` or `rayon::scope` from an async context; use `spawn_blocking` to bridge |
| **`Arc` for shared services** | Services shared across tasks go in `Arc<ServiceType>`; `Rc<RefCell<T>>` is `!Send` |
| **`async_trait` for object-safe async traits** | Async methods in `dyn Trait` need `#[async_trait::async_trait]` (boxes the future) |

## Quick Reference

```rust
// CPU-bound or blocking I/O: spawn_blocking
let result = tokio::task::spawn_blocking(move || {
    expensive_cpu_work(&data)   // runs on a dedicated blocking pool
}).await?;

// !Send type (e.g. a non-Send DB connection): also spawn_blocking
let db_path = db_path.clone();
let result = tokio::task::spawn_blocking(move || -> Result<_, MyError> {
    let conn = open_connection(&db_path)?;
    conn.query("SELECT 1")
}).await??;   // outer ? unwraps JoinError, inner ? propagates task Result

// Shared service across tasks
pub struct Server {
    pub client: Arc<dyn HttpClient + Send + Sync>,
    pub cache:  Arc<Cache>,
}

// Fan-out with join_all (bounded, known set)
let results = futures::future::join_all(
    items.iter().map(|item| process(item))
).await;

// Fan-out with bounded concurrency (semaphore)
let sem = Arc::new(tokio::sync::Semaphore::new(8));
let handles: Vec<_> = items.iter().map(|item| {
    let sem = sem.clone();
    let item = item.clone();
    tokio::spawn(async move {
        let _permit = sem.acquire().await?;
        process(&item).await
    })
}).collect();

// Timeout on any future
tokio::time::timeout(Duration::from_secs(30), some_future)
    .await
    .map_err(|_| MyError::Timeout)?

// tokio::select! for racing futures
tokio::select! {
    result = do_work() => result?,
    _ = shutdown_signal() => return Ok(()),
}
```

## Holding Locks Across Await

```rust
// WRONG: std::sync::MutexGuard held across .await
async fn bad(state: Arc<Mutex<State>>) {
    let guard = state.lock().unwrap();
    some_async_call().await;   // MutexGuard still held -> deadlock risk
    drop(guard);
}

// RIGHT: drop before awaiting
async fn good_a(state: Arc<Mutex<State>>) {
    let value = {
        let guard = state.lock().unwrap();
        guard.value.clone()   // take what you need, drop guard
    };
    some_async_call_with(value).await;
}

// RIGHT: use tokio::sync::Mutex when guard must span await
async fn good_b(state: Arc<tokio::sync::Mutex<State>>) {
    let mut guard = state.lock().await;
    some_async_call().await;   // tokio Mutex is designed for this
    guard.counter += 1;
}
```

## Best Practices

1. **Profile before adding `spawn_blocking`.** The blocking pool has overhead; only offload genuinely slow work.
2. **Bound concurrency explicitly.** Unbounded `tokio::spawn` in a loop can OOM; use a semaphore or `FuturesUnordered`.
3. **Propagate `context`-style cancellation.** Accept a `CancellationToken` (from `tokio-util`) or `oneshot` receiver in long-running tasks.
4. **Double-`?` is idiomatic on `spawn_blocking`.** `handle.await??` unwraps `JoinError` then the task's `Result`.
5. **Prefer `tokio::sync::mpsc` for streaming.** For bounded producer-consumer patterns, `mpsc::channel(N)` provides backpressure.
6. **Use `#[tokio::test]` for async tests.** Never construct a runtime manually in tests; the macro handles it.
7. **Avoid `block_on` from async code.** Calling `Handle::block_on` or `Runtime::block_on` from an async context panics; use `spawn_blocking` instead.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `std::fs::read` in an async fn | `tokio::fs::read` or `spawn_blocking(|| std::fs::read(...))` |
| `rayon::scope` from async code | Bridge with `spawn_blocking`; Rayon tasks are sync |
| `thread::sleep` in async code | `tokio::time::sleep` |
| Unbounded `tokio::spawn` in a loop | Semaphore or `FuturesUnordered` with bounded concurrency |
| Holding `std::sync::MutexGuard` across `.await` | Drop before awaiting, or switch to `tokio::sync::Mutex` |
| `Rc<RefCell<T>>` in a spawned task | Use `Arc<Mutex<T>>` for shared mutable state across tasks |
| `.unwrap()` inside an async fn | Panics the entire task; return `Result` and use `?` |

## Next Steps

- Review `rust-error-handling` for propagating errors through `spawn_blocking` and async handlers
- Review `rust-trait-design` for object-safe async traits with `async_trait`
