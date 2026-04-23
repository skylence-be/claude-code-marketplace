# Mocking in Go

## The Right Mental Model

Go mocking is about **interface substitution**. You define a small interface at the consumer side, then swap in a fake implementation in tests. The language's implicit interface satisfaction makes this effortless.

```go
// Consumer defines the interface it needs (minimal!)
type UserStore interface {
    Get(ctx context.Context, id int) (*User, error)
    Save(ctx context.Context, u *User) error
}

// Service depends on the interface, not a concrete type
type UserService struct {
    store UserStore
}

// In tests: inject a fake
type fakeStore struct {
    users map[int]*User
}

func (f *fakeStore) Get(_ context.Context, id int) (*User, error) {
    u, ok := f.users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return u, nil
}

func (f *fakeStore) Save(_ context.Context, u *User) error {
    f.users[u.ID] = u
    return nil
}
```

## Hand-Written Fakes (Preferred for Simple Cases)

For simple cases, write the fake by hand. It's explicit, readable, and has no dependencies:

```go
func TestUserService_GetByID(t *testing.T) {
    store := &fakeStore{users: map[int]*User{
        1: {ID: 1, Name: "Alice"},
    }}
    svc := NewUserService(store)

    user, err := svc.GetByID(context.Background(), 1)
    if err != nil {
        t.Fatalf("GetByID(1) error = %v", err)
    }
    if user.Name != "Alice" {
        t.Errorf("GetByID(1).Name = %q, want %q", user.Name, "Alice")
    }
}
```

## gomock (Generated Mocks)

For interfaces with many methods or complex call expectations, use `go.uber.org/mock/gomock`:

```bash
go install go.uber.org/mock/mockgen@latest
mockgen -source=internal/store/store.go -destination=internal/store/mock/mock_store.go
```

```go
func TestUserService_GetByID_StoreError(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockStore := mock.NewMockUserStore(ctrl)
    mockStore.EXPECT().
        Get(gomock.Any(), 42).
        Return(nil, ErrNotFound)

    svc := NewUserService(mockStore)
    _, err := svc.GetByID(context.Background(), 42)
    if !errors.Is(err, ErrNotFound) {
        t.Errorf("expected ErrNotFound, got %v", err)
    }
}
```

## testcontainers-go (Integration Tests)

For storage, queues, or external services — don't mock, use the real thing via containers:

```go
import (
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestUserStore_Integration(t *testing.T) {
    ctx := context.Background()

    pgc, err := postgres.RunContainer(ctx,
        testcontainers.WithImage("postgres:16"),
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready to accept connections"),
        ),
    )
    if err != nil {
        t.Fatalf("start postgres: %v", err)
    }
    t.Cleanup(func() { pgc.Terminate(ctx) })

    dsn, _ := pgc.ConnectionString(ctx, "sslmode=disable")
    store := NewPostgresStore(dsn)
    // test against real DB
}
```

Tag integration tests to keep unit tests fast:

```go
//go:build integration

func TestUserStore_Integration(t *testing.T) { ... }
```

```bash
# Run only unit tests (fast)
go test ./...

# Run integration tests
go test -tags=integration ./...
```

## Rules for Mocking

1. **Mock only what you own** — don't mock types from third-party packages; wrap them behind your own interface first
2. **Define interfaces at the consumer** — the package that uses the type defines the interface
3. **Keep interfaces small** — only include methods the consumer actually calls; don't copy the full interface from the provider
4. **Prefer real implementations** — if a real DB is practical (testcontainers), prefer it over mocks; mocks can drift from reality
5. **Don't mock the standard library** — wrap `http.Client`, `os.File`, etc. behind small interfaces, then mock the wrapper

## What NOT to Mock

- `time.Now()` — inject a `func() time.Time` or `clock.Clock` interface instead
- `rand.Rand` — inject a seeded source or interface
- Your own internal packages — only mock at layer boundaries (store, external service, file system)
