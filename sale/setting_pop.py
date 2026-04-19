import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from typing import List, Dict, Optional


class SettingItemPopup:
	"""A modal popup to edit product quantity and discount price.

	Usage:
		popup = EditItemPopup(parent, product_data, batch_data)
		result = popup.show()

	The popup will return a dict with keys: `quantity`, `discount_price`,
	`selected_batch` (or None) when Apply is clicked, or None when cancelled.
	"""

	WIDTH = 520
	HEIGHT = 420

	def __init__(self, parent: tk.Widget, product_data: Dict, batch_data: Optional[List[Dict]]):
		self.parent = parent
		# Do not modify inputs
		self._product = dict(product_data)
		# allow None for batch_data -> treat as empty list
		self._batches = [dict(b) for b in (batch_data or [])]

		self.result: Optional[Dict] = None

		self._root = tk.Toplevel(parent)
		self._root.withdraw()
		self._root.transient(parent)
		self._root.configure(bg="#FFFFFF")
		self._root.resizable(False, False)
		self._root.title("Edit Item")

		self._create_styles()
		self._create_ui()
		self._bind_events()

		self._selected_batch = None

	def _create_styles(self):
		style = ttk.Style(self._root)
		# Use default theme but tweak some styles
		try:
			style.theme_use('clam')
		except Exception:
			pass
		style.configure('Primary.TButton', background='#3B82F6', foreground='#FFFFFF')
		style.map('Primary.TButton', background=[('active', '#2563EB')])

	def _create_ui(self):
		pad = 12
		frm = ttk.Frame(self._root, padding=pad)
		frm.pack(fill='both', expand=True)

		# Top section: product name and MRP
		top = ttk.Frame(frm)
		top.pack(fill='x')

		product_name = self._product.get('name', 'Unnamed Product')
		name_lbl = ttk.Label(top, text=product_name, font=('Segoe UI', 14, 'bold'), foreground='#111827')
		name_lbl.pack(anchor='w')

		mrp_val = self._product.get('mrp', 0.0)
		mrp_frame = ttk.Frame(top)
		mrp_frame.pack(fill='x', pady=(6, 12))
		ttk.Label(mrp_frame, text='MRP:', foreground='#111827').pack(side='left')
		self._mrp_display = ttk.Label(mrp_frame, text=f'₹ {mrp_val:.2f}', foreground='#111827')
		self._mrp_display.pack(side='left', padx=(6,))

		# Middle section: discount price and quantity
		mid = ttk.Frame(frm)
		mid.pack(fill='x', pady=(0, 12))

		# Discount price with ₹ prefix
		dp_frame = ttk.Frame(mid)
		dp_frame.pack(fill='x', pady=(0, 8))
		ttk.Label(dp_frame, text='Discount Price:', foreground='#111827').pack(anchor='w')
		entry_frame = ttk.Frame(dp_frame)
		entry_frame.pack(anchor='w', pady=(6, 0))
		tk.Label(entry_frame, text='₹', bg='#FFFFFF', fg='#111827').pack(side='left')
		self._discount_var = tk.StringVar(value=f"{self._product.get('discount_price', 0.0):.2f}")
		self._discount_entry = ttk.Entry(entry_frame, textvariable=self._discount_var, width=12)
		self._discount_entry.pack(side='left', padx=(6, 0))

		# Quantity with - and + buttons
		qty_frame = ttk.Frame(mid)
		qty_frame.pack(fill='x')
		ttk.Label(qty_frame, text='Quantity:', foreground='#111827').pack(side='left')
		btn_frame = ttk.Frame(qty_frame)
		btn_frame.pack(side='left', padx=(8, 0))

		self._qty_var = tk.IntVar(value=max(1, int(self._product.get('quantity', 1))))
		minus = ttk.Button(btn_frame, text='-', width=3, command=self._decrease_qty)
		minus.pack(side='left')
		self._qty_entry = ttk.Entry(btn_frame, textvariable=self._qty_var, width=6, justify='center')
		self._qty_entry.pack(side='left', padx=(6, 6))
		plus = ttk.Button(btn_frame, text='+', width=3, command=self._increase_qty)
		plus.pack(side='left')

		# Separator
		sep = ttk.Separator(frm, orient='horizontal')
		sep.pack(fill='x', pady=8)

		# Bottom: Treeview table for batches
		table_frame = ttk.Frame(frm)
		table_frame.pack(fill='both', expand=True)

		cols = ('batch_id', 'stock', 'mrp', 'discount')
		self._tree = ttk.Treeview(table_frame, columns=cols, show='headings', selectmode='browse', height=6)
		self._tree.heading('batch_id', text='Batch ID')
		self._tree.heading('stock', text='Stock Count')
		self._tree.heading('mrp', text='MRP')
		self._tree.heading('discount', text='Discount Price')
		self._tree.column('batch_id', width=140, anchor='center')
		self._tree.column('stock', width=100, anchor='center')
		self._tree.column('mrp', width=100, anchor='center')
		self._tree.column('discount', width=120, anchor='center')
		self._tree.pack(fill='both', expand=True)

		# populate
		for b in self._batches:
			self._tree.insert('', 'end', values=(b.get('batch_id', ''), b.get('stock', 0), f"₹ {b.get('mrp', 0.0):.2f}", f"₹ {b.get('discount_price', 0.0):.2f}"))

		# Bottom buttons
		btns = ttk.Frame(frm)
		btns.pack(fill='x', pady=(12, 0))
		self._cancel_btn = ttk.Button(btns, text='Cancel', command=self._on_cancel)
		self._cancel_btn.pack(side='right', padx=(6, 0))
		self._apply_btn = ttk.Button(btns, text='Apply', style='Primary.TButton', command=self._on_apply)
		self._apply_btn.pack(side='right')

	def _bind_events(self):
		self._tree.bind('<<TreeviewSelect>>', self._on_row_select)
		self._root.bind('<Return>', lambda e: self._on_apply())
		self._root.bind('<Escape>', lambda e: self._on_cancel())

		# When shown, focus discount entry and select all
		self._root.bind('<Map>', lambda e: self._focus_discount())

	def _focus_discount(self):
		try:
			self._discount_entry.focus_set()
			self._discount_entry.selection_range(0, 'end')
		except Exception:
			pass

	def _on_row_select(self, event=None):
		sel = self._tree.selection()
		if not sel:
			return
		vals = self._tree.item(sel[0], 'values')
		# vals: batch_id, stock, mrp, discount
		batch_id = vals[0]
		# find batch dict
		batch = next((b for b in self._batches if str(b.get('batch_id')) == str(batch_id)), None)
		if not batch:
			return
		# autofill discount price and optionally mrp
		self._discount_var.set(f"{batch.get('discount_price', batch.get('mrp', 0.0)):.2f}")
		# optionally update mrp display
		self._mrp_display.config(text=f"₹ {batch.get('mrp', self._product.get('mrp', 0.0)):.2f}")
		self._selected_batch = dict(batch)

	def _decrease_qty(self):
		v = max(1, self._qty_var.get() - 1)
		self._qty_var.set(v)

	def _increase_qty(self):
		v = max(1, self._qty_var.get() + 1)
		self._qty_var.set(v)

	def _validate(self) -> bool:
		# Quantity >= 1
		try:
			qty = int(self._qty_var.get())
		except Exception:
			messagebox.showerror('Validation', 'Quantity must be an integer >= 1', parent=self._root)
			return False
		if qty < 1:
			messagebox.showerror('Validation', 'Quantity must be at least 1', parent=self._root)
			return False

		# Discount price <= MRP
		try:
			dp = float(self._discount_var.get())
		except Exception:
			messagebox.showerror('Validation', 'Discount price must be a number', parent=self._root)
			return False
		# current mrp display text may include ₹
		mrp_text = self._mrp_display.cget('text').replace('₹', '').strip()
		try:
			mrp = float(mrp_text)
		except Exception:
			mrp = float(self._product.get('mrp', 0.0))

		if dp > mrp:
			messagebox.showerror('Validation', 'Discount price cannot be greater than MRP', parent=self._root)
			return False

		return True

	def _on_apply(self):
		if not self._validate():
			return
		quantity = int(self._qty_var.get())
		discount_price = float(self._discount_var.get())
		selected = dict(self._selected_batch) if self._selected_batch is not None else None
		self.result = {
			'quantity': quantity,
			'discount_price': discount_price,
			'selected_batch': selected,
		}
		self._root.destroy()

	def _on_cancel(self):
		self.result = None
		self._root.destroy()

	def _center_window(self):
		self._root.update_idletasks()
		w = self.WIDTH
		h = self.HEIGHT
		ws = self._root.winfo_screenwidth()
		hs = self._root.winfo_screenheight()
		x = (ws // 2) - (w // 2)
		y = (hs // 2) - (h // 2)
		self._root.geometry(f'{w}x{h}+{x}+{y}')

	def show(self) -> Optional[Dict]:
		"""Display the modal popup and return result or None."""
		self._center_window()
		self._root.deiconify()
		self._root.grab_set()
		self._root.wait_window()
		return self.result


def open_edit_popup(parent: tk.Widget, product_data: Dict, batch_data: Optional[List[Dict]]) -> Optional[Dict]:
	"""Convenience function to open EditItemPopup as a modal and return the result.

	Example:
		result = open_edit_popup(root, product_data, batch_data)
	"""
	popup = SettingItemPopup(parent, product_data, batch_data)
	return popup.show()


if __name__ == '__main__':
	# Small example demonstrating usage
	root = tk.Tk()
	root.geometry('800x600')
	sample_product = {
		'id': 1,
		'name': 'Organic Almonds 1kg',
		'mrp': 799.00,
		'quantity': 2,
		'discount_price': 699.00,
	}
	sample_batches = [
		{'batch_id': 'BATCH-001', 'stock': 12, 'mrp': 799.0, 'discount_price': 699.0},
		{'batch_id': 'BATCH-002', 'stock': 5, 'mrp': 749.0, 'discount_price': 649.0},
	]

	def open_and_print():
		res = open_edit_popup(root, sample_product, sample_batches)
		print('Popup result:', res)

	ttk.Button(root, text='Open Edit Popup', command=open_and_print).pack(pady=40)
	root.mainloop()

