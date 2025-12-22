# Lifecycle Hooks

Livewire 4 component lifecycle hooks for initialization, updates, and cleanup.

## Complete Lifecycle Overview

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\On;

class LifecycleDemo extends Component
{
    public $data = [];
    public $counter = 0;

    /**
     * Called when component is first created.
     * Use for initialization logic.
     * Only runs on initial page load.
     */
    public function mount($initialValue = 0)
    {
        $this->counter = $initialValue;
        logger('Component mounted with counter: ' . $initialValue);
    }

    /**
     * Called once when component class boots.
     * Use for event listeners or one-time setup.
     * Runs before mount().
     */
    public function boot()
    {
        logger('Component booted');
    }

    /**
     * Called on every request (including initial).
     * Use for resetting state or reloading data.
     * Runs after mount/hydrate.
     */
    public function hydrate()
    {
        logger('Component hydrated on request');
    }

    /**
     * Called before any property updates.
     * Receives property name and new value.
     */
    public function updating($name, $value)
    {
        logger("Updating {$name} to {$value}");
    }

    /**
     * Called after any property updates.
     * Receives property name and new value.
     */
    public function updated($name, $value)
    {
        logger("Updated {$name} to {$value}");
    }

    /**
     * Called before specific property updates.
     * Method name: updating{PropertyName}
     */
    public function updatingCounter($value)
    {
        if ($value < 0) {
            $this->addError('counter', 'Counter cannot be negative');
            return;
        }
    }

    /**
     * Called after specific property updates.
     * Method name: updated{PropertyName}
     */
    public function updatedCounter($value)
    {
        if ($value >= 10) {
            session()->flash('message', 'Counter reached 10!');
        }
    }

    /**
     * Called before component is dehydrated (serialized).
     * Use for cleanup before sending to client.
     */
    public function dehydrate()
    {
        logger('Component dehydrating');
    }

    /**
     * Called when component is about to be removed.
     * Use for cleanup logic.
     */
    public function destroy()
    {
        logger('Component destroying');
    }

    public function render()
    {
        logger('Rendering component');
        return view('livewire.lifecycle-demo');
    }
}
```

## mount() - Initial Setup

```php
class UserProfile extends Component
{
    public $user;
    public $posts;

    /**
     * mount() receives route parameters and component props.
     * Use for loading initial data and setting defaults.
     */
    public function mount(User $user, $showPosts = true)
    {
        $this->user = $user;

        if ($showPosts) {
            $this->posts = $user->posts()->latest()->limit(10)->get();
        }
    }
}

// Usage in blade
<livewire:user-profile :user="$user" :showPosts="true" />

// Or via route
Route::get('/users/{user}', UserProfile::class);
```

## hydrate() - Every Request

```php
class Dashboard extends Component
{
    public $notifications = [];

    /**
     * hydrate() runs on every Livewire request.
     * Good for re-establishing connections or refreshing data.
     */
    public function hydrate()
    {
        // Reload notifications on every request
        $this->notifications = auth()->user()
            ->notifications()
            ->unread()
            ->get();
    }
}
```

## Property Update Hooks

```php
class SearchComponent extends Component
{
    public $search = '';
    public $category = '';
    public $filters = [];

    /**
     * Generic updating hook - runs before any property changes.
     */
    public function updating($property, $value)
    {
        // Log all property changes
        logger("Property {$property} changing to", ['value' => $value]);
    }

    /**
     * Generic updated hook - runs after any property changes.
     */
    public function updated($property, $value)
    {
        // Reset pagination when any filter changes
        $this->resetPage();
    }

    /**
     * Specific property hook - runs before 'search' changes.
     */
    public function updatingSearch($value)
    {
        // Sanitize search input
        $this->search = strip_tags($value);
    }

    /**
     * Specific property hook - runs after 'search' changes.
     */
    public function updatedSearch($value)
    {
        // Validate minimum length
        if (strlen($value) > 0 && strlen($value) < 3) {
            $this->addError('search', 'Search must be at least 3 characters');
        } else {
            $this->resetErrorBag('search');
        }
    }

    /**
     * Nested property hook - for array/object properties.
     * Format: updated{Property}{Key}
     */
    public function updatedFiltersCategory($value)
    {
        // Runs when $filters['category'] changes
        logger("Category filter changed to: {$value}");
    }
}
```

## Lifecycle Order

```php
class LifecycleOrder extends Component
{
    /**
     * Lifecycle execution order:
     *
     * Initial Request:
     * 1. boot()
     * 2. mount()
     * 3. hydrate()
     * 4. render()
     * 5. dehydrate()
     *
     * Subsequent Requests:
     * 1. boot()
     * 2. hydrate()
     * 3. updating() / updatingProperty()
     * 4. updated() / updatedProperty()
     * 5. render()
     * 6. dehydrate()
     */
}
```

## Practical Examples

### Form with Validation on Blur

```php
class ContactForm extends Component
{
    public $name = '';
    public $email = '';
    public $message = '';

    public function updatedEmail($value)
    {
        // Validate email format as user types/blurs
        $this->validateOnly('email', [
            'email' => 'required|email|max:255',
        ]);
    }

    public function updatedName($value)
    {
        // Auto-capitalize name
        $this->name = ucwords(strtolower($value));
    }
}
```

### Slug Auto-Generation

```php
class PostEditor extends Component
{
    public $title = '';
    public $slug = '';
    public $slugManuallyEdited = false;

    public function updatedTitle($value)
    {
        // Auto-generate slug unless manually edited
        if (!$this->slugManuallyEdited) {
            $this->slug = Str::slug($value);
        }
    }

    public function updatingSlug($value)
    {
        // Mark as manually edited when user changes it
        $this->slugManuallyEdited = true;
    }
}
```

### Dependent Dropdowns

```php
class LocationSelector extends Component
{
    public $country = '';
    public $state = '';
    public $city = '';
    public $states = [];
    public $cities = [];

    public function updatedCountry($value)
    {
        // Reset dependent fields
        $this->state = '';
        $this->city = '';
        $this->cities = [];

        // Load states for selected country
        $this->states = State::where('country_id', $value)->get();
    }

    public function updatedState($value)
    {
        // Reset city
        $this->city = '';

        // Load cities for selected state
        $this->cities = City::where('state_id', $value)->get();
    }
}
```

### Search with Debounce Validation

```php
class UserSearch extends Component
{
    public $search = '';
    public $results = [];
    public $searching = false;

    public function updatingSearch()
    {
        $this->searching = true;
    }

    public function updatedSearch($value)
    {
        if (strlen($value) >= 3) {
            $this->results = User::where('name', 'like', "%{$value}%")
                ->limit(10)
                ->get();
        } else {
            $this->results = [];
        }

        $this->searching = false;
    }
}
```

```blade
<div>
    <input
        type="text"
        wire:model.live.debounce.500ms="search"
        placeholder="Search users..."
    >

    <span wire:loading wire:target="search">Searching...</span>

    @if(strlen($search) > 0 && strlen($search) < 3)
        <p class="hint">Type at least 3 characters</p>
    @endif

    @foreach($results as $user)
        <div>{{ $user->name }}</div>
    @endforeach
</div>
```
