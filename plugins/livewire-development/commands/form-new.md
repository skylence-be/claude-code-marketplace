---
description: Create Livewire 4 form with validation and state management
model: claude-sonnet-4-5
---

Create a Livewire 4 form component with validation.

## Form Specification

$ARGUMENTS

## Livewire 4 Form Patterns

### 1. **Form Object Pattern** (Recommended)

```php
<?php

namespace App\Livewire\Forms;

use Livewire\Form;
use Livewire\Attributes\Validate;

class PostForm extends Form
{
    #[Validate('required|min:3')]
    public string $title = '';

    #[Validate('required')]
    public string $content = '';

    #[Validate('nullable|date')]
    public ?string $published_at = null;

    public function store()
    {
        $this->validate();

        Post::create($this->only(['title', 'content', 'published_at']));

        $this->reset();
    }

    public function update(Post $post)
    {
        $this->validate();

        $post->update($this->only(['title', 'content', 'published_at']));
    }
}
```

**Component Using Form**
```php
<?php

namespace App\Livewire;

use App\Livewire\Forms\PostForm;
use Livewire\Component;

class CreatePost extends Component
{
    public PostForm $form;

    public function save()
    {
        $this->form->store();

        session()->flash('success', 'Post created!');

        return $this->redirect('/posts');
    }

    public function render()
    {
        return view('livewire.create-post');
    }
}
```

**Blade Template**
```blade
<form wire:submit="save">
    <div class="mb-4">
        <label for="title" class="block mb-2">Title</label>
        <input
            type="text"
            id="title"
            wire:model="form.title"
            class="w-full px-4 py-2 border rounded"
        >
        @error('form.title')
            <span class="text-red-600 text-sm">{{ $message }}</span>
        @enderror
    </div>

    <div class="mb-4">
        <label for="content" class="block mb-2">Content</label>
        <textarea
            id="content"
            wire:model="form.content"
            rows="5"
            class="w-full px-4 py-2 border rounded"
        ></textarea>
        @error('form.content')
            <span class="text-red-600 text-sm">{{ $message }}</span>
        @enderror
    </div>

    <button
        type="submit"
        wire:loading.attr="disabled"
        class="px-4 py-2 bg-blue-600 text-white rounded"
    >
        <span wire:loading.remove>Save</span>
        <span wire:loading>Saving...</span>
    </button>
</form>
```

### 2. **Inline Form Pattern**

```php
class CreatePost extends Component
{
    #[Validate('required|min:3')]
    public string $title = '';

    #[Validate('required')]
    public string $content = '';

    public function save()
    {
        $validated = $this->validate();

        Post::create($validated);

        $this->reset();
    }
}
```

### 3. **Real-time Validation**

```php
#[Validate('required|email')]
public string $email = '';

public function updated($property)
{
    $this->validateOnly($property);
}
```

### 4. **Custom Validation Messages**

```php
protected function rules()
{
    return [
        'title' => 'required|min:3',
        'email' => 'required|email',
    ];
}

protected function messages()
{
    return [
        'title.required' => 'The post title is required.',
        'email.email' => 'Please provide a valid email address.',
    ];
}
```

Generate complete Livewire 4 forms with proper validation and UX.
