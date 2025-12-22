# Polling Patterns

Livewire 4 wire:poll for auto-refresh and real-time updates.

## Basic Polling

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
            ->whereNull('read_at')
            ->latest()
            ->limit(5)
            ->get()
            ->toArray();

        $this->tasks = Task::where('status', 'pending')
            ->latest()
            ->get()
            ->toArray();
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
            <div>{{ $notification['message'] }}</div>
        @empty
            <p>No notifications</p>
        @endforelse
    </div>

    {{-- Default polling (2 seconds) --}}
    <div wire:poll>
        Updates every 2 seconds
    </div>

    {{-- Poll with different intervals --}}
    <div wire:poll.1s>Every second</div>
    <div wire:poll.10s>Every 10 seconds</div>
    <div wire:poll.30s>Every 30 seconds</div>
    <div wire:poll.1m>Every minute</div>
</div>
```

## Conditional Polling

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class ConditionalPolling extends Component
{
    public $isPolling = true;
    public $data = [];

    public function togglePolling()
    {
        $this->isPolling = !$this->isPolling;
    }

    public function loadData()
    {
        if (!$this->isPolling) {
            return;
        }

        $this->data = $this->fetchLatestData();
    }

    public function render()
    {
        return view('livewire.conditional-polling');
    }
}
```

```blade
<div>
    {{-- Conditional polling based on property --}}
    <div wire:poll.3s="{{ $isPolling ? 'loadData' : '' }}">
        <button wire:click="togglePolling">
            {{ $isPolling ? 'Stop' : 'Start' }} Auto-Refresh
        </button>

        @foreach($data as $item)
            <div>{{ $item }}</div>
        @endforeach
    </div>

    {{-- Or use Livewire's built-in toggle --}}
    @if($isPolling)
        <div wire:poll.5s="loadData">
            Content that polls
        </div>
    @else
        <div>
            Polling stopped
        </div>
    @endif
</div>
```

## Visibility-Based Polling

```blade
<div>
    {{-- Only poll when element is visible in viewport --}}
    <div wire:poll.visible.5s="loadData">
        Only polls when visible
    </div>

    {{-- Keep alive (poll without calling method) --}}
    <div wire:poll.keep-alive.10s>
        <p>This component stays active without explicit refresh</p>
    </div>

    {{-- Combine visibility with longer intervals --}}
    <div wire:poll.visible.30s="checkForUpdates">
        Efficient polling when scrolled into view
    </div>
</div>
```

## Smart Polling with Alpine.js

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\Attributes\Computed;

class SmartPolling extends Component
{
    public $isPolling = true;
    public $pollInterval = 5000;
    public $lastChecked;

    public function mount()
    {
        $this->lastChecked = now();
    }

    #[Computed]
    public function notifications()
    {
        return \App\Models\Notification::where('user_id', auth()->id())
            ->where('created_at', '>', $this->lastChecked)
            ->get();
    }

    public function checkForUpdates()
    {
        $newNotifications = $this->notifications;

        if ($newNotifications->isNotEmpty()) {
            $this->lastChecked = now();
            $this->dispatch('new-notifications', count: $newNotifications->count());

            // Reset to fast polling when activity detected
            $this->pollInterval = 5000;
        } else {
            // Slow down polling when idle
            $this->pollInterval = min($this->pollInterval * 1.5, 30000);
        }
    }

    public function render()
    {
        return view('livewire.smart-polling');
    }
}
```

```blade
<div
    x-data="{
        polling: @entangle('isPolling'),
        interval: @entangle('pollInterval'),
        timer: null
    }"
    x-init="
        timer = setInterval(() => {
            if (polling && !document.hidden) {
                $wire.checkForUpdates()
            }
        }, interval);

        // Pause when tab is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                clearInterval(timer);
            } else {
                timer = setInterval(() => {
                    if (polling) $wire.checkForUpdates()
                }, interval);
            }
        });
    "
    x-on:beforeunload.window="clearInterval(timer)"
>
    <button @click="polling = !polling">
        <span x-text="polling ? 'Stop' : 'Start'"></span> Polling
    </button>

    <p>Interval: <span x-text="interval / 1000"></span>s</p>

    <div class="notifications">
        @foreach($this->notifications as $notification)
            <div>{{ $notification->message }}</div>
        @endforeach
    </div>
</div>
```

## Efficient Polling Strategies

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Illuminate\Support\Facades\Cache;

class EfficientPolling extends Component
{
    public $lastUpdateHash;

    /**
     * Only fetch full data if hash changed.
     */
    public function checkForChanges()
    {
        $currentHash = Cache::get('notifications_hash_' . auth()->id());

        if ($currentHash !== $this->lastUpdateHash) {
            $this->lastUpdateHash = $currentHash;
            $this->dispatch('data-changed');
        }
    }

    /**
     * Use timestamps for incremental updates.
     */
    public $lastFetched;

    public function fetchNewItems()
    {
        $newItems = \App\Models\Item::where('created_at', '>', $this->lastFetched)
            ->get();

        if ($newItems->isNotEmpty()) {
            $this->lastFetched = now();
            // Merge new items with existing
        }
    }

    /**
     * Batch multiple checks into one poll.
     */
    public function pollAll()
    {
        return [
            'notifications' => $this->getNotificationCount(),
            'messages' => $this->getMessageCount(),
            'tasks' => $this->getPendingTaskCount(),
        ];
    }
}
```

```blade
<div>
    {{-- Poll for changes, not full data --}}
    <div wire:poll.10s="checkForChanges">
        @if($dataChanged)
            <button wire:click="loadFullData">
                New updates available - click to refresh
            </button>
        @endif
    </div>

    {{-- Or auto-load on change --}}
    <div
        x-data
        x-on:data-changed.window="$wire.loadFullData()"
        wire:poll.10s="checkForChanges"
    >
        {{ $content }}
    </div>
</div>
```

## Polling Best Practices

```php
class PollingBestPractices extends Component
{
    /**
     * 1. Use appropriate intervals
     *    - Real-time critical: 1-2s
     *    - Normal updates: 5-10s
     *    - Background checks: 30s-1m
     */

    /**
     * 2. Only poll when necessary
     */
    public function shouldPoll()
    {
        // Don't poll for completed processes
        return $this->task->status === 'processing';
    }

    /**
     * 3. Minimize payload
     */
    public function checkStatus()
    {
        // Return only what changed
        $newStatus = $this->task->fresh()->status;

        if ($newStatus !== $this->status) {
            $this->status = $newStatus;
        }
    }

    /**
     * 4. Use visibility checks
     */
    // wire:poll.visible.5s

    /**
     * 5. Implement backoff for errors
     */
    public $errorCount = 0;

    public function poll()
    {
        try {
            $this->fetchData();
            $this->errorCount = 0;
        } catch (\Exception $e) {
            $this->errorCount++;
            // Will slow down polling on repeated errors
        }
    }
}
```

```blade
{{-- Good: Visibility + reasonable interval --}}
<div wire:poll.visible.10s="checkForUpdates">

{{-- Bad: Too frequent, always active --}}
{{-- <div wire:poll.500ms="heavyOperation"> --}}

{{-- Good: Conditional with user control --}}
@if($autoRefresh)
    <div wire:poll.5s="refresh"></div>
@endif
<label>
    <input type="checkbox" wire:model.live="autoRefresh">
    Auto-refresh
</label>
```
