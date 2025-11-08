---
description: Create Filament 4 cluster for organizing resources
model: claude-sonnet-4-5
---

Create a Filament 4 cluster.

## Cluster Specification

$ARGUMENTS

## Filament Cluster Patterns

### 1. **Basic Cluster**

```php
<?php

namespace App\Filament\Clusters;

use Filament\Clusters\Cluster;

class Settings extends Cluster
{
    protected static ?string $navigationIcon = 'heroicon-o-cog-6-tooth';

    protected static ?string $navigationGroup = 'Administration';

    protected static ?int $navigationSort = 99;
}
```

### 2. **Cluster with Resources**

```php
<?php

namespace App\Filament\Clusters;

use Filament\Clusters\Cluster;

class Shop extends Cluster
{
    protected static ?string $navigationIcon = 'heroicon-o-shopping-bag';

    protected static ?string $navigationLabel = 'Shop Management';

    protected static ?int $navigationSort = 10;
}

// Resources belonging to this cluster:
// app/Filament/Clusters/Shop/Resources/ProductResource.php
// app/Filament/Clusters/Shop/Resources/CategoryResource.php
// app/Filament/Clusters/Shop/Resources/OrderResource.php
```

Generate complete Filament 4 cluster.
