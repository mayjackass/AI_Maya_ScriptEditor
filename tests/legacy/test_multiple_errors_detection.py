"""
Test the multiple syntax error detection system
Run this to verify the syntax error detection is working
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main_window import AiScriptEditor
from PySide6 import QtWidgets

def test_multiple_syntax_errors():
    """Test multiple syntax error detection"""
    
    # Test code with multiple syntax errors
    test_code = '''# Multiple syntax errors for testing

# Error 1: Unterminated string
print("Hello world

# Error 2: Missing colon
if True
    pass

# Error 3: Bad indentation
def test_function():
print("Bad indentation")

# Error 4: Undefined variable and invalid operator
x == = 5
y = z + undefined_var

print("End of test")
'''
    
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    try:
        # Create editor instance
        editor_window = AiScriptEditor()
        
        # Test syntax error detection
        print("=== TESTING MULTIPLE SYNTAX ERROR DETECTION ===")
        
        problems = editor_window._get_python_syntax_errors(test_code)
        
        print(f"\n✅ Detection Results: Found {len(problems)} syntax errors")
        
        for i, problem in enumerate(problems, 1):
            print(f"  {i}. Line {problem['line']}: {problem['message']}")
        
        if len(problems) >= 4:
            print("\n🎯 SUCCESS: Multiple syntax errors detected correctly!")
        elif len(problems) == 1:
            print("\n❌ ISSUE: Only 1 error detected - the system is stopping at first error")
        else:
            print(f"\n⚠️ PARTIAL: {len(problems)} errors detected (expected at least 4)")
            
        return len(problems)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    count = test_multiple_syntax_errors()
    print(f"\nFinal result: {count} syntax errors detected")