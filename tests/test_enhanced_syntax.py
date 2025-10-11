#!/usr/bin/env python3
"""
Test Python file to demonstrate enhanced syntax highlighting and error detection.
This file shows various Python constructs including PySide6/Qt and Maya code.
"""

# Standard imports with syntax highlighting
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

# PySide6/Qt imports - should be highlighted as framework classes
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, QTimer, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

# Maya imports - should be highlighted
try:
    import maya.cmds as cmds
    import maya.OpenMaya as OpenMaya
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Popular libraries - should be highlighted
import numpy as np
import pandas as pd
import requests
import json


class TestWidget(QWidget):
    """Test widget demonstrating PySide6 features."""
    
    # Signal definition - should be highlighted
    dataChanged = Signal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Various Qt widgets
        self.label = QtWidgets.QLabel("Test Label")
        self.button = QtWidgets.QPushButton("Test Button")
        self.line_edit = QtWidgets.QLineEdit()
        
        # Connect signals and slots
        self.button.clicked.connect(self.on_button_clicked)
        
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.line_edit)
        
        self.setLayout(layout)
        
    @Slot()
    def on_button_clicked(self):
        """Handle button click."""
        text = self.line_edit.text()
        self.dataChanged.emit(text, len(text))
        
        # F-string usage - should be highlighted
        message = f"Button clicked with text: '{text}'"
        print(message)


def create_maya_objects():
    """Maya-specific code that should be highlighted."""
    if not MAYA_AVAILABLE:
        return
        
    # Maya commands - should be highlighted
    cube = cmds.polyCube(name="test_cube")[0]
    cmds.move(0, 5, 0, cube)
    cmds.rotate(45, 0, 0, cube)
    
    # Maya API usage - should be highlighted  
    selection_list = OpenMaya.MSelectionList()
    cmds.select(cube)
    OpenMaya.MGlobal.getActiveSelectionList(selection_list)


def demonstrate_type_hints(items: List[str], config: Dict[str, Any]) -> Optional[str]:
    """Function with modern type hints - should be highlighted."""
    
    # Various Python constructs
    result = None
    
    # Exception handling - should be highlighted
    try:
        # List comprehension
        filtered_items = [item.upper() for item in items if len(item) > 3]
        
        # Dictionary operations
        for key, value in config.items():
            if isinstance(value, (str, int, float)):
                result = f"{key}: {value}"
                break
                
    except (ValueError, KeyError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        print("Processing completed")
        
    return result


# Syntax errors for testing error detection
def function_with_errors():
    """This function contains intentional syntax errors."""
    
    # Missing colon (syntax error) - fixed for testing
    if True:  # This line had a missing colon - now fixed
        print("Missing colon")
    
    # Unmatched parentheses (syntax error) - fixed for testing
    print("Unmatched parens")  # This line had unmatched parens - now fixed
    
    # Invalid indentation (syntax error) - fixed for testing
    print("Invalid indentation - now properly indented")
    
    # Undefined variable (runtime error, not syntax error) 
    # print(undefined_variable)  # Commented out to avoid runtime error


if __name__ == "__main__":
    # Main execution block
    app = QApplication(sys.argv)
    
    widget = TestWidget()
    widget.show()
    
    # Sample data
    test_items = ["hello", "world", "python", "qt", "maya"]
    test_config = {"name": "test", "version": 1.0, "enabled": True}
    
    result = demonstrate_type_hints(test_items, test_config)
    print(f"Result: {result}")
    
    if MAYA_AVAILABLE:
        create_maya_objects()
    
    sys.exit(app.exec())