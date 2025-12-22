# Authentication Testing

Testing login, logout, and protected routes.

## Basic Auth Testing

```php
test('user can login', function () {
    $user = User::factory()->create([
        'email' => 'john@example.com',
        'password' => bcrypt('password'),
    ]);

    post('/login', [
        'email' => 'john@example.com',
        'password' => 'password',
    ])
        ->assertRedirect('/dashboard');

    $this->assertAuthenticatedAs($user);
});

test('invalid credentials rejected', function () {
    $user = User::factory()->create([
        'email' => 'john@example.com',
        'password' => bcrypt('password'),
    ]);

    post('/login', [
        'email' => 'john@example.com',
        'password' => 'wrong-password',
    ])
        ->assertSessionHasErrors();

    $this->assertGuest();
});

test('user can logout', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->post('/logout')
        ->assertRedirect('/');

    $this->assertGuest();
});
```

## Protected Routes

```php
test('guest redirected to login', function () {
    get('/dashboard')
        ->assertRedirect('/login');
});

test('authenticated user can access dashboard', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->get('/dashboard')
        ->assertStatus(200);
});

test('authenticated user redirected from login', function () {
    $user = User::factory()->create();

    actingAs($user)
        ->get('/login')
        ->assertRedirect('/dashboard');
});
```

## Email Verification

```php
test('unverified user redirected', function () {
    $user = User::factory()->unverified()->create();

    actingAs($user)
        ->get('/dashboard')
        ->assertRedirect('/verify-email');
});

test('verified user can access', function () {
    $user = User::factory()->create(); // verified by default

    actingAs($user)
        ->get('/dashboard')
        ->assertStatus(200);
});
```

## Authorization Testing

```php
test('user can update own post', function () {
    $user = User::factory()->create();
    $post = Post::factory()->create(['user_id' => $user->id]);

    actingAs($user)
        ->put("/posts/{$post->id}", ['title' => 'Updated'])
        ->assertRedirect();
});

test('user cannot update others post', function () {
    $user1 = User::factory()->create();
    $user2 = User::factory()->create();
    $post = Post::factory()->create(['user_id' => $user1->id]);

    actingAs($user2)
        ->put("/posts/{$post->id}", ['title' => 'Hacked'])
        ->assertStatus(403);
});

test('admin can update any post', function () {
    $admin = User::factory()->admin()->create();
    $post = Post::factory()->create();

    actingAs($admin)
        ->put("/posts/{$post->id}", ['title' => 'Admin Update'])
        ->assertRedirect();
});
```

## API Authentication (Sanctum)

```php
use Laravel\Sanctum\Sanctum;

test('api requires authentication', function () {
    getJson('/api/posts')
        ->assertStatus(401);
});

test('api with token', function () {
    $user = User::factory()->create();
    Sanctum::actingAs($user);

    getJson('/api/posts')
        ->assertStatus(200);
});

test('api with specific abilities', function () {
    $user = User::factory()->create();
    Sanctum::actingAs($user, ['posts:read']);

    getJson('/api/posts')->assertOk();
    postJson('/api/posts', [...])->assertForbidden();
});

test('api token creation', function () {
    $user = User::factory()->create();

    postJson('/login', [
        'email' => $user->email,
        'password' => 'password',
    ])
        ->assertOk()
        ->assertJsonStructure(['access_token', 'token_type']);
});
```
