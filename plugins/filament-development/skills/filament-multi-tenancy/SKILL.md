---
name: filament-multi-tenancy
description: Master Filament 4 multi-tenancy patterns including panel configuration, tenant models, tenant-aware queries, global scopes, tenant switching, billing, team management, and security isolation. Use when building SaaS applications or multi-tenant systems.
category: filament
tags: [filament, multi-tenancy, saas, teams, security, isolation]
related_skills: [filament-resource-patterns, laravel-security-patterns, eloquent-patterns]
---

# Filament Multi-Tenancy

Comprehensive guide to implementing multi-tenancy in Filament 4, covering panel configuration, tenant models and relationships, tenant-aware queries and global scopes, tenant switching and context management, billing and subscriptions, team management, invitations, tenant isolation strategies, and testing multi-tenant applications.

## When to Use This Skill

- Building SaaS applications with multiple customers/organizations
- Implementing team-based access control and workspaces
- Creating multi-tenant admin panels with data isolation
- Building applications with organization-level billing
- Implementing tenant-specific customization and branding
- Creating team collaboration features with role-based access
- Building invitation systems for team member management
- Implementing tenant switching for users across organizations
- Ensuring data security and isolation between tenants
- Testing multi-tenant application logic and data segregation

## Core Concepts

### 1. Tenancy Models
- **Tenant Model**: Organization, Team, Company entity
- **Ownership**: Resources belong to specific tenants
- **Relationships**: Users can belong to multiple tenants
- **Roles**: Tenant-specific user permissions
- **Context**: Current active tenant for user

### 2. Data Isolation
- **Global Scopes**: Automatically filter queries by tenant
- **Middleware**: Enforce tenant context on requests
- **Foreign Keys**: Tenant ID on all tenant-owned models
- **Validation**: Prevent cross-tenant data access
- **Security**: Strict tenant boundary enforcement

### 3. Panel Configuration
- **Tenant Registration**: Enable tenancy on panels
- **Tenant Routes**: URL structure with tenant context
- **Tenant Middleware**: Verify tenant access
- **Tenant Menu**: Show current tenant information
- **Tenant Switching**: UI for changing active tenant

### 4. Team Features
- **Members**: Users within a tenant
- **Invitations**: Invite new team members
- **Roles**: Member-specific permissions
- **Ownership**: Tenant owner/admin
- **Billing**: Subscription management

### 5. Advanced Features
- **Subdomain Tenancy**: Tenant-specific domains
- **Customization**: Per-tenant branding
- **Storage**: Isolated file storage
- **Notifications**: Tenant-scoped notifications
- **Analytics**: Per-tenant metrics

## Quick Start

```php
<?php

// Configure panel for tenancy
use Filament\Panel;

public function panel(Panel $panel): Panel
{
    return $panel
        ->tenant(Team::class)
        ->tenantRegistration(RegisterTeam::class)
        ->tenantProfile(EditTeam::class);
}
```

## Fundamental Patterns

### Pattern 1: Basic Panel Tenancy Configuration

```php
<?php

namespace App\Providers\Filament;

use App\Filament\Pages\Tenancy\EditTeam;
use App\Filament\Pages\Tenancy\RegisterTeam;
use App\Models\Team;
use Filament\Http\Middleware\Authenticate;
use Filament\Http\Middleware\DisableBladeIconComponents;
use Filament\Http\Middleware\DispatchServingFilamentEvent;
use Filament\Panel;
use Filament\PanelProvider;
use Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse;
use Illuminate\Cookie\Middleware\EncryptCookies;
use Illuminate\Foundation\Http\Middleware\VerifyCsrfToken;
use Illuminate\Routing\Middleware\SubstituteBindings;
use Illuminate\Session\Middleware\AuthenticateSession;
use Illuminate\Session\Middleware\StartSession;
use Illuminate\View\Middleware\ShareErrorsFromSession;

class AdminPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        return $panel
            ->default()
            ->id('admin')
            ->path('app')
            ->login()
            ->registration()
            ->passwordReset()
            ->emailVerification()
            // Enable multi-tenancy
            ->tenant(Team::class)
            ->tenantRegistration(RegisterTeam::class)
            ->tenantProfile(EditTeam::class)
            ->tenantMenuItems([
                'register' => MenuItem::make()->label('Create Team'),
                'profile' => MenuItem::make()->label('Team Settings'),
            ])
            // Customize tenant menu
            ->tenantMenu(fn () => auth()->user()->teams()->count() > 1)
            ->tenantBillingProvider(new StripeProvider())
            // Tenant ownership relationship
            ->tenantOwnershipRelationshipName('team')
            // URL structure: /app/team-slug/...
            ->tenantRoutePrefix('/{tenant}')
            ->colors([
                'primary' => Color::Amber,
            ])
            ->discoverResources(in: app_path('Filament/Resources'), for: 'App\\Filament\\Resources')
            ->discoverPages(in: app_path('Filament/Pages'), for: 'App\\Filament\\Pages')
            ->pages([
                Pages\Dashboard::class,
            ])
            ->discoverWidgets(in: app_path('Filament/Widgets'), for: 'App\\Filament\\Widgets')
            ->middleware([
                EncryptCookies::class,
                AddQueuedCookiesToResponse::class,
                StartSession::class,
                AuthenticateSession::class,
                ShareErrorsFromSession::class,
                VerifyCsrfToken::class,
                SubstituteBindings::class,
                DisableBladeIconComponents::class,
                DispatchServingFilamentEvent::class,
            ])
            ->authMiddleware([
                Authenticate::class,
            ]);
    }
}
```

### Pattern 2: Tenant Model with Relationships

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\SoftDeletes;

class Team extends Model
{
    use HasFactory, SoftDeletes;

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

    /**
     * Get the owner of the team.
     */
    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'owner_id');
    }

    /**
     * Get all team members.
     */
    public function members(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'team_user')
            ->withPivot(['role', 'permissions', 'joined_at'])
            ->withTimestamps()
            ->using(TeamMember::class);
    }

    /**
     * Get pending invitations.
     */
    public function invitations(): HasMany
    {
        return $this->hasMany(TeamInvitation::class);
    }

    /**
     * Get team projects.
     */
    public function projects(): HasMany
    {
        return $this->hasMany(Project::class);
    }

    /**
     * Get team documents.
     */
    public function documents(): HasMany
    {
        return $this->hasMany(Document::class);
    }

    /**
     * Get team subscription.
     */
    public function subscription(): HasMany
    {
        return $this->hasMany(Subscription::class);
    }

    /**
     * Check if user is team owner.
     */
    public function isOwner(User $user): bool
    {
        return $this->owner_id === $user->id;
    }

    /**
     * Check if user is team member.
     */
    public function hasMember(User $user): bool
    {
        return $this->members->contains($user);
    }

    /**
     * Get member role.
     */
    public function getMemberRole(User $user): ?string
    {
        return $this->members()
            ->where('user_id', $user->id)
            ->first()
            ?->pivot
            ?->role;
    }

    /**
     * Check if team has active subscription.
     */
    public function hasActiveSubscription(): bool
    {
        return $this->subscription_ends_at &&
               $this->subscription_ends_at->isFuture();
    }

    /**
     * Check if team is on trial.
     */
    public function onTrial(): bool
    {
        return $this->trial_ends_at &&
               $this->trial_ends_at->isFuture() &&
               !$this->hasActiveSubscription();
    }

    /**
     * Get team storage limit.
     */
    public function getStorageLimit(): int
    {
        return match($this->plan) {
            'free' => 1024 * 1024 * 100, // 100MB
            'pro' => 1024 * 1024 * 1024 * 10, // 10GB
            'enterprise' => 1024 * 1024 * 1024 * 100, // 100GB
            default => 0,
        };
    }

    /**
     * Get team member limit.
     */
    public function getMemberLimit(): ?int
    {
        return match($this->plan) {
            'free' => 3,
            'pro' => 25,
            'enterprise' => null, // Unlimited
            default => 1,
        };
    }

    /**
     * Check if team can add more members.
     */
    public function canAddMember(): bool
    {
        $limit = $this->getMemberLimit();

        if ($limit === null) {
            return true; // Unlimited
        }

        return $this->members()->count() < $limit;
    }

    /**
     * Boot the model.
     */
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

### Pattern 3: User Model with Tenant Relationships

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

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
    ];

    /**
     * Get teams the user belongs to.
     */
    public function teams(): BelongsToMany
    {
        return $this->belongsToMany(Team::class, 'team_user')
            ->withPivot(['role', 'permissions', 'joined_at'])
            ->withTimestamps()
            ->using(TeamMember::class);
    }

    /**
     * Get teams owned by the user.
     */
    public function ownedTeams(): HasMany
    {
        return $this->hasMany(Team::class, 'owner_id');
    }

    /**
     * Get current team.
     */
    public function currentTeam()
    {
        return $this->belongsTo(Team::class, 'current_team_id');
    }

    /**
     * Get all tenants (teams) for Filament.
     */
    public function getTenants(Panel $panel): Collection
    {
        return $this->teams;
    }

    /**
     * Check if user can access tenant.
     */
    public function canAccessTenant(Model $tenant): bool
    {
        return $this->teams->contains($tenant);
    }

    /**
     * Check if user can access panel.
     */
    public function canAccessPanel(Panel $panel): bool
    {
        return true; // Add custom logic if needed
    }

    /**
     * Switch to a different team.
     */
    public function switchTeam(Team $team): void
    {
        if (!$this->canAccessTenant($team)) {
            throw new \Exception('Cannot access this team');
        }

        $this->update(['current_team_id' => $team->id]);
    }

    /**
     * Check if user owns team.
     */
    public function ownsTeam(Team $team): bool
    {
        return $this->id === $team->owner_id;
    }

    /**
     * Get role in team.
     */
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

    /**
     * Check if user has permission in team.
     */
    public function hasTeamPermission(Team $team, string $permission): bool
    {
        if ($this->ownsTeam($team)) {
            return true; // Owners have all permissions
        }

        $pivot = $this->teams()
            ->where('team_id', $team->id)
            ->first()
            ?->pivot;

        if (!$pivot) {
            return false;
        }

        $permissions = $pivot->permissions ?? [];

        return in_array($permission, $permissions);
    }
}
```

### Pattern 4: Tenant-Aware Resources

```php
<?php

namespace App\Filament\Resources;

use App\Models\Project;
use Filament\Facades\Filament;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class ProjectResource extends Resource
{
    protected static ?string $model = Project::class;

    protected static ?string $navigationIcon = 'heroicon-o-folder';

    protected static ?string $tenantOwnershipRelationshipName = 'team';

    /**
     * Scope all queries to current tenant.
     */
    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->whereBelongsTo(Filament::getTenant());
    }

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Hidden::make('team_id')
                    ->default(fn () => Filament::getTenant()->id),

                Forms\Components\TextInput::make('name')
                    ->required()
                    ->maxLength(255),

                Forms\Components\Textarea::make('description')
                    ->rows(4)
                    ->maxLength(1000),

                Forms\Components\Select::make('status')
                    ->options([
                        'planning' => 'Planning',
                        'active' => 'Active',
                        'on_hold' => 'On Hold',
                        'completed' => 'Completed',
                    ])
                    ->default('planning')
                    ->required(),

                Forms\Components\DatePicker::make('start_date')
                    ->native(false),

                Forms\Components\DatePicker::make('end_date')
                    ->native(false)
                    ->after('start_date'),

                Forms\Components\Select::make('owner_id')
                    ->label('Project Owner')
                    ->options(function () {
                        $team = Filament::getTenant();
                        return $team->members()->pluck('name', 'id');
                    })
                    ->searchable()
                    ->required(),

                Forms\Components\Select::make('members')
                    ->label('Team Members')
                    ->multiple()
                    ->options(function () {
                        $team = Filament::getTenant();
                        return $team->members()->pluck('name', 'id');
                    })
                    ->searchable()
                    ->preload(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->sortable()
                    ->weight('bold'),

                Tables\Columns\BadgeColumn::make('status')
                    ->colors([
                        'secondary' => 'planning',
                        'primary' => 'active',
                        'warning' => 'on_hold',
                        'success' => 'completed',
                    ]),

                Tables\Columns\TextColumn::make('owner.name')
                    ->searchable()
                    ->sortable(),

                Tables\Columns\TextColumn::make('members_count')
                    ->counts('members')
                    ->label('Members')
                    ->badge(),

                Tables\Columns\TextColumn::make('start_date')
                    ->date()
                    ->sortable(),

                Tables\Columns\TextColumn::make('end_date')
                    ->date()
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'planning' => 'Planning',
                        'active' => 'Active',
                        'on_hold' => 'On Hold',
                        'completed' => 'Completed',
                    ])
                    ->multiple(),

                Tables\Filters\SelectFilter::make('owner')
                    ->relationship('owner', 'name')
                    ->searchable()
                    ->preload()
                    ->multiple(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    /**
     * Authorize resource access.
     */
    public static function canAccess(): bool
    {
        return Filament::getTenant() !== null;
    }

    /**
     * Authorize viewing any records.
     */
    public static function canViewAny(): bool
    {
        $tenant = Filament::getTenant();

        if (!$tenant) {
            return false;
        }

        return auth()->user()->hasTeamPermission($tenant, 'view_projects');
    }

    /**
     * Authorize creating records.
     */
    public static function canCreate(): bool
    {
        $tenant = Filament::getTenant();

        if (!$tenant) {
            return false;
        }

        return auth()->user()->hasTeamPermission($tenant, 'create_projects');
    }

    /**
     * Authorize editing records.
     */
    public static function canEdit(Model $record): bool
    {
        $tenant = Filament::getTenant();

        // Verify record belongs to current tenant
        if ($record->team_id !== $tenant->id) {
            return false;
        }

        return auth()->user()->hasTeamPermission($tenant, 'edit_projects');
    }

    /**
     * Authorize deleting records.
     */
    public static function canDelete(Model $record): bool
    {
        $tenant = Filament::getTenant();

        if ($record->team_id !== $tenant->id) {
            return false;
        }

        return auth()->user()->hasTeamPermission($tenant, 'delete_projects');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListProjects::route('/'),
            'create' => Pages\CreateProject::route('/create'),
            'edit' => Pages\EditProject::route('/{record}/edit'),
        ];
    }
}
```

### Pattern 5: Team Registration Page

```php
<?php

namespace App\Filament\Pages\Tenancy;

use App\Models\Team;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\Toggle;
use Filament\Forms\Form;
use Filament\Pages\Tenancy\RegisterTenant;

class RegisterTeam extends RegisterTenant
{
    public static function getLabel(): string
    {
        return 'Create Team';
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                TextInput::make('name')
                    ->label('Team Name')
                    ->required()
                    ->maxLength(255)
                    ->live(onBlur: true)
                    ->afterStateUpdated(function ($state, callable $set) {
                        $set('slug', \Str::slug($state));
                    }),

                TextInput::make('slug')
                    ->required()
                    ->unique(Team::class)
                    ->maxLength(255)
                    ->helperText('This will be used in your team URL')
                    ->regex('/^[a-z0-9-]+$/')
                    ->rules(['alpha_dash']),

                Select::make('plan')
                    ->label('Subscription Plan')
                    ->options([
                        'free' => 'Free (Up to 3 members)',
                        'pro' => 'Pro ($29/month - Up to 25 members)',
                        'enterprise' => 'Enterprise ($99/month - Unlimited)',
                    ])
                    ->default('free')
                    ->required()
                    ->native(false)
                    ->helperText('You can change this later in team settings'),

                Toggle::make('start_trial')
                    ->label('Start 14-day free trial')
                    ->helperText('No credit card required')
                    ->default(true)
                    ->visible(fn ($get) => in_array($get('plan'), ['pro', 'enterprise'])),
            ]);
    }

    protected function handleRegistration(array $data): Team
    {
        $team = Team::create([
            'name' => $data['name'],
            'slug' => $data['slug'],
            'owner_id' => auth()->id(),
            'plan' => $data['plan'],
            'trial_ends_at' => $data['start_trial'] ?? false
                ? now()->addDays(14)
                : null,
        ]);

        // Add creator as team member
        $team->members()->attach(auth()->id(), [
            'role' => 'owner',
            'permissions' => ['*'], // All permissions
            'joined_at' => now(),
        ]);

        // Send welcome email
        \Notification::route('mail', auth()->user()->email)
            ->notify(new TeamCreatedNotification($team));

        return $team;
    }
}
```

### Pattern 6: Team Profile/Settings Page

```php
<?php

namespace App\Filament\Pages\Tenancy;

use App\Models\Team;
use Filament\Facades\Filament;
use Filament\Forms\Components\FileUpload;
use Filament\Forms\Components\Grid;
use Filament\Forms\Components\Section;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Forms\Components\ColorPicker;
use Filament\Forms\Form;
use Filament\Pages\Tenancy\EditTenantProfile;
use Filament\Notifications\Notification;

class EditTeam extends EditTenantProfile
{
    public static function getLabel(): string
    {
        return 'Team Settings';
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Section::make('Team Information')
                    ->schema([
                        TextInput::make('name')
                            ->required()
                            ->maxLength(255),

                        TextInput::make('slug')
                            ->required()
                            ->unique(Team::class, ignoreRecord: true)
                            ->maxLength(255)
                            ->helperText('Changing this will affect your team URL'),

                        FileUpload::make('logo')
                            ->image()
                            ->imageEditor()
                            ->directory('team-logos')
                            ->maxSize(2048)
                            ->columnSpanFull(),
                    ])
                    ->columns(2),

                Section::make('Branding')
                    ->schema([
                        ColorPicker::make('branding.primary_color')
                            ->label('Primary Color')
                            ->default('#3b82f6'),

                        ColorPicker::make('branding.secondary_color')
                            ->label('Secondary Color')
                            ->default('#6366f1'),

                        Toggle::make('branding.custom_domain')
                            ->label('Use Custom Domain')
                            ->helperText('Available on Enterprise plan'),

                        TextInput::make('branding.domain')
                            ->label('Custom Domain')
                            ->url()
                            ->visible(fn ($get) => $get('branding.custom_domain')),
                    ])
                    ->columns(2)
                    ->collapsible(),

                Section::make('Subscription')
                    ->schema([
                        Select::make('plan')
                            ->options([
                                'free' => 'Free',
                                'pro' => 'Pro',
                                'enterprise' => 'Enterprise',
                            ])
                            ->disabled()
                            ->helperText('Contact support to change your plan'),

                        TextInput::make('subscription_ends_at')
                            ->label('Subscription Valid Until')
                            ->disabled()
                            ->formatStateUsing(fn ($state) =>
                                $state ? $state->format('M d, Y') : 'N/A'
                            ),
                    ])
                    ->columns(2)
                    ->visible(fn () => Filament::getTenant()->hasActiveSubscription()),

                Section::make('Danger Zone')
                    ->schema([
                        Toggle::make('delete_confirmation')
                            ->label('I understand that deleting this team is permanent')
                            ->reactive(),

                        \Filament\Forms\Components\Actions::make([
                            \Filament\Forms\Components\Actions\Action::make('delete_team')
                                ->label('Delete Team')
                                ->color('danger')
                                ->icon('heroicon-o-trash')
                                ->requiresConfirmation()
                                ->disabled(fn ($get) => !$get('delete_confirmation'))
                                ->action(function () {
                                    $team = Filament::getTenant();

                                    if ($team->owner_id !== auth()->id()) {
                                        Notification::make()
                                            ->danger()
                                            ->title('Unauthorized')
                                            ->body('Only team owner can delete the team')
                                            ->send();
                                        return;
                                    }

                                    // Delete team
                                    $team->delete();

                                    // Redirect to dashboard
                                    return redirect()->route('filament.admin.pages.dashboard');
                                }),
                        ]),
                    ])
                    ->collapsible()
                    ->collapsed(),
            ]);
    }
}
```

### Pattern 7: Team Member Management

```php
<?php

namespace App\Filament\Pages;

use App\Models\Team;
use App\Models\TeamInvitation;
use Filament\Facades\Filament;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Tables\Concerns\InteractsWithTable;
use Filament\Tables\Contracts\HasTable;

class TeamMembers extends Page implements HasTable
{
    use InteractsWithTable;

    protected static ?string $navigationIcon = 'heroicon-o-users';

    protected static string $view = 'filament.pages.team-members';

    protected static ?string $navigationGroup = 'Team Management';

    public static function canAccess(): bool
    {
        $team = Filament::getTenant();
        return $team && auth()->user()->hasTeamPermission($team, 'manage_members');
    }

    protected function getHeaderActions(): array
    {
        return [
            \Filament\Actions\Action::make('invite')
                ->label('Invite Member')
                ->icon('heroicon-o-envelope')
                ->form([
                    Forms\Components\TextInput::make('email')
                        ->email()
                        ->required()
                        ->unique(TeamInvitation::class, 'email', function ($query) {
                            return $query->where('team_id', Filament::getTenant()->id)
                                ->whereNull('accepted_at');
                        })
                        ->helperText('User will receive an invitation email'),

                    Forms\Components\Select::make('role')
                        ->options([
                            'admin' => 'Admin - Full access',
                            'member' => 'Member - Standard access',
                            'viewer' => 'Viewer - Read-only access',
                        ])
                        ->default('member')
                        ->required(),

                    Forms\Components\CheckboxList::make('permissions')
                        ->options([
                            'view_projects' => 'View Projects',
                            'create_projects' => 'Create Projects',
                            'edit_projects' => 'Edit Projects',
                            'delete_projects' => 'Delete Projects',
                            'manage_members' => 'Manage Team Members',
                        ])
                        ->columns(2),
                ])
                ->action(function (array $data) {
                    $team = Filament::getTenant();

                    if (!$team->canAddMember()) {
                        Notification::make()
                            ->danger()
                            ->title('Member limit reached')
                            ->body('Upgrade your plan to add more members')
                            ->send();
                        return;
                    }

                    $invitation = TeamInvitation::create([
                        'team_id' => $team->id,
                        'email' => $data['email'],
                        'role' => $data['role'],
                        'permissions' => $data['permissions'] ?? [],
                        'invited_by' => auth()->id(),
                        'token' => \Str::random(32),
                    ]);

                    // Send invitation email
                    \Mail::to($data['email'])->send(new TeamInvitationMail($invitation));

                    Notification::make()
                        ->success()
                        ->title('Invitation sent')
                        ->body("Invitation sent to {$data['email']}")
                        ->send();
                })
                ->disabled(fn () => !Filament::getTenant()->canAddMember())
                ->modalWidth('lg'),
        ];
    }

    public function table(Table $table): Table
    {
        return $table
            ->query(
                Filament::getTenant()
                    ->members()
                    ->withPivot(['role', 'permissions', 'joined_at'])
            )
            ->columns([
                Tables\Columns\ImageColumn::make('avatar')
                    ->circular()
                    ->size(40)
                    ->defaultImageUrl(fn ($record) =>
                        'https://ui-avatars.com/api/?name=' . urlencode($record->name)
                    ),

                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->sortable()
                    ->description(fn ($record) => $record->email),

                Tables\Columns\BadgeColumn::make('pivot.role')
                    ->label('Role')
                    ->colors([
                        'danger' => 'owner',
                        'warning' => 'admin',
                        'primary' => 'member',
                        'secondary' => 'viewer',
                    ])
                    ->formatStateUsing(fn ($state) => ucfirst($state)),

                Tables\Columns\TextColumn::make('pivot.joined_at')
                    ->label('Joined')
                    ->date()
                    ->sortable()
                    ->since(),

                Tables\Columns\TextColumn::make('pivot.permissions')
                    ->label('Permissions')
                    ->badge()
                    ->formatStateUsing(fn ($state) => count($state ?? []))
                    ->tooltip(fn ($state) => implode(', ', $state ?? [])),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('role')
                    ->options([
                        'owner' => 'Owner',
                        'admin' => 'Admin',
                        'member' => 'Member',
                        'viewer' => 'Viewer',
                    ]),
            ])
            ->actions([
                Tables\Actions\Action::make('edit_role')
                    ->label('Edit')
                    ->icon('heroicon-o-pencil')
                    ->form([
                        Forms\Components\Select::make('role')
                            ->options([
                                'admin' => 'Admin',
                                'member' => 'Member',
                                'viewer' => 'Viewer',
                            ])
                            ->default(fn ($record) => $record->pivot->role)
                            ->required(),

                        Forms\Components\CheckboxList::make('permissions')
                            ->options([
                                'view_projects' => 'View Projects',
                                'create_projects' => 'Create Projects',
                                'edit_projects' => 'Edit Projects',
                                'delete_projects' => 'Delete Projects',
                                'manage_members' => 'Manage Team Members',
                            ])
                            ->default(fn ($record) => $record->pivot->permissions ?? [])
                            ->columns(2),
                    ])
                    ->action(function ($record, array $data) {
                        Filament::getTenant()
                            ->members()
                            ->updateExistingPivot($record->id, [
                                'role' => $data['role'],
                                'permissions' => $data['permissions'],
                            ]);

                        Notification::make()
                            ->success()
                            ->title('Member updated')
                            ->send();
                    })
                    ->visible(fn ($record) =>
                        $record->id !== Filament::getTenant()->owner_id
                    ),

                Tables\Actions\DeleteAction::make()
                    ->label('Remove')
                    ->requiresConfirmation()
                    ->action(function ($record) {
                        Filament::getTenant()
                            ->members()
                            ->detach($record->id);

                        Notification::make()
                            ->success()
                            ->title('Member removed')
                            ->send();
                    })
                    ->visible(fn ($record) =>
                        $record->id !== Filament::getTenant()->owner_id
                    ),
            ]);
    }
}
```

### Pattern 8: Global Scopes for Tenant Isolation

```php
<?php

namespace App\Models\Scopes;

use Filament\Facades\Filament;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Scope;

class TenantScope implements Scope
{
    /**
     * Apply the scope to a given Eloquent query builder.
     */
    public function apply(Builder $builder, Model $model): void
    {
        $tenant = Filament::getTenant();

        if ($tenant) {
            $builder->where($model->getTable() . '.team_id', $tenant->id);
        }
    }
}
```

```php
<?php

namespace App\Models;

use App\Models\Scopes\TenantScope;
use Illuminate\Database\Eloquent\Model;

class Document extends Model
{
    protected $fillable = [
        'team_id',
        'name',
        'path',
        'size',
        'mime_type',
    ];

    /**
     * Boot the model.
     */
    protected static function booted(): void
    {
        // Automatically apply tenant scope
        static::addGlobalScope(new TenantScope());

        // Set team_id on create
        static::creating(function ($model) {
            if (empty($model->team_id)) {
                $model->team_id = Filament::getTenant()->id;
            }
        });
    }

    /**
     * Relationship to team.
     */
    public function team()
    {
        return $this->belongsTo(Team::class);
    }
}
```

## Advanced Patterns

### Pattern 9: Tenant Billing and Subscriptions

```php
<?php

namespace App\Filament\Pages;

use App\Models\Team;
use Filament\Facades\Filament;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Laravel\Cashier\Cashier;

class TeamBilling extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-credit-card';

    protected static string $view = 'filament.pages.team-billing';

    protected static ?string $navigationGroup = 'Team Management';

    public ?array $data = [];

    public function mount(): void
    {
        $this->form->fill([
            'plan' => Filament::getTenant()->plan,
        ]);
    }

    public static function canAccess(): bool
    {
        $team = Filament::getTenant();
        return $team && ($team->owner_id === auth()->id());
    }

    protected function getFormSchema(): array
    {
        $team = Filament::getTenant();

        return [
            Forms\Components\Section::make('Current Plan')
                ->schema([
                    Forms\Components\Placeholder::make('current_plan')
                        ->label('Plan')
                        ->content(fn () => ucfirst($team->plan)),

                    Forms\Components\Placeholder::make('status')
                        ->label('Status')
                        ->content(function () use ($team) {
                            if ($team->onTrial()) {
                                return 'Trial (ends ' . $team->trial_ends_at->format('M d, Y') . ')';
                            }

                            if ($team->hasActiveSubscription()) {
                                return 'Active (renews ' . $team->subscription_ends_at->format('M d, Y') . ')';
                            }

                            return 'Inactive';
                        }),

                    Forms\Components\Placeholder::make('members')
                        ->label('Team Members')
                        ->content(fn () =>
                            $team->members()->count() . ' / ' . ($team->getMemberLimit() ?? '∞')
                        ),
                ])
                ->columns(3),

            Forms\Components\Section::make('Change Plan')
                ->schema([
                    Forms\Components\Radio::make('plan')
                        ->label('Select Plan')
                        ->options([
                            'free' => 'Free - Up to 3 members',
                            'pro' => 'Pro - $29/month - Up to 25 members',
                            'enterprise' => 'Enterprise - $99/month - Unlimited',
                        ])
                        ->descriptions([
                            'free' => '100MB storage, basic features',
                            'pro' => '10GB storage, advanced features, priority support',
                            'enterprise' => '100GB storage, all features, dedicated support',
                        ])
                        ->required()
                        ->reactive(),

                    Forms\Components\Actions::make([
                        Forms\Components\Actions\Action::make('update_plan')
                            ->label(fn ($get) =>
                                $get('plan') === 'free' ? 'Downgrade to Free' : 'Subscribe'
                            )
                            ->color(fn ($get) =>
                                $get('plan') === 'free' ? 'danger' : 'primary'
                            )
                            ->requiresConfirmation()
                            ->disabled(fn ($get) => $get('plan') === $team->plan)
                            ->action(function (array $data) use ($team) {
                                if ($data['plan'] === 'free') {
                                    // Downgrade to free
                                    $team->subscription()->cancel();
                                    $team->update(['plan' => 'free']);

                                    Notification::make()
                                        ->success()
                                        ->title('Downgraded to Free')
                                        ->send();
                                } else {
                                    // Redirect to Stripe checkout
                                    $checkout = $team->newSubscription('default', $data['plan'])
                                        ->checkout([
                                            'success_url' => route('filament.admin.pages.team-billing'),
                                            'cancel_url' => route('filament.admin.pages.team-billing'),
                                        ]);

                                    return redirect($checkout->url);
                                }
                            }),
                    ]),
                ])
                ->collapsible(),

            Forms\Components\Section::make('Payment Method')
                ->schema([
                    Forms\Components\Placeholder::make('payment_method')
                        ->content(function () use ($team) {
                            $paymentMethod = $team->defaultPaymentMethod();

                            if (!$paymentMethod) {
                                return 'No payment method on file';
                            }

                            return "{$paymentMethod->card->brand} ending in {$paymentMethod->card->last4}";
                        }),

                    Forms\Components\Actions::make([
                        Forms\Components\Actions\Action::make('update_payment')
                            ->label('Update Payment Method')
                            ->icon('heroicon-o-credit-card')
                            ->action(function () use ($team) {
                                $session = $team->newSubscription('default', $team->plan)
                                    ->checkout([
                                        'success_url' => route('filament.admin.pages.team-billing'),
                                        'cancel_url' => route('filament.admin.pages.team-billing'),
                                    ]);

                                return redirect($session->url);
                            }),
                    ]),
                ])
                ->visible(fn () => $team->hasActiveSubscription())
                ->collapsible(),

            Forms\Components\Section::make('Invoices')
                ->schema([
                    Forms\Components\Placeholder::make('invoices')
                        ->content(function () use ($team) {
                            $invoices = $team->invoices();

                            if ($invoices->isEmpty()) {
                                return 'No invoices yet';
                            }

                            return view('filament.components.invoice-list', [
                                'invoices' => $invoices,
                            ]);
                        }),
                ])
                ->visible(fn () => $team->hasActiveSubscription())
                ->collapsible(),
        ];
    }
}
```

### Pattern 10: Tenant Storage Isolation

```php
<?php

namespace App\Services;

use App\Models\Team;
use Filament\Facades\Filament;
use Illuminate\Support\Facades\Storage;

class TenantStorage
{
    /**
     * Get tenant-specific storage disk.
     */
    public static function disk(): \Illuminate\Contracts\Filesystem\Filesystem
    {
        $tenant = Filament::getTenant();

        if (!$tenant) {
            throw new \Exception('No active tenant');
        }

        return Storage::disk('tenant-' . $tenant->id);
    }

    /**
     * Store file in tenant storage.
     */
    public static function put(string $path, $contents, array $options = []): string
    {
        return static::disk()->put($path, $contents, $options);
    }

    /**
     * Get file from tenant storage.
     */
    public static function get(string $path): string
    {
        return static::disk()->get($path);
    }

    /**
     * Delete file from tenant storage.
     */
    public static function delete(string $path): bool
    {
        return static::disk()->delete($path);
    }

    /**
     * Get tenant storage usage.
     */
    public static function getUsage(): int
    {
        $disk = static::disk();
        $files = $disk->allFiles();

        $totalSize = 0;
        foreach ($files as $file) {
            $totalSize += $disk->size($file);
        }

        return $totalSize;
    }

    /**
     * Check if tenant has exceeded storage limit.
     */
    public static function hasExceededLimit(): bool
    {
        $tenant = Filament::getTenant();
        $usage = static::getUsage();
        $limit = $tenant->getStorageLimit();

        return $usage >= $limit;
    }

    /**
     * Get storage usage percentage.
     */
    public static function getUsagePercentage(): float
    {
        $tenant = Filament::getTenant();
        $usage = static::getUsage();
        $limit = $tenant->getStorageLimit();

        if ($limit === 0) {
            return 0;
        }

        return ($usage / $limit) * 100;
    }
}
```

## Testing Strategies

```php
<?php

namespace Tests\Feature\Filament;

use App\Filament\Resources\ProjectResource;
use App\Models\Project;
use App\Models\Team;
use App\Models\User;
use Filament\Facades\Filament;
use Livewire\Livewire;
use Tests\TestCase;

class MultiTenancyTest extends TestCase
{
    public function test_user_can_only_see_their_team_projects(): void
    {
        $team1 = Team::factory()->create();
        $team2 = Team::factory()->create();

        $user = User::factory()->create();
        $user->teams()->attach($team1);

        $team1Projects = Project::factory()->count(3)->create(['team_id' => $team1->id]);
        $team2Projects = Project::factory()->count(2)->create(['team_id' => $team2->id]);

        $this->actingAs($user);

        Filament::setTenant($team1);

        Livewire::test(ProjectResource\Pages\ListProjects::class)
            ->assertCanSeeTableRecords($team1Projects)
            ->assertCanNotSeeTableRecords($team2Projects);
    }

    public function test_user_cannot_access_other_team_project(): void
    {
        $team1 = Team::factory()->create();
        $team2 = Team::factory()->create();

        $user = User::factory()->create();
        $user->teams()->attach($team1);

        $team2Project = Project::factory()->create(['team_id' => $team2->id]);

        $this->actingAs($user);
        Filament::setTenant($team1);

        Livewire::test(ProjectResource\Pages\EditProject::class, [
            'record' => $team2Project->getRouteKey(),
        ])->assertForbidden();
    }

    public function test_team_member_permissions_enforced(): void
    {
        $team = Team::factory()->create();
        $user = User::factory()->create();

        $user->teams()->attach($team, [
            'role' => 'viewer',
            'permissions' => ['view_projects'], // No create permission
        ]);

        $this->actingAs($user);
        Filament::setTenant($team);

        expect(ProjectResource::canCreate())->toBeFalse();
        expect(ProjectResource::canViewAny())->toBeTrue();
    }
}
```

## Common Pitfalls

### Pitfall 1: Forgetting Tenant Scopes

```php
// WRONG: Not scoped to tenant
$projects = Project::all();

// CORRECT: Use resource query or add scope
$projects = ProjectResource::getEloquentQuery()->get();
```

### Pitfall 2: Not Setting Tenant ID

```php
// WRONG: Tenant ID not set
Project::create(['name' => 'Test']);

// CORRECT: Set tenant ID
Project::create([
    'name' => 'Test',
    'team_id' => Filament::getTenant()->id,
]);
```

### Pitfall 3: Cross-Tenant Data Leaks

```php
// WRONG: Can access other tenant data
$project = Project::find($id); // No tenant check

// CORRECT: Verify ownership
$project = ProjectResource::getEloquentQuery()->findOrFail($id);
```

## Best Practices

1. **Always use global scopes** for automatic tenant filtering
2. **Verify tenant ownership** before all operations
3. **Use Filament::getTenant()** consistently for current tenant
4. **Implement proper authorization** with policies and permissions
5. **Isolate tenant storage** in separate directories
6. **Test cross-tenant access** prevention thoroughly
7. **Set tenant ID automatically** in model events
8. **Cache tenant data** to reduce database queries
9. **Implement audit logging** for security
10. **Use subdomain tenancy** for better isolation (optional)

## Resources

- **Filament Multi-Tenancy**: https://filamentphp.com/docs/panels/tenancy
- **Laravel Multi-Tenancy**: https://laravel.com/docs/multi-tenancy
- **Spatie Multi-Tenancy**: https://spatie.be/docs/laravel-multitenancy
- **Laravel Cashier**: https://laravel.com/docs/billing
