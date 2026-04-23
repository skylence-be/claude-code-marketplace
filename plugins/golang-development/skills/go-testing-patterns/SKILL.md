---
name: go-testing-patterns
description: Idiomatic Go testing patterns including table-driven tests, t.Run subtests, t.Parallel, t.Helper, mocking with interfaces, and integration tests with testcontainers. Use when writing Go tests, reviewing test quality, setting up CI test pipelines, or adding benchmark tests.
---

# Go Testing Patterns

## When to Use This Skill

- Writing tests for a new Go function or package
- Reviewing tests for common anti-patterns (goroutine-unsafe `t.Fatal`, no parallel, unnamed cases)
- Setting up integration tests with real databases via testcontainers
- Choosing between testify assertions and standard `testing` package
- Adding benchmark tests to measure performance regressions

## Pattern Files

| Pattern | Use Case |
|---------|----------|
| [table-driven-tests.md](table-driven-tests.md) | Canonical Go test structure with t.Run, t.Parallel, failure messages |
| [mocking.md](mocking.md) | Interface mocking with gomock/mockery, when to use testcontainers instead |

## Core Concepts

| Concept | Rule |
|---------|------|
| **Table-driven tests** | The canonical Go pattern — struct slice with `name`, inputs, `want` |
| **`t.Run`** | Each table case runs as a named subtest — essential for readable output |
| **`t.Parallel()`** | Call at the top of the subtest body; Go 1.22+ loop capture is safe |
| **`t.Helper()`** | Call in assertion helpers so failures point to the caller, not the helper |
| **`t.Fatal` vs `t.Error`** | `t.Fatal` stops; use for setup. `t.Error` continues; use in loops |
| **`t.Cleanup`** | Preferred over `defer` in test helpers for resource teardown |
| **`-race` flag** | Always run `go test -race` in CI to catch data races |

## Quick Reference

```go
func TestParseDate(t *testing.T) {
    t.Parallel()  // mark the top-level test parallel too

    tests := []struct {
        name    string
        input   string
        want    time.Time
        wantErr bool
    }{
        {name: "valid RFC3339", input: "2024-01-15T10:00:00Z", want: time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC)},
        {name: "empty string", input: "", wantErr: true},
        {name: "invalid format", input: "not-a-date", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got, err := ParseDate(tt.input)
            if (err != nil) != tt.wantErr {
                t.Fatalf("ParseDate(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
            }
            if !tt.wantErr && !got.Equal(tt.want) {
                t.Errorf("ParseDate(%q) = %v, want %v", tt.input, got, tt.want)
            }
        })
    }
}
```

## Best Practices

1. **Always name table cases** — unnamed cases make failing output unreadable
2. **Failure message format**: `FuncName(inputs) = got, want want` — always show all three
3. **Call `t.Parallel()` in both the top-level test and each subtest** for maximum parallelism
4. **Use `t.Helper()` in every shared assertion function** — points failures at the caller
5. **Use `t.Cleanup` in helpers** instead of `defer` — runs even if the test panics
6. **Never call `t.Fatal` from a goroutine** — it panics after the test has returned
7. **Run tests with `-race` flag** — catches races that `go vet` misses

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| No `name` field in table test | Always add `name string` as the first struct field |
| `t.Fatal` in a spawned goroutine | Use a channel or `errgroup` to collect errors; call `t.Fatal` from the test goroutine |
| `time.Sleep` for async coordination | Use a done channel or `testcontainers.WaitFor` strategies |
| Missing `t.Helper()` in assertion func | Add `t.Helper()` as the first line of every helper |
| No `t.Parallel()` | Add it to top-level tests and subtests where safe |

## Next Steps

- See [table-driven-tests.md](table-driven-tests.md) for complete patterns with error cases and benchmarks
- See [mocking.md](mocking.md) for interface mocking and testcontainers integration patterns
