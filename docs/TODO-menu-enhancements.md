# Menu Enhancements TODO

## Tasks

- [ ] **Show ₹ symbol instead of "INR" in menu item list**
  Replace `INR 120.00` with `₹120.00` in the item row price display using a currency symbol mapping.

- [ ] **Add rupee prefix icon to price field in Add Item dialog**
  Add a `₹` prefix to the price input field in the MenuItemDialog component.

- [ ] **Add missing fields to Add Menu Item dialog**
  Backend supports `dietary_labels`, `image_url`, `preparation_time_minutes` but the dialog only has name, description, price, currency, and availability. Add the missing fields.

- [ ] **Add drag-and-drop reorder for menu items**
  Add CDK DragDrop to item rows within each category to allow reordering. Update `display_order` on the backend via the `updateItem` API after reorder.
