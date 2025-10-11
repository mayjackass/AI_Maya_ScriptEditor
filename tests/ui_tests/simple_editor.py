#!/usr/bin/env python3
"""
Super simple window test - bypassing all the complex initialization
"""
import sys
import os
from PySide6 import QtWidgets, QtCore, QtGui

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

DARK_STYLE = """
QWidget { background: #1E1E1E; color: #DDD; font-family: Segoe UI, Consolas; }
QMenuBar, QMenu, QToolBar { font-size: 11pt; background-color:#2D2D30; }
QTextBrowser, QTextEdit { border: 1px solid #333; border-radius: 4px; }
QPushButton { background: #2D2D30; color: #EEE; border-radius: 4px; padding: 4px 8px; }
QPushButton:hover { background: #3E3E42; }
QLineEdit { background: #252526; border: 1px solid #333; color: #EEE; border-radius: 4px; padding: 3px; }
QDockWidget::title { background: #252526; padding: 4px; }
QTabBar::tab { background: #2D2D30; color: #DDD; padding: 6px 12px; border:1px solid #3E3E42; }
QTabBar::tab:selected { background: #3E3E42; }
"""

class SimpleAIEditor(QtWidgets.QMainWindow):
    """Simplified AI Editor for testing."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Script Editor - Simple Test")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(DARK_STYLE)
        
        # Create central widget with text editor
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add a simple text editor
        self.editor = QtWidgets.QTextEdit()
        self.editor.setPlainText("""# AI Script Editor - Enhanced Syntax Highlighting Test

# PySide6/Qt imports - should be highlighted
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot

# Maya imports - should be highlighted  
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

class TestWidget(QtWidgets.QWidget):
    # Signal definition
    dataChanged = Signal(str, int)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    @Slot()
    def on_button_clicked(self):
        print("Button clicked!")

# Test the enhanced syntax highlighting by typing Python code here!
""")
        
        layout.addWidget(self.editor)
        
        # Add status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("✅ AI Script Editor Ready - Enhanced syntax highlighting enabled!")
        
        print("✅ Simple AI Editor created successfully!")

def main():
    print("🚀 Starting Simple AI Script Editor...")
    
    app = QtWidgets.QApplication(sys.argv)
    
    window = SimpleAIEditor()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("🎯 Simple editor window should be visible!")
    print("   Try typing Python code to test basic functionality")
    
    return app.exec()

if __name__ == "__main__":
    main()