---
name: eloquent-relationships
description: Master Eloquent ORM relationships including one-to-one, one-to-many, many-to-many, polymorphic, and advanced relationship patterns with eager loading and N+1 prevention. Use when designing database relationships, optimizing queries, or implementing complex data models in Laravel.
---

# Eloquent Relationships

Comprehensive guide to implementing and optimizing Eloquent ORM relationships in Laravel.

## When to Use This Skill

- Designing database relationships and model structures
- Implementing one-to-one, one-to-many, or many-to-many relationships
- Building polymorphic relationships for flexible data models
- Optimizing queries with eager loading to prevent N+1 problems
- Creating has-one-through and has-many-through relationships

## Pattern Files

For detailed implementations, read the specific pattern file:

| Pattern | File | Use Case |
|---------|------|----------|
| One-to-One | `one-to-one.md` | User → Profile, User → Address |
| One-to-Many | `one-to-many.md` | Post → Comments, User → Posts |
| Many-to-Many | `many-to-many.md` | Users ↔ Roles, Posts ↔ Tags |
| Through | `through.md` | Country → Posts (via Users) |
| Polymorphic | `polymorphic.md` | Comments on Posts or Videos |
| Eager Loading | `eager-loading.md` | **Critical for N+1 prevention** |
| Query Methods | `queries.md` | exists(), create(), sync() |
| Advanced | `advanced.md` | Caching, aggregates, defaults |

## Core Concepts

### Relationship Types
- **One-to-One**: Single record relates to single record (`hasOne`/`belongsTo`)
- **One-to-Many**: Single record relates to multiple records (`hasMany`/`belongsTo`)
- **Many-to-Many**: Multiple records relate to multiple records (`belongsToMany`)
- **Polymorphic**: Model can belong to multiple other models (`morphTo`/`morphMany`)

### Eager vs Lazy Loading
```php
// Lazy Loading - causes N+1 (BAD)
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name; // Query per post!
}

// Eager Loading - 2 queries total (GOOD)
$posts = Post::with('author')->get();
foreach ($posts as $post) {
    echo $post->author->name; // No additional queries
}
```

## Quick Reference

### Define Relationships
```php
// One-to-One
public function profile(): HasOne
{
    return $this->hasOne(Profile::class);
}

// One-to-Many
public function posts(): HasMany
{
    return $this->hasMany(Post::class);
}

// Inverse (belongs to)
public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}

// Many-to-Many
public function roles(): BelongsToMany
{
    return $this->belongsToMany(Role::class)->withTimestamps();
}
```

### Eager Load Patterns
```php
// Single relationship
Post::with('author')->get();

// Multiple relationships
Post::with(['author', 'comments', 'tags'])->get();

// Nested relationships
Post::with('author.profile')->get();

// Constrained eager loading
Post::with(['comments' => fn($q) => $q->where('approved', true)])->get();

// Select specific columns
Post::with('author:id,name,email')->get();
```

### Common Operations
```php
// Create through relationship
$user->posts()->create(['title' => 'New Post']);

// Attach/Detach (many-to-many)
$user->roles()->attach([1, 2, 3]);
$user->roles()->detach([1]);
$user->roles()->sync([2, 3, 4]);

// Check existence
$user->posts()->exists();
$user->posts()->count();

// Query with relationship
Post::has('comments')->get();
Post::whereHas('author', fn($q) => $q->where('active', true))->get();
```

## Best Practices

1. **Always eager load** when accessing relationships in loops
2. **Use `withCount()`** instead of loading full relationships for counts
3. **Define inverse relationships** for bidirectional access
4. **Specify foreign keys** explicitly when they don't follow conventions
5. **Use `withDefault()`** to prevent null errors on belongsTo

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| N+1 queries | Use `with()` eager loading |
| Loading all columns | Use `with('relation:id,name')` |
| No inverse relationship | Define `belongsTo()` on related model |
| Wrong foreign key | Specify explicitly: `belongsTo(User::class, 'author_id')` |
| Null relationship errors | Use `withDefault()` on belongsTo |

## Next Steps

Read the specific pattern files listed above for detailed implementations and code examples.
