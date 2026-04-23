# Table-Driven Tests

## The Canonical Pattern

Table-driven tests are the idiomatic Go testing pattern. Every test case is an entry in a slice of structs, run via `t.Run` as a named subtest.

```go
func TestAdd(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name    string
        a, b    int
        want    int
    }{
        {name: "positive numbers", a: 1, b: 2, want: 3},
        {name: "negative numbers", a: -1, b: -2, want: -3},
        {name: "zero values", a: 0, b: 0, want: 0},
        {name: "mixed signs", a: 5, b: -3, want: 2},
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

## Failure Message Format

Standard format: `FuncName(inputs) = got, want want`

Always include all three: **input**, **actual output**, **expected output**.

```go
// Good
t.Errorf("ParseDate(%q) = %v, want %v", tt.input, got, tt.want)
t.Errorf("Multiply(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)

// Bad — missing context
t.Errorf("got %d, want %d", got, tt.want)
t.Errorf("test failed")
```

## Error-Returning Functions

```go
func TestParseConfig(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name    string
        input   string
        want    *Config
        wantErr bool
    }{
        {name: "valid JSON", input: `{"port":8080}`, want: &Config{Port: 8080}},
        {name: "empty input", input: "", wantErr: true},
        {name: "invalid JSON", input: "{bad}", wantErr: true},
        {name: "missing required field", input: `{}`, wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got, err := ParseConfig([]byte(tt.input))
            if (err != nil) != tt.wantErr {
                t.Fatalf("ParseConfig(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
            }
            if !tt.wantErr && !reflect.DeepEqual(got, tt.want) {
                t.Errorf("ParseConfig(%q) = %+v, want %+v", tt.input, got, tt.want)
            }
        })
    }
}
```

## `t.Fatal` vs `t.Error`

- `t.Fatal` — stops the current test immediately. Use when subsequent assertions would be meaningless (e.g., after setup failure).
- `t.Error` — marks failure but continues. Use in loops so all failing cases surface.
- **Never call `t.Fatal` from a goroutine** — it panics. Only the test's goroutine may call Fatal/Error.

```go
// Fatal for: setup failures, nil pointer guards
file, err := os.Open(tt.path)
if err != nil {
    t.Fatalf("open(%q) = %v", tt.path, err)  // no point checking file if it's nil
}
defer file.Close()

// Error for: value comparison — let all cases run
if got != tt.want {
    t.Errorf("Process(%v) = %v, want %v", tt.input, got, tt.want)
}
```

## Test Helpers with `t.Helper()`

Add `t.Helper()` as the first line of every shared assertion function. It makes failures point to the call site, not the helper.

```go
func assertEqual(t *testing.T, got, want int) {
    t.Helper()  // <-- this line
    if got != want {
        t.Errorf("got %d, want %d", got, want)
    }
}
```

## Cleanup with `t.Cleanup`

Prefer `t.Cleanup` over `defer` in test helpers — it runs even if the test panics, and the order is well-defined.

```go
func setupDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatalf("open db: %v", err)
    }
    t.Cleanup(func() { db.Close() })
    return db
}
```

## Subtests for Edge Case Organization

Group related edge cases in nested subtests:

```go
func TestParser(t *testing.T) {
    t.Run("valid inputs", func(t *testing.T) {
        t.Parallel()
        // ...table of valid inputs...
    })

    t.Run("invalid inputs", func(t *testing.T) {
        t.Parallel()
        // ...table of invalid inputs...
    })
}
```

## Loop Variable Capture

Go 1.22+: loop variable capture is safe by default inside goroutines and subtests.
Pre-1.22: capture the loop variable explicitly:

```go
for _, tt := range tests {
    tt := tt  // pre-Go 1.22 only
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // ...
    })
}
```
