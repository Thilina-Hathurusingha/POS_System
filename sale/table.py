"""
Order Table Panel - Top right section displaying order items in a Treeview.
"""

import tkinter as tk
from tkinter import ttk
from log.logging_config import get_logger
import shared.configuration as config

logger = get_logger(__name__)


class OrderTablePanel(tk.Frame):
    """Panel for displaying order items in a table"""

    FONT_HEADER = ("Segoe UI", 15, "bold")
    FONT_NORMAL = ("Segoe UI", 14, "normal")

    BG_PANEL = "#FFFFFF"
    BG_MAIN = "#EEF2F6"
    BORDER_COLOR = "#E5E7EB"
    TEXT_PRIMARY = "#111827"

    def __init__(self, parent, on_quantity_change=None, on_delete=None, on_settings=None, **kwargs):
        if 'bg' not in kwargs:
            kwargs['bg'] = self.BG_PANEL
        super().__init__(parent, **kwargs)

        self.on_quantity_change = on_quantity_change
        self.on_delete = on_delete
        self.on_settings = on_settings

        self.items = {}
        self.quantity_vars = {}

        self._create_ui()

    # ================= UI =================
    def _create_ui(self):
        header = tk.Label(
            self,
            text="Order Items",
            font=self.FONT_HEADER,
            bg=self.BG_PANEL,
            fg=self.TEXT_PRIMARY,
            anchor=tk.W
        )
        header.pack(fill=tk.X, padx=12, pady=(12, 8))

        table_container = tk.Frame(self, bg=self.BG_PANEL)
        table_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        table_container.pack_propagate(False)  # prevent expansion pressure

        columns = ("Item Name", "Rate", "Qty", "Subtotal", "Delete")

        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            height=16,
            show="headings",
            selectmode="none"
        )

        # Reduced widths to avoid forcing layout expansion
        column_config = [
            ("Item Name", 120),
            ("Rate", 80),
            ("Qty", 70),
            ("Subtotal", 90),
            ("Delete", 60)
        ]

        for col, width in column_config:
            if col == "Item Name":
                self.tree.column(col, width=width, anchor="w", stretch=True)
            else:
                self.tree.column(col, width=width, anchor="center", stretch=False)
            self.tree.heading(col, text=col)

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

        self.tree.tag_configure('oddrow', background=self.BG_PANEL)
        self.tree.tag_configure('evenrow', background='#F9FAFB')

        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind ONCE (important fix)
        self.tree.bind("<Button-1>", self._on_tree_click)

    # ================= Data =================
    def add_item(self, product):
        product_id = product.id if hasattr(product, 'id') else product.get('id')

        if product_id in self.items:
            self.update_quantity(product_id, self.items[product_id]['quantity'] + 1)
            return

        name = product.name if hasattr(product, 'name') else product.get('name', '')
        price = product.price if hasattr(product, 'price') else product.get('price', 0)

        qty = 1
        subtotal = qty * price

        tag = 'evenrow' if len(self.items) % 2 == 0 else 'oddrow'

        row_id = self.tree.insert("", "end", values=(
            name,
            f"{config.currency_symbol}{price:.2f}",
            qty,
            f"{config.currency_symbol}{subtotal:.2f}",
            "✖"
        ), tags=(tag,))

        self.items[product_id] = {
            "product": product,
            "quantity": qty,
            "row_id": row_id
        }

    def update_quantity(self, product_id, quantity):
        if product_id not in self.items:
            return

        if quantity <= 0:
            self.remove_item(product_id)
            return

        item = self.items[product_id]
        product = item["product"]

        price = product.price if hasattr(product, 'price') else product.get('price', 0)
        subtotal = price * quantity

        item["quantity"] = quantity

        name = product.name if hasattr(product, 'name') else product.get('name', '')

        self.tree.item(item["row_id"], values=(
            name,
            f"{config.currency_symbol}{price:.2f}",
            quantity,
            f"{config.currency_symbol}{subtotal:.2f}",
            "✖"
        ))

        if self.on_quantity_change:
            self.on_quantity_change(product_id, quantity, subtotal)

    def remove_item(self, product_id):
        if product_id not in self.items:
            return

        self.tree.delete(self.items[product_id]["row_id"])
        del self.items[product_id]

        if self.on_delete:
            self.on_delete(product_id)

    # ================= Click Handling =================
    def _on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if not item:
            return

        for product_id, item_data in self.items.items():
            if item_data["row_id"] == item:
                if col == "#5":  # Delete column
                    self.remove_item(product_id)
                else:
                    if self.on_settings:
                        self.on_settings(product_id)
                break

    # ================= Utils =================
    def get_total_amount(self):
        total = 0
        for item in self.items.values():
            product = item["product"]
            price = product.price if hasattr(product, 'price') else product.get('price', 0)
            total += price * item["quantity"]
        return total

    def get_item_count(self):
        return len(self.items)

    def clear_all(self):
        self.tree.delete(*self.tree.get_children())
        self.items.clear()

    def get_all_items(self):
        return list(self.items.values())