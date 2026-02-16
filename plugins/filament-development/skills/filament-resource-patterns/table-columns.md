# Table Columns

Filament 5 table column patterns and custom rendering.

## Text Columns

```php
Tables\Columns\TextColumn::make('name')
    ->searchable()
    ->sortable()
    ->weight(FontWeight::Bold)
    ->copyable()
    ->copyMessage('Copied!')
    ->limit(50)
    ->tooltip(fn (Model $record) => $record->name),

Tables\Columns\TextColumn::make('description')
    ->limit(100)
    ->wrap()
    ->html(),

Tables\Columns\TextColumn::make('email')
    ->searchable()
    ->icon('heroicon-o-envelope')
    ->iconPosition('before'),

Tables\Columns\TextColumn::make('price')
    ->money('usd')
    ->sortable()
    ->alignEnd()
    ->summarize([
        Tables\Columns\Summarizers\Sum::make()->money('usd'),
        Tables\Columns\Summarizers\Average::make()->money('usd'),
    ]),

Tables\Columns\TextColumn::make('created_at')
    ->dateTime()
    ->sortable()
    ->since()
    ->description(fn (Model $record) =>
        $record->created_at->format('M d, Y g:i A')
    ),
```

## Badge Columns

```php
Tables\Columns\TextColumn::make('status')
    ->badge()
    ->color(fn (string $state): string => match ($state) {
        'draft' => 'gray',
        'pending' => 'warning',
        'published' => 'success',
        'archived' => 'danger',
        default => 'secondary',
    })
    ->icon(fn (string $state): ?string => match ($state) {
        'draft' => 'heroicon-o-pencil',
        'pending' => 'heroicon-o-clock',
        'published' => 'heroicon-o-check-circle',
        'archived' => 'heroicon-o-archive-box',
        default => null,
    })
    ->formatStateUsing(fn (string $state) => ucfirst($state)),
```

## Relationship Columns

```php
// BelongsTo
Tables\Columns\TextColumn::make('author.name')
    ->searchable()
    ->sortable(),

// Count relationship
Tables\Columns\TextColumn::make('comments_count')
    ->counts('comments')
    ->label('Comments')
    ->badge()
    ->color('info'),

// Sum relationship
Tables\Columns\TextColumn::make('items_sum_total')
    ->sum('items', 'total')
    ->money('usd'),

// Custom relationship query
Tables\Columns\TextColumn::make('latest_order')
    ->state(fn (Model $record) =>
        $record->orders()->latest()->first()?->number ?? 'No orders'
    ),
```

## Icon Columns

```php
Tables\Columns\IconColumn::make('is_active')
    ->boolean()
    ->trueIcon('heroicon-o-check-circle')
    ->falseIcon('heroicon-o-x-circle')
    ->trueColor('success')
    ->falseColor('danger'),

Tables\Columns\IconColumn::make('status')
    ->icon(fn (string $state): string => match ($state) {
        'pending' => 'heroicon-o-clock',
        'approved' => 'heroicon-o-check',
        'rejected' => 'heroicon-o-x-mark',
        default => 'heroicon-o-question-mark-circle',
    })
    ->color(fn (string $state): string => match ($state) {
        'pending' => 'warning',
        'approved' => 'success',
        'rejected' => 'danger',
        default => 'gray',
    }),
```

## Image Columns

```php
Tables\Columns\ImageColumn::make('avatar')
    ->circular()
    ->size(40)
    ->defaultImageUrl(fn (Model $record) =>
        'https://ui-avatars.com/api/?name=' . urlencode($record->name)
    ),

Tables\Columns\ImageColumn::make('gallery')
    ->square()
    ->stacked()
    ->limit(3)
    ->limitedRemainingText(),
```

## Toggle Column

```php
Tables\Columns\ToggleColumn::make('is_active')
    ->label('Active')
    ->onColor('success')
    ->offColor('danger')
    ->afterStateUpdated(function (Model $record, $state) {
        activity()->performedOn($record)->log('Status changed');
        cache()->forget("product.{$record->id}");
    }),
```

## Computed State

```php
Tables\Columns\TextColumn::make('profit_margin')
    ->state(function (Model $record): float {
        if ($record->cost === 0) return 0;
        return (($record->price - $record->cost) / $record->price) * 100;
    })
    ->formatStateUsing(fn (float $state) => number_format($state, 1) . '%')
    ->color(fn (float $state): string => match (true) {
        $state < 20 => 'danger',
        $state < 40 => 'warning',
        default => 'success',
    })
    ->sortable(query: fn (Builder $query, string $direction) =>
        $query->orderByRaw('((price - cost) / price * 100) ' . $direction)
    ),

Tables\Columns\TextColumn::make('full_address')
    ->state(fn (Model $record) =>
        "{$record->city}, {$record->state} {$record->zip}"
    ),
```

## Column Layouts

```php
// Stack layout
Tables\Columns\Layout\Stack::make([
    Tables\Columns\TextColumn::make('name')
        ->weight(FontWeight::Bold),
    Tables\Columns\TextColumn::make('email')
        ->size('sm')
        ->color('gray'),
])
    ->space(1),

// Split layout
Tables\Columns\Layout\Split::make([
    Tables\Columns\ImageColumn::make('avatar')
        ->circular()
        ->grow(false),
    Tables\Columns\Layout\Stack::make([
        Tables\Columns\TextColumn::make('name'),
        Tables\Columns\TextColumn::make('role')
            ->badge(),
    ]),
]),

// Grid layout
Tables\Columns\Layout\Grid::make([
    Tables\Columns\TextColumn::make('title'),
    Tables\Columns\TextColumn::make('category'),
    Tables\Columns\TextColumn::make('price'),
])
    ->columns(3),
```

## Toggleable Columns

```php
Tables\Columns\TextColumn::make('id')
    ->toggleable(isToggledHiddenByDefault: true),

Tables\Columns\TextColumn::make('created_at')
    ->dateTime()
    ->toggleable(isToggledHiddenByDefault: true),

Tables\Columns\TextColumn::make('updated_at')
    ->dateTime()
    ->toggleable(isToggledHiddenByDefault: true),
```

## Custom View Column

```php
Tables\Columns\ViewColumn::make('progress')
    ->view('filament.tables.columns.progress-bar'),
```

```blade
{{-- resources/views/filament/tables/columns/progress-bar.blade.php --}}
<div class="w-full bg-gray-200 rounded-full h-2.5">
    <div class="bg-primary-600 h-2.5 rounded-full"
         style="width: {{ $getState() }}%">
    </div>
</div>
<span class="text-xs text-gray-500">{{ $getState() }}%</span>
```
