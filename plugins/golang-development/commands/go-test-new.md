---
description: Generate table-driven tests for a Go function or method with t.Run subtests and parallel execution
---

# New Go Test

Generate idiomatic table-driven tests for a Go function or method, following Go testing conventions with named subtests, parallel execution, and proper failure messages.

## Specification

$ARGUMENTS

## Process

1. **Identify the target function/method** from the specification
2. **Determine test cases** — happy path, zero values, boundary conditions, error cases
3. **Write the test struct** with `name string` first, then inputs, then `want` / `wantErr`
4. **Use `t.Run` with `t.Parallel()`** inside each subtest
5. **Format failure messages** as `FuncName(inputs) = got, want want`
6. **Add `t.Helper()`** to any shared assertion helpers
7. **Include benchmark** if the function is on a hot path

## Examples

### Pure function test

```go
func TestAdd(t *testing.T) {
    t.Parallel()
    tests := []struct {
        name    string
        a, b    int
        want    int
    }{
        {name: "positive", a: 1, b: 2, want: 3},
        {name: "negative", a: -1, b: -2, want: -3},
        {name: "zero", a: 0, b: 0, want: 0},
        {name: "overflow boundary", a: math.MaxInt, b: 1, want: math.MinInt},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

### Error-returning function test

```go
func TestParseConfig(t *testing.T) {
    t.Parallel()
    tests := []struct {
        name    string
        input   string
        want    *Config
        wantErr bool
    }{
        {name: "valid", input: `{"port":8080}`, want: &Config{Port: 8080}},
        {name: "empty", input: "", wantErr: true},
        {name: "invalid json", input: "{bad}", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got, err := ParseConfig([]byte(tt.input))
            if (err != nil) != tt.wantErr {
                t.Fatalf("ParseConfig() error = %v, wantErr %v", err, tt.wantErr)
            }
            if !tt.wantErr && !reflect.DeepEqual(got, tt.want) {
                t.Errorf("ParseConfig() = %+v, want %+v", got, tt.want)
            }
        })
    }
}
```

### Benchmark alongside tests

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```

Generate idiomatic table-driven tests with descriptive case names and `FuncName(inputs) = got, want want` failure messages.
