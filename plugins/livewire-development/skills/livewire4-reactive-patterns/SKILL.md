---
name: livewire4-reactive-patterns
description: Master Livewire 4 reactive patterns including attributes (#[Reactive], #[Computed], #[Locked], #[Modelable]), wire directives, lifecycle hooks, and component communication. Use when building interactive components, managing state, or implementing real-time features.
---

# Livewire 4 Reactive Patterns

Comprehensive guide to implementing reactive patterns in Livewire 4, covering attributes, wire directives, lifecycle hooks, event dispatching, component communication, and building highly interactive user interfaces with minimal JavaScript.

## When to Use This Skill

- Building real-time interactive components with reactive state management
- Implementing computed properties that automatically update when dependencies change
- Creating reusable components with locked properties for security
- Building parent-child component communication patterns
- Implementing wire:model bindings with various modifiers (live, blur, debounce)
- Managing component lifecycle with hooks (mount, hydrate, updating, updated)
- Dispatching and listening to events between components
- Creating nested component hierarchies with proper data flow
- Implementing loading states and optimistic UI updates
- Building dynamic forms with real-time validation and feedback

## Core Concepts

### 1. Reactive Attributes
- **#[Reactive]**: Property automatically updates when changed by parent component
- **#[Computed]**: Cached computed property that updates when dependencies change
- **#[Locked]**: Property cannot be changed after initialization (security)
- **#[Modelable]**: Two-way binding between parent and child components
- **#[Lazy]**: Defers property updates until component action completes

### 2. Wire Directives
- **wire:model**: Two-way data binding between input and component property
- **wire:click**: Trigger component method on click event
- **wire:submit**: Handle form submission
- **wire:loading**: Show/hide elements during component updates
- **wire:poll**: Automatically refresh component at intervals

### 3. Lifecycle Hooks
- **mount()**: Called when component is first instantiated
- **hydrate()**: Called when component is rehydrated on subsequent requests
- **updating()**: Called before property is updated
- **updated()**: Called after property is updated
- **booted()**: Called once when component class is first loaded

### 4. Component Communication
- **dispatch()**: Send events to other components or JavaScript
- **listen()**: Receive events from other components or browser
- **$parent**: Access parent component properties
- **$children**: Interact with child components
- **Global events**: Broadcast events to all components on page

### 5. State Management
- **Public properties**: Automatically synced between requests
- **Protected/private properties**: Not synced, reset on each request
- **$wire**: JavaScript object for programmatic interaction
- **Entangle**: Sync Alpine.js data with Livewire properties

## Quick Start

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Reactive;
use Livewire\Attributes\Computed;

class Counter extends Component
{
    // Reactive property
    public $count = 0;

    // Computed property
    #[Computed]
    public function doubled()
    {
        return $this->count * 2;
    }

    // Action method
    public function increment()
    {
        $this->count++;
    }

    public function render()
    {
        return view('livewire.counter');
    }
}
```

```blade
<div>
    <h2>Count: {{ $count }}</h2>
    <h3>Doubled: {{ $this->doubled }}</h3>

    <button wire:click="increment">Increment</button>
</div>
```

## Fundamental Patterns

### Pattern 1: Reactive Attribute for Parent-Child Communication

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

    /**
     * This method is called whenever reactive properties change.
     */
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
    public $userStatus = 'active';

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
    <h2>Parent Component</h2>

    <select wire:model.live="selectedUserId">
        <option value="1">User 1</option>
        <option value="2">User 2</option>
        <option value="3">User 3</option>
    </select>

    {{-- Pass reactive properties to child --}}
    <livewire:child-component
        :userId="$selectedUserId"
        :status="$userStatus"
    />
</div>

{{-- child-component.blade.php --}}
<div>
    <h3>Child Component</h3>
    <p>Watching User ID: {{ $userId }}</p>
    <p>Status: {{ $status }}</p>
</div>
```

### Pattern 2: Computed Properties with Caching

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use App\Models\User;
use App\Models\Post;

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
        return $this->user->posts()
            ->latest()
            ->limit(10)
            ->get();
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
            'avg_comments' => $this->posts->avg('comments_count'),
        ];
    }

    /**
     * You can invalidate cache manually if needed.
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
        <span>Avg Comments: {{ number_format($this->stats['avg_comments'], 1) }}</span>
    </div>

    <h3>Recent Posts</h3>
    @foreach($this->posts as $post)
        <article>
            <h4>{{ $post->title }}</h4>
            <p>{{ $post->excerpt }}</p>
        </article>
    @endforeach

    <button wire:click="refreshUser">Refresh</button>
</div>
```

### Pattern 3: Locked Properties for Security

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Locked;
use Livewire\Attributes\Reactive;
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

    /**
     * Normal property - can be modified.
     */
    public $notes = '';

    /**
     * Initialize locked properties in mount.
     */
    public function mount($orderId)
    {
        $this->orderId = $orderId;
        $this->userId = auth()->id();
    }

    /**
     * Safe to use locked properties in methods.
     */
    public function updateNotes()
    {
        $order = Order::where('id', $this->orderId)
            ->where('user_id', $this->userId)
            ->firstOrFail();

        $order->update(['notes' => $this->notes]);

        session()->flash('message', 'Notes updated successfully.');
    }

    public function render()
    {
        $order = Order::with('items')
            ->where('id', $this->orderId)
            ->where('user_id', $this->userId)
            ->firstOrFail();

        return view('livewire.order-details', [
            'order' => $order,
        ]);
    }
}
```

```blade
<div>
    <h2>Order #{{ $orderId }}</h2>

    {{-- User cannot modify orderId from browser devtools --}}
    <input type="hidden" wire:model="orderId">

    <div class="order-items">
        @foreach($order->items as $item)
            <div>{{ $item->name }} - ${{ $item->price }}</div>
        @endforeach
    </div>

    <textarea
        wire:model.blur="notes"
        placeholder="Order notes"
    ></textarea>

    <button wire:click="updateNotes">Save Notes</button>
</div>
```

### Pattern 4: Modelable for Two-Way Parent-Child Binding

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

    /**
     * Local state not shared with parent.
     */
    public $suggestions = [];

    public function updatedQuery()
    {
        // Update suggestions when query changes
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
    public $results = [];

    public function updatedSearchQuery()
    {
        $this->search();
    }

    public function search()
    {
        $this->results = \App\Models\Product::where('name', 'like', "%{$this->searchQuery}%")
            ->get();
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
    <h2>Product Search</h2>

    {{-- Two-way binding with child component --}}
    <livewire:search-input wire:model="searchQuery" />

    <div class="results">
        <p>Searching for: "{{ $searchQuery }}"</p>
        @foreach($results as $product)
            <div>{{ $product->name }} - ${{ $product->price }}</div>
        @endforeach
    </div>
</div>

{{-- search-input.blade.php --}}
<div class="search-input">
    <input
        type="text"
        wire:model.live.debounce.300ms="query"
        placeholder="Search products..."
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

### Pattern 5: Wire Model with Modifiers

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class FormModifiers extends Component
{
    // Live update - updates on every keystroke
    public $liveInput = '';

    // Blur - updates when input loses focus
    public $blurInput = '';

    // Debounce - updates after user stops typing
    public $debounceInput = '';

    // Throttle - updates at most every X milliseconds
    public $throttleInput = '';

    // Lazy - updates on blur or form submit
    public $lazyInput = '';

    // Number - casts to number
    public $quantity = 1;

    // Boolean - casts to boolean
    public $isActive = false;

    /**
     * Track changes for demonstration.
     */
    public $updateCount = 0;

    public function updated($propertyName)
    {
        $this->updateCount++;
    }

    public function render()
    {
        return view('livewire.form-modifiers');
    }
}
```

```blade
<div>
    <h2>Wire Model Modifiers</h2>

    <div class="form-group">
        <label>Live (updates immediately)</label>
        <input type="text" wire:model.live="liveInput">
        <p>Value: {{ $liveInput }}</p>
    </div>

    <div class="form-group">
        <label>Blur (updates on blur)</label>
        <input type="text" wire:model.blur="blurInput">
        <p>Value: {{ $blurInput }}</p>
    </div>

    <div class="form-group">
        <label>Debounce 500ms (updates after pause)</label>
        <input type="text" wire:model.live.debounce.500ms="debounceInput">
        <p>Value: {{ $debounceInput }}</p>
    </div>

    <div class="form-group">
        <label>Throttle 1000ms (max once per second)</label>
        <input type="text" wire:model.live.throttle.1000ms="throttleInput">
        <p>Value: {{ $throttleInput }}</p>
    </div>

    <div class="form-group">
        <label>Lazy (updates on blur or submit)</label>
        <input type="text" wire:model.lazy="lazyInput">
        <p>Value: {{ $lazyInput }}</p>
    </div>

    <div class="form-group">
        <label>Number (auto-cast)</label>
        <input type="number" wire:model.number="quantity">
        <p>Value: {{ $quantity }} (Type: {{ gettype($quantity) }})</p>
    </div>

    <div class="form-group">
        <label>Boolean (auto-cast)</label>
        <input type="checkbox" wire:model.boolean="isActive">
        <p>Active: {{ $isActive ? 'Yes' : 'No' }} (Type: {{ gettype($isActive) }})</p>
    </div>

    <p>Total Updates: {{ $updateCount }}</p>
</div>
```

### Pattern 6: Wire Click and Action Methods

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class ActionMethods extends Component
{
    public $count = 0;
    public $items = [];
    public $confirmDelete = false;

    /**
     * Simple action method.
     */
    public function increment()
    {
        $this->count++;
    }

    /**
     * Action with parameters.
     */
    public function add($amount)
    {
        $this->count += $amount;
    }

    /**
     * Action with multiple parameters.
     */
    public function addItem($name, $quantity)
    {
        $this->items[] = [
            'name' => $name,
            'quantity' => $quantity,
        ];
    }

    /**
     * Remove item by index.
     */
    public function removeItem($index)
    {
        unset($this->items[$index]);
        $this->items = array_values($this->items); // Re-index
    }

    /**
     * Prevent default event behavior.
     */
    public function delete()
    {
        if (!$this->confirmDelete) {
            $this->confirmDelete = true;
            return;
        }

        // Perform delete
        $this->items = [];
        $this->count = 0;
        $this->confirmDelete = false;
    }

    public function render()
    {
        return view('livewire.action-methods');
    }
}
```

```blade
<div>
    <h2>Count: {{ $count }}</h2>

    {{-- Simple click --}}
    <button wire:click="increment">+1</button>

    {{-- Click with parameter --}}
    <button wire:click="add(5)">+5</button>
    <button wire:click="add(10)">+10</button>

    {{-- Click with multiple parameters --}}
    <button wire:click="addItem('Apple', 3)">Add 3 Apples</button>
    <button wire:click="addItem('Orange', 5)">Add 5 Oranges</button>

    {{-- Prevent default and stop propagation --}}
    <form wire:submit.prevent="save">
        <button type="submit">Save</button>
    </form>

    <div class="items">
        @foreach($items as $index => $item)
            <div>
                {{ $item['name'] }} ({{ $item['quantity'] }})
                <button wire:click="removeItem({{ $index }})">Remove</button>
            </div>
        @endforeach
    </div>

    {{-- Confirmation pattern --}}
    @if($confirmDelete)
        <div class="confirm">
            <p>Are you sure?</p>
            <button wire:click="delete">Yes, Delete</button>
            <button wire:click="$set('confirmDelete', false)">Cancel</button>
        </div>
    @else
        <button wire:click="delete" class="danger">Delete All</button>
    @endif
</div>
```

### Pattern 7: Wire Loading States

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Illuminate\Support\Facades\Http;

class LoadingStates extends Component
{
    public $posts = [];
    public $search = '';
    public $isDeleting = false;

    /**
     * Simulate slow API call.
     */
    public function fetchPosts()
    {
        sleep(2); // Simulate delay

        $this->posts = \App\Models\Post::latest()
            ->limit(10)
            ->get()
            ->toArray();
    }

    /**
     * Search with loading state.
     */
    public function searchPosts()
    {
        sleep(1); // Simulate delay

        $this->posts = \App\Models\Post::where('title', 'like', "%{$this->search}%")
            ->get()
            ->toArray();
    }

    /**
     * Delete with loading state.
     */
    public function deletePost($postId)
    {
        $this->isDeleting = true;
        sleep(1); // Simulate delay

        \App\Models\Post::destroy($postId);
        $this->fetchPosts();
        $this->isDeleting = false;
    }

    public function render()
    {
        return view('livewire.loading-states');
    }
}
```

```blade
<div>
    <h2>Loading States</h2>

    {{-- Default loading indicator --}}
    <button wire:click="fetchPosts">
        Fetch Posts
        <span wire:loading>Loading...</span>
    </button>

    {{-- Loading with target --}}
    <button wire:click="searchPosts">
        Search
        <span wire:loading.delay wire:target="searchPosts">
            Searching...
        </span>
    </button>

    {{-- Hide element while loading --}}
    <div wire:loading.remove wire:target="fetchPosts">
        Content hidden during loading
    </div>

    {{-- Show element while loading --}}
    <div wire:loading.flex wire:target="fetchPosts">
        <svg class="spinner">...</svg>
        Loading posts...
    </div>

    {{-- Multiple targets --}}
    <div wire:loading wire:target="fetchPosts, searchPosts">
        Loading data...
    </div>

    {{-- Loading delay (prevents flash) --}}
    <div wire:loading.delay.longest wire:target="fetchPosts">
        This appears after 500ms
    </div>

    {{-- Class-based loading states --}}
    <button
        wire:click="deletePost(1)"
        wire:loading.attr="disabled"
        wire:loading.class="opacity-50"
        wire:loading.class.remove="bg-blue-500"
    >
        Delete
    </button>

    {{-- Attribute changes --}}
    <button
        wire:click="fetchPosts"
        wire:loading.attr="disabled"
    >
        Fetch
    </button>

    {{-- Results --}}
    <div class="posts">
        @foreach($posts as $post)
            <article>{{ $post['title'] }}</article>
        @endforeach
    </div>
</div>
```

### Pattern 8: Wire Poll for Auto-Refresh

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use App\Models\Notification;
use App\Models\Task;

class AutoRefresh extends Component
{
    public $notifications = [];
    public $tasks = [];
    public $isPolling = true;

    /**
     * Load initial data.
     */
    public function mount()
    {
        $this->loadData();
    }

    /**
     * This is called automatically by wire:poll.
     */
    public function loadData()
    {
        $this->notifications = Notification::where('user_id', auth()->id())
            ->where('read_at', null)
            ->latest()
            ->limit(5)
            ->get()
            ->toArray();

        $this->tasks = Task::where('status', 'pending')
            ->latest()
            ->get()
            ->toArray();
    }

    /**
     * Toggle polling on/off.
     */
    public function togglePolling()
    {
        $this->isPolling = !$this->isPolling;
    }

    /**
     * Specific action that should trigger refresh.
     */
    public function markAsRead($notificationId)
    {
        Notification::find($notificationId)->update(['read_at' => now()]);
        $this->loadData();
    }

    public function render()
    {
        return view('livewire.auto-refresh');
    }
}
```

```blade
<div>
    {{-- Poll every 5 seconds --}}
    <div wire:poll.5s="loadData">
        <h3>Notifications (auto-refresh every 5s)</h3>
        @forelse($notifications as $notification)
            <div>
                {{ $notification['message'] }}
                <button wire:click="markAsRead({{ $notification['id'] }})">
                    Mark Read
                </button>
            </div>
        @empty
            <p>No notifications</p>
        @endforelse
    </div>

    {{-- Conditional polling --}}
    <div wire:poll.3s="{{ $isPolling ? 'loadData' : '' }}">
        <h3>Tasks</h3>
        <button wire:click="togglePolling">
            {{ $isPolling ? 'Stop' : 'Start' }} Auto-Refresh
        </button>

        @foreach($tasks as $task)
            <div>{{ $task['title'] }}</div>
        @endforeach
    </div>

    {{-- Keep alive (poll without calling method) --}}
    <div wire:poll.keep-alive.10s>
        <p>This component stays active</p>
    </div>

    {{-- Visible only (poll only when visible) --}}
    <div wire:poll.visible.5s="loadData">
        <p>Only polls when visible in viewport</p>
    </div>
</div>
```

### Pattern 9: Lifecycle Hooks

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
     */
    public function mount($initialValue = 0)
    {
        $this->counter = $initialValue;
        logger('Component mounted with counter: ' . $initialValue);
    }

    /**
     * Called on every request (including initial).
     * Use for resetting state or reloading data.
     */
    public function hydrate()
    {
        logger('Component hydrated on request');
    }

    /**
     * Called once when component class boots.
     * Use for event listeners or one-time setup.
     */
    public function boot()
    {
        logger('Component booted');
    }

    /**
     * Called before any property updates.
     */
    public function updating($name, $value)
    {
        logger("Updating {$name} to {$value}");
    }

    /**
     * Called after any property updates.
     */
    public function updated($name, $value)
    {
        logger("Updated {$name} to {$value}");
    }

    /**
     * Called before specific property updates.
     */
    public function updatingCounter($value)
    {
        // Validate before update
        if ($value < 0) {
            $this->addError('counter', 'Counter cannot be negative');
            return;
        }
    }

    /**
     * Called after specific property updates.
     */
    public function updatedCounter($value)
    {
        // React to counter changes
        if ($value >= 10) {
            session()->flash('message', 'Counter reached 10!');
        }
    }

    /**
     * Called before component is dehydrated.
     */
    public function dehydrate()
    {
        logger('Component dehydrating');
    }

    public function increment()
    {
        $this->counter++;
    }

    public function render()
    {
        logger('Rendering component');
        return view('livewire.lifecycle-demo');
    }
}
```

```blade
<div>
    <h2>Lifecycle Demo</h2>

    <p>Counter: {{ $counter }}</p>

    <button wire:click="increment">Increment</button>

    <input type="number" wire:model.live="counter">

    @error('counter')
        <span class="error">{{ $message }}</span>
    @enderror

    @if(session('message'))
        <div class="alert">{{ session('message') }}</div>
    @endif
</div>
```

### Pattern 10: Event Dispatching and Listening

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\On;

class EventDispatcher extends Component
{
    public $message = '';

    /**
     * Dispatch event to other components.
     */
    public function sendMessage()
    {
        // Dispatch to all components
        $this->dispatch('message-sent', message: $this->message);

        // Dispatch to specific component
        $this->dispatch('notification', message: 'Message sent!')
            ->to('notification-center');

        // Dispatch to parent only
        $this->dispatch('child-updated')->up();

        // Dispatch to self (refresh)
        $this->dispatch('refresh')->self();
    }

    /**
     * Dispatch to browser (JavaScript).
     */
    public function notifyBrowser()
    {
        $this->dispatch('show-toast',
            title: 'Success',
            message: 'Operation completed',
            type: 'success'
        );
    }

    public function render()
    {
        return view('livewire.event-dispatcher');
    }
}

class EventListener extends Component
{
    public $messages = [];
    public $lastMessage = '';

    /**
     * Listen to event using attribute.
     */
    #[On('message-sent')]
    public function handleMessage($message)
    {
        $this->messages[] = $message;
        $this->lastMessage = $message;
    }

    /**
     * Listen to multiple events.
     */
    #[On('refresh')]
    #[On('reload')]
    public function refresh()
    {
        $this->messages = [];
        $this->lastMessage = '';
    }

    /**
     * Alternative: Define listeners array.
     */
    protected $listeners = [
        'message-sent' => 'handleMessage',
        'clear-messages' => 'clearMessages',
    ];

    public function clearMessages()
    {
        $this->messages = [];
    }

    public function render()
    {
        return view('livewire.event-listener');
    }
}
```

```blade
{{-- event-dispatcher.blade.php --}}
<div>
    <h3>Send Messages</h3>

    <input type="text" wire:model="message" placeholder="Enter message">

    <button wire:click="sendMessage">Send to All Components</button>
    <button wire:click="notifyBrowser">Notify Browser</button>
</div>

{{-- event-listener.blade.php --}}
<div>
    <h3>Received Messages</h3>

    <p>Last: {{ $lastMessage }}</p>

    <ul>
        @foreach($messages as $msg)
            <li>{{ $msg }}</li>
        @endforeach
    </ul>

    <button wire:click="$dispatch('clear-messages')">Clear</button>
</div>

{{-- Listen in JavaScript --}}
<script>
document.addEventListener('livewire:init', () => {
    Livewire.on('show-toast', (event) => {
        console.log(event.title, event.message, event.type);
        // Show toast notification
    });
});
</script>
```

## Advanced Patterns

### Pattern 11: Nested Component Communication

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\On;
use Livewire\Attributes\Reactive;

class GrandparentComponent extends Component
{
    public $sharedData = 'Initial data';

    #[On('update-from-grandchild')]
    public function handleGrandchildUpdate($data)
    {
        $this->sharedData = $data;
    }

    public function render()
    {
        return view('livewire.grandparent-component');
    }
}

class ParentComponent extends Component
{
    #[Reactive]
    public $sharedData;

    public $parentData = 'Parent data';

    public function updateParent($data)
    {
        $this->parentData = $data;

        // Pass up to grandparent
        $this->dispatch('update-from-grandchild', data: $data)->up();
    }

    public function render()
    {
        return view('livewire.parent-component');
    }
}

class ChildComponent extends Component
{
    #[Reactive]
    public $sharedData;

    public $childData = '';

    public function sendToGrandparent()
    {
        // Dispatch event that bubbles up
        $this->dispatch('update-from-grandchild', data: $this->childData);
    }

    public function render()
    {
        return view('livewire.child-component');
    }
}
```

```blade
{{-- grandparent-component.blade.php --}}
<div>
    <h2>Grandparent Component</h2>
    <p>Shared Data: {{ $sharedData }}</p>

    <livewire:parent-component :sharedData="$sharedData" />
</div>

{{-- parent-component.blade.php --}}
<div>
    <h3>Parent Component</h3>
    <p>From Grandparent: {{ $sharedData }}</p>
    <p>Parent Data: {{ $parentData }}</p>

    <livewire:child-component :sharedData="$sharedData" />
</div>

{{-- child-component.blade.php --}}
<div>
    <h4>Child Component</h4>
    <p>From Grandparent: {{ $sharedData }}</p>

    <input type="text" wire:model="childData" placeholder="Send to grandparent">
    <button wire:click="sendToGrandparent">Send Up</button>
</div>
```

### Pattern 12: Dynamic Component Loading

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class DynamicLoader extends Component
{
    public $activeComponent = 'dashboard';
    public $components = [
        'dashboard' => 'Dashboard',
        'profile' => 'User Profile',
        'settings' => 'Settings',
    ];

    public function switchComponent($component)
    {
        $this->activeComponent = $component;
    }

    public function render()
    {
        return view('livewire.dynamic-loader');
    }
}
```

```blade
<div>
    <nav>
        @foreach($components as $key => $label)
            <button
                wire:click="switchComponent('{{ $key }}')"
                @class(['active' => $activeComponent === $key])
            >
                {{ $label }}
            </button>
        @endforeach
    </nav>

    <div class="content">
        @switch($activeComponent)
            @case('dashboard')
                <livewire:dashboard :key="'dashboard-'.now()" />
                @break
            @case('profile')
                <livewire:user-profile :key="'profile-'.now()" />
                @break
            @case('settings')
                <livewire:settings :key="'settings-'.now()" />
                @break
        @endswitch
    </div>
</div>
```

### Pattern 13: Form Wizards with State Management

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Validate;

class MultiStepForm extends Component
{
    public $currentStep = 1;
    public $totalSteps = 3;

    // Step 1 data
    #[Validate('required|string|min:3')]
    public $name = '';

    #[Validate('required|email')]
    public $email = '';

    // Step 2 data
    #[Validate('required|string')]
    public $address = '';

    #[Validate('required|string')]
    public $city = '';

    // Step 3 data
    #[Validate('required|boolean')]
    public $terms = false;

    public function nextStep()
    {
        $this->validateCurrentStep();

        if ($this->currentStep < $this->totalSteps) {
            $this->currentStep++;
        }
    }

    public function previousStep()
    {
        if ($this->currentStep > 1) {
            $this->currentStep--;
        }
    }

    public function goToStep($step)
    {
        if ($step <= $this->currentStep || $this->canAccessStep($step)) {
            $this->currentStep = $step;
        }
    }

    private function validateCurrentStep()
    {
        $rules = match($this->currentStep) {
            1 => ['name', 'email'],
            2 => ['address', 'city'],
            3 => ['terms'],
            default => [],
        };

        $this->validate(array_fill_keys($rules, 'required'));
    }

    private function canAccessStep($step)
    {
        // Check if previous steps are complete
        for ($i = 1; $i < $step; $i++) {
            try {
                $this->validateStep($i);
            } catch (\Exception $e) {
                return false;
            }
        }
        return true;
    }

    public function submit()
    {
        $this->validate();

        // Process form
        logger('Form submitted', [
            'name' => $this->name,
            'email' => $this->email,
            'address' => $this->address,
            'city' => $this->city,
        ]);

        session()->flash('message', 'Form submitted successfully!');
        $this->reset();
    }

    public function render()
    {
        return view('livewire.multi-step-form');
    }
}
```

```blade
<div>
    <div class="steps-indicator">
        @for($i = 1; $i <= $totalSteps; $i++)
            <div @class([
                'step',
                'active' => $i === $currentStep,
                'completed' => $i < $currentStep
            ])>
                {{ $i }}
            </div>
        @endfor
    </div>

    <form wire:submit.prevent="submit">
        @if($currentStep === 1)
            <div class="step-content">
                <h3>Step 1: Personal Information</h3>

                <input type="text" wire:model.blur="name" placeholder="Name">
                @error('name') <span class="error">{{ $message }}</span> @enderror

                <input type="email" wire:model.blur="email" placeholder="Email">
                @error('email') <span class="error">{{ $message }}</span> @enderror
            </div>
        @endif

        @if($currentStep === 2)
            <div class="step-content">
                <h3>Step 2: Address</h3>

                <input type="text" wire:model.blur="address" placeholder="Address">
                @error('address') <span class="error">{{ $message }}</span> @enderror

                <input type="text" wire:model.blur="city" placeholder="City">
                @error('city') <span class="error">{{ $message }}</span> @enderror
            </div>
        @endif

        @if($currentStep === 3)
            <div class="step-content">
                <h3>Step 3: Confirmation</h3>

                <div class="summary">
                    <p><strong>Name:</strong> {{ $name }}</p>
                    <p><strong>Email:</strong> {{ $email }}</p>
                    <p><strong>Address:</strong> {{ $address }}, {{ $city }}</p>
                </div>

                <label>
                    <input type="checkbox" wire:model="terms">
                    I agree to the terms and conditions
                </label>
                @error('terms') <span class="error">{{ $message }}</span> @enderror
            </div>
        @endif

        <div class="form-actions">
            @if($currentStep > 1)
                <button type="button" wire:click="previousStep">Previous</button>
            @endif

            @if($currentStep < $totalSteps)
                <button type="button" wire:click="nextStep">Next</button>
            @else
                <button type="submit">Submit</button>
            @endif
        </div>
    </form>
</div>
```

### Pattern 14: Real-time Search with Debouncing

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithPagination;
use App\Models\Product;

class LiveSearch extends Component
{
    use WithPagination;

    public $search = '';
    public $category = '';
    public $minPrice = '';
    public $maxPrice = '';
    public $sortBy = 'name';
    public $sortDirection = 'asc';

    protected $queryString = [
        'search' => ['except' => ''],
        'category' => ['except' => ''],
        'sortBy' => ['except' => 'name'],
    ];

    public function updatingSearch()
    {
        // Reset pagination when search changes
        $this->resetPage();
    }

    public function updatingCategory()
    {
        $this->resetPage();
    }

    public function sortBy($field)
    {
        if ($this->sortBy === $field) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortBy = $field;
            $this->sortDirection = 'asc';
        }
    }

    public function clearFilters()
    {
        $this->reset(['search', 'category', 'minPrice', 'maxPrice']);
        $this->resetPage();
    }

    #[Computed]
    public function results()
    {
        return Product::query()
            ->when($this->search, function ($query) {
                $query->where(function ($q) {
                    $q->where('name', 'like', '%' . $this->search . '%')
                      ->orWhere('description', 'like', '%' . $this->search . '%');
                });
            })
            ->when($this->category, fn($q) => $q->where('category_id', $this->category))
            ->when($this->minPrice, fn($q) => $q->where('price', '>=', $this->minPrice))
            ->when($this->maxPrice, fn($q) => $q->where('price', '<=', $this->maxPrice))
            ->orderBy($this->sortBy, $this->sortDirection)
            ->paginate(12);
    }

    public function render()
    {
        return view('livewire.live-search');
    }
}
```

```blade
<div>
    <div class="filters">
        <input
            type="text"
            wire:model.live.debounce.500ms="search"
            placeholder="Search products..."
        >

        <select wire:model.live="category">
            <option value="">All Categories</option>
            <option value="1">Electronics</option>
            <option value="2">Clothing</option>
            <option value="3">Books</option>
        </select>

        <input
            type="number"
            wire:model.live.debounce.500ms="minPrice"
            placeholder="Min Price"
        >

        <input
            type="number"
            wire:model.live.debounce.500ms="maxPrice"
            placeholder="Max Price"
        >

        <button wire:click="clearFilters">Clear Filters</button>
    </div>

    <div class="results" wire:loading.class="opacity-50">
        <div class="sort-bar">
            <button wire:click="sortBy('name')">
                Name
                @if($sortBy === 'name')
                    {{ $sortDirection === 'asc' ? '↑' : '↓' }}
                @endif
            </button>
            <button wire:click="sortBy('price')">
                Price
                @if($sortBy === 'price')
                    {{ $sortDirection === 'asc' ? '↑' : '↓' }}
                @endif
            </button>
        </div>

        <div class="products">
            @forelse($this->results as $product)
                <div class="product-card">
                    <h3>{{ $product->name }}</h3>
                    <p>${{ number_format($product->price, 2) }}</p>
                </div>
            @empty
                <p>No products found.</p>
            @endforelse
        </div>

        {{ $this->results->links() }}
    </div>

    <div wire:loading wire:target="search,category,minPrice,maxPrice">
        <div class="loading-overlay">Searching...</div>
    </div>
</div>
```

### Pattern 15: Optimistic UI Updates

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use App\Models\Post;

class OptimisticUpdates extends Component
{
    public $posts = [];

    public function mount()
    {
        $this->loadPosts();
    }

    public function loadPosts()
    {
        $this->posts = Post::with('author')
            ->latest()
            ->limit(20)
            ->get()
            ->toArray();
    }

    public function toggleLike($postId)
    {
        $post = Post::find($postId);
        $liked = $post->toggleLike(auth()->id());

        // Update local state immediately (optimistic)
        $index = collect($this->posts)->search(fn($p) => $p['id'] == $postId);
        if ($index !== false) {
            $this->posts[$index]['likes_count'] = $post->likes_count;
            $this->posts[$index]['is_liked'] = $liked;
        }
    }

    public function render()
    {
        return view('livewire.optimistic-updates');
    }
}
```

```blade
<div>
    @foreach($posts as $post)
        <article class="post">
            <h3>{{ $post['title'] }}</h3>
            <p>{{ $post['excerpt'] }}</p>

            <button
                wire:click="toggleLike({{ $post['id'] }})"
                @class([
                    'like-button',
                    'liked' => $post['is_liked'] ?? false
                ])
            >
                ❤️ {{ $post['likes_count'] }}
            </button>
        </article>
    @endforeach
</div>
```

## Real-World Applications

### Application 1: Real-Time Notification System

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\On;
use App\Models\Notification;

class NotificationCenter extends Component
{
    public $notifications = [];
    public $unreadCount = 0;
    public $isOpen = false;

    public function mount()
    {
        $this->loadNotifications();
    }

    public function loadNotifications()
    {
        $this->notifications = Notification::where('user_id', auth()->id())
            ->latest()
            ->limit(10)
            ->get()
            ->toArray();

        $this->unreadCount = Notification::where('user_id', auth()->id())
            ->whereNull('read_at')
            ->count();
    }

    public function togglePanel()
    {
        $this->isOpen = !$this->isOpen;
    }

    public function markAsRead($notificationId)
    {
        Notification::find($notificationId)->update(['read_at' => now()]);
        $this->loadNotifications();
    }

    public function markAllAsRead()
    {
        Notification::where('user_id', auth()->id())
            ->whereNull('read_at')
            ->update(['read_at' => now()]);

        $this->loadNotifications();
    }

    #[On('echo:notifications.{userId},NotificationCreated')]
    public function notificationReceived($notification)
    {
        $this->loadNotifications();
        $this->dispatch('show-toast', message: 'New notification received!');
    }

    public function render()
    {
        return view('livewire.notification-center');
    }
}
```

### Application 2: Shopping Cart with Live Updates

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;
use Livewire\Attributes\On;

class ShoppingCart extends Component
{
    public $cartItems = [];

    public function mount()
    {
        $this->loadCart();
    }

    public function loadCart()
    {
        $this->cartItems = session()->get('cart', []);
    }

    #[Computed]
    public function total()
    {
        return collect($this->cartItems)->sum(function ($item) {
            return $item['price'] * $item['quantity'];
        });
    }

    #[Computed]
    public function itemCount()
    {
        return collect($this->cartItems)->sum('quantity');
    }

    #[On('product-added')]
    public function addProduct($productId, $quantity = 1)
    {
        $product = \App\Models\Product::find($productId);

        if (isset($this->cartItems[$productId])) {
            $this->cartItems[$productId]['quantity'] += $quantity;
        } else {
            $this->cartItems[$productId] = [
                'id' => $product->id,
                'name' => $product->name,
                'price' => $product->price,
                'quantity' => $quantity,
            ];
        }

        $this->saveCart();
        $this->dispatch('cart-updated');
    }

    public function updateQuantity($productId, $quantity)
    {
        if ($quantity <= 0) {
            $this->removeItem($productId);
            return;
        }

        $this->cartItems[$productId]['quantity'] = $quantity;
        $this->saveCart();
    }

    public function removeItem($productId)
    {
        unset($this->cartItems[$productId]);
        $this->saveCart();
    }

    private function saveCart()
    {
        session()->put('cart', $this->cartItems);
    }

    public function render()
    {
        return view('livewire.shopping-cart');
    }
}
```

## Performance Best Practices

### Practice 1: Use Computed Properties for Expensive Operations

```php
// BAD: Queries run on every render
public function render()
{
    $posts = Post::with('author', 'comments')->get(); // Runs every time
    return view('livewire.posts', ['posts' => $posts]);
}

// GOOD: Cached with computed property
#[Computed]
public function posts()
{
    return Post::with('author', 'comments')->get(); // Cached
}
```

### Practice 2: Debounce User Input

```blade
{{-- BAD: Updates on every keystroke --}}
<input wire:model.live="search">

{{-- GOOD: Updates after user stops typing --}}
<input wire:model.live.debounce.500ms="search">
```

### Practice 3: Use Lazy Loading for Heavy Components

```blade
{{-- Load component on scroll/interaction --}}
<div>
    @if($showComments)
        <livewire:comments :post-id="$postId" />
    @else
        <button wire:click="$set('showComments', true)">Load Comments</button>
    @endif
</div>
```

## Common Pitfalls

### Pitfall 1: Forgetting #[Reactive] on Child Properties

```php
// WRONG: Child won't see parent changes
class ChildComponent extends Component
{
    public $userId; // Not reactive
}

// CORRECT: Child updates when parent changes
class ChildComponent extends Component
{
    #[Reactive]
    public $userId;
}
```

### Pitfall 2: Not Using #[Computed] for Expensive Operations

```php
// WRONG: Query runs on every render
public function render()
{
    return view('livewire.dashboard', [
        'stats' => $this->calculateExpensiveStats(), // Runs every time
    ]);
}

// CORRECT: Cached until dependencies change
#[Computed]
public function stats()
{
    return $this->calculateExpensiveStats(); // Cached
}
```

### Pitfall 3: Overusing wire:model.live

```blade
{{-- WRONG: Too many updates --}}
<textarea wire:model.live="content"></textarea>

{{-- CORRECT: Update on blur --}}
<textarea wire:model.blur="content"></textarea>
```

## Testing

```php
<?php

namespace Tests\Feature\Livewire;

use App\Livewire\Counter;
use Livewire\Livewire;
use Tests\TestCase;

class CounterTest extends TestCase
{
    public function test_can_increment_counter()
    {
        Livewire::test(Counter::class)
            ->assertSet('count', 0)
            ->call('increment')
            ->assertSet('count', 1);
    }

    public function test_computed_property_works()
    {
        Livewire::test(Counter::class)
            ->set('count', 5)
            ->assertSee('Doubled: 10');
    }

    public function test_reactive_property_updates()
    {
        $component = Livewire::test(ChildComponent::class, ['userId' => 1])
            ->assertSet('userId', 1);

        $component->set('userId', 2)
            ->assertSet('userId', 2)
            ->assertDispatched('user-changed');
    }
}
```

## Resources

- **Livewire 4 Documentation**: https://livewire.laravel.com
- **Reactive Properties**: https://livewire.laravel.com/docs/properties
- **Computed Properties**: https://livewire.laravel.com/docs/computed-properties
- **Wire Directives**: https://livewire.laravel.com/docs/wire-directives
- **Lifecycle Hooks**: https://livewire.laravel.com/docs/lifecycle-hooks
- **Events**: https://livewire.laravel.com/docs/events

## Best Practices Summary

1. **Use #[Reactive]** for child component properties that need parent updates
2. **Use #[Computed]** for expensive operations that should be cached
3. **Use #[Locked]** for security-sensitive properties that shouldn't be modified
4. **Debounce user input** with wire:model.live.debounce to reduce server requests
5. **Use lifecycle hooks** for initialization and cleanup logic
6. **Dispatch events** for component communication instead of tight coupling
7. **Load components lazily** to improve initial page load performance
8. **Use wire:loading** to provide feedback during asynchronous operations
9. **Implement optimistic UI** updates for better perceived performance
10. **Test reactivity** thoroughly with Livewire's testing utilities
