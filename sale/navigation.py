"""
Navigation Panel - Bottom left section with pagination controls.
"""

import tkinter as tk


class NavigationPanel(tk.Frame):
    """Panel for pagination controls"""

    # UI Constants
    FONT_NORMAL = ("Segoe UI", 11, "normal")
    FONT_PAGE = ("Segoe UI", 10, "bold")
    
    # Colors
    BG_PANEL = "#FFFFFF"
    PRIMARY_BLUE = "#3B82F6"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#6B7280"
    BG_BUTTON = "#F3F4F6"

    def __init__(self, parent, on_page_change=None, **kwargs):
        """
        Initialize NavigationPanel.
        
        Args:
            parent: Parent widget
            on_page_change: Callback when page changes
        """
        if 'bg' not in kwargs:
            kwargs['bg'] = self.BG_PANEL
        super().__init__(parent, **kwargs)
        
        # ========== Store Callback ==========
        # Called whenever user navigates to a different page
        self.on_page_change = on_page_change
        
        # ========== Pagination State ==========
        # Track current page number (1-indexed)
        self.current_page = 1
        # Total number of pages available
        self.total_pages = 1
        # List of page number button widgets
        self.page_buttons = []
        
        # ========== Create UI ==========
        # Build pagination controls (first, prev, page numbers, next, last)
        self._create_ui()

    def _create_ui(self):
        """Create pagination UI"""
        # ========== Main Container ==========
        # Frame to hold all pagination controls
        container = tk.Frame(self, bg=self.BG_PANEL)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # ========== Pagination Controls Frame ==========
        # Left-aligned controls for navigation
        controls_frame = tk.Frame(container, bg=self.BG_PANEL)
        controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ========== First Page Button ==========
        # Navigate to the first page (|<)
        self.btn_first = self._create_nav_button(
            controls_frame,
            "« First",
            lambda: self._go_to_page(1)  # Go to page 1
        )
        self.btn_first.pack(side=tk.LEFT, padx=2)
        
        # ========== Previous Page Button ==========
        # Navigate to previous page (<)
        self.btn_prev = self._create_nav_button(
            controls_frame,
            "‹ Prev",
            lambda: self._go_to_page(self.current_page - 1)  # Go back one page
        )
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        
        # ========== Page Numbers Container ==========
        # Frame to hold individual page number buttons
        self.pages_frame = tk.Frame(controls_frame, bg=self.BG_PANEL)
        self.pages_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        # ========== Next Page Button ==========
        # Navigate to next page (>)
        self.btn_next = self._create_nav_button(
            controls_frame,
            "Next ›",
            lambda: self._go_to_page(self.current_page + 1)  # Go forward one page
        )
        self.btn_next.pack(side=tk.LEFT, padx=2)
        
        # ========== Last Page Button ==========
        # Navigate to the last page (>|)
        self.btn_last = self._create_nav_button(
            controls_frame,
            "Last »",
            lambda: self._go_to_page(self.total_pages)  # Go to last page
        )
        self.btn_last.pack(side=tk.LEFT, padx=2)
        
        # ========== Information Label ==========
        # Right-aligned label showing current page and total pages (e.g., "Page 1 of 5")
        self.info_label = tk.Label(
            container,
            text="Page 1 of 1",
            font=self.FONT_NORMAL,
            bg=self.BG_PANEL,
            fg=self.TEXT_SECONDARY
        )
        self.info_label.pack(side=tk.RIGHT)

    def _create_nav_button(self, parent, text, command):
        """
        Create a navigation button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            
        Returns:
            Button widget
        """
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.FONT_NORMAL,
            bg=self.BG_BUTTON,
            fg=self.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        return btn

    def _create_page_button(self, parent, page_num):
        """
        Create a page number button.
        
        Args:
            parent: Parent widget
            page_num: Page number
            
        Returns:
            Button widget
        """
        is_current = page_num == self.current_page
        
        btn = tk.Button(
            parent,
            text=str(page_num),
            command=lambda: self._go_to_page(page_num),
            font=self.FONT_PAGE,
            bg=self.PRIMARY_BLUE if is_current else self.BG_BUTTON,
            fg="white" if is_current else self.TEXT_PRIMARY,
            relief=tk.FLAT,
            width=3,
            padx=4,
            pady=4,
            cursor="hand2"
        )
        return btn

    def _go_to_page(self, page_num):
        """Go to specific page"""
        if 1 <= page_num <= self.total_pages and page_num != self.current_page:
            self.current_page = page_num
            self.update_pagination()
            
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def update_pagination(self, total_pages=None):
        """
        Update pagination display.
        
        Args:
            total_pages: Total number of pages (optional)
        """
        if total_pages is not None:
            self.total_pages = total_pages
        
        # Clear page buttons
        for btn in self.page_buttons:
            btn.destroy()
        self.page_buttons.clear()
        
        # Create page number buttons
        start_page = max(1, self.current_page - 1)
        end_page = min(self.total_pages, self.current_page + 1)
        
        for page_num in range(start_page, end_page + 1):
            btn = self._create_page_button(self.pages_frame, page_num)
            btn.pack(side=tk.LEFT, padx=2)
            self.page_buttons.append(btn)
        
        # Update button states
        self.btn_first.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.btn_prev.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
        self.btn_last.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
        
        # Update info label
        self.info_label.config(text=f"Page {self.current_page} of {self.total_pages}")

    def set_page_info(self, current_page, total_pages):
        """Set page information"""
        self.current_page = current_page
        self.total_pages = total_pages
        self.update_pagination(total_pages)
