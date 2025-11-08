---
description: Create Laravel Form Request with validation rules
model: claude-sonnet-4-5
---

Create a Laravel Form Request for validation.

## Request Specification

$ARGUMENTS

## Laravel Form Request Patterns

### 1. **Basic Form Request**

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'slug' => ['required', 'string', 'max:255', 'unique:posts,slug'],
            'excerpt' => ['nullable', 'string', 'max:500'],
            'content' => ['required', 'string'],
            'status' => ['required', 'in:draft,published,archived'],
            'published_at' => ['nullable', 'date', 'after_or_equal:today'],
            'category_id' => ['required', 'exists:categories,id'],
            'tags' => ['array'],
            'tags.*' => ['exists:tags,id'],
        ];
    }

    public function messages(): array
    {
        return [
            'title.required' => 'A post title is required.',
            'slug.unique' => 'This slug is already taken. Please choose another.',
            'published_at.after_or_equal' => 'Publication date must be today or later.',
        ];
    }

    public function attributes(): array
    {
        return [
            'category_id' => 'category',
            'published_at' => 'publication date',
        ];
    }
}
```

### 2. **Update Form Request**

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UpdatePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('update', $this->route('post'));
    }

    public function rules(): array
    {
        $postId = $this->route('post')->id;

        return [
            'title' => ['required', 'string', 'max:255'],
            'slug' => [
                'required',
                'string',
                'max:255',
                Rule::unique('posts')->ignore($postId),
            ],
            'content' => ['required', 'string'],
            'status' => ['required', Rule::in(['draft', 'published', 'archived'])],
            'published_at' => [
                'nullable',
                'date',
                Rule::when(
                    fn () => $this->status === 'published',
                    ['required', 'after_or_equal:today']
                ),
            ],
        ];
    }

    protected function prepareForValidation(): void
    {
        $this->merge([
            'slug' => $this->slug ?? Str::slug($this->title),
        ]);
    }
}
```

### 3. **Form Request with Custom Validation**

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Validator;

class StoreUserRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'email', 'unique:users,email'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
            'role' => ['required', 'in:user,admin,moderator'],
            'avatar' => ['nullable', 'image', 'max:2048'],
        ];
    }

    public function withValidator(Validator $validator): void
    {
        $validator->after(function (Validator $validator) {
            if ($this->role === 'admin' && !$this->user()->isAdmin()) {
                $validator->errors()->add(
                    'role',
                    'Only administrators can create admin users.'
                );
            }
        });
    }

    protected function passedValidation(): void
    {
        $this->merge([
            'password' => Hash::make($this->password),
        ]);
    }
}
```

### 4. **API Request with Nested Validation**

```php
<?php

namespace App\Http\Requests\Api;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Contracts\Validation\Validator;
use Illuminate\Http\Exceptions\HttpResponseException;

class StoreOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'customer.name' => ['required', 'string', 'max:255'],
            'customer.email' => ['required', 'email'],
            'customer.phone' => ['nullable', 'string', 'max:20'],

            'items' => ['required', 'array', 'min:1'],
            'items.*.product_id' => ['required', 'exists:products,id'],
            'items.*.quantity' => ['required', 'integer', 'min:1'],
            'items.*.price' => ['required', 'numeric', 'min:0'],

            'shipping_address.street' => ['required', 'string'],
            'shipping_address.city' => ['required', 'string'],
            'shipping_address.postal_code' => ['required', 'string'],
            'shipping_address.country' => ['required', 'string', 'size:2'],

            'payment_method' => ['required', 'in:credit_card,paypal,bank_transfer'],
        ];
    }

    protected function failedValidation(Validator $validator)
    {
        throw new HttpResponseException(
            response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors(),
            ], 422)
        );
    }
}
```

## Best Practices
- Use authorize() for authorization logic
- Create separate requests for store and update
- Use Rule::unique()->ignore() for updates
- Add custom error messages for better UX
- Use prepareForValidation() for data preparation
- Use withValidator() for complex validation
- Use passedValidation() for post-validation logic
- Consider using Laravel Precognition for live validation

Generate complete Form Request with validation rules and authorization.
