# Relation Managers

Filament 5 relation managers for managing related models.

## HasMany Relation Manager

```php
<?php

namespace App\Filament\Resources\ProductResource\RelationManagers;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Tables;
use Filament\Tables\Table;

class ReviewsRelationManager extends RelationManager
{
    protected static string $relationship = 'reviews';
    protected static ?string $recordTitleAttribute = 'title';

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('title')
                    ->required()
                    ->maxLength(255),

                Forms\Components\Textarea::make('content')
                    ->required()
                    ->rows(4)
                    ->columnSpanFull(),

                Forms\Components\Select::make('rating')
                    ->options([
                        5 => '5 Stars',
                        4 => '4 Stars',
                        3 => '3 Stars',
                        2 => '2 Stars',
                        1 => '1 Star',
                    ])
                    ->required(),

                Forms\Components\Toggle::make('is_approved')
                    ->default(false),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('title')
            ->columns([
                Tables\Columns\TextColumn::make('user.name')
                    ->label('Reviewer')
                    ->searchable(),

                Tables\Columns\TextColumn::make('title')
                    ->searchable()
                    ->limit(30),

                Tables\Columns\TextColumn::make('rating')
                    ->badge()
                    ->color(fn (int $state): string => match (true) {
                        $state >= 4 => 'success',
                        $state === 3 => 'warning',
                        default => 'danger',
                    })
                    ->formatStateUsing(fn (int $state) =>
                        str_repeat('⭐', $state)
                    ),

                Tables\Columns\IconColumn::make('is_approved')
                    ->boolean(),

                Tables\Columns\TextColumn::make('created_at')
                    ->since(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('rating')
                    ->options([5 => '5', 4 => '4', 3 => '3', 2 => '2', 1 => '1']),

                Tables\Filters\TernaryFilter::make('is_approved'),
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),

                Tables\Actions\Action::make('approve')
                    ->icon('heroicon-o-check-circle')
                    ->color('success')
                    ->visible(fn ($record) => !$record->is_approved)
                    ->action(fn ($record) => $record->update(['is_approved' => true])),

                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),

                    Tables\Actions\BulkAction::make('approve')
                        ->icon('heroicon-o-check-circle')
                        ->action(fn ($records) =>
                            $records->each->update(['is_approved' => true])
                        ),
                ]),
            ])
            ->defaultSort('created_at', 'desc');
    }
}
```

## BelongsToMany with Pivot

```php
<?php

namespace App\Filament\Resources\ProjectResource\RelationManagers;

use Filament\Forms;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Tables;
use Filament\Tables\Actions\AttachAction;

class MembersRelationManager extends RelationManager
{
    protected static string $relationship = 'members';
    protected static ?string $recordTitleAttribute = 'name';

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('role')
                    ->options([
                        'owner' => 'Owner',
                        'admin' => 'Admin',
                        'member' => 'Member',
                        'viewer' => 'Viewer',
                    ])
                    ->required(),

                Forms\Components\TextInput::make('hourly_rate')
                    ->numeric()
                    ->prefix('$'),

                Forms\Components\DatePicker::make('joined_at')
                    ->default(now()),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\ImageColumn::make('avatar')
                    ->circular(),

                Tables\Columns\TextColumn::make('name')
                    ->description(fn ($record) => $record->email),

                Tables\Columns\BadgeColumn::make('pivot.role')
                    ->label('Role')
                    ->colors([
                        'danger' => 'owner',
                        'warning' => 'admin',
                        'primary' => 'member',
                        'gray' => 'viewer',
                    ]),

                Tables\Columns\TextColumn::make('pivot.hourly_rate')
                    ->money('usd'),

                Tables\Columns\TextColumn::make('pivot.joined_at')
                    ->date()
                    ->since(),
            ])
            ->headerActions([
                Tables\Actions\AttachAction::make()
                    ->form(fn (AttachAction $action): array => [
                        $action->getRecordSelect(),

                        Forms\Components\Select::make('role')
                            ->options([
                                'admin' => 'Admin',
                                'member' => 'Member',
                                'viewer' => 'Viewer',
                            ])
                            ->required()
                            ->default('member'),

                        Forms\Components\TextInput::make('hourly_rate')
                            ->numeric()
                            ->prefix('$'),

                        Forms\Components\DatePicker::make('joined_at')
                            ->default(now()),
                    ])
                    ->preloadRecordSelect(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DetachAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\DetachBulkAction::make(),

                Tables\Actions\BulkAction::make('change_role')
                    ->form([
                        Forms\Components\Select::make('role')
                            ->options([
                                'admin' => 'Admin',
                                'member' => 'Member',
                                'viewer' => 'Viewer',
                            ])
                            ->required(),
                    ])
                    ->action(function ($records, array $data, RelationManager $livewire) {
                        foreach ($records as $record) {
                            $livewire->getRelationship()
                                ->updateExistingPivot($record->id, [
                                    'role' => $data['role'],
                                ]);
                        }
                    }),
            ]);
    }
}
```

## MorphMany Relation

```php
class CommentsRelationManager extends RelationManager
{
    protected static string $relationship = 'comments';

    public function table(Table $table): Table
    {
        return $table
            ->modifyQueryUsing(fn (Builder $query) =>
                $query->with('user')->latest()
            )
            ->columns([
                Tables\Columns\TextColumn::make('user.name'),
                Tables\Columns\TextColumn::make('body')->limit(50),
                Tables\Columns\TextColumn::make('created_at')->since(),
            ]);
    }
}
```

## Register in Resource

```php
// In Resource class
public static function getRelations(): array
{
    return [
        RelationManagers\ReviewsRelationManager::class,
        RelationManagers\MembersRelationManager::class,
        RelationManagers\CommentsRelationManager::class,
    ];
}
```

## Relation Manager Options

```php
class ItemsRelationManager extends RelationManager
{
    protected static string $relationship = 'items';

    // Custom title
    protected static ?string $title = 'Order Items';

    // Icon in tabs
    protected static ?string $icon = 'heroicon-o-shopping-cart';

    // Badge count
    protected static ?string $badge = null;

    public static function getBadge(Model $ownerRecord, string $pageClass): ?string
    {
        return $ownerRecord->items()->count();
    }

    // Modify base query
    protected function getTableQuery(): Builder
    {
        return parent::getTableQuery()->with('product');
    }

    // Check if can view
    public static function canViewForRecord(Model $ownerRecord, string $pageClass): bool
    {
        return $ownerRecord->status !== 'cancelled';
    }
}
```
