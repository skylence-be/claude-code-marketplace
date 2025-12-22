# Job Chains

Execute jobs sequentially.

## Basic Chain

```php
use Illuminate\Support\Facades\Bus;

Bus::chain([
    new ProcessPodcast($podcast),
    new OptimizePodcast($podcast),
    new ReleasePodcast($podcast),
    new NotifySubscribers($podcast),
])->dispatch();

// Jobs execute in order
// If any job fails, remaining jobs are skipped
```

## Chain with Callbacks

```php
Bus::chain([
    new ProcessPodcast($podcast),
    new ReleasePodcast($podcast),
])
->catch(function (Throwable $e) {
    // Handle chain failure
    Log::error('Chain failed', ['error' => $e->getMessage()]);
})
->finally(function () use ($podcast) {
    // Always runs after chain completes
    $podcast->update(['processed' => true]);
})
->onQueue('processing')
->dispatch();
```

## Conditional Chaining

```php
Bus::chain([
    new ProcessPodcast($podcast),
    $podcast->needs_transcription
        ? new TranscribePodcast($podcast)
        : null,
    new ReleasePodcast($podcast),
])->filter()->dispatch();

// filter() removes null jobs
```

## Chain from Job

```php
class ProcessPodcast implements ShouldQueue
{
    public function handle(): void
    {
        // Process podcast...

        // Start a new chain
        Bus::chain([
            new OptimizePodcast($this->podcast),
            new ReleasePodcast($this->podcast),
        ])->dispatch();
    }
}
```

## Dynamic Chain Building

```php
class PodcastProcessor
{
    public function process(Podcast $podcast): void
    {
        $jobs = collect();

        $jobs->push(new ProcessPodcast($podcast));

        if ($podcast->needs_transcription) {
            $jobs->push(new TranscribePodcast($podcast));
        }

        if ($podcast->has_video) {
            $jobs->push(new ProcessVideo($podcast));
        }

        $jobs->push(new ReleasePodcast($podcast));
        $jobs->push(new NotifySubscribers($podcast));

        Bus::chain($jobs->all())
            ->onQueue('processing')
            ->catch(function (Throwable $e) use ($podcast) {
                $podcast->markAsFailed($e->getMessage());
            })
            ->dispatch();
    }
}
```

## Chain with Batches

```php
// Mix chains and batches
Bus::chain([
    new PrepareImport($file),

    // Parallel processing
    Bus::batch([
        new ImportChunk($chunk1),
        new ImportChunk($chunk2),
        new ImportChunk($chunk3),
    ]),

    // After batch completes
    new FinalizeImport($file),
    new NotifyUser($user),
])->dispatch();
```

## Chain Queue/Connection

```php
Bus::chain([
    new ProcessPodcast($podcast),
    new ReleasePodcast($podcast),
])
->onConnection('redis')
->onQueue('podcasts')
->dispatch();

// Individual jobs can override
class ProcessPodcast implements ShouldQueue
{
    public $queue = 'processing'; // Override chain queue
}
```
