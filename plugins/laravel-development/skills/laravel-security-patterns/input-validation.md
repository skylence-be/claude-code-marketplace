# Input Validation

Validate and sanitize all user input.

## Form Request Validation

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('create', Post::class);
    }

    public function rules(): array
    {
        return [
            'title' => 'required|string|max:255',
            'content' => 'required|string|max:50000',
            'category_id' => 'required|exists:categories,id',
            'tags' => 'array|max:10',
            'tags.*' => 'string|max:50',
            'published_at' => 'nullable|date|after:now',
            'featured_image' => 'nullable|image|max:2048',
        ];
    }

    public function messages(): array
    {
        return [
            'title.required' => 'A title is required.',
            'content.max' => 'Content cannot exceed 50,000 characters.',
        ];
    }

    protected function prepareForValidation(): void
    {
        $this->merge([
            'slug' => Str::slug($this->title),
        ]);
    }
}
```

## Common Validation Rules

```php
$rules = [
    // Strings
    'name' => 'required|string|min:2|max:255',
    'bio' => 'nullable|string|max:1000',

    // Email
    'email' => 'required|email:rfc,dns|unique:users,email',

    // URLs
    'website' => 'nullable|url',

    // Numeric
    'age' => 'required|integer|min:18|max:120',
    'price' => 'required|numeric|min:0|max:999999.99',

    // Files
    'avatar' => 'nullable|image|mimes:jpg,png|max:2048',
    'document' => 'nullable|file|mimes:pdf,doc,docx|max:10240',

    // Arrays
    'items' => 'required|array|min:1|max:100',
    'items.*.id' => 'required|exists:products,id',
    'items.*.quantity' => 'required|integer|min:1',

    // Dates
    'start_date' => 'required|date|after:today',
    'end_date' => 'required|date|after:start_date',

    // Conditional
    'reason' => 'required_if:action,cancel',
];
```

## Sanitization

```php
// In Form Request
protected function prepareForValidation(): void
{
    $this->merge([
        'phone' => preg_replace('/[^0-9+]/', '', $this->phone),
        'email' => strtolower(trim($this->email)),
        'name' => strip_tags($this->name),
    ]);
}

// In controller
$clean = $request->only(['name', 'email', 'bio']);
$clean = $request->validated(); // Only validated fields
```

## File Validation

```php
$request->validate([
    'avatar' => [
        'required',
        'image',
        'mimes:jpg,jpeg,png,gif',
        'max:2048', // 2MB
        'dimensions:min_width=100,min_height=100,max_width=2000,max_height=2000',
    ],
    'document' => [
        'required',
        'file',
        'mimes:pdf,doc,docx',
        'max:10240', // 10MB
    ],
]);

// Validate file contents (not just extension)
use Illuminate\Validation\Rules\File;

$request->validate([
    'attachment' => [
        'required',
        File::types(['pdf', 'doc', 'docx'])
            ->max(10 * 1024), // 10MB
    ],
]);
```

## Custom Validation Rules

```php
// Create rule
php artisan make:rule NoSpam

// app/Rules/NoSpam.php
class NoSpam implements ValidationRule
{
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $spamWords = ['viagra', 'casino', 'lottery'];

        foreach ($spamWords as $word) {
            if (str_contains(strtolower($value), $word)) {
                $fail('The :attribute contains spam content.');
            }
        }
    }
}

// Usage
$request->validate([
    'content' => ['required', 'string', new NoSpam],
]);
```

## Rate Limiting Validation

```php
// Prevent form spam
RateLimiter::for('submit-form', function (Request $request) {
    return Limit::perMinute(5)->by($request->user()?->id ?: $request->ip());
});

// Apply to route
Route::post('/contact', [ContactController::class, 'submit'])
    ->middleware('throttle:submit-form');
```
