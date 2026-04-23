# Error Wrapping

## The Two Verbs: `%w` and `%v`

Go 1.13 introduced error wrapping via `fmt.Errorf`:

- **`%w`** wraps the error — `errors.Is` and `errors.As` can unwrap through it
- **`%v`** annotates the error — does NOT wrap; callers cannot inspect the underlying error

```go
// %w: wrap — callers can errors.Is(err, ErrNotFound)
return fmt.Errorf("loading user %d: %w", id, err)

// %v: annotate — callers cannot inspect the original error
return fmt.Errorf("loading user %d: %v", id, err)
```

## When to Use `%w`

Use `%w` when callers within the same service/module might need to check the underlying error type or sentinel:

```go
func LoadProfile(userID int) (*Profile, error) {
    user, err := store.GetUser(userID)
    if err != nil {
        return nil, fmt.Errorf("load profile %d: %w", userID, err)
    }
    return buildProfile(user), nil
}

// Caller can still detect ErrNotFound through the wrap chain:
_, err := LoadProfile(42)
if errors.Is(err, store.ErrNotFound) {
    // handle not found
}
```

## When to Use `%v`

Use `%v` at system boundaries (RPC handlers, HTTP handlers, storage adapters) to prevent internal error types from leaking to external callers:

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
    user, err := s.store.GetUser(idFromPath(r))
    if err != nil {
        // %v at the boundary — don't expose internal sentinel/type to HTTP clients
        log.Printf("get user: %v", err)
        http.Error(w, "user not found", http.StatusNotFound)
        return
    }
    // ...
}
```

## Wrapping Good and Bad Examples

```go
// Good: adds context the underlying error lacks
return fmt.Errorf("opening config file: %w", err)
return fmt.Errorf("query user %d: %w", id, err)

// Bad: duplicates what the underlying error already says
// os.Open already says "open /etc/config.yaml: no such file or directory"
return fmt.Errorf("could not open /etc/config.yaml: %w", err)

// Bad: no context at all
return fmt.Errorf("error: %w", err)
return err  // fine to return bare when there's nothing useful to add
```

## Unwrapping — `errors.Is` and `errors.As`

`errors.Is` traverses the entire wrap chain checking for a target error:

```go
err := fmt.Errorf("a: %w", fmt.Errorf("b: %w", ErrNotFound))
errors.Is(err, ErrNotFound) // true — works through two levels of wrapping
```

`errors.As` traverses the chain looking for a target type and populates it:

```go
err := fmt.Errorf("process: %w", &ValidationError{Field: "email"})

var ve *ValidationError
if errors.As(err, &ve) {
    fmt.Println(ve.Field) // "email"
}
```

## `errors.Join` (Go 1.20+)

Combine multiple errors into one:

```go
func validateAll(fields []Field) error {
    var errs []error
    for _, f := range fields {
        if err := validate(f); err != nil {
            errs = append(errs, err)
        }
    }
    return errors.Join(errs...)  // nil if errs is empty
}
```

`errors.Is` and `errors.As` work through `errors.Join` results.

## Multi-wrap (Go 1.20+)

Wrap multiple errors in a single `fmt.Errorf`:

```go
// Both errs can be unwrapped from the result
return fmt.Errorf("combined: %w; %w", err1, err2)
```
