# Channels and Sync Primitives

## Channel Direction in Signatures

Always specify channel direction in function parameters. This documents intent and lets the compiler enforce it:

```go
// Receive-only: function can only receive from ch
func consume(ch <-chan int) { ... }

// Send-only: function can only send to ch
func produce(ch chan<- int) { ... }

// Bidirectional: use only inside the owning function — don't pass bidirectional channels around
ch := make(chan int)
go produce(ch)   // implicitly narrows to chan<- int
go consume(ch)   // implicitly narrows to <-chan int
```

## Buffered vs Unbuffered

**Unbuffered channels** (default): synchronous handoff — sender blocks until receiver is ready.

```go
ch := make(chan int)   // unbuffered
```

**Buffered channels**: sender only blocks when the buffer is full.

```go
ch := make(chan int, 1)   // buffer of 1 — sender doesn't wait if receiver is slow
```

Use buffered channels only when you've thought through what happens when the buffer is full. Size 1 is usually enough to decouple sender from receiver slightly. Document why you chose the size.

## The `done` Channel Pattern (Stop Signal)

A closed `done` channel signals all receivers simultaneously:

```go
func worker(done <-chan struct{}) {
    for {
        select {
        case <-done:
            return
        default:
            doWork()
        }
    }
}

done := make(chan struct{})
go worker(done)
// ...
close(done)  // signals ALL workers simultaneously
```

Never close a channel from a receiver — only the sender closes.

## Pipeline Pattern

Each stage receives from an upstream channel and sends to a downstream channel:

```go
// Stage 1: generate values
func generate(done <-chan struct{}, nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            select {
            case out <- n:
            case <-done:
                return
            }
        }
    }()
    return out
}

// Stage 2: square values
func square(done <-chan struct{}, in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            select {
            case out <- n * n:
            case <-done:
                return
            }
        }
    }()
    return out
}

// Wire the pipeline
done := make(chan struct{})
defer close(done)
for n := range square(done, generate(done, 1, 2, 3, 4)) {
    fmt.Println(n)
}
```

## `sync.Mutex` and `sync.RWMutex`

- Zero value is usable — no initialization needed
- Never copy — always use a pointer receiver or embed in a struct passed by pointer
- `RWMutex` for read-heavy workloads: multiple concurrent readers, exclusive writer

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

// RWMutex for read-heavy map
type Cache struct {
    mu    sync.RWMutex
    items map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    v, ok := c.items[key]
    return v, ok
}

func (c *Cache) Set(key, val string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = val
}
```

## `sync.Once` — One-Time Initialization

```go
var (
    instance *DB
    once     sync.Once
)

func GetDB() *DB {
    once.Do(func() {
        instance = openDB()
    })
    return instance
}
```

## `sync.Map` — When to Use It

Use `sync.Map` only for specific patterns:
- Write-once, read-many: config, routes
- Cache with many goroutines reading different keys

Don't use it as a general replacement for `map + sync.Mutex` — the API is less ergonomic and performance isn't always better.

```go
var m sync.Map

m.Store("key", "value")

if v, ok := m.Load("key"); ok {
    fmt.Println(v.(string))
}

m.LoadOrStore("key", "default")  // atomic check-and-set
```

## `select` with Timeout

```go
select {
case result := <-ch:
    // got result
case <-time.After(5 * time.Second):
    // timed out — note: time.After leaks until it fires; use time.NewTimer for long-lived loops
case <-ctx.Done():
    // context cancelled
}
```

For long-lived loops, prefer `time.NewTimer` to avoid timer leaks:

```go
timer := time.NewTimer(5 * time.Second)
defer timer.Stop()

select {
case result := <-ch:
case <-timer.C:
}
```
