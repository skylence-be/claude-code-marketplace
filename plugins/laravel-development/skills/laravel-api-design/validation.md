# API Validation

Form requests and error handling for APIs.

## Form Request

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Contracts\Validation\Validator;
use Illuminate\Http\Exceptions\HttpResponseException;

class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'category_id' => 'required|exists:categories,id',
            'tags' => 'array',
            'tags.*' => 'exists:tags,id',
            'status' => 'in:draft,published',
            'published_at' => 'nullable|date|after:now',
        ];
    }

    public function messages(): array
    {
        return [
            'title.required' => 'A post title is required',
            'content.required' => 'Post content cannot be empty',
            'category_id.exists' => 'The selected category does not exist',
        ];
    }

    /**
     * Handle failed validation for API.
     */
    protected function failedValidation(Validator $validator)
    {
        throw new HttpResponseException(
            response()->json([
                'message' => 'Validation failed',
                'errors' => $validator->errors(),
            ], 422)
        );
    }

    protected function prepareForValidation(): void
    {
        $this->merge([
            'slug' => Str::slug($this->title),
        ]);
    }
}
```

## Error Handler

```php
<?php

namespace App\Exceptions;

use Illuminate\Foundation\Exceptions\Handler as ExceptionHandler;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Throwable;

class Handler extends ExceptionHandler
{
    public function register(): void
    {
        $this->renderable(function (NotFoundHttpException $e, $request) {
            if ($request->is('api/*')) {
                return response()->json([
                    'message' => 'Resource not found',
                ], 404);
            }
        });

        $this->renderable(function (ModelNotFoundException $e, $request) {
            if ($request->is('api/*')) {
                return response()->json([
                    'message' => 'Record not found',
                ], 404);
            }
        });

        $this->renderable(function (AuthenticationException $e, $request) {
            if ($request->is('api/*')) {
                return response()->json([
                    'message' => 'Unauthenticated',
                ], 401);
            }
        });

        $this->renderable(function (ValidationException $e, $request) {
            if ($request->is('api/*')) {
                return response()->json([
                    'message' => 'Validation failed',
                    'errors' => $e->errors(),
                ], 422);
            }
        });
    }
}
```

## Custom Exception

```php
namespace App\Exceptions;

use Exception;

class ApiException extends Exception
{
    protected int $statusCode;
    protected array $errors;

    public function __construct(
        string $message,
        int $statusCode = 400,
        array $errors = []
    ) {
        parent::__construct($message);
        $this->statusCode = $statusCode;
        $this->errors = $errors;
    }

    public function render($request)
    {
        $response = ['message' => $this->message];

        if (!empty($this->errors)) {
            $response['errors'] = $this->errors;
        }

        return response()->json($response, $this->statusCode);
    }
}

// Usage
throw new ApiException('Post limit reached', 403);
```
