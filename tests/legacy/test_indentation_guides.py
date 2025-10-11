#!/usr/bin/env python3
"""
Indentation Guide Test - NEO Script Editor
Test the vertical indentation guide lines feature.
"""

# Test various indentation levels
class IndentationTest:
    """Test class with multiple indentation levels."""
    
    def __init__(self):
        """Initialize with nested structures."""
        self.data = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': [
                            'deeply',
                            'nested',
                            'structure'
                        ]
                    }
                }
            }
        }
    
    def nested_function(self):
        """Function with multiple indentation levels."""
        if self.data:
            for key, value in self.data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, dict):
                            for deep_key, deep_value in sub_value.items():
                                if isinstance(deep_value, dict):
                                    for very_deep_key, very_deep_value in deep_value.items():
                                        if isinstance(very_deep_value, list):
                                            for item in very_deep_value:
                                                print(f"Found item: {item}")
                                                if len(item) > 5:
                                                    print("Long item detected")
    
    def control_structures(self):
        """Test control structures with indentation."""
        numbers = list(range(20))
        
        for num in numbers:
            if num % 2 == 0:
                if num % 4 == 0:
                    if num % 8 == 0:
                        print(f"{num} is divisible by 8")
                    else:
                        print(f"{num} is divisible by 4 but not 8")
                else:
                    print(f"{num} is even but not divisible by 4")
            else:
                if num % 3 == 0:
                    if num % 9 == 0:
                        print(f"{num} is divisible by 9")
                    else:
                        print(f"{num} is divisible by 3 but not 9")
                else:
                    print(f"{num} is odd and not divisible by 3")
    
    def try_except_blocks(self):
        """Test exception handling indentation."""
        try:
            result = self.complex_operation()
            if result:
                try:
                    processed = self.process_result(result)
                    if processed:
                        try:
                            final = self.finalize(processed)
                            return final
                        except Exception as e:
                            print(f"Finalization error: {e}")
                            return None
                    else:
                        print("Processing failed")
                        return None
                except Exception as e:
                    print(f"Processing error: {e}")
                    return None
            else:
                print("Operation failed")
                return None
        except Exception as e:
            print(f"Operation error: {e}")
            return None
        finally:
            print("Cleanup completed")
    
    def complex_operation(self):
        """Simulate complex operation."""
        return {'status': 'success', 'data': [1, 2, 3]}
    
    def process_result(self, result):
        """Process the result."""
        return result['data'] if result['status'] == 'success' else None
    
    def finalize(self, data):
        """Finalize the data."""
        return sum(data) if data else 0

# Function definitions at module level
def module_level_function():
    """Module level function with indentation."""
    
    def inner_function():
        """Inner function with more indentation."""
        
        def deeply_nested():
            """Deeply nested function."""
            
            def very_deep():
                """Very deep nesting."""
                return "Deep!"
            
            return very_deep()
        
        return deeply_nested()
    
    return inner_function()

# List comprehensions and generators
def comprehension_tests():
    """Test comprehensions with indentation."""
    
    # Nested list comprehension
    matrix = [
        [
            [
                item * multiplier 
                for item in range(3)
            ] 
            for multiplier in range(1, 4)
        ] 
        for _ in range(2)
    ]
    
    # Generator with conditions
    filtered_data = (
        item 
        for sublist in matrix 
        for subsublist in sublist 
        for item in subsublist 
        if item % 2 == 0
        if item > 2
    )
    
    return list(filtered_data)

# Context managers
def context_manager_test():
    """Test context managers with indentation."""
    
    with open(__file__, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        
        with open('output.tmp', 'w') as out_file:
            for line_num, line in enumerate(lines):
                if 'def ' in line:
                    with open('functions.log', 'a') as log_file:
                        log_file.write(f"Line {line_num}: {line.strip()}\n")
                        
                        if 'nested' in line.lower():
                            with open('nested_functions.log', 'a') as nested_log:
                                nested_log.write(f"Nested function found: {line.strip()}\n")

if __name__ == "__main__":
    print("=== Indentation Guide Test ===")
    print("Expected results:")
    print("- Vertical dotted lines should appear at each indentation level")
    print("- Lines should be subtle gray color (#404040)")
    print("- Lines should extend continuously through the visible area")
    print("- Different indentation levels should be clearly distinguished")
    print("- Toggle via View → Show Indentation Guides menu")
    
    # Run tests
    test = IndentationTest()
    test.control_structures()
    result = comprehension_tests()
    print(f"Comprehension result: {result[:5]}...")  # Show first 5 items