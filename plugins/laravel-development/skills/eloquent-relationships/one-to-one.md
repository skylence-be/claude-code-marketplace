# One-to-One Relationships

One-to-One relationships link a single record to exactly one related record.

## Use Cases
- User → Profile
- User → Address
- Order → Invoice

## Implementation

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class User extends Model
{
    /**
     * Get the profile associated with the user.
     */
    public function profile(): HasOne
    {
        return $this->hasOne(Profile::class);
    }

    /**
     * Get the user's address.
     */
    public function address(): HasOne
    {
        return $this->hasOne(Address::class);
    }
}

class Profile extends Model
{
    protected $fillable = ['user_id', 'bio', 'avatar', 'website'];

    /**
     * Get the user that owns the profile.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}

class Address extends Model
{
    protected $fillable = ['user_id', 'street', 'city', 'state', 'zip'];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
```

## Usage Examples

```php
$user = User::find(1);

// Access profile
$profile = $user->profile;
$bio = $user->profile->bio;

// Create related model
$user->profile()->create([
    'bio' => 'Software developer',
    'avatar' => 'avatar.jpg',
    'website' => 'https://example.com'
]);

// Update or create (upsert)
$user->profile()->updateOrCreate(
    ['user_id' => $user->id],
    ['bio' => 'Updated bio']
);

// Access inverse relationship
$profile = Profile::find(1);
$owner = $profile->user;
```

## Migration

```php
Schema::create('profiles', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->cascadeOnDelete();
    $table->string('bio')->nullable();
    $table->string('avatar')->nullable();
    $table->string('website')->nullable();
    $table->timestamps();
});
```
