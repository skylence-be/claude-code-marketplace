# Validation Patterns

Livewire 4 validation strategies and custom rules.

## Inline Validation with #[Validate]

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class RegistrationForm extends Component
{
    #[Validate('required|min:3|max:50')]
    public $username = '';

    #[Validate('required|email|unique:users,email')]
    public $email = '';

    #[Validate('required|min:8|confirmed')]
    public $password = '';

    public $password_confirmation = '';

    // Multiple rules as array
    #[Validate([
        'required',
        'regex:/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/'
    ])]
    public $phone = '';

    public function register()
    {
        $validated = $this->validate();

        $user = \App\Models\User::create([
            'username' => $validated['username'],
            'email' => $validated['email'],
            'password' => bcrypt($validated['password']),
        ]);

        auth()->login($user);

        return redirect()->route('dashboard');
    }
}
```

## Real-Time Validation

```php
class RealTimeValidation extends Component
{
    public $username = '';
    public $email = '';

    /**
     * Validate username as user types.
     */
    public function updatedUsername($value)
    {
        $this->validateOnly('username', [
            'username' => 'required|min:3|max:50',
        ]);

        // Additional custom validation
        if (\App\Models\User::where('username', $value)->exists()) {
            $this->addError('username', 'This username is already taken.');
        }
    }

    /**
     * Validate email with debounce in view.
     */
    public function updatedEmail($value)
    {
        $this->validateOnly('email', [
            'email' => 'required|email|unique:users,email',
        ]);

        // Check blocked domains
        $domain = substr(strrchr($value, "@"), 1);
        if (in_array($domain, config('auth.blocked_domains'))) {
            $this->addError('email', 'This email domain is not allowed.');
        }
    }
}
```

```blade
<div>
    <input
        type="text"
        wire:model.live.debounce.300ms="username"
        @error('username') class="border-red-500" @enderror
    >
    @error('username')
        <span class="error">{{ $message }}</span>
    @enderror

    <span wire:loading wire:target="username">
        Checking availability...
    </span>
</div>
```

## Custom Validation Rules

```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

class StrongPassword implements ValidationRule
{
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        if (strlen($value) < 8) {
            $fail('The password must be at least 8 characters.');
        }

        if (!preg_match('/[a-z]/', $value)) {
            $fail('The password must contain at least one lowercase letter.');
        }

        if (!preg_match('/[A-Z]/', $value)) {
            $fail('The password must contain at least one uppercase letter.');
        }

        if (!preg_match('/[0-9]/', $value)) {
            $fail('The password must contain at least one number.');
        }

        if (!preg_match('/[^a-zA-Z0-9]/', $value)) {
            $fail('The password must contain at least one special character.');
        }
    }
}

class UniqueSlug implements ValidationRule
{
    public function __construct(
        private ?int $exceptId = null,
        private string $table = 'posts'
    ) {}

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $query = \DB::table($this->table)->where('slug', $value);

        if ($this->exceptId) {
            $query->where('id', '!=', $this->exceptId);
        }

        if ($query->exists()) {
            $fail("The {$attribute} is already taken.");
        }
    }
}
```

```php
// Using custom rules in component
use App\Rules\StrongPassword;
use App\Rules\UniqueSlug;

class CustomValidation extends Component
{
    public $password = '';
    public $slug = '';
    public $postId = null;

    public function rules()
    {
        return [
            'password' => ['required', new StrongPassword()],
            'slug' => ['required', new UniqueSlug($this->postId)],
        ];
    }

    // Or inline closure validation
    public function validateSlug()
    {
        $this->validate([
            'slug' => [
                'required',
                function ($attribute, $value, $fail) {
                    if (!preg_match('/^[a-z0-9-]+$/', $value)) {
                        $fail('The slug can only contain lowercase letters, numbers, and hyphens.');
                    }
                }
            ]
        ]);
    }
}
```

## Conditional Validation

```php
class ConditionalValidation extends Component
{
    public $accountType = 'personal';
    public $companyName = '';
    public $taxId = '';
    public $individualName = '';

    /**
     * Dynamic validation rules based on conditions.
     */
    protected function rules()
    {
        $rules = [
            'accountType' => 'required|in:personal,business',
        ];

        if ($this->accountType === 'business') {
            $rules['companyName'] = 'required|string|min:3';
            $rules['taxId'] = 'required|string';
        } else {
            $rules['individualName'] = 'required|string|min:3';
        }

        return $rules;
    }

    /**
     * Clear errors when switching account type.
     */
    public function updatedAccountType()
    {
        if ($this->accountType === 'personal') {
            $this->resetErrorBag(['companyName', 'taxId']);
            $this->companyName = '';
            $this->taxId = '';
        } else {
            $this->resetErrorBag('individualName');
            $this->individualName = '';
        }
    }

    public function submit()
    {
        $this->validate();
        // Process form
    }
}
```

```blade
<div>
    <select wire:model.live="accountType">
        <option value="personal">Personal</option>
        <option value="business">Business</option>
    </select>

    @if($accountType === 'business')
        <input wire:model.blur="companyName" placeholder="Company Name">
        @error('companyName') <span class="error">{{ $message }}</span> @enderror

        <input wire:model.blur="taxId" placeholder="Tax ID">
        @error('taxId') <span class="error">{{ $message }}</span> @enderror
    @else
        <input wire:model.blur="individualName" placeholder="Full Name">
        @error('individualName') <span class="error">{{ $message }}</span> @enderror
    @endif
</div>
```

## Error Handling

```php
class ErrorHandling extends Component
{
    public $email = '';

    /**
     * Add custom error.
     */
    public function addCustomError()
    {
        $this->addError('email', 'Custom error message');
    }

    /**
     * Reset specific error.
     */
    public function clearEmailError()
    {
        $this->resetErrorBag('email');
    }

    /**
     * Reset all errors.
     */
    public function clearAllErrors()
    {
        $this->resetErrorBag();
    }

    /**
     * Check if has errors.
     */
    public function hasErrors(): bool
    {
        return $this->getErrorBag()->isNotEmpty();
    }
}
```

```blade
{{-- Show all errors --}}
@if($errors->any())
    <div class="error-summary">
        <ul>
            @foreach($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif

{{-- Field-specific error --}}
<input wire:model.blur="email" @class(['border-red-500' => $errors->has('email')])>
@error('email')
    <span class="error" role="alert">{{ $message }}</span>
@enderror
```

## Error Bags for Multiple Forms

```php
class MultipleForms extends Component
{
    public $loginEmail = '';
    public $loginPassword = '';
    public $registerEmail = '';

    public function login()
    {
        // Use 'login' error bag
        $this->validate([
            'loginEmail' => 'required|email',
            'loginPassword' => 'required',
        ], [], [], 'login');

        if (!auth()->attempt([
            'email' => $this->loginEmail,
            'password' => $this->loginPassword,
        ])) {
            $this->addError('loginPassword', 'Invalid credentials.', 'login');
        }
    }

    public function register()
    {
        // Use 'register' error bag
        $this->validate([
            'registerEmail' => 'required|email|unique:users,email',
        ], [], [], 'register');
    }
}
```

```blade
{{-- Login form errors --}}
@error('loginEmail', 'login')
    <span class="error">{{ $message }}</span>
@enderror

{{-- Register form errors --}}
@error('registerEmail', 'register')
    <span class="error">{{ $message }}</span>
@enderror
```

## Custom Validation Messages

```php
class CustomMessages extends Component
{
    protected function messages()
    {
        return [
            'email.required' => 'We need your email address.',
            'email.email' => 'Please enter a valid email.',
            'password.min' => 'Password must be at least :min characters.',
        ];
    }

    protected function validationAttributes()
    {
        return [
            'email' => 'email address',
            'dob' => 'date of birth',
        ];
    }
}
```
