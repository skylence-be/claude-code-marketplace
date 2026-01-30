# Wire Directives

Livewire 4 wire directives for data binding, actions, and UI states.

## BREAKING CHANGE in v4: wire:model

In Livewire 4, `wire:model` now only listens for events originating directly on the element itself. Use `.deep` modifier to capture child element events.

## wire:model - Data Binding

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class FormModifiers extends Component
{
    public $liveInput = '';      // Updates on every keystroke
    public $blurInput = '';      // Updates when input loses focus
    public $debounceInput = '';  // Updates after user stops typing
    public $throttleInput = '';  // Updates at most every X milliseconds
    public $quantity = 1;        // Number casting
    public $isActive = false;    // Boolean casting
    public $nested = [];         // Nested data from child elements

    public function render()
    {
        return view('livewire.form-modifiers');
    }
}
```

```blade
<div>
    {{-- Live update - updates on every keystroke --}}
    <input type="text" wire:model.live="liveInput">

    {{-- Blur - updates when input loses focus --}}
    {{-- BREAKING: In v4, also controls client-side state sync timing --}}
    <input type="text" wire:model.live.blur="blurInput">

    {{-- Debounce - updates after pause in typing --}}
    <input type="text" wire:model.live.debounce.500ms="debounceInput">

    {{-- Throttle - updates at most once per interval --}}
    <input type="text" wire:model.live.throttle.1000ms="throttleInput">

    {{-- Number casting --}}
    <input type="number" wire:model.number="quantity">

    {{-- Boolean casting --}}
    <input type="checkbox" wire:model.boolean="isActive">

    {{-- Lazy - updates on blur or form submit --}}
    <input type="text" wire:model.lazy="lazyInput">

    {{-- NEW in v4: .deep modifier for child element events --}}
    <div wire:model.deep="nested">
        <input type="text" name="child_input"> {{-- Captured! --}}
    </div>
</div>
```

## wire:click - Action Methods

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class ActionMethods extends Component
{
    public $count = 0;
    public $items = [];
    public $confirmDelete = false;

    public function increment()
    {
        $this->count++;
    }

    public function add($amount)
    {
        $this->count += $amount;
    }

    public function addItem($name, $quantity)
    {
        $this->items[] = [
            'name' => $name,
            'quantity' => $quantity,
        ];
    }

    public function removeItem($index)
    {
        unset($this->items[$index]);
        $this->items = array_values($this->items);
    }

    public function delete()
    {
        if (!$this->confirmDelete) {
            $this->confirmDelete = true;
            return;
        }

        $this->items = [];
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

    {{-- Prevent default --}}
    <form wire:submit.prevent="save">
        <button type="submit">Save</button>
    </form>

    {{-- Items list with remove --}}
    @foreach($items as $index => $item)
        <div>
            {{ $item['name'] }} ({{ $item['quantity'] }})
            <button wire:click="removeItem({{ $index }})">Remove</button>
        </div>
    @endforeach

    {{-- Confirmation pattern --}}
    @if($confirmDelete)
        <div>
            <p>Are you sure?</p>
            <button wire:click="delete">Yes, Delete</button>
            <button wire:click="$set('confirmDelete', false)">Cancel</button>
        </div>
    @else
        <button wire:click="delete">Delete All</button>
    @endif

    {{-- $set for simple property changes --}}
    <button wire:click="$set('count', 0)">Reset</button>

    {{-- $toggle for booleans --}}
    <button wire:click="$toggle('confirmDelete')">Toggle</button>
</div>
```

## wire:loading - Loading States

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class LoadingStates extends Component
{
    public $posts = [];

    public function fetchPosts()
    {
        sleep(2); // Simulate delay
        $this->posts = \App\Models\Post::latest()->limit(10)->get()->toArray();
    }

    public function searchPosts($term)
    {
        sleep(1);
        $this->posts = \App\Models\Post::where('title', 'like', "%{$term}%")->get()->toArray();
    }

    public function render()
    {
        return view('livewire.loading-states');
    }
}
```

```blade
<div>
    {{-- Default loading indicator --}}
    <button wire:click="fetchPosts">
        Fetch Posts
        <span wire:loading>Loading...</span>
    </button>

    {{-- Loading with specific target --}}
    <button wire:click="searchPosts('test')">
        Search
        <span wire:loading wire:target="searchPosts">Searching...</span>
    </button>

    {{-- Loading delay (prevents flash) --}}
    <div wire:loading.delay wire:target="fetchPosts">
        This appears after short delay
    </div>

    <div wire:loading.delay.longest wire:target="fetchPosts">
        This appears after 500ms
    </div>

    {{-- Hide element while loading --}}
    <div wire:loading.remove wire:target="fetchPosts">
        Content hidden during loading
    </div>

    {{-- Display modes --}}
    <div wire:loading.flex wire:target="fetchPosts">
        <svg class="spinner">...</svg> Loading...
    </div>

    <div wire:loading.grid wire:target="fetchPosts">
        Grid display while loading
    </div>

    {{-- Multiple targets --}}
    <div wire:loading wire:target="fetchPosts, searchPosts">
        Loading data...
    </div>

    {{-- Class-based loading states --}}
    <button
        wire:click="fetchPosts"
        wire:loading.attr="disabled"
        wire:loading.class="opacity-50"
        wire:loading.class.remove="bg-blue-500"
    >
        Fetch
    </button>

    {{-- Attribute changes --}}
    <button wire:click="save" wire:loading.attr="disabled">
        Save
    </button>

    <input wire:loading.attr="readonly" wire:target="save">
</div>
```

## wire:submit - Form Submission

```blade
{{-- Prevent default and call method --}}
<form wire:submit="save">
    <input type="text" wire:model="name">
    <button type="submit">Save</button>
</form>

{{-- With prevent modifier (explicit) --}}
<form wire:submit.prevent="save">
    <button type="submit">Save</button>
</form>

{{-- With loading state --}}
<form wire:submit="save">
    <button type="submit" wire:loading.attr="disabled">
        <span wire:loading.remove>Save</span>
        <span wire:loading>Saving...</span>
    </button>
</form>
```

## Other Wire Directives

```blade
{{-- wire:key for list items --}}
@foreach($items as $item)
    <div wire:key="{{ $item->id }}">
        {{ $item->name }}
    </div>
@endforeach

{{-- wire:ignore to skip DOM updates --}}
<div wire:ignore>
    {{-- Third-party JS widget here --}}
</div>

{{-- wire:ignore.self for container only --}}
<div wire:ignore.self>
    <span>This child can update</span>
</div>

{{-- wire:dirty to show when changed --}}
<input wire:model="name" wire:dirty.class="border-yellow-500">
<span wire:dirty wire:target="name">Unsaved changes</span>

{{-- wire:offline for connection status --}}
<div wire:offline>
    You are currently offline.
</div>

{{-- wire:confirm for confirmation dialogs --}}
<button wire:click="delete" wire:confirm="Are you sure you want to delete?">
    Delete
</button>

{{-- wire:transition - now uses native View Transitions API in v4 --}}
<div wire:transition>
    This will animate in/out
</div>
```

## NEW in v4: Advanced Directives

```blade
{{-- wire:sort - Drag-and-drop sorting --}}
<ul wire:sort="reorder">
    @foreach($items as $item)
        <li wire:key="{{ $item->id }}" wire:sort.item="{{ $item->id }}">
            <span wire:sort.handle>⋮⋮</span>
            {{ $item->name }}
        </li>
    @endforeach
</ul>

{{-- wire:intersect - Viewport intersection detection --}}
<div wire:intersect="loadMore">
    Load more when this becomes visible
</div>

<div wire:intersect.once="trackImpression">
    Track only once
</div>

<div wire:intersect.half="halfVisible">
    Triggers at 50% visibility
</div>

<div wire:intersect.full="fullyVisible">
    Triggers at 100% visibility
</div>

<div wire:intersect.threshold.75="mostlyVisible">
    Triggers at 75% visibility
</div>

{{-- wire:ref - Element reference for JavaScript --}}
<canvas wire:ref="myCanvas"></canvas>
<script>
    // Access via this.$refs.myCanvas
</script>

{{-- wire:navigate:scroll - Preserve scroll position (replaces wire:scroll) --}}
<div wire:navigate:scroll>
    Scrollable content that preserves position
</div>
```

## NEW in v4: Action Modifiers

```blade
{{-- .async - Run action in parallel, non-blocking --}}
<button wire:click.async="refreshStats">Refresh (Non-blocking)</button>
<button wire:click.async="refreshChart">Chart (Non-blocking)</button>

{{-- .bundle - Bundle multiple parallel requests --}}
<button wire:click.bundle="action1">Action 1</button>
<button wire:click.bundle="action2">Action 2</button>

{{-- .renderless - Execute action without re-rendering --}}
<button wire:click.renderless="trackClick">Track (No Re-render)</button>

{{-- .preserve-scroll - Maintain scroll position during update --}}
<button wire:click.preserve-scroll="loadMore">Load More</button>

{{-- data-loading attribute - Auto-applied to request-triggering elements --}}
{{-- Style with CSS: [data-loading] { opacity: 0.5; } --}}
```

## Event Modifiers

```blade
{{-- Prevent default --}}
<a href="#" wire:click.prevent="doSomething">Link</a>

{{-- Stop propagation --}}
<button wire:click.stop="handleClick">Click</button>

{{-- Self (only direct clicks) --}}
<div wire:click.self="handleClick">
    <button>This won't trigger parent</button>
</div>

{{-- Keyboard modifiers --}}
<input wire:keydown.enter="submit">
<input wire:keydown.escape="cancel">
<input wire:keydown.tab="nextField">

{{-- Key combinations --}}
<input wire:keydown.ctrl.s.prevent="save">
<input wire:keydown.meta.enter="submit">

{{-- Mouse modifiers --}}
<div wire:click.right="showContextMenu">Right click</div>
<div wire:click.middle="openNewTab">Middle click</div>

{{-- Debounce on events --}}
<input wire:keyup.debounce.500ms="search">

{{-- Throttle on events --}}
<div wire:scroll.throttle.100ms="handleScroll">
```
