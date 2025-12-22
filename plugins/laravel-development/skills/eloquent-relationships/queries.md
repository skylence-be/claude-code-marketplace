# Relationship Query Methods

Common query methods for working with Eloquent relationships.

## Checking Relationship Existence

```php
$user = User::find(1);

// Check if relationship exists
$hasComments = $user->comments()->exists();
$doesntHaveComments = $user->comments()->doesntExist();

// Count without loading
$commentCount = $user->comments()->count();
```

## Creating Related Models

```php
// Create single related model
$comment = $user->comments()->create([
    'content' => 'My comment',
    'approved' => false
]);

// Create multiple
$user->comments()->createMany([
    ['content' => 'Comment 1'],
    ['content' => 'Comment 2'],
]);

// First or create
$comment = $user->comments()->firstOrCreate(
    ['content' => 'First!'],
    ['approved' => false]
);

// First or new (doesn't save)
$comment = $user->comments()->firstOrNew(['content' => 'Draft']);

// Update or create
$post = $user->posts()->updateOrCreate(
    ['slug' => 'my-first-post'],
    ['title' => 'My First Post', 'content' => '...']
);

// Find or fallback
$post = $user->posts()->findOr(1, function () use ($user) {
    return $user->posts()->create([
        'title' => 'Default Post',
        'content' => 'Default content'
    ]);
});
```

## Many-to-Many Operations

```php
$user = User::find(1);

// Attach (add relationship)
$user->roles()->attach(1);
$user->roles()->attach([1, 2, 3]);
$user->roles()->attach(1, ['assigned_at' => now()]);

// Detach (remove relationship)
$user->roles()->detach(1);
$user->roles()->detach([1, 2, 3]);
$user->roles()->detach(); // Remove all

// Sync (set to exactly these)
$user->roles()->sync([1, 2, 3]);
$user->roles()->sync([1 => ['expires_at' => now()->addYear()]]);
$user->roles()->syncWithoutDetaching([4, 5]); // Only add, don't remove

// Toggle
$user->roles()->toggle([1, 2, 3]);

// Update pivot data
$user->roles()->updateExistingPivot($roleId, [
    'assigned_by' => auth()->id()
]);
```

## Querying Relationships

```php
$user = User::find(1);

// Filter relationship
$recentPosts = $user->posts()
    ->where('created_at', '>', now()->subDays(7))
    ->orderBy('created_at', 'desc')
    ->get();

// Paginate relationships
$comments = $user->comments()->paginate(20);

// Cursor pagination
$comments = $user->comments()->cursorPaginate(20);

// Get first
$latestPost = $user->posts()->latest()->first();

// Chunk relationships
$user->posts()->chunk(100, function ($posts) {
    foreach ($posts as $post) {
        // Process post
    }
});
```

## Deleting Related Models

```php
$user = User::find(1);

// Delete all related
$user->posts()->delete();

// Force delete (if using soft deletes)
$user->posts()->forceDelete();

// Delete with conditions
$user->posts()->where('status', 'draft')->delete();
```

## Aggregates on Relationships

```php
$user = User::find(1);

// Count
$postCount = $user->posts()->count();

// Sum
$totalViews = $user->posts()->sum('views');

// Average
$avgRating = $user->posts()->avg('rating');

// Max/Min
$maxViews = $user->posts()->max('views');
$oldestPost = $user->posts()->min('created_at');
```

## Custom Relationship Methods

```php
class User extends Model
{
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }

    public function publishedPosts(): HasMany
    {
        return $this->posts()
            ->where('status', 'published')
            ->where('published_at', '<=', now());
    }

    public function popularPosts(): HasMany
    {
        return $this->hasMany(Post::class)
            ->where('views', '>=', 1000)
            ->orderBy('views', 'desc');
    }

    // Helper methods
    public function getPostCountAttribute(): int
    {
        return $this->posts()->count();
    }

    public function hasRole(string $roleName): bool
    {
        return $this->roles()->where('name', $roleName)->exists();
    }

    public function assignRole(string $roleName): void
    {
        $role = Role::where('name', $roleName)->firstOrFail();
        $this->roles()->attach($role->id);
    }
}

// Usage
$user = User::find(1);
$publishedPosts = $user->publishedPosts;
$popularPosts = $user->popularPosts;

// Combine with scopes
$posts = $user->posts()->published()->popular()->get();
```

## Saving Related Models

```php
// Associate (belongsTo)
$comment = new Comment(['content' => 'My comment']);
$comment->post()->associate($post);
$comment->save();

// Dissociate
$comment->post()->dissociate();
$comment->save();

// Save (hasMany)
$post = new Post(['title' => 'New Post']);
$user->posts()->save($post);

// Save many
$user->posts()->saveMany([
    new Post(['title' => 'Post 1']),
    new Post(['title' => 'Post 2']),
]);

// Push (saves model and all relationships)
$user->posts->first()->title = 'Updated Title';
$user->push(); // Saves user and modified post
```
