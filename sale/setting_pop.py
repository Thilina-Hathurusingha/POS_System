import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional

class SettingItemPopup:
    """A modal popup to edit product quantity and discount price."""

    WIDTH = 600
    HEIGHT = 650

    def __init__(self, parent: tk.Widget, product_data: Dict, batch_data: Optional[List[Dict]]):
        self.parent = parent
        self._product = dict(product_data)
        self._batches = [dict(b) for b in (batch_data or [])]
        self.result: Optional[Dict] = None

        self._root = tk.Toplevel(parent)
        self._root.withdraw()
        self._root.transient(parent)
        self._root.configure(bg="#F8FAFC")
        self._root.resizable(False, False)
        self._root.title("Edit Item")

        self._selected_batch = None
        self._create_styles()
        self._create_ui()
        self._bind_events()

    def _create_styles(self):
        style = ttk.Style(self._root)
        style.theme_use('clam')
        
        style.configure('ProductName.TLabel', background='#F1F5F9', font=('Segoe UI', 16, 'bold'), foreground='#1E293B')
        style.configure('MRP.TLabel', background='#F1F5F9', font=('Segoe UI', 12), foreground='#64748B')
        style.configure('MRPValue.TLabel', background='#F1F5F9', font=('Segoe UI', 12, 'bold'), foreground='#2563EB')
        style.configure('FieldLabel.TLabel', background='#FFFFFF', font=('Segoe UI', 10, 'bold'), foreground='#1E293B')
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), background='#2563EB', foreground='#FFFFFF')
        style.map('Primary.TButton', background=[('active', '#1D4ED8')])
        style.configure('Cancel.TButton', font=('Segoe UI', 10), background='#FFFFFF', foreground='#1E293B')
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=35)

    def _create_ui(self):
        main_container = tk.Frame(self._root, bg="#F8FAFC", padx=20, pady=20)
        main_container.pack(fill='both', expand=True)

        # 1. Top Header Card
        header_card = tk.Frame(main_container, bg="#F1F5F9", highlightbackground="#E2E8F0", highlightthickness=1, bd=0)
        header_card.pack(fill='x', pady=(0, 15), ipady=15)
        
        tk.Label(header_card, text="📦", font=("Arial", 30), bg="#DBEafe", fg="#2563EB", width=2).pack(side='left', padx=20)

        info_frame = tk.Frame(header_card, bg="#F1F5F9")
        info_frame.pack(side='left', fill='y')
        
        ttk.Label(info_frame, text=self._product.get('name', 'Product'), style='ProductName.TLabel').pack(anchor='w')
        
        mrp_row = tk.Frame(info_frame, bg="#F1F5F9")
        mrp_row.pack(anchor='w', pady=(5, 0))
        ttk.Label(mrp_row, text="MRP: ", style='MRP.TLabel').pack(side='left')
        
        # Fixed: Assigning to self._mrp_display so _on_row_select can find it
        self._mrp_display = ttk.Label(mrp_row, text=f"₹ {self._product.get('mrp', 0.0):.2f}", style='MRPValue.TLabel')
        self._mrp_display.pack(side='left')

        # 2. Controls Card
        controls_card = tk.Frame(main_container, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, bd=0)
        controls_card.pack(fill='x', pady=10, ipady=15, ipadx=15)

        dp_frame = tk.Frame(controls_card, bg="#FFFFFF")
        dp_frame.pack(side='left', padx=20, fill='y')
        ttk.Label(dp_frame, text='Discount Price (₹)', style='FieldLabel.TLabel').pack(anchor='w', pady=(0, 5))
        
        self._discount_var = tk.StringVar(value=f"{self._product.get('discount_price', 0.0):.2f}")
        entry_border = tk.Frame(dp_frame, bg="#2563EB", padx=1, pady=1)
        entry_border.pack(anchor='w')
        self._discount_entry = tk.Entry(entry_border, textvariable=self._discount_var, width=25, font=('Segoe UI', 12), relief='flat', bd=5)
        self._discount_entry.pack()

        qty_frame = tk.Frame(controls_card, bg="#FFFFFF")
        qty_frame.pack(side='right', padx=20, fill='y')
        ttk.Label(qty_frame, text='Quantity', style='FieldLabel.TLabel').pack(anchor='w', pady=(0, 5))
        
        # Blue border frame to match Discount Price
        qty_entry_border = tk.Frame(qty_frame, bg="#2563EB", padx=1, pady=1)
        qty_entry_border.pack(anchor='w')
        
        self._qty_var = tk.IntVar(value=max(1, int(self._product.get('quantity', 2))))
        self._qty_entry = tk.Entry(
            qty_entry_border, 
            textvariable=self._qty_var, 
            width=25, # Same width as Discount Price
            font=('Segoe UI', 12), 
            relief='flat', 
            bd=5,
            justify='left'
        )
        self._qty_entry.pack()
        
        tk.Label(qty_frame, text="(Minimum quantity: 1)", font=("Segoe UI", 8), bg="#FFFFFF", fg="#64748B").pack(anchor='w', pady=(2, 0))


        # 3. Batch Table
        ttk.Label(main_container, text="Available Batches / Stock", style='FieldLabel.TLabel', background="#F8FAFC").pack(anchor='w', pady=(10, 5))
        
        table_frame = tk.Frame(main_container, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        table_frame.pack(fill='both', expand=True)

        cols = ('batch_id', 'stock', 'mrp', 'discount')
        self._tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=5)
        self._tree.heading('batch_id', text='Batch ID')
        self._tree.heading('stock', text='Stock Count')
        self._tree.heading('mrp', text='MRP (₹)')
        self._tree.heading('discount', text='Discount Price (₹)')
        
        for col in cols:
            self._tree.column(col, anchor='center', width=100)
        self._tree.pack(fill='both', expand=True)

        for b in self._batches:
            self._tree.insert('', 'end', values=(
                b.get('batch_id'), b.get('stock'), 
                f"{b.get('mrp', 0.0):.2f}", f"{b.get('discount_price', 0.0):.2f}"
            ))

        # 4. Footer
        footer = tk.Frame(main_container, bg="#F8FAFC")
        footer.pack(fill='x', pady=(20, 0))
        ttk.Button(footer, text='✓ Apply Changes', style='Primary.TButton', command=self._on_apply).pack(side='right', padx=(10, 0))
        ttk.Button(footer, text='✕ Cancel', style='Cancel.TButton', command=self._on_cancel).pack(side='right')

    def _bind_events(self):
        self._tree.bind('<<TreeviewSelect>>', self._on_row_select)
        self._root.bind('<Return>', lambda e: self._on_apply())
        self._root.bind('<Escape>', lambda e: self._on_cancel())
        self._root.bind('<Map>', lambda e: self._focus_discount())

    def _focus_discount(self):
        self._qty_entry.focus_set()
        self._qty_entry.selection_range(0, 'end')

    def _on_row_select(self, event=None):
        sel = self._tree.selection()
        if not sel: return
        vals = self._tree.item(sel[0], 'values')
        batch = next((b for b in self._batches if str(b.get('batch_id')) == str(vals[0])), None)
        if batch:
            self._discount_var.set(f"{batch.get('discount_price', 0.0):.2f}")
            self._mrp_display.config(text=f"₹ {batch.get('mrp', 0.0):.2f}")
            self._selected_batch = dict(batch)

    def _decrease_qty(self):
        self._qty_var.set(max(1, self._qty_var.get() - 1))

    def _increase_qty(self):
        self._qty_var.set(self._qty_var.get() + 1)

    def _on_apply(self):
        try:
            self.result = {
                'quantity': int(self._qty_var.get()),
                'discount_price': float(self._discount_var.get()),
                'selected_batch': self._selected_batch,
            }
            self._root.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def _on_cancel(self):
        self.result = None
        self._root.destroy()

    def show(self) -> Optional[Dict]:
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self._root.winfo_screenheight() // 2) - (self.HEIGHT // 2)
        self._root.geometry(f'{self.WIDTH}x{self.HEIGHT}+{x}+{y}')
        self._root.deiconify()
        self._root.grab_set()
        self._root.wait_window()
        return self.result

def open_edit_popup(parent, prod, batch):
    return SettingItemPopup(parent, prod, batch).show()