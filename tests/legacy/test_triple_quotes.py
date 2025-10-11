#!/usr/bin/env python3
"""Test script for triple quote highlighting in NEO Script Editor."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore
from editor.code_editor import CodeEditor
from editor.highlighter import PythonHighlighter

def test_triple_quotes():
    """Test the triple quote highlighting functionality."""
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create a code editor
    editor = CodeEditor()
    editor.show()
    
    # Test code with various triple quote scenarios
    test_code = '''# Test triple quote highlighting
def test_function():
    """This is a docstring
    that spans multiple lines
    and should be highlighted properly"""
    
    multi_line_string = """
    This is another multi-line string
    with multiple lines of content
    that should all be highlighted
    """
    
    f_string_multi = f"""
    This is an f-string
    with multiple lines: {1 + 2}
    """
    
    single_quote_multi = \'\'\'
    Single quote multi-line string
    should also work properly
    \'\'\'
    
    return "Normal string should not interfere"

# More code after strings
print("Testing complete")
'''
    
    # Set the test code
    editor.setPlainText(test_code)
    
    print("Triple quote highlighting test setup complete!")
    print("Check the editor window to verify that:")
    print("1. Multi-line docstrings are fully highlighted")
    print("2. Multi-line strings with ''' and \"\"\" work")
    print("3. F-strings with triple quotes work")
    print("4. Regular code highlighting still works")
    
    # Keep the window open for manual inspection
    app.exec()

if __name__ == "__main__":
    test_triple_quotes()