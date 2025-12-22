# Eager Loading and N+1 Prevention

Eager loading is **critical** for preventing N+1 query problems in Laravel applications.

## The N+1 Problem

```php
// BAD: N+1 Problem - Causes 101 queries for 100 posts
$posts = Post::all(); // 1 query

foreach ($posts as $post) {
    echo $post->author->name; // 100 additional queries (1 per post)
}
```

## The Solution: Eager Loading

```php
// GOOD: Eager loading - Only 2 queries
$posts = Post::with('author')->get(); // 2 queries total

foreach ($posts as $post) {
    echo $post->author->name; // No additional queries
}
```

## Eager Loading Patterns

### Single Relationship
```php
$posts = Post::with('author')->get();
```

### Multiple Relationships
```php
$posts = Post::with(['author', 'comments', 'tags'])->get();
```

### Nested Eager Loading
```php
$posts = Post::with([
    'author.profile',           // Load author and their profile
    'comments.author',          // Load comments and comment authors
    'comments.replies.author'   // Load comment replies and their authors
])->get();
```

### Constrained Eager Loading
```php
$posts = Post::with([
    'comments' => function ($query) {
        $query->where('approved', true)
            ->orderBy('created_at', 'desc')
            ->limit(10);
    },
    'author' => function ($query) {
        $query->select('id', 'name', 'email'); // Only load specific columns
    }
])->get();
```

### Arrow Function Syntax (PHP 7.4+)
```php
$posts = Post::with([
    'comments' => fn($q) => $q->where('approved', true)->latest(),
    'author' => fn($q) => $q->select('id', 'name'),
])->get();
```

## Lazy Eager Loading

Load relationships after the initial query:

```php
$posts = Post::all();

// Later, decide to load relationships
if ($includeAuthor) {
    $posts->load('author', 'comments');
}

// Load with constraints
$posts->load([
    'comments' => fn($q) => $q->where('approved', true)
]);
```

## Select Specific Columns

Reduce memory usage by loading only needed columns:

```php
// Always include foreign key columns!
$posts = Post::with('author:id,name,email')->get();

// Multiple relationships with column selection
$posts = Post::with([
    'author:id,name',
    'category:id,name,slug',
    'tags:id,name'
])->get();
```

## Relationship Counts

Get counts without loading full relationships:

```php
// Count relationships
$posts = Post::withCount('comments')->get();
// Access: $post->comments_count

// Multiple counts
$posts = Post::withCount(['comments', 'likes', 'shares'])->get();

// Conditional counts
$posts = Post::withCount([
    'comments',
    'comments as approved_comments_count' => function ($query) {
        $query->where('approved', true);
    }
])->get();
```

## Aggregate Functions

```php
$users = User::withCount('posts')
    ->withSum('posts', 'views')
    ->withAvg('posts', 'rating')
    ->withMax('posts', 'created_at')
    ->withMin('posts', 'created_at')
    ->get();

// Access: $user->posts_count, $user->posts_sum_views, etc.
```

## Relationship Existence Queries

```php
// Posts that have comments
$posts = Post::has('comments')->get();

// Posts with at least 10 comments
$posts = Post::has('comments', '>=', 10)->get();

// Posts with approved comments
$posts = Post::whereHas('comments', function ($query) {
    $query->where('approved', true);
})->get();

// Posts without comments
$posts = Post::doesntHave('comments')->get();

// Nested relationship checks
$users = User::whereHas('posts.comments', function ($query) {
    $query->where('approved', true);
})->get();
```

## Performance Best Practices

### 1. Always Eager Load in Loops
```php
// BAD
$users = User::all();
foreach ($users as $user) {
    echo $user->profile->bio; // N+1!
}

// GOOD
$users = User::with('profile')->get();
```

### 2. Use Exists Instead of Count
```php
// BAD: Loads all comments
if (count($post->comments) > 0) { }

// GOOD: Uses EXISTS query
if ($post->comments()->exists()) { }
```

### 3. Chunk Large Datasets
```php
// BAD: Loads all users into memory
$users = User::with('posts')->get();

// GOOD: Process in chunks
User::with('posts')->chunk(100, function ($users) {
    foreach ($users as $user) {
        // Process user
    }
});

// GOOD: Cursor for memory efficiency
foreach (User::with('posts')->cursor() as $user) {
    // Process user
}
```

### 4. Load Only Required Columns
```php
// BAD
$posts = Post::with('author')->get();

// GOOD
$posts = Post::select('id', 'title', 'user_id', 'created_at')
    ->with('author:id,name,email')
    ->get();
```

### 5. Use Relationship Counts Over Loading
```php
// BAD: Loads all comments
$posts = Post::with('comments')->get();
foreach ($posts as $post) {
    echo count($post->comments);
}

// GOOD: Only count, don't load
$posts = Post::withCount('comments')->get();
foreach ($posts as $post) {
    echo $post->comments_count;
}
```

## Detecting N+1 Problems

Use Laravel Debugbar or enable query logging:

```php
// Enable query log
DB::enableQueryLog();

// Your code here
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name;
}

// Check queries
dd(DB::getQueryLog()); // Will show N+1 problem
```

Or use the `preventLazyLoading` method in development:

```php
// In AppServiceProvider boot()
Model::preventLazyLoading(! app()->isProduction());
```
