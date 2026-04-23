# Sentinel Errors

## What Are Sentinel Errors

Sentinel errors are package-level error variables callers check by identity. They answer the question: "Did this specific thing go wrong?"

```go
var ErrNotFound = errors.New("not found")
var ErrTimeout  = errors.New("operation timed out")
var ErrInvalid  = errors.New("invalid input")
```

## Naming Convention

- Exported sentinels: `Err` prefix — `ErrNotFound`, `ErrPermission`, `ErrAlreadyExists`
- Unexported sentinels (package-internal): `err` prefix — `errClosed`, `errEmpty`
- Document every exported sentinel with a doc comment

```go
// ErrNotFound is returned when a requested resource does not exist.
var ErrNotFound = errors.New("not found")

// ErrAlreadyExists is returned when attempting to create a resource that exists.
var ErrAlreadyExists = errors.New("already exists")
```

## Checking Sentinel Errors

Always use `errors.Is` — not `==`. This works correctly even when the error is wrapped:

```go
// Correct — works through wrap chains
if errors.Is(err, ErrNotFound) {
    // handle not found
}

// Wrong — breaks when err is wrapped with fmt.Errorf("%w", ErrNotFound)
if err == ErrNotFound {
    // this may miss the error after wrapping
}
```

## Returning Sentinel Errors

Return the sentinel directly, or wrap it with context:

```go
func GetUser(id int) (*User, error) {
    u, ok := db[id]
    if !ok {
        return nil, ErrNotFound  // direct return
    }
    return u, nil
}

func LoadProfile(userID int) (*Profile, error) {
    user, err := GetUser(userID)
    if err != nil {
        // wrap with context — errors.Is still finds ErrNotFound
        return nil, fmt.Errorf("loading profile for user %d: %w", userID, err)
    }
    return buildProfile(user), nil
}
```

## When to Use Sentinel Errors

**Use sentinels when:**
- Callers need to check for a specific condition and branch on it
- The error represents a normal, expected outcome (e.g., "not found", "already exists")
- The error carries no additional structured data

**Don't use sentinels when:**
- The error carries structured data a caller needs (use a custom error type instead)
- The error is an internal implementation detail callers shouldn't distinguish

## Sentinel Error in Standard Library

The stdlib uses this pattern extensively — study these as canonical examples:

```go
io.EOF                  // signals end of input (expected, not an error per se)
os.ErrNotExist          // file not found (use errors.Is, not string comparison)
context.DeadlineExceeded
context.Canceled
sql.ErrNoRows
```

## Common Mistakes

```go
// Mistake 1: Comparing wrapped errors with ==
err = fmt.Errorf("reading: %w", ErrNotFound)
err == ErrNotFound  // false — use errors.Is

// Mistake 2: Returning concrete error type from exported function
func Get() *NotFoundError { ... }
// Problem: callers must import the error type; nil interface bugs lurk

// Correct: return the error interface
func Get() error { return ErrNotFound }
```
