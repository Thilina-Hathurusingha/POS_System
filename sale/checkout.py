"""
Checkout Panel - Bottom right section with summary and action buttons.
"""

import tkinter as tk
from logging_config import get_logger

logger = get_logger(__name__)


class CheckoutPanel(tk.Frame):
    """Panel for checkout summary and actions"""

    # UI Constants
    FONT_LABEL = ("Segoe UI", 11, "normal")
    FONT_VALUE = ("Segoe UI", 12, "bold")
    FONT_BUTTON = ("Segoe UI", 11, "normal")
    
    # Colors
    BG_PANEL = "#FFFFFF"
    BG_MAIN = "#EEF2F6"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    PRIMARY_BLUE = "#3B82F6"
    GREEN_CHECKOUT = "#22C55E"
    RED_CLEAR = "#EF4444"
    BG_BUTTON_GRAY = "#F3F4F6"

    def __init__(self, parent, on_clear=None, on_checkout=None, on_checkout_print=None, **kwargs):
        """
        Initialize CheckoutPanel.
        
        Args:
            parent: Parent widget
            on_clear: Callback for clear button
            on_checkout: Callback for checkout button
            on_checkout_print: Callback for checkout & print button
        """
        logger.debug("ENTRY: CheckoutPanel.__init__()")
        
        if 'bg' not in kwargs:
            kwargs['bg'] = self.BG_PANEL
        super().__init__(parent, **kwargs)
        
        try:
            # ========== Store Callback Functions ==========
            # Callbacks for order management operations
            self.on_clear = on_clear  # Clear entire order
            self.on_checkout = on_checkout  # Process payment
            self.on_checkout_print = on_checkout_print  # Process payment and print receipt
            
            # ========== Order Summary Variables ==========
            # These track the order totals that will be displayed
            self.discount_amount = 0.0  # Total discount applied
            self.total_amount = 0.0  # Total amount before payment
            self.amount_received = 0.0  # Cash received from customer
            self.change_amount = 0.0  # Change to give back to customer
            
            # ========== Create UI ==========
            # Build summary display and action buttons
            self._create_ui()
            logger.debug("EXIT: CheckoutPanel.__init__() - Success")
            
        except Exception as e:
            logger.error(f"Failed to initialize CheckoutPanel: {str(e)}", exc_info=True)
            raise

    def _create_ui(self):
        """Create checkout UI"""
        # ========== Main Container ==========
        # Frame to hold all checkout summary and payment controls
        container = tk.Frame(self, bg=self.BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # ========== Row 1: Order Summary (Discount & Total) ==========
        # Summary frame showing order totals
        summary_frame = tk.Frame(container, bg=self.BG_PANEL)
        summary_frame.pack(fill=tk.X, pady=(0, 12))
        
        # ========== Discount Display ==========
        # Shows discount amount applied to order
        discount_left = tk.Frame(summary_frame, bg=self.BG_PANEL)
        discount_left.pack(side=tk.LEFT, padx=(0, 20))
        
        discount_label = tk.Label(
            discount_left,
            text="Discount:",
            font=self.FONT_LABEL,
            bg=self.BG_PANEL,
            fg=self.TEXT_SECONDARY
        )
        discount_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Display discount amount in blue
        self.discount_value = tk.Label(
            discount_left,
            text="₹0.00",
            font=self.FONT_VALUE,
            bg=self.BG_PANEL,
            fg=self.PRIMARY_BLUE
        )
        self.discount_value.pack(side=tk.LEFT)
        
        # ========== Total Amount Display ==========
        # Shows final order total after discount
        total_left = tk.Frame(summary_frame, bg=self.BG_PANEL)
        total_left.pack(side=tk.LEFT, padx=(0, 20))
        
        total_label = tk.Label(
            total_left,
            text="Total Amount:",
            font=self.FONT_LABEL,
            bg=self.BG_PANEL,
            fg=self.TEXT_SECONDARY
        )
        total_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Display total in green to highlight final amount
        self.total_value = tk.Label(
            total_left,
            text="₹0.00",
            font=self.FONT_VALUE,
            bg=self.BG_PANEL,
            fg=self.GREEN_CHECKOUT
        )
        self.total_value.pack(side=tk.LEFT)
        
        # ========== Row 2: Payment Information ==========
        # Frame for cash received and change calculation
        payment_frame = tk.Frame(container, bg=self.BG_PANEL)
        payment_frame.pack(fill=tk.X, pady=(0, 12))
        
        # ========== Amount Received Input ==========
        # Input field for customer's payment amount
        received_label = tk.Label(
            payment_frame,
            text="Amount Received:",
            font=self.FONT_LABEL,
            bg=self.BG_PANEL,
            fg=self.TEXT_SECONDARY
        )
        received_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Create StringVar for tracking amount received changes
        self.amount_received_var = tk.StringVar()
        self.amount_received_var.trace("w", self._on_amount_change)  # Recalculate change on input
        
        amount_entry = tk.Entry(
            payment_frame,
            textvariable=self.amount_received_var,
            font=self.FONT_LABEL,
            bg=self.BG_MAIN,
            fg=self.TEXT_PRIMARY,
            relief=tk.FLAT,
            border=1,
            width=12
        )
        amount_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # ========== Change Display ==========
        # Shows calculated change to give back to customer
        change_label = tk.Label(
            payment_frame,
            text="Change:",
            font=self.FONT_LABEL,
            bg=self.BG_PANEL,
            fg=self.TEXT_SECONDARY
        )
        change_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.change_value = tk.Label(
            payment_frame,
            text="₹0.00",
            font=self.FONT_VALUE,
            bg=self.BG_PANEL,
            fg=self.TEXT_PRIMARY
        )
        self.change_value.pack(side=tk.LEFT)
        
        # Row 3: Action Buttons
        button_frame = tk.Frame(container, bg=self.BG_PANEL)
        button_frame.pack(fill=tk.X)
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            font=self.FONT_BUTTON,
            bg=self.BG_BUTTON_GRAY,
            fg=self.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_clear_click
        )
        clear_btn.pack(side=tk.LEFT, padx=4)
        
        # Checkout button
        checkout_btn = tk.Button(
            button_frame,
            text="Checkout",
            font=self.FONT_BUTTON,
            bg=self.GREEN_CHECKOUT,
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_checkout_click
        )
        checkout_btn.pack(side=tk.LEFT, padx=4)
        
        # Checkout & Print button
        checkout_print_btn = tk.Button(
            button_frame,
            text="Checkout & Print",
            font=self.FONT_BUTTON,
            bg=self.PRIMARY_BLUE,
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._on_checkout_print_click
        )
        checkout_print_btn.pack(side=tk.LEFT, padx=4)

    def _on_amount_change(self, *args):
        """Handle amount received change"""
        try:
            amount_str = self.amount_received_var.get().strip()
            amount = float(amount_str) if amount_str else 0.0
            self.amount_received = amount
            
            # Calculate change
            self.change_amount = max(0, amount - self.total_amount)
            self.change_value.config(text=f"₹{self.change_amount:.2f}")
        except ValueError:
            self.change_value.config(text="₹0.00")

    def _on_clear_click(self):
        """Handle clear button click"""
        if self.on_clear:
            self.on_clear()

    def _on_checkout_click(self):
        """Handle checkout button click"""
        if self.on_checkout:
            self.on_checkout()

    def _on_checkout_print_click(self):
        """Handle checkout & print button click"""
        if self.on_checkout_print:
            self.on_checkout_print()

    def update_totals(self, total_amount, discount_amount=0.0):
        """
        Update displayed totals.
        
        Args:
            total_amount: Total amount
            discount_amount: Discount amount
        """
        self.total_amount = total_amount
        self.discount_amount = discount_amount
        
        self.discount_value.config(text=f"₹{discount_amount:.2f}")
        self.total_value.config(text=f"₹{total_amount:.2f}")
        
        # Reset change calculation
        self._on_amount_change()

    def reset(self):
        """Reset checkout panel"""
        self.discount_amount = 0.0
        self.total_amount = 0.0
        self.amount_received = 0.0
        self.change_amount = 0.0
        
        self.discount_value.config(text="₹0.00")
        self.total_value.config(text="₹0.00")
        self.amount_received_var.set("")
        self.change_value.config(text="₹0.00")

    def get_transaction_data(self):
        """
        Get transaction data.
        
        Returns:
            Dictionary with transaction details
        """
        return {
            "total_amount": self.total_amount,
            "discount_amount": self.discount_amount,
            "amount_received": self.amount_received,
            "change": self.change_amount,
        }
