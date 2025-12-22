# Advanced Testing Patterns

Parallel testing, middleware, console commands, and more.

## Parallel Testing

```php
// Run tests in parallel
php artisan test --parallel

// Or with Pest
./vendor/bin/pest --parallel

// Configure in tests/Pest.php
uses(Tests\TestCase::class)->in('Feature');
```

## Middleware Testing

```php
test('auth middleware blocks unauthenticated', function () {
    get('/dashboard')
        ->assertRedirect('/login');
});

test('admin middleware restricts access', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->get('/admin/dashboard')
        ->assertForbidden();
});

test('admin middleware allows admins', function () {
    $admin = User::factory()->admin()->create();

    actingAs($admin)
        ->get('/admin/dashboard')
        ->assertOk();
});

test('rate limiting middleware', function () {
    for ($i = 0; $i < 60; $i++) {
        get('/api/posts')->assertOk();
    }

    get('/api/posts')->assertStatus(429);
});
```

## Console Command Testing

```php
test('command runs successfully', function () {
    $this->artisan('users:cleanup')
        ->expectsOutput('Cleaning up users...')
        ->expectsOutput('Cleanup complete!')
        ->assertExitCode(0);
});

test('command prompts for input', function () {
    $this->artisan('posts:delete-all')
        ->expectsQuestion('Are you sure?', 'yes')
        ->expectsOutput('All posts deleted')
        ->assertExitCode(0);
});

test('command with arguments', function () {
    $this->artisan('user:delete', ['id' => 1])
        ->expectsOutput('User 1 deleted')
        ->assertExitCode(0);
});

test('command with table output', function () {
    User::factory()->count(3)->create();

    $this->artisan('users:list')
        ->expectsTable(['ID', 'Name', 'Email'], [
            [1, 'User 1', 'user1@example.com'],
            // ...
        ])
        ->assertExitCode(0);
});
```

## Model Testing

```php
test('model has attributes', function () {
    $post = new Post(['title' => 'Test']);

    expect($post->title)->toBe('Test');
});

test('model relationships', function () {
    $user = User::factory()
        ->has(Post::factory()->count(3))
        ->create();

    expect($user->posts)->toHaveCount(3)
        ->and($user->posts->first())->toBeInstanceOf(Post::class);
});

test('model scopes', function () {
    Post::factory()->count(5)->published()->create();
    Post::factory()->count(3)->create(['status' => 'draft']);

    expect(Post::published()->count())->toBe(5);
});

test('model casts', function () {
    $post = Post::factory()->create([
        'published_at' => '2024-01-01',
        'metadata' => ['views' => 100],
    ]);

    expect($post->published_at)->toBeInstanceOf(Carbon::class)
        ->and($post->metadata)->toBeArray();
});
```

## Service Testing

```php
beforeEach(function () {
    $this->orderService = new OrderService();
});

test('calculates total', function () {
    $order = Order::factory()->create();
    $order->items()->create([
        'product_id' => Product::factory()->create(['price' => 10])->id,
        'quantity' => 2,
    ]);

    $total = $this->orderService->calculateTotal($order);

    expect($total)->toBe(20.0);
});

test('applies discount', function () {
    $order = Order::factory()->create();
    $order->items()->create([
        'product_id' => Product::factory()->create(['price' => 100])->id,
        'quantity' => 1,
    ]);

    $total = $this->orderService->calculateTotal($order, discountPercent: 10);

    expect($total)->toBe(90.0);
});

test('throws for invalid order', function () {
    $order = Order::factory()->create();

    expect(fn () => $this->orderService->process($order))
        ->toThrow(\InvalidArgumentException::class);
});
```

## Testing Jobs

```php
use Illuminate\Support\Facades\Bus;

test('job is dispatched', function () {
    Bus::fake();

    $user = User::factory()->create();
    ProcessUserJob::dispatch($user);

    Bus::assertDispatched(ProcessUserJob::class, function ($job) use ($user) {
        return $job->user->id === $user->id;
    });
});

test('job chain', function () {
    Bus::fake();

    Bus::chain([
        new FirstJob,
        new SecondJob,
    ])->dispatch();

    Bus::assertChained([FirstJob::class, SecondJob::class]);
});
```

## Performance Testing

```php
test('eager loading prevents n+1', function () {
    User::factory()->count(10)->create()->each(
        fn($user) => Post::factory()->count(5)->create(['user_id' => $user->id])
    );

    DB::enableQueryLog();

    $posts = Post::with('author')->get();
    $posts->each(fn($post) => $post->author->name);

    // Should be 2 queries: 1 for posts, 1 for users
    expect(DB::getQueryLog())->toHaveCount(2);
});
```

## Exception Testing

```php
test('throws specific exception', function () {
    expect(fn () => $service->riskyOperation())
        ->toThrow(CustomException::class);
});

test('throws with message', function () {
    expect(fn () => $service->riskyOperation())
        ->toThrow(CustomException::class, 'Expected error message');
});

test('exception renders correctly', function () {
    $this->withoutExceptionHandling();

    expect(fn () => get('/nonexistent'))
        ->toThrow(NotFoundHttpException::class);
});
```
