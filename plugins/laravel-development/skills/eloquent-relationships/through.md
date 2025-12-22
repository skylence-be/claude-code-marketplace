# Through Relationships

Has-One-Through and Has-Many-Through relationships access distant relations through intermediate models.

## Has-One-Through

Access a single distant relation through an intermediate model.

### Use Case
Mechanic → Car → Owner (Mechanic's car owner)

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

class Mechanic extends Model
{
    /**
     * Get the car's owner (through Car).
     */
    public function carOwner(): HasOneThrough
    {
        return $this->hasOneThrough(
            Owner::class,     // Final model
            Car::class,       // Intermediate model
            'mechanic_id',    // Foreign key on cars table
            'car_id',         // Foreign key on owners table
            'id',             // Local key on mechanics table
            'id'              // Local key on cars table
        );
    }
}

class Car extends Model
{
    protected $fillable = ['mechanic_id', 'make', 'model'];

    public function mechanic()
    {
        return $this->belongsTo(Mechanic::class);
    }

    public function owner()
    {
        return $this->hasOne(Owner::class);
    }
}

class Owner extends Model
{
    protected $fillable = ['car_id', 'name', 'email'];

    public function car()
    {
        return $this->belongsTo(Car::class);
    }
}

// Usage
$mechanic = Mechanic::find(1);
$owner = $mechanic->carOwner; // Get owner through car
```

## Has-Many-Through

Access multiple distant relations through an intermediate model.

### Use Case
Country → Users → Posts (All posts by users in a country)

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasManyThrough;

class Country extends Model
{
    /**
     * Get all posts for the country (through users).
     */
    public function posts(): HasManyThrough
    {
        return $this->hasManyThrough(
            Post::class,      // Final model
            User::class,      // Intermediate model
            'country_id',     // Foreign key on users table
            'user_id',        // Foreign key on posts table
            'id',             // Local key on countries table
            'id'              // Local key on users table
        );
    }
}

class User extends Model
{
    public function country()
    {
        return $this->belongsTo(Country::class);
    }

    public function posts()
    {
        return $this->hasMany(Post::class);
    }
}

// Usage
$country = Country::find(1);
$posts = $country->posts; // All posts by users in this country

$recentPosts = $country->posts()
    ->where('created_at', '>', now()->subDays(7))
    ->get();
```

## Key Parameters

```
hasOneThrough / hasManyThrough(
    FinalModel::class,      // Target model
    IntermediateModel::class, // Middle model
    'first_key',            // FK on intermediate table pointing to local
    'second_key',           // FK on final table pointing to intermediate
    'local_key',            // PK on local table (usually 'id')
    'second_local_key'      // PK on intermediate table (usually 'id')
)
```

## Shorthand Syntax

When using conventional key names:

```php
// Shorthand (uses conventional keys)
public function posts(): HasManyThrough
{
    return $this->hasManyThrough(Post::class, User::class);
}
```
