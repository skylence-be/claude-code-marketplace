---
description: Create Filament 4 custom panel theme
model: claude-sonnet-4-5
---

Create a Filament 4 custom theme.

## Theme Specification

$ARGUMENTS

## Filament Theme Patterns

### 1. **Custom Theme CSS** (resources/css/filament/admin/theme.css)

```css
@import '/vendor/filament/filament/resources/css/theme.css';

@config 'tailwind.config.js';

:root {
    --primary: 220 70% 50%;
    --gray-50: 220 20% 98%;
    --gray-100: 220 15% 95%;
    /* ... other color variables */
}

.dark {
    --primary: 220 70% 60%;
    /* ... dark mode colors */
}

/* Custom component styles */
.fi-header {
    @apply bg-gradient-to-r from-primary-500 to-primary-600;
}

.fi-sidebar {
    @apply shadow-xl;
}
```

### 2. **Tailwind Config** (tailwind.config.js)

```js
import preset from './vendor/filament/filament/tailwind.config.preset'

export default {
    presets: [preset],
    content: [
        './app/Filament/**/*.php',
        './resources/views/filament/**/*.blade.php',
        './vendor/filament/**/*.blade.php',
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#3b82f6',
                    600: '#2563eb',
                    700: '#1d4ed8',
                    800: '#1e40af',
                    900: '#1e3a8a',
                    950: '#172554',
                },
            },
        },
    },
}
```

### 3. **Register Theme in Panel**

```php
<?php

use Filament\Panel;

return Panel::make()
    ->id('admin')
    ->path('admin')
    ->viteTheme('resources/css/filament/admin/theme.css')
    ->colors([
        'primary' => Color::Blue,
    ])
    ->font('Inter');
```

Generate complete Filament 4 custom theme with Tailwind configuration.
