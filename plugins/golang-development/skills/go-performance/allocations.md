# Reducing Allocations

## Why Allocations Matter

Every allocation puts pressure on the garbage collector. In high-throughput services, reducing allocations in hot paths can eliminate GC pauses and improve latency percentiles (p99, p999).

Profile first — `go test -bench=. -benchmem` shows allocations per operation. Only optimize what the profiler points to.

## Slice Pre-allocation

```go
// Bad — grows the backing array multiple times (O(log n) allocations)
var results []string
for _, item := range input {
    results = append(results, transform(item))
}

// Good — allocate exactly what we need upfront (1 allocation)
results := make([]string, 0, len(input))
for _, item := range input {
    results = append(results, transform(item))
}
```

Also pre-allocate maps:

```go
// Allocates incrementally as entries are added
m := make(map[string]int)

// Allocates ~n buckets upfront
m := make(map[string]int, len(keys))
```

## `strconv` Over `fmt` for Primitives

`fmt.Sprintf` uses reflection and allocates. `strconv` is direct and ~2x faster:

```go
// Slower — allocates due to reflection
s := fmt.Sprintf("%d", n)
s := fmt.Sprintf("%f", f)

// Faster
s := strconv.Itoa(n)                         // int → string
s := strconv.FormatInt(n, 10)                // int64 → string
s := strconv.FormatFloat(f, 'f', 2, 64)     // float64 → string
s := strconv.FormatBool(b)                   // bool → string

n, _ := strconv.Atoi(s)                      // string → int
n, _ := strconv.ParseInt(s, 10, 64)         // string → int64
f, _ := strconv.ParseFloat(s, 64)           // string → float64
```

## `strings.Builder` for String Concatenation

`+` concatenation in a loop creates a new string each iteration (O(n²) allocations):

```go
// Bad — O(n²) allocations
var result string
for _, word := range words {
    result += word + " "
}

// Good — one allocation for the final string
var b strings.Builder
b.Grow(estimatedLen)  // optional but helpful if you know the size
for _, word := range words {
    b.WriteString(word)
    b.WriteByte(' ')
}
result := b.String()
```

## Avoiding Unnecessary Conversions

Conversions between `string` and `[]byte` always allocate:

```go
// Bad in a hot path — allocates a new []byte every call
data := []byte(str)

// Good — work with []byte throughout if the data comes as bytes
func process(data []byte) { ... }
```

Use `strings.Contains`, `strings.HasPrefix`, etc. when working with strings to avoid converting to bytes.

## Escape Analysis

The Go compiler's escape analysis decides whether a variable is allocated on the stack (cheap) or the heap (GC pressure). Use `go build -gcflags="-m"` to see what escapes:

```bash
go build -gcflags="-m" ./...
```

Common reasons values escape to the heap:
- Passed to a function that takes `interface{}`
- Address taken and returned from a function
- Too large for the stack
- Closed over by a goroutine

Minimize escapes in hot paths by:
- Using value types instead of pointers for small structs
- Avoiding `interface{}` in tight loops
- Pre-allocating buffers rather than creating them inside functions

## Reusing Byte Slices

For temporary buffers that follow the pattern "create, fill, use, discard":

```go
// Bad — allocates a new buffer on every request
func handler(w http.ResponseWriter, r *http.Request) {
    buf := make([]byte, 32*1024)
    // ... use buf
}

// Good — reuse buffers across requests with sync.Pool
var bufPool = sync.Pool{
    New: func() any {
        b := make([]byte, 32*1024)
        return &b
    },
}

func handler(w http.ResponseWriter, r *http.Request) {
    bp := bufPool.Get().(*[]byte)
    buf := *bp
    defer bufPool.Put(bp)
    // ... use buf
}
```

## Filter Without Allocation

Filtering a slice in place avoids a new allocation:

```go
// Bad — allocates a new slice
filtered := make([]Item, 0)
for _, item := range items {
    if keep(item) {
        filtered = append(filtered, item)
    }
}

// Good — reuse the backing array
filtered := items[:0]
for _, item := range items {
    if keep(item) {
        filtered = append(filtered, item)
    }
}
// Note: original items are modified! Only use if you don't need the original.
```

## Zero-Value Structs as Signals

For channel signals, use `struct{}` — it has zero size:

```go
done := make(chan struct{})
close(done)  // signal completion with zero allocation
```
