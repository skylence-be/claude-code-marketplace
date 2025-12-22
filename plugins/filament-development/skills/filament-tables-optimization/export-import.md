# Export & Import

Filament 4 queued export and import with progress tracking.

## Export Header Action

```php
protected function getHeaderActions(): array
{
    return [
        Actions\Action::make('export')
            ->label('Export')
            ->icon('heroicon-o-arrow-down-tray')
            ->form([
                Forms\Components\Select::make('format')
                    ->options([
                        'csv' => 'CSV',
                        'xlsx' => 'Excel (XLSX)',
                        'json' => 'JSON',
                    ])
                    ->default('xlsx')
                    ->required(),

                Forms\Components\CheckboxList::make('columns')
                    ->label('Columns to Export')
                    ->options([
                        'id' => 'ID',
                        'name' => 'Name',
                        'sku' => 'SKU',
                        'price' => 'Price',
                        'stock' => 'Stock',
                        'created_at' => 'Created Date',
                    ])
                    ->default(['name', 'sku', 'price', 'stock'])
                    ->required()
                    ->columns(3),

                Forms\Components\Toggle::make('apply_filters')
                    ->label('Apply Current Filters')
                    ->default(true),
            ])
            ->action(function (array $data, $livewire) {
                $query = static::getResource()::getEloquentQuery();

                // Apply filters if requested
                if ($data['apply_filters']) {
                    // Apply current table filters to query
                    foreach ($livewire->tableFilters as $filter => $value) {
                        if ($value) {
                            // Apply filter logic
                        }
                    }
                }

                $productIds = $query->pluck('id')->toArray();
                $filename = 'export-' . now()->format('Y-m-d-His') . '.' . $data['format'];

                ExportProductsJob::dispatch(
                    productIds: $productIds,
                    columns: $data['columns'],
                    format: $data['format'],
                    userId: auth()->id(),
                    filename: $filename
                );

                Notification::make()
                    ->success()
                    ->title('Export started')
                    ->body('You will be notified when ready')
                    ->persistent()
                    ->send();
            })
            ->modalWidth('2xl'),
    ];
}
```

## Export Job

```php
<?php

namespace App\Jobs;

use App\Models\Product;
use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Storage;
use Filament\Notifications\Notification;
use Filament\Notifications\Actions\Action;

class ExportProductsJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        public array $productIds,
        public array $columns,
        public string $format,
        public int $userId,
        public string $filename
    ) {}

    public function handle(): void
    {
        $products = Product::whereIn('id', $this->productIds)
            ->with(['category'])
            ->get();

        $data = [];
        $total = $products->count();
        $processed = 0;

        foreach ($products as $product) {
            $row = [];
            foreach ($this->columns as $column) {
                $row[$column] = match($column) {
                    'category' => $product->category?->name,
                    'is_active' => $product->is_active ? 'Active' : 'Inactive',
                    default => $product->$column,
                };
            }
            $data[] = $row;
            $processed++;

            // Update progress every 100 items
            if ($processed % 100 === 0) {
                $this->updateProgress($processed, $total);
            }
        }

        // Generate file
        $path = $this->generateFile($data);

        // Send notification
        $user = User::find($this->userId);

        Notification::make()
            ->success()
            ->title('Export completed')
            ->body("{$total} records exported.")
            ->actions([
                Action::make('download')
                    ->button()
                    ->url(Storage::url($path))
                    ->openUrlInNewTab(),
            ])
            ->persistent()
            ->sendToDatabase($user);
    }

    protected function generateFile(array $data): string
    {
        $path = "exports/{$this->filename}";

        switch ($this->format) {
            case 'csv':
                $csv = \League\Csv\Writer::createFromPath(
                    storage_path("app/public/{$path}"),
                    'w+'
                );
                if (count($data) > 0) {
                    $csv->insertOne(array_keys($data[0]));
                }
                $csv->insertAll($data);
                break;

            case 'xlsx':
                // Use Laravel Excel
                \Excel::store(new ProductsExport($data), "public/{$path}");
                break;

            case 'json':
                Storage::put("public/{$path}", json_encode($data, JSON_PRETTY_PRINT));
                break;
        }

        return "public/{$path}";
    }

    protected function updateProgress(int $processed, int $total): void
    {
        cache()->put(
            "export.{$this->userId}.progress",
            ['processed' => $processed, 'total' => $total],
            now()->addHour()
        );
    }
}
```

## Import Header Action

```php
Actions\Action::make('import')
    ->label('Import')
    ->icon('heroicon-o-arrow-up-tray')
    ->form([
        Forms\Components\FileUpload::make('file')
            ->label('Import File')
            ->required()
            ->acceptedFileTypes([
                'text/csv',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ])
            ->maxSize(10240) // 10MB
            ->directory('imports')
            ->helperText('Upload CSV or Excel file'),

        Forms\Components\Toggle::make('update_existing')
            ->label('Update Existing Records')
            ->helperText('Update if SKU already exists')
            ->default(true),

        Forms\Components\Select::make('duplicate_handling')
            ->label('Duplicate Handling')
            ->options([
                'skip' => 'Skip duplicates',
                'update' => 'Update duplicates',
                'error' => 'Report as error',
            ])
            ->default('update')
            ->required(),
    ])
    ->action(function (array $data) {
        $path = Storage::disk('local')->putFile('imports', $data['file']);

        ImportProductsJob::dispatch(
            filePath: $path,
            userId: auth()->id(),
            updateExisting: $data['update_existing'],
            duplicateHandling: $data['duplicate_handling']
        );

        Notification::make()
            ->success()
            ->title('Import started')
            ->body('You will be notified when complete')
            ->send();
    })
    ->modalWidth('lg'),
```

## Import Job

```php
<?php

namespace App\Jobs;

use App\Models\Product;
use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Filament\Notifications\Notification;

class ImportProductsJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $timeout = 3600; // 1 hour

    public function __construct(
        public string $filePath,
        public int $userId,
        public bool $updateExisting = true,
        public string $duplicateHandling = 'update'
    ) {}

    public function handle(): void
    {
        $rows = $this->readFile(Storage::disk('local')->path($this->filePath));

        $total = count($rows);
        $created = 0;
        $updated = 0;
        $skipped = 0;
        $errors = [];

        foreach ($rows as $index => $row) {
            $result = $this->processRow($row, $index + 2);

            match ($result['status']) {
                'created' => $created++,
                'updated' => $updated++,
                'skipped' => $skipped++,
                'error' => $errors[] = $result['message'],
            };

            // Update progress every 50 items
            if (($index + 1) % 50 === 0) {
                $this->updateProgress($index + 1, $total, $created, $updated, $skipped);
            }
        }

        // Send completion notification
        $this->sendCompletionNotification($created, $updated, $skipped, $errors);

        // Cleanup
        Storage::disk('local')->delete($this->filePath);
    }

    protected function processRow(array $row, int $lineNumber): array
    {
        $validator = Validator::make($row, [
            'sku' => 'required|string|max:50',
            'name' => 'required|string|max:255',
            'price' => 'required|numeric|min:0',
            'stock' => 'required|integer|min:0',
        ]);

        if ($validator->fails()) {
            return [
                'status' => 'error',
                'message' => "Line {$lineNumber}: " . implode(', ', $validator->errors()->all()),
            ];
        }

        $existing = Product::where('sku', $row['sku'])->first();

        if ($existing) {
            return match ($this->duplicateHandling) {
                'skip' => ['status' => 'skipped'],
                'error' => ['status' => 'error', 'message' => "Line {$lineNumber}: SKU exists"],
                'update' => tap(['status' => 'updated'], fn() => $existing->update($row)),
            };
        }

        Product::create($row);
        return ['status' => 'created'];
    }

    protected function readFile(string $path): array
    {
        $extension = pathinfo($path, PATHINFO_EXTENSION);

        if ($extension === 'csv') {
            $csv = \League\Csv\Reader::createFromPath($path, 'r');
            $csv->setHeaderOffset(0);
            return iterator_to_array($csv->getRecords());
        }

        // Excel file
        return \Excel::toArray(null, $path)[0];
    }

    protected function sendCompletionNotification(int $created, int $updated, int $skipped, array $errors): void
    {
        $user = User::find($this->userId);

        $notification = Notification::make()
            ->title('Import completed')
            ->body("Created: {$created}, Updated: {$updated}, Skipped: {$skipped}");

        if (count($errors) > 0) {
            $notification->warning()->body(
                $notification->getBody() . "\n" . count($errors) . " errors occurred."
            );
        } else {
            $notification->success();
        }

        $notification->sendToDatabase($user);
    }

    protected function updateProgress(int $processed, int $total, int $created, int $updated, int $skipped): void
    {
        cache()->put(
            "import.{$this->userId}.progress",
            compact('processed', 'total', 'created', 'updated', 'skipped'),
            now()->addHour()
        );
    }
}
```
