---
description: Create Filament 4 custom table column
model: claude-sonnet-4-5
---

Create a Filament 4 custom table column.

## Custom Column Specification

$ARGUMENTS

## Filament Custom Column Patterns

### 1. **Basic Custom Column**

```php
<?php

namespace App\Tables\Columns;

use Filament\Tables\Columns\Column;

class StatusBadge extends Column
{
    protected string $view = 'tables.columns.status-badge';

    protected array $colors = [
        'success' => 'completed',
        'warning' => 'pending',
        'danger' => 'failed',
    ];

    public function colors(array $colors): static
    {
        $this->colors = $colors;

        return $this;
    }

    public function getColors(): array
    {
        return $this->colors;
    }
}
```

**Blade View** (resources/views/tables/columns/status-badge.blade.php):

```blade
<div class="px-4 py-3">
    @php
        $state = $getState();
        $colors = $getColors();
        $color = collect($colors)->first(fn ($value, $key) => $value === $state) ?? 'gray';

        $colorClasses = [
            'success' => 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
            'warning' => 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
            'danger' => 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
            'gray' => 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
        ];
    @endphp

    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {{ $colorClasses[$color] }}">
        {{ ucfirst($state) }}
    </span>
</div>
```

### 2. **Column with Actions**

```php
<?php

namespace App\Tables\Columns;

use Filament\Tables\Columns\Column;

class ImageWithPreview extends Column
{
    protected string $view = 'tables.columns.image-with-preview';

    protected ?int $width = 40;
    protected ?int $height = 40;

    public function size(int $width, int $height = null): static
    {
        $this->width = $width;
        $this->height = $height ?? $width;

        return $this;
    }
}
```

**Blade View**:

```blade
<div x-data="{ showModal: false }">
    <button
        type="button"
        @click="showModal = true"
        class="hover:opacity-75 transition"
    >
        <img
            src="{{ $getState() }}"
            alt="{{ $getRecord()->name }}"
            class="rounded-lg object-cover"
            style="width: {{ $width }}px; height: {{ $height }}px;"
        />
    </button>

    <div
        x-show="showModal"
        x-cloak
        @click.away="showModal = false"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    >
        <img
            src="{{ $getState() }}"
            alt="{{ $getRecord()->name }}"
            class="max-w-4xl max-h-screen rounded-lg"
        />
    </div>
</div>
```

Generate complete Filament 4 custom table column with view.
