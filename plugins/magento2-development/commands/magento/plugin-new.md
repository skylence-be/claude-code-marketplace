---
description: Create Magento 2 Plugin/Interceptor
model: claude-sonnet-4-5
---

Create a Magento 2 Plugin (Interceptor).

## Plugin Specification

$ARGUMENTS

## Magento 2 Plugin Patterns

### 1. **Before Plugin**

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    /**
     * Before plugin - modify arguments before method execution
     */
    public function beforeSetName(
        \Magento\Catalog\Model\Product $subject,
        $name
    ) {
        // Modify the name before it's set
        $modifiedName = strtoupper($name);
        return [$modifiedName];
    }
}
```

### 2. **After Plugin**

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    /**
     * After plugin - modify return value after method execution
     */
    public function afterGetName(
        \Magento\Catalog\Model\Product $subject,
        $result
    ) {
        // Modify the returned name
        return $result . ' - Custom Suffix';
    }
}
```

### 3. **Around Plugin**

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    /**
     * Around plugin - wrap the original method
     */
    public function aroundGetPrice(
        \Magento\Catalog\Model\Product $subject,
        \Closure $proceed
    ) {
        // Code before original method
        $result = $proceed(); // Call original method

        // Code after original method
        return $result * 1.1; // Add 10% markup
    }
}
```

### 4. **Configuration** (etc/di.xml)

```xml
<type name="Magento\Catalog\Model\Product">
    <plugin name="vendor_module_product_plugin"
            type="Vendor\Module\Plugin\ProductPlugin"
            sortOrder="10"
            disabled="false"/>
</type>
```

Generate a complete Magento 2 plugin with proper configuration.
