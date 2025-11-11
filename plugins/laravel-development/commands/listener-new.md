---
description: Create Laravel event listener
model: claude-sonnet-4-5
---

Create a Laravel event listener.

## Listener Specification

$ARGUMENTS

## Laravel Listener Patterns

### 1. **Basic Event Listener**

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use App\Notifications\OrderShippedNotification;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Queue\InteractsWithQueue;

class SendShipmentNotification implements ShouldQueue
{
    use InteractsWithQueue;

    public function handle(OrderShipped $event): void
    {
        $event->order->user->notify(
            new OrderShippedNotification($event->order)
        );
    }

    public function failed(OrderShipped $event, \Throwable $exception): void
    {
        // Handle listener failure
        Log::error('Failed to send shipment notification', [
            'order_id' => $event->order->id,
            'error' => $exception->getMessage(),
        ]);
    }
}
```

### 2. **Listener with Dependencies**

```php
<?php

namespace App\Listeners;

use App\Events\UserRegistered;
use App\Services\AnalyticsService;
use App\Services\EmailService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Queue\InteractsWithQueue;

class ProcessUserRegistration implements ShouldQueue
{
    use InteractsWithQueue;

    public $tries = 3;
    public $timeout = 60;

    public function __construct(
        protected EmailService $emailService,
        protected AnalyticsService $analytics
    ) {}

    public function handle(UserRegistered $event): void
    {
        // Send welcome email
        $this->emailService->sendWelcome($event->user);

        // Track in analytics
        $this->analytics->track('user_registered', [
            'user_id' => $event->user->id,
            'source' => $event->source,
        ]);

        // Set up default preferences
        $event->user->preferences()->create([
            'theme' => 'light',
            'notifications' => true,
        ]);
    }
}
```

### 3. **Synchronous Listener**

```php
<?php

namespace App\Listeners;

use App\Events\PaymentProcessed;
use App\Models\Invoice;

class GenerateInvoice
{
    public function handle(PaymentProcessed $event): void
    {
        Invoice::create([
            'order_id' => $event->payment->order_id,
            'amount' => $event->payment->amount,
            'payment_method' => $event->payment->method,
            'transaction_id' => $event->payment->transaction_id,
        ]);
    }
}
```

### 4. **Listener with Conditional Execution**

```php
<?php

namespace App\Listeners;

use App\Events\PostPublished;
use App\Jobs\NotifySubscribers;
use Illuminate\Support\Facades\Cache;

class NotifyPostSubscribers
{
    public function handle(PostPublished $event): void
    {
        // Only notify if post is in certain categories
        if (!$event->post->category->should_notify) {
            return;
        }

        // Prevent duplicate notifications
        $cacheKey = "notified_post_{$event->post->id}";
        if (Cache::has($cacheKey)) {
            return;
        }

        Cache::put($cacheKey, true, now()->addDay());

        // Dispatch notification job
        NotifySubscribers::dispatch($event->post);
    }
}
```

### 5. **Multiple Event Listener**

```php
<?php

namespace App\Listeners;

use Illuminate\Auth\Events\Login;
use Illuminate\Auth\Events\Logout;

class LogUserActivity
{
    public function handleLogin(Login $event): void
    {
        $event->user->update([
            'last_login_at' => now(),
            'last_login_ip' => request()->ip(),
        ]);
    }

    public function handleLogout(Logout $event): void
    {
        activity()
            ->performedOn($event->user)
            ->log('User logged out');
    }

    public function subscribe($events): array
    {
        return [
            Login::class => 'handleLogin',
            Logout::class => 'handleLogout',
        ];
    }
}
```

## Best Practices
- Implement ShouldQueue for long-running tasks
- Use dependency injection in constructor
- Set appropriate timeouts and retries
- Implement failed() for error handling
- Keep listeners focused on single responsibility
- Register in EventServiceProvider
- Use job classes for complex logic
- Test listener behavior thoroughly

Generate complete Laravel listener with queue support.
