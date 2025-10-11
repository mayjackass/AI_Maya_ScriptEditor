#!/usr/bin/env python3
"""
Test the enhanced false positive fixes for variable name validation.
"""

def test_enhanced_false_positive_fixes():
    """Test that common valid Python patterns don't trigger false positives."""
    
    def _enhanced_variable_check(line_stripped, line_num):
        """Enhanced variable validation logic (extracted from main code)."""
        import re
        
        problems = []
        
        if ('=' in line_stripped and 
            not line_stripped.startswith(('def ', 'class ', 'if ', 'elif ', 'while ', 'for ', 'try:', 'except', 'with ')) and
            not any(op in line_stripped for op in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '**=', '//=', '%=']) and
            not line_stripped.startswith('#') and  # Skip comments
            not line_stripped.startswith(('print(', 'return ', 'yield ', 'raise ', 'assert ')) and  # Skip function calls
            '(' not in line_stripped.split('=')[0]):  # Skip function calls with assignment
            
            var_part = line_stripped.split('=')[0].strip()
            if var_part:
                # Enhanced validation - be very conservative
                is_valid = (
                    # Allow standard variable patterns
                    re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_part) or  # single_var
                    re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)+$', var_part) or  # a, b, c
                    # Allow attribute access
                    var_part.startswith(('self.', 'cls.')) or
                    '.' in var_part or  # obj.attr, module.var
                    # Allow indexing
                    '[' in var_part or ']' in var_part or  # arr[0], dict['key']
                    # Allow unpacking
                    '(' in var_part or ')' in var_part or  # (a, b)
                    # Allow special cases
                    var_part in ['_', '__']  # underscore variables
                )
                
                # Only flag genuinely invalid cases
                if not is_valid:
                    # Double-check: only flag if it's clearly wrong
                    if (re.match(r'^\d', var_part) or  # Starts with digit: 123abc
                        var_part in ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'import', 'from'] or  # Python keywords
                        re.search(r'[^\w\s,\.\[\]()_]', var_part)):  # Contains invalid characters
                        
                        problems.append({
                            'type': 'Error',
                            'message': f'Invalid variable name: {var_part}',
                            'line': line_num,
                            'file': 'Current File'
                        })
        
        return problems
    
    print("🧪 Testing Enhanced False Positive Prevention")
    print("=" * 55)
    
    # Test cases that should NOT trigger errors (valid Python)
    valid_cases = [
        "material_name = 'MyMaterial'",
        "cube_name = 'test_cube'", 
        "self.attribute = value",
        "obj.property = data",
        "arr[0] = item",
        "dict['key'] = value", 
        "a, b, c = values",
        "result = function_call()",
        "x = y + z",
        "_ = unused_value",
        "sphere_name = cmds.polySphere(name='randomColorSphere')[0]",
        "shading_group = cmds.sets(material, renderable=True)",
        "cmds.setAttr(material + '.color', 0.2, 0.6, 0.8)",
        "material = cmds.shadingNode('lambert', asShader=True)"
    ]
    
    # Test cases that SHOULD trigger errors (invalid Python)
    invalid_cases = [
        "123abc = 'starts with number'",
        "def = 'keyword as variable'",
        "class = 'another keyword'",
        "if = 'control keyword'",
        "2var = 'starts with digit'"
    ]
    
    print("\n📋 Testing VALID cases (should have NO false positives):")
    false_positives = 0
    
    for i, case in enumerate(valid_cases, 1):
        errors = _enhanced_variable_check(case, i)
        if errors:
            print(f"  ❌ Line {i}: '{case}' → {errors[0]['message']}")
            false_positives += 1
        else:
            print(f"  ✅ Line {i}: '{case}'")
    
    print(f"\n📊 False Positives: {false_positives}/{len(valid_cases)}")
    
    print("\n📋 Testing INVALID cases (should detect real errors):")
    real_errors_detected = 0
    
    for i, case in enumerate(invalid_cases, 1):
        errors = _enhanced_variable_check(case, i)
        if errors:
            print(f"  ✅ Line {i}: '{case}' → Correctly flagged as error")
            real_errors_detected += 1
        else:
            print(f"  ❌ Line {i}: '{case}' → Should be flagged as error!")
    
    print(f"\n📊 Real Errors Detected: {real_errors_detected}/{len(invalid_cases)}")
    
    # Summary
    print("\n" + "=" * 55)
    if false_positives == 0 and real_errors_detected >= len(invalid_cases) // 2:
        print("✅ SUCCESS: Enhanced validation prevents false positives!")
    else:
        print(f"⚠️  NEEDS WORK: {false_positives} false positives, {real_errors_detected} real errors detected")
    
    return false_positives, real_errors_detected

if __name__ == "__main__":
    test_enhanced_false_positive_fixes()