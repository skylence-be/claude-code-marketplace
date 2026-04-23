# Writing Benchmarks

## The Canonical Benchmark

```go
func BenchmarkProcess(b *testing.B) {
    // Setup outside the loop — not counted
    data := generateTestData()

    b.ResetTimer()  // exclude setup time from the benchmark

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

`b.N` is automatically adjusted by the test runner until results are statistically stable.

## `b.ReportAllocs()` — Always Include

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ReportAllocs()  // shows allocs/op and bytes/op
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

Output:
```
BenchmarkProcess-8    1000000    1234 ns/op    512 B/op    3 allocs/op
```

- `ns/op` — nanoseconds per operation
- `B/op` — bytes allocated per operation
- `allocs/op` — number of heap allocations per operation

## Running Benchmarks

```bash
# Run all benchmarks in the package
go test -bench=. ./...

# Run specific benchmark
go test -bench=BenchmarkProcess ./internal/processor

# Run with allocation stats
go test -bench=. -benchmem ./...

# Run for a specific duration
go test -bench=. -benchtime=10s ./...

# Run N times for stability
go test -bench=. -benchtime=5x ./...

# Compare before/after with benchstat
go test -bench=. -benchmem -count=5 ./... > before.txt
# make your change
go test -bench=. -benchmem -count=5 ./... > after.txt
benchstat before.txt after.txt
```

## Sub-benchmarks

```go
func BenchmarkFormat(b *testing.B) {
    cases := []struct {
        name string
        n    int
    }{
        {name: "small", n: 1},
        {name: "medium", n: 1000},
        {name: "large", n: 1000000},
    }

    for _, bc := range cases {
        b.Run(bc.name, func(b *testing.B) {
            b.ReportAllocs()
            for i := 0; i < b.N; i++ {
                _ = strconv.Itoa(bc.n)
            }
        })
    }
}
```

## Preventing Compiler Optimization

The compiler may optimize away a function call if the result is unused. Use a package-level variable to prevent this:

```go
var result int  // package-level sink

func BenchmarkAdd(b *testing.B) {
    var r int
    for i := 0; i < b.N; i++ {
        r = Add(1, 2)
    }
    result = r  // ensure Add() is not eliminated by the compiler
}
```

## CPU and Memory Profiling

```bash
# Generate CPU profile
go test -bench=BenchmarkProcess -cpuprofile=cpu.prof ./...

# Generate memory profile
go test -bench=BenchmarkProcess -memprofile=mem.prof ./...

# Analyze with pprof
go tool pprof cpu.prof

# Common pprof commands:
# top      — top functions by CPU time
# web      — open a flame graph in browser (requires graphviz)
# list Foo — show source-level annotation for function Foo
```

## pprof HTTP Endpoint in Services

For production profiling, expose the pprof endpoint:

```go
import _ "net/http/pprof"  // registers /debug/pprof/ routes

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

```bash
# Profile a running service for 30 seconds
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap profile
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine profile (detect leaks)
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

## `benchstat` — Comparing Benchmarks

```bash
go install golang.org/x/perf/cmd/benchstat@latest

# Run each version 5+ times for statistical stability
go test -bench=. -benchmem -count=5 ./... > before.txt
# make change
go test -bench=. -benchmem -count=5 ./... > after.txt

benchstat before.txt after.txt
```

Output shows whether differences are statistically significant:
```
name         old time/op  new time/op  delta
Process-8    1.23µs ± 2%  0.98µs ± 1%  -20.3%  (p=0.000 n=5+5)
```

## What to Benchmark

- Any function on a critical request path
- Functions that process large inputs
- Functions called millions of times (parsers, serializers, validators)
- After any optimization — measure before and after

What NOT to benchmark:
- Setup/teardown code (exclude with `b.ResetTimer()`)
- Simple functions the compiler will inline anyway
- Code that runs once at startup
