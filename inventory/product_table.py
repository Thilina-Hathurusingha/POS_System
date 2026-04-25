import tkinter as tk
from tkinter import ttk

__all__ = ["product_table"]

class ProductTable(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#F5F6F8")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#FFFFFF", 
                        foreground="#1F2937", 
                        rowheight=32, 
                        fieldbackground="#FFFFFF", 
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", 
                        background="#F5F6F8", 
                        foreground="#1F2937", 
                        font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#E5E7EB")])

        self.tree = ttk.Treeview(
            self, columns=("code", "name", "category", "qty", "price", "actions"),
            show="headings", selectmode="none", height=10
        )
        self.tree.heading("code", text="Product Code")
        self.tree.heading("name", text="Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("qty", text="Quantity")
        self.tree.heading("price", text="Price")
        self.tree.heading("actions", text="Actions")

        self.tree.column("code", width=110, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("price", width=90, anchor="center")
        self.tree.column("actions", width=260, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Store current data for refresh
        self._data = []

        # Bind for action simulation
        self.tree.bind("<Button-1>", self._on_click)

    def load_data(self, data_list):
        # Only refresh if data changed
        if data_list == self._data:
            return
        self._data = data_list
        self.tree.delete(*self.tree.get_children())
        for idx, item in enumerate(data_list):
            code_tag = self._make_code_tag(item["code"], item.get("active", True))
            actions = self._make_actions(idx)
            self.tree.insert(
                "", "end", iid=idx,
                values=(code_tag, item["name"], item["category"], item["quantity"], f"₹{item['price']:.2f}", actions)
            )

    def _make_code_tag(self, code, active):
        # Simulate colored tag with unicode block and color text
        if active:
            return f"\u25A0 {code}"  # Green
        else:
            return f"\u25A0 {code}"  # Red

    def _make_actions(self, idx):
        # Simulate buttons with text (real buttons not supported in Treeview)
        return "  [Add Stock]  [Edit]  [Damage]"

    def _on_click(self, event):
        # Simulate action button clicks
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or col != "#6":
            return
        x_offset = event.x - self.tree.bbox(row_id, col)[0]
        # Simulate button hitboxes
        if 0 <= x_offset < 80:
            self._add_stock(int(row_id))
        elif 80 <= x_offset < 150:
            self._edit(int(row_id))
        elif 150 <= x_offset < 240:
            self._damage(int(row_id))

    def _add_stock(self, idx):
        tk.messagebox.showinfo("Add Stock", f"Add stock for: {self._data[idx]['name']}")

    def _edit(self, idx):
        tk.messagebox.showinfo("Edit Product", f"Edit: {self._data[idx]['name']}")

    def _damage(self, idx):
        tk.messagebox.showinfo("Damage", f"Mark as damaged: {self._data[idx]['name']}")