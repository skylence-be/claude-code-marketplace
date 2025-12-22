# Bulk Operations

Filament 4 bulk actions with queue processing for large datasets.

## Standard Bulk Actions

```php
->bulkActions([
    Tables\Actions\BulkActionGroup::make([
        Tables\Actions\DeleteBulkAction::make(),
        Tables\Actions\RestoreBulkAction::make(),
        Tables\Actions\ForceDeleteBulkAction::make(),

        Tables\Actions\BulkAction::make('activate')
            ->label('Activate')
            ->icon('heroicon-o-check-circle')
            ->color('success')
            ->requiresConfirmation()
            ->action(fn (Collection $records) =>
                $records->each->update(['is_active' => true])
            )
            ->deselectRecordsAfterCompletion(),

        Tables\Actions\BulkAction::make('deactivate')
            ->label('Deactivate')
            ->icon('heroicon-o-x-circle')
            ->color('danger')
            ->requiresConfirmation()
            ->action(fn (Collection $records) =>
                $records->each->update(['is_active' => false])
            )
            ->deselectRecordsAfterCompletion(),
    ]),
])
```

## Bulk Action with Form

```php
Tables\Actions\BulkAction::make('update_prices')
    ->label('Update Prices')
    ->icon('heroicon-o-currency-dollar')
    ->form([
        Forms\Components\Select::make('action')
            ->options([
                'increase' => 'Increase',
                'decrease' => 'Decrease',
                'set' => 'Set to',
            ])
            ->required()
            ->reactive(),

        Forms\Components\TextInput::make('value')
            ->numeric()
            ->required()
            ->suffix(fn ($get) =>
                $get('action') === 'set' ? 'USD' : '%'
            ),
    ])
    ->action(function (Collection $records, array $data) {
        \DB::transaction(function () use ($records, $data) {
            foreach ($records as $record) {
                $newPrice = match ($data['action']) {
                    'increase' => $record->price * (1 + $data['value'] / 100),
                    'decrease' => $record->price * (1 - $data['value'] / 100),
                    'set' => $data['value'],
                };
                $record->update(['price' => round($newPrice, 2)]);
            }
        });

        Notification::make()
            ->success()
            ->title('Prices updated')
            ->body("{$records->count()} products updated")
            ->send();
    })
    ->deselectRecordsAfterCompletion(),
```

## Queued Bulk Action

```php
Tables\Actions\BulkAction::make('process_bulk')
    ->label('Process Selected')
    ->icon('heroicon-o-cog')
    ->action(function (Collection $records, array $data) {
        // Queue for large operations
        if ($records->count() > 100) {
            ProcessBulkRecordsJob::dispatch(
                $records->pluck('id')->toArray(),
                $data,
                auth()->id()
            );

            Notification::make()
                ->success()
                ->title('Processing queued')
                ->body('You will be notified when complete')
                ->send();
        } else {
            // Process immediately for small batches
            $records->chunk(50)->each(function ($chunk) use ($data) {
                foreach ($chunk as $record) {
                    // Process record
                }
            });

            Notification::make()
                ->success()
                ->title('Processing complete')
                ->send();
        }
    })
    ->deselectRecordsAfterCompletion(),
```

## Chunked Delete Action

```php
Tables\Actions\DeleteBulkAction::make()
    ->action(function (Collection $records) {
        // Process in chunks to avoid memory issues
        $records->chunk(100)->each(function ($chunk) {
            $chunk->each->delete();
        });

        Notification::make()
            ->success()
            ->title('Products deleted')
            ->body("{$records->count()} products have been deleted")
            ->send();
    }),
```

## Export Bulk Action

```php
Tables\Actions\BulkAction::make('export')
    ->label('Export Selected')
    ->icon('heroicon-o-arrow-down-tray')
    ->form([
        Forms\Components\Select::make('format')
            ->options([
                'csv' => 'CSV',
                'xlsx' => 'Excel',
                'json' => 'JSON',
            ])
            ->default('csv')
            ->required(),

        Forms\Components\CheckboxList::make('columns')
            ->options([
                'name' => 'Name',
                'sku' => 'SKU',
                'price' => 'Price',
                'stock' => 'Stock',
            ])
            ->default(['name', 'sku', 'price', 'stock'])
            ->required()
            ->columns(2),
    ])
    ->action(function (Collection $records, array $data) {
        $filename = 'export-' . now()->format('Y-m-d-His') . '.' . $data['format'];

        ExportRecordsJob::dispatch(
            $records->pluck('id')->toArray(),
            $data['columns'],
            $data['format'],
            auth()->id(),
            $filename
        );

        Notification::make()
            ->success()
            ->title('Export started')
            ->body('You will be notified when ready')
            ->send();
    })
    ->requiresConfirmation(),
```

## Bulk Email Action

```php
Tables\Actions\BulkAction::make('send_emails')
    ->icon('heroicon-o-envelope')
    ->form([
        Forms\Components\TextInput::make('subject')
            ->required(),
        Forms\Components\RichEditor::make('body')
            ->required(),
    ])
    ->action(function (Collection $records, array $data) {
        if ($records->count() > 50) {
            // Queue for large batches
            SendBulkEmailsJob::dispatch(
                $records->pluck('id')->toArray(),
                $data['subject'],
                $data['body'],
                auth()->id()
            );

            Notification::make()
                ->success()
                ->title('Emails queued')
                ->send();
        } else {
            // Send immediately
            foreach ($records as $record) {
                Mail::to($record->email)
                    ->send(new CustomEmail($data['subject'], $data['body']));
            }

            Notification::make()
                ->success()
                ->title("{$records->count()} emails sent")
                ->send();
        }
    })
    ->deselectRecordsAfterCompletion(),
```

## Table Options

```php
return $table
    ->bulkActions([...])
    // Select only current page for safety
    ->selectCurrentPageOnly()
    // Keep selection when filtering
    ->deselectAllRecordsWhenFiltered(false);
```
