---
description: Create Laravel policy for authorization logic
model: claude-sonnet-4-5
---

Create a Laravel policy for authorization.

## Policy Specification

$ARGUMENTS

## Laravel Policy Patterns

### 1. **Resource Policy**

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    public function viewAny(User $user): bool
    {
        return true;
    }

    public function view(?User $user, Post $post): bool
    {
        return $post->status === 'published'
            || $user?->id === $post->user_id
            || $user?->isAdmin();
    }

    public function create(User $user): bool
    {
        return $user->email_verified_at !== null;
    }

    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id || $user->isAdmin();
    }

    public function delete(User $user, Post $post): bool
    {
        return $user->id === $post->user_id || $user->isAdmin();
    }

    public function restore(User $user, Post $post): bool
    {
        return $user->isAdmin();
    }

    public function forceDelete(User $user, Post $post): bool
    {
        return $user->isAdmin();
    }

    public function publish(User $user, Post $post): bool
    {
        return $user->id === $post->user_id && $post->status === 'draft';
    }
}
```

### 2. **Policy with Before Hook**

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    public function before(User $user, string $ability): ?bool
    {
        // Admins can do everything
        if ($user->isAdmin()) {
            return true;
        }

        // Banned users can't do anything
        if ($user->isBanned()) {
            return false;
        }

        return null; // Continue to individual ability checks
    }

    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }

    public function delete(User $user, Post $post): bool
    {
        return $user->id === $post->user_id
            && $post->created_at->diffInHours() < 24;
    }
}
```

### 3. **Policy with Responses**

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

class PostPolicy
{
    public function update(User $user, Post $post): Response
    {
        if ($user->id !== $post->user_id) {
            return Response::deny('You do not own this post.');
        }

        if ($post->published_at && $post->published_at->isPast()) {
            return Response::deny('Cannot edit published posts after 24 hours.')
                ->withStatus(403);
        }

        return Response::allow();
    }

    public function delete(User $user, Post $post): Response
    {
        return $user->id === $post->user_id
            ? Response::allow()
            : Response::denyWithStatus(403, 'You do not own this post.');
    }

    public function publish(User $user, Post $post): Response
    {
        if (!$user->hasVerifiedEmail()) {
            return Response::deny('You must verify your email before publishing.');
        }

        if ($post->status !== 'draft') {
            return Response::deny('Only draft posts can be published.');
        }

        return Response::allow();
    }
}
```

### 4. **Guest-Aware Policy**

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    public function view(?User $user, Post $post): bool
    {
        // Public posts viewable by anyone
        if ($post->status === 'published') {
            return true;
        }

        // Draft posts only viewable by author
        return $user !== null && $user->id === $post->user_id;
    }

    public function viewAny(?User $user): bool
    {
        // Anyone can view the post list
        return true;
    }

    public function create(?User $user): bool
    {
        // Must be authenticated to create
        return $user !== null;
    }
}
```

### 5. **Policy with Helper Methods**

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    public function update(User $user, Post $post): bool
    {
        return $this->isOwner($user, $post) && $this->isEditable($post);
    }

    public function delete(User $user, Post $post): bool
    {
        return $this->isOwner($user, $post) || $this->isModerator($user);
    }

    protected function isOwner(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }

    protected function isEditable(Post $post): bool
    {
        return $post->status === 'draft'
            || $post->published_at?->isFuture();
    }

    protected function isModerator(User $user): bool
    {
        return in_array($user->role, ['admin', 'moderator']);
    }
}
```

## Best Practices
- Use nullable User for guest access
- Use before() hook for admin bypass
- Return Response objects for detailed messages
- Use helper methods for complex logic
- Consider time-based restrictions
- Register policies in AuthServiceProvider
- Use policy filters for global rules
- Test all authorization scenarios

Generate complete Laravel policy with authorization methods.
