"""
Debug Test Sample - NEO Script Editor
Test the breakpoint and debugging features with this script
"""

def calculate_fibonacci(n):
    """Calculate Fibonacci sequence up to n numbers."""
    print(f"Calculating Fibonacci sequence for {n} numbers...")
    
    fib_sequence = []
    a, b = 0, 1
    
    for i in range(n):
        fib_sequence.append(a)
        print(f"  Step {i+1}: {a}")
        a, b = b, a + b  # Set breakpoint here (line 15)
    
    return fib_sequence


def test_variables():
    """Test variable inspection in breakpoints."""
    name = "NEO Script Editor"
    version = "1.0"
    features = ["Syntax Highlighting", "Morpheus AI", "Debugging"]
    
    print(f"\nTesting {name} v{version}")
    
    for i, feature in enumerate(features, 1):
        print(f"{i}. {feature}")  # Set breakpoint here (line 30)
    
    return features


def main():
    """Main function to test debugging."""
    print("="*50)
    print("🐛 Debug Test Started")
    print("="*50)
    
    # Test 1: Fibonacci
    result1 = calculate_fibonacci(8)
    print(f"\nFibonacci Result: {result1}")
    
    # Test 2: Variables
    result2 = test_variables()
    
    # Test 3: Math operations
    numbers = [1, 2, 3, 4, 5]
    total = 0
    
    print("\nCalculating sum...")
    for num in numbers:
        total += num  # Set breakpoint here (line 53)
        print(f"  Current sum: {total}")
    
    print(f"\nFinal sum: {total}")
    
    print("\n" + "="*50)
    print("✅ Debug Test Complete")
    print("="*50)


# Run the test
if __name__ == "__main__":
    main()
