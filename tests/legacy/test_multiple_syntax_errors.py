"""
Test file with multiple syntax errors to verify the enhanced error detection system.
This should detect ALL errors, not just the first one.
"""

# Multiple Python syntax errors for testing

# Error 1: Missing closing quote
print("This is an unterminated string

# Error 2: Invalid indentation
def test_function():
print("Bad indentation")

# Error 3: Unclosed parenthesis
result = some_function(arg1, arg2

# Error 4: Invalid syntax
if True
    print("Missing colon")

# Error 5: Mixed tabs and spaces (if applicable)
def another_function():
	if True:  # Tab here
        print("Space here")  # Spaces here

# Error 6: Invalid operator
x == = 5

# Error 7: Incomplete statement
for i in

# Error 8: Invalid variable name
123invalid = "test"

print("End of test file")