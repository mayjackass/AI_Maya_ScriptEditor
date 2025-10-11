# Test file with multiple syntax errors to test the enhanced diff system

# Error 1: Missing colon
def broken_function()
    print("This function is missing a colon")

# Error 2: Invalid indentation
def another_function():
print("This line has wrong indentation")

# Error 3: Unclosed parentheses  
def third_function():
    result = (1 + 2 + 3
    return result

# Error 4: Invalid syntax
def fourth_function():
    x = 5
    if x = 5:  # Should be == not =
        print("This is wrong")

print("Testing multiple errors")