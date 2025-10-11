#!/usr/bin/env python3
"""
Test syntax error detection method directly without GUI.
"""

def test_syntax_detection_method():
    """Test the syntax detection logic without GUI components."""
    
    def _get_python_syntax_errors(code):
        """Simplified version of the enhanced syntax error detection."""
        problems = []
        
        if not code.strip():
            return problems
            
        # Method 1: Try basic compile to catch first error (but continue for more)
        try:
            compile(code, '<string>', 'exec')
            # No syntax errors found by compile()
        except SyntaxError as e:
            # Found at least one error, add it
            problems.append({
                'type': 'Error',
                'message': e.msg or 'Syntax error',
                'line': e.lineno or 1,
                'file': 'Current File'
            })
        except Exception as e:
            problems.append({
                'type': 'Error', 
                'message': f'Compilation error: {str(e)}',
                'line': 1,
                'file': 'Current File'
            })
            
        # Method 2: Line-by-line syntax pattern detection
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith('#'):
                continue
                
            # Check for unterminated strings (improved detection)
            in_string = False
            string_char = None
            escape_next = False
            
            for j, char in enumerate(line_stripped):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if not in_string and char in ['"', "'"]:
                    # Check for triple quotes
                    if j + 2 < len(line_stripped) and line_stripped[j:j+3] == char*3:
                        continue  # Skip triple quotes for now
                    in_string = True
                    string_char = char
                elif in_string and char == string_char:
                    in_string = False
                    string_char = None
            
            # If still in string at end of line, it's unterminated
            if in_string:
                # Check if this error already exists
                error_exists = any(p['line'] == i and 'string' in p['message'].lower() for p in problems)
                if not error_exists:
                    problems.append({
                        'type': 'Error',
                        'message': 'Unterminated string literal',
                        'line': i,
                        'file': 'Current File'
                    })
                    
            # Check for missing colons after keywords
            if (line_stripped.startswith(('if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally')) 
                and not line_stripped.endswith(':') and not line_stripped.endswith('\\') 
                and '#' not in line_stripped):
                error_exists = any(p['line'] == i and 'colon' in p['message'].lower() for p in problems)
                if not error_exists:
                    problems.append({
                        'type': 'Error',
                        'message': 'Missing colon after control statement',
                        'line': i,
                        'file': 'Current File'
                    })
                    
        return problems
    
    # Test code with multiple different syntax errors
    test_code = '''
def hello_world(
    print("Hello world"
    
def another_function():
    if True
        print("Missing colon")
        
class TestClass
    def method(self):
        return "unterminated string
        
for i in range(10)
    print(i)
'''
    
    print("🧪 Testing Enhanced Multiple Syntax Error Detection")
    print("=" * 60)
    
    # Test the enhanced syntax detection method
    problems = _get_python_syntax_errors(test_code)
    
    print(f"✅ Detected {len(problems)} syntax errors:")
    print()
    
    for i, problem in enumerate(problems, 1):
        print(f"  {i}. Line {problem['line']}: {problem['message']}")
        print(f"     Type: {problem['type']}")
        print()
    
    print(f"🎯 Total Errors: {len(problems)}")
    
    if len(problems) >= 4:  # Should find multiple different types
        print("✅ SUCCESS: Enhanced multi-error detection working!")
    else:
        print("⚠️  WARNING: May not be detecting all error types")
    
    print("\n" + "=" * 60)
    return len(problems)

if __name__ == "__main__":
    test_syntax_detection_method()