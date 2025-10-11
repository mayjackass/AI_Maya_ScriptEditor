"""Test PEP 8 style code that should NOT trigger false positive errors."""

# This file contains various PEP 8 compliant code patterns that were
# previously causing false positive error detection

# Multi-line function definitions (PEP 8 style)
def long_function_name(
    var_one, var_two, var_three,
    var_four
):
    return var_one + var_two

# Multi-line class definitions
class MyLongClassName(
    SomeVeryLongBaseClassName,
    AnotherLongBaseClassName
):
    pass

# Multi-line function calls
result = some_function_with_long_name(
    argument_one,
    argument_two,
    argument_three
)

# Multi-line list definitions
my_list = [
    'item_one',
    'item_two', 
    'item_three'
]

# Multi-line dictionary definitions
my_dict = {
    'key_one': 'value_one',
    'key_two': 'value_two',
    'key_three': 'value_three'
}

# Multi-line expressions
total = (
    first_value +
    second_value +
    third_value
)

# Import statements
import maya.cmds as cmds
import os
import sys
from collections import defaultdict

# Function with type hints (PEP 484)
def typed_function(
    name: str,
    age: int,
    active: bool = True
) -> dict:
    return {'name': name, 'age': age, 'active': active}

# Long string literals broken across lines
long_string = (
    "This is a very long string that needs to be "
    "broken across multiple lines for better "
    "readability according to PEP 8 guidelines"
)

# Complex conditional statements
if (
    condition_one and
    condition_two and 
    condition_three
):
    do_something()

# Multi-line comprehensions  
filtered_data = [
    item.process()
    for item in data
    if item.is_valid()
]

print("All PEP 8 code above should be valid with no false positive errors!")