#!/usr/bin/env python3
"""
AI Script Editor with Enhanced Syntax Highlighting - Working Version
Includes the advanced CodeEditor and syntax highlighting features
"""
import sys
import os
from PySide6 import QtWidgets, QtCore, QtGui

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import our enhanced editor
from editor.code_editor import CodeEditor
from editor.highlighter import PythonHighlighter, MELHighlighter

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

class EnhancedAIEditor(QtWidgets.QMainWindow):
    """Enhanced AI Script Editor with VSCode-style syntax highlighting."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 AI Script Editor - Enhanced Syntax Highlighting & Error Detection")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(DARK_STYLE)
        
        self._setup_ui()
        self._setup_menu()
        
        print("✅ Enhanced AI Script Editor initialized successfully!")
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Main widget
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(main_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        toolbar_widget = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Language selector
        lang_label = QtWidgets.QLabel("Language:")
        lang_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        toolbar_layout.addWidget(lang_label)
        
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItems(["🐍 Python", "🔧 MEL Script"])
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        toolbar_layout.addWidget(self.language_combo)
        
        toolbar_layout.addStretch()
        
        # File operations
        new_btn = QtWidgets.QPushButton("📄 New")
        new_btn.clicked.connect(self._new_file)
        toolbar_layout.addWidget(new_btn)
        
        open_btn = QtWidgets.QPushButton("📁 Open")
        open_btn.clicked.connect(self._open_file)
        toolbar_layout.addWidget(open_btn)
        
        save_btn = QtWidgets.QPushButton("💾 Save")
        save_btn.clicked.connect(self._save_file)
        toolbar_layout.addWidget(save_btn)
        
        # Test button to load sample code
        test_btn = QtWidgets.QPushButton("🧪 Load Test Code")
        test_btn.clicked.connect(self._load_test_code)
        toolbar_layout.addWidget(test_btn)
        
        layout.addWidget(toolbar_widget)
        
        # Tab widget for multiple editors
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("✅ Enhanced AI Script Editor Ready!")
        
        # Create initial tab
        self._new_file()
        
    def _setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QtGui.QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QtGui.QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QtGui.QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QtGui.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _new_file(self):
        """Create a new file tab."""
        try:
            editor = CodeEditor()
            
            # Set language based on combo box
            lang = self.language_combo.currentText()
            if "Python" in lang:
                editor.set_language("python")
            else:
                editor.set_language("mel")
            
            # Connect error signals
            if hasattr(editor, 'errorDetected'):
                editor.errorDetected.connect(self._on_error_detected)
            if hasattr(editor, 'errorsCleared'):
                editor.errorsCleared.connect(self._on_errors_cleared)
            
            # Add tab
            index = self.tab_widget.addTab(editor, "untitled")
            self.tab_widget.setCurrentIndex(index)
            
            self.status_bar.showMessage("✅ New file created")
            
        except Exception as e:
            self.status_bar.showMessage(f"❌ Error creating file: {e}")
            print(f"Error in _new_file: {e}")
            import traceback
            traceback.print_exc()
        
    def _open_file(self):
        """Open a file."""
        try:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open File", "", 
                "Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                editor = CodeEditor()
                editor.setPlainText(content)
                
                # Set language based on file extension
                if file_path.endswith('.mel'):
                    editor.set_language("mel")
                    self.language_combo.setCurrentText("🔧 MEL Script")
                else:
                    editor.set_language("python")
                    self.language_combo.setCurrentText("🐍 Python")
                
                # Connect error signals
                if hasattr(editor, 'errorDetected'):
                    editor.errorDetected.connect(self._on_error_detected)
                if hasattr(editor, 'errorsCleared'):
                    editor.errorsCleared.connect(self._on_errors_cleared)
                
                filename = os.path.basename(file_path)
                index = self.tab_widget.addTab(editor, filename)
                self.tab_widget.setCurrentIndex(index)
                
                # Store file path
                editor._file_path = file_path
                
                self.status_bar.showMessage(f"✅ Opened: {filename}")
                
        except Exception as e:
            self.status_bar.showMessage(f"❌ Error opening file: {e}")
            
    def _save_file(self):
        """Save current file."""
        try:
            current_editor = self.tab_widget.currentWidget()
            if not current_editor:
                return
            
            # Get file path
            if hasattr(current_editor, '_file_path'):
                file_path = current_editor._file_path
            else:
                file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                    self, "Save File", "",
                    "Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
                )
                if not file_path:
                    return
            
            # Save content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(current_editor.toPlainText())
            
            current_editor._file_path = file_path
            
            # Update tab title
            filename = os.path.basename(file_path)
            current_index = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(current_index, filename)
            
            self.status_bar.showMessage(f"✅ Saved: {filename}")
            
        except Exception as e:
            self.status_bar.showMessage(f"❌ Error saving file: {e}")
            
    def _close_tab(self, index):
        """Close a tab."""
        if self.tab_widget.count() <= 1:
            self._new_file()
        self.tab_widget.removeTab(index)
        
    def _on_language_changed(self, language):
        """Handle language change."""
        current_editor = self.tab_widget.currentWidget()
        if current_editor:
            if "Python" in language:
                current_editor.set_language("python")
            else:
                current_editor.set_language("mel")
                
    def _load_test_code(self):
        """Load test code to demonstrate syntax highlighting."""
        test_code = '''#!/usr/bin/env python3
"""
Test Python file demonstrating enhanced syntax highlighting and error detection.
This showcases various Python constructs including PySide6/Qt and Maya code.
"""

# Standard imports with syntax highlighting
import sys, os, json
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


class TestWidget(QWidget):
    """Test widget demonstrating PySide6 features with enhanced highlighting."""
    
    # Signal definition - should be highlighted
    dataChanged = Signal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface with Qt widgets."""
        layout = QVBoxLayout()
        
        # Various Qt widgets - all should be highlighted
        self.label = QtWidgets.QLabel("Enhanced Syntax Test")
        self.button = QtWidgets.QPushButton("Test Button")  
        self.line_edit = QtWidgets.QLineEdit()
        
        # Connect signals and slots - should be highlighted
        self.button.clicked.connect(self.on_button_clicked)
        
        layout.addWidget(self.label)
        layout.addWidget(self.button) 
        layout.addWidget(self.line_edit)
        
        self.setLayout(layout)
        
    @Slot()  # Decorator should be highlighted
    def on_button_clicked(self):
        """Handle button click with enhanced error detection."""
        text = self.line_edit.text()
        self.dataChanged.emit(text, len(text))
        
        # F-string usage - should be highlighted
        message = f"Button clicked with text: '{text}'"
        print(message)


def create_maya_objects():
    """Maya-specific code with enhanced highlighting."""
    if not MAYA_AVAILABLE:
        return
        
    # Maya commands - should be highlighted in special color
    cube = cmds.polyCube(name="enhanced_test_cube")[0]
    cmds.move(0, 5, 0, cube)
    cmds.rotate(45, 0, 0, cube)
    
    # Maya API usage - should be highlighted
    selection_list = OpenMaya.MSelectionList()
    cmds.select(cube)
    OpenMaya.MGlobal.getActiveSelectionList(selection_list)


def demonstrate_features(items: List[str], config: Dict[str, Any]) -> Optional[str]:
    """Function demonstrating modern Python features and type hints."""
    
    result = None
    
    try:
        # List comprehension with enhanced highlighting
        filtered_items = [item.upper() for item in items if len(item) > 3]
        
        # Dictionary operations with proper highlighting
        for key, value in config.items():
            if isinstance(value, (str, int, float)):
                result = f"Processing {key}: {value}"
                break
                
    except (ValueError, KeyError, TypeError) as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        print("Processing completed")
        
    return result


# Test async/await syntax - should be highlighted
async def async_example():
    """Async function example with proper highlighting."""
    await asyncio.sleep(1)
    return "Async completed"


if __name__ == "__main__":
    # Main execution with enhanced highlighting
    app = QApplication(sys.argv)
    
    widget = TestWidget()
    widget.show()
    
    # Sample data for testing
    test_items = ["python", "pyside6", "maya", "qt", "enhanced"]
    test_config = {"name": "test", "version": 2.0, "enabled": True}
    
    result = demonstrate_features(test_items, test_config)
    print(f"Demo result: {result}")
    
    if MAYA_AVAILABLE:
        create_maya_objects()
    
    sys.exit(app.exec())

# Try adding syntax errors here to test error detection:
# if True  # Missing colon - should show red wavy underline
#     print("Error")
'''
        
        # Create new tab with test code
        editor = CodeEditor()
        editor.setPlainText(test_code)
        editor.set_language("python")
        
        # Connect error signals
        if hasattr(editor, 'errorDetected'):
            editor.errorDetected.connect(self._on_error_detected)
        if hasattr(editor, 'errorsCleared'):
            editor.errorsCleared.connect(self._on_errors_cleared)
        
        index = self.tab_widget.addTab(editor, "test_enhanced_syntax.py")
        self.tab_widget.setCurrentIndex(index)
        
        self.status_bar.showMessage("✅ Test code loaded - Check the enhanced syntax highlighting!")
        
    def _on_error_detected(self, line, message):
        """Handle syntax error detection."""
        self.status_bar.showMessage(f"❌ Syntax Error on line {line}: {message}")
        
    def _on_errors_cleared(self):
        """Handle when errors are cleared."""
        self.status_bar.showMessage("✅ No syntax errors detected")
        
    def _show_about(self):
        """Show about dialog."""
        QtWidgets.QMessageBox.about(self, "About", 
            """🚀 AI Script Editor - Enhanced Version

✨ Features:
• VSCode-style syntax highlighting
• Real-time error detection with red wavy underlines  
• Comprehensive PySide6/Qt framework support
• Maya Python API highlighting
• Modern Python features (type hints, f-strings, async/await)
• Popular libraries support (NumPy, Pandas, etc.)

🎯 Try the 'Load Test Code' button to see all features in action!""")


def main():
    print("🚀 Starting Enhanced AI Script Editor...")
    print("   Features: VSCode-style syntax highlighting, real-time error detection")
    
    app = QtWidgets.QApplication(sys.argv)
    
    window = EnhancedAIEditor()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("🎯 Enhanced AI Script Editor is now running!")
    print("   • Click 'Load Test Code' to see syntax highlighting")
    print("   • Try typing Python code to test error detection")
    print("   • PySide6/Qt classes should be highlighted in different colors")
    
    return app.exec()


if __name__ == "__main__":
    main()