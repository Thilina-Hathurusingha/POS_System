import threading
import queue
from shared.data_struct import Category, Product, Vendor


#shared data
products_details = {}
category_details = {}
vendor_details = {}


# ========== Thread Synchronization ==========

# Event to signal GUI thread that data processor has processed a request
GUI_event_queue = queue.Queue()

# Event to signal GUI thread that data processor has processed a request
background_event_queue = queue.Queue()

