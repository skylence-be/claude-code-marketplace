# Reactive Attributes

Livewire 4 attributes for reactive properties and computed values.

## #[Reactive] - Parent-Child Communication

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Reactive;

class ChildComponent extends Component
{
    /**
     * Reactive property automatically updates when parent changes it.
     * Without #[Reactive], changes from parent won't reflect in child.
     */
    #[Reactive]
    public $userId;

    #[Reactive]
    public $status = 'active';

    public function updatedUserId($value)
    {
        // React to userId changes from parent
        logger("User ID changed to: {$value}");
    }

    public function render()
    {
        return view('livewire.child-component');
    }
}

class ParentComponent extends Component
{
    public $selectedUserId = 1;

    public function changeUser($userId)
    {
        $this->selectedUserId = $userId;
        // Child component automatically sees this change
    }

    public function render()
    {
        return view('livewire.parent-component');
    }
}
```

```blade
{{-- parent-component.blade.php --}}
<div>
    <select wire:model.live="selectedUserId">
        <option value="1">User 1</option>
        <option value="2">User 2</option>
    </select>

    <livewire:child-component :userId="$selectedUserId" />
</div>

{{-- child-component.blade.php --}}
<div>
    <p>Watching User ID: {{ $userId }}</p>
</div>
```

## #[Computed] - Cached Computed Properties

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use App\Models\User;

class UserProfile extends Component
{
    public $userId;

    /**
     * Computed property with automatic caching.
     * Only re-computed when $userId changes.
     */
    #[Computed]
    public function user()
    {
        return User::with('profile')->findOrFail($this->userId);
    }

    /**
     * Computed property that depends on another computed property.
     */
    #[Computed]
    public function posts()
    {
        return $this->user->posts()->latest()->limit(10)->get();
    }

    /**
     * Computed property with calculations.
     */
    #[Computed]
    public function stats()
    {
        return [
            'total_posts' => $this->posts->count(),
            'total_likes' => $this->posts->sum('likes_count'),
        ];
    }

    /**
     * Invalidate cache manually if needed.
     */
    public function refreshUser()
    {
        unset($this->user); // Clear cached computed property
    }

    public function render()
    {
        return view('livewire.user-profile');
    }
}
```

```blade
<div>
    {{-- Access computed properties like regular properties --}}
    <h2>{{ $this->user->name }}</h2>
    <p>{{ $this->user->profile->bio }}</p>

    <div class="stats">
        <span>Posts: {{ $this->stats['total_posts'] }}</span>
        <span>Likes: {{ $this->stats['total_likes'] }}</span>
    </div>

    @foreach($this->posts as $post)
        <article>{{ $post->title }}</article>
    @endforeach

    <button wire:click="refreshUser">Refresh</button>
</div>
```

## #[Locked] - Security Properties

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Locked;
use App\Models\Order;

class OrderDetails extends Component
{
    /**
     * Locked property - cannot be tampered with from frontend.
     * Throws PropertyCannotBeSetException if client tries to change it.
     */
    #[Locked]
    public $orderId;

    #[Locked]
    public $userId;

    public $notes = '';

    public function mount($orderId)
    {
        $this->orderId = $orderId;
        $this->userId = auth()->id();
    }

    public function updateNotes()
    {
        // Safe to use locked properties - they're trusted
        $order = Order::where('id', $this->orderId)
            ->where('user_id', $this->userId)
            ->firstOrFail();

        $order->update(['notes' => $this->notes]);
    }

    public function render()
    {
        $order = Order::where('id', $this->orderId)
            ->where('user_id', $this->userId)
            ->firstOrFail();

        return view('livewire.order-details', ['order' => $order]);
    }
}
```

## #[Modelable] - Two-Way Parent-Child Binding

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Modelable;

class SearchInput extends Component
{
    /**
     * Two-way binding with parent component.
     * Changes in parent reflect here and vice versa.
     */
    #[Modelable]
    public $query = '';

    public $suggestions = [];

    public function updatedQuery()
    {
        $this->suggestions = $this->fetchSuggestions($this->query);
    }

    private function fetchSuggestions($query)
    {
        if (strlen($query) < 2) {
            return [];
        }

        return \App\Models\Product::where('name', 'like', "%{$query}%")
            ->limit(5)
            ->pluck('name')
            ->toArray();
    }

    public function selectSuggestion($suggestion)
    {
        $this->query = $suggestion;
        $this->suggestions = [];
    }

    public function render()
    {
        return view('livewire.search-input');
    }
}

class ProductSearch extends Component
{
    public $searchQuery = '';

    public function updatedSearchQuery()
    {
        $this->search();
    }

    public function render()
    {
        return view('livewire.product-search');
    }
}
```

```blade
{{-- product-search.blade.php --}}
<div>
    {{-- Two-way binding with child component --}}
    <livewire:search-input wire:model="searchQuery" />

    <p>Searching for: "{{ $searchQuery }}"</p>
</div>

{{-- search-input.blade.php --}}
<div class="search-input">
    <input
        type="text"
        wire:model.live.debounce.300ms="query"
        placeholder="Search..."
    >

    @if(count($suggestions) > 0)
        <ul class="suggestions">
            @foreach($suggestions as $suggestion)
                <li wire:click="selectSuggestion('{{ $suggestion }}')">
                    {{ $suggestion }}
                </li>
            @endforeach
        </ul>
    @endif
</div>
```

## Combining Attributes

```php
class AdvancedComponent extends Component
{
    #[Locked]
    public $userId;        // Security - can't be changed

    #[Reactive]
    public $filters;       // Receives from parent

    #[Modelable]
    public $selected = ''; // Two-way with parent

    #[Computed]
    public function items()
    {
        return Item::where('user_id', $this->userId)
            ->filter($this->filters)
            ->get();
    }
}
```
