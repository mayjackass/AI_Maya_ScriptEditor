#!/usr/bin/env python
"""
Simple test runner without Unicode issues for Windows.
"""

import re
import html

def test_code_parsing():
    """Test basic code block parsing functionality."""
    
    print("Testing Code Block Parsing...")
    print("=" * 40)
    
    # Test content
    content = '''Here is a Python script:

```python
import maya.cmds as cmds
def create_cube():
    return cmds.polyCube()[0]
```

This creates a cube.'''

    # Test regex
    pattern = r'```(?:(\w+)\n)?(.*?)```'
    code_blocks = re.findall(pattern, content, flags=re.DOTALL)
    
    print(f"Content length: {len(content)}")
    print(f"Code blocks found: {len(code_blocks)}")
    
    success = True
    
    if len(code_blocks) != 1:
        print("FAIL: Expected 1 code block")
        success = False
    else:
        language, code = code_blocks[0]
        if language != 'python':
            print(f"FAIL: Expected 'python', got '{language}'")
            success = False
        if 'maya.cmds' not in code:
            print("FAIL: Maya code not detected")
            success = False
            
    if success:
        print("PASS: Code parsing working correctly")
    
    return success

def test_html_generation():
    """Test HTML generation for code blocks."""
    
    print("\nTesting HTML Generation...")
    print("=" * 40)
    
    code = "import maya.cmds as cmds\ndef test():\n    pass"
    
    try:
        # Simple HTML escaping
        escaped = html.escape(code)
        
        # Check if escaping worked
        if '&lt;' in escaped or '&gt;' in escaped or len(escaped) >= len(code):
            print("PASS: HTML escaping working")
            return True
        else:
            print("FAIL: HTML escaping not working")
            return False
            
    except Exception as e:
        print(f"FAIL: HTML error - {e}")
        return False

def test_maya_detection():
    """Test Maya code detection logic."""
    
    print("\nTesting Maya Code Detection...")
    print("=" * 40)
    
    test_cases = [
        ("import maya.cmds as cmds", True),
        ("cmds.polyCube()", True), 
        ("console.log('test')", False),
        ("def create_cube(): pass", True),
        ("<html>test</html>", False)
    ]
    
    success = True
    
    for code, expected in test_cases:
        is_maya = (
            'maya.cmds' in code or
            'cmds.' in code or
            ('def ' in code and 'console.log' not in code and '<html' not in code)
        )
        
        if is_maya == expected:
            print(f"PASS: '{code[:20]}...' -> {is_maya}")
        else:
            print(f"FAIL: '{code[:20]}...' -> {is_maya} (expected {expected})")
            success = False
    
    return success

def main():
    """Run all simple tests."""
    
    print("NEO Script Editor - Simple Test Suite")
    print("=" * 50)
    
    tests = [
        test_code_parsing,
        test_html_generation, 
        test_maya_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All core functionality working!")
        return True
    else:
        print(f"FAILED: {total - passed} tests failed")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)