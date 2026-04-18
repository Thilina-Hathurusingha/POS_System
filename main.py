"""
Main Application - Root window, menu bar, and page management for POS system.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import queue
import uuid
from proessing.data_processor import DataProcessor
from sale.sale_page import SalePage
from log.logging_config import AppLogger, get_logger
import shared.resource as resource

# ========== Initialize Logging ==========
# Setup logging with default ERROR level
# Can be changed via AppLogger.set_level() or configured at startup
logger = get_logger(__name__)


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
        logger.debug("=" * 50)
        logger.debug("ENTRY: MainApp.__init__()")
        
        super().__init__()
        
        try:
            # ========== Window Configuration ==========
            # Set window title and maximize to fill screen
            logger.debug("Configuring window properties...")
            self.title("POS System")
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
            self.resizable(True, True)
            self.config(bg=self.BG_MAIN)  # Set background color
            self.state('zoomed')  # Maximize window on startup
            logger.debug(f"Window initialized: {self.winfo_screenwidth()}x{self.winfo_screenheight()}")
            
            # ========== Background Thread for Data Processing ==========
            # Use shared event_queue from resource.py for communication between threads
            # This allows both GUI and data processor to access the same queue
            logger.debug("Setting up data processor thread...")
            # Pass callback to signal GUI when responses are ready
            self.data_processor = DataProcessor(gui_callback=self._on_data_available)
            self.data_processor.start()  # Start the background thread
            logger.debug("Data processor thread started successfully")
            
            # ========== Application State ==========
            # Track current page and store all page widgets
            self.current_page = "sale"  # Default page is sale
            self.pages = {}  # Dictionary to store page widgets
            logger.debug("Application state initialized")
            
            # ========== Create UI Components ==========
            logger.debug("Creating menu bar...")
            self._create_menu_bar()  # Create top navigation menu
            logger.debug("Menu bar created")
            
            logger.debug("Creating pages...")
            self._create_pages()  # Create all page panels
            logger.debug("Pages created")
            
            logger.debug("Displaying sale page...")
            self._show_page("sale")  # Display sale page by default
            logger.debug("Sale page displayed")
            
            # ========== Background Tasks ==========
            # Schedule periodic checking of data queue (every 500ms)
            # With thread-safe callback, latency is much lower
            # Less frequent polling is needed since thread signals immediately
            logger.debug("Scheduling data queue checks...")
            self.after(500, self._check_data_queue)
            logger.debug("Data queue checks scheduled")
            
            # Register callback for window close event
            # This ensures proper cleanup when user closes the application
            self.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            logger.debug("EXIT: MainApp.__init__() - Initialization successful")
            logger.info("POS System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MainApp: {str(e)}", exc_info=True)
            raise

    def _create_menu_bar(self):
        """Create top menu bar"""
        logger.debug("ENTRY: MainApp._create_menu_bar()")
        
        try:
            # ========== Main Menu Container ==========
            # Create menu bar frame with white background and fixed height
            logger.debug("Creating menu bar frame...")
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
            logger.debug(f"Creating {len(menu_items)} menu buttons...")
            self.menu_buttons = {}
            for label, page_name in menu_items:
                logger.debug(f"  Creating button: {label} -> {page_name}")
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
            logger.debug("Updating menu highlight...")
            self._update_menu_highlight()
            
            logger.debug("EXIT: MainApp._create_menu_bar() - Success")
            
        except Exception as e:
            logger.error(f"Failed to create menu bar: {str(e)}", exc_info=True)
            raise

    def _create_pages(self):
        """Create all pages"""
        logger.debug("ENTRY: MainApp._create_pages()")
        
        try:
            # Main container for pages
            logger.debug("Creating pages container...")
            self.pages_container = tk.Frame(self, bg=self.BG_MAIN)
            self.pages_container.pack(fill=tk.BOTH, expand=True)
            
            # Sale page
            logger.debug("Creating Sale page...")
            sale_page = SalePage(self.pages_container, data_processor=self.data_processor, name="sale")
            self.pages["sale"] = sale_page
            logger.debug("Sale page created successfully")
            
            # Placeholder pages for other menu items
            placeholder_pages = ["inventory", "reports", "settings"]
            logger.debug(f"Creating {len(placeholder_pages)} placeholder pages...")
            for page_name in placeholder_pages:
                logger.debug(f"  Creating placeholder: {page_name}")
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
            
            logger.debug(f"EXIT: MainApp._create_pages() - Created {len(self.pages)} pages")
            
        except Exception as e:
            logger.error(f"Failed to create pages: {str(e)}", exc_info=True)
            raise

    def _show_page(self, page_name):
        """Show specific page"""
        logger.debug(f"ENTRY: MainApp._show_page(page_name={page_name})")
        
        try:
            if page_name not in self.pages:
                logger.warning(f"Requested page '{page_name}' not found. Available pages: {list(self.pages.keys())}")
                return
            
            logger.debug(f"Hiding previous page: {self.current_page}")
            # Hide all pages
            for page in self.pages.values():
                page.pack_forget()
            
            # Show selected page
            logger.debug(f"Displaying page: {page_name}")
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name
            self._update_menu_highlight()
            
            logger.debug(f"EXIT: MainApp._show_page() - Page '{page_name}' displayed")
            
        except Exception as e:
            logger.error(f"Failed to show page '{page_name}': {str(e)}", exc_info=True)

    def _update_menu_highlight(self):
        """Update menu button highlighting"""
        logger.debug(f"ENTRY: MainApp._update_menu_highlight()")
        
        try:
            logger.debug(f"Updating highlight for current page: {self.current_page}")
            for page_name, btn in self.menu_buttons.items():
                if page_name == self.current_page:
                    logger.debug(f"  Highlighting button: {page_name}")
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
            
            logger.debug(f"EXIT: MainApp._update_menu_highlight()")
            
        except Exception as e:
            logger.error(f"Failed to update menu highlight: {str(e)}", exc_info=True)

    def _on_data_available(self):
        """Called by worker thread when new data is available (thread-safe callback)"""
        logger.debug("ENTRY: MainApp._on_data_available()")
        
        try:
            # Schedule the check on the GUI thread using self.after()
            # This is thread-safe and wakes up GUI immediately
            logger.debug("Data available signal received - scheduling queue check on GUI thread")
            self.after(0, self._check_data_queue_immediate)
        except Exception as e:
            logger.error(f"Error in _on_data_available: {str(e)}", exc_info=True)
        
        logger.debug("EXIT: MainApp._on_data_available()")

    def send_request_to_processor(self, action, request_data=None):
        """
        Send a request to data processor and get response via event_queue.
        GUI puts request in queue and signals the processor thread.
        
        Args:
            action: Action to perform (e.g., 'get_products_page', 'filter_products')
            request_data: Additional data for the request
            
        Returns:
            Request ID that can be used to match responses
        """
        logger.debug(f"ENTRY: MainApp.send_request_to_processor(action={action})")
        
        try:
            request_id = str(uuid.uuid4())
            
            request = {
                'type': 'gui_request',
                'action': action,
                'request_id': request_id,
                **(request_data or {})
            }
            
            logger.debug(f"Putting request in queue: action={action}, request_id={request_id}")
            resource.GUI_event_queue.put(request)
            
            
            logger.debug(f"EXIT: MainApp.send_request_to_processor() - request_id={request_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to send request: {str(e)}", exc_info=True)
            return None

    def _check_data_queue_immediate(self):
        """Check queue immediately (called from signal or polling)"""
        logger.debug("ENTRY: MainApp._check_data_queue_immediate()")
        
        try:
            processed_count = 0
            while True:
                message = resource.background_event_queue.get_nowait()
                
                if message.get('type') == 'response':
                    logger.debug(f"Received response from data processor: action={message.get('action')}, status={message.get('status')}")
                    request_id = message.get('request_id')
                    action = message.get('action')
                    status = message.get('status')
                    
                    if status == 'success':
                        logger.debug(f"Response successful for request {request_id}: {action}")
                        # Handle response data based on action
                        self._handle_processor_response(action, request_id, message)
                    else:
                        logger.warning(f"Response error for request {request_id}: {message.get('error')}")
                
                else:
                    logger.debug(f"Received message from data processor: {message.get('type', 'unknown')}")
                
                processed_count += 1
                
        except queue.Empty:
            if processed_count > 0:
                logger.debug(f"Processed {processed_count} messages from queue")
        except Exception as e:
            logger.error(f"Error checking data queue: {str(e)}", exc_info=True)
        
        logger.debug("EXIT: MainApp._check_data_queue_immediate()")

    def _handle_processor_response(self, action, request_id, response):
        """
        Handle response from data processor based on action.
        
        Args:
            action: The action that was requested
            request_id: ID of the original request
            response: Response message from processor
        """
        logger.debug(f"ENTRY: MainApp._handle_processor_response(action={action}, request_id={request_id})")
        
        try:
            if action == 'refresh_products_page':
                logger.debug(f"Handling products page response for request {request_id}")
                # Store response for pages to retrieve
                if not hasattr(self, '_pending_responses'):
                    self._pending_responses = {}
                self._pending_responses[request_id] = response
                logger.debug(f"Response stored with key {request_id}")
            
            elif action == 'filter_products':
                logger.debug(f"Handling filter products response for request {request_id}")
                if not hasattr(self, '_pending_responses'):
                    self._pending_responses = {}
                self._pending_responses[request_id] = response
                logger.debug(f"Response stored with key {request_id}")
            
            elif action == 'get_categories_vendors':
                logger.debug(f"Handling categories/vendors response for request {request_id}")
                if not hasattr(self, '_pending_responses'):
                    self._pending_responses = {}
                self._pending_responses[request_id] = response
                logger.debug(f"Response stored with key {request_id}")
            
            else:
                logger.warning(f"Unknown action in response: {action}")
            
            logger.debug(f"EXIT: MainApp._handle_processor_response()")
            
        except Exception as e:
            logger.error(f"Failed to handle processor response: {str(e)}", exc_info=True)

    def get_response(self, request_id):
        """
        Retrieve response for a specific request.
        
        Args:
            request_id: ID of the request to retrieve response for
            
        Returns:
            Response data or None if not yet available
        """
        logger.debug(f"ENTRY: MainApp.get_response(request_id={request_id})")
        
        try:
            if not hasattr(self, '_pending_responses'):
                self._pending_responses = {}
            
            response = self._pending_responses.pop(request_id, None)
            if response:
                logger.debug(f"Retrieved response for request {request_id}")
            else:
                logger.debug(f"No response yet for request {request_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get response: {str(e)}", exc_info=True)
            return None

    def _check_data_queue(self):
        """Periodic check for data from data processor (polling fallback)"""
        logger.debug("ENTRY: MainApp._check_data_queue() [periodic check]")
        
        try:
            # This is the periodic polling check (fallback)
            # With callback signaling, this happens less frequently
            self._check_data_queue_immediate()
        except Exception as e:
            logger.error(f"Error in periodic queue check: {str(e)}", exc_info=True)
        
        # Schedule next periodic check (500ms, with callback we check more efficiently)
        self.after(500, self._check_data_queue)
        logger.debug("EXIT: MainApp._check_data_queue() [rescheduled]")

    def _on_closing(self):
        """Handle window close"""
        logger.info("Window close event triggered")
        logger.debug("ENTRY: MainApp._on_closing()")
        
        try:
            logger.debug("Stopping data processor...")
            self.data_processor.stop()
            logger.debug("Data processor stopped")
            
            logger.debug("Destroying application window...")
            self.destroy()
            logger.info("Application closed successfully")
            logger.debug("EXIT: MainApp._on_closing()")
            
        except Exception as e:
            logger.error(f"Error during application close: {str(e)}", exc_info=True)
            self.destroy()


def main():
    """Main entry point"""
    # Clear all log files at program startup to prevent them from growing too large
    AppLogger.clear_all_logs()
    
    logger.debug("=" * 50)
    logger.debug("ENTRY: main()")
    logger.info("Starting POS System Application...")
    
    try:
        # ========== Allow configurable log level via environment variable ==========
        # Usage: set LOG_LEVEL=DEBUG  (or WARNING/ERROR)
        # Default is ERROR
        import os
        log_level = os.environ.get('LOG_LEVEL', 'ERROR').upper()
        valid_levels = ['ERROR', 'WARNING', 'DEBUG']
        if log_level not in valid_levels:
            logger.warning(f"Invalid LOG_LEVEL '{log_level}'. Using ERROR. Valid options: {', '.join(valid_levels)}")
            log_level = 'ERROR'
        
        logger.info(f"Setting log level to: {log_level}")
        AppLogger.setup(log_level=log_level, log_file='log/pos.log')
        
        logger.info("Creating MainApp instance...")
        app = MainApp()
        logger.info("MainApp created successfully, starting main loop...")
        app.mainloop()
        logger.info("Main loop ended, application shutting down...")
        logger.debug("EXIT: main()")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
