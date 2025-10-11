"""
Test script to trigger syntax error highlighting in the main application
"""

import subprocess
import time
import sys
import os

def test_syntax_highlighting():
    """Test syntax highlighting by creating code with errors"""
    
    # Code with multiple syntax errors
    error_code = '''# Test file with syntax errors
print("Missing quote
def test_function():
print("Bad indentation")
if True
    print("Missing colon above")
x == = 5  # Invalid operator
'''
    
    print("🧪 SYNTAX HIGHLIGHTING TEST")
    print("=" * 50)
    print()
    print("📝 Instructions:")
    print("1. The AI Script Editor should be running")
    print("2. Copy this code and paste it into the editor:")
    print()
    print(error_code)
    print()
    print("3. Wait 1 second for auto-detection")
    print()
    print("✅ Expected Results:")
    print("   🔴 Red wavy underlines on error lines")
    print("   🔴 Red dots on line numbers (2, 4, 5, 7)")
    print("   🔴 Problems panel populated with errors")
    print("   🔴 Debug output in terminal showing error detection")
    print()
    print("📊 Check the terminal running main_window.py for debug output!")
    print()
    
    # Create a test file that can be opened in the editor
    test_file = "test_syntax_errors_temp.py"
    try:
        with open(test_file, 'w') as f:
            f.write(error_code)
        print(f"📁 Created test file: {test_file}")
        print("   You can open this file in the AI Script Editor to test")
        
    except Exception as e:
        print(f"❌ Could not create test file: {e}")

if __name__ == "__main__":
    test_syntax_highlighting()