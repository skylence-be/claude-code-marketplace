# HTTP Testing

Testing HTTP endpoints and responses.

## Basic Requests

```php
use function Pest\Laravel\{get, post, put, patch, delete};

test('index returns posts', function () {
    Post::factory()->count(5)->create();

    get('/posts')
        ->assertStatus(200)
        ->assertViewIs('posts.index')
        ->assertViewHas('posts', fn($posts) => $posts->count() === 5);
});

test('store creates post', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->post('/posts', [
            'title' => 'New Post',
            'content' => 'Content here',
        ])
        ->assertRedirect('/posts')
        ->assertSessionHas('success');

    $this->assertDatabaseHas('posts', ['title' => 'New Post']);
});

test('update modifies post', function () {
    $post = Post::factory()->create();

    actingAs($post->user)
        ->put("/posts/{$post->id}", ['title' => 'Updated'])
        ->assertRedirect();

    expect($post->fresh()->title)->toBe('Updated');
});

test('delete removes post', function () {
    $post = Post::factory()->create();

    actingAs($post->user)
        ->delete("/posts/{$post->id}")
        ->assertRedirect('/posts');

    $this->assertDatabaseMissing('posts', ['id' => $post->id]);
});
```

## JSON/API Testing

```php
test('api returns posts', function () {
    Post::factory()->count(3)->create();

    get('/api/posts')
        ->assertStatus(200)
        ->assertJsonCount(3, 'data')
        ->assertJsonStructure([
            'data' => [
                '*' => ['id', 'title', 'content', 'created_at']
            ]
        ]);
});

test('api creates post', function () {
    $user = User::factory()->create();
    Sanctum::actingAs($user);

    postJson('/api/posts', [
        'title' => 'API Post',
        'content' => 'Created via API',
    ])
        ->assertStatus(201)
        ->assertJsonPath('data.title', 'API Post');
});

test('api validates input', function () {
    $user = User::factory()->create();
    Sanctum::actingAs($user);

    postJson('/api/posts', [])
        ->assertStatus(422)
        ->assertJsonValidationErrors(['title', 'content']);
});

test('api returns specific resource', function () {
    $post = Post::factory()->create(['title' => 'Specific']);

    getJson("/api/posts/{$post->id}")
        ->assertOk()
        ->assertJson([
            'data' => [
                'id' => $post->id,
                'title' => 'Specific',
            ]
        ]);
});
```

## Validation Testing

```php
test('validation requires title', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->post('/posts', ['content' => 'No title'])
        ->assertSessionHasErrors('title');
});

test('validation rejects short title', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->post('/posts', ['title' => 'ab', 'content' => 'Content'])
        ->assertSessionHasErrors(['title']);
});

test('validation accepts valid data', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->post('/posts', [
            'title' => 'Valid Title',
            'content' => 'Valid content',
        ])
        ->assertSessionHasNoErrors();
});
```

## File Uploads

```php
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

test('can upload avatar', function () {
    Storage::fake('public');

    $user = User::factory()->create();
    $file = UploadedFile::fake()->image('avatar.jpg');

    actingAs($user)
        ->post('/profile/avatar', ['avatar' => $file])
        ->assertOk();

    Storage::disk('public')->assertExists('avatars/' . $file->hashName());
});

test('validates file type', function () {
    Storage::fake('public');

    $user = User::factory()->create();
    $file = UploadedFile::fake()->create('document.pdf');

    actingAs($user)
        ->post('/profile/avatar', ['avatar' => $file])
        ->assertSessionHasErrors('avatar');
});

test('validates file size', function () {
    Storage::fake('public');

    $user = User::factory()->create();
    $file = UploadedFile::fake()->image('large.jpg')->size(10240);

    actingAs($user)
        ->post('/profile/avatar', ['avatar' => $file])
        ->assertSessionHasErrors('avatar');
});
```
