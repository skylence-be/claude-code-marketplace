# Actions & Bulk Actions

Filament 5 table actions and bulk action patterns.

## Row Actions

```php
->actions([
    Tables\Actions\ActionGroup::make([
        Tables\Actions\ViewAction::make(),
        Tables\Actions\EditAction::make(),

        Tables\Actions\Action::make('duplicate')
            ->icon('heroicon-o-document-duplicate')
            ->requiresConfirmation()
            ->action(function (Model $record) {
                $newRecord = $record->replicate();
                $newRecord->name .= ' (Copy)';
                $newRecord->save();

                Notification::make()
                    ->success()
                    ->title('Record duplicated')
                    ->send();
            }),

        Tables\Actions\Action::make('download')
            ->icon('heroicon-o-arrow-down-tray')
            ->action(fn (Model $record) =>
                response()->download($record->file_path)
            ),

        Tables\Actions\DeleteAction::make(),
        Tables\Actions\RestoreAction::make(),
        Tables\Actions\ForceDeleteAction::make(),
    ])
        ->label('Actions')
        ->icon('heroicon-m-ellipsis-vertical')
        ->button(),
])
```

## Actions with Forms

```php
Tables\Actions\Action::make('send_email')
    ->icon('heroicon-o-envelope')
    ->form([
        Forms\Components\TextInput::make('subject')
            ->required(),
        Forms\Components\RichEditor::make('body')
            ->required(),
        Forms\Components\Toggle::make('send_copy')
            ->label('Send me a copy'),
    ])
    ->action(function (Model $record, array $data) {
        Mail::to($record->email)
            ->send(new CustomEmail($data['subject'], $data['body']));

        if ($data['send_copy']) {
            Mail::to(auth()->user()->email)
                ->send(new CustomEmail($data['subject'], $data['body']));
        }

        Notification::make()
            ->success()
            ->title('Email sent')
            ->send();
    }),

Tables\Actions\Action::make('change_status')
    ->icon('heroicon-o-arrows-right-left')
    ->form([
        Forms\Components\Select::make('status')
            ->options([
                'pending' => 'Pending',
                'approved' => 'Approved',
                'rejected' => 'Rejected',
            ])
            ->required(),
        Forms\Components\Textarea::make('reason')
            ->required(fn (Get $get) => $get('status') === 'rejected'),
    ])
    ->action(function (Model $record, array $data) {
        $record->update([
            'status' => $data['status'],
            'status_reason' => $data['reason'] ?? null,
        ]);
    }),
```

## Conditional Actions

```php
Tables\Actions\Action::make('approve')
    ->icon('heroicon-o-check-circle')
    ->color('success')
    ->requiresConfirmation()
    ->visible(fn (Model $record) => $record->status === 'pending')
    ->action(fn (Model $record) => $record->update(['status' => 'approved'])),

Tables\Actions\Action::make('reject')
    ->icon('heroicon-o-x-circle')
    ->color('danger')
    ->requiresConfirmation()
    ->visible(fn (Model $record) => $record->status === 'pending')
    ->form([
        Forms\Components\Textarea::make('reason')
            ->required(),
    ])
    ->action(function (Model $record, array $data) {
        $record->update([
            'status' => 'rejected',
            'rejection_reason' => $data['reason'],
        ]);
    }),

Tables\Actions\Action::make('publish')
    ->icon('heroicon-o-globe-alt')
    ->visible(fn (Model $record) => $record->status === 'draft')
    ->disabled(fn (Model $record) => !$record->isReadyToPublish())
    ->action(fn (Model $record) => $record->publish()),
```

## Header Actions

```php
->headerActions([
    Tables\Actions\CreateAction::make(),

    Tables\Actions\Action::make('import')
        ->icon('heroicon-o-arrow-up-tray')
        ->form([
            Forms\Components\FileUpload::make('file')
                ->required()
                ->acceptedFileTypes(['text/csv']),
        ])
        ->action(function (array $data) {
            ImportJob::dispatch($data['file']);
            Notification::make()
                ->success()
                ->title('Import started')
                ->send();
        }),

    Tables\Actions\Action::make('export')
        ->icon('heroicon-o-arrow-down-tray')
        ->action(function () {
            return Excel::download(new ProductsExport, 'products.xlsx');
        }),
])
```

## Bulk Actions

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

        Tables\Actions\BulkAction::make('change_category')
            ->icon('heroicon-o-tag')
            ->form([
                Forms\Components\Select::make('category_id')
                    ->relationship('category', 'name')
                    ->required(),
            ])
            ->action(function (Collection $records, array $data) {
                $records->each->update(['category_id' => $data['category_id']]);
            })
            ->deselectRecordsAfterCompletion(),

        Tables\Actions\BulkAction::make('export_selected')
            ->icon('heroicon-o-arrow-down-tray')
            ->action(function (Collection $records) {
                return Excel::download(
                    new ProductsExport($records->pluck('id')),
                    'selected-products.xlsx'
                );
            }),
    ]),
])
```

## Bulk Actions with Queues

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
        // Dispatch to queue for large batches
        if ($records->count() > 50) {
            SendBulkEmailsJob::dispatch(
                $records->pluck('id')->toArray(),
                $data['subject'],
                $data['body'],
                auth()->id()
            );

            Notification::make()
                ->success()
                ->title('Emails queued')
                ->body('You will be notified when complete')
                ->send();
        } else {
            // Process immediately for small batches
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

## URL Actions

```php
Tables\Actions\Action::make('view_profile')
    ->icon('heroicon-o-user')
    ->url(fn (Model $record) => route('profile', $record))
    ->openUrlInNewTab(),

Tables\Actions\Action::make('external_link')
    ->icon('heroicon-o-arrow-top-right-on-square')
    ->url(fn (Model $record) => $record->external_url)
    ->openUrlInNewTab()
    ->visible(fn (Model $record) => filled($record->external_url)),
```
