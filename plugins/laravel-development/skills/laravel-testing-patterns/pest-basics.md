# Pest Basics

Core Pest testing patterns and structure.

## Test Structure

```php
<?php

use App\Models\User;
use App\Models\Post;
use function Pest\Laravel\{get, post, put, delete, actingAs};

// Setup for all tests in file
beforeEach(function () {
    $this->user = User::factory()->create();
});

// Basic test
test('homepage loads', function () {
    get('/')->assertStatus(200);
});

// With description
it('allows users to login', function () {
    // Test code
});

// Using actingAs helper
test('authenticated user can create post', function () {
    actingAs($this->user)
        ->post('/posts', ['title' => 'Test', 'content' => 'Content'])
        ->assertStatus(302)
        ->assertSessionHas('success');

    $this->assertDatabaseHas('posts', [
        'title' => 'Test',
        'user_id' => $this->user->id,
    ]);
});
```

## Pest Expectations

```php
test('expectations examples', function () {
    $post = Post::factory()->create(['title' => 'Hello']);

    // Basic expectations
    expect($post->title)->toBe('Hello');
    expect($post->id)->toBeInt();
    expect($post->published_at)->toBeNull();

    // Chained expectations
    expect($post)
        ->title->toBe('Hello')
        ->status->toBe('draft')
        ->user_id->toBeInt();

    // Collection expectations
    $users = User::factory()->count(3)->create();
    expect($users)->toHaveCount(3);
    expect($users->first())->toBeInstanceOf(User::class);

    // Negative expectations
    expect($post->title)->not->toBe('Goodbye');
    expect($post->deleted_at)->not->toBeNull();
});
```

## Groups and Filtering

```php
// Tag tests for filtering
test('admin feature')->group('admin', 'feature');
test('user feature')->group('user', 'feature');

// Skip tests
test('pending feature')->skip();
test('skip on CI')->skip(env('CI'));

// Only run this test
test('focus this')->only();

// Run specific groups
// ./vendor/bin/pest --group=admin
```

## Datasets

```php
// Inline dataset
test('validates email format', function (string $email) {
    expect(filter_var($email, FILTER_VALIDATE_EMAIL))->toBeFalse();
})->with(['invalid', 'also-invalid', 'no@tld']);

// Named dataset
dataset('invalid_emails', [
    'missing @' => ['invalid'],
    'no domain' => ['test@'],
    'no tld' => ['test@domain'],
]);

test('rejects invalid emails', function (string $email) {
    post('/register', ['email' => $email])
        ->assertSessionHasErrors('email');
})->with('invalid_emails');
```

## Hooks

```php
// Before each test
beforeEach(function () {
    $this->user = User::factory()->create();
});

// After each test
afterEach(function () {
    // Cleanup
});

// Before all tests in file
beforeAll(function () {
    // One-time setup
});

// After all tests
afterAll(function () {
    // One-time cleanup
});
```
