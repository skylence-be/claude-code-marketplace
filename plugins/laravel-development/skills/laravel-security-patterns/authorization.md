# Authorization

Gates, policies, and role-based access control.

## Gates

```php
// Define in AuthServiceProvider
use Illuminate\Support\Facades\Gate;

public function boot(): void
{
    Gate::define('update-post', function (User $user, Post $post) {
        return $user->id === $post->user_id;
    });

    Gate::define('delete-post', function (User $user, Post $post) {
        return $user->id === $post->user_id || $user->isAdmin();
    });

    // Before callback (super admin)
    Gate::before(function (User $user, string $ability) {
        if ($user->isSuperAdmin()) {
            return true;
        }
    });
}

// Usage
if (Gate::allows('update-post', $post)) {
    // User can update
}

if (Gate::denies('delete-post', $post)) {
    abort(403);
}
```

## Policies

```php
// Create policy
php artisan make:policy PostPolicy --model=Post

// app/Policies/PostPolicy.php
class PostPolicy
{
    public function viewAny(User $user): bool
    {
        return true;
    }

    public function view(User $user, Post $post): bool
    {
        return $post->published || $user->id === $post->user_id;
    }

    public function create(User $user): bool
    {
        return $user->hasVerifiedEmail();
    }

    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }

    public function delete(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }

    public function forceDelete(User $user, Post $post): bool
    {
        return $user->isAdmin();
    }
}

// Register in AuthServiceProvider
protected $policies = [
    Post::class => PostPolicy::class,
];
```

## Using Policies

```php
// In controllers
public function update(Request $request, Post $post)
{
    $this->authorize('update', $post);
    // Update post...
}

public function store(Request $request)
{
    $this->authorize('create', Post::class);
    // Create post...
}

// In Blade
@can('update', $post)
    <button>Edit</button>
@endcan

@cannot('delete', $post)
    <p>You cannot delete this post</p>
@endcannot

@canany(['update', 'delete'], $post)
    <div class="actions">...</div>
@endcanany
```

## Role-Based Access

```php
// Simple role check
class User extends Model
{
    public function isAdmin(): bool
    {
        return $this->role === 'admin';
    }

    public function hasRole(string $role): bool
    {
        return $this->role === $role;
    }
}

// Middleware
class AdminMiddleware
{
    public function handle(Request $request, Closure $next)
    {
        if (!$request->user()?->isAdmin()) {
            abort(403);
        }
        return $next($request);
    }
}

// Route protection
Route::middleware('admin')->group(function () {
    Route::get('/admin/dashboard', [AdminController::class, 'index']);
});
```

## Resource Controllers

```php
class PostController extends Controller
{
    public function __construct()
    {
        $this->authorizeResource(Post::class, 'post');
    }

    // All methods automatically authorized:
    // index -> viewAny
    // show -> view
    // create -> create
    // store -> create
    // edit -> update
    // update -> update
    // destroy -> delete
}
```
