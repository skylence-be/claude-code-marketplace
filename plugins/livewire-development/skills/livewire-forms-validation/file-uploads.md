# File Uploads

Livewire 4 file upload handling with validation and preview.

## Basic File Upload

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
    public $photos = [];

    // Document upload
    #[Validate('required|file|mimes:pdf,doc,docx|max:10240')] // 10MB max
    public $document;

    // Avatar with dimensions
    #[Validate('required|image|dimensions:min_width=100,min_height=100,max_width=1000,max_height=1000')]
    public $avatar;

    public function save()
    {
        $this->validate();

        // Store single file
        $photoPath = $this->photo->store('photos', 'public');

        // Store with custom name
        $documentPath = $this->document->storeAs(
            'documents',
            $this->document->getClientOriginalName(),
            'public'
        );

        // Store multiple files
        $photoPaths = [];
        foreach ($this->photos as $photo) {
            $photoPaths[] = $photo->store('photos', 'public');
        }

        session()->flash('success', 'Files uploaded!');
        $this->reset(['photo', 'photos', 'document', 'avatar']);
    }

    public function render()
    {
        return view('livewire.file-upload-form');
    }
}
```

## File Upload View

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
            Uploading...
        </div>

        {{-- Preview --}}
        @if ($photo)
            <div class="preview">
                <img src="{{ $photo->temporaryUrl() }}" alt="Preview">
            </div>
        @endif
    </div>

    {{-- Multiple files --}}
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

        @if (!empty($photos))
            <div class="photo-grid">
                @foreach($photos as $index => $photo)
                    <div class="photo-item">
                        <img src="{{ $photo->temporaryUrl() }}">
                        <button type="button" wire:click="removePhoto({{ $index }})">
                            Remove
                        </button>
                    </div>
                @endforeach
            </div>
        @endif
    </div>

    {{-- Document upload --}}
    <div class="form-group">
        <label>Document (PDF, DOC)</label>
        <input type="file" wire:model="document" accept=".pdf,.doc,.docx">

        @error('document')
            <span class="error">{{ $message }}</span>
        @enderror

        @if ($document)
            <p>Selected: {{ $document->getClientOriginalName() }}
               ({{ number_format($document->getSize() / 1024, 2) }} KB)</p>
        @endif
    </div>

    <button type="submit" wire:loading.attr="disabled">
        Upload Files
    </button>
</form>
```

## Real-Time Validation

```php
class FileValidation extends Component
{
    use WithFileUploads;

    public $photo;

    /**
     * Validate file immediately after upload.
     */
    public function updatedPhoto()
    {
        $this->validateOnly('photo', [
            'photo' => 'image|max:2048',
        ]);
    }

    /**
     * Remove photo from preview.
     */
    public function removePhoto()
    {
        $this->photo = null;
    }
}
```

## Multiple File Management

```php
class MultipleFiles extends Component
{
    use WithFileUploads;

    public $photos = [];

    public function updatedPhotos()
    {
        $this->validate([
            'photos.*' => 'image|max:1024',
        ]);
    }

    public function removePhoto($index)
    {
        unset($this->photos[$index]);
        $this->photos = array_values($this->photos);
    }

    public function save()
    {
        $this->validate([
            'photos' => 'required|array|min:1|max:5',
            'photos.*' => 'image|max:1024',
        ]);

        $paths = [];
        foreach ($this->photos as $photo) {
            $paths[] = $photo->store('photos', 'public');
        }

        return $paths;
    }
}
```

## Upload Progress with Alpine.js

```blade
<div
    x-data="{ uploading: false, progress: 0 }"
    x-on:livewire-upload-start="uploading = true"
    x-on:livewire-upload-finish="uploading = false"
    x-on:livewire-upload-cancel="uploading = false"
    x-on:livewire-upload-error="uploading = false"
    x-on:livewire-upload-progress="progress = $event.detail.progress"
>
    <input type="file" wire:model="photo">

    <div x-show="uploading">
        <div class="progress-bar">
            <div
                class="progress"
                :style="'width: ' + progress + '%'"
            ></div>
        </div>
        <span x-text="progress + '%'"></span>
    </div>
</div>
```

## Existing File Replacement

```php
class AvatarUpload extends Component
{
    use WithFileUploads;

    public $avatar;
    public $currentAvatar;

    public function mount()
    {
        $this->currentAvatar = auth()->user()->avatar;
    }

    public function save()
    {
        $this->validate([
            'avatar' => 'required|image|max:2048',
        ]);

        $user = auth()->user();

        // Delete old avatar
        if ($user->avatar) {
            \Storage::disk('public')->delete($user->avatar);
        }

        // Store new avatar
        $path = $this->avatar->store('avatars', 'public');

        $user->update(['avatar' => $path]);

        $this->currentAvatar = $path;
        $this->avatar = null;

        session()->flash('success', 'Avatar updated!');
    }
}
```

```blade
<div>
    @if($currentAvatar)
        <img src="{{ Storage::url($currentAvatar) }}" alt="Current avatar">
    @endif

    <input type="file" wire:model="avatar">

    @if($avatar)
        <img src="{{ $avatar->temporaryUrl() }}" alt="New avatar preview">
        <button wire:click="save">Save New Avatar</button>
        <button wire:click="$set('avatar', null)">Cancel</button>
    @endif
</div>
```

## File Validation Rules

```php
// Common validation rules
$rules = [
    // Images
    'photo' => 'image|max:2048',  // Any image, 2MB max
    'photo' => 'image|mimes:jpg,jpeg,png|max:2048',  // Specific formats

    // Dimensions
    'photo' => 'image|dimensions:min_width=100,min_height=100',
    'photo' => 'image|dimensions:max_width=1000,max_height=1000',
    'photo' => 'image|dimensions:ratio=1/1',  // Square

    // Documents
    'document' => 'file|mimes:pdf,doc,docx|max:10240',  // 10MB

    // Multiple files
    'photos' => 'array|min:1|max:5',
    'photos.*' => 'image|max:1024',

    // Required with
    'photo' => 'required_without:url',  // Required if URL not provided
];
```

## S3/Cloud Storage

```php
class CloudUpload extends Component
{
    use WithFileUploads;

    public $file;

    public function save()
    {
        $this->validate(['file' => 'required|file|max:10240']);

        // Store to S3
        $path = $this->file->store('uploads', 's3');

        // Store with public visibility
        $path = $this->file->storePublicly('uploads', 's3');

        // Get public URL
        $url = \Storage::disk('s3')->url($path);

        return $url;
    }
}
```
