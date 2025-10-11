"""
Test script to verify enhanced syntax error detection
Run this to test multiple syntax error detection and highlighting
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main_window import AiScriptEditor
from PySide6 import QtWidgets, QtCore

def test_multiple_syntax_errors():
    """Test the enhanced syntax error detection system."""
    
    # Sample code with multiple syntax errors
    test_code = '''# Test code with multiple syntax errors

# Error 1: Unterminated string
print("Missing quote

# Error 2: Bad indentation  
def test():
print("Bad indent")

# Error 3: Missing colon
if True
    pass

# Error 4: Invalid syntax
x == = 5

print("Valid line at end")
'''
    
    print("=== ENHANCED SYNTAX ERROR DETECTION TEST ===")
    print()
    
    # Create a minimal app to test syntax detection
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    try:
        # Create editor instance
        editor_window = AiScriptEditor()
        
        # Test the enhanced syntax error detection
        problems = editor_window._get_python_syntax_errors(test_code)
        
        print(f"✅ Enhanced detection found {len(problems)} syntax errors:")
        print()
        
        for i, problem in enumerate(problems, 1):
            print(f"  {i}. Line {problem['line']}: {problem['message']}")
        
        print()
        print("Expected errors:")
        print("  - Unterminated string literal")  
        print("  - Indentation errors")
        print("  - Missing colon")
        print("  - Invalid assignment operator")
        print()
        
        if len(problems) >= 3:
            print("✅ SUCCESS: Multiple errors detected!")
            print("✅ Red underlines and dots should appear in the editor")
            print("✅ Problems panel should populate automatically")
        else:
            print("❌ ISSUE: Only detecting limited errors")
            
        print()
        print("📋 Testing Instructions:")
        print("1. Open the running AI Script Editor")
        print("2. Paste the test code into the editor") 
        print("3. Wait 1 second for auto-detection")
        print("4. Check for:")
        print("   - Red wavy underlines on error lines")
        print("   - Red dots on line numbers") 
        print("   - Problems panel showing all errors")
        print("   - Double-click problems to navigate to errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    test_multiple_syntax_errors()