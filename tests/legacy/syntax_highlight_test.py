#!/usr/bin/env python3
"""
Comprehensive Python syntax highlighting test file.
This file contains various Python constructs to test VS Code-style highlighting.
"""

import os
import sys
import maya.cmds as cmds
from typing import List, Dict, Optional, Union, Any, Callable
from collections import defaultdict, namedtuple
from dataclasses import dataclass
import asyncio

# Global constants
DEBUG = True
PI = 3.14159
VERSION = "1.0.0"

# Numbers - different formats
integer_num = 42
float_num = 3.14159
scientific = 1.23e-4
hex_num = 0xFF00AA
binary_num = 0b11010110
octal_num = 0o755

# Strings - all varieties
single_quote = 'Hello world'
double_quote = "Hello world"
raw_string = r"C:\Users\Path\file.txt"
f_string = f"The value is {integer_num}"
triple_quote = """
Multi-line string
with multiple lines
"""

# Built-in constants and types
values = [True, False, None, Ellipsis, NotImplemented]
types = [int, str, float, bool, list, dict, tuple, set]

@dataclass
class Person:
    """A person class with type hints."""
    name: str
    age: int
    active: bool = True
    
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def __str__(self) -> str:
        return f"Person(name='{self.name}', age={self.age})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def is_adult(self) -> bool:
        return self.age >= 18
    
    @staticmethod  
    def create_from_dict(data: Dict[str, Any]) -> 'Person':
        return Person(data['name'], data['age'])
    
    @classmethod
    def create_anonymous(cls, age: int) -> 'Person':
        return cls("Anonymous", age)

# Function with complex type hints
def process_data(
    items: List[Dict[str, Union[int, str]]],
    callback: Optional[Callable[[str], bool]] = None,
    *args: Any,
    **kwargs: Any
) -> Dict[str, List[str]]:
    """Process a list of data items with optional callback."""
    result = defaultdict(list)
    
    for item in items:
        if callback and callback(item.get('name', '')):
            result['processed'].append(str(item))
        else:
            result['skipped'].append(str(item))
    
    return dict(result)

# Exception handling
try:
    x = 10 / 0
except ZeroDivisionError as e:
    print(f"Error occurred: {e}")
except (ValueError, TypeError) as e:
    print(f"Multiple exception types: {e}")
finally:
    print("Cleanup code")

# Control structures
if DEBUG:
    print("Debug mode enabled")
elif VERSION == "1.0.0":
    print("Version 1.0.0")
else:
    print("Other version")

# Loops
for i in range(10):
    if i % 2 == 0:
        continue
    print(f"Odd number: {i}")

while True:
    break

# Comprehensions
numbers = [x**2 for x in range(10) if x % 2 == 0]
squares_dict = {x: x**2 for x in range(5)}
unique_chars = {char for char in "hello world" if char != ' '}

# Lambda functions
square = lambda x: x ** 2
add = lambda a, b: a + b

# Generators
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Async functions
async def async_function():
    await asyncio.sleep(1)
    return "Done"

async def main():
    result = await async_function()
    print(result)

# Context managers
with open("file.txt", "w") as f:
    f.write("Hello world")

# Advanced features
def decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@decorator
def decorated_function():
    pass

# Maya-specific code (if available)
if 'maya' in sys.modules:
    # Maya commands
    cube = cmds.polyCube(name="test_cube")[0]
    cmds.move(0, 5, 0, cube)
    cmds.rotate(45, 0, 0, cube)
    cmds.scale(2, 2, 2, cube)
    
    # Maya Python API
    import maya.api.OpenMaya as om
    
    selection_list = om.MSelectionList()
    selection_list.add(cube)

# Error handling with custom exceptions
class CustomError(Exception):
    """Custom exception class."""
    pass

try:
    raise CustomError("Something went wrong")
except CustomError:
    pass

# Regular expressions
import re
pattern = r"(\d+)-(\d+)-(\d+)"
match = re.match(pattern, "2023-10-15")

# Magic methods showcase
class MagicClass:
    def __add__(self, other):
        return self
    
    def __len__(self):
        return 42
    
    def __getitem__(self, key):
        return key
    
    def __call__(self, *args):
        return args

if __name__ == "__main__":
    # Test all the syntax highlighting
    person = Person("John", 25)
    print(person.is_adult)
    
    data = [{"name": "test", "value": 123}]
    result = process_data(data)
    print(result)