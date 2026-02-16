# Team Management

Filament 5 team registration, profile, and member management.

## Team Registration Page

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
                    ->afterStateUpdated(fn ($state, Set $set) =>
                        $set('slug', \Str::slug($state))
                    ),

                TextInput::make('slug')
                    ->required()
                    ->unique(Team::class)
                    ->maxLength(255)
                    ->helperText('Used in your team URL')
                    ->regex('/^[a-z0-9-]+$/'),

                Select::make('plan')
                    ->options([
                        'free' => 'Free (Up to 3 members)',
                        'pro' => 'Pro ($29/month)',
                        'enterprise' => 'Enterprise ($99/month)',
                    ])
                    ->default('free')
                    ->required(),

                Toggle::make('start_trial')
                    ->label('Start 14-day free trial')
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
            'trial_ends_at' => ($data['start_trial'] ?? false)
                ? now()->addDays(14)
                : null,
        ]);

        // Add creator as team owner
        $team->members()->attach(auth()->id(), [
            'role' => 'owner',
            'permissions' => ['*'],
            'joined_at' => now(),
        ]);

        return $team;
    }
}
```

## Team Profile/Settings Page

```php
<?php

namespace App\Filament\Pages\Tenancy;

use App\Models\Team;
use Filament\Facades\Filament;
use Filament\Forms\Components\FileUpload;
use Filament\Forms\Components\Section;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\ColorPicker;
use Filament\Forms\Components\Toggle;
use Filament\Forms\Form;
use Filament\Pages\Tenancy\EditTenantProfile;

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
                            ->unique(Team::class),

                        FileUpload::make('logo')
                            ->image()
                            ->imageEditor()
                            ->directory('team-logos')
                            ->maxSize(2048),
                    ])
                    ->columns(2),

                Section::make('Branding')
                    ->schema([
                        ColorPicker::make('branding.primary_color')
                            ->label('Primary Color')
                            ->default('#3b82f6'),

                        ColorPicker::make('branding.secondary_color')
                            ->label('Secondary Color'),

                        Toggle::make('branding.custom_domain')
                            ->label('Use Custom Domain'),

                        TextInput::make('branding.domain')
                            ->label('Custom Domain')
                            ->url()
                            ->visible(fn ($get) => $get('branding.custom_domain')),
                    ])
                    ->columns(2)
                    ->collapsible(),

                Section::make('Danger Zone')
                    ->schema([
                        Toggle::make('delete_confirmation')
                            ->label('I understand deletion is permanent')
                            ->live(),

                        \Filament\Forms\Components\Actions::make([
                            \Filament\Forms\Components\Actions\Action::make('delete_team')
                                ->label('Delete Team')
                                ->color('danger')
                                ->requiresConfirmation()
                                ->disabled(fn ($get) => !$get('delete_confirmation'))
                                ->action(function () {
                                    $team = Filament::getTenant();

                                    if ($team->owner_id !== auth()->id()) {
                                        Notification::make()
                                            ->danger()
                                            ->title('Only team owner can delete')
                                            ->send();
                                        return;
                                    }

                                    $team->delete();
                                    return redirect()->route('filament.admin.pages.dashboard');
                                }),
                        ]),
                    ])
                    ->collapsed(),
            ]);
    }
}
```

## Team Members Page

```php
<?php

namespace App\Filament\Pages;

use App\Models\TeamInvitation;
use Filament\Facades\Filament;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Filament\Tables;
use Filament\Tables\Contracts\HasTable;
use Filament\Tables\Concerns\InteractsWithTable;

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
                        ->unique(TeamInvitation::class, 'email', fn ($query) =>
                            $query->where('team_id', Filament::getTenant()->id)
                                ->whereNull('accepted_at')
                        ),

                    Forms\Components\Select::make('role')
                        ->options([
                            'admin' => 'Admin - Full access',
                            'member' => 'Member - Standard access',
                            'viewer' => 'Viewer - Read-only',
                        ])
                        ->default('member')
                        ->required(),

                    Forms\Components\CheckboxList::make('permissions')
                        ->options([
                            'view_projects' => 'View Projects',
                            'create_projects' => 'Create Projects',
                            'edit_projects' => 'Edit Projects',
                            'delete_projects' => 'Delete Projects',
                            'manage_members' => 'Manage Members',
                        ])
                        ->columns(2),
                ])
                ->action(function (array $data) {
                    $team = Filament::getTenant();

                    if (!$team->canAddMember()) {
                        Notification::make()
                            ->danger()
                            ->title('Member limit reached')
                            ->body('Upgrade to add more members')
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

                    \Mail::to($data['email'])->send(new TeamInvitationMail($invitation));

                    Notification::make()
                        ->success()
                        ->title('Invitation sent')
                        ->send();
                })
                ->disabled(fn () => !Filament::getTenant()->canAddMember()),
        ];
    }

    public function table(Tables\Table $table): Tables\Table
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
                    ->defaultImageUrl(fn ($record) =>
                        'https://ui-avatars.com/api/?name=' . urlencode($record->name)
                    ),

                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->description(fn ($record) => $record->email),

                Tables\Columns\BadgeColumn::make('pivot.role')
                    ->label('Role')
                    ->colors([
                        'danger' => 'owner',
                        'warning' => 'admin',
                        'primary' => 'member',
                        'secondary' => 'viewer',
                    ]),

                Tables\Columns\TextColumn::make('pivot.joined_at')
                    ->label('Joined')
                    ->since(),
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
                                'manage_members' => 'Manage Members',
                            ])
                            ->default(fn ($record) => $record->pivot->permissions ?? []),
                    ])
                    ->action(function ($record, array $data) {
                        Filament::getTenant()
                            ->members()
                            ->updateExistingPivot($record->id, [
                                'role' => $data['role'],
                                'permissions' => $data['permissions'],
                            ]);

                        Notification::make()->success()->title('Updated')->send();
                    })
                    ->visible(fn ($record) =>
                        $record->id !== Filament::getTenant()->owner_id
                    ),

                Tables\Actions\DeleteAction::make()
                    ->label('Remove')
                    ->action(fn ($record) =>
                        Filament::getTenant()->members()->detach($record->id)
                    )
                    ->visible(fn ($record) =>
                        $record->id !== Filament::getTenant()->owner_id
                    ),
            ]);
    }
}
```

## Team Invitation Model

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TeamInvitation extends Model
{
    protected $fillable = [
        'team_id',
        'email',
        'role',
        'permissions',
        'invited_by',
        'token',
        'accepted_at',
    ];

    protected $casts = [
        'permissions' => 'array',
        'accepted_at' => 'datetime',
    ];

    public function team()
    {
        return $this->belongsTo(Team::class);
    }

    public function inviter()
    {
        return $this->belongsTo(User::class, 'invited_by');
    }
}
```
