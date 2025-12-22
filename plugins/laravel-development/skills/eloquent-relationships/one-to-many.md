# One-to-Many Relationships

One-to-Many relationships link a single record to multiple related records.

## Use Cases
- Post → Comments
- User → Posts
- Category → Products

## Implementation

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Post extends Model
{
    protected $fillable = ['user_id', 'title', 'content', 'published_at'];

    /**
     * Get the comments for the post.
     */
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    /**
     * Get approved comments only.
     */
    public function approvedComments(): HasMany
    {
        return $this->hasMany(Comment::class)
            ->where('approved', true)
            ->orderBy('created_at', 'desc');
    }

    /**
     * Get the author of the post.
     */
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }
}

class Comment extends Model
{
    protected $fillable = ['post_id', 'user_id', 'content', 'approved'];

    public function post(): BelongsTo
    {
        return $this->belongsTo(Post::class);
    }

    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }
}
```

## Usage Examples

```php
$post = Post::find(1);

// Get all comments
$comments = $post->comments;

// Get count without loading models
$commentCount = $post->comments()->count();

// Add new comment
$post->comments()->create([
    'user_id' => auth()->id(),
    'content' => 'Great post!',
    'approved' => false
]);

// Create multiple comments
$post->comments()->createMany([
    ['user_id' => 1, 'content' => 'Comment 1'],
    ['user_id' => 2, 'content' => 'Comment 2'],
]);

// Query relationship
$recentComments = $post->comments()
    ->where('created_at', '>', now()->subDays(7))
    ->get();

// Check if relationship exists
if ($post->comments()->exists()) {
    // Post has comments
}
```

## Scoped Relationships

```php
class User extends Model
{
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }

    public function publishedPosts(): HasMany
    {
        return $this->hasMany(Post::class)
            ->where('status', 'published')
            ->orderBy('published_at', 'desc');
    }

    public function recentPosts(): HasMany
    {
        return $this->hasMany(Post::class)
            ->whereBetween('created_at', [now()->subMonth(), now()]);
    }
}
```
