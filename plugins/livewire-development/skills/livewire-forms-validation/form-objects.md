# Form Objects

Livewire Form class for encapsulating form logic and validation.

## Basic Form Object

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
    }
}
```

## Using Form Objects in Components

```php
<?php

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
        return view('livewire.create-post', [
            'categories' => \App\Models\Category::all(),
        ]);
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
        return view('livewire.edit-post', [
            'categories' => \App\Models\Category::all(),
        ]);
    }
}
```

## Form View Template

```blade
{{-- resources/views/livewire/post-form.blade.php --}}
<form wire:submit="{{ $isEditing ? 'update' : 'save' }}">
    <div class="form-group">
        <label for="title">Title</label>
        <input
            type="text"
            id="title"
            wire:model.blur="form.title"
            @error('form.title') aria-invalid="true" @enderror
        >
        @error('form.title')
            <span class="error">{{ $message }}</span>
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

    <button type="submit" wire:loading.attr="disabled">
        <span wire:loading.remove>{{ $isEditing ? 'Update' : 'Create' }} Post</span>
        <span wire:loading>Saving...</span>
    </button>
</form>
```

## Form with Computed Properties

```php
<?php

namespace App\Livewire\Forms;

use Livewire\Form;
use Livewire\Attributes\Validate;
use Livewire\Attributes\Computed;

class OrderForm extends Form
{
    #[Validate('required|array|min:1')]
    public $items = [];

    #[Validate('required|numeric|min:0')]
    public $discount = 0;

    #[Validate('required|numeric|min:0|max:100')]
    public $taxRate = 10;

    #[Computed]
    public function subtotal()
    {
        return collect($this->items)->sum(function ($item) {
            return ($item['price'] ?? 0) * ($item['quantity'] ?? 0);
        });
    }

    #[Computed]
    public function taxAmount()
    {
        return $this->subtotal * ($this->taxRate / 100);
    }

    #[Computed]
    public function total()
    {
        return $this->subtotal + $this->taxAmount - $this->discount;
    }

    public function addItem($productId)
    {
        $product = \App\Models\Product::find($productId);

        $this->items[] = [
            'product_id' => $product->id,
            'name' => $product->name,
            'price' => $product->price,
            'quantity' => 1,
        ];
    }

    public function removeItem($index)
    {
        unset($this->items[$index]);
        $this->items = array_values($this->items);
    }
}
```

## Form Reset and State Management

```php
class ContactForm extends Form
{
    public $name = '';
    public $email = '';
    public $message = '';

    /**
     * Reset all form fields.
     */
    public function resetForm()
    {
        $this->reset();
    }

    /**
     * Reset specific fields.
     */
    public function resetMessage()
    {
        $this->reset('message');
    }

    /**
     * Fill from array.
     */
    public function fill(array $data)
    {
        $this->name = $data['name'] ?? '';
        $this->email = $data['email'] ?? '';
        $this->message = $data['message'] ?? '';
    }

    /**
     * Get all values as array.
     */
    public function toArray()
    {
        return [
            'name' => $this->name,
            'email' => $this->email,
            'message' => $this->message,
        ];
    }
}

// In component
class Contact extends Component
{
    public ContactForm $form;

    public function submit()
    {
        $this->form->validate();

        Mail::to('admin@example.com')
            ->send(new ContactMail($this->form->toArray()));

        $this->form->resetForm();

        session()->flash('success', 'Message sent!');
    }
}
```
