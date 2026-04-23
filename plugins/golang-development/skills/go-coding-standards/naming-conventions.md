# Go Naming Conventions

## The Golden Rule: MixedCaps

Go uses MixedCaps (CamelCase) everywhere. **Never use underscores in identifiers** (except test function names like `TestFoo_returnsError` and blank identifiers).

```go
// Good
type UserAccount struct{}
func parseURL(s string) {}
var maxRetryCount int

// Bad
type user_account struct{}
func parse_url(s string) {}
var max_retry_count int
```

## Package Names

- Lowercase, single word, no underscores or mixed case
- Named after the directory that contains the package
- Never: `util`, `common`, `helper`, `lib`, `misc`

```go
// Good — descriptive of what's in the package
package config
package strutil
package httputil
package timeutil

// Bad
package utils     // too vague
package helpers   // tells callers nothing
package myPackage // mixed case
```

## Exported vs Unexported

- Exported (public): starts with uppercase letter — `UserID`, `ParseURL`, `ErrNotFound`
- Unexported (package-private): starts with lowercase — `userID`, `parseURL`, `errNotFound`

## Initialisms (URL, ID, HTTP, JSON, etc.)

Keep initialisms consistently cased within an identifier:

```go
// Good
var userID string       // not userId
func parseURL() {}     // not parseUrl
type HTTPClient struct{} // not HttpClient
type JSONDecoder struct{} // not JsonDecoder

// Bad
var userId string
func parseUrl() {}
type HttpClient struct{}
```

## Receiver Names

- 1–2 letters, abbreviation of the type name
- Consistent across ALL methods of the same type
- Never `self`, `this`, `me`

```go
// Good — c for Client, consistently
func (c *Client) Connect() error { ... }
func (c *Client) Close() error { ... }
func (c *Client) Do(req *Request) (*Response, error) { ... }

// Bad — inconsistent, or verbose
func (client *Client) Connect() error { ... }
func (self *Client) Close() error { ... }
```

## Getters and Setters

- Getters: **omit** the `Get` prefix — `Owner()` not `GetOwner()`
- Setters: use `Set` prefix — `SetOwner()`

```go
type Config struct {
    timeout int
}

func (c *Config) Timeout() int         { return c.timeout }     // getter
func (c *Config) SetTimeout(d int)     { c.timeout = d }        // setter
```

## Variable Names

Name length should correlate with scope:

```go
// Short scope → short name (fine)
for i, v := range items { ... }
func sum(a, b int) int { return a + b }

// Wide scope → descriptive name
var defaultRequestTimeout = 30 * time.Second
func (s *Server) handleUserRegistration(w http.ResponseWriter, r *http.Request) { ... }
```

**Never include type information in the name:**
```go
// Bad
userString := "alice"
countInt := 42
responseMap := map[string]any{}

// Good
user := "alice"
count := 42
response := map[string]any{}
```

## Avoiding Package Repetition

Don't repeat the package name in exported symbol names:

```go
// Good — callers write http.Client, widget.New()
package http
type Client struct{}

package widget
func New() *Widget {}

// Bad — callers would write http.HTTPClient, widget.NewWidget()
package http
type HTTPClient struct{}

package widget
func NewWidget() *Widget {}
```

## Constants and Enums

- Use MixedCaps, not ALL_CAPS
- Name by role, not value
- Start enums at `iota + 1` unless 0 is a meaningful default

```go
// Good
const (
    StatusActive   Status = iota + 1
    StatusInactive
    StatusDeleted
)

// Bad
const (
    STATUS_ACTIVE   = 0
    STATUS_INACTIVE = 1
)
```

## Error Variables

- Exported error variables: `Err` prefix → `ErrNotFound`, `ErrTimeout`
- Error types (structs): `Error` suffix → `ValidationError`, `ParseError`

```go
var ErrNotFound = errors.New("not found")
var ErrTimeout  = errors.New("timeout")

type ValidationError struct {
    Field   string
    Message string
}
```
