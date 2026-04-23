# Context Usage

## The Contract

`context.Context` carries deadlines, cancellation signals, and request-scoped values across API boundaries. It is always the **first parameter** of any function that does I/O, blocks, or needs to be cancelable.

```go
// Correct
func FetchUser(ctx context.Context, id int) (*User, error)
func (s *Server) handleRequest(ctx context.Context, req *Request) error

// Wrong — context buried, or missing entirely
func FetchUser(id int, ctx context.Context) (*User, error)
func FetchUser(id int) (*User, error)
```

## Never Store Context in a Struct

Context is per-call, not per-object. Storing it breaks cancellation across calls.

```go
// Wrong
type Client struct {
    ctx context.Context  // don't do this
}

// Correct — pass context on each method call
type Client struct {
    baseURL string
}
func (c *Client) Get(ctx context.Context, path string) (*Response, error) { ... }
```

## Creating Derived Contexts

```go
// Cancel: create a cancel function, defer its call
ctx, cancel := context.WithCancel(ctx)
defer cancel()  // always call cancel to release resources

// Timeout: automatically cancels after duration
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

// Deadline: cancels at an absolute time
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(ctx, deadline)
defer cancel()
```

## Checking Cancellation

In long-running loops, check `ctx.Done()`:

```go
func processItems(ctx context.Context, items []Item) error {
    for _, item := range items {
        select {
        case <-ctx.Done():
            return ctx.Err()  // context.Canceled or context.DeadlineExceeded
        default:
        }
        if err := process(ctx, item); err != nil {
            return err
        }
    }
    return nil
}
```

Or use a non-blocking select for lightweight checks:

```go
select {
case <-ctx.Done():
    return ctx.Err()
default:
    // keep going
}
```

## Context Values

Use `ctx.Value` sparingly — only for cross-cutting concerns that would pollute every function signature (request ID, trace ID, auth token). Never use it to pass business logic parameters.

```go
// Define an unexported key type to avoid collisions
type contextKey int
const requestIDKey contextKey = iota

// Set
ctx = context.WithValue(ctx, requestIDKey, requestID)

// Get — always assert with comma-ok and provide a fallback
id, ok := ctx.Value(requestIDKey).(string)
if !ok {
    id = "unknown"
}
```

## `context.Background()` and `context.TODO()`

- `context.Background()` — the root context; use in `main`, server initialization, and test setup
- `context.TODO()` — placeholder when you know a context should be threaded but haven't yet; treat as technical debt

## Propagating Context in HTTP Handlers

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()  // carries client's timeout / cancellation

    user, err := s.store.GetUser(ctx, idFromPath(r))
    if err != nil {
        if errors.Is(err, context.Canceled) {
            return  // client disconnected; no response needed
        }
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    // ...
}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `context.Background()` inside a handler | Use `r.Context()` to propagate client cancellation |
| Storing context in a struct field | Pass context on each method call |
| Ignoring `ctx.Err()` after `ctx.Done()` | Return `ctx.Err()` to propagate the reason (Canceled vs DeadlineExceeded) |
| Using `interface{}` keys for context values | Use unexported typed keys to prevent collisions |
| Never calling `cancel()` | Always `defer cancel()` immediately after `WithTimeout` / `WithCancel` |
