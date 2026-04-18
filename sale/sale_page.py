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
from log.logging_config import get_logger
import shared.resource as resource
import shared.configuration as config

# ========== Initialize Logger ==========
logger = get_logger(__name__)


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
        logger.debug("ENTRY: SalePage.__init__()")
        
        try:
            super().__init__(parent, bg=self.BG_MAIN, **kwargs)
            
            # ========== Store References ==========
            # Keep reference to data processor for retrieving product data
            self.data_processor = data_processor
            logger.debug("Data processor reference stored")
            
            # ========== State Variables ==========
            # Track current page number for pagination
            self.current_page = 1
            # Store active filter criteria (category, vendor, search)
            self.current_filters = {}
            # Track asynchronous request IDs
            self.categories_request_id = None
            self.products_request_id = None
            self.filter_request_id = None
            logger.debug("State variables initialized")
            
            # ========== Build UI and Load Data ==========
            # Create the visual layout with filter, product, and order panels
            logger.debug("Creating layout...")
            self._create_layout()
            logger.debug("Layout created")
            
            # Load initial product data from processor
            logger.debug("Loading initial data...")
            self._load_initial_data()
            logger.debug("Initial data loaded")
            
            logger.debug("EXIT: SalePage.__init__() - Success")
            
        except Exception as e:
            logger.error(f"Failed to initialize SalePage: {str(e)}", exc_info=True)
            raise

    def _create_layout(self):
        """Create main layout with left and right sections"""
        logger.debug("ENTRY: SalePage._create_layout()")
        
        try:
            # ========== Main Container ==========
            # Create main frame that will hold all sections
            logger.debug("Creating main container...")
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
            logger.debug("Left section created with filter, products, and navigation panels")
            
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
            logger.debug("Right section created with order table and checkout panels")
            
            logger.debug("EXIT: SalePage._create_layout() - Success")
            
        except Exception as e:
            logger.error(f"Failed to create layout: {str(e)}", exc_info=True)
            raise

    def _load_initial_data(self):
        """Load initial data from data processor asynchronously"""
        logger.debug("ENTRY: SalePage._load_initial_data()")
        
        try:
            # Get reference to main app for sending requests
            root = self.winfo_toplevel()
            if hasattr(root, 'send_request_to_processor'):
                logger.debug("Sending requests for categories, vendors, and products to data processor...")
                
                # Request 1: Get categories and vendors
                self.categories_request_id = root.send_request_to_processor(
                    action='get_categories_vendors'
                )
                logger.debug(f"Sent categories/vendors request: {self.categories_request_id}")
                
                # Request 2: Get first page of products
                self.products_request_id = root.send_request_to_processor(
                    action='get_products_page',
                    request_data={'page': 1, 'items_per_page': config.items_per_page}
                )
                logger.debug(f"Sent products page request: {self.products_request_id}")
                
                # Schedule checking for responses (non-blocking)
                self.after(100, self._check_initial_data_responses, root)
            else:
                logger.warning("Main app not available, cannot send requests")
            
            logger.debug("EXIT: SalePage._load_initial_data()")
            
        except Exception as e:
            logger.error(f"Failed to load initial data: {str(e)}", exc_info=True)

    def _check_initial_data_responses(self, root):
        """Check if initial data responses are ready"""
        logger.debug("ENTRY: SalePage._check_initial_data_responses()")
        
        try:
            responses_received = 0
            
            # Check for categories/vendors response
            if hasattr(self, 'categories_request_id') and not hasattr(self, 'categories_loaded'):
                response = root.get_response(self.categories_request_id)
                if response:
                    logger.debug(f"Received categories/vendors response")
                    categories = response.get('categories', [])
                    vendors = response.get('vendors', [])
                    logger.debug(f"Updating filter dropdowns with {len(categories)} categories and {len(vendors)} vendors")
                    self.filter_panel.update_categories(categories)
                    self.filter_panel.update_vendors(vendors)
                    self.categories_loaded = True
                    responses_received += 1
            
            # Check for products page response
            if hasattr(self, 'products_request_id') and not hasattr(self, 'products_loaded'):
                response = root.get_response(self.products_request_id)
                if response:
                    logger.debug(f"Received products page response")
                    products_page = response.get('data', {})
                    products = products_page.get('products', [])
                    logger.debug(f"Displaying {len(products)} products")
                    self.products_panel.display_products(products)
                    
                    # Update pagination
                    logger.debug(f"Updating pagination: page {products_page.get('current_page')} of {products_page.get('total_pages')}")
                    self.navigation_panel.set_page_info(
                        products_page.get('current_page', 1),
                        products_page.get('total_pages', 1)
                    )
                    self.products_loaded = True
                    responses_received += 1
            
            if responses_received < 2:
                # Not all responses ready yet, check again soon
                logger.debug(f"Received {responses_received}/2 responses, checking again in 100ms")
                self.after(100, self._check_initial_data_responses, root)
            else:
                logger.debug("All initial data responses received")
            
            logger.debug("EXIT: SalePage._check_initial_data_responses()")
            
        except Exception as e:
            logger.error(f"Failed to check initial data responses: {str(e)}", exc_info=True)

    def _on_filter_change(self, filters):
        """Handle filter changes"""
        logger.debug(f"ENTRY: SalePage._on_filter_change(filters={filters})")
        
        try:
            if not hasattr(self, 'products_panel'):
                logger.warning("Products panel not yet initialized")
                return
            
            self.current_filters = filters
            logger.debug(f"Filters updated: {filters}")
            self.current_page = 1
            logger.debug("Reset to page 1")
            self._refresh_products()
            logger.debug("EXIT: SalePage._on_filter_change()")
            
        except Exception as e:
            logger.error(f"Failed to handle filter change: {str(e)}", exc_info=True)

    def _on_page_change(self, page_num):
        """Handle page change"""
        logger.debug(f"ENTRY: SalePage._on_page_change(page_num={page_num})")
        
        try:
            self.current_page = page_num
            logger.debug(f"Changed to page {page_num}")
            
            start_point = config.items_per_page * (page_num - 1)
            logger.debug(f"Calculating page slice: start={start_point}, end={start_point + config.items_per_page}")
            products = resource.products_details[start_point:start_point + config.items_per_page]
            logger.debug(f"Displaying {len(products)} products")
            self.products_panel.display_products(products)

            logger.debug("EXIT: SalePage._on_page_change()")
            
        except Exception as e:
            logger.error(f"Failed to handle page change: {str(e)}", exc_info=True)

    def _refresh_products(self):
        """Refresh products based on current filters and page - asynchronously"""
        logger.debug("ENTRY: SalePage._refresh_products()")
        
        try:

            


            #TODO Remove this
            '''
            # Get reference to main app for sending requests
            root = self.winfo_toplevel()
            if hasattr(root, 'send_request_to_processor'):
                logger.debug(f"Sending filter request with criteria: {self.current_filters}")
                
                # Send filter request to data processor
                self.filter_request_id = root.send_request_to_processor(
                    action='filter_products',
                    request_data={
                        'category': self.current_filters.get('category'),
                        'vendor': self.current_filters.get('vendor'),
                        'search': self.current_filters.get('search')
                    }
                )
                logger.debug(f"Sent filter request: {self.filter_request_id}")
                
                # Schedule checking for response
                self.after(50, self._check_filter_response, root)
            else:
                logger.warning("Main app not available, cannot send filter request")
            
            logger.debug("EXIT: SalePage._refresh_products()")
            '''
            
        except Exception as e:
            logger.error(f"Failed to refresh products: {str(e)}", exc_info=True)

    def _check_filter_response(self, root):
        """Check if filter response is ready and update display"""
        logger.debug("ENTRY: SalePage._check_filter_response()")
        
        try:
            if hasattr(self, 'filter_request_id'):
                response = root.get_response(self.filter_request_id)
                if response:
                    logger.debug(f"Received filter response")
                    filtered = response.get('data', [])
                    logger.debug(f"Filtered results: {len(filtered)} products")
                    
                    # Calculate pagination for filtered results
                    items_per_page = 20
                    total = len(filtered)
                    total_pages = (total + items_per_page - 1) // items_per_page
                    self.current_page = max(1, min(self.current_page, total_pages))
                    logger.debug(f"Pagination: page {self.current_page} of {total_pages}")
                    
                    # Get page slice
                    start_idx = (self.current_page - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    page_products = filtered[start_idx:end_idx]
                    logger.debug(f"Displaying {len(page_products)} products for page {self.current_page}")
                    
                    # Update display
                    self.products_panel.display_products(page_products)
                    self.navigation_panel.set_page_info(self.current_page, total_pages)
                else:
                    # Response not ready yet, check again
                    logger.debug("Filter response not ready yet, checking again in 50ms")
                    self.after(50, self._check_filter_response, root)
            
            logger.debug("EXIT: SalePage._check_filter_response()")
            
        except Exception as e:
            logger.error(f"Failed to check filter response: {str(e)}", exc_info=True)

    def _on_product_click(self, product):
        """Handle product card click - add to order"""
        product_id = product.id if hasattr(product, 'id') else product.get('id')
        product_name = product.name if hasattr(product, 'name') else product.get('name', 'Unknown')
        logger.debug(f"ENTRY: SalePage._on_product_click(product_id={product_id}, name={product_name})")
        
        try:
            logger.debug(f"Adding product to order: {product_name}")
            self.order_table.add_item(product)
            logger.debug("Product added successfully")
            self._update_order_totals()
            logger.debug("EXIT: SalePage._on_product_click()")
            
        except Exception as e:
            logger.error(f"Failed to handle product click: {str(e)}", exc_info=True)

    def _on_quantity_change(self, product_id, quantity, subtotal):
        """Handle quantity change"""
        logger.debug(f"ENTRY: SalePage._on_quantity_change(product_id={product_id}, quantity={quantity}, subtotal={subtotal})")
        
        try:
            logger.debug(f"Quantity changed for product {product_id} to {quantity}")
            self._update_order_totals()
            logger.debug("EXIT: SalePage._on_quantity_change()")
            
        except Exception as e:
            logger.error(f"Failed to handle quantity change: {str(e)}", exc_info=True)

    def _on_item_delete(self, product_id):
        """Handle item delete"""
        logger.debug(f"ENTRY: SalePage._on_item_delete(product_id={product_id})")
        
        try:
            logger.debug(f"Item deleted: {product_id}")
            self._update_order_totals()
            logger.debug("EXIT: SalePage._on_item_delete()")
            
        except Exception as e:
            logger.error(f"Failed to handle item delete: {str(e)}", exc_info=True)

    def _on_item_settings(self, product_id):
        """Handle settings button click"""
        logger.debug(f"ENTRY: SalePage._on_item_settings(product_id={product_id})")
        logger.debug(f"Settings clicked for item {product_id}")
        messageBox.showinfo("Settings", f"Settings for item {product_id}\n(Placeholder functionality)")
        logger.debug("EXIT: SalePage._on_item_settings()")

    def _update_order_totals(self):
        """Update totals in checkout panel"""
        logger.debug("ENTRY: SalePage._update_order_totals()")
        
        try:
            total = self.order_table.get_total_amount()
            logger.debug(f"Order total: ₹{total:.2f}")
            self.checkout_panel.update_totals(total, 0.0)
            logger.debug("EXIT: SalePage._update_order_totals()")
            
        except Exception as e:
            logger.error(f"Failed to update order totals: {str(e)}", exc_info=True)

    def _on_clear_order(self):
        """Handle clear order button"""
        logger.debug("ENTRY: SalePage._on_clear_order()")
        logger.warn("User initiated clear order")
        
        try:
            if messagebox.askyesno("Clear Order", "Clear all items from order?"):
                logger.info("Clearing order...")
                self.order_table.clear_all()
                self.checkout_panel.reset()
                logger.info("Order cleared successfully")
            else:
                logger.debug("Clear order cancelled by user")
            
            logger.debug("EXIT: SalePage._on_clear_order()")
            
        except Exception as e:
            logger.error(f"Failed to clear order: {str(e)}", exc_info=True)

    def _on_checkout(self):
        """Handle checkout button"""
        logger.debug("ENTRY: SalePage._on_checkout()")
        logger.info("Checkout initiated")
        
        try:
            transaction = self.checkout_panel.get_transaction_data()
            logger.debug(f"Transaction data: total={transaction.get('total_amount')}, received={transaction.get('amount_received')}")
            
            if transaction['total_amount'] == 0:
                logger.warning("Checkout attempted with empty order")
                messagebox.showwarning("Empty Order", "Please add items to checkout")
                return
            
            if transaction['amount_received'] < transaction['total_amount']:
                logger.warning(f"Insufficient payment: received ₹{transaction['amount_received']}, required ₹{transaction['total_amount']}")
                messagebox.showwarning("Insufficient Amount", "Amount received is less than total")
                return
            
            logger.info(f"Checkout successful! Total: ₹{transaction['total_amount']:.2f}, Change: ₹{transaction['change']:.2f}")
            messagebox.showinfo(
                "Checkout Complete",
                f"Order completed!\n\nTotal: ₹{transaction['total_amount']:.2f}\n"
                f"Received: ₹{transaction['amount_received']:.2f}\n"
                f"Change: ₹{transaction['change']:.2f}"
            )
            self.order_table.clear_all()
            self.checkout_panel.reset()
            logger.debug("EXIT: SalePage._on_checkout()")
            
        except Exception as e:
            logger.error(f"Failed during checkout: {str(e)}", exc_info=True)

    def _on_checkout_print(self):
        """Handle checkout & print button"""
        logger.debug("ENTRY: SalePage._on_checkout_print()")
        logger.info("Checkout with print initiated")
        
        try:
            transaction = self.checkout_panel.get_transaction_data()
            logger.debug(f"Transaction data for print: total={transaction.get('total_amount')}, received={transaction.get('amount_received')}")
            
            if transaction['total_amount'] == 0:
                logger.warning("Checkout & print attempted with empty order")
                messagebox.showwarning("Empty Order", "Please add items to checkout")
                return
            
            if transaction['amount_received'] < transaction['total_amount']:
                logger.warning(f"Insufficient payment for print checkout: received ₹{transaction['amount_received']}, required ₹{transaction['total_amount']}")
                messagebox.showwarning("Insufficient Amount", "Amount received is less than total")
                return
            
            logger.info(f"Checkout & print successful! Total: ₹{transaction['total_amount']:.2f}, Change: ₹{transaction['change']:.2f}")
            messagebox.showinfo(
                "Checkout & Print Complete",
                f"Order completed & printing!\n\nTotal: ₹{transaction['total_amount']:.2f}\n"
                f"Received: ₹{transaction['amount_received']:.2f}\n"
                f"Change: ₹{transaction['change']:.2f}"
            )
            self.order_table.clear_all()
            self.checkout_panel.reset()
            logger.debug("EXIT: SalePage._on_checkout_print()")
            
        except Exception as e:
            logger.error(f"Failed during checkout & print: {str(e)}", exc_info=True)
            "Checkout & Print",
            f"Order completed and sent to printer!\n\n"
            f"Total: ₹{transaction['total_amount']:.2f}\n"
            f"Received: ₹{transaction['amount_received']:.2f}\n"
            f"Change: ₹{transaction['change']:.2f}"
        
        self.order_table.clear_all()
        self.checkout_panel.reset()
