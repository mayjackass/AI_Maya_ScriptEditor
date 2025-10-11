#!/usr/bin/env python3
"""
Hover Tooltip Test - NEO Script Editor
Test the syntax hover functionality similar to VS Code IntelliSense.
"""

# Python keywords to test hover on
def test_function():
    """Test function - hover over 'def' keyword."""
    for i in range(10):  # hover over 'for', 'range'
        if i % 2 == 0:   # hover over 'if'
            print(f"Even: {i}")  # hover over 'print'
        else:             # hover over 'else'
            continue      # hover over 'continue'
    
    # Test with statements
    with open("test.txt", "r") as f:  # hover over 'with', 'open', 'as'
        content = f.read()
    
    # Test try/except
    try:                    # hover over 'try'
        result = int("123") # hover over 'int'
    except ValueError as e: # hover over 'except', 'ValueError'
        pass               # hover over 'pass'
    finally:               # hover over 'finally'
        print("Done")

class TestClass:           # hover over 'class'
    """Test class for hover tooltips."""
    
    def __init__(self, value):  # hover over '__init__', 'self'
        self.value = value      # hover over 'self'
    
    def __str__(self):          # hover over '__str__'
        return str(self.value)  # hover over 'str', 'return'
    
    @property                   # hover over decorators
    def doubled(self):
        return self.value * 2

# Test built-in functions
numbers = list(range(5))    # hover over 'list', 'range'
length = len(numbers)       # hover over 'len'
is_empty = bool(numbers)    # hover over 'bool'
text = "hello world"
upper_text = text.upper()

# Test Maya Python commands (if available)
try:
    import maya.cmds as cmds     # hover over 'import', 'as', 'cmds'
    
    # Maya commands to test hover
    cube = cmds.polyCube()       # hover over 'polyCube'
    cmds.move(0, 5, 0)          # hover over 'move'  
    cmds.rotate(45, 0, 0)       # hover over 'rotate'
    cmds.scale(2, 2, 2)         # hover over 'scale'
    selected = cmds.ls(selection=True)  # hover over 'ls'
    cmds.select(clear=True)     # hover over 'select'
    
except ImportError:
    print("Maya not available - testing Python-only features")

# Test PySide6/Qt (if available)
try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton  # hover over Qt classes
    from PySide6.QtCore import Signal, Slot  # hover over 'Signal', 'Slot'
    
    class TestWidget(QWidget):   # hover over 'QWidget'
        clicked = Signal()       # hover over 'Signal'
        
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout()    # hover over 'QVBoxLayout' 
            button = QPushButton("Test")  # hover over 'QPushButton'
            layout.addWidget(button)
            
        @Slot()                  # hover over 'Slot'
        def handle_click(self):
            print("Button clicked!")

except ImportError:
    print("PySide6 not available - testing Python-only features")

# Lambda and advanced features
square = lambda x: x * x     # hover over 'lambda'
numbers = [1, 2, 3, 4, 5]
squared = [square(x) for x in numbers]  # hover over comprehension

# Global and nonlocal
global_var = "I'm global"    # hover over 'global'

def outer():
    x = 10
    def inner():
        nonlocal x           # hover over 'nonlocal'
        x += 1
        global global_var    # hover over 'global'
        global_var = "Modified"
    inner()
    return x

print("=== Hover Tooltip Test Ready! ===")
print("Hover over any highlighted syntax element to see tooltips")
print("Expected features:")
print("- Python keywords show syntax help")  
print("- Built-in functions show descriptions")
print("- Maya commands show usage examples")
print("- Qt classes show import information")  
print("- Magic methods show explanations")
print("- Variables and identifiers show context help")