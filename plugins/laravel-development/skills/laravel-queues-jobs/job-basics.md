# Job Basics

Creating and dispatching queue jobs.

## Job Structure

```php
<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ProcessPodcast implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * Number of retry attempts.
     */
    public int $tries = 3;

    /**
     * Timeout in seconds.
     */
    public int $timeout = 120;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public Podcast $podcast,
        public User $user
    ) {}

    /**
     * Execute the job.
     */
    public function handle(AudioProcessor $processor): void
    {
        $processor->process($this->podcast);
    }

    /**
     * Handle job failure.
     */
    public function failed(\Throwable $exception): void
    {
        // Notify admin, log, etc.
    }
}
```

## Dispatching Jobs

```php
// Basic dispatch
ProcessPodcast::dispatch($podcast);

// With delay
ProcessPodcast::dispatch($podcast)
    ->delay(now()->addMinutes(10));

// On specific queue
ProcessPodcast::dispatch($podcast)
    ->onQueue('processing');

// On specific connection
ProcessPodcast::dispatch($podcast)
    ->onConnection('redis');

// Dispatch after HTTP response
ProcessPodcast::dispatchAfterResponse($podcast);

// Conditional dispatch
ProcessPodcast::dispatchIf($shouldProcess, $podcast);
ProcessPodcast::dispatchUnless($skipProcessing, $podcast);

// Synchronous dispatch (bypass queue)
ProcessPodcast::dispatchSync($podcast);
```

## Job Configuration

```php
class ProcessPodcast implements ShouldQueue
{
    // Retry attempts
    public int $tries = 3;

    // Timeout in seconds
    public int $timeout = 120;

    // Maximum exceptions before failing
    public int $maxExceptions = 3;

    // Seconds between retries
    public int $backoff = 60;

    // Delete if model is missing
    public bool $deleteWhenMissingModels = true;

    // Dynamic backoff (progressive delays)
    public function backoff(): array
    {
        return [60, 120, 300]; // 1min, 2min, 5min
    }

    // Retry until specific time
    public function retryUntil(): DateTime
    {
        return now()->addHours(1);
    }
}
```

## Middleware

```php
use Illuminate\Queue\Middleware\WithoutOverlapping;
use Illuminate\Queue\Middleware\RateLimited;

class ProcessPodcast implements ShouldQueue
{
    public function middleware(): array
    {
        return [
            new WithoutOverlapping($this->podcast->id),
            new RateLimited('podcasts'),
        ];
    }
}

// Configure rate limiter in AppServiceProvider
RateLimiter::for('podcasts', function ($job) {
    return Limit::perMinute(10);
});
```

## Unique Jobs

```php
use Illuminate\Contracts\Queue\ShouldBeUnique;

class ProcessPodcast implements ShouldQueue, ShouldBeUnique
{
    // Unique for 1 hour
    public int $uniqueFor = 3600;

    public function uniqueId(): string
    {
        return $this->podcast->id;
    }

    // Custom unique lock key
    public function uniqueVia()
    {
        return Cache::driver('redis');
    }
}
```

## Queue Worker

```bash
# Start worker
php artisan queue:work

# Specific queue
php artisan queue:work --queue=high,default

# Process single job
php artisan queue:work --once

# Memory limit
php artisan queue:work --memory=128

# Sleep between jobs
php artisan queue:work --sleep=3

# Timeout
php artisan queue:work --timeout=60
```
