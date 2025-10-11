#!/usr/bin/env python
"""Simple test for multiple error detection - no GUI"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_error_detection_only():
    """Test just the error detection logic without GUI"""
    
    # Import only what we need
    from main_window import AiScriptEditor
    
    # Create instance
    editor = AiScriptEditor()
    
    # Test code with multiple errors
    error_code = '''# Multiple errors
if True  # Missing colon - ERROR 1
    print("test")

x = 5 +   # Incomplete - ERROR 2

def func(  # Unclosed paren - ERROR 3
    return "test"

for i in range(5)  # Missing colon - ERROR 4
    print(i)
'''
    
    print("🔍 Testing error detection...")
    print(f"Code has {len(error_code.splitlines())} lines")
    
    # Test the detection method directly
    problems = editor._get_python_syntax_errors(error_code)
    
    print(f"\n📊 RESULTS:")
    print(f"   Errors found: {len(problems)}")
    
    if problems:
        print("   Error details:")
        for i, problem in enumerate(problems, 1):
            print(f"     {i}. Line {problem['line']}: {problem['message']}")
    
    # Expected: Should find at least 3-4 errors
    expected_min = 3
    success = len(problems) >= expected_min
    
    print(f"\n✅ {'SUCCESS' if success else 'FAILED'}: Expected >= {expected_min} errors, found {len(problems)}")
    
    return success

if __name__ == "__main__":
    try:
        success = test_error_detection_only()
        if success:
            print("\n🎉 Error detection is working correctly!")
        else:
            print("\n⚠️ Error detection needs improvement")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()