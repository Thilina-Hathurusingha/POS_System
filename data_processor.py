"""
Data Processor Thread - Handles backend data operations and dummy data feeds.
This thread runs separately from the GUI thread and sends data via queue.
"""

import threading
import queue
import time
from dataclasses import dataclass
from typing import List, Dict, Any


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

    def __init__(self, gui_queue: queue.Queue):
        """
        Initialize DataProcessor thread.
        
        Args:
            gui_queue: Queue to send data updates to GUI thread
        """
        super().__init__(daemon=True)
        self.gui_queue = gui_queue
        self.running = True
        self._init_dummy_data()

    def _init_dummy_data(self):
        """Initialize dummy product data"""
        # ========== Sample Product Data ==========
        # Create a list of Product objects with realistic data
        # Each product has: id, name, price, category, vendor, and stock quantity
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
        
        # ========== Extract Unique Categories and Vendors ==========
        # Extract all unique categories and vendors from products, then sort alphabetically
        # This data is used to populate filter dropdown menus
        self.categories = sorted(set(p.category for p in self.products))
        self.vendors = sorted(set(p.vendor for p in self.products))

    def get_products_page(self, page: int = 1, items_per_page: int = 12) -> Dict[str, Any]:
        """
        Get products for a specific page.
        
        Args:
            page: Page number (1-indexed)
            items_per_page: Items per page
            
        Returns:
            Dictionary with products and pagination info
        """
        # ========== Calculate Pagination ==========
        # Determine total number of pages needed based on total products
        total = len(self.products)
        total_pages = (total + items_per_page - 1) // items_per_page  # Ceiling division
        
        # ========== Validate Page Number ==========
        # Ensure page is within valid range (1 to total_pages)
        page = max(1, min(page, total_pages))
        
        # ========== Calculate Slice Indices ==========
        # Determine the starting and ending index for the current page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        # ========== Return Paginated Data ==========
        # Return the products for this page plus pagination metadata
        return {
            "products": self.products[start_idx:end_idx],  # Products on current page
            "current_page": page,  # Current page number
            "total_pages": total_pages,  # Total available pages
            "total_items": total,  # Total number of products
        }

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
        # Start with all products as the base result set
        results = self.products
        
        # ========== Filter by Category ==========
        # If a specific category is selected (not 'All Categories'),
        # keep only products matching that category
        if category and category != "All Categories":
            results = [p for p in results if p.category == category]
        
        # ========== Filter by Vendor ==========
        # Further refine results by vendor if a specific vendor is selected
        if vendor and vendor != "All Vendors":
            results = [p for p in results if p.vendor == vendor]
        
        # ========== Search by Product Name ==========
        # Final filter: search for products whose name contains the search term
        # Search is case-insensitive for better user experience
        if search and search.strip():  # Only apply if search term is not empty
            search_lower = search.lower()  # Convert search to lowercase
            results = [p for p in results if search_lower in p.name.lower()]
        
        return results

    def run(self):
        """Main thread loop - sends periodic updates to GUI"""
        # ========== Thread Main Loop ==========
        # This runs in the background as a daemon thread
        # It sends data updates to the GUI via a thread-safe queue
        while self.running:
            try:
                # Send initial data once when thread starts
                # This includes categories, vendors, and first page of products
                self.gui_queue.put({
                    "type": "initial_data",  # Message type identifier
                    "categories": self.categories,  # List of product categories
                    "vendors": self.vendors,  # List of product vendors
                    "products_page": self.get_products_page(1),  # First page of products
                })
                
                # Keep thread alive, processing requests from GUI if needed
                # Sleep for 1 second between iterations to reduce CPU usage
                time.sleep(1)
            except Exception as e:
                # Log any errors that occur in the thread
                print(f"Data processor error: {e}")
                time.sleep(1)  # Wait before retrying

    def stop(self):
        """Stop the data processing thread"""
        # Set flag to exit the main loop
        self.running = False
