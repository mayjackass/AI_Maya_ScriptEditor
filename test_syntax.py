# Test Python Syntax Highlighting
import sys
from PySide6 import QtWidgets

class TestClass:
    def __init__(self):
        self.value = 42
        
    def method(self):
        """This is a string"""
        x = 10 + 20
        if x > 15:
            print("Hello World")
            return True
        return False
