"""
Data Processor Thread - Handles backend data operations and dummy data feeds.
This thread runs separately from the GUI thread and sends data via queue.
"""

from dbm import sqlite3
import sqlite3
import threading
import queue
import time
#from dataclasses import dataclass
from typing import List, Dict, Any
from log.logging_config import get_logger
import shared.resource as resource
from shared.data_struct import Category, Product, Vendor, Batch

# ========== Initialize Logger ==========
logger = get_logger(__name__)

db_path = "database/POS_Data.db"  # Path to the SQLite database file



class DataProcessor(threading.Thread):
    """Thread that processes data and sends updates to GUI via queue"""

    def __init__(self, gui_callback=None):
        """
        Initialize DataProcessor thread.
        
        Args:
            gui_callback: Optional callback to signal GUI when response is ready
        """
        logger.debug("ENTRY: DataProcessor.__init__()")
        
        try:
            super().__init__(daemon=True)
            logger.debug("DataProcessor thread initialized as daemon thread")
            
            self.gui_callback = gui_callback
            if gui_callback:
                logger.debug("GUI callback function registered for sending responses to GUI")
            else:
                logger.debug("No GUI callback provided")
            
            self.running = True
            logger.debug("Running flag set to True")
            
            
            logger.debug("EXIT: DataProcessor.__init__() - Success")
            
        except Exception as e:
            logger.error(f"Failed to initialize DataProcessor: {str(e)}", exc_info=True)
            raise


    def refrech_products_details(self, page: int = 1, items_per_page: int = 20) -> Dict[str, Any]:
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

            #reload the product details from the DB
            self._initialized_data()

            #limit calculation for SQL query
            last_id = (page - 1) * items_per_page
            logger.debug(f"Calculated last_id for pagination: {last_id}")
            

            # Calculate total products and total pages for pagination metadata
            self.cursor.execute("SELECT COUNT(*) FROM products")
            total = self.cursor.fetchone()[0]
            total_pages = (total + items_per_page - 1) // items_per_page
            logger.debug(f"Total products in database: {total}")
            logger.debug(f"Total pages calculated: {total_pages}")


            
            # ========== Return Paginated Data ==========
            # Return the products for this page plus pagination metadata
            result = {
                #"products": resource.products_details[last_id:last_id + items_per_page],  # Products on current page
                "current_page": page,  # Current page number
                "total_pages": total_pages,  # Total available pages
                "total_items": total,  # Total number of products
            }
            
            logger.debug(f"EXIT: DataProcessor.get_products_page() - Returning pagination info")
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
            results = resource.products_details
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

    def _handle_gui_request(self, message):
        """
        Process GUI requests from event_queue.
        This is called from run() loop after gui_request_event is signaled.
        
        IMPORTANT: Only process gui_request messages. Put unknown messages back.
        This avoids consuming response messages meant for the GUI.
        """
        logger.debug("ENTRY: DataProcessor._handle_gui_request()")
        
        try:
            # Collect all gui_request messages (stop at first non-request or empty queue)
            requests_to_process = []
            messages_to_requeue = []
            


            #message = resource.event_queue.get_nowait()
            logger.debug(message)
            
            if message.get('type') == 'gui_request':
                requests_to_process.append(message)
            else:
                # Put non-request messages back for GUI to handle
                messages_to_requeue.append(message)
                    

            
            # Process all collected requests
            for message in requests_to_process:
                try:
                    action = message.get('action')
                    request_id = message.get('request_id')
                    source = message.get('source')
                    logger.debug(f"Processing GUI request: {action}")
                    
                    # ========== Route Request to Appropriate Handler ==========
                    if action == 'refresh_products_page':
                        logger.debug("Handling refresh_products_page request")
                        page = message.get('page')
                        logger.debug(f"page = {page}")
                        items_per_page = message.get('items_per_page', 20)
                        result = self.refrech_products_details(page, items_per_page)
                        response = {
                            'type': 'response',
                            'action': action,
                            'source' : source,
                            'request_id': request_id,
                            'status': 'success',
                            'data': result
                        }
                        
                    elif action == 'filter_products':
                        logger.debug("Handling filter_products request")
                        category = message.get('category')
                        vendor = message.get('vendor')
                        search = message.get('search')
                        result = self.filter_products(category, vendor, search)
                        response = {
                            'type': 'response',
                            'action': action,
                            'request_id': request_id,
                            'status': 'success',
                            'data': result
                        }
                        
                    elif action == 'get_categories_vendors':
                        logger.debug("Handling get_categories_vendors request")
                        response = {
                            'type': 'response',
                            'action': action,
                            'request_id': request_id,
                            'status': 'success',
                            'categories': self.categories,
                            'vendors': self.vendors
                        }
                        
                    else:
                        logger.warning(f"Unknown action requested: {action}")
                        response = {
                            'type': 'response',
                            'action': action,
                            'request_id': request_id,
                            'status': 'error',
                            'error': f'Unknown action: {action}'
                        }
                    
                    # Put response in queue
                    logger.debug(f"Putting response in queue for request {request_id}")
                    resource.background_event_queue.put(response)
                    
                except Exception as e:
                    logger.error(f"Error processing request: {str(e)}", exc_info=True)
                    # Put error response in queue
                    try:
                        resource.resource.event_queue.put({
                            'type': 'response',
                            'request_id': message.get('request_id'),
                            'status': 'error',
                            'error': str(e)
                        })
                    except:
                        pass
            
            # Requeue any non-request messages (like responses)
            for msg in messages_to_requeue:
                resource.GUI_event_queue.put(msg)
            
            # Signal GUI that processing complete and responses are ready
            if self.gui_callback and len(requests_to_process) > 0:
                logger.debug("Signaling GUI that response(s) are ready")
                self.gui_callback()
            
            logger.debug("EXIT: DataProcessor._handle_gui_request()")
            
        except Exception as e:
            logger.error(f"Critical error in request handler: {str(e)}", exc_info=True)

    def _initialized_data(self):
        """Load data from database (if needed)"""
        logger.debug("ENTRY: DataProcessor.load_data()")
        
        try:
            # Placeholder for any initial data loading if necessary
            logger.debug("Load Category and Vendor data for filters...")

            self.cursor.execute("""
                SELECT category_id, category_name
                FROM category
                ORDER BY category_id
            """)

            rows =self. cursor.fetchall()
            resource.category_details = [Category(row[0], row[1]) for row in rows]

            self.cursor.execute("""
                SELECT vendor_id, vendor_name
                FROM vendor
                ORDER BY vendor_id
            """)

            rows =self. cursor.fetchall()
            resource.vendor_details = [Vendor(row[0], row[1]) for row in rows]

            #load the product data from the DB
            self.cursor.execute("""
                SELECT product_id, name, mrp, price, total_in_stock, category_id, vendor_id, description, batch_id, cost
                FROM products
                ORDER BY product_id
            """)

            row = self.cursor.fetchall()
            resource.products_details = [Product(id=r[0], name=r[1], description=r[7], price=r[3], category=r[5], vendor=r[6], stock=r[4], batch_id=r[8], cost=r[9]) for r in row]

            
            self.cursor.execute("""
                SELECT batch_id, item_code, cost, mrp, price, quantity, in_stock
                FROM stock
                ORDER BY batch_id
            """)

            row = self.cursor.fetchall()
            resource.stock_details = [Batch(batch_id=r[0], item_code=r[1], cost=r[2], mrp=r[3], price=r[4], quantity=r[5], in_stock=r[6]) for r in row]

            logger.debug("EXIT: DataProcessor.load_data() - Success")
            
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}", exc_info=True)
            raise

    def run(self):
        """
        Main thread loop - waits for and processes GUI requests.
        Runs in background thread and signals GUI when responses are ready.
        """
        logger.info("DataProcessor thread started")
        logger.debug("ENTRY: DataProcessor.run()")

        #connet with data base
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.categories = []  # List of unique categories for filters
        self.vendors = []  # List of unique vendors for filters 

        
        try:
            while self.running:
                try:

                    logger.debug("Waiting for GUI requests...")
                    message = resource.GUI_event_queue.get()
                    logger.debug("GUI request received  from queue")
                    self._handle_gui_request(message)

                except Exception as e:
                    logger.error(f"Error in request processing loop: {str(e)}", exc_info=True)
                    time.sleep(0.1)
            
            logger.info("DataProcessor thread stopped")
            logger.debug("EXIT: DataProcessor.run()")
            
        except Exception as e:
            logger.error(f"Critical error in DataProcessor.run(): {str(e)}", exc_info=True)

    def stop(self):
        """Stop the data processing thread"""
        logger.debug("ENTRY: DataProcessor.stop()")
        logger.info("Stopping data processor thread...")
        
        try:
            # Set flag to exit the main loop
            self.running = False
            logger.debug("Running flag set to False - thread will stop on next iteration")
            
        except Exception as e:
            logger.error(f"Error stopping data processor: {str(e)}", exc_info=True)
