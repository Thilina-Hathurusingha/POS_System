import tkinter as tk
from tkinter import ttk
from .filter import FilterBar
from .product_table import ProductTable
from .paging import Pagination

# Dummy data for demonstration
DUMMY_PRODUCTS = [
    {
        "code": f"P{str(i+1).zfill(3)}",
        "name": f"Atlas EX {40 + i*20}PG {'Single' if i % 2 == 0 else 'Square'}",
        "category": "Exercise Books",
        "quantity": (i * 3 + 6) % 25,
        "price": 54.00 + (i % 5) * 18,
        "active": i not in [5, 7],  # Simulate inactive for P006, P008
    }
    for i in range(20)
]

__all__ = ["InventoryPage"]

class InventoryPage(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, bg="#F5F6F8", *args, **kwargs)
        self.pack(fill="both", expand=True)
        self.products = DUMMY_PRODUCTS.copy()
        self.filtered_products = self.products.copy()
        self.current_page = 1
        self.rows_per_page = 10

        # Filter Bar
        self.filter_bar = FilterBar(
            self,
            categories=["All Categories", "Exercise Books"],
            vendors=["All Vendors", "Vendor A", "Vendor B"],
            on_search=self.on_search,
            on_filter_change=self.on_filter_change,
            on_new_product=self.on_new_product
        )
        self.filter_bar.pack(fill="x", padx=24, pady=(24, 8))

        # Product Table
        self.table_frame = tk.Frame(self, bg="#F5F6F8")
        self.table_frame.pack(fill="both", expand=True, padx=24)
        self.product_table = ProductTable(self.table_frame)
        self.product_table.pack(fill="both", expand=True)

        # Pagination
        self.pagination = Pagination(
            self,
            total_items=len(self.filtered_products),
            rows_per_page=self.rows_per_page,
            on_page_change=self.on_page_change
        )
        self.pagination.pack(fill="x", pady=(8, 24))

        self.refresh_table()

    def on_search(self, search_text):
        self.current_page = 1
        self.apply_filters(search=search_text)

    def on_filter_change(self, category, vendor):
        self.current_page = 1
        self.apply_filters(category, vendor)

    def on_new_product(self):
        # Placeholder for new product logic
        tk.messagebox.showinfo("New Product", "Add new product dialog would appear.")

    def on_page_change(self, page_number):
        self.current_page = page_number
        self.refresh_table()

    def apply_filters(self, category=None, vendor=None, search=None):
        # Simulate filtering and searching
        data = self.products
        if category and category != "All Categories":
            data = [p for p in data if p["category"] == category]
        if vendor and vendor != "All Vendors":
            # Simulate vendor filter (not in dummy data)
            pass
        if search:
            s = search.lower()
            data = [p for p in data if s in p["code"].lower() or s in p["name"].lower()]
        self.filtered_products = data
        self.pagination.update_total(len(self.filtered_products))
        self.refresh_table()

    def refresh_table(self):
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        page_data = self.filtered_products[start:end]
        self.product_table.load_data(page_data)
