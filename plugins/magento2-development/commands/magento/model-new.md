---
description: Create Magento 2 Model, ResourceModel, and Collection
model: claude-sonnet-4-5
---

Create Magento 2 Model with ResourceModel and Collection.

## Model Specification

$ARGUMENTS

## Magento 2 Model Pattern

### 1. **Model** (Model/Entity.php)

```php
<?php
namespace Vendor\Module\Model;

use Magento\Framework\Model\AbstractModel;
use Vendor\Module\Api\Data\EntityInterface;

class Entity extends AbstractModel implements EntityInterface
{
    const CACHE_TAG = 'vendor_module_entity';

    protected $_cacheTag = 'vendor_module_entity';
    protected $_eventPrefix = 'vendor_module_entity';

    protected function _construct()
    {
        $this->_init(\Vendor\Module\Model\ResourceModel\Entity::class);
    }

    public function getIdentities()
    {
        return [self::CACHE_TAG . '_' . $this->getId()];
    }
}
```

### 2. **ResourceModel** (Model/ResourceModel/Entity.php)

```php
<?php
namespace Vendor\Module\Model\ResourceModel;

use Magento\Framework\Model\ResourceModel\Db\AbstractDb;

class Entity extends AbstractDb
{
    protected function _construct()
    {
        $this->_init('vendor_module_entity', 'entity_id');
    }
}
```

### 3. **Collection** (Model/ResourceModel/Entity/Collection.php)

```php
<?php
namespace Vendor\Module\Model\ResourceModel\Entity;

use Magento\Framework\Model\ResourceModel\Db\Collection\AbstractCollection;

class Collection extends AbstractCollection
{
    protected $_idFieldName = 'entity_id';
    protected $_eventPrefix = 'vendor_module_entity_collection';
    protected $_eventObject = 'entity_collection';

    protected function _construct()
    {
        $this->_init(
            \Vendor\Module\Model\Entity::class,
            \Vendor\Module\Model\ResourceModel\Entity::class
        );
    }
}
```

### 4. **Data Interface** (Api/Data/EntityInterface.php)

```php
<?php
namespace Vendor\Module\Api\Data;

interface EntityInterface
{
    const ENTITY_ID = 'entity_id';
    const NAME = 'name';
    const STATUS = 'status';

    public function getId();
    public function getName();
    public function getStatus();

    public function setId($id);
    public function setName($name);
    public function setStatus($status);
}
```

### 5. **Repository** (Model/EntityRepository.php)

```php
<?php
namespace Vendor\Module\Model;

use Vendor\Module\Api\EntityRepositoryInterface;
use Vendor\Module\Api\Data\EntityInterface;
use Vendor\Module\Model\ResourceModel\Entity as ResourceEntity;
use Magento\Framework\Exception\CouldNotSaveException;
use Magento\Framework\Exception\NoSuchEntityException;

class EntityRepository implements EntityRepositoryInterface
{
    protected $resource;
    protected $entityFactory;

    public function __construct(
        ResourceEntity $resource,
        EntityFactory $entityFactory
    ) {
        $this->resource = $resource;
        $this->entityFactory = $entityFactory;
    }

    public function save(EntityInterface $entity)
    {
        try {
            $this->resource->save($entity);
        } catch (\Exception $exception) {
            throw new CouldNotSaveException(__($exception->getMessage()));
        }
        return $entity;
    }

    public function getById($entityId)
    {
        $entity = $this->entityFactory->create();
        $this->resource->load($entity, $entityId);
        if (!$entity->getId()) {
            throw new NoSuchEntityException(__('Entity with id "%1" does not exist.', $entityId));
        }
        return $entity;
    }

    public function delete(EntityInterface $entity)
    {
        try {
            $this->resource->delete($entity);
        } catch (\Exception $exception) {
            throw new CouldNotDeleteException(__($exception->getMessage()));
        }
        return true;
    }
}
```

Generate complete Magento 2 Model with ResourceModel, Collection, Interface, and Repository.
