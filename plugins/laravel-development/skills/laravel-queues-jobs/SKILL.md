---
name: laravel-queues-jobs
description: Master Laravel queues and job processing with queue drivers, job batching, chaining, failure handling, Horizon monitoring, and advanced queue patterns. Use when implementing background job processing, async tasks, scheduled work, or building scalable job pipelines.
---

# Laravel Queues & Jobs

Comprehensive guide to background job processing in Laravel.

## When to Use This Skill

- Processing tasks asynchronously
- Sending emails without blocking
- Processing uploaded files
- Making delayed API calls
- Building job pipelines

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Job Basics | `job-basics.md` | Creating and dispatching jobs |
| Batching | `batching.md` | Processing jobs in batches |
| Chains | `chains.md` | Sequential job processing |
| Failures | `failure-handling.md` | Retries and error handling |

## Quick Start

```php
// Create a job
php artisan make:job ProcessPodcast

// Job class
class ProcessPodcast implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(public Podcast $podcast) {}

    public function handle(): void
    {
        // Process the podcast
    }
}

// Dispatch
ProcessPodcast::dispatch($podcast);

// Run worker
php artisan queue:work
```

## Core Concepts

### Queue Drivers
- **Database**: Jobs in database (development)
- **Redis**: Fast, reliable (production)
- **SQS**: Amazon queue service
- **Sync**: Immediate execution (testing)

### Job Lifecycle
1. Dispatched → 2. Queued → 3. Processed → 4. Completed/Failed

### Configuration
```bash
# .env
QUEUE_CONNECTION=redis

# Run queue worker
php artisan queue:work

# Run specific queue
php artisan queue:work --queue=high,default
```

## Quick Reference

### Dispatch Jobs
```php
// Basic dispatch
ProcessPodcast::dispatch($podcast);

// Delayed dispatch
ProcessPodcast::dispatch($podcast)->delay(now()->addMinutes(10));

// Specific queue
ProcessPodcast::dispatch($podcast)->onQueue('processing');

// Specific connection
ProcessPodcast::dispatch($podcast)->onConnection('redis');

// Dispatch after response
ProcessPodcast::dispatchAfterResponse($podcast);

// Dispatch if
ProcessPodcast::dispatchIf($condition, $podcast);
```

### Job Options
```php
class ProcessPodcast implements ShouldQueue
{
    public int $tries = 3;
    public int $timeout = 120;
    public int $maxExceptions = 3;
    public int $backoff = 60; // Seconds between retries

    public bool $deleteWhenMissingModels = true;

    // Dynamic backoff
    public function backoff(): array
    {
        return [60, 120, 300]; // 1min, 2min, 5min
    }
}
```

### Batching
```php
use Illuminate\Bus\Batch;
use Illuminate\Support\Facades\Bus;

$batch = Bus::batch([
    new ProcessPodcast($podcast1),
    new ProcessPodcast($podcast2),
])
->then(fn(Batch $batch) => /* All completed */)
->catch(fn(Batch $batch) => /* First failure */)
->finally(fn(Batch $batch) => /* Batch finished */)
->dispatch();
```

### Chaining
```php
Bus::chain([
    new ProcessPodcast($podcast),
    new ReleasePodcast($podcast),
    new NotifySubscribers($podcast),
])->dispatch();
```

## Best Practices

1. **Keep jobs small** and focused
2. **Use database transactions** carefully
3. **Set appropriate timeouts** and retries
4. **Handle failures gracefully**
5. **Monitor with Horizon** (Redis)
6. **Use rate limiting** for external APIs

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Jobs timing out | Increase timeout, break into smaller jobs |
| Memory leaks | Release models, unset large variables |
| Duplicate processing | Use unique jobs or locks |
| Silent failures | Implement failed() method |
