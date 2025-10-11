#!/usr/bin/env python
"""
Test script to verify syntax error detection and problems panel integration
"""

import sys
import os

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from main_window import AiScriptEditor

def test_syntax_error_detection():
    """Test the syntax error detection system."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create the main window
    window = AiScriptEditor()
    
    # Create a new tab with test content
    editor = window.new_tab("Syntax Test")
    
    # Test code with multiple syntax errors
    test_code = '''# Test code with multiple syntax errors
def broken_function()  # Missing colon
    print("This should cause an error")
    
def another_broken():
print("Wrong indentation")  # Indentation error

x = (1 + 2  # Unclosed parenthesis
y = 5
if x = 5:  # Assignment instead of comparison
    print("Wrong operator")
'''
    
    # Set the test code
    editor.setPlainText(test_code)
    
    # The syntax checking should happen automatically via textChanged signal
    print("✅ Test code with multiple syntax errors added to editor")
    print("📝 Expected behavior:")
    print("  - Red wavy underlines should appear on error lines")
    print("  - Problems panel should show syntax errors")
    print("  - Error details should include line numbers and descriptions")
    
    # Show the window for testing
    window.show()
    
    return app, window

if __name__ == "__main__":
    app, window = test_syntax_error_detection()
    
    print("\n🔧 Testing Instructions:")
    print("1. Check if the Problems panel shows syntax errors")
    print("2. Verify red wavy underlines appear on error lines")
    print("3. Test the AI chat with multiple error fixes")
    print("4. Verify that Keep/Copy/Undo buttons work with multiple changes")
    
    app.exec()