import tkinter as tk
from tkinter import ttk, messagebox

__all__ = ["ProductTable"]


class ProductTable(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#FFFFFF")

        style = ttk.Style()
        style.theme_use("default")

        # ---------------- TABLE STYLE ----------------
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#1F2937",
            rowheight=42,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#F9FAFB",
            foreground="#1F2937",
            font=("Segoe UI", 11, "bold"),
            borderwidth=0
        )

        style.map("Treeview", background=[("selected", "#E5E7EB")])

        # Remove default borders
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        # ---------------- TABLE ----------------
        self.tree = ttk.Treeview(
            self,
            columns=("code", "name", "category", "qty", "price", "actions"),
            show="headings",
            selectmode="browse"
        )

        headings = ["Product Code", "Name", "Category", "Quantity", "Price", "Actions"]
        for col, text in zip(self.tree["columns"], headings):
            self.tree.heading(col, text=text)

        self.tree.column("code", width=100, anchor="center")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("category", width=140, anchor="center")
        self.tree.column("qty", width=90, anchor="center")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("actions", width=260, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- ROW STYLES ----------------
        # Stripe rows (this creates horizontal line effect)
        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background="#F3F4F6")

        # Subtle status highlight overlay feel
        self.tree.tag_configure("active", foreground="#065F46")   # green text
        self.tree.tag_configure("inactive", foreground="#991B1B") # red text

        self._data = []

        self.tree.bind("<Button-1>", self._on_click)

    # ---------------- LOAD DATA ----------------
    def load_data(self, data_list):
        if data_list == self._data:
            return

        self._data = data_list
        self.tree.delete(*self.tree.get_children())

        for idx, item in enumerate(data_list):
            stripe_tag = "even" if idx % 2 == 0 else "odd"
            status_tag = "active" if item.get("active", True) else "inactive"

            self.tree.insert(
                "",
                "end",
                iid=idx,
                values=(
                    item["code"],
                    item["name"],
                    item["category"],
                    item["quantity"],
                    f"₹{item['price']:.2f}",
                    "➕ Add   ✏ Edit   ⚠ Damage"
                ),
                tags=(stripe_tag, status_tag)
            )

    # ---------------- ACTION HANDLING ----------------
    def _on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if not row_id or col != "#6":
            return

        x_offset = event.x - self.tree.bbox(row_id, col)[0]

        if 0 <= x_offset < 90:
            messagebox.showinfo("Add Stock", f"{self._data[int(row_id)]['name']}")
        elif 90 <= x_offset < 170:
            messagebox.showinfo("Edit Product", f"{self._data[int(row_id)]['name']}")
        else:
            messagebox.showinfo("Damage", f"{self._data[int(row_id)]['name']}")