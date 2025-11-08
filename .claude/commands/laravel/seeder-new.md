---
description: Create Laravel seeder for database population
model: claude-sonnet-4-5
---

Create a Laravel database seeder.

## Seeder Specification

$ARGUMENTS

## Laravel Seeder Patterns

### 1. **Basic Model Seeder**

```php
<?php

namespace Database\Seeders;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Seeder;

class PostSeeder extends Seeder
{
    public function run(): void
    {
        $users = User::all();

        $users->each(function (User $user) {
            Post::factory()
                ->count(rand(3, 10))
                ->for($user)
                ->create();
        });
    }
}
```

### 2. **Seeder with Relationships**

```php
<?php

namespace Database\Seeders;

use App\Models\Category;
use App\Models\Post;
use App\Models\Tag;
use App\Models\User;
use Illuminate\Database\Seeder;

class BlogSeeder extends Seeder
{
    public function run(): void
    {
        // Create categories
        $categories = Category::factory()->count(5)->create();

        // Create tags
        $tags = Tag::factory()->count(20)->create();

        // Create users with posts
        User::factory()
            ->count(10)
            ->create()
            ->each(function (User $user) use ($categories, $tags) {
                // Create posts for each user
                Post::factory()
                    ->count(rand(5, 15))
                    ->published()
                    ->create([
                        'user_id' => $user->id,
                        'category_id' => $categories->random()->id,
                    ])
                    ->each(function (Post $post) use ($tags) {
                        // Attach random tags to each post
                        $post->tags()->attach(
                            $tags->random(rand(2, 5))->pluck('id')
                        );
                    });
            });
    }
}
```

### 3. **Seeder with Specific Data**

```php
<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class UserSeeder extends Seeder
{
    public function run(): void
    {
        // Create admin user
        User::create([
            'name' => 'Admin User',
            'email' => 'admin@example.com',
            'password' => Hash::make('password'),
            'role' => 'admin',
            'email_verified_at' => now(),
        ]);

        // Create test users
        User::factory()->count(50)->create();
    }
}
```

### 4. **Environment-Aware Seeder**

```php
<?php

namespace Database\Seeders;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        if (app()->environment('local', 'staging')) {
            // Development data
            $this->call([
                UserSeeder::class,
                CategorySeeder::class,
                TagSeeder::class,
                PostSeeder::class,
                CommentSeeder::class,
            ]);
        }

        if (app()->environment('production')) {
            // Production initial data only
            $this->call([
                AdminUserSeeder::class,
                DefaultCategorySeeder::class,
            ]);
        }
    }
}
```

### 5. **Seeder with Progress Indication**

```php
<?php

namespace Database\Seeders;

use App\Models\Product;
use Illuminate\Database\Seeder;

class ProductSeeder extends Seeder
{
    public function run(): void
    {
        $this->command->info('Seeding products...');

        $bar = $this->command->getOutput()->createProgressBar(100);

        for ($i = 0; $i < 100; $i++) {
            Product::factory()->create();
            $bar->advance();
        }

        $bar->finish();
        $this->command->newLine();
        $this->command->info('Products seeded successfully!');
    }
}
```

### 6. **Seeder with Model Events Control**

```php
<?php

namespace Database\Seeders;

use App\Models\Post;
use Illuminate\Database\Seeder;

class PostSeeder extends Seeder
{
    public function run(): void
    {
        // Disable model events during seeding for performance
        Post::withoutEvents(function () {
            Post::factory()->count(1000)->create();
        });

        // Or use unguarded for mass assignment
        Post::unguard();
        Post::factory()->count(1000)->create();
        Post::reguard();
    }
}
```

## Best Practices
- Use factories for generating test data
- Call seeders in logical order (users before posts)
- Use transactions for data integrity
- Disable model events for better performance
- Use command output for progress feedback
- Create separate seeders for different environments
- Use chunking for large datasets
- Make seeders idempotent when possible

Generate complete Laravel seeder with proper structure.
