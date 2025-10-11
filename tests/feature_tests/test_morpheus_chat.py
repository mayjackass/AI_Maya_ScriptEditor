#!/usr/bin/env python3
"""
Quick test script to verify Morpheus AI chat functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PySide6 import QtWidgets, QtCore, QtGui
import time

def test_morpheus_chat():
    """Test Morpheus chat functionality."""
    print("🧪 Testing Morpheus Chat Functionality...")
    
    # Import the main window
    from main_window import ScriptEditorWindow
    
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # Create main window
    window = ScriptEditorWindow()
    window.show()
    
    # Wait a moment for UI to initialize
    QtCore.QTimer.singleShot(1000, lambda: test_chat_features(window))
    
    print("✅ Application started - testing chat features in 1 second...")
    return app

def test_chat_features(window):
    """Test specific chat features."""
    print("🔍 Testing chat features...")
    
    try:
        # Check if chat input exists
        if hasattr(window, 'chatInput'):
            print("✅ Chat input exists")
            
            # Test typing in chat
            window.chatInput.setPlainText("Hello Morpheus, can you help me with Python?")
            print("✅ Can type in chat input")
            
            # Check if AI manager exists
            if hasattr(window, 'ai_manager'):
                print("✅ AI manager exists")
                
                # Test send message (without actually calling API)
                message = window.chatInput.toPlainText()
                if message:
                    print(f"✅ Message ready to send: '{message[:50]}...'")
                    
                    # Test message formatting
                    if hasattr(window.ai_manager, '_format_morpheus_message'):
                        test_msg = "Here's some code:\n```python\nprint('Hello World')\n```"
                        formatted = window.ai_manager._format_morpheus_message(test_msg)
                        print("✅ Message formatting works")
                        
                        # Test thinking indicator
                        if hasattr(window.ai_manager, '_show_thinking_indicator'):
                            window.ai_manager._show_thinking_indicator()
                            print("✅ Thinking indicator can be shown")
                            
                            # Hide it after a moment
                            QtCore.QTimer.singleShot(2000, window.ai_manager._hide_thinking_indicator)
                            print("✅ Thinking indicator will hide in 2 seconds")
                        
                    else:
                        print("❌ Message formatting method missing")
                else:
                    print("❌ No message in chat input")
            else:
                print("❌ AI manager missing")
        else:
            print("❌ Chat input missing")
            
        # Check if chat display exists
        if hasattr(window, 'chatDisplay'):
            print("✅ Chat display exists")
            
            # Add a test message
            window.chatDisplay.append("🧪 Test message - Morpheus chat is working!")
            print("✅ Can add messages to chat display")
        else:
            print("❌ Chat display missing")
            
    except Exception as e:
        print(f"❌ Error during chat testing: {e}")
    
    print("🏁 Chat testing completed!")

if __name__ == "__main__":
    app = test_morpheus_chat()
    
    # Run for a few seconds then exit
    QtCore.QTimer.singleShot(5000, app.quit)
    
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    
    print("🎯 Test completed!")