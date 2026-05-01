import tkinter as tk
from tkinter import ttk

__all__ = ["FilterBar"]


class FilterBar(tk.Frame):
    def __init__(self, master, categories, vendors, on_search, on_filter_change, on_new_product):
        super().__init__(master, bg="#F5F6F8")

        self.on_search = on_search
        self.on_filter_change = on_filter_change
        self.on_new_product = on_new_product

        pad_x = 12
        pad_y = 6

        # ---------------- Category ----------------
        tk.Label(self, text="Category", bg="#F5F6F8", fg="#374151",
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=pad_x)

        self.category_var = tk.StringVar(value=categories[0])
        self.category_cb = ttk.Combobox(
            self, textvariable=self.category_var,
            values=categories, state="readonly",
            width=20, font=("Segoe UI", 10)
        )
        self.category_cb.grid(row=1, column=0, padx=pad_x, pady=(0, pad_y))
        self.category_cb.bind("<<ComboboxSelected>>", self._filter_changed)

        # ---------------- Vendor ----------------
        tk.Label(self, text="Vendor", bg="#F5F6F8", fg="#374151",
                 font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w", padx=pad_x)

        self.vendor_var = tk.StringVar(value=vendors[0])
        self.vendor_cb = ttk.Combobox(
            self, textvariable=self.vendor_var,
            values=vendors, state="readonly",
            width=20, font=("Segoe UI", 10)
        )
        self.vendor_cb.grid(row=1, column=1, padx=pad_x, pady=(0, pad_y))
        self.vendor_cb.bind("<<ComboboxSelected>>", self._filter_changed)

        # ---------------- Search ----------------
        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            self,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=35,
            bd=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#E5E7EB",
            highlightcolor="#3B82F6"
        )
        self.search_entry.grid(row=1, column=2, padx=pad_x, pady=(0, pad_y))
        self.search_entry.insert(0, "Search by product code or name...")
        self.search_entry.config(fg="#9CA3AF")

        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._add_placeholder)
        self.search_entry.bind("<Return>", self._search)

        # Search Button
        self.search_btn = tk.Button(
            self,
            text="🔍",
            font=("Segoe UI", 10),
            bg="#3B82F6",
            fg="white",
            bd=0,
            padx=10,
            pady=4,
            activebackground="#2563EB",
            cursor="hand2",
            command=self._search
        )
        self.search_btn.grid(row=1, column=3, padx=(0, pad_x))

        # Spacer
        self.grid_columnconfigure(4, weight=1)

        # ---------------- New Product ----------------
        self.new_btn = tk.Button(
            self,
            text="+ New Product",
            font=("Segoe UI", 10, "bold"),
            bg="#3B82F6",
            fg="white",
            bd=0,
            padx=18,
            pady=6,
            activebackground="#2563EB",
            cursor="hand2",
            command=self.on_new_product
        )
        self.new_btn.grid(row=1, column=5, padx=pad_x)

        self._placeholder = "Search by product code or name..."

    def _clear_placeholder(self, event):
        if self.search_entry.get() == self._placeholder:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="#111827")

    def _add_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, self._placeholder)
            self.search_entry.config(fg="#9CA3AF")

    def _search(self, event=None):
        value = self.search_var.get()
        if value == self._placeholder:
            value = ""
        self.on_search(value)

    def _filter_changed(self, event=None):
        self.on_filter_change(self.category_var.get(), self.vendor_var.get())