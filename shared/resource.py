import threading
import queue

products = {}
lock = threading.Lock()
event_queue = queue.Queue()

# ========== Thread Synchronization ==========
# Event to signal data processor thread that GUI has sent a request
gui_request_event = threading.Event()
# Event to signal GUI thread that data processor has processed a request
processor_response_event = threading.Event()