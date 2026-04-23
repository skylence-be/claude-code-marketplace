# Goroutine Lifecycle

## The Ownership Rule

Every goroutine must have an owner. The owner is responsible for:
1. Knowing when the goroutine exits
2. Waiting for it to exit before the owner itself exits
3. Propagating errors from it

A goroutine without an exit path is a **goroutine leak** — it runs forever and is undetectable.

## `errgroup` — The Preferred Pattern for Fan-Out

`golang.org/x/sync/errgroup` handles fan-out, error collection, and context cancellation atomically:

```go
import "golang.org/x/sync/errgroup"

func processBatch(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)  // g cancels ctx when any goroutine errors

    for _, item := range items {
        item := item  // pre-Go 1.22: capture loop variable
        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    return g.Wait()  // waits for all goroutines; returns first non-nil error
}
```

Key properties:
- `g.Wait()` returns the first non-nil error from any goroutine
- `ctx` is cancelled when any `g.Go` goroutine returns an error
- All other goroutines should check `ctx.Done()` and exit cleanly

## Bounded Concurrency with `errgroup`

Limit the number of concurrent goroutines:

```go
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)  // at most 10 goroutines running at once

for _, item := range items {
    item := item
    g.Go(func() error {
        return processItem(ctx, item)
    })
}
return g.Wait()
```

## `sync.WaitGroup` — When You Don't Need Errors

```go
var wg sync.WaitGroup

for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)
}

wg.Wait()
```

Rules:
- Call `wg.Add(1)` before starting the goroutine (not inside it)
- Always `defer wg.Done()` as the first statement inside the goroutine

## Graceful Shutdown

Services need to stop goroutines cleanly on shutdown:

```go
type Server struct {
    done chan struct{}
    wg   sync.WaitGroup
}

func (s *Server) Start() {
    s.wg.Add(1)
    go func() {
        defer s.wg.Done()
        for {
            select {
            case <-s.done:
                return
            default:
                s.tick()
            }
        }
    }()
}

func (s *Server) Stop() {
    close(s.done)
    s.wg.Wait()
}
```

Or with context:

```go
func (s *Server) Run(ctx context.Context) error {
    g, ctx := errgroup.WithContext(ctx)

    g.Go(func() error { return s.runWorker(ctx) })
    g.Go(func() error { return s.runMetrics(ctx) })

    return g.Wait()
}
```

## Worker Pool

Fixed-size pool of goroutines processing a shared channel of work:

```go
func workerPool(ctx context.Context, jobs <-chan Job, n int) error {
    g, ctx := errgroup.WithContext(ctx)

    for i := 0; i < n; i++ {
        g.Go(func() error {
            for {
                select {
                case job, ok := <-jobs:
                    if !ok {
                        return nil  // channel closed; worker exits
                    }
                    if err := process(ctx, job); err != nil {
                        return err
                    }
                case <-ctx.Done():
                    return ctx.Err()
                }
            }
        })
    }

    return g.Wait()
}
```

## Common Goroutine Leak Patterns

```go
// Leak 1: goroutine blocks on channel send forever
go func() {
    result := compute()
    ch <- result  // nobody receives — goroutine leaks
}()

// Fix: use a buffered channel, or ensure receiver always runs
ch := make(chan Result, 1)

// Leak 2: goroutine in a loop with no exit condition
go func() {
    for {
        poll()        // loops forever; nothing to stop it
        time.Sleep(1) // sleep doesn't help
    }
}()

// Fix: check ctx.Done()
go func() {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            poll()
        }
        time.Sleep(time.Second)
    }
}()
```

## Detecting Leaks in Tests

Use `go.uber.org/goleak` to fail tests when goroutines are leaked:

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}

// Or per-test:
func TestWorker(t *testing.T) {
    defer goleak.VerifyNone(t)
    // ...
}
```
