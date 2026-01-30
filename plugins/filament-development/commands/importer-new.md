---
description: Create Filament 5 data importer
model: claude-sonnet-4-5
---

Create a Filament 5 importer.

## Importer Specification

$ARGUMENTS

## Filament Importer Patterns

### 1. **Basic Importer**

```php
<?php

namespace App\Filament\Imports;

use App\Models\User;
use Filament\Actions\Imports\ImportColumn;
use Filament\Actions\Imports\Importer;
use Filament\Actions\Imports\Models\Import;

class UserImporter extends Importer
{
    protected static ?string $model = User::class;

    public static function getColumns(): array
    {
        return [
            ImportColumn::make('name')
                ->requiredMapping()
                ->rules(['required', 'max:255']),

            ImportColumn::make('email')
                ->requiredMapping()
                ->rules(['required', 'email', 'unique:users,email']),

            ImportColumn::make('password')
                ->requiredMapping()
                ->rules(['required', 'min:8'])
                ->fillRecordUsing(function ($record, $state) {
                    $record->password = Hash::make($state);
                }),

            ImportColumn::make('role')
                ->rules(['in:admin,user,moderator'])
                ->default('user'),
        ];
    }

    public function resolveRecord(): ?User
    {
        return User::firstOrNew([
            'email' => $this->data['email'],
        ]);
    }

    public static function getCompletedNotificationBody(Import $import): string
    {
        $body = 'Your user import has completed and ' . number_format($import->successful_rows) . ' ' . str('row')->plural($import->successful_rows) . ' imported.';

        if ($failedRowsCount = $import->getFailedRowsCount()) {
            $body .= ' ' . number_format($failedRowsCount) . ' ' . str('row')->plural($failedRowsCount) . ' failed to import.';
        }

        return $body;
    }
}
```

### 2. **Importer with Relationships**

```php
<?php

namespace App\Filament\Imports;

use App\Models\Post;
use App\Models\Category;
use Filament\Actions\Imports\ImportColumn;
use Filament\Actions\Imports\Importer;

class PostImporter extends Importer
{
    protected static ?string $model = Post::class;

    public static function getColumns(): array
    {
        return [
            ImportColumn::make('title')
                ->requiredMapping()
                ->rules(['required', 'max:255']),

            ImportColumn::make('slug')
                ->rules(['required', 'unique:posts,slug']),

            ImportColumn::make('category')
                ->requiredMapping()
                ->relationship(resolveUsing: 'name')
                ->fillRecordUsing(function ($record, $state) {
                    $category = Category::firstOrCreate(['name' => $state]);
                    $record->category_id = $category->id;
                }),

            ImportColumn::make('content')
                ->requiredMapping()
                ->rules(['required']),

            ImportColumn::make('status')
                ->rules(['in:draft,published,archived'])
                ->default('draft'),

            ImportColumn::make('published_at')
                ->castStateUsing(function ($state) {
                    return \Carbon\Carbon::parse($state);
                }),
        ];
    }

    public function resolveRecord(): ?Post
    {
        return Post::firstOrNew([
            'slug' => $this->data['slug'],
        ]);
    }
}
```

Generate complete Filament 5 importer with validation.
