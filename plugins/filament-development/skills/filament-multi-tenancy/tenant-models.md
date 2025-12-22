# Tenant Models

Filament 4 tenant and user models with relationships.

## Team (Tenant) Model

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\SoftDeletes;

class Team extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'name',
        'slug',
        'owner_id',
        'plan',
        'trial_ends_at',
        'subscription_ends_at',
        'settings',
        'branding',
    ];

    protected $casts = [
        'trial_ends_at' => 'datetime',
        'subscription_ends_at' => 'datetime',
        'settings' => 'array',
        'branding' => 'array',
    ];

    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'owner_id');
    }

    public function members(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'team_user')
            ->withPivot(['role', 'permissions', 'joined_at'])
            ->withTimestamps()
            ->using(TeamMember::class);
    }

    public function invitations(): HasMany
    {
        return $this->hasMany(TeamInvitation::class);
    }

    public function projects(): HasMany
    {
        return $this->hasMany(Project::class);
    }

    // Helper methods
    public function isOwner(User $user): bool
    {
        return $this->owner_id === $user->id;
    }

    public function hasMember(User $user): bool
    {
        return $this->members->contains($user);
    }

    public function getMemberRole(User $user): ?string
    {
        return $this->members()
            ->where('user_id', $user->id)
            ->first()
            ?->pivot
            ?->role;
    }

    public function hasActiveSubscription(): bool
    {
        return $this->subscription_ends_at &&
               $this->subscription_ends_at->isFuture();
    }

    public function onTrial(): bool
    {
        return $this->trial_ends_at &&
               $this->trial_ends_at->isFuture() &&
               !$this->hasActiveSubscription();
    }

    public function getMemberLimit(): ?int
    {
        return match($this->plan) {
            'free' => 3,
            'pro' => 25,
            'enterprise' => null, // Unlimited
            default => 1,
        };
    }

    public function canAddMember(): bool
    {
        $limit = $this->getMemberLimit();
        return $limit === null || $this->members()->count() < $limit;
    }

    protected static function boot()
    {
        parent::boot();

        static::creating(function ($team) {
            if (empty($team->slug)) {
                $team->slug = \Str::slug($team->name);
            }
        });
    }
}
```

## User Model with Tenants

```php
<?php

namespace App\Models;

use Filament\Models\Contracts\FilamentUser;
use Filament\Models\Contracts\HasTenants;
use Filament\Panel;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Support\Collection;

class User extends Authenticatable implements FilamentUser, HasTenants
{
    protected $fillable = [
        'name',
        'email',
        'password',
        'current_team_id',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
    ];

    public function teams(): BelongsToMany
    {
        return $this->belongsToMany(Team::class, 'team_user')
            ->withPivot(['role', 'permissions', 'joined_at'])
            ->withTimestamps()
            ->using(TeamMember::class);
    }

    public function ownedTeams(): HasMany
    {
        return $this->hasMany(Team::class, 'owner_id');
    }

    public function currentTeam()
    {
        return $this->belongsTo(Team::class, 'current_team_id');
    }

    // Required by HasTenants
    public function getTenants(Panel $panel): Collection
    {
        return $this->teams;
    }

    // Required by HasTenants
    public function canAccessTenant(Model $tenant): bool
    {
        return $this->teams->contains($tenant);
    }

    // Required by FilamentUser
    public function canAccessPanel(Panel $panel): bool
    {
        return true;
    }

    public function switchTeam(Team $team): void
    {
        if (!$this->canAccessTenant($team)) {
            throw new \Exception('Cannot access this team');
        }

        $this->update(['current_team_id' => $team->id]);
    }

    public function ownsTeam(Team $team): bool
    {
        return $this->id === $team->owner_id;
    }

    public function teamRole(Team $team): ?string
    {
        if ($this->ownsTeam($team)) {
            return 'owner';
        }

        return $this->teams()
            ->where('team_id', $team->id)
            ->first()
            ?->pivot
            ?->role;
    }

    public function hasTeamPermission(Team $team, string $permission): bool
    {
        if ($this->ownsTeam($team)) {
            return true;
        }

        $pivot = $this->teams()
            ->where('team_id', $team->id)
            ->first()
            ?->pivot;

        if (!$pivot) {
            return false;
        }

        $permissions = $pivot->permissions ?? [];
        return in_array($permission, $permissions) || in_array('*', $permissions);
    }
}
```

## Team Member Pivot Model

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Relations\Pivot;

class TeamMember extends Pivot
{
    protected $table = 'team_user';

    protected $casts = [
        'permissions' => 'array',
        'joined_at' => 'datetime',
    ];
}
```

## Migration

```php
Schema::create('teams', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('slug')->unique();
    $table->foreignId('owner_id')->constrained('users');
    $table->string('plan')->default('free');
    $table->timestamp('trial_ends_at')->nullable();
    $table->timestamp('subscription_ends_at')->nullable();
    $table->json('settings')->nullable();
    $table->json('branding')->nullable();
    $table->timestamps();
    $table->softDeletes();
});

Schema::create('team_user', function (Blueprint $table) {
    $table->id();
    $table->foreignId('team_id')->constrained()->cascadeOnDelete();
    $table->foreignId('user_id')->constrained()->cascadeOnDelete();
    $table->string('role')->default('member');
    $table->json('permissions')->nullable();
    $table->timestamp('joined_at')->nullable();
    $table->timestamps();

    $table->unique(['team_id', 'user_id']);
});
```
