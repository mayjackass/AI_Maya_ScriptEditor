"""
Test script to verify chat history counter and floating button functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore
from main_window import AiScriptEditor

def test_chat_counter_and_buttons():
    """Test the chat functionality and button operations."""
    
    # Create the application
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create main window
    window = AiScriptEditor()
    window.show()
    
    # Test 1: Check initial state
    print("=== Initial State Test ===")
    if hasattr(window, 'morpheus_manager'):
        current, total = window.morpheus_manager.get_conversation_info()
        print(f"Initial conversation info: {current}/{total}")
        print(f"Chat history length: {len(window.morpheus_manager.chat_history)}")
    else:
        print("❌ MorpheusManager not found!")
        return
    
    # Test 2: Check history label
    if hasattr(window, 'historyLabel'):
        print(f"History label text: '{window.historyLabel.text()}'")
    else:
        print("❌ History label not found!")
    
    # Test 3: Check floating buttons
    print("\n=== Floating Button Test ===")
    if hasattr(window, 'floatingActions'):
        print(f"Floating actions widget exists: {window.floatingActions is not None}")
        print(f"Floating actions visible: {window.floatingActions.isVisible()}")
        
        if hasattr(window, 'floatingCopyBtn'):
            print(f"Copy button exists: {window.floatingCopyBtn is not None}")
            print(f"Copy button enabled: {window.floatingCopyBtn.isEnabled()}")
        
        if hasattr(window, 'floatingApplyBtn'):
            print(f"Apply button exists: {window.floatingApplyBtn is not None}")
            print(f"Apply button enabled: {window.floatingApplyBtn.isEnabled()}")
            
        if hasattr(window, 'floatingFixBtn'):
            print(f"Fix button exists: {window.floatingFixBtn is not None}")
            print(f"Fix button enabled: {window.floatingFixBtn.isEnabled()}")
    else:
        print("❌ Floating actions not found!")
    
    # Test 4: Test button positioning
    print("\n=== Button Positioning Test ===")
    if hasattr(window, '_position_floating_actions'):
        try:
            window._position_floating_actions()
            pos = window.floatingActions.pos()
            size = window.floatingActions.size()
            print(f"Button position: {pos.x()}, {pos.y()}")
            print(f"Button size: {size.width()}x{size.height()}")
            print("✅ Positioning method works")
        except Exception as e:
            print(f"❌ Positioning error: {e}")
    
    # Test 5: Simulate showing floating actions
    print("\n=== Show Floating Actions Test ===")
    test_code = "print('Hello World')\nx = 1 + 1"
    try:
        window._show_floating_actions(test_code)
        print(f"Current floating code set: {len(window.current_floating_code)} chars")
        print(f"Floating actions visible after show: {window.floatingActions.isVisible()}")
        print("✅ Show floating actions works")
    except Exception as e:
        print(f"❌ Show floating actions error: {e}")
    
    # Test 6: Test navigation buttons
    print("\n=== Navigation Button Test ===")
    if hasattr(window, 'prevChatBtn') and hasattr(window, 'nextChatBtn'):
        print(f"Previous button enabled: {window.prevChatBtn.isEnabled()}")
        print(f"Next button enabled: {window.nextChatBtn.isEnabled()}")
    else:
        print("❌ Navigation buttons not found!")
    
    print("\n=== Test Complete ===")
    
    # Keep window open for manual testing
    QtCore.QTimer.singleShot(100, lambda: print("✨ Window ready for manual testing"))
    return app, window

if __name__ == "__main__":
    app, window = test_chat_counter_and_buttons()
    
    print("\n🔧 Manual Test Instructions:")
    print("1. Try sending a message in the chat")
    print("2. Check if history counter updates")
    print("3. Try clicking Copy/Apply/Fix buttons when they appear")
    print("4. Close window when done testing")
    
    app.exec()