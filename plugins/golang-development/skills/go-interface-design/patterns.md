# Interface Design Patterns

## Consumer-Defined Interface

The package that *uses* a type defines the interface it needs. The package that *provides* the type exports a concrete struct.

```go
// package store — exports a concrete type
package store

type PostgresUserStore struct { db *sql.DB }

func (s *PostgresUserStore) Get(ctx context.Context, id int) (*User, error) { ... }
func (s *PostgresUserStore) Save(ctx context.Context, u *User) error { ... }
func (s *PostgresUserStore) Delete(ctx context.Context, id int) error { ... }
func (s *PostgresUserStore) List(ctx context.Context) ([]*User, error) { ... }


// package service — defines only what it needs from the store
package service

// UserStore is the interface this service needs — not everything store.PostgresUserStore has
type UserStore interface {
    Get(ctx context.Context, id int) (*User, error)
    Save(ctx context.Context, u *User) error
}

type UserService struct {
    store UserStore
}

func NewUserService(s UserStore) *UserService {
    return &UserService{store: s}
}
```

This way:
- `store.PostgresUserStore` can be used in tests by implementing only the 2 methods `service` needs
- Adding methods to `PostgresUserStore` doesn't break any interface
- Circular imports are impossible (store doesn't know about service)

## Accept Interfaces, Return Concretes

```go
// Accept the minimal interface — callers can pass any implementation
func NewProcessor(r io.Reader) *Processor {
    return &Processor{r: r}
}

// Return concrete type — callers get full access to all methods
func NewHTTPClient(cfg Config) *http.Client {
    return &http.Client{Timeout: cfg.Timeout}
}

// Exception: return error interface for errors
func Parse(s string) (*Result, error) { ... }
```

## Compile-Time Interface Verification

Verify that a type implements an interface at compile time, near the type definition:

```go
// Ensures *MyHandler implements http.Handler — fails at compile time if not
var _ http.Handler = (*MyHandler)(nil)

// For unexported types too
var _ io.ReadCloser = (*myBuffer)(nil)
```

Place these `var _ = ...` declarations near the type, not in a separate file.

## Small Interface Composition

Build expressive interfaces from small pieces instead of defining large monoliths:

```go
// Standard library pattern
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

Your code:
```go
// Compose only what you need at each call site
func copy(dst io.Writer, src io.Reader) (int64, error) { ... }
func pipe(rw io.ReadWriter) error { ... }
```

## Dependency Injection Pattern

Wire concrete implementations at the top level; depend on interfaces everywhere else:

```go
// main.go — the composition root
func main() {
    db := store.NewPostgresStore(cfg.DSN)
    cache := cache.NewRedisCache(cfg.RedisAddr)
    svc := service.NewUserService(db, cache)
    srv := server.New(svc)
    srv.ListenAndServe(":8080")
}

// service/user.go — depends on interfaces
type UserService struct {
    store  UserStorer
    cache  UserCacher
}
```

## Pointer to Interface — Almost Always Wrong

```go
// Wrong — pointer to interface is almost never what you want
func Process(r *io.Reader) { ... }

// The interface already holds a pointer to the underlying data
// Correct
func Process(r io.Reader) { ... }
```

The rare exception: passing an interface as an `any` (empty interface) parameter to `reflect` or `encoding/json` sometimes requires a pointer to get addressability. This is almost never needed in application code.

## Avoiding Interface Pollution

Don't create interfaces preemptively:

```go
// Bad — premature interface, only one implementation exists
type UserServiceInterface interface {
    GetUser(id int) (*User, error)
    // ... 15 more methods
}

// Good — no interface until you need polymorphism or testability
type UserService struct { ... }
func (s *UserService) GetUser(id int) (*User, error) { ... }
```

Create an interface when:
1. You have two concrete implementations
2. You need testability (inject a fake in tests)
3. You need to break a circular dependency

## Wrapping Third-Party Types

If you need to mock a third-party type (e.g., `*redis.Client`), wrap it behind your own interface:

```go
// Don't mock *redis.Client directly — wrap it
type Cache interface {
    Get(ctx context.Context, key string) (string, error)
    Set(ctx context.Context, key, val string, ttl time.Duration) error
}

// RedisCache wraps *redis.Client and implements Cache
type RedisCache struct {
    client *redis.Client
}

func (c *RedisCache) Get(ctx context.Context, key string) (string, error) {
    return c.client.Get(ctx, key).Result()
}
```

Now tests can inject a fake `Cache` without needing a Redis instance.
