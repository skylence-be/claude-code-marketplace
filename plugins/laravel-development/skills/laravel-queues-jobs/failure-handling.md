# Failure Handling

Managing job failures and retries.

## Failed Method

```php
class ProcessPodcast implements ShouldQueue
{
    public function handle(): void
    {
        // Process...
    }

    /**
     * Handle job failure.
     */
    public function failed(\Throwable $exception): void
    {
        // Log the failure
        Log::error('Podcast processing failed', [
            'podcast_id' => $this->podcast->id,
            'error' => $exception->getMessage(),
        ]);

        // Notify admin
        Notification::send($admin, new JobFailed($this, $exception));

        // Update model status
        $this->podcast->update(['status' => 'failed']);
    }
}
```

## Retry Configuration

```php
class ProcessPodcast implements ShouldQueue
{
    // Fixed number of retries
    public int $tries = 3;

    // Maximum exceptions before failing
    public int $maxExceptions = 3;

    // Timeout in seconds
    public int $timeout = 60;

    // Fixed backoff delay
    public int $backoff = 60;

    // Progressive backoff
    public function backoff(): array
    {
        return [60, 300, 600]; // 1min, 5min, 10min
    }

    // Retry until specific time
    public function retryUntil(): DateTime
    {
        return now()->addHours(1);
    }
}
```

## Conditional Retries

```php
class ProcessPodcast implements ShouldQueue
{
    public function handle(): void
    {
        try {
            // Process...
        } catch (TemporaryException $e) {
            // Retry later
            $this->release(60);
        } catch (PermanentException $e) {
            // Fail immediately
            $this->fail($e);
        }
    }

    // Mark as failed without retrying
    public function fail($exception = null): void
    {
        parent::fail($exception);
    }
}
```

## Failed Jobs Table

```bash
# Create failed_jobs table
php artisan queue:failed-table
php artisan migrate

# View failed jobs
php artisan queue:failed

# Retry failed job
php artisan queue:retry {id}

# Retry all failed jobs
php artisan queue:retry all

# Delete failed job
php artisan queue:forget {id}

# Delete all failed jobs
php artisan queue:flush
```

## Custom Failure Handling

```php
// app/Providers/AppServiceProvider.php
use Illuminate\Queue\Events\JobFailed;

public function boot(): void
{
    Queue::failing(function (JobFailed $event) {
        // Log or notify for all failed jobs
        Log::error('Job failed', [
            'connection' => $event->connectionName,
            'job' => $event->job->resolveName(),
            'exception' => $event->exception->getMessage(),
        ]);
    });
}
```

## Delete on Missing Models

```php
class ProcessPodcast implements ShouldQueue
{
    use SerializesModels;

    // Delete job if model was deleted
    public bool $deleteWhenMissingModels = true;
}
```

## Exception Handling

```php
class ProcessPodcast implements ShouldQueue
{
    public function handle(): void
    {
        try {
            $this->process();
        } catch (RateLimitException $e) {
            // Release and retry after rate limit
            $this->release($e->retryAfter);
        } catch (ApiException $e) {
            // Retry for API errors
            throw $e;
        } catch (ValidationException $e) {
            // Don't retry validation errors
            $this->fail($e);
        }
    }
}
```

## Horizon Monitoring

```bash
# Install Horizon (Redis only)
composer require laravel/horizon
php artisan horizon:install
php artisan migrate

# Run Horizon
php artisan horizon

# Pause/Continue
php artisan horizon:pause
php artisan horizon:continue

# Terminate
php artisan horizon:terminate
```

```php
// config/horizon.php
'environments' => [
    'production' => [
        'supervisor-1' => [
            'connection' => 'redis',
            'queue' => ['high', 'default', 'low'],
            'balance' => 'auto',
            'minProcesses' => 1,
            'maxProcesses' => 10,
            'tries' => 3,
            'timeout' => 60,
        ],
    ],
],
```
