"""
Main Application - Root window, menu bar, and page management for POS system.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import queue
from data_processor import DataProcessor
from sale_page import SalePage


class MainApp(tk.Tk):
    """Main application window"""

    # UI Constants
    FONT_MENU = ("Segoe UI", 11, "normal")
    FONT_MENU_ACTIVE = ("Segoe UI", 11, "bold")
    
    # Colors
    BG_MAIN = "#EEF2F6"
    BG_MENU = "#FFFFFF"
    BORDER_COLOR = "#E5E7EB"
    TEXT_PRIMARY = "#111827"
    PRIMARY_BLUE = "#3B82F6"

    def __init__(self):
        """Initialize MainApp"""
        super().__init__()
        
        # ========== Window Configuration ==========
        # Set window title and maximize to fill screen
        self.title("POS System")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.resizable(True, True)
        self.config(bg=self.BG_MAIN)  # Set background color
        self.state('zoomed')  # Maximize window on startup
        
        # ========== Background Thread for Data Processing ==========
        # Create a queue to communicate between the background thread and GUI thread
        # This prevents blocking the UI while processing data
        self.gui_queue = queue.Queue()
        self.data_processor = DataProcessor(self.gui_queue)  # Create background worker thread
        self.data_processor.start()  # Start the background thread
        
        # ========== Application State ==========
        # Track current page and store all page widgets
        self.current_page = "sale"  # Default page is sale
        self.pages = {}  # Dictionary to store page widgets
        
        # ========== Create UI Components ==========
        self._create_menu_bar()  # Create top navigation menu
        self._create_pages()  # Create all page panels
        self._show_page("sale")  # Display sale page by default
        
        # ========== Background Tasks ==========
        # Schedule periodic checking of data queue (every 1000ms)
        # This allows receiving updates from background thread
        self.after(1000, self._check_data_queue)
        
        # Register callback for window close event
        # This ensures proper cleanup when user closes the application
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu_bar(self):
        """Create top menu bar"""
        # ========== Main Menu Container ==========
        # Create menu bar frame with white background and fixed height
        menu_frame = tk.Frame(self, bg=self.BG_MENU, height=50)
        menu_frame.pack(fill=tk.X, side=tk.TOP)
        menu_frame.pack_propagate(False)  # Prevent height from shrinking
        
        # Add subtle bottom border to separate menu from content
        border = tk.Frame(menu_frame, bg=self.BORDER_COLOR, height=1)
        border.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Container for menu item buttons
        items_frame = tk.Frame(menu_frame, bg=self.BG_MENU)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=0)
        
        # ========== Define Menu Items ==========
        # List of (display_label, page_identifier) tuples
        menu_items = [
            ("Sale", "sale"),          # Main sales interface
            ("Inventory", "inventory"),  # Inventory management
            ("Reports", "reports"),    # Sales reports and analytics
            ("Settings", "settings")   # Application settings
        ]
        
        # ========== Create Menu Buttons ==========
        # Store buttons in dict for later reference (e.g., for highlighting active page)
        self.menu_buttons = {}
        for label, page_name in menu_items:
            btn = tk.Button(
                items_frame,
                text=label,
                font=self.FONT_MENU,
                bg=self.BG_MENU,
                fg=self.TEXT_PRIMARY,
                relief=tk.FLAT,  # Flat style for modern look
                padx=20,
                pady=15,
                cursor="hand2",
                command=lambda pn=page_name: self._show_page(pn)  # Switch page on click
            )
            btn.pack(side=tk.LEFT)  # Place buttons horizontally
            self.menu_buttons[page_name] = btn  # Store reference to button
        
        # Highlight the currently active menu item
        self._update_menu_highlight()

    def _create_pages(self):
        """Create all pages"""
        # Main container for pages
        self.pages_container = tk.Frame(self, bg=self.BG_MAIN)
        self.pages_container.pack(fill=tk.BOTH, expand=True)
        
        # Sale page
        sale_page = SalePage(self.pages_container, data_processor=self.data_processor, name="sale")
        self.pages["sale"] = sale_page
        
        # Placeholder pages for other menu items
        for page_name in ["inventory", "reports", "settings"]:
            page = tk.Frame(self.pages_container, bg=self.BG_MAIN)
            label = tk.Label(
                page,
                text=f"{page_name.capitalize()} Page",
                font=("Segoe UI", 16, "bold"),
                bg=self.BG_MAIN,
                fg="#6B7280"
            )
            label.pack(pady=100)
            self.pages[page_name] = page

    def _show_page(self, page_name):
        """Show specific page"""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name
            self._update_menu_highlight()

    def _update_menu_highlight(self):
        """Update menu button highlighting"""
        for page_name, btn in self.menu_buttons.items():
            if page_name == self.current_page:
                btn.config(
                    bg=self.PRIMARY_BLUE,
                    fg="white",
                    font=self.FONT_MENU_ACTIVE
                )
            else:
                btn.config(
                    bg=self.BG_MENU,
                    fg=self.TEXT_PRIMARY,
                    font=self.FONT_MENU
                )

    def _check_data_queue(self):
        """Check for data from data processor"""
        try:
            while True:
                message = self.gui_queue.get_nowait()
                # Handle messages from data processor if needed
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(1000, self._check_data_queue)

    def _on_closing(self):
        """Handle window close"""
        self.data_processor.stop()
        self.destroy()


def main():
    """Main entry point"""
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
