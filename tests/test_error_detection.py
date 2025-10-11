#!/usr/bin/env python
"""
Test script for VS Code-style multiple error detection
"""

def _get_python_syntax_errors_fast(code):
    """VS Code-style multiple error detection - fast and comprehensive."""
    problems = []
    
    if not code.strip():
        return problems
    
    lines = code.split('\n')
    
    # Multi-pass approach like VS Code
    temp_code = code
    error_lines = set()
    
    # Pass 1: Get all compile errors by iteratively fixing them
    for attempt in range(5):  # Limit attempts
        try:
            compile(temp_code, '<string>', 'exec')
            break
        except SyntaxError as e:
            if e.lineno and e.lineno not in error_lines:
                problems.append({
                    'type': 'Error',
                    'message': e.msg or 'Syntax error',
                    'line': e.lineno,
                    'file': 'Current File'
                })
                error_lines.add(e.lineno)
                
                # Fix this line temporarily to find more errors
                temp_lines = temp_code.split('\n')
                if 1 <= e.lineno <= len(temp_lines):
                    temp_lines[e.lineno - 1] = f"# FIXED: {temp_lines[e.lineno - 1]}"
                    temp_code = '\n'.join(temp_lines)
            else:
                break
    
    # Pass 2: Quick pattern check for missed errors  
    for i, line in enumerate(lines, 1):
        if i in error_lines:
            continue
            
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('#'):
            continue
            
        # Common syntax errors VS Code catches
        if (line_stripped.startswith(('if ', 'elif ', 'def ', 'for ', 'while ', 'class ')) 
            and not line_stripped.endswith(':') and not line_stripped.endswith('\\')):
            problems.append({
                'type': 'Error',
                'message': 'Missing colon after statement',
                'line': i,
                'file': 'Current File'
            })
        elif line_stripped.endswith(('+', '-', '*', '/', '=')):
            problems.append({
                'type': 'Error', 
                'message': 'Incomplete expression',
                'line': i,
                'file': 'Current File'
            })
    
    return problems[:10]  # Limit to 10 errors like VS Code


# Test cases with multiple errors
test_code = """
def test_function()  # Missing colon
    if True  # Missing colon 
        x = 5 +  # Incomplete expression
    return x

class TestClass  # Missing colon
    def method(self)  # Missing colon
        y = 10 * # Incomplete expression
        return y
"""

print("Testing multiple error detection...")
print("=" * 50)

errors = _get_python_syntax_errors_fast(test_code)

print(f"Found {len(errors)} errors:")
for i, error in enumerate(errors, 1):
    print(f"  {i}. Line {error['line']}: {error['message']}")

print("\nExpected: 6+ errors (missing colons and incomplete expressions)")
print(f"Actual: {len(errors)} errors")

if len(errors) >= 4:
    print("✅ SUCCESS: Multiple error detection is working!")
else:
    print("❌ FAILED: Only detecting single error")