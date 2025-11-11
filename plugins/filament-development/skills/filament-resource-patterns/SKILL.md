---
name: filament-resource-patterns
description: Master Filament 4 resource patterns including form schemas, table columns, filters, actions, relation managers, and multi-tenant resources. Use when building admin panels, CRUD interfaces, or data management systems.
category: filament
tags: [filament, resources, crud, admin-panel, forms, tables]
related_skills: [filament-forms-advanced, filament-tables-optimization, filament-multi-tenancy]
---

# Filament Resource Patterns

Comprehensive guide to implementing Filament 4 resources, covering resource structure, form schemas, table configurations, filters, actions, relation managers, global search, navigation customization, and multi-tenant resource patterns.

## When to Use This Skill

- Building comprehensive CRUD interfaces for Eloquent models
- Creating admin panels with complex form schemas and validation
- Implementing table views with filtering, sorting, and bulk actions
- Managing model relationships through relation managers
- Configuring global search across multiple resources
- Customizing resource navigation with groups, icons, and badges
- Building multi-tenant applications with tenant-aware resources
- Creating custom resource pages beyond default CRUD operations
- Implementing authorization and policy-based access control
- Designing data management interfaces with advanced form layouts

## Core Concepts

### 1. Resource Structure
- **Resource Class**: Central class defining forms, tables, and pages
- **Pages**: CreateRecord, EditRecord, ListRecords, ViewRecord
- **Forms**: Schema defining input fields and layout
- **Tables**: Columns, filters, actions for data display
- **Relations**: Managers for handling related models

### 2. Form Components
- **Text Inputs**: TextInput, Textarea, RichEditor, MarkdownEditor
- **Select Fields**: Select, CheckboxList, Radio, Toggle
- **Date/Time**: DatePicker, DateTimePicker, TimePicker
- **Files**: FileUpload with image processing
- **Repeater/Builder**: Dynamic repeating fields and content blocks

### 3. Table Components
- **Columns**: TextColumn, ImageColumn, IconColumn, BadgeColumn
- **Filters**: SelectFilter, DateFilter, TernaryFilter, custom filters
- **Actions**: Single row actions, bulk actions, header actions
- **Search**: Searchable columns and global search integration

### 4. Resource Features
- **Soft Deletes**: Restore and force delete functionality
- **Global Search**: Cross-resource search capabilities
- **Modal Forms**: Edit/create in modals vs full pages
- **Widgets**: Dashboard widgets from resource data

### 5. Multi-Tenancy
- **Tenant Context**: Scope queries to current tenant
- **Tenant Isolation**: Ensure data separation
- **Tenant Switching**: Handle multiple tenant contexts
- **Ownership**: Associate resources with tenants

## Quick Start

```php
<?php

namespace App\Filament\Resources;

use Filament\Resources\Resource;
use Filament\Forms;
use Filament\Tables;
use App\Models\Post;

class PostResource extends Resource
{
    protected static ?string $model = Post::class;
    protected static ?string $navigationIcon = 'heroicon-o-document-text';

    public static function form(Form $form): Form
    {
        return $form->schema([
            Forms\Components\TextInput::make('title')
                ->required()
                ->maxLength(255),
            Forms\Components\RichEditor::make('content')
                ->required(),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('title')->searchable(),
                Tables\Columns\TextColumn::make('created_at')->dateTime(),
            ])
            ->filters([
                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ]);
    }
}
```

## Fundamental Patterns

### Pattern 1: Complete Resource with HasPages

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use App\Models\Product;
use App\Filament\Resources\ProductResource\Pages;
use App\Filament\Resources\ProductResource\RelationManagers;

class ProductResource extends Resource
{
    protected static ?string $model = Product::class;

    protected static ?string $navigationIcon = 'heroicon-o-shopping-bag';

    protected static ?string $navigationGroup = 'Shop';

    protected static ?int $navigationSort = 1;

    protected static ?string $recordTitleAttribute = 'name';

    protected static int $globalSearchResultsLimit = 20;

    /**
     * Define the form schema for create and edit pages.
     */
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Product Information')
                    ->schema([
                        Forms\Components\TextInput::make('name')
                            ->required()
                            ->maxLength(255)
                            ->live(onBlur: true)
                            ->afterStateUpdated(fn ($state, callable $set) =>
                                $set('slug', \Illuminate\Support\Str::slug($state))
                            ),

                        Forms\Components\TextInput::make('slug')
                            ->required()
                            ->maxLength(255)
                            ->unique(ignoreRecord: true)
                            ->disabled()
                            ->dehydrated(),

                        Forms\Components\Select::make('category_id')
                            ->relationship('category', 'name')
                            ->required()
                            ->searchable()
                            ->preload()
                            ->createOptionForm([
                                Forms\Components\TextInput::make('name')
                                    ->required()
                                    ->maxLength(255),
                            ]),

                        Forms\Components\RichEditor::make('description')
                            ->required()
                            ->columnSpanFull()
                            ->toolbarButtons([
                                'bold',
                                'italic',
                                'link',
                                'bulletList',
                                'orderedList',
                            ]),
                    ])
                    ->columns(2),

                Forms\Components\Section::make('Pricing & Inventory')
                    ->schema([
                        Forms\Components\TextInput::make('price')
                            ->required()
                            ->numeric()
                            ->prefix('$')
                            ->minValue(0)
                            ->step(0.01),

                        Forms\Components\TextInput::make('cost')
                            ->numeric()
                            ->prefix('$')
                            ->minValue(0)
                            ->step(0.01),

                        Forms\Components\TextInput::make('stock')
                            ->required()
                            ->numeric()
                            ->minValue(0)
                            ->default(0),

                        Forms\Components\TextInput::make('sku')
                            ->label('SKU')
                            ->required()
                            ->unique(ignoreRecord: true)
                            ->maxLength(50),
                    ])
                    ->columns(2),

                Forms\Components\Section::make('Status')
                    ->schema([
                        Forms\Components\Toggle::make('is_active')
                            ->required()
                            ->default(true),

                        Forms\Components\Toggle::make('is_featured')
                            ->default(false),

                        Forms\Components\DateTimePicker::make('published_at')
                            ->default(now()),
                    ])
                    ->columns(3),

                Forms\Components\Section::make('Media')
                    ->schema([
                        Forms\Components\FileUpload::make('image')
                            ->image()
                            ->imageEditor()
                            ->imageEditorAspectRatios([
                                '16:9',
                                '4:3',
                                '1:1',
                            ])
                            ->directory('products')
                            ->maxSize(2048)
                            ->downloadable(),

                        Forms\Components\FileUpload::make('gallery')
                            ->multiple()
                            ->image()
                            ->reorderable()
                            ->maxFiles(5)
                            ->directory('products/gallery'),
                    ]),
            ]);
    }

    /**
     * Define the table schema for list page.
     */
    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\ImageColumn::make('image')
                    ->square()
                    ->size(60),

                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->sortable()
                    ->weight('bold')
                    ->description(fn (Product $record): string =>
                        \Illuminate\Support\Str::limit($record->description, 50)
                    ),

                Tables\Columns\TextColumn::make('category.name')
                    ->badge()
                    ->searchable()
                    ->sortable(),

                Tables\Columns\TextColumn::make('price')
                    ->money('usd')
                    ->sortable()
                    ->alignEnd(),

                Tables\Columns\TextColumn::make('stock')
                    ->badge()
                    ->color(fn (int $state): string => match (true) {
                        $state === 0 => 'danger',
                        $state < 10 => 'warning',
                        default => 'success',
                    })
                    ->alignCenter(),

                Tables\Columns\IconColumn::make('is_active')
                    ->boolean()
                    ->alignCenter(),

                Tables\Columns\IconColumn::make('is_featured')
                    ->boolean()
                    ->alignCenter(),

                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),

                Tables\Columns\TextColumn::make('updated_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('category')
                    ->relationship('category', 'name')
                    ->searchable()
                    ->preload(),

                Tables\Filters\TernaryFilter::make('is_active')
                    ->label('Active')
                    ->boolean()
                    ->trueLabel('Active products')
                    ->falseLabel('Inactive products')
                    ->native(false),

                Tables\Filters\TernaryFilter::make('is_featured')
                    ->label('Featured'),

                Tables\Filters\Filter::make('low_stock')
                    ->query(fn ($query) => $query->where('stock', '<', 10))
                    ->toggle(),

                Tables\Filters\Filter::make('created_at')
                    ->form([
                        Forms\Components\DatePicker::make('created_from'),
                        Forms\Components\DatePicker::make('created_until'),
                    ])
                    ->query(function ($query, array $data) {
                        return $query
                            ->when($data['created_from'],
                                fn ($q, $date) => $q->whereDate('created_at', '>=', $date)
                            )
                            ->when($data['created_until'],
                                fn ($q, $date) => $q->whereDate('created_at', '<=', $date)
                            );
                    }),

                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
                Tables\Actions\RestoreAction::make(),
                Tables\Actions\ForceDeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\RestoreBulkAction::make(),
                    Tables\Actions\ForceDeleteBulkAction::make(),

                    Tables\Actions\BulkAction::make('activate')
                        ->label('Activate')
                        ->icon('heroicon-o-check-circle')
                        ->requiresConfirmation()
                        ->action(fn ($records) =>
                            $records->each->update(['is_active' => true])
                        )
                        ->deselectRecordsAfterCompletion(),

                    Tables\Actions\BulkAction::make('deactivate')
                        ->label('Deactivate')
                        ->icon('heroicon-o-x-circle')
                        ->requiresConfirmation()
                        ->action(fn ($records) =>
                            $records->each->update(['is_active' => false])
                        )
                        ->deselectRecordsAfterCompletion(),
                ]),
            ])
            ->defaultSort('created_at', 'desc')
            ->poll('60s');
    }

    /**
     * Get relations for the resource.
     */
    public static function getRelations(): array
    {
        return [
            RelationManagers\ReviewsRelationManager::class,
            RelationManagers\VariantsRelationManager::class,
        ];
    }

    /**
     * Get pages for the resource.
     */
    public static function getPages(): array
    {
        return [
            'index' => Pages\ListProducts::route('/'),
            'create' => Pages\CreateProduct::route('/create'),
            'view' => Pages\ViewProduct::route('/{record}'),
            'edit' => Pages\EditProduct::route('/{record}/edit'),
        ];
    }

    /**
     * Configure global search.
     */
    public static function getGlobalSearchResultDetails(Model $record): array
    {
        return [
            'Category' => $record->category->name,
            'Price' => '$' . number_format($record->price, 2),
            'Stock' => $record->stock,
        ];
    }

    /**
     * Get Eloquent query for the resource.
     */
    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->withoutGlobalScopes([
                SoftDeletingScope::class,
            ]);
    }

    /**
     * Get navigation badge.
     */
    public static function getNavigationBadge(): ?string
    {
        return static::getModel()::where('stock', '<', 10)->count();
    }

    /**
     * Get navigation badge color.
     */
    public static function getNavigationBadgeColor(): ?string
    {
        return static::getNavigationBadge() > 0 ? 'warning' : 'success';
    }
}
```

### Pattern 2: Form Schema with Advanced Components

```php
<?php

namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;

class ArticleResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Tabs::make('Article')
                    ->tabs([
                        Forms\Components\Tabs\Tab::make('Content')
                            ->schema([
                                Forms\Components\TextInput::make('title')
                                    ->required()
                                    ->maxLength(255)
                                    ->live(onBlur: true)
                                    ->afterStateUpdated(function ($state, callable $set) {
                                        $set('slug', \Illuminate\Support\Str::slug($state));
                                    }),

                                Forms\Components\TextInput::make('slug')
                                    ->required()
                                    ->unique(ignoreRecord: true)
                                    ->maxLength(255),

                                Forms\Components\Select::make('author_id')
                                    ->relationship('author', 'name')
                                    ->required()
                                    ->searchable()
                                    ->preload(),

                                Forms\Components\Select::make('status')
                                    ->options([
                                        'draft' => 'Draft',
                                        'reviewing' => 'Under Review',
                                        'published' => 'Published',
                                        'archived' => 'Archived',
                                    ])
                                    ->default('draft')
                                    ->required()
                                    ->native(false),

                                Forms\Components\RichEditor::make('content')
                                    ->required()
                                    ->columnSpanFull()
                                    ->fileAttachmentsDisk('public')
                                    ->fileAttachmentsDirectory('articles/attachments')
                                    ->fileAttachmentsVisibility('public'),

                                Forms\Components\Textarea::make('excerpt')
                                    ->rows(3)
                                    ->columnSpanFull()
                                    ->maxLength(500),
                            ]),

                        Forms\Components\Tabs\Tab::make('Metadata')
                            ->schema([
                                Forms\Components\Select::make('categories')
                                    ->multiple()
                                    ->relationship('categories', 'name')
                                    ->preload()
                                    ->searchable()
                                    ->createOptionForm([
                                        Forms\Components\TextInput::make('name')
                                            ->required(),
                                        Forms\Components\TextInput::make('slug')
                                            ->required(),
                                    ]),

                                Forms\Components\TagsInput::make('tags')
                                    ->separator(',')
                                    ->suggestions([
                                        'news',
                                        'tutorial',
                                        'review',
                                        'opinion',
                                    ]),

                                Forms\Components\DateTimePicker::make('published_at')
                                    ->native(false)
                                    ->displayFormat('M d, Y H:i')
                                    ->seconds(false),

                                Forms\Components\Toggle::make('is_featured')
                                    ->label('Featured Article')
                                    ->helperText('Display on homepage'),

                                Forms\Components\Toggle::make('allow_comments')
                                    ->default(true),

                                Forms\Components\TextInput::make('reading_time')
                                    ->numeric()
                                    ->suffix('minutes')
                                    ->helperText('Estimated reading time'),
                            ]),

                        Forms\Components\Tabs\Tab::make('SEO')
                            ->schema([
                                Forms\Components\TextInput::make('meta_title')
                                    ->maxLength(60)
                                    ->helperText('Recommended: 50-60 characters'),

                                Forms\Components\Textarea::make('meta_description')
                                    ->rows(3)
                                    ->maxLength(160)
                                    ->helperText('Recommended: 150-160 characters'),

                                Forms\Components\TagsInput::make('meta_keywords')
                                    ->separator(','),

                                Forms\Components\TextInput::make('canonical_url')
                                    ->url()
                                    ->maxLength(255),

                                Forms\Components\Select::make('robots')
                                    ->options([
                                        'index,follow' => 'Index, Follow',
                                        'noindex,follow' => 'No Index, Follow',
                                        'index,nofollow' => 'Index, No Follow',
                                        'noindex,nofollow' => 'No Index, No Follow',
                                    ])
                                    ->default('index,follow'),
                            ]),

                        Forms\Components\Tabs\Tab::make('Media')
                            ->schema([
                                Forms\Components\FileUpload::make('featured_image')
                                    ->image()
                                    ->imageEditor()
                                    ->imageEditorAspectRatios([
                                        '16:9',
                                        '4:3',
                                    ])
                                    ->directory('articles/featured')
                                    ->maxSize(2048)
                                    ->downloadable()
                                    ->openable()
                                    ->columnSpanFull(),

                                Forms\Components\TextInput::make('featured_image_alt')
                                    ->label('Featured Image Alt Text')
                                    ->maxLength(255),

                                Forms\Components\TextInput::make('featured_image_caption')
                                    ->maxLength(255),
                            ]),
                    ])
                    ->columnSpanFull(),
            ]);
    }
}
```

### Pattern 3: Table Columns with Custom Rendering

```php
<?php

namespace App\Filament\Resources;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Resources\Resource;
use App\Models\Order;

class OrderResource extends Resource
{
    protected static ?string $model = Order::class;

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('number')
                    ->label('Order #')
                    ->searchable()
                    ->sortable()
                    ->copyable()
                    ->copyMessage('Order number copied')
                    ->copyMessageDuration(1500)
                    ->weight('bold'),

                Tables\Columns\TextColumn::make('customer.name')
                    ->searchable()
                    ->sortable()
                    ->url(fn (Order $record): string =>
                        route('filament.admin.resources.customers.view', $record->customer)
                    )
                    ->openUrlInNewTab()
                    ->description(fn (Order $record): string => $record->customer->email),

                Tables\Columns\BadgeColumn::make('status')
                    ->colors([
                        'secondary' => 'pending',
                        'warning' => 'processing',
                        'success' => 'completed',
                        'danger' => 'cancelled',
                    ])
                    ->icons([
                        'heroicon-o-clock' => 'pending',
                        'heroicon-o-arrow-path' => 'processing',
                        'heroicon-o-check-circle' => 'completed',
                        'heroicon-o-x-circle' => 'cancelled',
                    ])
                    ->sortable()
                    ->searchable(),

                Tables\Columns\TextColumn::make('items_count')
                    ->counts('items')
                    ->label('Items')
                    ->alignCenter()
                    ->badge()
                    ->color('info'),

                Tables\Columns\TextColumn::make('total')
                    ->money('usd')
                    ->sortable()
                    ->summarize([
                        Tables\Columns\Summarizers\Sum::make()
                            ->money('usd')
                            ->label('Total Revenue'),
                        Tables\Columns\Summarizers\Average::make()
                            ->money('usd')
                            ->label('Avg Order'),
                    ])
                    ->alignEnd(),

                Tables\Columns\TextColumn::make('payment_status')
                    ->badge()
                    ->color(fn (string $state): string => match ($state) {
                        'paid' => 'success',
                        'pending' => 'warning',
                        'failed' => 'danger',
                        'refunded' => 'gray',
                        default => 'secondary',
                    })
                    ->formatStateUsing(fn (string $state): string =>
                        ucfirst($state)
                    )
                    ->sortable(),

                Tables\Columns\IconColumn::make('is_gift')
                    ->boolean()
                    ->label('Gift')
                    ->alignCenter()
                    ->toggleable(),

                Tables\Columns\TextColumn::make('shipping_method')
                    ->badge()
                    ->color('gray')
                    ->toggleable(isToggledHiddenByDefault: true),

                Tables\Columns\TextColumn::make('created_at')
                    ->label('Order Date')
                    ->dateTime()
                    ->sortable()
                    ->since()
                    ->description(fn (Order $record): string =>
                        $record->created_at->format('M d, Y g:i A')
                    ),

                Tables\Columns\ViewColumn::make('items')
                    ->view('filament.tables.columns.order-items')
                    ->toggleable(isToggledHiddenByDefault: true),

                Tables\Columns\Layout\Stack::make([
                    Tables\Columns\ImageColumn::make('customer.avatar')
                        ->circular()
                        ->size(40),
                    Tables\Columns\TextColumn::make('customer.name')
                        ->weight('bold'),
                    Tables\Columns\TextColumn::make('total')
                        ->money('usd'),
                ])
                    ->space(2)
                    ->visibleFrom('md'),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'pending' => 'Pending',
                        'processing' => 'Processing',
                        'completed' => 'Completed',
                        'cancelled' => 'Cancelled',
                    ])
                    ->multiple(),

                Tables\Filters\SelectFilter::make('payment_status')
                    ->options([
                        'paid' => 'Paid',
                        'pending' => 'Pending',
                        'failed' => 'Failed',
                        'refunded' => 'Refunded',
                    ])
                    ->multiple(),

                Tables\Filters\Filter::make('total')
                    ->form([
                        Forms\Components\TextInput::make('total_from')
                            ->numeric()
                            ->prefix('$'),
                        Forms\Components\TextInput::make('total_to')
                            ->numeric()
                            ->prefix('$'),
                    ])
                    ->query(function ($query, array $data) {
                        return $query
                            ->when($data['total_from'],
                                fn ($q, $value) => $q->where('total', '>=', $value)
                            )
                            ->when($data['total_to'],
                                fn ($q, $value) => $q->where('total', '<=', $value)
                            );
                    }),

                Tables\Filters\TernaryFilter::make('is_gift'),

                Tables\Filters\Filter::make('created_at')
                    ->form([
                        Forms\Components\DatePicker::make('created_from')
                            ->native(false),
                        Forms\Components\DatePicker::make('created_until')
                            ->native(false),
                    ])
                    ->query(function ($query, array $data) {
                        return $query
                            ->when($data['created_from'],
                                fn ($q, $date) => $q->whereDate('created_at', '>=', $date)
                            )
                            ->when($data['created_until'],
                                fn ($q, $date) => $q->whereDate('created_at', '<=', $date)
                            );
                    })
                    ->indicateUsing(function (array $data): array {
                        $indicators = [];

                        if ($data['created_from'] ?? null) {
                            $indicators[] = 'From ' . Carbon::parse($data['created_from'])->toFormattedDateString();
                        }

                        if ($data['created_until'] ?? null) {
                            $indicators[] = 'Until ' . Carbon::parse($data['created_until'])->toFormattedDateString();
                        }

                        return $indicators;
                    }),
            ])
            ->filtersLayout(Tables\Enums\FiltersLayout::AboveContent)
            ->persistFiltersInSession()
            ->deselectAllRecordsWhenFiltered(false);
    }
}
```

### Pattern 4: Actions and Bulk Actions

```php
<?php

namespace App\Filament\Resources;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Resources\Resource;
use Filament\Notifications\Notification;
use App\Models\Invoice;

class InvoiceResource extends Resource
{
    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                // ... columns here
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make()
                    ->label('New Invoice')
                    ->icon('heroicon-o-plus'),

                Tables\Actions\Action::make('import')
                    ->label('Import')
                    ->icon('heroicon-o-arrow-up-tray')
                    ->form([
                        Forms\Components\FileUpload::make('file')
                            ->required()
                            ->acceptedFileTypes(['text/csv', 'application/vnd.ms-excel']),
                    ])
                    ->action(function (array $data) {
                        // Handle import
                    }),

                Tables\Actions\Action::make('export')
                    ->label('Export')
                    ->icon('heroicon-o-arrow-down-tray')
                    ->action(function () {
                        // Handle export
                        return response()->download(storage_path('app/invoices.csv'));
                    }),
            ])
            ->actions([
                Tables\Actions\ActionGroup::make([
                    Tables\Actions\ViewAction::make(),

                    Tables\Actions\EditAction::make(),

                    Tables\Actions\Action::make('send')
                        ->icon('heroicon-o-envelope')
                        ->requiresConfirmation()
                        ->action(function (Invoice $record) {
                            // Send invoice email
                            \Mail::to($record->customer->email)->send(new InvoiceMail($record));

                            Notification::make()
                                ->success()
                                ->title('Invoice sent')
                                ->body("Invoice #{$record->number} has been sent to {$record->customer->email}")
                                ->send();
                        }),

                    Tables\Actions\Action::make('download')
                        ->icon('heroicon-o-arrow-down-tray')
                        ->action(function (Invoice $record) {
                            return response()->download($record->pdf_path);
                        }),

                    Tables\Actions\Action::make('mark_as_paid')
                        ->icon('heroicon-o-check-circle')
                        ->color('success')
                        ->requiresConfirmation()
                        ->visible(fn (Invoice $record) => $record->status !== 'paid')
                        ->form([
                            Forms\Components\DatePicker::make('paid_at')
                                ->label('Payment Date')
                                ->required()
                                ->default(now())
                                ->native(false),
                            Forms\Components\Select::make('payment_method')
                                ->options([
                                    'bank_transfer' => 'Bank Transfer',
                                    'credit_card' => 'Credit Card',
                                    'cash' => 'Cash',
                                    'check' => 'Check',
                                ])
                                ->required(),
                        ])
                        ->action(function (Invoice $record, array $data) {
                            $record->update([
                                'status' => 'paid',
                                'paid_at' => $data['paid_at'],
                                'payment_method' => $data['payment_method'],
                            ]);

                            Notification::make()
                                ->success()
                                ->title('Invoice marked as paid')
                                ->send();
                        }),

                    Tables\Actions\Action::make('duplicate')
                        ->icon('heroicon-o-document-duplicate')
                        ->requiresConfirmation()
                        ->action(function (Invoice $record) {
                            $newInvoice = $record->replicate();
                            $newInvoice->number = Invoice::generateNumber();
                            $newInvoice->status = 'draft';
                            $newInvoice->save();

                            // Copy invoice items
                            $record->items->each(function ($item) use ($newInvoice) {
                                $newInvoice->items()->create($item->only([
                                    'description',
                                    'quantity',
                                    'unit_price',
                                    'tax_rate',
                                ]));
                            });

                            Notification::make()
                                ->success()
                                ->title('Invoice duplicated')
                                ->body("New invoice #{$newInvoice->number} created")
                                ->send();
                        }),

                    Tables\Actions\DeleteAction::make(),
                ])
                    ->label('Actions')
                    ->icon('heroicon-m-ellipsis-vertical')
                    ->size('sm')
                    ->color('primary')
                    ->button(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),

                    Tables\Actions\BulkAction::make('send_bulk')
                        ->label('Send Invoices')
                        ->icon('heroicon-o-envelope')
                        ->requiresConfirmation()
                        ->deselectRecordsAfterCompletion()
                        ->action(function ($records) {
                            $sent = 0;
                            foreach ($records as $record) {
                                \Mail::to($record->customer->email)->send(new InvoiceMail($record));
                                $sent++;
                            }

                            Notification::make()
                                ->success()
                                ->title("{$sent} invoices sent")
                                ->send();
                        }),

                    Tables\Actions\BulkAction::make('mark_as_paid_bulk')
                        ->label('Mark as Paid')
                        ->icon('heroicon-o-check-circle')
                        ->color('success')
                        ->requiresConfirmation()
                        ->deselectRecordsAfterCompletion()
                        ->action(function ($records) {
                            $records->each->update([
                                'status' => 'paid',
                                'paid_at' => now(),
                            ]);

                            Notification::make()
                                ->success()
                                ->title('Invoices marked as paid')
                                ->send();
                        }),

                    Tables\Actions\BulkAction::make('export_bulk')
                        ->label('Export Selected')
                        ->icon('heroicon-o-arrow-down-tray')
                        ->action(function ($records) {
                            // Generate CSV or PDF
                            return response()->download(
                                InvoiceExporter::export($records),
                                'invoices-' . now()->format('Y-m-d') . '.pdf'
                            );
                        }),

                    Tables\Actions\BulkAction::make('change_status')
                        ->label('Change Status')
                        ->icon('heroicon-o-arrows-right-left')
                        ->form([
                            Forms\Components\Select::make('status')
                                ->options([
                                    'draft' => 'Draft',
                                    'sent' => 'Sent',
                                    'paid' => 'Paid',
                                    'overdue' => 'Overdue',
                                    'cancelled' => 'Cancelled',
                                ])
                                ->required(),
                        ])
                        ->action(function ($records, array $data) {
                            $records->each->update(['status' => $data['status']]);

                            Notification::make()
                                ->success()
                                ->title('Status updated')
                                ->send();
                        })
                        ->deselectRecordsAfterCompletion(),
                ]),
            ])
            ->recordAction(null)
            ->recordUrl(null);
    }
}
```

### Pattern 5: Relation Managers

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

                Forms\Components\Textarea::make('comment')
                    ->required()
                    ->rows(4)
                    ->columnSpanFull(),

                Forms\Components\Select::make('rating')
                    ->options([
                        1 => '1 Star',
                        2 => '2 Stars',
                        3 => '3 Stars',
                        4 => '4 Stars',
                        5 => '5 Stars',
                    ])
                    ->required()
                    ->native(false),

                Forms\Components\Toggle::make('is_approved')
                    ->label('Approved')
                    ->default(false),

                Forms\Components\DateTimePicker::make('approved_at')
                    ->label('Approval Date')
                    ->native(false)
                    ->visible(fn ($get) => $get('is_approved')),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('title')
            ->columns([
                Tables\Columns\TextColumn::make('user.name')
                    ->label('Reviewer')
                    ->searchable()
                    ->sortable(),

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
                    ->formatStateUsing(fn (int $state): string =>
                        str_repeat('⭐', $state)
                    )
                    ->sortable(),

                Tables\Columns\IconColumn::make('is_approved')
                    ->boolean()
                    ->sortable(),

                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->since(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('rating')
                    ->options([
                        5 => '5 Stars',
                        4 => '4 Stars',
                        3 => '3 Stars',
                        2 => '2 Stars',
                        1 => '1 Star',
                    ]),

                Tables\Filters\TernaryFilter::make('is_approved')
                    ->label('Approval Status')
                    ->placeholder('All reviews')
                    ->trueLabel('Approved reviews')
                    ->falseLabel('Pending reviews'),
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make(),

                Tables\Actions\Action::make('approve_all')
                    ->label('Approve All Pending')
                    ->icon('heroicon-o-check-circle')
                    ->requiresConfirmation()
                    ->action(function (RelationManager $livewire) {
                        $livewire->getRelationship()
                            ->where('is_approved', false)
                            ->update([
                                'is_approved' => true,
                                'approved_at' => now(),
                            ]);

                        Notification::make()
                            ->success()
                            ->title('All reviews approved')
                            ->send();
                    }),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),

                Tables\Actions\Action::make('approve')
                    ->icon('heroicon-o-check-circle')
                    ->color('success')
                    ->requiresConfirmation()
                    ->visible(fn ($record) => !$record->is_approved)
                    ->action(function ($record) {
                        $record->update([
                            'is_approved' => true,
                            'approved_at' => now(),
                        ]);

                        Notification::make()
                            ->success()
                            ->title('Review approved')
                            ->send();
                    }),

                Tables\Actions\Action::make('reject')
                    ->icon('heroicon-o-x-circle')
                    ->color('danger')
                    ->requiresConfirmation()
                    ->visible(fn ($record) => $record->is_approved)
                    ->action(function ($record) {
                        $record->update([
                            'is_approved' => false,
                            'approved_at' => null,
                        ]);

                        Notification::make()
                            ->success()
                            ->title('Review rejected')
                            ->send();
                    }),

                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),

                    Tables\Actions\BulkAction::make('approve')
                        ->label('Approve')
                        ->icon('heroicon-o-check-circle')
                        ->requiresConfirmation()
                        ->action(function ($records) {
                            $records->each->update([
                                'is_approved' => true,
                                'approved_at' => now(),
                            ]);
                        })
                        ->deselectRecordsAfterCompletion(),

                    Tables\Actions\BulkAction::make('reject')
                        ->label('Reject')
                        ->icon('heroicon-o-x-circle')
                        ->color('danger')
                        ->requiresConfirmation()
                        ->action(function ($records) {
                            $records->each->update([
                                'is_approved' => false,
                                'approved_at' => null,
                            ]);
                        })
                        ->deselectRecordsAfterCompletion(),
                ]),
            ])
            ->modifyQueryUsing(fn ($query) => $query->withCount('helpfulVotes'))
            ->defaultSort('created_at', 'desc');
    }
}
```

### Pattern 6: Many-to-Many Relation Manager with Pivot Data

```php
<?php

namespace App\Filament\Resources\ProjectResource\RelationManagers;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Tables;
use Filament\Tables\Table;

class TeamMembersRelationManager extends RelationManager
{
    protected static string $relationship = 'teamMembers';

    protected static ?string $recordTitleAttribute = 'name';

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('user_id')
                    ->label('Team Member')
                    ->relationship('user', 'name')
                    ->required()
                    ->searchable()
                    ->preload()
                    ->createOptionForm([
                        Forms\Components\TextInput::make('name')
                            ->required(),
                        Forms\Components\TextInput::make('email')
                            ->email()
                            ->required(),
                    ]),

                Forms\Components\Select::make('role')
                    ->options([
                        'owner' => 'Owner',
                        'admin' => 'Admin',
                        'member' => 'Member',
                        'viewer' => 'Viewer',
                    ])
                    ->required()
                    ->default('member')
                    ->native(false),

                Forms\Components\DatePicker::make('joined_at')
                    ->label('Join Date')
                    ->required()
                    ->default(now())
                    ->native(false),

                Forms\Components\TextInput::make('hourly_rate')
                    ->numeric()
                    ->prefix('$')
                    ->step(0.01)
                    ->minValue(0),

                Forms\Components\Toggle::make('can_manage_tasks')
                    ->label('Can Manage Tasks')
                    ->default(false),

                Forms\Components\Toggle::make('can_invite_members')
                    ->label('Can Invite Members')
                    ->default(false),

                Forms\Components\Textarea::make('notes')
                    ->rows(3)
                    ->columnSpanFull(),
            ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->recordTitleAttribute('name')
            ->columns([
                Tables\Columns\ImageColumn::make('avatar')
                    ->circular()
                    ->size(40),

                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->sortable()
                    ->description(fn ($record): string => $record->email),

                Tables\Columns\BadgeColumn::make('pivot.role')
                    ->label('Role')
                    ->colors([
                        'danger' => 'owner',
                        'warning' => 'admin',
                        'success' => 'member',
                        'secondary' => 'viewer',
                    ])
                    ->sortable(),

                Tables\Columns\TextColumn::make('pivot.joined_at')
                    ->label('Joined')
                    ->date()
                    ->sortable()
                    ->since(),

                Tables\Columns\TextColumn::make('pivot.hourly_rate')
                    ->label('Rate')
                    ->money('usd')
                    ->sortable(),

                Tables\Columns\IconColumn::make('pivot.can_manage_tasks')
                    ->label('Manage Tasks')
                    ->boolean()
                    ->alignCenter(),

                Tables\Columns\IconColumn::make('pivot.can_invite_members')
                    ->label('Invite Members')
                    ->boolean()
                    ->alignCenter(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('role')
                    ->options([
                        'owner' => 'Owner',
                        'admin' => 'Admin',
                        'member' => 'Member',
                        'viewer' => 'Viewer',
                    ]),
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
                        Forms\Components\DatePicker::make('joined_at')
                            ->required()
                            ->default(now()),
                        Forms\Components\TextInput::make('hourly_rate')
                            ->numeric()
                            ->prefix('$'),
                    ])
                    ->preloadRecordSelect(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DetachAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DetachBulkAction::make(),

                    Tables\Actions\BulkAction::make('change_role')
                        ->label('Change Role')
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
                ]),
            ]);
    }
}
```

## Advanced Patterns

### Pattern 7: Multi-Tenant Resources

```php
<?php

namespace App\Filament\Resources;

use Filament\Facades\Filament;
use Filament\Resources\Resource;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use App\Models\Document;

class DocumentResource extends Resource
{
    protected static ?string $model = Document::class;

    protected static ?string $tenantOwnershipRelationshipName = 'team';

    /**
     * Scope resource to current tenant.
     */
    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->whereBelongsTo(Filament::getTenant());
    }

    /**
     * Associate new records with current tenant.
     */
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Hidden::make('team_id')
                    ->default(fn () => Filament::getTenant()->id),

                Forms\Components\TextInput::make('title')
                    ->required()
                    ->maxLength(255),

                Forms\Components\Select::make('folder_id')
                    ->relationship(
                        'folder',
                        'name',
                        fn (Builder $query) => $query->whereBelongsTo(Filament::getTenant())
                    )
                    ->searchable()
                    ->preload(),

                // ... other fields
            ]);
    }

    /**
     * Filter available records by tenant.
     */
    public static function canAccess(): bool
    {
        return Filament::getTenant() !== null;
    }

    /**
     * Check if user can view any records.
     */
    public static function canViewAny(): bool
    {
        $tenant = Filament::getTenant();

        if (! $tenant) {
            return false;
        }

        return auth()->user()->can('viewAny', [static::getModel(), $tenant]);
    }

    /**
     * Check if user can create records.
     */
    public static function canCreate(): bool
    {
        $tenant = Filament::getTenant();

        if (! $tenant) {
            return false;
        }

        return auth()->user()->can('create', [static::getModel(), $tenant]);
    }

    /**
     * Check tenant ownership before operations.
     */
    public static function canEdit(Model $record): bool
    {
        $tenant = Filament::getTenant();

        return $record->team_id === $tenant->id
            && auth()->user()->can('update', [$record, $tenant]);
    }

    public static function canDelete(Model $record): bool
    {
        $tenant = Filament::getTenant();

        return $record->team_id === $tenant->id
            && auth()->user()->can('delete', [$record, $tenant]);
    }

    /**
     * Get navigation badge for current tenant.
     */
    public static function getNavigationBadge(): ?string
    {
        $tenant = Filament::getTenant();

        if (! $tenant) {
            return null;
        }

        return static::getModel()::whereBelongsTo($tenant)
            ->where('status', 'pending')
            ->count();
    }
}
```

### Pattern 8: Custom Resource Pages

```php
<?php

namespace App\Filament\Resources\ProductResource\Pages;

use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
use Filament\Resources\Components\Tab;
use Illuminate\Database\Eloquent\Builder;

class ListProducts extends ListRecords
{
    protected static string $resource = ProductResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }

    /**
     * Define custom tabs for filtering.
     */
    public function getTabs(): array
    {
        return [
            'all' => Tab::make('All Products')
                ->badge(fn () => Product::count()),

            'active' => Tab::make('Active')
                ->modifyQueryUsing(fn (Builder $query) =>
                    $query->where('is_active', true)
                )
                ->badge(fn () => Product::where('is_active', true)->count())
                ->badgeColor('success'),

            'inactive' => Tab::make('Inactive')
                ->modifyQueryUsing(fn (Builder $query) =>
                    $query->where('is_active', false)
                )
                ->badge(fn () => Product::where('is_active', false)->count())
                ->badgeColor('danger'),

            'low_stock' => Tab::make('Low Stock')
                ->modifyQueryUsing(fn (Builder $query) =>
                    $query->where('stock', '<', 10)
                )
                ->badge(fn () => Product::where('stock', '<', 10)->count())
                ->badgeColor('warning'),

            'featured' => Tab::make('Featured')
                ->modifyQueryUsing(fn (Builder $query) =>
                    $query->where('is_featured', true)
                )
                ->badge(fn () => Product::where('is_featured', true)->count())
                ->badgeColor('info'),
        ];
    }

    /**
     * Get header widgets.
     */
    protected function getHeaderWidgets(): array
    {
        return [
            ProductResource\Widgets\ProductStatsOverview::class,
        ];
    }

    /**
     * Get footer widgets.
     */
    protected function getFooterWidgets(): array
    {
        return [
            ProductResource\Widgets\ProductsChart::class,
        ];
    }
}
```

### Pattern 9: Global Search Configuration

```php
<?php

namespace App\Filament\Resources;

use Filament\GlobalSearch\GlobalSearchResult;
use Filament\Resources\Resource;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class CustomerResource extends Resource
{
    protected static ?string $model = Customer::class;

    /**
     * Attribute used as title in search results.
     */
    protected static ?string $recordTitleAttribute = 'name';

    /**
     * Define additional searchable columns.
     */
    public static function getGloballySearchableAttributes(): array
    {
        return ['name', 'email', 'phone', 'company'];
    }

    /**
     * Customize search result display.
     */
    public static function getGlobalSearchResultTitle(Model $record): string
    {
        return $record->name;
    }

    /**
     * Add details to search results.
     */
    public static function getGlobalSearchResultDetails(Model $record): array
    {
        return [
            'Email' => $record->email,
            'Company' => $record->company,
            'Orders' => $record->orders_count,
            'Total Spent' => '$' . number_format($record->total_spent, 2),
        ];
    }

    /**
     * Customize search result URL.
     */
    public static function getGlobalSearchResultUrl(Model $record): string
    {
        return static::getUrl('view', ['record' => $record]);
    }

    /**
     * Add actions to search results.
     */
    public static function getGlobalSearchResultActions(Model $record): array
    {
        return [
            Action::make('edit')
                ->url(static::getUrl('edit', ['record' => $record])),
            Action::make('view_orders')
                ->url(OrderResource::getUrl('index', [
                    'tableFilters' => [
                        'customer_id' => ['value' => $record->id],
                    ],
                ])),
        ];
    }

    /**
     * Customize search query.
     */
    public static function getGlobalSearchEloquentQuery(): Builder
    {
        return parent::getGlobalSearchEloquentQuery()
            ->with(['orders'])
            ->withCount('orders')
            ->withSum('orders', 'total');
    }

    /**
     * Limit search results.
     */
    protected static int $globalSearchResultsLimit = 10;
}
```

### Pattern 10: Resource Navigation Customization

```php
<?php

namespace App\Filament\Resources;

use Filament\Resources\Resource;
use Filament\Navigation\NavigationItem;
use Filament\Navigation\NavigationGroup;

class InventoryResource extends Resource
{
    /**
     * Navigation icon.
     */
    protected static ?string $navigationIcon = 'heroicon-o-cube';

    /**
     * Navigation label.
     */
    protected static ?string $navigationLabel = 'Inventory';

    /**
     * Navigation group.
     */
    protected static ?string $navigationGroup = 'Warehouse';

    /**
     * Navigation sort order.
     */
    protected static ?int $navigationSort = 2;

    /**
     * Navigation badge.
     */
    public static function getNavigationBadge(): ?string
    {
        return static::getModel()::where('stock', '<', 10)->count();
    }

    /**
     * Navigation badge color.
     */
    public static function getNavigationBadgeColor(): ?string
    {
        $lowStockCount = static::getModel()::where('stock', '<', 10)->count();

        return match (true) {
            $lowStockCount > 50 => 'danger',
            $lowStockCount > 20 => 'warning',
            $lowStockCount > 0 => 'info',
            default => 'success',
        };
    }

    /**
     * Register additional navigation items.
     */
    public static function getNavigationItems(): array
    {
        return [
            NavigationItem::make(static::getNavigationLabel())
                ->group(static::getNavigationGroup())
                ->icon(static::getNavigationIcon())
                ->activeIcon('heroicon-s-cube')
                ->isActiveWhen(fn () => request()->routeIs(static::getRouteBaseName() . '.*'))
                ->badge(static::getNavigationBadge())
                ->badgeColor(static::getNavigationBadgeColor())
                ->sort(static::getNavigationSort())
                ->url(static::getUrl()),

            NavigationItem::make('Low Stock Alert')
                ->group(static::getNavigationGroup())
                ->icon('heroicon-o-exclamation-triangle')
                ->badge(fn () => static::getModel()::where('stock', '<', 10)->count())
                ->badgeColor('danger')
                ->url(static::getUrl('index', [
                    'tableFilters' => [
                        'low_stock' => ['isActive' => true],
                    ],
                ]))
                ->visible(fn () => static::getModel()::where('stock', '<', 10)->exists()),
        ];
    }

    /**
     * Determine if resource should appear in navigation.
     */
    public static function shouldRegisterNavigation(): bool
    {
        return auth()->user()->can('viewAny', static::getModel());
    }
}
```

## Testing Strategies

```php
<?php

namespace Tests\Feature\Filament\Resources;

use App\Filament\Resources\ProductResource;
use App\Models\Product;
use App\Models\User;
use Filament\Actions\DeleteAction;
use Livewire\Livewire;
use Tests\TestCase;

class ProductResourceTest extends TestCase
{
    public function test_can_render_list_page(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\ListProducts::class)
            ->assertSuccessful();
    }

    public function test_can_list_products(): void
    {
        $products = Product::factory()->count(10)->create();

        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\ListProducts::class)
            ->assertCanSeeTableRecords($products);
    }

    public function test_can_render_create_page(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->assertSuccessful();
    }

    public function test_can_create_product(): void
    {
        $this->actingAs(User::factory()->create());

        $newData = Product::factory()->make();

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->fillForm([
                'name' => $newData->name,
                'slug' => $newData->slug,
                'price' => $newData->price,
                'stock' => $newData->stock,
                'sku' => $newData->sku,
            ])
            ->call('create')
            ->assertHasNoFormErrors();

        $this->assertDatabaseHas(Product::class, [
            'name' => $newData->name,
            'slug' => $newData->slug,
        ]);
    }

    public function test_can_validate_product_input(): void
    {
        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\CreateProduct::class)
            ->fillForm([
                'name' => null,
            ])
            ->call('create')
            ->assertHasFormErrors(['name' => 'required']);
    }

    public function test_can_render_edit_page(): void
    {
        $this->actingAs(User::factory()->create());

        $product = Product::factory()->create();

        Livewire::test(ProductResource\Pages\EditProduct::class, [
            'record' => $product->getRouteKey(),
        ])
            ->assertSuccessful();
    }

    public function test_can_retrieve_data(): void
    {
        $this->actingAs(User::factory()->create());

        $product = Product::factory()->create();

        Livewire::test(ProductResource\Pages\EditProduct::class, [
            'record' => $product->getRouteKey(),
        ])
            ->assertFormSet([
                'name' => $product->name,
                'price' => $product->price,
            ]);
    }

    public function test_can_save_product(): void
    {
        $this->actingAs(User::factory()->create());

        $product = Product::factory()->create();
        $newData = Product::factory()->make();

        Livewire::test(ProductResource\Pages\EditProduct::class, [
            'record' => $product->getRouteKey(),
        ])
            ->fillForm([
                'name' => $newData->name,
                'price' => $newData->price,
            ])
            ->call('save')
            ->assertHasNoFormErrors();

        expect($product->refresh())
            ->name->toBe($newData->name)
            ->price->toBe($newData->price);
    }

    public function test_can_delete_product(): void
    {
        $this->actingAs(User::factory()->create());

        $product = Product::factory()->create();

        Livewire::test(ProductResource\Pages\EditProduct::class, [
            'record' => $product->getRouteKey(),
        ])
            ->callAction(DeleteAction::class);

        $this->assertModelMissing($product);
    }

    public function test_can_filter_products_by_category(): void
    {
        $category = Category::factory()->create();
        $products = Product::factory()->count(3)->create(['category_id' => $category->id]);
        $otherProducts = Product::factory()->count(2)->create();

        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\ListProducts::class)
            ->filterTable('category', $category->id)
            ->assertCanSeeTableRecords($products)
            ->assertCanNotSeeTableRecords($otherProducts);
    }

    public function test_can_search_products_by_name(): void
    {
        $products = Product::factory()->count(3)->create();
        $searchProduct = $products->first();

        $this->actingAs(User::factory()->create());

        Livewire::test(ProductResource\Pages\ListProducts::class)
            ->searchTable($searchProduct->name)
            ->assertCanSeeTableRecords([$searchProduct])
            ->assertCanNotSeeTableRecords($products->skip(1));
    }
}
```

## Common Pitfalls

### Pitfall 1: Forgetting to Eager Load Relationships

```php
// WRONG: N+1 query problem
public static function table(Table $table): Table
{
    return $table->columns([
        Tables\Columns\TextColumn::make('author.name'), // N+1
    ]);
}

// CORRECT: Eager load relationships
public static function getEloquentQuery(): Builder
{
    return parent::getEloquentQuery()->with('author');
}
```

### Pitfall 2: Not Using Dehydrated on Disabled Fields

```php
// WRONG: Disabled field won't save
Forms\Components\TextInput::make('slug')
    ->disabled(),

// CORRECT: Use dehydrated to save value
Forms\Components\TextInput::make('slug')
    ->disabled()
    ->dehydrated(),
```

### Pitfall 3: Incorrect Pivot Data Access

```php
// WRONG: Trying to access pivot data incorrectly
Tables\Columns\TextColumn::make('role'), // Won't work for pivot

// CORRECT: Use pivot prefix
Tables\Columns\TextColumn::make('pivot.role'),
```

## Best Practices

1. **Always eager load** relationships used in tables to prevent N+1 queries
2. **Use form sections** to organize complex forms into logical groups
3. **Implement global search** for better user experience across resources
4. **Add navigation badges** to show important counts or alerts
5. **Use computed properties** in table columns for dynamic values
6. **Implement authorization** with policies for all resource operations
7. **Configure proper validation** rules on all form inputs
8. **Use relation managers** for managing related models efficiently
9. **Customize search** with multiple searchable attributes
10. **Test all CRUD operations** thoroughly with Pest tests

## Resources

- **Filament Resources Documentation**: https://filamentphp.com/docs/panels/resources
- **Form Builder**: https://filamentphp.com/docs/forms/fields
- **Table Builder**: https://filamentphp.com/docs/tables/columns
- **Actions**: https://filamentphp.com/docs/actions/overview
- **Relation Managers**: https://filamentphp.com/docs/panels/resources/relation-managers
- **Global Search**: https://filamentphp.com/docs/panels/resources/global-search
