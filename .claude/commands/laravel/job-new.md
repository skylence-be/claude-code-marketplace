---
description: Create Laravel job for queue processing
model: claude-sonnet-4-5
---

Create a Laravel queued job.

## Job Specification

$ARGUMENTS

## Laravel Job Patterns

### 1. **Basic Queued Job**

```php
<?php

namespace App\Jobs;

use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class SendWelcomeEmail implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public User $user
    ) {}

    public function handle(): void
    {
        Mail::to($this->user->email)->send(new WelcomeEmail($this->user));
    }
}
```

### 2. **Job with Retry Logic**

```php
<?php

namespace App\Jobs;

use App\Models\Order;
use App\Services\PaymentGateway;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ProcessPayment implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $tries = 3;
    public $maxExceptions = 3;
    public $timeout = 120;
    public $backoff = [30, 60, 120]; // Exponential backoff in seconds

    public function __construct(
        public Order $order
    ) {}

    public function handle(PaymentGateway $gateway): void
    {
        $gateway->process($this->order);
    }

    public function failed(\Throwable $exception): void
    {
        // Handle job failure
        $this->order->update(['status' => 'payment_failed']);

        // Notify admin
        Notification::route('mail', config('mail.admin'))
            ->notify(new PaymentFailedNotification($this->order, $exception));
    }
}
```

### 3. **Job with Rate Limiting**

```php
<?php

namespace App\Jobs;

use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\RateLimiter;

class SendNotification implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public User $user,
        public string $message
    ) {}

    public function handle(): void
    {
        RateLimiter::attempt(
            'send-notification:' . $this->user->id,
            $perMinute = 5,
            function () {
                // Send notification
                $this->user->notify(new CustomNotification($this->message));
            }
        );
    }

    public function middleware(): array
    {
        return [
            (new WithoutOverlapping($this->user->id))
                ->expireAfter(60)
                ->releaseAfter(10),
        ];
    }
}
```

### 4. **Batch Job**

```php
<?php

namespace App\Jobs;

use App\Models\User;
use Illuminate\Bus\Batchable;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ProcessUserData implements ShouldQueue
{
    use Batchable, Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public User $user
    ) {}

    public function handle(): void
    {
        if ($this->batch()->cancelled()) {
            return;
        }

        // Process user data
        $this->user->processData();
    }
}

// Dispatch batch:
// Bus::batch([
//     new ProcessUserData($user1),
//     new ProcessUserData($user2),
// ])->then(function (Batch $batch) {
//     // All jobs completed
// })->catch(function (Batch $batch, Throwable $e) {
//     // First batch job failure
// })->finally(function (Batch $batch) {
//     // Batch finished
// })->dispatch();
```

### 5. **Unique Job**

```php
<?php

namespace App\Jobs;

use App\Models\Report;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class GenerateReport implements ShouldQueue, ShouldBeUnique
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $uniqueFor = 3600; // 1 hour

    public function __construct(
        public int $reportId,
        public string $type
    ) {}

    public function uniqueId(): string
    {
        return $this->reportId . '-' . $this->type;
    }

    public function handle(): void
    {
        $report = Report::find($this->reportId);
        $report->generate($this->type);
    }
}
```

### 6. **Chain Job**

```php
<?php

namespace App\Jobs;

use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ProcessOrder implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public Order $order
    ) {}

    public function handle(): void
    {
        // Process the order
        $this->order->update(['status' => 'processing']);
    }
}

// Dispatch chain:
// ProcessOrder::withChain([
//     new SendOrderConfirmation($order),
//     new NotifyWarehouse($order),
//     new UpdateInventory($order),
// ])->dispatch($order);
```

## Best Practices
- Use dependency injection in handle()
- Set appropriate timeouts and retries
- Implement failed() for cleanup
- Use ShouldBeUnique for idempotent jobs
- Monitor queue performance with Horizon/Pulse
- Use batching for bulk operations
- Set proper queue priorities
- Handle job failures gracefully

Generate complete Laravel job with queue configuration.
