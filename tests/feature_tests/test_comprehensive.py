#!/usr/bin/env python
"""
Comprehensive test for the enhanced AI Script Editor features:
1. Multiple error handling in diff system
2. Real-time syntax error checking with red underlines
3. Problems panel with VS Code styling
4. Double-click navigation to errors
"""

import sys
import os

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from main_window import AiScriptEditor

def test_comprehensive_features():
    """Test all enhanced features together."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create the main window
    window = AiScriptEditor()
    
    print("🚀 Starting Comprehensive Feature Test")
    print("=" * 50)
    
    # Test 1: Create tab with multiple syntax errors
    print("\n📝 Test 1: Multiple Syntax Errors Detection")
    editor = window.new_tab("Multi-Error Test")
    
    # Test code with multiple different types of syntax errors
    test_code_with_errors = '''# Multiple syntax error test file
def broken_function()  # Error 1: Missing colon
    print("This function is missing a colon")
    
def another_function():
print("Wrong indentation")  # Error 2: Indentation error

def third_function():
    result = (1 + 2 + 3  # Error 3: Unclosed parenthesis
    return result

def fourth_function():
    x = 5
    if x = 5:  # Error 4: Assignment instead of comparison
        print("This is wrong")

# Error 5: Invalid string
def fifth_function():
    msg = "unclosed string
    return msg

print("Testing multiple errors")
'''
    
    editor.setPlainText(test_code_with_errors)
    print("   ✅ Added code with 5 different syntax errors")
    print("   📋 Expected: Problems panel should show 5 errors")
    
    # Test 2: Show corrected version for multiple error fixing
    print("\n🔧 Test 2: Multiple Error Correction")
    
    # Simulate AI response with multiple fixes
    corrected_code = '''# Fixed version of the test file
def broken_function():  # Fix 1: Added missing colon
    print("This function now has a colon")
    
def another_function():
    print("This line now has correct indentation")  # Fix 2: Corrected indentation

def third_function():
    result = (1 + 2 + 3)  # Fix 3: Closed parenthesis properly
    return result

def fourth_function():
    x = 5
    if x == 5:  # Fix 4: Changed = to ==
        print("This is now correct")

# Fix 5: Fixed string
def fifth_function():
    msg = "properly closed string"
    return msg

print("Testing multiple errors")
'''
    
    print("   ✅ Prepared corrected version with all 5 fixes")
    print("   🎯 Expected: Intelligent diff should detect all function changes")
    
    # Test 3: Create another tab to test navigation
    print("\n🧪 Test 3: Problem Navigation Test")
    editor2 = window.new_tab("Navigation Test")
    
    navigation_test_code = '''def test_navigation():
    # Line 2
    x = undefined_variable  # This should cause an error
    # Line 4
    y = another_undefined  # Another error
    # Line 6
    return x + y

# More code to test navigation
for i in range(invalid_syntax:  # Syntax error on line 9
    print(i)
'''
    
    editor2.setPlainText(navigation_test_code)
    print("   ✅ Added navigation test code")
    print("   🎯 Expected: Double-clicking problems should jump to error lines")
    
    # Show the window
    window.show()
    
    # Print test instructions
    print("\n" + "=" * 50)
    print("🔍 MANUAL TESTING INSTRUCTIONS:")
    print("=" * 50)
    
    print("\n1. 🐛 SYNTAX ERROR CHECKING:")
    print("   • Check if red wavy underlines appear on error lines")
    print("   • Verify Problems panel shows errors with line numbers")
    print("   • Confirm status bar shows error count")
    
    print("\n2. 🧹 MULTIPLE ERROR FIXING:")
    print("   • Use AI chat to fix multiple errors")
    print("   • Verify Keep/Copy/Undo buttons appear") 
    print("   • Check that ALL errors are fixed, not just one")
    print("   • Confirm intelligent diff highlights all changes")
    
    print("\n3. 🎯 PROBLEM NAVIGATION:")
    print("   • Switch to 'Navigation Test' tab")
    print("   • Double-click on any problem in Problems panel")
    print("   • Verify cursor jumps to the correct error line")
    
    print("\n4. 🎨 VS CODE STYLE VERIFICATION:")
    print("   • Problems panel should have dark VS Code styling")
    print("   • Error icons should be red, warnings yellow")
    print("   • Alternating row colors in problems list")
    
    print("\n5. 🔄 REAL-TIME UPDATES:")
    print("   • Edit the code to fix an error manually")
    print("   • Verify problems list updates automatically") 
    print("   • Check that error count in status bar updates")
    
    print("\n" + "=" * 50)
    print("🎯 SUCCESS CRITERIA:")
    print("   ✅ All 5 syntax errors detected and shown in Problems")
    print("   ✅ Red wavy underlines visible on error lines")
    print("   ✅ Double-click navigation works correctly")
    print("   ✅ Multiple errors fixed simultaneously by AI")
    print("   ✅ VS Code-style dark theme applied consistently")
    print("=" * 50)
    
    return app, window

if __name__ == "__main__":
    app, window = test_comprehensive_features()
    
    # Set up a timer to print additional hints
    def print_hints():
        print("\n💡 HINT: Try asking the AI to:")
        print("   'Fix all syntax errors in this code'")
        print("   'Correct the multiple syntax issues'")
        print("   Then test the Keep/Copy/Undo functionality!")
    
    QTimer.singleShot(5000, print_hints)  # Print hints after 5 seconds
    
    app.exec()