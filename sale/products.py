"""
Products Panel - Middle left section displaying product cards in a grid.
"""

import tkinter as tk
from tkinter import ttk
from logging_config import get_logger

logger = get_logger(__name__)


class ItemCard(tk.Frame):
    """Reusable product card component"""

    # UI Constants
    FONT_NAME = ("Segoe UI", 11, "bold")
    FONT_PRICE = ("Segoe UI", 12, "bold")
    
    # Colors
    BG_PANEL = "#FFFFFF"
    BORDER_COLOR = "#E5E7EB"
    BG_HOVER = "#F3F4F6"
    BG_CLICK = "#E0E7FF"
    TEXT_PRIMARY = "#111827"
    PRIMARY_BLUE = "#3B82F6"

    def __init__(self, parent, product=None, on_click=None, **kwargs):
        """
        Initialize ItemCard.
        
        Args:
            parent: Parent widget
            product: Product data (dict or object with id, name, price)
            on_click: Callback when card is clicked
        """
        super().__init__(parent, bg=self.BG_PANEL, **kwargs)
        
        # ========== Store Data and Callbacks ==========
        self.product = product  # Store product data for display
        self.on_click = on_click  # Callback function when card is clicked
        
        # ========== Animation State ==========
        self.is_hovered = False  # Track hover state for visual feedback
        self.animation_running = False  # Prevent animation conflicts
        
        # ========== Create Visual Structure ==========
        # Create border frame for flat design effect
        self.border_frame = tk.Frame(self, bg=self.BORDER_COLOR)
        self.border_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Main content frame with product information
        self.main_frame = tk.Frame(self.border_frame, bg=self.BG_PANEL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI only if product data is provided
        if product:
            self._create_ui()  # Display product information
            self._bind_events()  # Bind mouse events for interaction

    def _create_ui(self):
        """Create card UI"""
        # ========== Content Padding Frame ==========
        # Create padding around product information
        content = tk.Frame(self.main_frame, bg=self.BG_PANEL)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ========== Product Name ==========
        # Extract name from product object or dict
        name_label = tk.Label(
            content,
            text=self.product.name if hasattr(self.product, 'name') else str(self.product.get('name', '')),
            font=self.FONT_NAME,
            bg=self.BG_PANEL,
            fg=self.TEXT_PRIMARY,
            wraplength=120,  # Wrap text to 120 pixels wide
            justify=tk.CENTER
        )
        name_label.pack(fill=tk.X, pady=(0, 5))
        
        # ========== Price ==========
        # Display product price in rupees (₹)
        price = self.product.price if hasattr(self.product, 'price') else self.product.get('price', 0)
        price_label = tk.Label(
            content,
            text=f"₹{price:.2f}",  # Format to 2 decimal places
            font=self.FONT_PRICE,
            bg=self.BG_PANEL,
            fg=self.PRIMARY_BLUE  # Blue color for price emphasis
        )
        price_label.pack(fill=tk.X, pady=(0, 5))
        
        # ========== Stock Information ==========
        # Show available stock quantity in smaller text
        stock = self.product.stock if hasattr(self.product, 'stock') else self.product.get('stock', 0)
        stock_label = tk.Label(
            content,
            text=f"Stock: {stock}",
            font=("Segoe UI", 9),  # Smaller font for secondary info
            bg=self.BG_PANEL,
            fg="#6B7280"  # Gray color for secondary text
        )
        stock_label.pack(fill=tk.X)

    def _bind_events(self):
        """Bind mouse events for hover effect"""
        # ========== Recursive Binding Function ==========
        # Bind events to all nested widgets for consistent behavior
        def bind_recursive(widget):
            # Bind mouse enter and leave events for hover effect
            widget.bind("<Enter>", self._on_hover)
            widget.bind("<Leave>", self._on_leave)
            # Bind click event to add product to order
            widget.bind("<Button-1>", self._on_card_click)
            # Recursively bind events to all child widgets
            for child in widget.winfo_children():
                bind_recursive(child)
        
        # Start binding from main content frame
        bind_recursive(self.main_frame)
        # Also bind to the card frame itself
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_card_click)

    def _on_hover(self, event):
        """Handle hover effect - only change color"""
        # ========== Check Hover State ==========
        # Only update if not already hovered and no animation is in progress
        if not self.is_hovered and not self.animation_running:
            self.is_hovered = True  # Mark as hovered
            # Change to hover color
            self.main_frame.config(bg=self.BG_HOVER)
            # Apply hover color to all nested widgets
            self._set_bg_recursive(self.main_frame, self.BG_HOVER)

    def _on_leave(self, event):
        """Handle leave effect - restore color"""
        # ========== Restore Normal State ==========
        # Only restore if currently hovered and no animation is in progress
        if self.is_hovered and not self.animation_running:
            self.is_hovered = False  # Mark as not hovered
            # Restore to normal background color
            self.main_frame.config(bg=self.BG_PANEL)
            # Apply normal color to all nested widgets
            self._set_bg_recursive(self.main_frame, self.BG_PANEL)

    def _set_bg_recursive(self, widget, color):
        """Recursively set background color"""
        try:
            current_bg = widget.cget("bg")
            if current_bg in [self.BG_PANEL, self.BG_HOVER, self.BG_CLICK]:
                widget.config(bg=color)
        except tk.TclError:
            pass
        
        for child in widget.winfo_children():
            self._set_bg_recursive(child, color)

    def _animate_click(self):
        """Animate card on click with quick color change"""
        if self.animation_running:
            return
        
        self.animation_running = True
        original_color = self.main_frame.cget("bg")
        
        # Flash to click color
        self.main_frame.config(bg=self.BG_CLICK)
        self._set_bg_recursive(self.main_frame, self.BG_CLICK)
        
        # Restore after 150ms
        self.after(150, lambda: self._restore_animation_color(original_color))

    def _restore_animation_color(self, original_color):
        """Restore original color after animation"""
        self.main_frame.config(bg=original_color)
        self._set_bg_recursive(self.main_frame, original_color)
        self.animation_running = False

    def _on_card_click(self, event):
        """Handle card click"""
        self._animate_click()
        if self.on_click:
            self.on_click(self.product)


class ProductsPanel(tk.Frame):
    """Panel for displaying products in a grid layout"""

    # UI Constants
    GRID_COLS = 4
    GRID_ROWS = 5
    FONT_LOADING = ("Segoe UI", 12)
    
    # Colors
    BG_MAIN = "#EEF2F6"
    BG_PANEL = "#FFFFFF"

    def __init__(self, parent, on_product_click=None, **kwargs):
        """
        Initialize ProductsPanel.
        
        Args:
            parent: Parent widget
            on_product_click: Callback when product is clicked
        """
        if 'bg' not in kwargs:
            kwargs['bg'] = self.BG_MAIN
        super().__init__(parent, **kwargs)
        
        self.on_product_click = on_product_click
        self.products = []
        self.cards = []
        
        self._create_ui()

    def _create_ui(self):
        """Create panel UI"""
        # Container for grid
        self.container = tk.Frame(self, bg=self.BG_MAIN)
        self.container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Initially show loading message
        self.loading_label = tk.Label(
            self.container,
            text="Loading products...",
            font=self.FONT_LOADING,
            bg=self.BG_MAIN,
            fg="#6B7280"
        )
        self.loading_label.pack(pady=20)

    def display_products(self, products):
        """
        Display products in grid layout.
        
        Args:
            products: List of product objects
        """
        self.products = products
        
        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        
        # Remove loading label if present
        if hasattr(self, 'loading_label'):
            self.loading_label.pack_forget()
        
        # Clear and recreate grid
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Create grid layout
        grid_frame = tk.Frame(self.container, bg=self.BG_MAIN)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns
        for col in range(self.GRID_COLS):
            grid_frame.columnconfigure(col, weight=1)
        
        # Add product cards
        row = 0
        col = 0
        for product in products:
            card = ItemCard(
                grid_frame,
                product=product,
                on_click=self.on_product_click,
                height=140,
                width=150
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self.cards.append(card)
            
            col += 1
            if col >= self.GRID_COLS:
                col = 0
                row += 1
        
        # If no products, show message
        if not products:
            empty_label = tk.Label(
                grid_frame,
                text="No products found",
                font=self.FONT_LOADING,
                bg=self.BG_MAIN,
                fg="#9CA3AF"
            )
            empty_label.grid(row=0, column=0, columnspan=self.GRID_COLS, pady=40)

    def clear(self):
        """Clear all displayed products"""
        for card in self.cards:
            card.destroy()
        self.cards.clear()
        self.products.clear()
