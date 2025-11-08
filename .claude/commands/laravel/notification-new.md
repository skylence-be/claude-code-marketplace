---
description: Create Laravel notification for multi-channel alerts
model: claude-sonnet-4-5
---

Create a Laravel notification.

## Notification Specification

$ARGUMENTS

## Laravel Notification Patterns

### 1. **Multi-Channel Notification**

```php
<?php

namespace App\Notifications;

use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

class OrderShipped extends Notification implements ShouldQueue
{
    use Queueable;

    public function __construct(
        public Order $order
    ) {}

    public function via(object $notifiable): array
    {
        return ['mail', 'database'];
    }

    public function toMail(object $notifiable): MailMessage
    {
        return (new MailMessage)
            ->subject('Order Shipped!')
            ->greeting('Hello ' . $notifiable->name)
            ->line('Your order #' . $this->order->number . ' has been shipped.')
            ->action('Track Order', route('orders.track', $this->order))
            ->line('Thank you for your purchase!');
    }

    public function toDatabase(object $notifiable): array
    {
        return [
            'order_id' => $this->order->id,
            'order_number' => $this->order->number,
            'tracking_number' => $this->order->tracking_number,
            'message' => 'Your order has been shipped.',
        ];
    }
}
```

### 2. **Broadcast Notification**

```php
<?php

namespace App\Notifications;

use App\Models\Message;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Notifications\Messages\BroadcastMessage;
use Illuminate\Notifications\Notification;

class NewMessage extends Notification implements ShouldBroadcast
{
    use Queueable;

    public function __construct(
        public Message $message
    ) {}

    public function via(object $notifiable): array
    {
        return ['broadcast', 'database'];
    }

    public function toBroadcast(object $notifiable): BroadcastMessage
    {
        return new BroadcastMessage([
            'message' => $this->message->content,
            'sender' => $this->message->sender->name,
            'sent_at' => $this->message->created_at->toISOString(),
        ]);
    }

    public function broadcastOn(): array
    {
        return [
            new PrivateChannel('users.' . $this->message->receiver_id),
        ];
    }

    public function toDatabase(object $notifiable): array
    {
        return [
            'message_id' => $this->message->id,
            'sender_name' => $this->message->sender->name,
            'preview' => substr($this->message->content, 0, 50),
        ];
    }
}
```

### 3. **Slack Notification**

```php
<?php

namespace App\Notifications;

use App\Models\Deployment;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\SlackMessage;
use Illuminate\Notifications\Notification;

class DeploymentCompleted extends Notification
{
    use Queueable;

    public function __construct(
        public Deployment $deployment
    ) {}

    public function via(object $notifiable): array
    {
        return ['slack'];
    }

    public function toSlack(object $notifiable): SlackMessage
    {
        $status = $this->deployment->success ? 'successful' : 'failed';
        $emoji = $this->deployment->success ? ':white_check_mark:' : ':x:';

        return (new SlackMessage)
            ->success($this->deployment->success)
            ->content('Deployment ' . $status . ' ' . $emoji)
            ->attachment(function ($attachment) {
                $attachment->title('Deployment #' . $this->deployment->id)
                    ->fields([
                        'Environment' => $this->deployment->environment,
                        'Branch' => $this->deployment->branch,
                        'Duration' => $this->deployment->duration . 's',
                    ])
                    ->action('View Details', route('deployments.show', $this->deployment));
            });
    }
}
```

### 4. **Conditional Notification**

```php
<?php

namespace App\Notifications;

use App\Models\Comment;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

class CommentAdded extends Notification
{
    use Queueable;

    public function __construct(
        public Comment $comment
    ) {}

    public function via(object $notifiable): array
    {
        $channels = ['database'];

        if ($notifiable->notification_preferences['email_comments']) {
            $channels[] = 'mail';
        }

        if ($notifiable->notification_preferences['push_comments']) {
            $channels[] = 'broadcast';
        }

        return $channels;
    }

    public function toMail(object $notifiable): MailMessage
    {
        return (new MailMessage)
            ->subject('New comment on your post')
            ->line($this->comment->user->name . ' commented on your post.')
            ->line('"' . substr($this->comment->body, 0, 100) . '..."')
            ->action('View Comment', route('posts.show', $this->comment->post_id));
    }

    public function toDatabase(object $notifiable): array
    {
        return [
            'comment_id' => $this->comment->id,
            'post_id' => $this->comment->post_id,
            'commenter' => $this->comment->user->name,
            'preview' => substr($this->comment->body, 0, 50),
        ];
    }
}
```

### 5. **On-Demand Notification**

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

class SystemAlert extends Notification
{
    use Queueable;

    public function __construct(
        public string $title,
        public string $message,
        public string $level = 'info'
    ) {}

    public function via(object $notifiable): array
    {
        return ['mail'];
    }

    public function toMail(object $notifiable): MailMessage
    {
        $mailMessage = (new MailMessage)
            ->subject($this->title)
            ->line($this->message);

        return match ($this->level) {
            'error' => $mailMessage->error(),
            'success' => $mailMessage->success(),
            default => $mailMessage,
        };
    }
}

// Usage:
// Notification::route('mail', 'admin@example.com')
//     ->notify(new SystemAlert('Server Down', 'Production server is down!', 'error'));
```

## Best Practices
- Implement ShouldQueue for performance
- Use appropriate channels for notification type
- Customize notification preferences per user
- Keep notification messages concise
- Use action buttons in emails
- Store important data in database channel
- Test all notification channels
- Consider rate limiting for bulk notifications

Generate complete Laravel notification with multi-channel support.
