---
name: laravel-testing-patterns
description: Master Laravel testing with Pest 4 syntax, feature tests, unit tests, database testing, factories, mocking, browser testing with Dusk, and comprehensive testing strategies. Use when writing tests, implementing TDD, or building robust test suites.
---

# Laravel Testing Patterns

Comprehensive guide to testing Laravel applications using Pest 4.

## When to Use This Skill

- Writing feature tests for HTTP endpoints
- Creating unit tests for services and logic
- Testing database operations with factories
- Mocking external services and APIs
- Implementing TDD/BDD practices

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Pest Basics | [pest-basics.md](pest-basics.md) | Test structure, assertions, setup |
| HTTP Testing | [http-testing.md](http-testing.md) | Endpoints, responses, validation |
| Database Testing | [database-testing.md](database-testing.md) | Factories, assertions, transactions |
| Mocking | [mocking.md](mocking.md) | HTTP, Mail, Queue, Events |
| Authentication | [auth-testing.md](auth-testing.md) | Login, logout, guards |
| Advanced | [advanced.md](advanced.md) | Parallel, middleware, commands |
| Browser Testing | [pest-browser-testing.md](pest-browser-testing.md) | Pest 4 real browser tests, smoke testing, visual regression, sharding |

## Test File Naming

Test files follow `{Verb}{Noun}Test.php` naming in `tests/Feature/{Domain}/`:

```
tests/
  Feature/
    {Domain}/           ← one directory per domain (Todos/, Users/, Posts/)
      {Verb}{Noun}Test.php
  Unit/
    Actions/
      {Domain}/
        {Verb}{Noun}ActionTest.php
  Browser/
    {Domain}/
      {Verb}{Noun}BrowserTest.php
  Arch/
    ActionsTest.php
    ControllersTest.php
```

| Rule | Example | Anti-pattern |
|------|---------|-------------|
| File = `{Verb}{Noun}Test.php` | `ArchiveTodoTest.php` | `TodoArchivedAtMassAssignmentTest.php` (noun-first) |
| Regression = `{Verb}{Noun}RegressionTest.php` | `ArchiveTodoRegressionTest.php` | `TodoRegressionTest.php` (too vague) |
| Domain directory = the model/feature name | `tests/Feature/Todos/` | `tests/Feature/Regression/` (cross-cutting) |
| Unit action = `{Verb}{Noun}ActionTest.php` | `CreateTodoActionTest.php` | `TodoCreateTest.php` |

### What NOT to Create

Do not create cross-cutting directories. Tests live in their domain directory:

- `tests/Feature/Regression/` -- regression tests live in their domain directory as `{Verb}{Noun}RegressionTest.php`
- `tests/Feature/Integration/` -- feature tests ARE integration tests
- `tests/Feature/Api/` -- API tests live in the domain directory (`tests/Feature/Todos/ListTodosTest.php` works for both web and API)
- `tests/Helpers/` -- use Pest's `beforeEach()` or `uses()` traits

### Before Writing a Test File

1. `ls tests/Feature/{Domain}/` -- check siblings
2. If `{Verb}{Noun}Test.php` already exists for the feature you're testing, **add a test case to the existing file** instead of creating a new file
3. Only create a new file when testing a distinct verb (create vs archive vs export)

## Quick Start

```php
// Install Pest
composer require pestphp/pest --dev
php artisan pest:install

// Basic test structure
test('user can create post', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->post('/posts', ['title' => 'Test', 'content' => 'Content'])
        ->assertRedirect();

    $this->assertDatabaseHas('posts', ['title' => 'Test']);
});

// Run tests
php artisan test
./vendor/bin/pest
```

## Core Concepts

### Test Types
- **Feature Tests**: Test complete HTTP flows
- **Unit Tests**: Test isolated classes/methods
- **Browser Tests**: Test JavaScript with Dusk

### AAA Pattern
```php
test('example', function () {
    // Arrange - Set up test data
    $user = User::factory()->create();

    // Act - Execute the code
    $response = actingAs($user)->get('/dashboard');

    // Assert - Verify results
    $response->assertSuccessful();
});
```

## Quick Reference

### HTTP Assertions
```php
// Use semantic assertions — never assertStatus() with numeric codes
$response->assertSuccessful();   // 2xx (prefer over assertStatus(200))
$response->assertOk();           // 200
$response->assertCreated();      // 201
$response->assertNoContent();    // 204
$response->assertNotFound();     // 404 (prefer over assertStatus(404))
$response->assertForbidden();    // 403
$response->assertUnauthorized(); // 401

$response->assertRedirect('/path');
$response->assertSessionHas('key');
$response->assertSessionHasErrors(['field']);
$response->assertViewIs('view.name');
$response->assertViewHas('key');
```

### JSON Assertions
```php
$response->assertJson(['key' => 'value']);
$response->assertJsonPath('data.id', 1);
$response->assertJsonCount(3, 'data');
$response->assertJsonStructure([
    'data' => ['id', 'title']
]);
$response->assertJsonValidationErrors(['field']);
```

### Database Assertions
```php
$this->assertDatabaseHas('users', ['email' => 'test@example.com']);
$this->assertDatabaseMissing('users', ['email' => 'deleted@example.com']);
$this->assertDatabaseCount('users', 5);
$this->assertSoftDeleted($model);
$this->assertModelExists($model);
```

### Factories
```php
// Create single model
$user = User::factory()->create();

// Create multiple
$users = User::factory()->count(5)->create();

// With states
$admin = User::factory()->admin()->create();

// With relationships
$user = User::factory()
    ->has(Post::factory()->count(3))
    ->create();
```

### Mocking
```php
// HTTP
Http::fake(['api.example.com/*' => Http::response(['data' => 'value'])]);

// Mail
Mail::fake();
Mail::assertSent(WelcomeMail::class);

// Queue
Queue::fake();
Queue::assertPushed(ProcessJob::class);

// Storage
Storage::fake('public');
Storage::disk('public')->assertExists('file.txt');
```

## Best Practices

1. **Use Pest syntax** for cleaner, readable tests
2. **Use RefreshDatabase** to isolate tests
3. **Use factories** for all test data
4. **Test behavior**, not implementation
5. **Mock external services** only
6. **Keep tests fast** with in-memory DB
7. **Run tests in parallel** for speed

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Tests affect each other | Use RefreshDatabase trait |
| Slow tests | Use in-memory SQLite |
| Testing implementation | Test observable behavior |
| Over-mocking | Only mock external services |
| No assertions | Every test must assert something |
| assertStatus(200) | Use assertSuccessful() or assertOk() |
| assertStatus(404) | Use assertNotFound() |
| Shared beforeEach state | Each test sets up its own factories |

## Minimum Test Counts Per Endpoint

Happy path alone is not enough. Every controller endpoint requires coverage across multiple categories:

| Endpoint type | Min tests | Coverage |
|---|---|---|
| POST store | 6 | happy path, auth (401), authz (403), validation datasets, uniqueness, response structure |
| GET index | 4 | happy path, empty state, pagination/filters, data isolation |
| PUT update | 6 | happy path, auth (401), authz (403), validation datasets, not found (404), no-op/partial update |
| DELETE destroy | 4 | happy path, auth (401), authz (403), not found (404) |
| PATCH toggle/archive | 5 | happy path, auth (401), authz (403), not found (404), idempotent |
| GET show | 3 | happy path, auth (401), not found (404) |

## 10-Point Test Checklist Per Endpoint

For every endpoint (GET, POST, PUT, PATCH, DELETE), generate tests covering ALL of these:

1. **Happy path** -- request succeeds with valid data, correct response code, correct state change
2. **Authentication (401)** -- unauthenticated request returns 401 or redirects to login. Test with `$this->get(route(...))` (no `actingAs`)
3. **Authorization (403)** -- authenticated but wrong user returns 403. Test with `actingAs($otherUser)->get(route(..., $model))`
4. **Validation (POST/PUT/PATCH)** -- use named datasets for missing required, empty string, max length exceeded, wrong type
5. **Not found (404)** -- request with non-existent ID returns 404. `actingAs($user)->get(route('todos.edit', 99999))->assertNotFound()`
6. **Data isolation** -- response contains ONLY the authenticated user's data, not other users'
7. **State transitions** -- assert DB state changed: `assertDatabaseHas`, `assertModelExists`, `$model->refresh()`, timestamp checks
8. **Edge cases** -- toggle back, idempotent archive, partial update leaves other fields unchanged, delete archived model
9. **Response structure (API)** -- correct JSON keys present, no internal fields leaked, pagination meta on list endpoints
10. **Flash/redirects (web)** -- after store redirect to index with `success` flash, after validation failure redirect back with errors

### Validation Datasets

Use named datasets for validation rules. One `it()` with a dataset beats five separate `it()` blocks:

```php
it('rejects invalid store data', function (array $data, string $errorKey): void {
    $this->actingAs(User::factory()->create())
        ->post(route('todos.store'), $data)
        ->assertSessionHasErrors($errorKey);
})->with([
    'missing title' => [['notes' => 'some notes'], 'title'],
    'empty title' => [['title' => ''], 'title'],
    'title too long' => [['title' => str_repeat('a', 256)], 'title'],
    'title not string' => [['title' => 123], 'title'],
]);
```

**Rule:** 3+ similar assertions = dataset. 2 = leave separate.

### Unit Test Checklist for Actions

1. **Happy path** -- action executes, returns correct type, side effects fire
2. **Invalid state** -- action throws domain exception on invalid input
3. **Side effects verified** -- `Event::assertDispatched`, `Mail::assertQueued`, etc.
4. **No leaking** -- action doesn't touch models it shouldn't

## Architecture Tests (`tests/Arch/`)

Architecture tests enforce conventions as executable rules. Place in `tests/Arch/`:

```php
// tests/Arch/ActionsTest.php
arch('actions are final')
    ->expect('App\Actions')
    ->toBeFinal();

arch('actions have an execute method')
    ->expect('App\Actions')
    ->toHaveMethod('execute');

arch('actions live only in App\Actions')
    ->expect('App\Actions')
    ->toHaveSuffix('Action');

arch('domain actions are final and have an execute method')
    ->expect('App\Domains')
    ->classes()
    ->that->haveSuffix('Action')
    ->toBeFinal()
    ->toHaveMethod('execute');
```

```php
// tests/Arch/ControllersTest.php
arch('controllers do not use DB, Cache, or Mail directly')
    ->expect('App\Http\Controllers')
    ->not->toUse([
        'Illuminate\Support\Facades\DB',
        'Illuminate\Support\Facades\Cache',
        'Illuminate\Support\Facades\Mail',
    ]);
```

```php
// tests/Arch/NoServicesTest.php
arch('no classes named Service live in app')
    ->expect('App')
    ->classes()
    ->not->toHaveSuffix('Service');

arch('no Repository classes')
    ->expect('App')
    ->classes()
    ->not->toHaveSuffix('Repository');
```

```php
// tests/Arch/DomainBoundariesTest.php
arch('Subscriptions internals are not imported outside the context')
    ->expect('App\Domains\Subscriptions\Actions')
    ->toOnlyBeUsedIn([
        'App\Http\Controllers',
        'App\Domains\Subscriptions',
        'Tests',
    ]);

arch('models never import controllers or HTTP')
    ->expect('App\Models')
    ->not->toUse('App\Http');
```

## Pipeline and DDD Test Templates

### Unit Test Per Pipe

```php
use App\Pipelines\Checkout\Pipes\ReserveInventoryAction;

it('attaches a reservation id to the payload', function (): void {
    $reserver = Mockery::mock(InventoryReserver::class);
    $reserver->shouldReceive('reserve')->once()->andReturn('res-123');

    $pipe = new ReserveInventoryAction($reserver);
    $data = StartCheckoutData::from([
        'userId' => 1,
        'lineItems' => [['product_id' => 1, 'quantity' => 2]],
    ]);

    $result = $pipe->handle($data, fn (StartCheckoutData $payload) => $payload);

    expect($result->reservationId)->toBe('res-123');
});
```

### Feature Test for Whole Pipeline

```php
use App\Pipelines\Checkout\CheckoutPipeline;

it('turns a StartCheckoutData into an Order', function (): void {
    $user = User::factory()->create();
    $product = Product::factory()->create(['stock' => 10]);

    Event::fake();

    $data = StartCheckoutData::from([
        'userId' => $user->id,
        'lineItems' => [['product_id' => $product->id, 'quantity' => 2]],
    ]);

    $result = app(CheckoutPipeline::class)->execute($data);

    expect($result->order)->toBeInstanceOf(Order::class);
    $result->order->assertModelExists();

    Event::assertDispatched(OrderPlaced::class);
});
```

### DDD Action Tests

DDD action feature tests live in `tests/Feature/Domains/{Context}/`:

```php
// tests/Feature/Domains/Subscriptions/CreateSubscriptionTest.php

it('creates a subscription via POST /subscriptions', function (): void {
    $user = User::factory()->create();
    $plan = Plan::factory()->create();

    Event::fake();

    $this->actingAs($user)
        ->post('/subscriptions', [
            'plan_id' => $plan->id,
            'billing_cycle_days' => 30,
        ])
        ->assertRedirect();

    $this->assertDatabaseHas('subscriptions', [
        'user_id' => $user->id,
        'plan_id' => $plan->id,
        'billing_cycle_days' => 30,
    ]);

    Event::assertDispatched(SubscriptionCreated::class);
});
```
