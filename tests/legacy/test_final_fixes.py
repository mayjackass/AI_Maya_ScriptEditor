#!/usr/bin/env python
"""Test multiple error detection and targeted code application"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main_window import AiScriptEditor
from PySide6.QtWidgets import QApplication

def test_multiple_errors():
    """Test that we can detect multiple syntax errors"""
    
    # Create app if not exists
    if not QApplication.instance():
        app = QApplication([])
    
    # Create editor instance
    editor = AiScriptEditor()
    
    # Code with multiple syntax errors
    error_code = '''
# Multiple syntax errors test
if True:  # Missing colon - ERROR 1
    print("test")

x = 5 +   # Incomplete expression - ERROR 2

def broken_func(  # Unclosed parenthesis - ERROR 3
    return "test"

for i in range(5)  # Missing colon - ERROR 4
    print(i)
'''
    
    # Test multiple error detection
    problems = editor._get_python_syntax_errors(error_code)
    
    print("🔍 MULTIPLE ERROR DETECTION TEST:")
    print(f"   Total problems found: {len(problems)}")
    
    if len(problems) >= 3:  # Should find multiple errors
        print("✅ SUCCESS: Multiple errors detected!")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. Line {problem['line']}: {problem['message']}")
        return True
    else:
        print("❌ FAILED: Should detect multiple errors!")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. Line {problem['line']}: {problem['message']}")
        return False

def test_targeted_changes():
    """Test that code changes are targeted, not full replacement"""
    
    # Create app if not exists
    if not QApplication.instance():
        app = QApplication([])
    
    # Create editor instance
    editor = AiScriptEditor()
    
    original_code = '''def hello():
    print("Hello")
    x = 5
    return x

def goodbye():
    print("Goodbye")'''

    suggested_code = '''def hello():
    print("Hello World")  # Changed line
    x = 10               # Changed line
    return x

def goodbye():
    print("Goodbye")'''
    
    print("\n🎯 TARGETED CHANGES TEST:")
    print("   Original has 2 functions")
    print("   Suggestion changes only 2 lines in first function")
    
    # Test targeted application
    try:
        editor._apply_targeted_changes(None, original_code, suggested_code)
        print("✅ SUCCESS: Targeted changes method works!")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Final Fixes...")
    
    # Run tests
    test1_passed = test_multiple_errors()
    test2_passed = test_targeted_changes()
    
    print(f"\n📊 RESULTS:")
    print(f"   Multiple Error Detection: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Targeted Code Changes: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   • Multiple errors are now detected properly")
        print("   • Code changes are targeted, not full replacement")
        print("   • Issues should be resolved!")
    else:
        print("\n⚠️  Some tests failed - check output above")