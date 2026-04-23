---
name: go-concurrency-patterns
description: Idiomatic Go concurrency patterns covering context propagation, goroutine lifecycle management, errgroup, channels, sync primitives, and worker pools. Use when implementing concurrent programs, reviewing for goroutine leaks, designing concurrent APIs, or debugging deadlocks and race conditions.
---

# Go Concurrency Patterns

## When to Use This Skill

- Implementing concurrent processing (fan-out, pipelines, worker pools)
- Reviewing code for goroutine leaks or missing cancellation
- Designing an API that spawns goroutines (deciding whether to expose channels or callbacks)
- Debugging deadlocks or data races detected by `go test -race`
- Adding graceful shutdown to a service

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [context-usage.md](context-usage.md) | Context propagation, cancellation, timeout, value keys |
| [goroutine-lifecycle.md](goroutine-lifecycle.md) | Ownership, WaitGroup, errgroup, goroutine leak prevention |
| [channels-sync.md](channels-sync.md) | Channel direction, buffering, pipelines, sync primitives |

## Core Concepts

| Concept | Rule |
|---------|------|
| **Context first** | `context.Context` is always the first parameter |
| **Goroutine ownership** | Every goroutine has an owner responsible for knowing when it exits |
| **Don't store context** | Never store `context.Context` in a struct field |
| **Sender closes channel** | The goroutine that sends on a channel is responsible for closing it |
| **`errgroup` for fan-out** | Prefer `golang.org/x/sync/errgroup` over manual WaitGroup + error channel |
| **Channel direction** | Always specify direction in function signatures: `<-chan T`, `chan<- T` |
| **`sync.Mutex` is not copyable** | Never copy a struct containing a mutex; use a pointer receiver |

## Quick Reference

```go
// Context always first
func ProcessBatch(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, item := range items {
        item := item  // pre-Go 1.22: capture loop variable
        g.Go(func() error {
            return process(ctx, item)
        })
    }

    return g.Wait()
}

// Channel with explicit direction
func generate(done <-chan struct{}, values ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, v := range values {
            select {
            case out <- v:
            case <-done:
                return
            }
        }
    }()
    return out
}
```

## Best Practices

1. **Always propagate context** — pass `ctx` to every function that does I/O or blocks
2. **Use `errgroup`** for fan-out that needs error collection and automatic context cancellation
3. **Specify channel direction** in all function signatures — `<-chan T` for receive-only
4. **Buffered channels only when deliberate** — size of 1 is usually enough; document the reasoning
5. **Prefer synchronous functions** — callers can add goroutines; removing them is hard
6. **Test with `-race`** — all concurrent code must pass `go test -race` in CI
7. **Check `ctx.Done()` in loops** — any long-running loop must select on context cancellation

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| Fire-and-forget goroutine | Track with WaitGroup or errgroup; every goroutine must have an exit path |
| `time.Sleep` for synchronization | Use channels or `sync.WaitGroup`; sleep is racey |
| Spawning goroutines in `init()` | Move to explicit lifecycle management (Start/Stop methods) |
| Copying `sync.Mutex` | Use pointer receiver or embed as `*sync.Mutex` |
| Closing a channel from the receiver | Only the sender closes; use `done` channel to signal stop |
| Storing context in struct field | Pass context as parameter on each call |

## Next Steps

- See [context-usage.md](context-usage.md) for context propagation, timeouts, and value keys
- See [goroutine-lifecycle.md](goroutine-lifecycle.md) for ownership, errgroup, and graceful shutdown
- See [channels-sync.md](channels-sync.md) for channel patterns, pipelines, and sync primitives
