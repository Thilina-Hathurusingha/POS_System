"""
Order Table Panel - Top right section displaying order items in a Treeview.
"""

import tkinter as tk
from tkinter import ttk
from logging_config import get_logger

logger = get_logger(__name__)


class OrderTablePanel(tk.Frame):
    """Panel for displaying order items in a table"""

    # UI Constants
    FONT_HEADER = ("Segoe UI", 15, "bold")
    FONT_NORMAL = ("Segoe UI", 14, "normal")
    
    # Colors
    BG_PANEL = "#FFFFFF"
    BG_MAIN = "#EEF2F6"
    BORDER_COLOR = "#E5E7EB"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    RED_DELETE = "#EF4444"
    PRIMARY_BLUE = "#3B82F6"

    def __init__(self, parent, on_quantity_change=None, on_delete=None, on_settings=None, **kwargs):
        """
        Initialize OrderTablePanel.
        
        Args:
            parent: Parent widget
            on_quantity_change: Callback when quantity changes
            on_delete: Callback when delete button clicked
            on_settings: Callback when settings button clicked
        """
        logger.debug("ENTRY: OrderTablePanel.__init__()")
        
        if 'bg' not in kwargs:
            kwargs['bg'] = self.BG_PANEL
        super().__init__(parent, **kwargs)
        
        try:
            # ========== Store Callback Functions ==========
            # These callbacks are triggered for various order management operations
            self.on_quantity_change = on_quantity_change  # Called when item quantity changes
            self.on_delete = on_delete  # Called when user deletes an item
            self.on_settings = on_settings  # Called for item settings/options
            
            # ========== Order Items Storage ==========
            # Dictionary mapping product_id to {product, quantity, row_id}
            # Helps quick lookup and updates of items in the order
            self.items = {}
            # Dictionary mapping product_id to StringVar for quantity input
            self.quantity_vars = {}
            
            # ========== Create UI Components ==========
            # Build the table display with columns and styling
            self._create_ui()
            logger.debug("EXIT: OrderTablePanel.__init__() - Success")
            
        except Exception as e:
            logger.error(f"Failed to initialize OrderTablePanel: {str(e)}", exc_info=True)
            raise

    def _create_ui(self):
        """Create table UI"""
        # Header
        header = tk.Label(
            self,
            text="Order Items",
            font=self.FONT_HEADER,
            bg=self.BG_PANEL,
            fg=self.TEXT_PRIMARY,
            anchor=tk.W
        )
        header.pack(fill=tk.X, padx=12, pady=(12, 8))
        
        # Table container with scrollbar
        table_container = tk.Frame(self, bg=self.BG_PANEL)
        table_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        # Create Treeview
        columns = ("Item Name", "Unit Price", "Quantity", "Subtotal", "Actions")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            height=16,
            show="headings",
            selectmode="none"
        )
        
        # Define column headings and widths
        column_config = [
            ("Item Name", 150),
            ("Unit Price", 90),
            ("Quantity", 80),
            ("Subtotal", 100),
            ("Actions", 100)
        ]
        
        for col, width in column_config:
            self.tree.column(col, width=width, anchor="center")
            self.tree.heading(col, text=col)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Treeview',
            font=self.FONT_NORMAL,
            background=self.BG_PANEL,
            foreground=self.TEXT_PRIMARY,
            fieldbackground=self.BG_PANEL,
            bordercolor=self.BORDER_COLOR,
            borderwidth=1,
            rowheight=40
        )
        style.configure(
            'Treeview.Heading',
            font=self.FONT_HEADER,
            background=self.BG_MAIN,
            foreground=self.TEXT_PRIMARY,
            borderwidth=1,
            rowheight=40
        )
        style.map('Treeview',
                  background=[('selected', '#F3F4F6')],
                  foreground=[('selected', self.TEXT_PRIMARY)])
        
        # Add row separators with tags
        self.tree.tag_configure('oddrow', background=self.BG_PANEL)
        self.tree.tag_configure('evenrow', background='#F9FAFB')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_item(self, product):
        """
        Add item to order table.
        
        Args:
            product: Product object (with id, name, price)
        """
        # ========== Extract Product ID ==========
        # Support both object attributes and dict keys
        product_id = product.id if hasattr(product, 'id') else product.get('id')
        
        # ========== Check if Item Already Exists ==========
        if product_id in self.items:
            # If product is already in order, just increase the quantity
            quantity = self.items[product_id]['quantity'] + 1
            self.update_quantity(product_id, quantity)
        else:
            # ========== New Item Being Added ==========
            # Extract product details (handle both objects and dicts)
            product_name = product.name if hasattr(product, 'name') else product.get('name', '')
            product_price = product.price if hasattr(product, 'price') else product.get('price', 0)
            
            # Start with quantity of 1
            quantity = 1
            subtotal = quantity * product_price  # Calculate line total
            
            # ========== Determine Row Color (Alternating) ==========
            # Use different background colors for alternating rows for readability
            row_count = len(self.items) + 1
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            
            # ========== Add Row to Treeview ==========
            # Insert new row with product details formatted for display
            row_id = self.tree.insert("", "end", values=(
                product_name,  # Product name
                f"₹{product_price:.2f}",  # Unit price in rupees
                quantity,  # Current quantity (1)
                f"₹{subtotal:.2f}",  # Subtotal (price * qty)
                "⚙️ 🗑"  # Settings and delete icons
            ), tags=(tag,))  # Apply alternating row color
            
            # ========== Store Item Metadata ==========
            # Keep track of this item for future updates
            self.items[product_id] = {
                'product': product,  # Reference to product data
                'quantity': quantity,  # Current quantity
                'row_id': row_id  # Treeview row identifier
            }
            
            # ========== Create Quantity Variable ==========
            # Create StringVar for potential spinbox/input control
            qty_var = tk.StringVar(value=str(quantity))
            self.quantity_vars[product_id] = qty_var
            
            # ========== Bind Table Click Event ==========
            # Allow users to click on action buttons (settings, delete)
            self.tree.bind("<Button-1>", self._on_tree_click)

    def update_quantity(self, product_id, quantity):
        """
        Update item quantity.
        
        Args:
            product_id: Product ID
            quantity: New quantity
        """
        if product_id not in self.items:
            return
        
        if quantity <= 0:
            self.remove_item(product_id)
            return
        
        item = self.items[product_id]
        product = item['product']
        product_price = product.price if hasattr(product, 'price') else product.get('price', 0)
        
        subtotal = quantity * product_price
        
        # Update item
        item['quantity'] = quantity
        
        # Update table row
        row_id = item['row_id']
        product_name = product.name if hasattr(product, 'name') else product.get('name', '')
        
        self.tree.item(row_id, values=(
            product_name,
            f"₹{product_price:.2f}",
            quantity,
            f"₹{subtotal:.2f}",
            "⚙️ 🗑"
        ))
        
        if self.on_quantity_change:
            self.on_quantity_change(product_id, quantity, subtotal)

    def remove_item(self, product_id):
        """
        Remove item from table.
        
        Args:
            product_id: Product ID
        """
        if product_id not in self.items:
            return
        
        row_id = self.items[product_id]['row_id']
        self.tree.delete(row_id)
        del self.items[product_id]
        
        if product_id in self.quantity_vars:
            del self.quantity_vars[product_id]
        
        if self.on_delete:
            self.on_delete(product_id)

    def _on_tree_click(self, event):
        """Handle tree click for action buttons"""
        item = self.tree.identify('item', event.x, event.y)
        col = self.tree.identify_column(event.x, event.y)
        
        if item and col == "#5":  # Actions column
            # Find which product this is
            for product_id, item_data in self.items.items():
                if item_data['row_id'] == item:
                    # Determine if settings or delete
                    col_width = self.tree.column("#5", 'width')
                    col_x = self.tree.bbox(item, "#5")[0]
                    click_x = event.x - col_x
                    
                    if click_x < col_width * 0.5:
                        # Settings button
                        if self.on_settings:
                            self.on_settings(product_id)
                    else:
                        # Delete button
                        self.remove_item(product_id)
                    break

    def get_total_amount(self):
        """
        Calculate total amount for all items.
        
        Returns:
            Total amount
        """
        total = 0
        for item_data in self.items.values():
            product = item_data['product']
            quantity = item_data['quantity']
            product_price = product.price if hasattr(product, 'price') else product.get('price', 0)
            total += quantity * product_price
        
        return total

    def get_item_count(self):
        """Get total number of items in order"""
        return len(self.items)

    def clear_all(self):
        """Clear all items from table"""
        self.tree.delete(*self.tree.get_children())
        self.items.clear()
        self.quantity_vars.clear()

    def get_all_items(self):
        """
        Get all items in order.
        
        Returns:
            List of items with quantity
        """
        return list(self.items.values())
