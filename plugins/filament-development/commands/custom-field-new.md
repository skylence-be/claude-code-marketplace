---
description: Create Filament 5 custom form field
model: claude-sonnet-4-5
---

Create a Filament 5 custom form field.

## Custom Field Specification

$ARGUMENTS

## Filament Custom Field Patterns

### 1. **Basic Custom Field**

```php
<?php

namespace App\Forms\Components;

use Filament\Forms\Components\Field;

class ColorPalette extends Field
{
    protected string $view = 'forms.components.color-palette';

    protected array $colors = [
        '#ef4444',
        '#f59e0b',
        '#10b981',
        '#3b82f6',
        '#6366f1',
        '#8b5cf6',
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

**Blade View** (resources/views/forms/components/color-palette.blade.php):

```blade
<x-dynamic-component
    :component="$getFieldWrapperView()"
    :field="$field"
>
    <div x-data="{ state: $wire.{{ $applyStateBindingModifiers("\$entangle('{$getStatePath()}')") }} }">
        <div class="grid grid-cols-6 gap-2">
            @foreach ($getColors() as $color)
                <button
                    type="button"
                    @click="state = '{{ $color }}'"
                    :class="{ 'ring-2 ring-primary-500': state === '{{ $color }}' }"
                    class="w-10 h-10 rounded-lg transition"
                    style="background-color: {{ $color }}"
                ></button>
            @endforeach
        </div>
    </div>
</x-dynamic-component>
```

### 2. **Field with JavaScript Integration**

```php
<?php

namespace App\Forms\Components;

use Filament\Forms\Components\Field;

class Signature extends Field
{
    protected string $view = 'forms.components.signature';

    protected string|null $backgroundColor = '#ffffff';

    protected string $penColor = '#000000';

    public function backgroundColor(string $color): static
    {
        $this->backgroundColor = $color;

        return $this;
    }

    public function penColor(string $color): static
    {
        $this->penColor = $color;

        return $this;
    }
}
```

Generate complete Filament 5 custom form field with view.
