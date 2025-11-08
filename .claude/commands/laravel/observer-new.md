---
description: Create Laravel observer for model lifecycle events
model: claude-sonnet-4-5
---

Create a Laravel model observer.

## Observer Specification

$ARGUMENTS

## Laravel Observer Patterns

### 1. **Basic Observer**

```php
<?php

namespace App\Observers;

use App\Models\Post;
use Illuminate\Support\Str;

class PostObserver
{
    public function creating(Post $post): void
    {
        if (empty($post->slug)) {
            $post->slug = Str::slug($post->title);
        }
    }

    public function created(Post $post): void
    {
        // Log post creation
        activity()
            ->performedOn($post)
            ->log('Post created');
    }

    public function updating(Post $post): void
    {
        // Update slug if title changed
        if ($post->isDirty('title') && !$post->isDirty('slug')) {
            $post->slug = Str::slug($post->title);
        }
    }

    public function updated(Post $post): void
    {
        // Clear cache when post updated
        Cache::forget('post.' . $post->id);
    }

    public function deleted(Post $post): void
    {
        // Delete related data
        $post->comments()->delete();
        $post->tags()->detach();
    }

    public function restored(Post $post): void
    {
        activity()
            ->performedOn($post)
            ->log('Post restored');
    }
}
```

### 2. **Observer with File Management**

```php
<?php

namespace App\Observers;

use App\Models\User;
use Illuminate\Support\Facades\Storage;

class UserObserver
{
    public function updating(User $user): void
    {
        // Delete old avatar when changed
        if ($user->isDirty('avatar') && $user->getOriginal('avatar')) {
            Storage::delete($user->getOriginal('avatar'));
        }
    }

    public function deleted(User $user): void
    {
        // Delete user's avatar
        if ($user->avatar) {
            Storage::delete($user->avatar);
        }

        // Delete user's uploaded files
        Storage::deleteDirectory('users/' . $user->id);
    }

    public function forceDeleted(User $user): void
    {
        // Permanent deletion cleanup
        $user->posts()->forceDelete();
        $user->comments()->forceDelete();
    }
}
```

### 3. **Observer with Events**

```php
<?php

namespace App\Observers;

use App\Events\OrderStatusChanged;
use App\Models\Order;

class OrderObserver
{
    public function creating(Order $order): void
    {
        $order->number = 'ORD-' . strtoupper(Str::random(10));
        $order->status = 'pending';
    }

    public function updating(Order $order): void
    {
        if ($order->isDirty('status')) {
            event(new OrderStatusChanged(
                $order,
                $order->getOriginal('status'),
                $order->status
            ));
        }
    }

    public function updated(Order $order): void
    {
        // Update related inventory when order status changes
        if ($order->wasChanged('status') && $order->status === 'confirmed') {
            $order->items->each(function ($item) {
                $item->product->decrement('stock', $item->quantity);
            });
        }
    }
}
```

### 4. **Observer with Validation**

```php
<?php

namespace App\Observers;

use App\Models\Product;
use Illuminate\Validation\ValidationException;

class ProductObserver
{
    public function saving(Product $product): void
    {
        // Validate price
        if ($product->price < 0) {
            throw ValidationException::withMessages([
                'price' => 'Price cannot be negative.',
            ]);
        }

        // Ensure stock is not negative
        if ($product->stock < 0) {
            $product->stock = 0;
        }
    }

    public function updating(Product $product): void
    {
        // Track price changes
        if ($product->isDirty('price')) {
            $product->priceHistory()->create([
                'old_price' => $product->getOriginal('price'),
                'new_price' => $product->price,
                'changed_at' => now(),
            ]);
        }
    }

    public function deleting(Product $product): void
    {
        // Prevent deletion if product has active orders
        if ($product->orders()->whereIn('status', ['pending', 'processing'])->exists()) {
            throw new \Exception('Cannot delete product with active orders.');
        }
    }
}
```

### 5. **Observer with Cache Management**

```php
<?php

namespace App\Observers;

use App\Models\Post;
use Illuminate\Support\Facades\Cache;

class PostObserver
{
    public function created(Post $post): void
    {
        // Clear post list cache
        $this->clearPostCaches();
    }

    public function updated(Post $post): void
    {
        // Clear specific post cache
        Cache::forget("post.{$post->id}");
        Cache::forget("post.slug.{$post->slug}");

        // Clear list cache if publication status changed
        if ($post->wasChanged('status')) {
            $this->clearPostCaches();
        }
    }

    public function deleted(Post $post): void
    {
        Cache::forget("post.{$post->id}");
        $this->clearPostCaches();
    }

    protected function clearPostCaches(): void
    {
        Cache::tags(['posts'])->flush();
    }
}
```

### 6. **Observer with Job Dispatch**

```php
<?php

namespace App\Observers;

use App\Jobs\ProcessImage;
use App\Jobs\SendWelcomeEmail;
use App\Models\User;

class UserObserver
{
    public function created(User $user): void
    {
        // Send welcome email asynchronously
        SendWelcomeEmail::dispatch($user)->delay(now()->addMinutes(5));

        // Set up default settings
        $user->settings()->create([
            'theme' => 'light',
            'timezone' => 'UTC',
            'notifications_enabled' => true,
        ]);
    }

    public function updating(User $user): void
    {
        // Process avatar image when changed
        if ($user->isDirty('avatar')) {
            ProcessImage::dispatch($user->avatar, 'avatar');
        }
    }
}
```

## Best Practices
- Register observers in EventServiceProvider or AppServiceProvider
- Use creating/updating for modifications before save
- Use created/updated for actions after save
- Clear caches when models change
- Dispatch jobs for time-consuming tasks
- Handle file cleanup in deleted/forceDeleted
- Use isDirty() to detect changes
- Consider performance impact of observers

Generate complete Laravel observer with lifecycle hooks.
