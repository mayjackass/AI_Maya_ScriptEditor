#!/usr/bin/env python3
"""
Test script for the NEO Script Editor debugging system.
This demonstrates various debugging scenarios.
"""

def calculate_fibonacci(n):
    """Calculate fibonacci number recursively."""
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def test_variables():
    """Test various variable types for debugging."""
    # Basic variables
    name = "NEO Script Editor"
    version = 2.0
    is_debugging = True
    
    # Collections
    numbers = [1, 2, 3, 4, 5]
    coordinates = {"x": 10, "y": 20, "z": 30}
    
    # Processing
    for i, num in enumerate(numbers):
        result = num * 2
        print(f"Item {i}: {num} * 2 = {result}")
    
    return coordinates

def main():
    """Main function to test debugging."""
    print("Starting debug test...")
    
    # Test fibonacci calculation
    fib_number = 5
    result = calculate_fibonacci(fib_number)
    print(f"Fibonacci({fib_number}) = {result}")
    
    # Test variable inspection
    test_data = test_variables()
    print(f"Test completed with data: {test_data}")

if __name__ == "__main__":
    main()