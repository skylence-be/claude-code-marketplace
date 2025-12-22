# Many-to-Many Relationships

Many-to-Many relationships link multiple records on both sides through a pivot table.

## Use Cases
- Users ↔ Roles
- Posts ↔ Tags
- Students ↔ Courses

## Implementation

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\Pivot;

class User extends Model
{
    /**
     * The roles that belong to the user.
     */
    public function roles(): BelongsToMany
    {
        return $this->belongsToMany(Role::class)
            ->withTimestamps()
            ->withPivot('assigned_at', 'assigned_by');
    }

    /**
     * The teams that the user belongs to.
     */
    public function teams(): BelongsToMany
    {
        return $this->belongsToMany(Team::class, 'team_user')
            ->using(TeamUser::class)
            ->withPivot('role', 'joined_at')
            ->withTimestamps();
    }
}

class Role extends Model
{
    protected $fillable = ['name', 'description'];

    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class)->withTimestamps();
    }

    public function permissions(): BelongsToMany
    {
        return $this->belongsToMany(Permission::class);
    }
}

// Custom pivot model
class TeamUser extends Pivot
{
    protected $table = 'team_user';

    protected $casts = [
        'joined_at' => 'datetime',
    ];
}
```

## Pivot Table Migration

```php
Schema::create('role_user', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained()->cascadeOnDelete();
    $table->foreignId('role_id')->constrained()->cascadeOnDelete();
    $table->timestamp('assigned_at')->nullable();
    $table->foreignId('assigned_by')->nullable()->constrained('users');
    $table->timestamps();

    $table->primary(['user_id', 'role_id']);
});
```

## Usage Examples

```php
$user = User::find(1);

// Attach roles
$user->roles()->attach(1);
$user->roles()->attach([2, 3]);
$user->roles()->attach(1, ['assigned_at' => now(), 'assigned_by' => auth()->id()]);

// Detach roles
$user->roles()->detach(1);
$user->roles()->detach([1, 2, 3]);
$user->roles()->detach(); // Remove all

// Sync roles (attach/detach to match exactly)
$user->roles()->sync([1, 2, 3]);
$user->roles()->syncWithoutDetaching([4, 5]); // Only attach new

// Toggle roles
$user->roles()->toggle([1, 2, 3]);

// Access pivot data
foreach ($user->roles as $role) {
    echo $role->pivot->assigned_at;
    echo $role->pivot->assigned_by;
}

// Query with pivot conditions
$admins = User::whereHas('roles', function ($query) {
    $query->where('name', 'admin');
})->get();

// Update pivot
$user->roles()->updateExistingPivot($roleId, [
    'assigned_by' => auth()->id()
]);
```

## Common Patterns

### Check Role
```php
public function hasRole(string $roleName): bool
{
    return $this->roles()->where('name', $roleName)->exists();
}
```

### Assign Role
```php
public function assignRole(string $roleName): void
{
    $role = Role::where('name', $roleName)->firstOrFail();
    $this->roles()->attach($role->id);
}
```
