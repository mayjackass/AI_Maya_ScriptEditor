#!/usr/bin/env python3
"""
Triple Quote Highlighting Test for NEO Script Editor
Run this in Maya's Script Editor to test the highlighting.
"""

# Test various triple quote scenarios

def test_docstrings():
    """This is a docstring
    that spans multiple lines
    and should be highlighted as a string
    with proper colors."""
    pass

def test_multiline_strings():
    # Regular multi-line string with triple double quotes
    description = """
    This is a multi-line string
    that should be highlighted
    in string color (greenish)
    """
    
    # Regular multi-line string with triple single quotes
    another_string = '''
    This uses single quotes
    but should also be highlighted
    as a string
    '''
    
    return description, another_string

def test_f_strings():
    name = "World"
    count = 42
    
    # F-string with triple quotes - should be highlighted differently
    f_string_multi = f"""
    Hello {name}!
    Count is {count}
    This should be highlighted as f-string
    """
    
    # F-string with single triple quotes
    f_single = f'''
    Another f-string: {name}
    With count: {count}
    '''
    
    return f_string_multi, f_single

def test_mixed_scenarios():
    """Mixed test function."""
    
    # Normal string (should not interfere)
    normal = "This is a normal string"
    
    # Multi-line after normal code
    multi = """
    Multi-line string
    after normal code
    """
    
    # Code after multi-line
    result = len(multi)
    
    # F-string at the end
    summary = f"""
    Summary:
    Normal: {normal}
    Length: {result}
    """
    
    return summary

# Test inline triple quotes
inline_test = """Complete triple quote on one line"""
f_inline = f"""F-string complete on one line: {test_docstrings.__name__}"""

print("Triple quote highlighting test ready!")
print("Expected results:")
print("1. Docstrings should be highlighted in string color")  
print("2. Regular triple quotes (''' and \"\"\") should be string color")
print("3. F-string triple quotes should be f-string color (different from regular strings)")
print("4. Normal code should remain unaffected")
print("5. Mixed scenarios should work correctly")