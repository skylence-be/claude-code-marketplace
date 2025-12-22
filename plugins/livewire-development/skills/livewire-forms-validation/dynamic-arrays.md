# Dynamic Arrays

Livewire 4 repeater fields and nested array validation.

## Basic Repeater Pattern

```php
<?php

namespace App\Livewire;

use Livewire\Component;

class DynamicInvoice extends Component
{
    public $invoiceNumber = '';
    public $customerName = '';
    public $items = [];
    public $taxRate = 10;

    public function mount()
    {
        $this->addItem();
        $this->invoiceNumber = 'INV-' . strtoupper(uniqid());
    }

    /**
     * Validation rules for items array.
     */
    protected function rules()
    {
        return [
            'customerName' => 'required|string|min:3',
            'items' => 'required|array|min:1',
            'items.*.description' => 'required|string|min:3',
            'items.*.quantity' => 'required|numeric|min:1',
            'items.*.price' => 'required|numeric|min:0',
            'taxRate' => 'required|numeric|min:0|max:100',
        ];
    }

    protected function messages()
    {
        return [
            'items.*.description.required' => 'Description is required',
            'items.*.quantity.min' => 'Quantity must be at least 1',
            'items.*.price.min' => 'Price must be positive',
        ];
    }

    public function addItem()
    {
        $this->items[] = [
            'description' => '',
            'quantity' => 1,
            'price' => 0,
        ];
    }

    public function removeItem($index)
    {
        unset($this->items[$index]);
        $this->items = array_values($this->items);
    }

    public function duplicateItem($index)
    {
        $this->items[] = $this->items[$index];
    }

    public function getLineTotal($index)
    {
        $item = $this->items[$index] ?? null;
        if (!$item) return 0;
        return ($item['quantity'] ?? 0) * ($item['price'] ?? 0);
    }

    public function getSubtotal()
    {
        return collect($this->items)->sum(function ($item, $index) {
            return $this->getLineTotal($index);
        });
    }

    public function getTotal()
    {
        $subtotal = $this->getSubtotal();
        return $subtotal + ($subtotal * $this->taxRate / 100);
    }

    /**
     * Validate specific item field.
     */
    public function updatedItems($value, $key)
    {
        $this->validateOnly("items.{$key}");
    }

    public function save()
    {
        $this->validate();

        $invoice = \App\Models\Invoice::create([
            'invoice_number' => $this->invoiceNumber,
            'customer_name' => $this->customerName,
            'subtotal' => $this->getSubtotal(),
            'tax_rate' => $this->taxRate,
            'total' => $this->getTotal(),
        ]);

        foreach ($this->items as $item) {
            $invoice->items()->create($item);
        }

        return redirect()->route('invoices.show', $invoice);
    }

    public function render()
    {
        return view('livewire.dynamic-invoice', [
            'subtotal' => $this->getSubtotal(),
            'total' => $this->getTotal(),
        ]);
    }
}
```

## Repeater View

```blade
<div>
    <form wire:submit="save">
        <div class="form-group">
            <label>Customer Name</label>
            <input type="text" wire:model.blur="customerName">
            @error('customerName') <span class="error">{{ $message }}</span> @enderror
        </div>

        <h3>Line Items</h3>

        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                @foreach($items as $index => $item)
                    <tr wire:key="item-{{ $index }}">
                        <td>
                            <input
                                type="text"
                                wire:model.blur="items.{{ $index }}.description"
                                placeholder="Description"
                            >
                            @error("items.{$index}.description")
                                <span class="error">{{ $message }}</span>
                            @enderror
                        </td>
                        <td>
                            <input
                                type="number"
                                wire:model.blur="items.{{ $index }}.quantity"
                                min="1"
                            >
                            @error("items.{$index}.quantity")
                                <span class="error">{{ $message }}</span>
                            @enderror
                        </td>
                        <td>
                            <input
                                type="number"
                                wire:model.blur="items.{{ $index }}.price"
                                step="0.01"
                            >
                            @error("items.{$index}.price")
                                <span class="error">{{ $message }}</span>
                            @enderror
                        </td>
                        <td>
                            ${{ number_format($this->getLineTotal($index), 2) }}
                        </td>
                        <td>
                            <button type="button" wire:click="duplicateItem({{ $index }})">
                                Copy
                            </button>
                            <button
                                type="button"
                                wire:click="removeItem({{ $index }})"
                                @if(count($items) === 1) disabled @endif
                            >
                                Remove
                            </button>
                        </td>
                    </tr>
                @endforeach
            </tbody>
        </table>

        <button type="button" wire:click="addItem">+ Add Item</button>

        @error('items')
            <span class="error">{{ $message }}</span>
        @enderror

        <div class="totals">
            <div>Subtotal: ${{ number_format($subtotal, 2) }}</div>
            <div>
                Tax:
                <input type="number" wire:model.blur="taxRate" min="0" max="100">%
            </div>
            <div><strong>Total: ${{ number_format($total, 2) }}</strong></div>
        </div>

        <button type="submit">Save Invoice</button>
    </form>
</div>
```

## Nested Arrays

```php
class NestedArrayForm extends Component
{
    public $sections = [];

    public function mount()
    {
        $this->addSection();
    }

    protected function rules()
    {
        return [
            'sections' => 'required|array|min:1',
            'sections.*.title' => 'required|string',
            'sections.*.items' => 'required|array|min:1',
            'sections.*.items.*.name' => 'required|string',
            'sections.*.items.*.value' => 'required|numeric',
        ];
    }

    public function addSection()
    {
        $this->sections[] = [
            'title' => '',
            'items' => [
                ['name' => '', 'value' => 0],
            ],
        ];
    }

    public function removeSection($index)
    {
        unset($this->sections[$index]);
        $this->sections = array_values($this->sections);
    }

    public function addItem($sectionIndex)
    {
        $this->sections[$sectionIndex]['items'][] = [
            'name' => '',
            'value' => 0,
        ];
    }

    public function removeItem($sectionIndex, $itemIndex)
    {
        unset($this->sections[$sectionIndex]['items'][$itemIndex]);
        $this->sections[$sectionIndex]['items'] = array_values(
            $this->sections[$sectionIndex]['items']
        );
    }
}
```

```blade
@foreach($sections as $sectionIndex => $section)
    <div wire:key="section-{{ $sectionIndex }}">
        <input wire:model.blur="sections.{{ $sectionIndex }}.title">
        @error("sections.{$sectionIndex}.title")
            <span class="error">{{ $message }}</span>
        @enderror

        @foreach($section['items'] as $itemIndex => $item)
            <div wire:key="section-{{ $sectionIndex }}-item-{{ $itemIndex }}">
                <input wire:model.blur="sections.{{ $sectionIndex }}.items.{{ $itemIndex }}.name">
                @error("sections.{$sectionIndex}.items.{$itemIndex}.name")
                    <span class="error">{{ $message }}</span>
                @enderror

                <button wire:click="removeItem({{ $sectionIndex }}, {{ $itemIndex }})">
                    Remove Item
                </button>
            </div>
        @endforeach

        <button wire:click="addItem({{ $sectionIndex }})">Add Item</button>
        <button wire:click="removeSection({{ $sectionIndex }})">Remove Section</button>
    </div>
@endforeach

<button wire:click="addSection">Add Section</button>
```

## Sortable Items

```php
class SortableItems extends Component
{
    public $items = [];

    public function mount()
    {
        $this->items = [
            ['id' => 1, 'name' => 'First', 'order' => 0],
            ['id' => 2, 'name' => 'Second', 'order' => 1],
            ['id' => 3, 'name' => 'Third', 'order' => 2],
        ];
    }

    public function reorder($orderedIds)
    {
        $this->items = collect($orderedIds)
            ->map(function ($id, $index) {
                $item = collect($this->items)->firstWhere('id', $id);
                $item['order'] = $index;
                return $item;
            })
            ->sortBy('order')
            ->values()
            ->toArray();
    }

    public function moveUp($index)
    {
        if ($index > 0) {
            $temp = $this->items[$index];
            $this->items[$index] = $this->items[$index - 1];
            $this->items[$index - 1] = $temp;
        }
    }

    public function moveDown($index)
    {
        if ($index < count($this->items) - 1) {
            $temp = $this->items[$index];
            $this->items[$index] = $this->items[$index + 1];
            $this->items[$index + 1] = $temp;
        }
    }
}
```

```blade
<div
    x-data
    x-init="Sortable.create($el, {
        onEnd: (evt) => {
            let orderedIds = Array.from($el.children).map(el => el.dataset.id);
            $wire.reorder(orderedIds);
        }
    })"
>
    @foreach($items as $index => $item)
        <div
            wire:key="item-{{ $item['id'] }}"
            data-id="{{ $item['id'] }}"
            class="sortable-item"
        >
            {{ $item['name'] }}
            <button wire:click="moveUp({{ $index }})">↑</button>
            <button wire:click="moveDown({{ $index }})">↓</button>
        </div>
    @endforeach
</div>
```

## Best Practices

```php
class ArrayBestPractices extends Component
{
    public $items = [];

    // 1. Always use wire:key for list items
    // 2. Re-index arrays after removal
    public function removeItem($index)
    {
        unset($this->items[$index]);
        $this->items = array_values($this->items);
    }

    // 3. Validate individual fields on update
    public function updatedItems($value, $key)
    {
        $this->validateOnly("items.{$key}");
    }

    // 4. Handle empty arrays gracefully
    protected function rules()
    {
        return [
            'items' => 'required|array|min:1',
            'items.*' => 'required|string',
        ];
    }

    // 5. Initialize with at least one item
    public function mount()
    {
        if (empty($this->items)) {
            $this->addItem();
        }
    }
}
```
