---
name: livewire-forms-validation
description: Master Livewire 4 form handling including form objects, real-time validation, custom validation rules, file uploads, multi-step forms, and error handling. Use when building complex forms, implementing validation logic, or handling user input.
---

# Livewire Forms and Validation

Comprehensive guide to building robust forms in Livewire 4.

## When to Use This Skill

- Building complex forms with multiple fields and validation rules
- Implementing real-time validation with instant user feedback
- Creating multi-step form wizards with state preservation
- Handling file uploads with progress indicators and validation
- Building dynamic forms with repeatable field groups
- Implementing custom validation rules for business logic

## Pattern Files

| Pattern | File | Use Case |
|---------|------|----------|
| Form Objects | [form-objects.md](form-objects.md) | Livewire Form class, reusable validation |
| Validation Patterns | [validation-patterns.md](validation-patterns.md) | #[Validate], real-time validation, custom rules |
| File Uploads | [file-uploads.md](file-uploads.md) | WithFileUploads, progress, preview |
| Multi-Step Forms | [multi-step-forms.md](multi-step-forms.md) | Form wizards, step validation |
| Dynamic Arrays | [dynamic-arrays.md](dynamic-arrays.md) | Repeater fields, nested validation |

## Quick Reference

### Basic Form Component

```php
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
        session()->flash('success', 'Message sent!');
        $this->reset();
    }
}
```

### Form Objects

```php
use Livewire\Form;
use Livewire\Attributes\Validate;

class PostForm extends Form
{
    #[Validate('required|string|min:3')]
    public $title = '';

    #[Validate('required|string|min:100')]
    public $content = '';

    public function store()
    {
        $this->validate();
        return Post::create($this->all());
    }
}

class CreatePost extends Component
{
    public PostForm $form;

    public function save()
    {
        $post = $this->form->store();
        return redirect()->route('posts.show', $post);
    }
}
```

### Validation Timing

```blade
{{-- Live validation (every keystroke) --}}
<input wire:model.live="email">

{{-- Blur validation (on focus loss) --}}
<input wire:model.blur="email">

{{-- Debounced validation --}}
<input wire:model.live.debounce.500ms="search">

{{-- Lazy (on submit only) --}}
<input wire:model.lazy="description">
```

### Error Display

```blade
<input wire:model.blur="email" @error('email') class="border-red-500" @enderror>
@error('email')
    <span class="text-red-500">{{ $message }}</span>
@enderror
```

## Best Practices

1. **Use Form objects** for complex forms with many fields
2. **Validate on blur** instead of live for better performance
3. **Debounce input** validation to reduce server requests
4. **Use proper error bags** for multiple forms on same page
5. **Show loading states** during file uploads and validation

## Common Pitfalls

1. **Not using Form objects** - Component gets cluttered with many properties
2. **Validating on every keystroke** - Too many server requests
3. **Not handling array validation** - Missing per-item error display
4. **Not resetting forms** - Old data persists after submission
