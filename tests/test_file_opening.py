#!/usr/bin/env python3
"""
Test File Opening from Explorer
This file tests the double-click functionality in the file explorer.
"""

def test_function():
    """This is a test function."""
    print("Hello from test file!")
    return "Test successful"

# Test variables
test_variable = 42
test_string = "This should be highlighted properly"

# Test multi-line string
docstring = """
This is a multi-line string
that should be highlighted correctly
when opened from the explorer
"""

if __name__ == "__main__":
    print("Test file loaded successfully!")
    result = test_function()
    print(f"Result: {result}")