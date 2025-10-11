#!/usr/bin/env python3
"""
Enhanced Python Syntax Highlighting Test
Tests all new features including PySide6, Qt, Maya, triple quotes, f-strings, etc.
"""

import os
import sys
import re
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Union, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path
import logging

# PySide6/Qt imports - should be highlighted in cyan
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import (QObject, QThread, QTimer, QSignal, QSlot, 
                           QApplication, QEvent, QEventLoop, QRect, QSize, QPoint)
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QLineEdit, QTextEdit,
                              QMessageBox, QFileDialog, QProgressBar)
from PySide6.QtGui import (QPixmap, QIcon, QFont, QColor, QPalette, QPainter,
                          QKeyEvent, QMouseEvent, QPaintEvent, QResizeEvent)

# Maya Python imports - should be highlighted in cyan  
try:
    import maya.cmds as cmds
    import maya.mel as mel
    import pymel.core as pm
    import maya.api.OpenMaya as om
    import maya.api.OpenMayaUI as omui
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
    executeDeferred = cmds.evalDeferred
except ImportError:
    print("Maya modules not available")

# Popular libraries - should be highlighted in cyan
import requests
import sqlite3
from collections import defaultdict, OrderedDict, Counter
from itertools import chain, combinations, permutations
from functools import lru_cache, partial, wraps
import concurrent.futures
from threading import Thread, Lock, Event
from multiprocessing import Process, Queue, Pool
import argparse
import configparser
from datetime import datetime, timedelta, timezone
import hashlib
import base64
import uuid
import pickle

# Triple quote strings - should be highlighted in orange
multi_line_docstring = """
This is a multi-line docstring that should be 
properly highlighted in orange color.

It can contain multiple paragraphs and should
maintain highlighting across all lines.
"""

raw_multi_line = r"""
This is a raw multi-line string with backslashes: \n\t\r
Path: C:\Users\Path\To\File.txt
Regex: \d+\.\d+\s*[a-zA-Z]+
"""

# F-strings - should be highlighted in orange with special formatting
name = "World"
value = 42
pi = 3.14159

# Regular f-strings
simple_f_string = f"Hello, {name}!"
complex_f_string = f"Value: {value}, Pi: {pi:.2f}, Hex: {value:x}"

# Raw f-strings  
raw_f_string = rf"Path: C:\Users\{name}\Documents\file_{value:03d}.txt"

# Multi-line f-strings
multi_f_string = f"""
Name: {name}
Value: {value}
Calculation: {value * pi:.3f}
"""

# F-string with expressions
expression_f_string = f"Result: {value * 2 + 10}, Square: {value**2}"

# Numbers - all formats should be highlighted in light green
integers = [42, 1000, -5, 0]
floats = [3.14, -2.5, 0.001, 1.23e-4, 2.5E+3]
hex_numbers = [0xFF, 0x00AA, 0xDEADBEEF]
binary_numbers = [0b1101, 0b11110000, 0B10101010]
octal_numbers = [0o755, 0o644, 0O777]
scientific = [1.23e-10, 2.34E+5, -1.5e3]

# Class with type hints and decorators
@dataclass
class Person:
    """Person class with comprehensive type hints."""
    name: str
    age: int
    active: bool = True
    scores: List[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.scores is None:
            self.scores = []
        if self.metadata is None:
            self.metadata = {}

# Qt/PySide6 GUI Class
class MainWindow(QMainWindow):
    """Main application window using PySide6."""
    
    # Qt Signals - should be highlighted
    dataChanged = QtCore.Signal(str)
    progressUpdated = QtCore.Signal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUI()
        self.connectSignals()
    
    def setupUI(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout setup
        layout = QVBoxLayout(central_widget)
        
        # Widgets
        self.label = QLabel("Enhanced Syntax Highlighting Demo")
        self.line_edit = QLineEdit()
        self.text_edit = QTextEdit()
        self.button = QPushButton("Process")
        self.progress_bar = QProgressBar()
        
        # Add to layout
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button)
        layout.addWidget(self.progress_bar)
        
        # Styling
        self.setWindowTitle("Python Syntax Highlighting Test")
        self.setGeometry(QRect(100, 100, 800, 600))
        
        # Font and colors
        font = QFont("Consolas", 12)
        self.setFont(font)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)
    
    @QtCore.Slot()
    def connectSignals(self):
        """Connect Qt signals and slots."""
        self.button.clicked.connect(self.processData)
        self.dataChanged.connect(self.updateDisplay)
        self.progressUpdated.connect(self.progress_bar.setValue)
    
    @QtCore.Slot()
    def processData(self):
        """Process data with progress updates."""
        text = self.line_edit.text()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter some text")
            return
        
        # Emit signals
        self.dataChanged.emit(f"Processing: {text}")
        
        # Simulate processing with progress
        for i in range(101):
            self.progressUpdated.emit(i)
            QtCore.QThread.msleep(10)  # Small delay
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key.Key_F5:
            self.processData()
        else:
            super().keyPressEvent(event)

# Maya integration class (if Maya available)
try:
    class MayaTools(MayaQWidgetBaseMixin, QWidget):
        """Maya-specific tools using Maya Python API."""
        
        def __init__(self):
            super().__init__()
            self.setupMayaUI()
        
        def setupMayaUI(self):
            """Setup Maya-specific UI elements."""
            layout = QVBoxLayout(self)
            
            # Maya command buttons
            create_cube_btn = QPushButton("Create Cube")
            create_sphere_btn = QPushButton("Create Sphere")
            select_all_btn = QPushButton("Select All")
            
            create_cube_btn.clicked.connect(self.createCube)
            create_sphere_btn.clicked.connect(self.createSphere)
            select_all_btn.clicked.connect(self.selectAll)
            
            layout.addWidget(create_cube_btn)
            layout.addWidget(create_sphere_btn)
            layout.addWidget(select_all_btn)
        
        def createCube(self):
            """Create a cube in Maya."""
            cube = cmds.polyCube(name="testCube")[0]
            cmds.move(0, 2, 0, cube)
            return cube
        
        def createSphere(self):
            """Create a sphere using PyMEL."""
            sphere = pm.polySphere(name="testSphere")[0]
            sphere.translateY.set(4)
            return sphere
        
        def selectAll(self):
            """Select all objects in the scene."""
            all_objects = cmds.ls(dag=True, shapes=True)
            if all_objects:
                cmds.select(all_objects)
            
        def getSelectedObjects(self) -> List[str]:
            """Get currently selected objects using OpenMaya."""
            selection_list = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(selection_list)
            
            objects = []
            for i in range(selection_list.length()):
                dag_path = selection_list.getDagPath(i)
                objects.append(dag_path.fullPathName())
            
            return objects

except (ImportError, NameError):
    print("Maya integration not available")

# Async functions - modern Python features
async def async_data_processor(data: List[Dict[str, Any]]) -> List[str]:
    """Async function for processing data."""
    results = []
    
    async def process_item(item: Dict[str, Any]) -> str:
        # Simulate async processing
        await asyncio.sleep(0.1)
        return f"Processed: {item.get('name', 'Unknown')}"
    
    # Process items concurrently
    tasks = [process_item(item) for item in data]
    results = await asyncio.gather(*tasks)
    
    return results

# Context manager with magic methods
class ResourceManager:
    """Context manager with magic methods."""
    
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.is_open = False
    
    def __enter__(self):
        print(f"Opening resource: {self.resource_name}")
        self.is_open = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing resource: {self.resource_name}")
        self.is_open = False
        return False
    
    def __str__(self) -> str:
        status = "open" if self.is_open else "closed"
        return f"ResourceManager({self.resource_name}, {status})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __len__(self) -> int:
        return len(self.resource_name)
    
    def __call__(self, *args, **kwargs):
        return f"Called with args: {args}, kwargs: {kwargs}"

# Decorators and advanced features
def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"{func.__name__} took {duration:.3f} seconds")
        return result
    return wrapper

@timing_decorator
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Cached fibonacci calculation."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Exception handling with custom exceptions
class CustomProcessingError(Exception):
    """Custom exception for processing errors."""
    
    def __init__(self, message: str, error_code: int = None):
        super().__init__(message)
        self.error_code = error_code

def risky_operation(value: Any) -> str:
    """Function that might raise various exceptions."""
    try:
        if isinstance(value, str):
            return json.dumps({"processed": value.upper()})
        elif isinstance(value, (int, float)):
            if value < 0:
                raise ValueError("Negative values not allowed")
            return str(value ** 2)
        else:
            raise CustomProcessingError(f"Unsupported type: {type(value)}", 400)
    
    except (TypeError, ValueError) as e:
        logging.error(f"Standard error: {e}")
        raise
    except CustomProcessingError as e:
        logging.error(f"Custom error: {e}, Code: {e.error_code}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Failed to process {value}") from e

# Main execution with comprehensive error handling
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test data processing
    test_data = [
        {"name": "item1", "value": 42},
        {"name": "item2", "value": 3.14},
        {"name": "item3", "value": "hello"}
    ]
    
    # Test async processing
    async def main():
        results = await async_data_processor(test_data)
        print("Async results:", results)
    
    # Test Qt application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Test context manager
    with ResourceManager("test_resource") as rm:
        print(f"Using resource: {rm}")
        print(f"Resource length: {len(rm)}")
        print(rm("test", key="value"))
    
    # Test fibonacci with timing
    fib_result = fibonacci(35)
    print(f"Fibonacci(35) = {fib_result}")
    
    # Test exception handling
    try:
        risky_operation(-5)
    except Exception as e:
        print(f"Caught exception: {e}")
    
    # Run the application
    print("Starting Qt application...")
    # app.exec()  # Uncomment to run GUI
    
    # Run async code
    asyncio.run(main())