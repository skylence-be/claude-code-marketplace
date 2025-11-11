---
name: livewire-forms-validation
description: Master Livewire 4 form handling including form objects, real-time validation, custom validation rules, file uploads, multi-step forms, and error handling. Use when building complex forms, implementing validation logic, or handling user input.
---

# Livewire Forms and Validation

Comprehensive guide to building robust forms in Livewire 4, covering form objects, real-time validation patterns, custom rules, file uploads, multi-step wizards, nested arrays, and advanced error handling techniques.

## When to Use This Skill

- Building complex forms with multiple fields and validation rules
- Implementing real-time validation with instant user feedback
- Creating multi-step form wizards with state preservation
- Handling file uploads with progress indicators and validation
- Building dynamic forms with repeatable field groups
- Implementing custom validation rules for business logic
- Managing form state across multiple component interactions
- Creating accessible forms with proper error messaging
- Handling nested arrays and complex data structures
- Building forms with conditional validation logic

## Core Concepts

### 1. Form Objects
- **Livewire\Form**: Dedicated class for encapsulating form logic
- **Property grouping**: Organize related form fields together
- **Reusable validation**: Share validation rules across components
- **State management**: Centralized form state handling
- **Reset functionality**: Easy form clearing and resetting

### 2. Validation Attributes
- **#[Validate]**: Inline validation rules on properties
- **#[Rule]**: Alternative validation syntax
- **Real-time validation**: Validate as user types or on blur
- **Custom messages**: Override default validation messages
- **Conditional rules**: Dynamic validation based on other fields

### 3. Validation Timing
- **wire:model.live**: Validate on every keystroke
- **wire:model.blur**: Validate when field loses focus
- **wire:model.lazy**: Validate on form submit or blur
- **Manual validation**: Programmatic validation control
- **Debounced validation**: Reduce validation frequency

### 4. File Handling
- **TemporaryUploadedFile**: Livewire's file upload handling
- **Progress indicators**: Show upload progress to users
- **Validation**: File size, type, and dimension validation
- **Storage**: Save files to disk or cloud storage
- **Preview**: Display uploaded images before submission

### 5. Error Management
- **Error bags**: Separate error collections for multiple forms
- **Error messages**: Display validation errors to users
- **Custom errors**: Add programmatic errors
- **Error clearing**: Remove errors manually
- **Error styling**: Conditional CSS based on errors

## Quick Start

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class ContactForm extends Component
{
    #[Validate('required|min:3')]
    public $name = '';

    #[Validate('required|email')]
    public $email = '';

    #[Validate('required|min:10')]
    public $message = '';

    public function submit()
    {
        $this->validate();

        // Process form
        logger('Contact form submitted', $this->all());

        session()->flash('success', 'Message sent successfully!');
        $this->reset();
    }

    public function render()
    {
        return view('livewire.contact-form');
    }
}
```

```blade
<form wire:submit="submit">
    <div>
        <label>Name</label>
        <input type="text" wire:model.blur="name">
        @error('name') <span class="error">{{ $message }}</span> @enderror
    </div>

    <div>
        <label>Email</label>
        <input type="email" wire:model.blur="email">
        @error('email') <span class="error">{{ $message }}</span> @enderror
    </div>

    <div>
        <label>Message</label>
        <textarea wire:model.blur="message"></textarea>
        @error('message') <span class="error">{{ $message }}</span> @enderror
    </div>

    <button type="submit">Send Message</button>
</form>
```

## Fundamental Patterns

### Pattern 1: Form Objects for Complex Forms

```php
<?php

namespace App\Livewire\Forms;

use Livewire\Form;
use Livewire\Attributes\Validate;

class PostForm extends Form
{
    #[Validate('required|string|min:3|max:255')]
    public $title = '';

    #[Validate('required|string|unique:posts,slug')]
    public $slug = '';

    #[Validate('required|string|min:100')]
    public $content = '';

    #[Validate('required|exists:categories,id')]
    public $category_id = '';

    #[Validate('required|in:draft,published')]
    public $status = 'draft';

    #[Validate('nullable|array')]
    public $tags = [];

    #[Validate('nullable|date')]
    public $published_at = null;

    /**
     * Custom validation messages.
     */
    public function messages()
    {
        return [
            'title.required' => 'Please enter a post title.',
            'content.min' => 'The post content must be at least 100 characters.',
            'slug.unique' => 'This slug is already taken.',
        ];
    }

    /**
     * Store the post.
     */
    public function store()
    {
        $this->validate();

        $post = \App\Models\Post::create([
            'title' => $this->title,
            'slug' => $this->slug,
            'content' => $this->content,
            'category_id' => $this->category_id,
            'status' => $this->status,
            'published_at' => $this->published_at,
            'user_id' => auth()->id(),
        ]);

        $post->tags()->sync($this->tags);

        return $post;
    }

    /**
     * Update existing post.
     */
    public function update(\App\Models\Post $post)
    {
        $this->validate([
            'slug' => 'required|string|unique:posts,slug,' . $post->id,
        ]);

        $post->update([
            'title' => $this->title,
            'slug' => $this->slug,
            'content' => $this->content,
            'category_id' => $this->category_id,
            'status' => $this->status,
            'published_at' => $this->published_at,
        ]);

        $post->tags()->sync($this->tags);

        return $post;
    }

    /**
     * Set form data from existing post.
     */
    public function setPost(\App\Models\Post $post)
    {
        $this->title = $post->title;
        $this->slug = $post->slug;
        $this->content = $post->content;
        $this->category_id = $post->category_id;
        $this->status = $post->status;
        $this->tags = $post->tags->pluck('id')->toArray();
        $this->published_at = $post->published_at?->format('Y-m-d');
    }
}

namespace App\Livewire;

use Livewire\Component;
use App\Livewire\Forms\PostForm;
use App\Models\Post;

class CreatePost extends Component
{
    public PostForm $form;

    public function save()
    {
        $post = $this->form->store();

        session()->flash('success', 'Post created successfully!');

        return redirect()->route('posts.show', $post);
    }

    public function render()
    {
        return view('livewire.create-post');
    }
}

class EditPost extends Component
{
    public PostForm $form;
    public Post $post;

    public function mount(Post $post)
    {
        $this->post = $post;
        $this->form->setPost($post);
    }

    public function update()
    {
        $this->form->update($this->post);

        session()->flash('success', 'Post updated successfully!');

        return redirect()->route('posts.show', $this->post);
    }

    public function render()
    {
        return view('livewire.edit-post');
    }
}
```

```blade
{{-- Shared form template: resources/views/livewire/post-form.blade.php --}}
<div>
    <div class="form-group">
        <label for="title">Title</label>
        <input
            type="text"
            id="title"
            wire:model.blur="form.title"
            @error('form.title') aria-invalid="true" aria-describedby="title-error" @enderror
        >
        @error('form.title')
            <span class="error" id="title-error">{{ $message }}</span>
        @enderror
    </div>

    <div class="form-group">
        <label for="slug">Slug</label>
        <input
            type="text"
            id="slug"
            wire:model.blur="form.slug"
        >
        @error('form.slug')
            <span class="error">{{ $message }}</span>
        @enderror
    </div>

    <div class="form-group">
        <label for="content">Content</label>
        <textarea
            id="content"
            wire:model.blur="form.content"
            rows="10"
        ></textarea>
        @error('form.content')
            <span class="error">{{ $message }}</span>
        @enderror
    </div>

    <div class="form-group">
        <label for="category">Category</label>
        <select wire:model.live="form.category_id">
            <option value="">Select category</option>
            @foreach($categories as $category)
                <option value="{{ $category->id }}">{{ $category->name }}</option>
            @endforeach
        </select>
        @error('form.category_id')
            <span class="error">{{ $message }}</span>
        @enderror
    </div>

    <div class="form-group">
        <label for="status">Status</label>
        <select wire:model.live="form.status">
            <option value="draft">Draft</option>
            <option value="published">Published</option>
        </select>
    </div>
</div>
```

### Pattern 2: Real-Time Validation with Multiple Strategies

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class RegistrationForm extends Component
{
    // Live validation - validates as user types
    #[Validate('required|min:3|max:50')]
    public $username = '';

    // Blur validation - validates when field loses focus
    #[Validate('required|email|unique:users,email')]
    public $email = '';

    // Lazy validation - validates on submit
    #[Validate('required|min:8|confirmed')]
    public $password = '';

    public $password_confirmation = '';

    // Custom validation with multiple rules
    #[Validate([
        'required',
        'regex:/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/'
    ])]
    public $phone = '';

    /**
     * Validate username uniqueness in real-time.
     */
    public function updatedUsername($value)
    {
        $this->validateOnly('username');

        // Additional custom validation
        if (\App\Models\User::where('username', $value)->exists()) {
            $this->addError('username', 'This username is already taken.');
        }
    }

    /**
     * Validate email as user types (with debounce in view).
     */
    public function updatedEmail($value)
    {
        $this->validateOnly('email');

        // Check if email is from blocked domain
        $domain = substr(strrchr($value, "@"), 1);
        if (in_array($domain, config('auth.blocked_domains'))) {
            $this->addError('email', 'Email domain is not allowed.');
        }
    }

    /**
     * Check password strength.
     */
    public function updatedPassword($value)
    {
        $strength = $this->checkPasswordStrength($value);

        if ($strength < 3) {
            $this->addError('password', 'Password is too weak. Use a mix of letters, numbers, and symbols.');
        }
    }

    private function checkPasswordStrength($password)
    {
        $strength = 0;
        $strength += (strlen($password) >= 8) ? 1 : 0;
        $strength += preg_match('/[a-z]/', $password) ? 1 : 0;
        $strength += preg_match('/[A-Z]/', $password) ? 1 : 0;
        $strength += preg_match('/[0-9]/', $password) ? 1 : 0;
        $strength += preg_match('/[^a-zA-Z0-9]/', $password) ? 1 : 0;

        return $strength;
    }

    public function register()
    {
        $validated = $this->validate();

        $user = \App\Models\User::create([
            'username' => $validated['username'],
            'email' => $validated['email'],
            'password' => bcrypt($validated['password']),
            'phone' => $validated['phone'],
        ]);

        auth()->login($user);

        return redirect()->route('dashboard');
    }

    public function render()
    {
        return view('livewire.registration-form');
    }
}
```

```blade
<form wire:submit="register">
    <div class="form-group">
        <label>Username</label>
        <input
            type="text"
            wire:model.live.debounce.300ms="username"
            class="@error('username') border-red-500 @enderror"
        >
        @error('username')
            <span class="text-red-500">{{ $message }}</span>
        @enderror

        {{-- Show loading indicator during validation --}}
        <span wire:loading wire:target="username" class="text-gray-500">
            Checking availability...
        </span>
    </div>

    <div class="form-group">
        <label>Email</label>
        <input
            type="email"
            wire:model.blur="email"
        >
        @error('email')
            <span class="text-red-500">{{ $message }}</span>
        @enderror
    </div>

    <div class="form-group">
        <label>Password</label>
        <input
            type="password"
            wire:model.live.debounce.500ms="password"
        >
        @error('password')
            <span class="text-red-500">{{ $message }}</span>
        @enderror

        {{-- Password strength indicator --}}
        <div class="password-strength">
            <div class="strength-bar" style="width: {{ min(100, strlen($password) * 10) }}%"></div>
        </div>
    </div>

    <div class="form-group">
        <label>Confirm Password</label>
        <input
            type="password"
            wire:model.lazy="password_confirmation"
        >
    </div>

    <div class="form-group">
        <label>Phone</label>
        <input
            type="tel"
            wire:model.blur="phone"
        >
        @error('phone')
            <span class="text-red-500">{{ $message }}</span>
        @enderror
    </div>

    <button
        type="submit"
        wire:loading.attr="disabled"
        wire:loading.class="opacity-50"
    >
        <span wire:loading.remove>Register</span>
        <span wire:loading>Registering...</span>
    </button>
</form>
```

### Pattern 3: Custom Validation Rules

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

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;
use App\Rules\StrongPassword;
use App\Rules\UniqueSlug;

class CustomValidation extends Component
{
    public $password = '';

    public $slug = '';

    public $postId = null;

    /**
     * Using custom rule object.
     */
    public function rules()
    {
        return [
            'password' => ['required', new StrongPassword()],
            'slug' => ['required', new UniqueSlug($this->postId)],
        ];
    }

    /**
     * Alternative: Inline custom validation.
     */
    public function validateSlug()
    {
        $this->validate([
            'slug' => [
                'required',
                function ($attribute, $value, $fail) {
                    if (!preg_match('/^[a-z0-9-]+$/', $value)) {
                        $fail('The slug can only contain lowercase letters, numbers, and hyphens.');
                    }

                    if (strlen($value) > 100) {
                        $fail('The slug cannot be longer than 100 characters.');
                    }
                }
            ]
        ]);
    }

    public function submit()
    {
        $this->validate();

        // Process form
    }

    public function render()
    {
        return view('livewire.custom-validation');
    }
}
```

### Pattern 4: File Upload with Validation

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithFileUploads;
use Livewire\Attributes\Validate;

class FileUploadForm extends Component
{
    use WithFileUploads;

    // Single file upload
    #[Validate('required|image|max:2048')] // 2MB max
    public $photo;

    // Multiple file upload
    #[Validate('required|array|min:1|max:5')]
    #[Validate('photos.*', 'required|image|mimes:jpg,jpeg,png|max:1024')]
    public $photos = [];

    // Document upload
    #[Validate('required|file|mimes:pdf,doc,docx|max:10240')] // 10MB max
    public $document;

    // Avatar with dimensions validation
    #[Validate('required|image|dimensions:min_width=100,min_height=100,max_width=1000,max_height=1000')]
    public $avatar;

    /**
     * Handle single file upload.
     */
    public function uploadPhoto()
    {
        $this->validate([
            'photo' => 'required|image|max:2048',
        ]);

        $path = $this->photo->store('photos', 'public');

        session()->flash('message', 'Photo uploaded successfully!');

        // Reset file input
        $this->photo = null;
    }

    /**
     * Handle multiple file uploads.
     */
    public function uploadPhotos()
    {
        $this->validate([
            'photos' => 'required|array|min:1|max:5',
            'photos.*' => 'required|image|max:1024',
        ]);

        $paths = [];
        foreach ($this->photos as $photo) {
            $paths[] = $photo->store('photos', 'public');
        }

        session()->flash('message', count($paths) . ' photos uploaded successfully!');

        $this->photos = [];
    }

    /**
     * Validate file during upload (before submit).
     */
    public function updatedPhoto()
    {
        $this->validateOnly('photo');
    }

    /**
     * Remove photo from preview.
     */
    public function removePhoto($index)
    {
        unset($this->photos[$index]);
        $this->photos = array_values($this->photos);
    }

    /**
     * Save with file upload.
     */
    public function save()
    {
        $this->validate();

        $user = auth()->user();

        // Store avatar
        if ($this->avatar) {
            // Delete old avatar
            if ($user->avatar) {
                \Storage::disk('public')->delete($user->avatar);
            }

            $avatarPath = $this->avatar->store('avatars', 'public');
            $user->update(['avatar' => $avatarPath]);
        }

        // Store document
        if ($this->document) {
            $documentPath = $this->document->storeAs(
                'documents',
                $this->document->getClientOriginalName(),
                'public'
            );

            \App\Models\Document::create([
                'user_id' => $user->id,
                'path' => $documentPath,
                'name' => $this->document->getClientOriginalName(),
                'size' => $this->document->getSize(),
            ]);
        }

        session()->flash('success', 'Files uploaded successfully!');

        $this->reset(['photo', 'photos', 'document', 'avatar']);
    }

    public function render()
    {
        return view('livewire.file-upload-form');
    }
}
```

```blade
<form wire:submit="save">
    {{-- Single file with preview --}}
    <div class="form-group">
        <label>Photo</label>
        <input type="file" wire:model="photo" accept="image/*">

        @error('photo')
            <span class="error">{{ $message }}</span>
        @enderror

        {{-- Upload progress --}}
        <div wire:loading wire:target="photo">
            Uploading... <span x-text="$wire.uploadProgress + '%'"></span>
        </div>

        {{-- Preview --}}
        @if ($photo)
            <div class="preview">
                <img src="{{ $photo->temporaryUrl() }}" alt="Preview">
            </div>
        @endif
    </div>

    {{-- Multiple files with preview --}}
    <div class="form-group">
        <label>Photos (max 5)</label>
        <input type="file" wire:model="photos" multiple accept="image/*">

        @error('photos')
            <span class="error">{{ $message }}</span>
        @enderror
        @error('photos.*')
            <span class="error">{{ $message }}</span>
        @enderror

        <div wire:loading wire:target="photos">
            Uploading photos...
        </div>

        {{-- Preview multiple --}}
        @if (!empty($photos))
            <div class="photo-grid">
                @foreach($photos as $index => $photo)
                    <div class="photo-item">
                        <img src="{{ $photo->temporaryUrl() }}">
                        <button
                            type="button"
                            wire:click="removePhoto({{ $index }})"
                        >
                            Remove
                        </button>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- Document upload --}}
    <div class="form-group">
        <label>Document (PDF, DOC, DOCX)</label>
        <input type="file" wire:model="document" accept=".pdf,.doc,.docx">

        @error('document')
            <span class="error">{{ $message }}</span>
        @enderror

        @if ($document)
            <p>Selected: {{ $document->getClientOriginalName() }}
               ({{ number_format($document->getSize() / 1024, 2) }} KB)</p>
        @endif
    </div>

    {{-- Avatar with dimensions validation --}}
    <div class="form-group">
        <label>Avatar (100x100 to 1000x1000 px)</label>
        <input type="file" wire:model="avatar" accept="image/*">

        @error('avatar')
            <span class="error">{{ $message }}</span>
        @enderror

        @if ($avatar)
            <div class="avatar-preview">
                <img src="{{ $avatar->temporaryUrl() }}">
            </div>
        @endif
    </div>

    <button type="submit" wire:loading.attr="disabled">
        Upload Files
    </button>
</form>

{{-- JavaScript for upload progress --}}
<script>
document.addEventListener('livewire:init', () => {
    Livewire.hook('commit', ({ component, commit, respond, succeed, fail }) => {
        // Access upload progress
        succeed(({ effects, component }) => {
            console.log('Upload progress:', effects.uploadProgress);
        });
    });
});
</script>
```

### Pattern 5: Multi-Step Form Wizard

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithFileUploads;
use Livewire\Attributes\Validate;

class UserOnboarding extends Component
{
    use WithFileUploads;

    public $currentStep = 1;
    public $totalSteps = 4;

    // Step 1: Personal Info
    #[Validate('required|min:3')]
    public $firstName = '';

    #[Validate('required|min:3')]
    public $lastName = '';

    #[Validate('required|date|before:today')]
    public $birthDate = '';

    // Step 2: Contact Info
    #[Validate('required|email|unique:users,email')]
    public $email = '';

    #[Validate('required|regex:/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/')]
    public $phone = '';

    #[Validate('required|string')]
    public $address = '';

    // Step 3: Account Setup
    #[Validate('required|min:8|confirmed')]
    public $password = '';

    public $password_confirmation = '';

    #[Validate('nullable|image|max:2048')]
    public $profilePhoto;

    // Step 4: Preferences
    #[Validate('required|array|min:1')]
    public $interests = [];

    #[Validate('required|boolean')]
    public $newsletter = false;

    #[Validate('required|accepted')]
    public $terms = false;

    /**
     * Get validation rules for current step.
     */
    protected function getRulesForStep($step)
    {
        return match($step) {
            1 => [
                'firstName' => 'required|min:3',
                'lastName' => 'required|min:3',
                'birthDate' => 'required|date|before:today',
            ],
            2 => [
                'email' => 'required|email|unique:users,email',
                'phone' => 'required|regex:/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/',
                'address' => 'required|string',
            ],
            3 => [
                'password' => 'required|min:8|confirmed',
                'profilePhoto' => 'nullable|image|max:2048',
            ],
            4 => [
                'interests' => 'required|array|min:1',
                'newsletter' => 'required|boolean',
                'terms' => 'required|accepted',
            ],
            default => [],
        };
    }

    /**
     * Validate and move to next step.
     */
    public function nextStep()
    {
        $this->validate($this->getRulesForStep($this->currentStep));

        if ($this->currentStep < $this->totalSteps) {
            $this->currentStep++;
        }
    }

    /**
     * Move to previous step without validation.
     */
    public function previousStep()
    {
        if ($this->currentStep > 1) {
            $this->currentStep--;
        }
    }

    /**
     * Jump to specific step (if accessible).
     */
    public function goToStep($step)
    {
        // Validate all previous steps
        for ($i = 1; $i < $step; $i++) {
            try {
                $this->validate($this->getRulesForStep($i));
            } catch (\Exception $e) {
                session()->flash('error', 'Please complete previous steps first.');
                return;
            }
        }

        $this->currentStep = $step;
    }

    /**
     * Submit the complete form.
     */
    public function submit()
    {
        // Validate all steps
        for ($i = 1; $i <= $this->totalSteps; $i++) {
            $this->validate($this->getRulesForStep($i));
        }

        // Store profile photo
        $photoPath = $this->profilePhoto
            ? $this->profilePhoto->store('profile-photos', 'public')
            : null;

        // Create user
        $user = \App\Models\User::create([
            'first_name' => $this->firstName,
            'last_name' => $this->lastName,
            'birth_date' => $this->birthDate,
            'email' => $this->email,
            'phone' => $this->phone,
            'address' => $this->address,
            'password' => bcrypt($this->password),
            'profile_photo' => $photoPath,
            'interests' => $this->interests,
            'newsletter' => $this->newsletter,
        ]);

        auth()->login($user);

        session()->flash('success', 'Account created successfully!');

        return redirect()->route('dashboard');
    }

    /**
     * Get progress percentage.
     */
    public function getProgressPercentage()
    {
        return ($this->currentStep / $this->totalSteps) * 100;
    }

    public function render()
    {
        return view('livewire.user-onboarding', [
            'progressPercentage' => $this->getProgressPercentage(),
        ]);
    }
}
```

```blade
<div>
    {{-- Progress bar --}}
    <div class="progress-bar">
        <div class="progress" style="width: {{ $progressPercentage }}%"></div>
    </div>

    {{-- Step indicators --}}
    <div class="steps">
        @for($i = 1; $i <= $totalSteps; $i++)
            <div @class([
                'step',
                'active' => $i === $currentStep,
                'completed' => $i < $currentStep,
            ])>
                <span class="step-number">{{ $i }}</span>
                <span class="step-label">
                    @switch($i)
                        @case(1) Personal @break
                        @case(2) Contact @break
                        @case(3) Account @break
                        @case(4) Preferences @break
                    @endswitch
                </span>
            </div>
        @endfor
    </div>

    {{-- Form steps --}}
    <form wire:submit="submit">
        {{-- Step 1: Personal Info --}}
        @if($currentStep === 1)
            <div class="step-content">
                <h3>Personal Information</h3>

                <div class="form-row">
                    <div class="form-group">
                        <label>First Name</label>
                        <input type="text" wire:model.blur="firstName">
                        @error('firstName') <span class="error">{{ $message }}</span> @enderror
                    </div>

                    <div class="form-group">
                        <label>Last Name</label>
                        <input type="text" wire:model.blur="lastName">
                        @error('lastName') <span class="error">{{ $message }}</span> @enderror
                    </div>
                </div>

                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" wire:model.blur="birthDate">
                    @error('birthDate') <span class="error">{{ $message }}</span> @enderror
                </div>
            </div>
        @endif

        {{-- Step 2: Contact Info --}}
        @if($currentStep === 2)
            <div class="step-content">
                <h3>Contact Information</h3>

                <div class="form-group">
                    <label>Email</label>
                    <input type="email" wire:model.blur="email">
                    @error('email') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" wire:model.blur="phone">
                    @error('phone') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>Address</label>
                    <textarea wire:model.blur="address"></textarea>
                    @error('address') <span class="error">{{ $message }}</span> @enderror
                </div>
            </div>
        @endif

        {{-- Step 3: Account Setup --}}
        @if($currentStep === 3)
            <div class="step-content">
                <h3>Account Setup</h3>

                <div class="form-group">
                    <label>Password</label>
                    <input type="password" wire:model.blur="password">
                    @error('password') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" wire:model.blur="password_confirmation">
                </div>

                <div class="form-group">
                    <label>Profile Photo (optional)</label>
                    <input type="file" wire:model="profilePhoto">
                    @error('profilePhoto') <span class="error">{{ $message }}</span> @enderror

                    @if($profilePhoto)
                        <img src="{{ $profilePhoto->temporaryUrl() }}" class="preview">
                    @endif
                </div>
            </div>
        @endif

        {{-- Step 4: Preferences --}}
        @if($currentStep === 4)
            <div class="step-content">
                <h3>Your Preferences</h3>

                <div class="form-group">
                    <label>Interests (select at least one)</label>
                    <div class="checkbox-group">
                        <label><input type="checkbox" wire:model="interests" value="technology"> Technology</label>
                        <label><input type="checkbox" wire:model="interests" value="sports"> Sports</label>
                        <label><input type="checkbox" wire:model="interests" value="music"> Music</label>
                        <label><input type="checkbox" wire:model="interests" value="travel"> Travel</label>
                    </div>
                    @error('interests') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" wire:model="newsletter">
                        Subscribe to newsletter
                    </label>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" wire:model="terms">
                        I agree to the terms and conditions
                    </label>
                    @error('terms') <span class="error">{{ $message }}</span> @enderror
                </div>
            </div>
        @endif

        {{-- Navigation buttons --}}
        <div class="form-actions">
            @if($currentStep > 1)
                <button type="button" wire:click="previousStep">
                    Previous
                </button>
            @endif

            @if($currentStep < $totalSteps)
                <button type="button" wire:click="nextStep">
                    Next
                </button>
            @else
                <button type="submit">
                    Complete Registration
                </button>
            @endif
        </div>
    </form>
</div>
```

### Pattern 6: Dynamic Nested Arrays and Repeater Fields

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class DynamicInvoice extends Component
{
    public $invoiceNumber = '';
    public $customerName = '';
    public $invoiceDate = '';

    // Dynamic line items
    public $items = [];

    // Tax and discount
    public $taxRate = 10;
    public $discount = 0;

    public function mount()
    {
        // Initialize with one empty item
        $this->addItem();
        $this->invoiceDate = now()->format('Y-m-d');
        $this->invoiceNumber = 'INV-' . strtoupper(uniqid());
    }

    /**
     * Validation rules for items array.
     */
    protected function rules()
    {
        return [
            'invoiceNumber' => 'required|string',
            'customerName' => 'required|string|min:3',
            'invoiceDate' => 'required|date',
            'items' => 'required|array|min:1',
            'items.*.description' => 'required|string|min:3',
            'items.*.quantity' => 'required|numeric|min:1',
            'items.*.price' => 'required|numeric|min:0',
            'taxRate' => 'required|numeric|min:0|max:100',
            'discount' => 'required|numeric|min:0',
        ];
    }

    /**
     * Custom validation messages.
     */
    protected function messages()
    {
        return [
            'items.*.description.required' => 'Description is required',
            'items.*.quantity.required' => 'Quantity is required',
            'items.*.quantity.min' => 'Quantity must be at least 1',
            'items.*.price.required' => 'Price is required',
            'items.*.price.min' => 'Price must be positive',
        ];
    }

    /**
     * Add new item to array.
     */
    public function addItem()
    {
        $this->items[] = [
            'description' => '',
            'quantity' => 1,
            'price' => 0,
        ];
    }

    /**
     * Remove item from array.
     */
    public function removeItem($index)
    {
        unset($this->items[$index]);
        $this->items = array_values($this->items); // Re-index array
    }

    /**
     * Duplicate an item.
     */
    public function duplicateItem($index)
    {
        $this->items[] = $this->items[$index];
    }

    /**
     * Calculate line total.
     */
    public function getLineTotal($index)
    {
        $item = $this->items[$index] ?? null;
        if (!$item) return 0;

        return ($item['quantity'] ?? 0) * ($item['price'] ?? 0);
    }

    /**
     * Calculate subtotal.
     */
    public function getSubtotal()
    {
        return collect($this->items)->sum(function ($item, $index) {
            return $this->getLineTotal($index);
        });
    }

    /**
     * Calculate tax amount.
     */
    public function getTaxAmount()
    {
        return $this->getSubtotal() * ($this->taxRate / 100);
    }

    /**
     * Calculate total.
     */
    public function getTotal()
    {
        return $this->getSubtotal() + $this->getTaxAmount() - $this->discount;
    }

    /**
     * Validate specific item field.
     */
    public function updatedItems($value, $key)
    {
        // $key will be like "0.description" or "1.quantity"
        $this->validateOnly("items.{$key}");
    }

    /**
     * Save invoice.
     */
    public function save()
    {
        $validated = $this->validate();

        $invoice = \App\Models\Invoice::create([
            'invoice_number' => $validated['invoiceNumber'],
            'customer_name' => $validated['customerName'],
            'invoice_date' => $validated['invoiceDate'],
            'subtotal' => $this->getSubtotal(),
            'tax_rate' => $validated['taxRate'],
            'tax_amount' => $this->getTaxAmount(),
            'discount' => $validated['discount'],
            'total' => $this->getTotal(),
        ]);

        foreach ($validated['items'] as $item) {
            $invoice->items()->create($item);
        }

        session()->flash('success', 'Invoice created successfully!');

        return redirect()->route('invoices.show', $invoice);
    }

    public function render()
    {
        return view('livewire.dynamic-invoice', [
            'subtotal' => $this->getSubtotal(),
            'taxAmount' => $this->getTaxAmount(),
            'total' => $this->getTotal(),
        ]);
    }
}
```

```blade
<div>
    <form wire:submit="save">
        <div class="invoice-header">
            <div class="form-group">
                <label>Invoice Number</label>
                <input type="text" wire:model="invoiceNumber" readonly>
            </div>

            <div class="form-group">
                <label>Customer Name</label>
                <input type="text" wire:model.blur="customerName">
                @error('customerName') <span class="error">{{ $message }}</span> @enderror
            </div>

            <div class="form-group">
                <label>Invoice Date</label>
                <input type="date" wire:model.blur="invoiceDate">
                @error('invoiceDate') <span class="error">{{ $message }}</span> @enderror
            </div>
        </div>

        <div class="line-items">
            <h3>Line Items</h3>

            <table>
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($items as $index => $item)
                        <tr>
                            <td>
                                <input
                                    type="text"
                                    wire:model.blur="items.{{ $index }}.description"
                                    placeholder="Item description"
                                >
                                @error("items.{$index}.description")
                                    <span class="error">{{ $message }}</span>
                                @enderror
                            </td>
                            <td>
                                <input
                                    type="number"
                                    wire:model.blur="items.{{ $index }}.quantity"
                                    min="1"
                                >
                                @error("items.{$index}.quantity")
                                    <span class="error">{{ $message }}</span>
                                @enderror
                            </td>
                            <td>
                                <input
                                    type="number"
                                    wire:model.blur="items.{{ $index }}.price"
                                    step="0.01"
                                    min="0"
                                >
                                @error("items.{$index}.price")
                                    <span class="error">{{ $message }}</span>
                                @enderror
                            </td>
                            <td>
                                ${{ number_format($this->getLineTotal($index), 2) }}
                            </td>
                            <td>
                                <button
                                    type="button"
                                    wire:click="duplicateItem({{ $index }})"
                                    title="Duplicate"
                                >
                                    📋
                                </button>
                                <button
                                    type="button"
                                    wire:click="removeItem({{ $index }})"
                                    title="Remove"
                                    @if(count($items) === 1) disabled @endif
                                >
                                    🗑️
                                </button>
                            </td>
                        </tr>
                    @endforeach
                </tbody>
            </table>

            <button type="button" wire:click="addItem" class="btn-add-item">
                + Add Line Item
            </button>

            @error('items') <span class="error">{{ $message }}</span> @enderror
        </div>

        <div class="invoice-totals">
            <div class="total-row">
                <span>Subtotal:</span>
                <span>${{ number_format($subtotal, 2) }}</span>
            </div>

            <div class="total-row">
                <span>Tax ({{ $taxRate }}%):</span>
                <input
                    type="number"
                    wire:model.blur="taxRate"
                    min="0"
                    max="100"
                    step="0.1"
                    style="width: 60px"
                >%
                <span>${{ number_format($taxAmount, 2) }}</span>
            </div>

            <div class="total-row">
                <span>Discount:</span>
                <input
                    type="number"
                    wire:model.blur="discount"
                    min="0"
                    step="0.01"
                    style="width: 100px"
                >
            </div>

            <div class="total-row grand-total">
                <span>Total:</span>
                <span>${{ number_format($total, 2) }}</span>
            </div>
        </div>

        <div class="form-actions">
            <button type="submit">Save Invoice</button>
        </div>
    </form>
</div>
```

## Advanced Patterns

### Pattern 7: Conditional Validation

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class ConditionalValidation extends Component
{
    public $accountType = 'personal';
    public $companyName = '';
    public $taxId = '';
    public $individualName = '';
    public $shippingMethod = 'standard';
    public $deliveryDate = '';

    /**
     * Dynamic validation rules based on conditions.
     */
    protected function rules()
    {
        $rules = [
            'accountType' => 'required|in:personal,business',
            'shippingMethod' => 'required|in:standard,express,scheduled',
        ];

        // Conditional rules based on account type
        if ($this->accountType === 'business') {
            $rules['companyName'] = 'required|string|min:3';
            $rules['taxId'] = 'required|string';
        } else {
            $rules['individualName'] = 'required|string|min:3';
        }

        // Conditional rules based on shipping method
        if ($this->shippingMethod === 'scheduled') {
            $rules['deliveryDate'] = 'required|date|after:today';
        }

        return $rules;
    }

    /**
     * Update validation when accountType changes.
     */
    public function updatedAccountType()
    {
        // Clear errors for fields that are no longer relevant
        if ($this->accountType === 'personal') {
            $this->resetErrorBag(['companyName', 'taxId']);
            $this->companyName = '';
            $this->taxId = '';
        } else {
            $this->resetErrorBag('individualName');
            $this->individualName = '';
        }
    }

    /**
     * Update validation when shippingMethod changes.
     */
    public function updatedShippingMethod()
    {
        if ($this->shippingMethod !== 'scheduled') {
            $this->resetErrorBag('deliveryDate');
            $this->deliveryDate = '';
        }
    }

    public function submit()
    {
        $this->validate();

        // Process form
        logger('Conditional form submitted', $this->all());

        session()->flash('success', 'Form submitted successfully!');
    }

    public function render()
    {
        return view('livewire.conditional-validation');
    }
}
```

```blade
<form wire:submit="submit">
    <div class="form-group">
        <label>Account Type</label>
        <select wire:model.live="accountType">
            <option value="personal">Personal</option>
            <option value="business">Business</option>
        </select>
    </div>

    @if($accountType === 'business')
        <div class="form-group">
            <label>Company Name</label>
            <input type="text" wire:model.blur="companyName">
            @error('companyName') <span class="error">{{ $message }}</span> @enderror
        </div>

        <div class="form-group">
            <label>Tax ID</label>
            <input type="text" wire:model.blur="taxId">
            @error('taxId') <span class="error">{{ $message }}</span> @enderror
        </div>
    @else
        <div class="form-group">
            <label>Full Name</label>
            <input type="text" wire:model.blur="individualName">
            @error('individualName') <span class="error">{{ $message }}</span> @enderror
        </div>
    @endif

    <div class="form-group">
        <label>Shipping Method</label>
        <select wire:model.live="shippingMethod">
            <option value="standard">Standard</option>
            <option value="express">Express</option>
            <option value="scheduled">Scheduled Delivery</option>
        </select>
    </div>

    @if($shippingMethod === 'scheduled')
        <div class="form-group">
            <label>Delivery Date</label>
            <input type="date" wire:model.blur="deliveryDate">
            @error('deliveryDate') <span class="error">{{ $message }}</span> @enderror
        </div>
    @endif

    <button type="submit">Submit</button>
</form>
```

### Pattern 8: Error Bags for Multiple Forms

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class MultipleForms extends Component
{
    // Login form
    public $loginEmail = '';
    public $loginPassword = '';

    // Registration form
    public $registerName = '';
    public $registerEmail = '';
    public $registerPassword = '';

    /**
     * Login with separate error bag.
     */
    public function login()
    {
        $this->validate([
            'loginEmail' => 'required|email',
            'loginPassword' => 'required',
        ], [], [], 'login'); // 'login' is the error bag name

        // Process login
        if (auth()->attempt([
            'email' => $this->loginEmail,
            'password' => $this->loginPassword,
        ])) {
            return redirect()->route('dashboard');
        }

        $this->addError('loginPassword', 'Invalid credentials.', 'login');
    }

    /**
     * Register with separate error bag.
     */
    public function register()
    {
        $this->validate([
            'registerName' => 'required|min:3',
            'registerEmail' => 'required|email|unique:users,email',
            'registerPassword' => 'required|min:8',
        ], [], [], 'register'); // 'register' error bag

        $user = \App\Models\User::create([
            'name' => $this->registerName,
            'email' => $this->registerEmail,
            'password' => bcrypt($this->registerPassword),
        ]);

        auth()->login($user);

        return redirect()->route('dashboard');
    }

    public function render()
    {
        return view('livewire.multiple-forms');
    }
}
```

```blade
<div class="auth-container">
    {{-- Login Form --}}
    <div class="form-panel">
        <h2>Login</h2>
        <form wire:submit="login">
            <div class="form-group">
                <label>Email</label>
                <input type="email" wire:model.blur="loginEmail">
                @error('loginEmail', 'login')
                    <span class="error">{{ $message }}</span>
                @enderror
            </div>

            <div class="form-group">
                <label>Password</label>
                <input type="password" wire:model="loginPassword">
                @error('loginPassword', 'login')
                    <span class="error">{{ $message }}</span>
                @enderror
            </div>

            <button type="submit">Login</button>
        </form>
    </div>

    {{-- Registration Form --}}
    <div class="form-panel">
        <h2>Register</h2>
        <form wire:submit="register">
            <div class="form-group">
                <label>Name</label>
                <input type="text" wire:model.blur="registerName">
                @error('registerName', 'register')
                    <span class="error">{{ $message }}</span>
                @enderror
            </div>

            <div class="form-group">
                <label>Email</label>
                <input type="email" wire:model.blur="registerEmail">
                @error('registerEmail', 'register')
                    <span class="error">{{ $message }}</span>
                @enderror
            </div>

            <div class="form-group">
                <label>Password</label>
                <input type="password" wire:model.blur="registerPassword">
                @error('registerPassword', 'register')
                    <span class="error">{{ $message }}</span>
                @enderror
            </div>

            <button type="submit">Register</button>
        </form>
    </div>
</div>
```

## Real-World Applications

### Application 1: E-commerce Checkout Form

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class CheckoutForm extends Component
{
    // Customer info
    #[Validate('required|email')]
    public $email = '';

    // Shipping address
    #[Validate('required|string')]
    public $shippingName = '';

    #[Validate('required|string')]
    public $shippingAddress = '';

    #[Validate('required|string')]
    public $shippingCity = '';

    #[Validate('required|string')]
    public $shippingZip = '';

    // Billing same as shipping
    public $billingDifferent = false;

    // Billing address (conditional)
    public $billingName = '';
    public $billingAddress = '';
    public $billingCity = '';
    public $billingZip = '';

    // Payment
    #[Validate('required|string')]
    public $cardNumber = '';

    #[Validate('required|string')]
    public $cardExpiry = '';

    #[Validate('required|digits:3')]
    public $cardCvv = '';

    protected function rules()
    {
        $rules = [
            'email' => 'required|email',
            'shippingName' => 'required|string',
            'shippingAddress' => 'required|string',
            'shippingCity' => 'required|string',
            'shippingZip' => 'required|string',
            'cardNumber' => 'required|string|size:16',
            'cardExpiry' => 'required|string',
            'cardCvv' => 'required|digits:3',
        ];

        if ($this->billingDifferent) {
            $rules['billingName'] = 'required|string';
            $rules['billingAddress'] = 'required|string';
            $rules['billingCity'] = 'required|string';
            $rules['billingZip'] = 'required|string';
        }

        return $rules;
    }

    public function checkout()
    {
        $validated = $this->validate();

        // Process order
        $order = \App\Models\Order::create([
            'user_id' => auth()->id(),
            'email' => $validated['email'],
            'shipping_address' => [
                'name' => $validated['shippingName'],
                'address' => $validated['shippingAddress'],
                'city' => $validated['shippingCity'],
                'zip' => $validated['shippingZip'],
            ],
            'billing_address' => $this->billingDifferent ? [
                'name' => $validated['billingName'],
                'address' => $validated['billingAddress'],
                'city' => $validated['billingCity'],
                'zip' => $validated['billingZip'],
            ] : null,
        ]);

        // Process payment
        // ...

        return redirect()->route('order.confirmation', $order);
    }

    public function render()
    {
        return view('livewire.checkout-form');
    }
}
```

## Performance Best Practices

### Practice 1: Use wire:model.blur for Better Performance

```blade
{{-- BAD: Validates on every keystroke --}}
<input type="text" wire:model.live="email">

{{-- GOOD: Validates only on blur --}}
<input type="email" wire:model.blur="email">
```

### Practice 2: Validate Only Changed Fields

```php
// Use validateOnly for single field validation
public function updatedEmail()
{
    $this->validateOnly('email');
}
```

### Practice 3: Defer File Upload Validation

```php
// Validate file after upload completes
public function updatedPhoto()
{
    $this->validateOnly('photo');
}
```

## Common Pitfalls

### Pitfall 1: Not Using Form Objects for Complex Forms

```php
// WRONG: All properties in component
class ComplexForm extends Component
{
    public $field1, $field2, $field3; // ... 20 more fields
}

// CORRECT: Use Form object
class ComplexForm extends Component
{
    public MyForm $form;
}
```

### Pitfall 2: Validating on Every Keystroke

```blade
{{-- WRONG: Too many requests --}}
<input wire:model.live="search">

{{-- CORRECT: Debounce input --}}
<input wire:model.live.debounce.500ms="search">
```

### Pitfall 3: Not Handling Array Validation Errors

```blade
{{-- WRONG: Only shows first error --}}
@error('items') {{ $message }} @enderror

{{-- CORRECT: Show errors for each item --}}
@foreach($items as $index => $item)
    @error("items.{$index}.name")
        {{ $message }}
    @enderror
@endforeach
```

## Testing

```php
<?php

namespace Tests\Feature\Livewire;

use App\Livewire\ContactForm;
use Livewire\Livewire;
use Tests\TestCase;

class FormValidationTest extends TestCase
{
    public function test_validates_required_fields()
    {
        Livewire::test(ContactForm::class)
            ->set('name', '')
            ->set('email', '')
            ->call('submit')
            ->assertHasErrors(['name', 'email']);
    }

    public function test_validates_email_format()
    {
        Livewire::test(ContactForm::class)
            ->set('email', 'invalid-email')
            ->call('submit')
            ->assertHasErrors('email');
    }

    public function test_submits_valid_form()
    {
        Livewire::test(ContactForm::class)
            ->set('name', 'John Doe')
            ->set('email', 'john@example.com')
            ->set('message', 'Test message')
            ->call('submit')
            ->assertHasNoErrors()
            ->assertSessionHas('success');
    }
}
```

## Resources

- **Livewire Forms**: https://livewire.laravel.com/docs/forms
- **Validation**: https://livewire.laravel.com/docs/validation
- **File Uploads**: https://livewire.laravel.com/docs/uploads
- **Laravel Validation**: https://laravel.com/docs/validation

## Best Practices Summary

1. **Use Form objects** for complex forms with many fields
2. **Validate on blur** instead of live for better performance
3. **Debounce input** validation to reduce server requests
4. **Use proper error bags** for multiple forms on same page
5. **Implement real-time validation** for critical fields like email/username
6. **Show loading states** during file uploads and validation
7. **Reset forms** after successful submission
8. **Provide clear error messages** with specific guidance
9. **Use custom rules** for complex business logic validation
10. **Test form validation** thoroughly with various input scenarios
