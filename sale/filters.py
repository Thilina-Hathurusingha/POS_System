"""
Filters Panel - Top left section with category, vendor dropdowns and search.
"""

import tkinter as tk
from tkinter import ttk
from logging_config import get_logger

logger = get_logger(__name__)


class FilterPanel(tk.Frame):
    """Panel for filtering products by category, vendor, and search"""

    # UI Constants
    FONT_NORMAL = ("Segoe UI", 11, "normal")
    FONT_LABEL = ("Segoe UI", 10, "normal")
    
    # Colors
    BG_MAIN = "#EEF2F6"
    BG_PANEL = "#FFFFFF"
    BORDER_COLOR = "#E5E7EB"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"

    def __init__(self, parent, on_filter_change=None, **kwargs):
        """
        Initialize FilterPanel.
        
        Args:
            parent: Parent widget
            on_filter_change: Callback when filters change
        """
        logger.debug("ENTRY: FilterPanel.__init__()")
        
        if 'bg' not in kwargs:
            kwargs['bg'] = self.BG_PANEL
        super().__init__(parent, **kwargs)
        
        self.on_filter_change = on_filter_change
        self.categories = []
        self.vendors = []
        
        try:
            self._create_ui()
            logger.debug("EXIT: FilterPanel.__init__() - Success")
        except Exception as e:
            logger.error(f"Failed to initialize FilterPanel: {str(e)}", exc_info=True)
            raise

    def _create_ui(self):
        """Create UI components"""
        # ========== Main Container ==========
        # Container frame for all filter controls
        container = tk.Frame(self, bg=self.BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # ========== Row 1: Dropdowns + Action Buttons ==========
        # Frame for filter dropdowns and buttons
        row1 = tk.Frame(container, bg=self.BG_PANEL)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # ========== Category Dropdown ==========
        # Filter products by product category
        self._create_dropdown_with_label(
            row1,
            "Category:",
            variable_name="category_var",
            on_change=self._on_filter_change  # Trigger filtering when changed
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # ========== Vendor Dropdown ==========
        # Filter products by vendor/supplier
        self._create_dropdown_with_label(
            row1,
            "Vendor:",
            variable_name="vendor_var",
            on_change=self._on_filter_change  # Trigger filtering when changed
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # ========== Action Buttons ==========
        # Placeholder buttons for additional features (3 buttons)
        for i in range(3):
            btn = tk.Button(
                row1,
                text=f"[Btn {i+1}]",
                font=self.FONT_NORMAL,
                bg=self.BG_MAIN,
                fg=self.TEXT_SECONDARY,
                relief=tk.FLAT,
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=4)
        
        # ========== Row 2: Search Bar ==========
        # Frame for product search functionality
        row2 = tk.Frame(container, bg=self.BG_PANEL)
        row2.pack(fill=tk.X)
        
        # Search label
        search_label = tk.Label(row2, text="Search:", font=self.FONT_LABEL, bg=self.BG_PANEL, fg=self.TEXT_PRIMARY)
        search_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # ========== Search Entry Field ==========
        # Variable to track search text and trigger filtering on change
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_filter_change())  # Fire event on text change
        
        search_entry = tk.Entry(
            row2,
            textvariable=self.search_var,
            font=self.FONT_NORMAL,
            bg=self.BG_MAIN,
            fg=self.TEXT_PRIMARY,
            relief=tk.FLAT,
            border=1
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Insert placeholder text
        search_entry.insert(0, "Search...")
        # Bind focus events to show/hide placeholder
        search_entry.bind("<FocusIn>", lambda e: self._on_search_focus_in(search_entry))
        search_entry.bind("<FocusOut>", lambda e: self._on_search_focus_out(search_entry))

    def _create_dropdown_with_label(self, parent, label_text, variable_name, on_change=None):
        """
        Create a labeled dropdown.
        
        Args:
            parent: Parent widget
            label_text: Label text
            variable_name: Variable attribute name
            on_change: Callback function
            
        Returns:
            Frame containing label and dropdown
        """
        # ========== Create Container Frame ==========
        # Frame to hold label and dropdown side by side
        frame = tk.Frame(parent, bg=parent["bg"])
        
        # ========== Create Label ==========
        # Label describing what the dropdown filters
        label = tk.Label(frame, text=label_text, font=self.FONT_LABEL, bg=parent["bg"], fg=self.TEXT_PRIMARY)
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        # ========== Create StringVar for Dropdown ==========
        # Variable to store selected dropdown value
        var = tk.StringVar()
        setattr(self, variable_name, var)  # Store as instance attribute
        
        # ========== Create Dropdown (Combobox) ==========
        # Dropdown with read-only state (user can only select from predefined options)
        dropdown = ttk.Combobox(
            frame,
            textvariable=var,
            values=[],  # Will be populated when categories/vendors are loaded
            state="readonly",  # Prevent manual typing
            font=self.FONT_NORMAL,
            width=15
        )
        dropdown.pack(side=tk.LEFT)
        dropdown.set("Loading...")  # Show loading status initially
        
        # ========== Bind Change Event ==========
        # Trigger callback when user selects a different option
        if on_change:
            var.trace("w", lambda *args: on_change())
        
        # Store dropdown reference for later updates
        setattr(self, f"{variable_name}_dropdown", dropdown)
        return frame

    def _on_search_focus_in(self, entry):
        """Handle search entry focus in"""
        if entry.get() == "Search...":
            entry.delete(0, tk.END)
            entry.config(fg=self.TEXT_PRIMARY)

    def _on_search_focus_out(self, entry):
        """Handle search entry focus out"""
        if entry.get() == "":
            entry.insert(0, "Search...")
            entry.config(fg=self.TEXT_SECONDARY)

    def _on_filter_change(self):
        """Callback when any filter changes"""
        if self.on_filter_change:
            filters = {
                "category": getattr(self, "category_var").get() if hasattr(self, "category_var") else None,
                "vendor": getattr(self, "vendor_var").get() if hasattr(self, "vendor_var") else None,
                "search": self.search_var.get() if self.search_var.get() != "Search..." else "",
            }
            self.on_filter_change(filters)

    def update_categories(self, categories):
        """Update category dropdown options"""
        self.categories = categories
        if hasattr(self, "category_var_dropdown"):
            values = ["All Categories"] + categories
            self.category_var_dropdown["values"] = values
            self.category_var_dropdown.set("All Categories")

    def update_vendors(self, vendors):
        """Update vendor dropdown options"""
        self.vendors = vendors
        if hasattr(self, "vendor_var_dropdown"):
            values = ["All Vendors"] + vendors
            self.vendor_var_dropdown["values"] = values
            self.vendor_var_dropdown.set("All Vendors")
