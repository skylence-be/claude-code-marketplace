# Job Batching

Process multiple jobs as a batch.

## Setup

```bash
php artisan queue:batches-table
php artisan migrate
```

## Create Batch

```php
use Illuminate\Bus\Batch;
use Illuminate\Support\Facades\Bus;

$batch = Bus::batch([
    new ProcessPodcast($podcast1),
    new ProcessPodcast($podcast2),
    new ProcessPodcast($podcast3),
])
->then(function (Batch $batch) {
    // All jobs completed successfully
    Log::info('Batch completed', ['id' => $batch->id]);
})
->catch(function (Batch $batch, Throwable $e) {
    // First batch job failure
    Log::error('Batch failed', ['error' => $e->getMessage()]);
})
->finally(function (Batch $batch) {
    // Batch finished (success or failure)
    Notification::send($admin, new BatchComplete($batch));
})
->name('Process Podcasts')
->allowFailures()
->dispatch();

// Get batch ID
$batchId = $batch->id;
```

## Batch-aware Jobs

```php
use Illuminate\Bus\Batchable;

class ProcessPodcast implements ShouldQueue
{
    use Batchable, Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function handle(): void
    {
        // Check if batch was cancelled
        if ($this->batch()->cancelled()) {
            return;
        }

        // Process podcast...

        // Add more jobs to batch
        $this->batch()->add([
            new TranscribePodcast($this->podcast),
        ]);
    }
}
```

## Track Batch Progress

```php
// Retrieve batch
$batch = Bus::findBatch($batchId);

// Progress information
$batch->id;
$batch->name;
$batch->totalJobs;
$batch->pendingJobs;
$batch->failedJobs;
$batch->processedJobs();
$batch->progress(); // Percentage complete
$batch->finished();
$batch->cancelled();

// Cancel batch
$batch->cancel();

// In controller
public function batchStatus(string $batchId)
{
    $batch = Bus::findBatch($batchId);

    return response()->json([
        'id' => $batch->id,
        'progress' => $batch->progress(),
        'pending' => $batch->pendingJobs,
        'failed' => $batch->failedJobs,
        'finished' => $batch->finished(),
    ]);
}
```

## Batch Options

```php
$batch = Bus::batch($jobs)
    ->name('Import Users')
    ->onQueue('imports')
    ->onConnection('redis')
    ->allowFailures() // Continue despite failures
    ->dispatch();
```

## Nested Batches

```php
$batch = Bus::batch([
    [
        new ProcessFile($file1),
        new ProcessFile($file2),
    ],
    new NotifyUser($user),
])
->dispatch();

// Jobs in nested array run in parallel
// NotifyUser runs after all ProcessFile jobs complete
```

## Real-World Example

```php
class ImportUsersController extends Controller
{
    public function import(Request $request)
    {
        $file = $request->file('csv');
        $rows = collect(/* parse CSV */);

        $jobs = $rows->chunk(100)->map(function ($chunk) {
            return new ImportUserChunk($chunk);
        })->all();

        $batch = Bus::batch($jobs)
            ->name('User Import')
            ->onQueue('imports')
            ->then(function (Batch $batch) use ($request) {
                Notification::send(
                    $request->user(),
                    new ImportComplete($batch)
                );
            })
            ->dispatch();

        return response()->json([
            'batch_id' => $batch->id,
            'total_jobs' => $batch->totalJobs,
        ]);
    }
}
```
