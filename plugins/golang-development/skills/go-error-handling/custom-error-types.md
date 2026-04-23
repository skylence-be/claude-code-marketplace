# Custom Error Types

## When to Use a Custom Error Type

Use a custom error type (a struct implementing the `error` interface) when:

- Callers need to extract **structured data** from the error (field name, status code, retry-after)
- A sentinel variable is not enough — you need parametric error values

Don't create a custom type just to give an error a name — use a sentinel `var ErrX = errors.New(...)` instead.

## Defining a Custom Error Type

```go
// ValidationError carries the field and message for a validation failure.
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}
```

Rules:
- Implement `Error() string` — that's the `error` interface
- Use a **pointer receiver** (`*ValidationError`, not `ValidationError`) so `errors.As` works correctly
- Export the type only if callers outside the package need to use `errors.As` to extract it

## Returning a Custom Error

```go
func validateEmail(email string) error {
    if !strings.Contains(email, "@") {
        return &ValidationError{Field: "email", Message: "must contain @"}
    }
    return nil
}
```

**Return the `error` interface, never the concrete type:**

```go
// Correct — return error interface
func validateEmail(email string) error { ... }

// Wrong — returning concrete type causes nil-interface bug
func validateEmail(email string) *ValidationError { ... }
// If the function returns (*ValidationError)(nil), callers checking `err != nil` get true!
```

## Extracting Custom Error Data with `errors.As`

```go
err := validateEmail("not-an-email")

var ve *ValidationError
if errors.As(err, &ve) {
    log.Printf("field %q: %s", ve.Field, ve.Message)
}
```

`errors.As` traverses the entire wrap chain — it works even if `err` is wrapped with `fmt.Errorf("validating user: %w", err)`.

## HTTP Status Code Error Pattern

```go
// HTTPError carries an HTTP status code alongside the message.
type HTTPError struct {
    Code    int
    Message string
}

func (e *HTTPError) Error() string {
    return fmt.Sprintf("HTTP %d: %s", e.Code, e.Message)
}

// Usage
func fetchUser(id int) (*User, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, fmt.Errorf("fetching user %d: %w", id, err)
    }
    if resp.StatusCode != http.StatusOK {
        return nil, &HTTPError{Code: resp.StatusCode, Message: resp.Status}
    }
    // ...
}

// Caller
var he *HTTPError
if errors.As(err, &he) && he.Code == http.StatusNotFound {
    // handle 404
}
```

## Wrapping Inside a Custom Error

Custom errors can themselves wrap an underlying error by implementing `Unwrap`:

```go
type StoreError struct {
    Op  string
    Err error
}

func (e *StoreError) Error() string { return e.Op + ": " + e.Err.Error() }
func (e *StoreError) Unwrap() error { return e.Err }

// Now errors.Is(err, ErrNotFound) traverses through StoreError
return &StoreError{Op: "GetUser", Err: ErrNotFound}
```

## Compile-Time Interface Check

Ensure your error type satisfies `error` at compile time:

```go
var _ error = (*ValidationError)(nil)
```
