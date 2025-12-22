# Database Testing

Testing database operations with factories and assertions.

## RefreshDatabase Trait

```php
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

test('creates user in database', function () {
    $user = User::factory()->create(['email' => 'test@example.com']);

    $this->assertDatabaseHas('users', ['email' => 'test@example.com']);
});
```

## Factory Patterns

```php
// database/factories/PostFactory.php
class PostFactory extends Factory
{
    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'title' => fake()->sentence(),
            'slug' => fake()->slug(),
            'content' => fake()->paragraphs(3, true),
            'status' => 'draft',
            'published_at' => null,
        ];
    }

    public function published(): static
    {
        return $this->state(fn (array $attrs) => [
            'status' => 'published',
            'published_at' => now(),
        ]);
    }

    public function withComments(int $count = 3): static
    {
        return $this->has(Comment::factory()->count($count));
    }
}
```

## Factory Usage

```php
test('factory states', function () {
    $draft = Post::factory()->create();
    $published = Post::factory()->published()->create();

    expect($draft->status)->toBe('draft');
    expect($published->status)->toBe('published');
});

test('factory relationships', function () {
    $user = User::factory()
        ->has(Post::factory()->count(3))
        ->create();

    expect($user->posts)->toHaveCount(3);
});

test('factory with specific attributes', function () {
    $post = Post::factory()->create([
        'title' => 'Specific Title',
    ]);

    expect($post->title)->toBe('Specific Title');
});

test('factory make vs create', function () {
    // make() - doesn't save to database
    $user = User::factory()->make();
    $this->assertDatabaseMissing('users', ['email' => $user->email]);

    // create() - saves to database
    $user = User::factory()->create();
    $this->assertDatabaseHas('users', ['email' => $user->email]);
});
```

## Database Assertions

```php
test('database has record', function () {
    $user = User::factory()->create(['email' => 'test@example.com']);

    $this->assertDatabaseHas('users', ['email' => 'test@example.com']);
});

test('database missing record', function () {
    $this->assertDatabaseMissing('users', ['email' => 'nonexistent@example.com']);
});

test('database count', function () {
    User::factory()->count(5)->create();

    $this->assertDatabaseCount('users', 5);
});

test('soft delete', function () {
    $post = Post::factory()->create();

    $post->delete();

    $this->assertSoftDeleted($post);
    $this->assertDatabaseHas('posts', ['id' => $post->id]);
});

test('model exists', function () {
    $user = User::factory()->create();

    $this->assertModelExists($user);
});

test('model missing', function () {
    $user = User::factory()->make(['id' => 999]);

    $this->assertModelMissing($user);
});
```

## Transactions

```php
test('database transaction', function () {
    DB::beginTransaction();

    User::factory()->create(['email' => 'test@example.com']);
    $this->assertDatabaseHas('users', ['email' => 'test@example.com']);

    DB::rollBack();
    $this->assertDatabaseMissing('users', ['email' => 'test@example.com']);
});
```
