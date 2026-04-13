"""
Sale Page - Full-screen sales interface with product grid, filters, and checkout.
"""

import tkinter as tk
from tkinter import messagebox
from sale.filters import FilterPanel
from sale.products import ProductsPanel
from sale.navigation import NavigationPanel
from sale.table import OrderTablePanel
from sale.checkout import CheckoutPanel


class SalePage(tk.Frame):
    """Sale page with full layout"""

    # UI Constants
    FONT_NORMAL = ("Segoe UI", 11, "normal")
    
    # Colors
    BG_MAIN = "#EEF2F6"
    BG_PANEL = "#FFFFFF"
    BORDER_COLOR = "#E5E7EB"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"

    def __init__(self, parent, data_processor=None, **kwargs):
        """
        Initialize SalePage.
        
        Args:
            parent: Parent widget
            data_processor: DataProcessor instance for getting data
        """
        super().__init__(parent, bg=self.BG_MAIN, **kwargs)
        
        # ========== Store References ==========
        # Keep reference to data processor for retrieving product data
        self.data_processor = data_processor
        
        # ========== State Variables ==========
        # Track current page number for pagination
        self.current_page = 1
        # Store active filter criteria (category, vendor, search)
        self.current_filters = {}
        
        # ========== Build UI and Load Data ==========
        # Create the visual layout with filter, product, and order panels
        self._create_layout()
        # Load initial product data from processor
        self._load_initial_data()

    def _create_layout(self):
        """Create main layout with left and right sections"""
        # ========== Main Container ==========
        # Create main frame that will hold all sections
        main_container = tk.Frame(self, bg=self.BG_MAIN)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ========== Configure Responsive Grid Layout ==========
        # Set column weights: left (60%) and right (40%) sections
        main_container.columnconfigure(0, weight=6)  # Left section (60%)
        main_container.columnconfigure(1, weight=4)  # Right section (40%)
        main_container.rowconfigure(0, weight=1)  # Allow vertical expansion
        
        # ========== LEFT SECTION (60%) - PRODUCT BROWSING ==========
        left_section = tk.Frame(main_container, bg=self.BG_MAIN)
        left_section.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        
        # Configure left section grid: 3 rows with different heights
        left_section.rowconfigure(0, weight=0)  # Filters - fixed height
        left_section.rowconfigure(1, weight=1)  # Products - expandable
        left_section.rowconfigure(2, weight=0)  # Navigation - fixed height
        left_section.columnconfigure(0, weight=1)  # Allow horizontal expansion
        
        # ========== Left Top: Filter Panel ==========
        # Panel for filtering products by category, vendor, and search term
        self.filter_panel = FilterPanel(
            left_section,
            on_filter_change=self._on_filter_change,  # Callback when filters change
            bg=self.BG_PANEL
        )
        self.filter_panel.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        
        # ========== Left Middle: Products Grid ==========
        # Container for product cards that can scroll
        products_container = tk.Frame(left_section, bg=self.BG_MAIN)
        products_container.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        products_container.columnconfigure(0, weight=1)
        products_container.rowconfigure(0, weight=1)
        
        # Product grid panel displaying product cards
        self.products_panel = ProductsPanel(
            products_container,
            on_product_click=self._on_product_click,  # Callback when product is clicked
            bg=self.BG_MAIN
        )
        self.products_panel.grid(row=0, column=0, sticky="nsew")
        
        # ========== Left Bottom: Pagination Controls ==========
        # Panel with buttons to navigate between product pages
        self.navigation_panel = NavigationPanel(
            left_section,
            on_page_change=self._on_page_change,  # Callback when page changes
            bg=self.BG_PANEL
        )
        self.navigation_panel.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        
        # ========== RIGHT SECTION (40%) - ORDER SUMMARY ==========
        right_section = tk.Frame(main_container, bg=self.BG_MAIN)
        right_section.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        
        # Configure right section grid: 2 rows with different heights
        right_section.rowconfigure(0, weight=1)  # Table - expandable
        right_section.rowconfigure(1, weight=0)  # Checkout - fixed height
        right_section.columnconfigure(0, weight=1)  # Allow horizontal expansion
        
        # Right Top: Order Table
        table_container = tk.Frame(right_section, bg=self.BG_MAIN)
        table_container.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        self.order_table = OrderTablePanel(
            table_container,
            on_quantity_change=self._on_quantity_change,
            on_delete=self._on_item_delete,
            on_settings=self._on_item_settings,
            bg=self.BG_PANEL
        )
        self.order_table.grid(row=0, column=0, sticky="nsew")
        
        # Right Bottom: Checkout
        self.checkout_panel = CheckoutPanel(
            right_section,
            on_clear=self._on_clear_order,
            on_checkout=self._on_checkout,
            on_checkout_print=self._on_checkout_print,
            bg=self.BG_PANEL
        )
        self.checkout_panel.grid(row=1, column=0, sticky="ew", pady=(6, 12))

    def _load_initial_data(self):
        """Load initial data from data processor"""
        if self.data_processor:
            products_page = self.data_processor.get_products_page(1)
            
            # Update filter dropdowns
            self.filter_panel.update_categories(self.data_processor.categories)
            self.filter_panel.update_vendors(self.data_processor.vendors)
            
            # Display products
            self.products_panel.display_products(products_page['products'])
            
            # Update pagination
            self.navigation_panel.set_page_info(
                products_page['current_page'],
                products_page['total_pages']
            )

    def _on_filter_change(self, filters):
        """Handle filter changes"""
        if not hasattr(self, 'products_panel'):
            return
        self.current_filters = filters
        self.current_page = 1
        self._refresh_products()

    def _on_page_change(self, page_num):
        """Handle page change"""
        self.current_page = page_num
        self._refresh_products()

    def _refresh_products(self):
        """Refresh products based on current filters and page"""
        if not self.data_processor:
            return
        
        # Filter products
        filtered = self.data_processor.filter_products(
            category=self.current_filters.get('category'),
            vendor=self.current_filters.get('vendor'),
            search=self.current_filters.get('search')
        )
        
        # Calculate pagination for filtered results
        items_per_page = 20
        total = len(filtered)
        total_pages = (total + items_per_page - 1) // items_per_page
        self.current_page = max(1, min(self.current_page, total_pages))
        
        # Get page slice
        start_idx = (self.current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_products = filtered[start_idx:end_idx]
        
        # Update display
        self.products_panel.display_products(page_products)
        self.navigation_panel.set_page_info(self.current_page, total_pages)

    def _on_product_click(self, product):
        """Handle product card click - add to order"""
        self.order_table.add_item(product)
        self._update_order_totals()

    def _on_quantity_change(self, product_id, quantity, subtotal):
        """Handle quantity change"""
        self._update_order_totals()

    def _on_item_delete(self, product_id):
        """Handle item delete"""
        self._update_order_totals()

    def _on_item_settings(self, product_id):
        """Handle settings button click"""
        messagebox.showinfo("Settings", f"Settings for item {product_id}\n(Placeholder functionality)")

    def _update_order_totals(self):
        """Update totals in checkout panel"""
        total = self.order_table.get_total_amount()
        self.checkout_panel.update_totals(total, 0.0)

    def _on_clear_order(self):
        """Handle clear order button"""
        if messagebox.askyesno("Clear Order", "Clear all items from order?"):
            self.order_table.clear_all()
            self.checkout_panel.reset()

    def _on_checkout(self):
        """Handle checkout button"""
        transaction = self.checkout_panel.get_transaction_data()
        if transaction['total_amount'] == 0:
            messagebox.showwarning("Empty Order", "Please add items to checkout")
            return
        
        if transaction['amount_received'] < transaction['total_amount']:
            messagebox.showwarning("Insufficient Amount", "Amount received is less than total")
            return
        
        messagebox.showinfo(
            "Checkout Complete",
            f"Order completed!\n\nTotal: ₹{transaction['total_amount']:.2f}\n"
            f"Received: ₹{transaction['amount_received']:.2f}\n"
            f"Change: ₹{transaction['change']:.2f}"
        )
        self.order_table.clear_all()
        self.checkout_panel.reset()

    def _on_checkout_print(self):
        """Handle checkout & print button"""
        transaction = self.checkout_panel.get_transaction_data()
        if transaction['total_amount'] == 0:
            messagebox.showwarning("Empty Order", "Please add items to checkout")
            return
        
        if transaction['amount_received'] < transaction['total_amount']:
            messagebox.showwarning("Insufficient Amount", "Amount received is less than total")
            return
        
        messagebox.showinfo(
            "Checkout & Print",
            f"Order completed and sent to printer!\n\n"
            f"Total: ₹{transaction['total_amount']:.2f}\n"
            f"Received: ₹{transaction['amount_received']:.2f}\n"
            f"Change: ₹{transaction['change']:.2f}"
        )
        self.order_table.clear_all()
        self.checkout_panel.reset()
