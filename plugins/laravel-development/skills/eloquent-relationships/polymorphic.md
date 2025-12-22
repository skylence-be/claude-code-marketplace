# Polymorphic Relationships

Polymorphic relationships allow a model to belong to multiple other models using a single association.

## Polymorphic One-to-Many

A single model (like Comment) can belong to multiple different models (Post, Video).

### Use Case
Comments can be on Posts OR Videos

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphTo;
use Illuminate\Database\Eloquent\Relations\MorphMany;

class Comment extends Model
{
    protected $fillable = ['content', 'user_id'];

    /**
     * Get the parent commentable model (post or video).
     */
    public function commentable(): MorphTo
    {
        return $this->morphTo();
    }

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}

class Post extends Model
{
    /**
     * Get all comments for the post.
     */
    public function comments(): MorphMany
    {
        return $this->morphMany(Comment::class, 'commentable');
    }
}

class Video extends Model
{
    /**
     * Get all comments for the video.
     */
    public function comments(): MorphMany
    {
        return $this->morphMany(Comment::class, 'commentable');
    }
}
```

### Migration
```php
Schema::create('comments', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->text('content');
    $table->morphs('commentable'); // Creates commentable_id and commentable_type
    $table->timestamps();
});
```

### Usage
```php
// Add comments
$post = Post::find(1);
$post->comments()->create([
    'content' => 'Great post!',
    'user_id' => auth()->id()
]);

$video = Video::find(1);
$video->comments()->create([
    'content' => 'Nice video!',
    'user_id' => auth()->id()
]);

// Retrieve parent model
$comment = Comment::find(1);
$commentable = $comment->commentable; // Returns Post or Video

// Query by type
$postComments = Comment::where('commentable_type', Post::class)->get();

// Eager load polymorphic relationships
$comments = Comment::with('commentable')->get();
```

## Polymorphic Many-to-Many

Multiple models can share a tagging system through a polymorphic pivot table.

### Use Case
Posts AND Videos can have Tags

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\MorphToMany;
use Illuminate\Database\Eloquent\Relations\MorphedByMany;

class Tag extends Model
{
    protected $fillable = ['name'];

    /**
     * Get all posts with this tag.
     */
    public function posts(): MorphedByMany
    {
        return $this->morphedByMany(Post::class, 'taggable');
    }

    /**
     * Get all videos with this tag.
     */
    public function videos(): MorphedByMany
    {
        return $this->morphedByMany(Video::class, 'taggable');
    }
}

class Post extends Model
{
    /**
     * Get all tags for the post.
     */
    public function tags(): MorphToMany
    {
        return $this->morphToMany(Tag::class, 'taggable')
            ->withTimestamps();
    }
}

class Video extends Model
{
    /**
     * Get all tags for the video.
     */
    public function tags(): MorphToMany
    {
        return $this->morphToMany(Tag::class, 'taggable')
            ->withTimestamps();
    }
}
```

### Migration
```php
Schema::create('taggables', function (Blueprint $table) {
    $table->foreignId('tag_id')->constrained()->cascadeOnDelete();
    $table->morphs('taggable'); // Creates taggable_id and taggable_type
    $table->timestamps();
});
```

### Usage
```php
$post = Post::find(1);
$post->tags()->attach([1, 2, 3]);

$video = Video::find(1);
$video->tags()->sync([2, 3, 4]);

// Query by tag
$tag = Tag::find(1);
$posts = $tag->posts;
$videos = $tag->videos;

// Get all taggable models
$allTagged = $tag->posts->merge($tag->videos);
```

## Custom Polymorphic Types

Define custom morph map for cleaner database values:

```php
// In AppServiceProvider boot()
use Illuminate\Database\Eloquent\Relations\Relation;

Relation::enforceMorphMap([
    'post' => Post::class,
    'video' => Video::class,
]);

// Now database stores 'post' instead of 'App\Models\Post'
```
