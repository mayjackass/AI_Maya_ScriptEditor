#!/usr/bin/env python3
"""
Simple test to verify debugging system works independently of OpenAI.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore
from debug_system import DebugSession, DebugControlPanel
from editor.code_editor import CodeEditor

class DebugTestWindow(QtWidgets.QMainWindow):
    """Simple test window for debugging features."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEO Debug System Test")
        self.setGeometry(200, 200, 1000, 600)
        
        # Create main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Create code editor
        self.editor = CodeEditor()
        self.editor.setPlainText("""def test_function(x, y):
    result = x + y
    print(f"Adding {x} + {y} = {result}")
    return result

def main():
    a = 5
    b = 10
    total = test_function(a, b)
    print(f"Final result: {total}")

if __name__ == "__main__":
    main()
""")
        layout.addWidget(self.editor, 2)
        
        # Create debug session and panel
        self.debug_session = DebugSession()
        self.debug_panel = DebugControlPanel()
        self.debug_panel.set_debug_session(self.debug_session)
        layout.addWidget(self.debug_panel, 1)
        
        # Connect debug session to editor
        self.debug_session.debugPaused.connect(self._on_debug_paused)
        self.debug_session.debugStopped.connect(self._on_debug_stopped)
        
        # Add some test breakpoints
        self.editor.set_breakpoint(3)
        self.editor.set_breakpoint(8)
        
        print("Debug test window created successfully!")
        print("- Code editor with sample Python code")
        print("- Debug control panel")  
        print("- Breakpoints set at lines 3 and 8")
        print("- Red circles should be visible in line numbers")
        
    def _on_debug_paused(self, line_number):
        """Handle debug pause."""
        self.editor.set_current_debug_line(line_number)
        print(f"Debug paused at line {line_number}")
        
    def _on_debug_stopped(self):
        """Handle debug stop."""
        self.editor.clear_debug_line()
        print("Debug session stopped")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet("""
        QWidget { 
            background: #1E1E1E; 
            color: #DDD; 
            font-family: 'Consolas', 'Courier New', monospace;
        }
        QTextEdit, QPlainTextEdit { 
            background: #252526; 
            border: 1px solid #3E3E42;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11pt;
        }
        QPushButton { 
            background: #2D2D30; 
            border: 1px solid #464647;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover { background: #3E3E40; }
        QPushButton:pressed { background: #1E1E1E; }
    """)
    
    window = DebugTestWindow()
    window.show()
    
    sys.exit(app.exec())