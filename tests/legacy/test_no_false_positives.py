#!/usr/bin/env python
"""Test script to verify false positive fixes"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the main window
from main_window import AiScriptEditor
from PySide6.QtWidgets import QApplication

def test_valid_code():
    """Test that valid Python code doesn't trigger false positives"""
    
    # Valid code that was previously flagging false positives
    test_code = '''
# Valid Python code - should have NO syntax errors
message = "Hello World"
name = "John"
path = r"C:\Users\Test"
text = """This is a
multi-line string"""

# Variables and assignments
x = 5
y = 10
result = x + y

# Functions
def greet(name):
    return f"Hello {name}"

# Classes
class Person:
    def __init__(self, name):
        self.name = name

# Control structures
if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")

for i in range(5):
    print(i)

# Dictionary and list operations
data = {"key": "value"}
items = [1, 2, 3, 4, 5]
'''

    # Create app if not exists
    if not QApplication.instance():
        app = QApplication([])
    
    # Create editor instance
    editor = AiScriptEditor()
    
    # Test syntax checking
    problems = editor._get_python_syntax_errors(test_code)
    
    print(f"✅ FALSE POSITIVE TEST RESULTS:")
    print(f"   Code length: {len(test_code.splitlines())} lines")
    print(f"   Problems found: {len(problems)}")
    
    if problems:
        print("❌ FAILED - False positives still detected:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. Line {problem['line']}: {problem['message']}")
        return False
    else:
        print("✅ PASSED - No false positives detected!")
        return True

def test_actual_errors():
    """Test that real syntax errors are still caught"""
    
    # Code with genuine syntax errors
    error_code = '''
# This has real syntax errors
if True
    print("missing colon")
    
x = 5 +
print("incomplete expression")

def broken_function(
    print("broken parameters")
'''
    
    # Create app if not exists
    if not QApplication.instance():
        app = QApplication([])
    
    # Create editor instance  
    editor = AiScriptEditor()
    
    # Test syntax checking
    problems = editor._get_python_syntax_errors(error_code)
    
    print(f"\n✅ REAL ERROR DETECTION TEST:")
    print(f"   Problems found: {len(problems)}")
    
    if problems:
        print("✅ PASSED - Real errors detected:")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. Line {problem['line']}: {problem['message']}")
        return True
    else:
        print("❌ FAILED - Should have detected real errors!")
        return False

if __name__ == "__main__":
    print("🔧 Testing False Positive Fixes...")
    
    # Run tests
    test1_passed = test_valid_code()
    test2_passed = test_actual_errors()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   False Positive Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Real Error Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! False positive fix successful!")
    else:
        print("⚠️  Some tests failed. Check output above.")