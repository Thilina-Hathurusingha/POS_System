"""
Data Processor Thread - Handles backend data operations and dummy data feeds.
This thread runs separately from the GUI thread and sends data via queue.
"""

import threading
import queue
import time
from dataclasses import dataclass
from typing import List, Dict, Any
from log.logging_config import get_logger

# ========== Initialize Logger ==========
logger = get_logger(__name__)


@dataclass
class Product:
    """Product data structure"""
    id: int
    name: str
    price: float
    category: str
    vendor: str
    stock: int


class DataProcessor(threading.Thread):
    """Thread that processes data and sends updates to GUI via queue"""

    def __init__(self, gui_queue: queue.Queue, gui_callback=None):
        """
        Initialize DataProcessor thread.
        
        Args:
            gui_queue: Queue to send data updates to GUI thread
            gui_callback: Optional callback function to signal GUI when data is available
        """
        logger.debug("ENTRY: DataProcessor.__init__()")
        
        try:
            super().__init__(daemon=True)
            logger.debug("DataProcessor thread initialized as daemon thread")
            
            self.gui_queue = gui_queue
            logger.debug("GUI queue reference stored")
            
            self.gui_callback = gui_callback
            if gui_callback:
                logger.debug("GUI callback function registered for thread-safe signaling")
            else:
                logger.debug("No GUI callback provided - GUI will use polling")
            
            self.running = True
            logger.debug("Running flag set to True")
            
            logger.debug("Initializing dummy data...")
            self._init_dummy_data()
            logger.debug("Dummy data initialized")
            
            logger.debug("EXIT: DataProcessor.__init__() - Success")
            
        except Exception as e:
            logger.error(f"Failed to initialize DataProcessor: {str(e)}", exc_info=True)
            raise

    def _init_dummy_data(self):
        """Initialize dummy product data"""
        logger.debug("ENTRY: DataProcessor._init_dummy_data()")
        
        try:
            # ========== Sample Product Data ==========
            # Create a list of Product objects with realistic data
            # Each product has: id, name, price, category, vendor, and stock quantity
            logger.debug("Creating container for 15 sample products...")
            self.products = [
                Product(1, "Coca-Cola 500ml", 25.99, "Beverages", "Global Drinks", 50),
                Product(2, "Pepsi 500ml", 25.99, "Beverages", "PepsiCo", 45),
                Product(3, "Orange Juice 1L", 45.50, "Beverages", "Fresh Juice Co", 30),
                Product(4, "Coffee Beans 500g", 299.99, "Coffee", "Mountain Blend", 20),
                Product(5, "Espresso Machine", 15999.00, "Machines", "CoffeeArt", 5),
                Product(6, "Tea Set 15 bags", 189.99, "Tea", "Premium Tea", 40),
                Product(7, "Milk Chocolate Bar", 89.99, "Snacks", "Sweet Company", 100),
                Product(8, "Almonds 250g", 349.99, "Snacks", "NutsPro", 25),
                Product(9, "Whole Wheat Bread", 79.99, "Bakery", "Daily Bread", 35),
                Product(10, "Croissant Pack", 199.99, "Bakery", "French Bakery", 15),
                Product(11, "Greek Yogurt 500ml", 129.99, "Dairy", "Dairy Fresh", 50),
                Product(12, "Butter 200g", 159.99, "Dairy", "Dairy Fresh", 40),
                Product(13, "Olive Oil 500ml", 449.99, "Oils", "Premium Oils", 20),
                Product(14, "Honey 500ml", 299.99, "Condiments", "Local Honey", 30),
                Product(15, "Pasta 500g", 99.99, "Grains", "Italian Made", 60),
            ]
            logger.debug(f"Created {len(self.products)} sample products")
            
            # ========== Extract Unique Categories and Vendors ==========
            # Extract all unique categories and vendors from products, then sort alphabetically
            # This data is used to populate filter dropdown menus
            logger.debug("Extracting unique categories and vendors...")
            self.categories = sorted(set(p.category for p in self.products))
            self.vendors = sorted(set(p.vendor for p in self.products))
            
            logger.debug(f"Extracted {len(self.categories)} categories: {self.categories}")
            logger.debug(f"Extracted {len(self.vendors)} vendors: {self.vendors}")
            logger.debug("EXIT: DataProcessor._init_dummy_data() - Success")
            
        except Exception as e:
            logger.error(f"Failed to initialize dummy data: {str(e)}", exc_info=True)
            raise

    def get_products_page(self, page: int = 1, items_per_page: int = 20) -> Dict[str, Any]:
        """
        Get products for a specific page.
        
        Args:
            page: Page number (1-indexed)
            items_per_page: Items per page
            
        Returns:
            Dictionary with products and pagination info
        """
        logger.debug(f"ENTRY: DataProcessor.get_products_page(page={page}, items_per_page={items_per_page})")
        
        try:
            # ========== Calculate Pagination ==========
            # Determine total number of pages needed based on total products
            total = len(self.products)
            total_pages = (total + items_per_page - 1) // items_per_page  # Ceiling division
            
            logger.debug(f"Total products: {total}, items per page: {items_per_page}, total pages: {total_pages}")
            
            # ========== Validate Page Number ==========
            # Ensure page is within valid range (1 to total_pages)
            original_page = page
            page = max(1, min(page, total_pages))
            if page != original_page:
                logger.warning(f"Page number {original_page} out of range [1, {total_pages}]. Using page {page}")
            
            # ========== Calculate Slice Indices ==========
            # Determine the starting and ending index for the current page
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            
            logger.debug(f"Page indices: {start_idx} to {end_idx}")
            
            # ========== Return Paginated Data ==========
            # Return the products for this page plus pagination metadata
            result = {
                "products": self.products[start_idx:end_idx],  # Products on current page
                "current_page": page,  # Current page number
                "total_pages": total_pages,  # Total available pages
                "total_items": total,  # Total number of products
            }
            
            logger.debug(f"EXIT: DataProcessor.get_products_page() - Returning {len(result['products'])} products")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get products page: {str(e)}", exc_info=True)
            raise

    def filter_products(self, category: str = None, vendor: str = None, search: str = None) -> List[Product]:
        """
        Filter products based on criteria.
        
        Args:
            category: Filter by category
            vendor: Filter by vendor
            search: Search in product name
            
        Returns:
            List of filtered products
        """
        logger.debug(f"ENTRY: DataProcessor.filter_products(category={category}, vendor={vendor}, search={search})")
        
        try:
            # Start with all products as the base result set
            results = self.products
            logger.debug(f"Starting with {len(results)} products")
            
            # ========== Filter by Category ==========
            # If a specific category is selected (not 'All Categories'),
            # keep only products matching that category
            if category and category != "All Categories":
                results = [p for p in results if p.category == category]
                logger.debug(f"After category filter: {len(results)} products")
            
            # ========== Filter by Vendor ==========
            # Further refine results by vendor if a specific vendor is selected
            if vendor and vendor != "All Vendors":
                results = [p for p in results if p.vendor == vendor]
                logger.debug(f"After vendor filter: {len(results)} products")
            
            # ========== Search by Product Name ==========
            # Final filter: search for products whose name contains the search term
            # Search is case-insensitive for better user experience
            if search and search.strip():  # Only apply if search term is not empty
                search_lower = search.lower()  # Convert search to lowercase
                results = [p for p in results if search_lower in p.name.lower()]
                logger.debug(f"After search filter for '{search}': {len(results)} products")
            
            logger.debug(f"EXIT: DataProcessor.filter_products() - Returning {len(results)} filtered products")
            return results
            
        except Exception as e:
            logger.error(f"Failed to filter products: {str(e)}", exc_info=True)
            raise


    #For now we don't need this function
    def run(self):
        """Main thread loop - sends periodic updates to GUI"""
        logger.info("DataProcessor thread started")
        logger.debug("ENTRY: DataProcessor.run()")
        
        iteration = 0
        # ========== Thread Main Loop ==========
        # This runs in the background as a daemon thread
        # It sends data updates to the GUI via a thread-safe queue
        while self.running:
            iteration += 1
            try:
                logger.debug(f"Thread iteration {iteration}: Preparing data for GUI...")
                
                # Send initial data once when thread starts
                # This includes categories, vendors, and first page of products
                message = {
                    "type": "initial_data",  # Message type identifier
                    "categories": self.categories,  # List of product categories
                    "vendors": self.vendors,  # List of product vendors
                    "products_page": self.get_products_page(1),  # First page of products
                }
                
                logger.debug(f"Putting message in queue: type={message['type']}")
                self.gui_queue.put(message)
                logger.debug(f"Message sent to GUI. Queue size: {self.gui_queue.qsize()}")
                
                # ========== Signal GUI Thread ==========
                # If callback is registered, call it to wake up GUI immediately
                # This is thread-safe because the callback uses self.after() internally
                if self.gui_callback:
                    logger.debug("Signaling GUI thread that data is available")
                    self.gui_callback()
                else:
                    logger.debug("No GUI callback - relying on polling")
                
                # Keep thread alive, processing requests from GUI if needed
                # Sleep for 1 second between iterations to reduce CPU usage
                logger.debug("Thread sleeping for 1 second...")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in data processor thread iteration {iteration}: {str(e)}", exc_info=True)
                time.sleep(1)  # Wait before retrying
        
        logger.info("DataProcessor thread stopped")
        logger.debug("EXIT: DataProcessor.run()")

    def stop(self):
        """Stop the data processing thread"""
        logger.debug("ENTRY: DataProcessor.stop()")
        logger.info("Stopping data processor thread...")
        
        try:
            # Set flag to exit the main loop
            self.running = False
            logger.debug("Running flag set to False")
            logger.debug("EXIT: DataProcessor.stop() - Stop flag sent")
            
        except Exception as e:
            logger.error(f"Error stopping data processor: {str(e)}", exc_info=True)
