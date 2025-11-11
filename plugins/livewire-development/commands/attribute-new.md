---
description: Create Livewire 4 custom attribute
model: claude-sonnet-4-5
---

Create a Livewire 4 custom attribute.

## Attribute Specification

$ARGUMENTS

## Livewire Attribute Patterns

### 1. **Basic Custom Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class Uppercase extends LivewireAttribute
{
    public function update($value)
    {
        return strtoupper($value);
    }
}
```

### 2. **Validation Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class Sanitize extends LivewireAttribute
{
    public function __construct(
        public array $tags = []
    ) {}

    public function update($value)
    {
        if ($this->tags) {
            return strip_tags($value, $this->tags);
        }

        return strip_tags($value);
    }
}

// Usage in component:
// #[Sanitize(['<p>', '<br>'])]
// public string $content = '';
```

### 3. **Transformation Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class Trim extends LivewireAttribute
{
    public function update($value)
    {
        if (is_string($value)) {
            return trim($value);
        }

        return $value;
    }
}

// Usage:
// #[Trim]
// public string $username = '';
```

### 4. **Formatting Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class Currency extends LivewireAttribute
{
    public function __construct(
        public string $currency = 'USD',
        public int $decimals = 2
    ) {}

    public function dehydrate($value)
    {
        // Format for display
        return number_format((float) $value, $this->decimals);
    }

    public function hydrate($value)
    {
        // Parse back to number
        return (float) str_replace(',', '', $value);
    }
}

// Usage:
// #[Currency('EUR', 2)]
// public float $price = 0.00;
```

### 5. **Caching Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Illuminate\Support\Facades\Cache;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class Cached extends LivewireAttribute
{
    public function __construct(
        public int $seconds = 3600
    ) {}

    public function update($value)
    {
        $key = $this->getComponent()->getId() . '.' . $this->getName();

        Cache::put($key, $value, $this->seconds);

        return $value;
    }
}

// Usage:
// #[Cached(600)]
// public array $searchResults = [];
```

### 6. **Access Control Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Illuminate\Support\Facades\Gate;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class RequiresPermission extends LivewireAttribute
{
    public function __construct(
        public string $permission
    ) {}

    public function call($params)
    {
        if (!Gate::allows($this->permission)) {
            abort(403, 'Unauthorized action.');
        }

        return $params;
    }
}

// Usage on methods:
// #[RequiresPermission('edit-posts')]
// public function updatePost() { }
```

### 7. **Rate Limiting Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Illuminate\Support\Facades\RateLimiter;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class RateLimit extends LivewireAttribute
{
    public function __construct(
        public int $maxAttempts = 5,
        public int $decayMinutes = 1
    ) {}

    public function call($params)
    {
        $key = $this->getComponent()->getId() . '.' . $this->getName();

        if (RateLimiter::tooManyAttempts($key, $this->maxAttempts)) {
            throw new \Exception('Too many attempts. Please try again later.');
        }

        RateLimiter::hit($key, $this->decayMinutes * 60);

        return $params;
    }
}

// Usage:
// #[RateLimit(maxAttempts: 3, decayMinutes: 5)]
// public function sendMessage() { }
```

### 8. **Logging Attribute**

```php
<?php

namespace App\Livewire\Attributes;

use Attribute;
use Illuminate\Support\Facades\Log;
use Livewire\Features\SupportAttributes\Attribute as LivewireAttribute;

#[Attribute]
class LogActivity extends LivewireAttribute
{
    public function __construct(
        public string $action = ''
    ) {}

    public function call($params)
    {
        $action = $this->action ?: $this->getName();

        Log::info("Livewire action: {$action}", [
            'component' => get_class($this->getComponent()),
            'user' => auth()->id(),
            'params' => $params,
        ]);

        return $params;
    }
}

// Usage:
// #[LogActivity('deleted post')]
// public function delete() { }
```

## Best Practices
- Use attributes for cross-cutting concerns (validation, logging, etc.)
- Keep attribute logic simple and focused
- Consider performance impact of attributes
- Use constructor parameters for flexibility
- Implement both update() and dehydrate()/hydrate() when needed
- Handle edge cases and null values
- Test attributes thoroughly
- Document attribute behavior clearly

## Common Use Cases
- Data transformation (uppercase, trim, formatting)
- Input sanitization and validation
- Access control and authorization
- Rate limiting and throttling
- Caching and memoization
- Activity logging and auditing
- Type coercion and casting

Generate complete Livewire 4 custom attribute with proper structure.
