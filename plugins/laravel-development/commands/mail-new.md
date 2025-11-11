---
description: Create Laravel mailable for email sending
model: claude-sonnet-4-5
---

Create a Laravel mailable class.

## Mailable Specification

$ARGUMENTS

## Laravel Mailable Patterns

### 1. **Basic Mailable**

```php
<?php

namespace App\Mail;

use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class OrderShipped extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public Order $order
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Your Order Has Been Shipped!',
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.orders.shipped',
            with: [
                'orderNumber' => $this->order->number,
                'trackingNumber' => $this->order->tracking_number,
            ],
        );
    }

    public function attachments(): array
    {
        return [];
    }
}
```

### 2. **Mailable with Attachments**

```php
<?php

namespace App\Mail;

use App\Models\Invoice;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Attachment;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class InvoiceGenerated extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public Invoice $invoice
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Invoice #' . $this->invoice->number,
            tags: ['invoice'],
            metadata: [
                'invoice_id' => $this->invoice->id,
            ],
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.invoices.generated',
            text: 'emails.invoices.generated-text',
        );
    }

    public function attachments(): array
    {
        return [
            Attachment::fromPath($this->invoice->pdf_path)
                ->as('invoice-' . $this->invoice->number . '.pdf')
                ->withMime('application/pdf'),
        ];
    }
}
```

### 3. **Markdown Mailable**

```php
<?php

namespace App\Mail;

use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class WelcomeEmail extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public User $user
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Welcome to ' . config('app.name') . '!',
        );
    }

    public function content(): Content
    {
        return new Content(
            markdown: 'emails.welcome',
            with: [
                'url' => route('dashboard'),
            ],
        );
    }
}

// Blade template: resources/views/emails/welcome.blade.php
// @component('mail::message')
// # Welcome {{ $user->name }}!
//
// Thank you for joining {{ config('app.name') }}.
//
// @component('mail::button', ['url' => $url])
// Get Started
// @endcomponent
//
// Thanks,<br>
// {{ config('app.name') }}
// @endcomponent
```

### 4. **Queued Mailable**

```php
<?php

namespace App\Mail;

use App\Models\Newsletter;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class NewsletterEmail extends Mailable implements ShouldQueue
{
    use Queueable, SerializesModels;

    public $tries = 3;
    public $timeout = 120;

    public function __construct(
        public Newsletter $newsletter,
        public string $subscriberEmail
    ) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            from: config('mail.from.newsletter'),
            subject: $this->newsletter->subject,
            tags: ['newsletter'],
        );
    }

    public function content(): Content
    {
        return new Content(
            view: 'emails.newsletter',
            with: [
                'unsubscribeUrl' => route('newsletter.unsubscribe', [
                    'email' => $this->subscriberEmail,
                ]),
            ],
        );
    }
}
```

### 5. **Localized Mailable**

```php
<?php

namespace App\Mail;

use App\Models\User;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class AccountVerification extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(
        public User $user,
        public string $verificationUrl
    ) {
        $this->locale($user->preferred_locale);
    }

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: __('Verify Your Email Address'),
        );
    }

    public function content(): Content
    {
        return new Content(
            markdown: 'emails.verify-email',
        );
    }
}
```

## Best Practices
- Use envelope() for metadata
- Use content() for view selection
- Implement ShouldQueue for bulk emails
- Use markdown for simpler templates
- Add attachments via attachments()
- Set proper from/reply-to addresses
- Use tags and metadata for tracking
- Test emails with Mailtrap/MailHog

Generate complete Laravel mailable with proper structure.
