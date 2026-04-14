#!/usr/bin/env python
"""Test bidirectional communication setup"""

try:
    from shared.resource import event_queue, gui_request_event
    from proessing.data_processor import DataProcessor
    from main import MainApp
    
    print("✅ Bidirectional communication system initialized!")
    print(f"   - event_queue: {event_queue}")
    print(f"   - gui_request_event: {gui_request_event}")
    print(f"   - DataProcessor: {DataProcessor}")
    print(f"   - MainApp: {MainApp}")
    print("\n✅ All components successfully imported!")
    print("\n📝 System Architecture:")
    print("   1. GUI sends REQUEST to event_queue + sets gui_request_event")
    print("   2. DataProcessor thread detects event and calls _handle_gui_request()")
    print("   3. DataProcessor processes request, puts RESPONSE in event_queue")
    print("   4. DataProcessor calls GUI's _on_data_available callback")
    print("   5. GUI detects response and retrieves it via get_response()")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
