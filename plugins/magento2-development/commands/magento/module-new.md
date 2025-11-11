---
description: Create complete Magento 2 module with proper structure
model: claude-sonnet-4-5
---

Create a complete Magento 2 module following best practices.

## Module Specification

$ARGUMENTS

## Magento 2 Module Structure

### 1. **Basic Module Files**

**registration.php** (app/code/Vendor/Module/)
```php
<?php
use Magento\Framework\Component\ComponentRegistrar;

ComponentRegistrar::register(
    ComponentRegistrar::MODULE,
    'Vendor_Module',
    __DIR__
);
```

**etc/module.xml**
```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Module/etc/module.xsd">
    <module name="Vendor_Module" setup_version="1.0.0">
        <sequence>
            <module name="Magento_Catalog"/>
        </sequence>
    </module>
</config>
```

**composer.json**
```json
{
    "name": "vendor/module-name",
    "description": "Module description",
    "type": "magento2-module",
    "version": "1.0.0",
    "license": "proprietary",
    "autoload": {
        "files": ["registration.php"],
        "psr-4": {
            "Vendor\\Module\\": ""
        }
    }
}
```

### 2. **Dependency Injection** (etc/di.xml)

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd">

    <!-- Preferences -->
    <preference for="Vendor\Module\Api\DataInterface"
                type="Vendor\Module\Model\Data"/>

    <!-- Plugins -->
    <type name="Magento\Catalog\Model\Product">
        <plugin name="vendor_module_product_plugin"
                type="Vendor\Module\Plugin\ProductPlugin"
                sortOrder="10"/>
    </type>

    <!-- Virtual Types -->
    <virtualType name="VendorModuleResourceModelCollection"
                 type="Magento\Framework\View\Element\UiComponent\DataProvider\SearchResult">
        <arguments>
            <argument name="mainTable" xsi:type="string">vendor_module_table</argument>
            <argument name="resourceModel" xsi:type="string">Vendor\Module\Model\ResourceModel\Entity</argument>
        </arguments>
    </virtualType>
</config>
```

### 3. **Database Schema** (etc/db_schema.xml)

```xml
<?xml version="1.0"?>
<schema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd">
    <table name="vendor_module_entity" resource="default" engine="innodb">
        <column xsi:type="int" name="entity_id" unsigned="true" nullable="false" identity="true"/>
        <column xsi:type="varchar" name="name" nullable="false" length="255"/>
        <column xsi:type="text" name="description" nullable="true"/>
        <column xsi:type="smallint" name="status" unsigned="true" nullable="false" default="1"/>
        <column xsi:type="timestamp" name="created_at" nullable="false" default="CURRENT_TIMESTAMP"/>
        <column xsi:type="timestamp" name="updated_at" nullable="false" default="CURRENT_TIMESTAMP"
                on_update="true"/>

        <constraint xsi:type="primary" referenceId="PRIMARY">
            <column name="entity_id"/>
        </constraint>

        <index referenceId="VENDOR_MODULE_ENTITY_NAME" indexType="btree">
            <column name="name"/>
        </index>
    </table>
</schema>
```

### 4. **ACL** (etc/acl.xml)

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Acl/etc/acl.xsd">
    <acl>
        <resources>
            <resource id="Magento_Backend::admin">
                <resource id="Vendor_Module::module" title="Module Name" sortOrder="100">
                    <resource id="Vendor_Module::manage" title="Manage" sortOrder="10"/>
                    <resource id="Vendor_Module::config" title="Configuration" sortOrder="20"/>
                </resource>
            </resource>
        </resources>
    </acl>
</config>
```

### 5. **Admin Routes** (etc/adminhtml/routes.xml)

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:App/etc/routes.xsd">
    <router id="admin">
        <route id="vendor_module" frontName="vendor_module">
            <module name="Vendor_Module"/>
        </route>
    </router>
</config>
```

### 6. **Frontend Routes** (etc/frontend/routes.xml)

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:App/etc/routes.xsd">
    <router id="standard">
        <route id="vendor_module" frontName="modulename">
            <module name="Vendor_Module"/>
        </route>
    </router>
</config>
```

### 7. **Module Directory Structure**

```
app/code/Vendor/Module/
├── Api/
│   ├── Data/
│   │   └── EntityInterface.php
│   └── EntityRepositoryInterface.php
├── Block/
│   ├── Adminhtml/
│   └── Frontend/
├── Controller/
│   ├── Adminhtml/
│   │   └── Entity/
│   │       ├── Index.php
│   │       ├── Edit.php
│   │       ├── Save.php
│   │       └── Delete.php
│   └── Index/
│       └── Index.php
├── etc/
│   ├── adminhtml/
│   │   ├── routes.xml
│   │   └── menu.xml
│   ├── frontend/
│   │   └── routes.xml
│   ├── acl.xml
│   ├── db_schema.xml
│   ├── di.xml
│   └── module.xml
├── Helper/
│   └── Data.php
├── Model/
│   ├── ResourceModel/
│   │   ├── Entity.php
│   │   └── Entity/
│   │       └── Collection.php
│   ├── Entity.php
│   └── EntityRepository.php
├── Plugin/
├── Observer/
├── Setup/
│   └── Patch/
│       ├── Data/
│       └── Schema/
├── Ui/
│   └── Component/
├── view/
│   ├── adminhtml/
│   │   ├── layout/
│   │   ├── templates/
│   │   └── ui_component/
│   └── frontend/
│       ├── layout/
│       ├── templates/
│       └── web/
│           ├── css/
│           └── js/
├── composer.json
└── registration.php
```

Generate a complete, production-ready Magento 2 module structure.
