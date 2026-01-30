---
description: Create Filament 5 resource with CRUD pages
model: claude-sonnet-4-5
---

Create a Filament 5 resource.

## Resource Specification

$ARGUMENTS

## Filament Resource Patterns

### 1. **Basic Resource**

```php
<?php

namespace App\Filament\Resources;

use App\Filament\Resources\PostResource\Pages;
use App\Models\Post;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class PostResource extends Resource
{
    protected static ?string $model = Post::class;

    protected static ?string $navigationIcon = 'heroicon-o-document-text';

    protected static ?string $navigationGroup = 'Content';

    protected static ?int $navigationSort = 1;

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('title')
                    ->required()
                    ->maxLength(255)
                    ->live(onBlur: true)
                    ->afterStateUpdated(fn ($state, Forms\Set $set) =>
                        $set('slug', Str::slug($state))
                    ),

                Forms\Components\TextInput::make('slug')
                    ->required()
                    ->maxLength(255)
                    ->unique(ignoreRecord: true),

                Forms\Components\Select::make('category_id')
                    ->relationship('category', 'name')
                    ->required()
                    ->searchable()
                    ->preload()
                    ->createOptionForm([
                        Forms\Components\TextInput::make('name')
                            ->required(),
                    ]),

                Forms\Components\RichEditor::make('content')
                    ->required()
                    ->columnSpanFull(),

                Forms\Components\Select::make('status')
                    ->options([
                        'draft' => 'Draft',
                        'published' => 'Published',
                        'archived' => 'Archived',
                    ])
                    ->required()
                    ->default('draft'),

                Forms\Components\DateTimePicker::make('published_at')
                    ->label('Publish Date'),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('title')
                    ->searchable()
                    ->sortable(),

                Tables\Columns\TextColumn::make('category.name')
                    ->sortable()
                    ->badge(),

                Tables\Columns\BadgeColumn::make('status')
                    ->colors([
                        'warning' => 'draft',
                        'success' => 'published',
                        'danger' => 'archived',
                    ]),

                Tables\Columns\TextColumn::make('published_at')
                    ->dateTime()
                    ->sortable(),

                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'draft' => 'Draft',
                        'published' => 'Published',
                        'archived' => 'Archived',
                    ]),

                Tables\Filters\SelectFilter::make('category')
                    ->relationship('category', 'name'),

                Tables\Filters\Filter::make('published_at')
                    ->form([
                        Forms\Components\DatePicker::make('published_from'),
                        Forms\Components\DatePicker::make('published_until'),
                    ])
                    ->query(function ($query, array $data) {
                        return $query
                            ->when($data['published_from'], fn ($q, $date) =>
                                $q->whereDate('published_at', '>=', $date)
                            )
                            ->when($data['published_until'], fn ($q, $date) =>
                                $q->whereDate('published_at', '<=', $date)
                            );
                    }),
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\BulkAction::make('publish')
                        ->icon('heroicon-o-check')
                        ->requiresConfirmation()
                        ->action(fn ($records) =>
                            $records->each->update(['status' => 'published'])
                        ),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListPosts::route('/'),
            'create' => Pages\CreatePost::route('/create'),
            'edit' => Pages\EditPost::route('/{record}/edit'),
        ];
    }
}
```

### 2. **Resource with Authorization**

```php
<?php

namespace App\Filament\Resources;

use App\Models\Post;
use Filament\Resources\Resource;
use Illuminate\Database\Eloquent\Builder;

class PostResource extends Resource
{
    protected static ?string $model = Post::class;

    public static function getEloquentQuery(): Builder
    {
        $query = parent::getEloquentQuery();

        // Filter by user if not admin
        if (!auth()->user()->isAdmin()) {
            $query->where('user_id', auth()->id());
        }

        return $query;
    }

    public static function canCreate(): bool
    {
        return auth()->user()->can('create', Post::class);
    }

    public static function canEdit(Model $record): bool
    {
        return auth()->user()->can('update', $record);
    }

    public static function canDelete(Model $record): bool
    {
        return auth()->user()->can('delete', $record);
    }

    public static function canViewAny(): bool
    {
        return auth()->user()->can('viewAny', Post::class);
    }
}
```

### 3. **Resource with Global Search**

```php
<?php

namespace App\Filament\Resources;

class PostResource extends Resource
{
    protected static ?string $recordTitleAttribute = 'title';

    public static function getGlobalSearchResultTitle(Model $record): string
    {
        return $record->title;
    }

    public static function getGloballySearchableAttributes(): array
    {
        return ['title', 'content', 'category.name'];
    }

    public static function getGlobalSearchResultDetails(Model $record): array
    {
        return [
            'Category' => $record->category?->name,
            'Author' => $record->user?->name,
        ];
    }

    public static function getGlobalSearchResultActions(Model $record): array
    {
        return [
            Action::make('edit')
                ->url(static::getUrl('edit', ['record' => $record])),
        ];
    }
}
```

Generate complete Filament 5 resource with form, table, and pages.
