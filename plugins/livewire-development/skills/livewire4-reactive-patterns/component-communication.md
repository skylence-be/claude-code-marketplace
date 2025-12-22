# Component Communication

Livewire 4 event dispatching and listening for component communication.

## Event Dispatching

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class EventDispatcher extends Component
{
    public $message = '';

    /**
     * Dispatch event to all components on page.
     */
    public function broadcastMessage()
    {
        $this->dispatch('message-sent', message: $this->message);
    }

    /**
     * Dispatch to specific component.
     */
    public function notifyComponent()
    {
        $this->dispatch('notification', message: 'Hello!')
            ->to('notification-center');
    }

    /**
     * Dispatch to parent only.
     */
    public function notifyParent()
    {
        $this->dispatch('child-updated', data: $this->message)
            ->up();
    }

    /**
     * Dispatch to self (refresh).
     */
    public function refreshSelf()
    {
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
```

## Event Listening

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\On;

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
    }

    /**
     * Listen with dynamic event name.
     */
    #[On('user-{id}-updated')]
    public function handleUserUpdate($id, $data)
    {
        // Handle update for specific user
    }

    /**
     * Alternative: Define listeners property.
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

## Blade Usage

```blade
{{-- event-dispatcher.blade.php --}}
<div>
    <input type="text" wire:model="message" placeholder="Enter message">

    <button wire:click="broadcastMessage">Send to All</button>
    <button wire:click="notifyComponent">Send to Specific</button>
    <button wire:click="notifyParent">Send to Parent</button>
    <button wire:click="notifyBrowser">Send to Browser</button>
</div>

{{-- event-listener.blade.php --}}
<div>
    <p>Last: {{ $lastMessage }}</p>

    <ul>
        @foreach($messages as $msg)
            <li>{{ $msg }}</li>
        @endforeach
    </ul>

    {{-- Dispatch from blade --}}
    <button wire:click="$dispatch('clear-messages')">Clear</button>
</div>

{{-- JavaScript listener --}}
<script>
document.addEventListener('livewire:init', () => {
    Livewire.on('show-toast', (event) => {
        // Show toast notification
        showToast(event.title, event.message, event.type);
    });
});
</script>
```

## Nested Component Communication

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

    public function updateParent($data)
    {
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
    <h2>Grandparent: {{ $sharedData }}</h2>
    <livewire:parent-component :sharedData="$sharedData" />
</div>

{{-- parent-component.blade.php --}}
<div>
    <h3>Parent: {{ $sharedData }}</h3>
    <livewire:child-component :sharedData="$sharedData" />
</div>

{{-- child-component.blade.php --}}
<div>
    <h4>Child: {{ $sharedData }}</h4>
    <input type="text" wire:model="childData">
    <button wire:click="sendToGrandparent">Send Up</button>
</div>
```

## Browser Events

```php
class BrowserEvents extends Component
{
    public function triggerBrowserEvent()
    {
        // Dispatch to browser JavaScript
        $this->dispatch('close-modal');
        $this->dispatch('scroll-to-top');
        $this->dispatch('focus-input', inputId: 'email');
    }
}
```

```blade
<div
    x-data="{ open: true }"
    x-on:close-modal.window="open = false"
>
    <div x-show="open">
        Modal content
    </div>
</div>

<script>
document.addEventListener('livewire:init', () => {
    Livewire.on('scroll-to-top', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    Livewire.on('focus-input', ({ inputId }) => {
        document.getElementById(inputId)?.focus();
    });
});
</script>
```

## Echo/WebSocket Events

```php
use Livewire\Attributes\On;

class RealTimeNotifications extends Component
{
    /**
     * Listen to Echo/Pusher events.
     * Format: echo:{channel},{event}
     */
    #[On('echo:notifications.{userId},NotificationCreated')]
    public function notificationReceived($notification)
    {
        $this->notifications[] = $notification;
        $this->dispatch('show-toast', message: 'New notification!');
    }

    /**
     * Private channel.
     */
    #[On('echo-private:user.{userId},MessageReceived')]
    public function messageReceived($message)
    {
        // Handle private message
    }

    /**
     * Presence channel.
     */
    #[On('echo-presence:chat.{roomId},here')]
    public function usersHere($users)
    {
        $this->onlineUsers = $users;
    }
}
```

## Event Best Practices

```php
class EventBestPractices extends Component
{
    /**
     * Use descriptive event names with verb-noun format.
     */
    public function goodEventNames()
    {
        $this->dispatch('user-created', user: $user);
        $this->dispatch('order-completed', orderId: $order->id);
        $this->dispatch('cart-item-removed', itemId: $itemId);
    }

    /**
     * Pass minimal data in events.
     * Pass IDs, not full objects.
     */
    public function efficientEventData()
    {
        // Good: Pass ID
        $this->dispatch('user-selected', userId: $user->id);

        // Bad: Pass full model (large payload)
        // $this->dispatch('user-selected', user: $user);
    }

    /**
     * Document expected event payloads.
     */
    #[On('user-created')]
    public function handleUserCreated(int $userId, string $email): void
    {
        // Handler with typed parameters
    }
}
```
