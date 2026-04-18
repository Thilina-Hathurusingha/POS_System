"""
Filters Panel - Top left section with category, vendor dropdowns and search.
"""

import tkinter as tk
from tkinter import ttk
from log.logging_config import get_logger

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
        
        # ========== ID Mappings for Dropdowns ==========
        # Maps display_name -> unique_id for reverse lookup
        self.category_id_map = {}  # Maps display_name -> category_id
        self.vendor_id_map = {}    # Maps display_name -> vendor_id
        
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
            map_name="category_id_map",
            on_change=self._on_filter_change  # Trigger filtering when changed
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # ========== Vendor Dropdown ==========
        # Filter products by vendor/supplier
        self._create_dropdown_with_label(
            row1,
            "Vendor:",
            variable_name="vendor_var",
            map_name="vendor_id_map",
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

    def _create_dropdown_with_label(self, parent, label_text, variable_name, map_name, on_change=None):
        """
        Create a labeled dropdown with ID mapping support.
        
        Args:
            parent: Parent widget
            label_text: Label text
            variable_name: Variable attribute name (e.g., "category_var")
            map_name: ID map attribute name (e.g., "category_id_map")
            on_change: Callback function when selection changes
            
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
        
        # ========== Store References ==========
        # Store dropdown reference and map name for later updates
        setattr(self, f"{variable_name}_dropdown", dropdown)
        setattr(self, f"{variable_name}_map_name", map_name)
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

    def _get_selected_id_and_name(self, variable_name, map_name):
        """
        Get the unique ID and display name for the currently selected dropdown option.
        
        Args:
            variable_name: The StringVar attribute name (e.g., "category_var")
            map_name: The ID map attribute name (e.g., "category_id_map")
            
        Returns:
            dict: {'id': unique_id, 'name': display_name} or None if nothing selected
        """
        if not hasattr(self, variable_name):
            return None
        
        display_name = getattr(self, variable_name).get()
        if not display_name or display_name == "Loading...":
            return None
        
        # Get the ID mapping dictionary
        id_map = getattr(self, map_name, {})
        
        # Look up the ID by display name
        if display_name in id_map:
            return {
                'id': id_map[display_name],
                'name': display_name
            }
        
        return None

    def _on_filter_change(self):
        """Callback when any filter changes"""
        if self.on_filter_change:
            # Get category selection with ID
            category_selection = self._get_selected_id_and_name("category_var", "category_id_map")
            
            # Get vendor selection with ID
            vendor_selection = self._get_selected_id_and_name("vendor_var", "vendor_id_map")
            
            filters = {
                "category": category_selection,  # Now contains {'id': ..., 'name': ...} or None
                "vendor": vendor_selection,      # Now contains {'id': ..., 'name': ...} or None
                "search": self.search_var.get() if self.search_var.get() != "Search..." else "",
            }
            self.on_filter_change(filters)

    def update_categories(self, categories):
        """
        Update category dropdown options.
        
        Args:
            categories: List of category objects with 'id' and 'name' attributes
        """
        self.categories = categories
        
        if hasattr(self, "category_var_dropdown"):
            # Clear existing mapping
            self.category_id_map = {}
            
            # Add "All Categories" option with ID 0
            display_values = ["All Categories"]
            self.category_id_map["All Categories"] = None
            
            # Add category options with their IDs
            for cat in categories:
                display_name = cat.name
                display_values.append(display_name)
                self.category_id_map[display_name] = cat.id
            
            # Update dropdown
            self.category_var_dropdown["values"] = display_values
            self.category_var_dropdown.set("All Categories")
            
            logger.debug(f"Updated categories dropdown with {len(categories)} options. ID Map: {self.category_id_map}")

    def update_vendors(self, vendors):
        """
        Update vendor dropdown options.
        
        Args:
            vendors: List of vendor objects with 'id' and 'name' attributes
        """
        self.vendors = vendors
        
        if hasattr(self, "vendor_var_dropdown"):
            # Clear existing mapping
            self.vendor_id_map = {}
            
            # Add "All Vendors" option with ID 0
            display_values = ["All Vendors"]
            self.vendor_id_map["All Vendors"] = None
            
            # Add vendor options with their IDs
            for vendor in vendors:
                display_name = vendor.name
                display_values.append(display_name)
                self.vendor_id_map[display_name] = vendor.id
            
            # Update dropdown
            self.vendor_var_dropdown["values"] = display_values
            self.vendor_var_dropdown.set("All Vendors")
            
            logger.debug(f"Updated vendors dropdown with {len(vendors)} options. ID Map: {self.vendor_id_map}")
