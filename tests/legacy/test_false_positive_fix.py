#!/usr/bin/env python
"""Test script to verify false positive error detection is fixed."""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    # Import the code editor
    from editor.code_editor import CodeEditor
    from PySide6.QtWidgets import QApplication, QMainWindow
    from PySide6.QtCore import Qt
    import sys
    
    app = QApplication(sys.argv)
    
    # Create a main window and add the code editor
    window = QMainWindow()
    editor = CodeEditor()
    window.setCentralWidget(editor)
    
    # Test with valid Python code that was previously flagged
    test_code = """import maya.cmds as cmds
import os
import sys

def test_function():
    pass

class TestClass:
    def __init__(self):
        self.value = 42
        
    def method(self):
        return self.value

# Comment test
x = 10
y = x + 5
result = test_function()
"""
    
    # Set the text
    editor.setPlainText(test_code)
    
    print("Test code set in editor:")
    print(test_code)
    print("\nIf error detection is working correctly, this should NOT show syntax errors")
    print("for the valid Python code above.")
    
    # Don't show the window - just test the detection
    print("\nTest complete. Check the console for any false positive error messages.")
    
except Exception as e:
    print(f"Error running test: {e}")
    import traceback
    traceback.print_exc()