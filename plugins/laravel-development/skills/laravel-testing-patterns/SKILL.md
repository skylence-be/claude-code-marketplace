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
        ->assertStatus(302);

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
    $response->assertStatus(200);
});
```

## Quick Reference

### HTTP Assertions
```php
$response->assertStatus(200);
$response->assertOk();
$response->assertCreated();      // 201
$response->assertNoContent();    // 204
$response->assertNotFound();     // 404
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
