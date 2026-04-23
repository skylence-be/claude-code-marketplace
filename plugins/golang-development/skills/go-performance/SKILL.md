---
name: go-performance
description: Go performance patterns covering allocation reduction, sync.Pool, escape analysis, slice pre-allocation, strconv vs fmt, and benchmark-driven optimization. Use when optimizing hot paths, reducing GC pressure, writing benchmarks, or profiling with pprof.
---

# Go Performance

## When to Use This Skill

- Profiling a Go service and identifying hot paths
- Reducing allocations in request handlers or tight loops
- Deciding between `fmt.Sprintf` and `strconv` for primitive formatting
- Implementing `sync.Pool` for reusable scratch buffers
- Writing benchmark tests to measure and protect performance
- Understanding escape analysis to minimize heap allocations

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [allocations.md](allocations.md) | Escape analysis, slice pre-allocation, strconv, strings.Builder |
| [benchmarks.md](benchmarks.md) | Writing b.N loops, benchmem, pprof profiling workflow |

## Core Concepts

| Concept | Rule |
|---------|------|
| **Measure first** | Never optimize without benchmark evidence; profile before guessing |
| **Pre-allocate slices** | `make([]T, 0, n)` when size is known; avoids repeated re-allocation |
| **Pre-allocate maps** | `make(map[K]V, n)` when count is known |
| **`strconv` over `fmt`** | `strconv.Itoa` is ~2x faster than `fmt.Sprintf("%d", n)` for primitives |
| **`strings.Builder`** | For string concatenation in loops; avoids O(n²) allocations |
| **`sync.Pool`** | Reuse temporary objects (buffers, scratch structs) to reduce GC pressure |
| **Escape analysis** | Use `go build -gcflags="-m"` to see what escapes to the heap |

## Quick Reference

```go
// Pre-allocate when size is known
results := make([]string, 0, len(input))

// strconv for primitives — faster than fmt
s := strconv.Itoa(n)              // not fmt.Sprintf("%d", n)
s := strconv.FormatFloat(f, 'f', 2, 64)

// strings.Builder for loop concatenation
var b strings.Builder
for _, word := range words {
    b.WriteString(word)
    b.WriteByte(' ')
}
result := b.String()

// sync.Pool for reusable scratch buffers
var bufPool = sync.Pool{
    New: func() any { return new(bytes.Buffer) },
}

func handler(w http.ResponseWriter, r *http.Request) {
    buf := bufPool.Get().(*bytes.Buffer)
    buf.Reset()
    defer bufPool.Put(buf)
    // use buf
}

// Benchmark
func BenchmarkProcess(b *testing.B) {
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

## Best Practices

1. **Profile first with pprof** — `go test -bench=. -benchmem -cpuprofile cpu.prof`, then `go tool pprof`
2. **`b.ReportAllocs()` in every benchmark** — shows allocations/op and bytes/op
3. **Avoid `interface{}` boxing in hot paths** — each boxing allocates; use generics (Go 1.18+) or concrete types
4. **Pass large structs by pointer** — avoids copy on every call; small structs (≤3 fields) are fine by value
5. **Reuse byte slices** — `[]byte` reuse with `sync.Pool` is the highest-ROI optimization in handlers
6. **Avoid unnecessary `string(b)` conversions** — work directly with `[]byte` in hot paths

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `fmt.Sprintf("%d", n)` in a loop | `strconv.Itoa(n)` — significantly faster |
| `s += piece` in a loop | `strings.Builder` — avoids O(n²) |
| Unbounded `sync.Pool` objects | Always call `buf.Reset()` before returning to pool |
| Optimizing before profiling | Profile first; 80% of time is in 20% of code |
| `make([]T, 0)` when size is known | `make([]T, 0, n)` — avoids re-allocation |

## Next Steps

- See [allocations.md](allocations.md) for escape analysis and allocation reduction techniques
- See [benchmarks.md](benchmarks.md) for writing effective benchmarks and using pprof
