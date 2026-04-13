# POS Desktop Application - Project Structure

## Overview
A full-screen Point of Sale (POS) desktop application built with Python Tkinter. The application features a clean, minimalistic UI with real-time order management, product display, and checkout functionality.

## Project Structure

```
python_learn/
├── main.py                    # Main entry point (GUI thread, menu bar, router)
├── data_processor.py          # Data processing thread with dummy data
└── sale/
    ├── __init__.py
    ├── filters.py             # Top-left panel (category/vendor filters + search)
    ├── products.py            # Middle-left panel (product grid with item cards)
    ├── navigation.py          # Bottom-left panel (pagination controls)
    ├── table.py               # Top-right panel (order table with Treeview)
    └── checkout.py            # Bottom-right panel (summary & checkout buttons)
```

## Files & Responsibilities

### 1. **main.py** - Application Root
   - `MainApp` class: Root window management
     - Full-screen window (maximized, non-resizable)
     - Top menu bar with page switching (Sale, Inventory, Reports, Settings)
     - Page container for swapping content
   - `SalePage` class: Sale page layout
     - 60/40 split (left/right sections)
     - Integrates all sub-panels
     - Handles callbacks and data flow
   - Data processor integration via queue

### 2. **data_processor.py** - Background Thread
   - `Product` dataclass: Product structure with id, name, price, category, vendor, stock
   - `DataProcessor` class (extends Thread):
     - Dummy product database (15 sample items)
     - Filtering by category, vendor, and search term
     - Pagination support
     - Sends data to GUI via queue

### 3. **sale/filters.py** - Top-Left Panel
   - `FilterPanel` class:
     - Category dropdown (filters + load dynamically)
     - Vendor dropdown (filters + load dynamically)
     - 3 placeholder buttons for custom actions
     - Search bar with placeholder text
     - Callbacks trigger product refresh on change

### 4. **sale/products.py** - Middle-Left Panel
   - `ItemCard` class: Reusable product card component
     - Displays item name, price, and stock
     - Hover effect (background color change)
     - Click callback integration
     - Grid layout (4 columns × 3 rows = 12 items per page)
   - `ProductsPanel` class:
     - Displays products in configurable grid
     - Empty state message
     - Dynamic card creation/destruction

### 5. **sale/navigation.py** - Bottom-Left Panel
   - `NavigationPanel` class:
     - First, Previous, page numbers, Next, Last buttons
     - Current page highlighting (blue background)
     - Disabled state for boundary pages
     - Page info display (e.g., "Page 1 of 5")

### 6. **sale/table.py** - Top-Right Panel (Order Table)
   - `OrderTablePanel` class (ttk.Treeview):
     - Columns: Item Name, Unit Price, Quantity, Subtotal, Actions
     - Row emojis: ⚙️ (Settings), 🗑 (Delete)
     - Add item → Auto-increment quantity if exists
     - Update quantity → Auto-recalculate subtotal
     - Delete item → Remove from table & update totals
     - Settings button → Popup (placeholder)

### 7. **sale/checkout.py** - Bottom-Right Panel
   - `CheckoutPanel` class:
     - Row 1: Discount display, Total amount display
     - Row 2: Amount received input, Change calculation
     - Row 3: Clear, Checkout, Checkout & Print buttons
     - Auto-calculate change on input change
     - Transaction data getter for order completion

## Color Theme

- **Main background**: #EEF2F6 (light gray-blue)
- **Panel background**: #FFFFFF (white)
- **Border color**: #E5E7EB (light gray)
- **Primary blue**: #3B82F6 (action color)
- **Green (checkout)**: #22C55E
- **Red (delete)**: #EF4444
- **Text primary**: #111827 (dark gray)
- **Text secondary**: #6B7280 (medium gray)

## Key Features

### Layout
- ✅ Full-screen window (maximized)
- ✅ Non-resizable, but minimizable
- ✅ Grid-based layout (no absolute positioning)
- ✅ 60/40 split between left and right sections
- ✅ Responsive frame management with pack() and grid()

### Functionality
- ✅ Product grid with 4-column layout
- ✅ Category/Vendor filtering
- ✅ Search functionality
- ✅ Pagination (First, Previous, Page numbers, Next, Last)
- ✅ Add items to order (auto-increment qty)
- ✅ Delete items from order
- ✅ Auto-update totals on quantity change
- ✅ Manual amount received input
- ✅ Auto-calculate change
- ✅ Clear order button
- ✅ Checkout and Checkout & Print buttons

### Architecture
- ✅ Modular class-based design
- ✅ Separate concerns (filters, products, table, checkout)
- ✅ Thread-based data processor
- ✅ Queue communication between threads
- ✅ Consistent font family (Segoe UI → Arial fallback)
- ✅ Callback-driven event handling

## Running the Application

```bash
cd c:\Users\pc\Documents\python_learn
python main.py
```

## Font Specifications
- **Titles**: Segoe UI, 14pt
- **Normal text**: Segoe UI, 11-12pt
- **Buttons**: Segoe UI, 12pt
- **Labels**: Segoe UI, 10-11pt
- **Fallback**: Arial

## Dummy Data
The `DataProcessor` includes 15 sample products across 5 categories:
- Beverages, Coffee, Tea, Snacks, Bakery, Dairy, Oils, Condiments, Grains

Each product has: id, name, price, category, vendor, stock

## Threading Model
- **GUI Thread**: Tkinter main loop (responsive UI)
- **Data Thread**: Background processor (non-blocking data operations)
- **Queue Communication**: Safe data exchange between threads

## UI Behavior Notes
1. **Product Cards**: Click to add to order (auto-increments qty if exists)
2. **Filters**: Change category/vendor/search to refresh products
3. **Pagination**: Navigate product pages; updates on filter change
4. **Order Table**: Rows show item details; settings/delete on row click
5. **Checkout**: Amount input auto-calculates change
6. **Menu Bar**: Click to switch pages (placeholder pages for other menus)

## Extensibility Points
- Add more products to `DataProcessor.products` list
- Create new page classes for Inventory, Reports, Settings
- Add database connection to `data_processor.py`
- Implement receipt printing in checkout callback
- Add discount input fields
- Add payment method selection
- Integrate with payment gateways

---

**Status**: Fully functional demo with dummy data. Ready for backend integration.
