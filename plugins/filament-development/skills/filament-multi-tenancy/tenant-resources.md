# Tenant-Aware Resources

Filament 4 resources with tenant isolation and authorization.

## Basic Tenant-Aware Resource

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

    // Scope all queries to current tenant
    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->whereBelongsTo(Filament::getTenant());
    }

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                // Auto-set tenant ID
                Forms\Components\Hidden::make('team_id')
                    ->default(fn () => Filament::getTenant()->id),

                Forms\Components\TextInput::make('name')
                    ->required(),

                // Filter options by tenant
                Forms\Components\Select::make('owner_id')
                    ->label('Project Owner')
                    ->options(function () {
                        $team = Filament::getTenant();
                        return $team->members()->pluck('name', 'id');
                    })
                    ->searchable()
                    ->required(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('owner.name'),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ]);
    }

    // Authorization
    public static function canAccess(): bool
    {
        return Filament::getTenant() !== null;
    }

    public static function canViewAny(): bool
    {
        $tenant = Filament::getTenant();
        return $tenant && auth()->user()->hasTeamPermission($tenant, 'view_projects');
    }

    public static function canCreate(): bool
    {
        $tenant = Filament::getTenant();
        return $tenant && auth()->user()->hasTeamPermission($tenant, 'create_projects');
    }

    public static function canEdit(Model $record): bool
    {
        $tenant = Filament::getTenant();

        // Verify record belongs to current tenant
        if ($record->team_id !== $tenant->id) {
            return false;
        }

        return auth()->user()->hasTeamPermission($tenant, 'edit_projects');
    }

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

## Global Scope for Tenant Isolation

```php
<?php

namespace App\Models\Scopes;

use Filament\Facades\Filament;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Scope;

class TenantScope implements Scope
{
    public function apply(Builder $builder, Model $model): void
    {
        $tenant = Filament::getTenant();

        if ($tenant) {
            $builder->where($model->getTable() . '.team_id', $tenant->id);
        }
    }
}
```

## Tenant-Aware Model

```php
<?php

namespace App\Models;

use App\Models\Scopes\TenantScope;
use Filament\Facades\Filament;
use Illuminate\Database\Eloquent\Model;

class Document extends Model
{
    protected $fillable = ['team_id', 'name', 'path'];

    protected static function booted(): void
    {
        // Auto-apply tenant scope
        static::addGlobalScope(new TenantScope());

        // Auto-set team_id on create
        static::creating(function ($model) {
            if (empty($model->team_id) && Filament::getTenant()) {
                $model->team_id = Filament::getTenant()->id;
            }
        });
    }

    public function team()
    {
        return $this->belongsTo(Team::class);
    }
}
```

## Tenant-Scoped Relationships

```php
// In resource form
Forms\Components\Select::make('folder_id')
    ->relationship(
        'folder',
        'name',
        fn (Builder $query) => $query->whereBelongsTo(Filament::getTenant())
    )
    ->searchable()
    ->preload(),

// Multi-select with tenant scope
Forms\Components\Select::make('tags')
    ->multiple()
    ->relationship(
        'tags',
        'name',
        fn (Builder $query) => $query->where('team_id', Filament::getTenant()->id)
    )
    ->preload(),
```

## Navigation Badge Per Tenant

```php
public static function getNavigationBadge(): ?string
{
    $tenant = Filament::getTenant();

    if (!$tenant) {
        return null;
    }

    return static::getModel()::whereBelongsTo($tenant)
        ->where('status', 'pending')
        ->count();
}

public static function getNavigationBadgeColor(): ?string
{
    $badge = static::getNavigationBadge();

    return match (true) {
        $badge > 10 => 'danger',
        $badge > 0 => 'warning',
        default => 'success',
    };
}
```

## Cross-Tenant Prevention

```php
// In resource or controller
public function resolveRecord($key): Model
{
    $record = parent::resolveRecord($key);

    // Verify tenant ownership
    if ($record->team_id !== Filament::getTenant()->id) {
        abort(403, 'You do not have access to this resource.');
    }

    return $record;
}
```
