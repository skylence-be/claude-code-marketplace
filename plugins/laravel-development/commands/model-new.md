---
description: Create Laravel Eloquent model with migration
model: claude-sonnet-4-5
---

Create a Laravel Eloquent model with migration and relationships.

## Model Specification

$ARGUMENTS

## Laravel Model Best Practices

### 1. **Model** (app/Models/Post.php)

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\SoftDeletes;

class Post extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        'title',
        'slug',
        'content',
        'user_id',
        'published_at',
    ];

    protected $casts = [
        'published_at' => 'datetime',
    ];

    // Relationships
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    // Scopes
    public function scopePublished($query)
    {
        return $query->whereNotNull('published_at');
    }

    // Accessors & Mutators
    public function getExcerptAttribute(): string
    {
        return str($this->content)->limit(150);
    }

    protected function title(): Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
            set: fn (string $value) => strtolower($value),
        );
    }
}
```

### 2. **Migration** (database/migrations/xxxx_create_posts_table.php)

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->string('slug')->unique();
            $table->text('content');
            $table->timestamp('published_at')->nullable();
            $table->timestamps();
            $table->softDeletes();

            $table->index(['user_id', 'published_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
```

### 3. **Factory** (database/factories/PostFactory.php)

```php
<?php

namespace Database\Factories;

use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

class PostFactory extends Factory
{
    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'title' => fake()->sentence(),
            'slug' => fake()->slug(),
            'content' => fake()->paragraphs(3, true),
            'published_at' => fake()->optional()->dateTimeBetween('-1 year', 'now'),
        ];
    }

    public function published(): static
    {
        return $this->state(fn (array $attributes) => [
            'published_at' => now(),
        ]);
    }
}
```

### 4. **Common Relationships**

```php
// One-to-Many
public function comments(): HasMany
{
    return $this->hasMany(Comment::class);
}

// Many-to-One
public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}

// Many-to-Many
public function tags(): BelongsToMany
{
    return $this->belongsToMany(Tag::class)->withTimestamps();
}

// Has One Through
public function latestComment(): HasOneThrough
{
    return $this->hasOneThrough(Comment::class, User::class)
        ->latest();
}

// Polymorphic
public function images(): MorphMany
{
    return $this->morphMany(Image::class, 'imageable');
}
```

Generate complete Laravel model with migration, factory, and relationships.
