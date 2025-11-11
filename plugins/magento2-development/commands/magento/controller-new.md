---
description: Create Magento 2 controller (admin or frontend)
model: claude-sonnet-4-5
---

Create a Magento 2 controller.

## Controller Specification

$ARGUMENTS

## Magento 2 Controller Patterns

### 1. **Admin Controller**

```php
<?php
namespace Vendor\Module\Controller\Adminhtml\Entity;

use Magento\Backend\App\Action;
use Magento\Backend\App\Action\Context;
use Magento\Framework\View\Result\PageFactory;

class Index extends Action
{
    const ADMIN_RESOURCE = 'Vendor_Module::entity';

    protected $resultPageFactory;

    public function __construct(
        Context $context,
        PageFactory $resultPageFactory
    ) {
        parent::__construct($context);
        $this->resultPageFactory = $resultPageFactory;
    }

    public function execute()
    {
        $resultPage = $this->resultPageFactory->create();
        $resultPage->setActiveMenu('Vendor_Module::entity');
        $resultPage->getConfig()->getTitle()->prepend(__('Manage Entities'));

        return $resultPage;
    }
}
```

### 2. **Frontend Controller**

```php
<?php
namespace Vendor\Module\Controller\Index;

use Magento\Framework\App\Action\Action;
use Magento\Framework\App\Action\Context;
use Magento\Framework\View\Result\PageFactory;

class Index extends Action
{
    protected $resultPageFactory;

    public function __construct(
        Context $context,
        PageFactory $resultPageFactory
    ) {
        parent::__construct($context);
        $this->resultPageFactory = $resultPageFactory;
    }

    public function execute()
    {
        return $this->resultPageFactory->create();
    }
}
```

### 3. **JSON Controller**

```php
<?php
namespace Vendor\Module\Controller\Ajax;

use Magento\Framework\App\Action\Action;
use Magento\Framework\App\Action\HttpPostActionInterface;
use Magento\Framework\Controller\Result\JsonFactory;

class Save extends Action implements HttpPostActionInterface
{
    protected $jsonFactory;

    public function execute()
    {
        $result = $this->jsonFactory->create();

        try {
            // Process data
            $data = $this->getRequest()->getParams();

            return $result->setData([
                'success' => true,
                'message' => __('Success')
            ]);
        } catch (\Exception $e) {
            return $result->setData([
                'success' => false,
                'message' => $e->getMessage()
            ]);
        }
    }
}
```

Generate complete Magento 2 controller with proper structure and validation.
