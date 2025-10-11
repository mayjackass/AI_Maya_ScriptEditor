#!/usr/bin/env python
"""
Test script to verify AI code block display is working.
This test creates a chat window and checks if code blocks render properly.
"""

import sys
import os

# Add the script directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from PySide6 import QtWidgets, QtCore
from ai.chat import ChatWidget

def test_ai_code_display():
    """Test that AI code blocks display properly in chat."""
    
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Create chat widget
    chat = ChatWidget()
    chat.show()
    chat.resize(800, 600)
    
    print("🧪 Testing AI Code Block Display")
    print("=" * 50)
    
    # Test message with code block
    test_response = """Here's a Maya Python script to create a cube:

```python
import maya.cmds as cmds

def create_cube():
    cube = cmds.polyCube(name="test_cube")[0]
    cmds.move(0, 5, 0, cube)
    return cube

# Create the cube
cube = create_cube()
print(f"Created cube: {cube}")
```

This script creates a cube and moves it up 5 units."""

    print("📝 Adding test AI response with code block...")
    
    # Add the response to chat
    chat._display_response(test_response)
    
    print("✅ Test response added to chat")
    print("👀 Check the chat window - you should see:")
    print("   • Properly formatted text")  
    print("   • Code block with syntax highlighting")
    print("   • 'Apply in Editor' button below code")
    print("   • Proper line breaks between elements")
    
    # Keep window open for inspection
    print("\n🔍 Chat window is open - inspect visually")
    print("   Press Ctrl+C to close when done testing")
    
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\n👋 Test completed")
        
if __name__ == "__main__":
    test_ai_code_display()