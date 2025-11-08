---
description: Create Laravel validation rule
model: claude-sonnet-4-5
---

Create a Laravel custom validation rule.

## Rule Specification

$ARGUMENTS

## Laravel Validation Rule Patterns

### 1. **Basic Validation Rule**

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class Uppercase implements ValidationRule
{
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        if (strtoupper($value) !== $value) {
            $fail('The :attribute must be uppercase.');
        }
    }
}
```

### 2. **Rule with Parameters**

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class MaxWords implements ValidationRule
{
    public function __construct(
        protected int $maxWords
    ) {}

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $wordCount = str_word_count($value);

        if ($wordCount > $this->maxWords) {
            $fail("The :attribute must not exceed {$this->maxWords} words.");
        }
    }
}

// Usage: 'description' => ['required', new MaxWords(100)]
```

### 3. **Rule with Database Check**

```php
<?php

namespace App\Rules;

use App\Models\User;
use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class UniqueUsername implements ValidationRule
{
    public function __construct(
        protected ?int $exceptUserId = null
    ) {}

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $query = User::where('username', $value);

        if ($this->exceptUserId) {
            $query->where('id', '!=', $this->exceptUserId);
        }

        if ($query->exists()) {
            $fail('The :attribute is already taken.');
        }
    }
}

// Usage: 'username' => ['required', new UniqueUsername($user->id)]
```

### 4. **Complex Validation Rule**

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\DataAwareRule;
use Illuminate\Contracts\Validation\ValidationRule;

class ValidPassword implements ValidationRule, DataAwareRule
{
    protected array $data = [];

    public function setData(array $data): static
    {
        $this->data = $data;
        return $this;
    }

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        // Minimum 8 characters
        if (strlen($value) < 8) {
            $fail('The :attribute must be at least 8 characters.');
            return;
        }

        // Must contain uppercase
        if (!preg_match('/[A-Z]/', $value)) {
            $fail('The :attribute must contain at least one uppercase letter.');
            return;
        }

        // Must contain lowercase
        if (!preg_match('/[a-z]/', $value)) {
            $fail('The :attribute must contain at least one lowercase letter.');
            return;
        }

        // Must contain number
        if (!preg_match('/[0-9]/', $value)) {
            $fail('The :attribute must contain at least one number.');
            return;
        }

        // Must contain special character
        if (!preg_match('/[^A-Za-z0-9]/', $value)) {
            $fail('The :attribute must contain at least one special character.');
            return;
        }

        // Cannot contain username
        if (isset($this->data['username']) &&
            str_contains(strtolower($value), strtolower($this->data['username']))) {
            $fail('The :attribute cannot contain your username.');
        }
    }
}
```

### 5. **Rule with External API Validation**

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Support\Facades\Http;

class ValidVatNumber implements ValidationRule
{
    public function __construct(
        protected string $countryCode
    ) {}

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        try {
            $response = Http::get('https://api.vat-api.com/validate', [
                'country' => $this->countryCode,
                'vat_number' => $value,
            ]);

            if (!$response->successful() || !$response->json('valid')) {
                $fail('The :attribute is not a valid VAT number.');
            }
        } catch (\Exception $e) {
            $fail('Unable to validate VAT number at this time.');
        }
    }
}
```

### 6. **Invokable Rule (Alternative Syntax)**

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\InvokableRule;

class PhoneNumber implements InvokableRule
{
    public function __invoke($attribute, $value, $fail)
    {
        // Remove all non-numeric characters
        $cleaned = preg_replace('/[^0-9]/', '', $value);

        // Check if it's 10 digits
        if (strlen($cleaned) !== 10) {
            $fail('The :attribute must be a valid 10-digit phone number.');
            return;
        }

        // Check if it starts with valid area code (example)
        $areaCode = substr($cleaned, 0, 3);
        $invalidAreaCodes = ['000', '111', '999'];

        if (in_array($areaCode, $invalidAreaCodes)) {
            $fail('The :attribute has an invalid area code.');
        }
    }
}
```

### 7. **Conditional Validation Rule**

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\DataAwareRule;
use Illuminate\Contracts\Validation\ValidationRule;

class RequiredIfPremium implements ValidationRule, DataAwareRule
{
    protected array $data = [];

    public function setData(array $data): static
    {
        $this->data = $data;
        return $this;
    }

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $isPremium = $this->data['account_type'] ?? null === 'premium';

        if ($isPremium && empty($value)) {
            $fail('The :attribute is required for premium accounts.');
        }
    }
}
```

## Best Practices
- Use descriptive rule class names
- Keep validation logic focused
- Use parameters for reusability
- Provide clear error messages
- Use DataAwareRule for cross-field validation
- Cache external API results when possible
- Handle exceptions gracefully
- Test rules with various inputs

Generate complete Laravel validation rule with proper structure.
