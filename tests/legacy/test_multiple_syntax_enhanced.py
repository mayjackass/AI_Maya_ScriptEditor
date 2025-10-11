#!/usr/bin/env python3
"""
Test enhanced multiple syntax error detection system.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_multiple_syntax_detection():
    """Test the enhanced syntax error detection with various error types."""
    
    # Import the main window to test syntax detection
    from main_window import AiScriptEditor
    
    # Create test editor instance
    editor = AiScriptEditor()
    
    # Test code with multiple different syntax errors
    test_code = '''
def hello_world(
    print("Hello world"
    
def another_function():
    if True
        print("Missing colon")
        
class TestClass
    def method(self)
        return "unterminated string
        
for i in range(10)
    print(i
    
# Invalid variable name
2var = "invalid"
def   = "cannot use keyword"
'''
    
    print("🧪 Testing Enhanced Multiple Syntax Error Detection")
    print("=" * 60)
    
    # Test the enhanced syntax detection method
    problems = editor._get_python_syntax_errors(test_code)
    
    print(f"✅ Detected {len(problems)} syntax errors:")
    print()
    
    for i, problem in enumerate(problems, 1):
        print(f"  {i}. Line {problem['line']}: {problem['message']}")
        print(f"     Type: {problem['type']}")
        print()
    
    # Test expected error types
    expected_errors = [
        'syntax',  # compile() errors
        'colon',   # missing colons
        'string',  # unterminated strings  
        'variable', # invalid variable names
        'parenthes', # unclosed parentheses
    ]
    
    found_types = [error['message'].lower() for error in problems]
    
    print("📊 Error Type Analysis:")
    for error_type in expected_errors:
        matches = [msg for msg in found_types if error_type in msg]
        print(f"  {error_type.capitalize()}: {len(matches)} detected")
    
    print()
    print(f"🎯 Total Errors: {len(problems)}")
    
    if len(problems) >= 6:  # Should find multiple different types
        print("✅ SUCCESS: Enhanced multi-error detection working!")
    else:
        print("⚠️  WARNING: May not be detecting all error types")
    
    print("\n" + "=" * 60)
    return len(problems)

if __name__ == "__main__":
    test_multiple_syntax_detection()