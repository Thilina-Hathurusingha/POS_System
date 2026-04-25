import tkinter as tk

__all__ = ["Pagination"]

class Pagination(tk.Frame):
    def __init__(self, master, total_items, rows_per_page, on_page_change):
        super().__init__(master, bg="#F5F6F8")
        self.on_page_change = on_page_change
        self.rows_per_page = rows_per_page
        self.total_items = total_items
        self.current_page = 1
        self.total_pages = max(1, (self.total_items + self.rows_per_page - 1) // self.rows_per_page)
        self._build()

    def _build(self):
        for widget in self.winfo_children():
            widget.destroy()
        btn_style = {"font": ("Segoe UI", 10), "bg": "#FFFFFF", "fg": "#1F2937", "bd": 0, "padx": 8, "pady": 2, "activebackground": "#E5E7EB", "cursor": "hand2"}
        # First
        tk.Button(self, text="« First", command=lambda: self._goto(1), state="normal" if self.current_page > 1 else "disabled", **btn_style).pack(side="left", padx=2)
        # Prev
        tk.Button(self, text="‹ Prev", command=lambda: self._goto(self.current_page - 1), state="normal" if self.current_page > 1 else "disabled", **btn_style).pack(side="left", padx=2)
        # Page numbers
        for i in range(1, self.total_pages + 1):
            if abs(i - self.current_page) <= 1 or i in [1, self.total_pages]:
                style = btn_style.copy()
                if i == self.current_page:
                    style["bg"] = "#3B82F6"
                    style["fg"] = "#FFFFFF"
                tk.Button(self, text=str(i), command=lambda i=i: self._goto(i), **style).pack(side="left", padx=1)
            elif i == self.current_page - 2 or i == self.current_page + 2:
                tk.Label(self, text="...", bg="#F5F6F8", font=("Segoe UI", 10)).pack(side="left", padx=2)
        # Next
        tk.Button(self, text="Next ›", command=lambda: self._goto(self.current_page + 1), state="normal" if self.current_page < self.total_pages else "disabled", **btn_style).pack(side="left", padx=2)
        # Last
        tk.Button(self, text="Last »", command=lambda: self._goto(self.total_pages), state="normal" if self.current_page < self.total_pages else "disabled", **btn_style).pack(side="left", padx=2)
        # Info
        info = f"  Showing {(self.current_page-1)*self.rows_per_page+1} to {min(self.current_page*self.rows_per_page, self.total_items)} of {self.total_items} items"
        tk.Label(self, text=info, bg="#F5F6F8", fg="#6B7280", font=("Segoe UI", 10)).pack(side="left", padx=12)

    def _goto(self, page):
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self._build()
            self.on_page_change(page)

    def update_total(self, total_items):
        self.total_items = total_items
        self.total_pages = max(1, (self.total_items + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        self._build()