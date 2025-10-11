#!/usr/bin/env python3
"""
Step-by-step manager initialization test
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from PySide6 import QtWidgets, QtCore, QtGui

# Import managers individually
print("🔍 Importing managers...")
from ui.components.ui_manager import UIManager
from ui.components.file_manager import FileManager  
from ui.components.syntax_manager import SyntaxManager
from ui.components.ai_manager import AIManager
print("✅ All managers imported")

class StepByStepWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Script Editor - Step by Step Init")
        self.setGeometry(100, 100, 1000, 700)
        
        print("🔍 Starting step-by-step initialization...")
        
        try:
            print("🔍 Step 1: Initializing UIManager...")
            self.ui_manager = UIManager(self)
            print("✅ UIManager initialized")
            
            print("🔍 Step 2: Initializing FileManager...")
            self.file_manager = FileManager(self)
            print("✅ FileManager initialized")
            
            print("🔍 Step 3: Initializing SyntaxManager...")
            self.syntax_manager = SyntaxManager(self)
            print("✅ SyntaxManager initialized")
            
            print("🔍 Step 4: Initializing AIManager...")
            self.ai_manager = AIManager(self)
            print("✅ AIManager initialized")
            
            print("🔍 Step 5: Setting up basic UI...")
            self._setup_basic_ui()
            print("✅ Basic UI setup complete")
            
            print("🎯 All managers initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            
            # Create fallback UI
            self._setup_fallback_ui()
            
    def _setup_basic_ui(self):
        """Setup a basic UI to test the window."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add title
        title = QtWidgets.QLabel("🚀 AI Script Editor - Modular Version")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Add status
        status = QtWidgets.QLabel("✅ All managers initialized successfully!")
        status.setStyleSheet("color: green; padding: 5px;")
        layout.addWidget(status)
        
        # Add simple editor
        editor = QtWidgets.QTextEdit()
        editor.setPlainText("""# AI Script Editor - Working!
# The modular version is now running with all managers:
# • UIManager ✅
# • FileManager ✅  
# • SyntaxManager ✅
# • AIManager ✅

# Try typing some Python code here to test!
from PySide6 import QtWidgets
print("Hello from AI Script Editor!")
""")
        layout.addWidget(editor)
        
        # Status bar
        self.statusBar().showMessage("✅ AI Script Editor modular version running successfully!")
        
    def _setup_fallback_ui(self):
        """Fallback UI if managers fail."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        error_label = QtWidgets.QLabel("⚠️ Manager initialization failed - running in fallback mode")
        error_label.setStyleSheet("color: orange; font-size: 14px; padding: 10px;")
        layout.addWidget(error_label)
        
        editor = QtWidgets.QTextEdit()
        editor.setPlainText("# Fallback mode - basic editor only")
        layout.addWidget(editor)

def main():
    print("🚀 Testing modular AI Script Editor initialization...")
    
    app = QtWidgets.QApplication(sys.argv)
    
    window = StepByStepWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("🎯 Window should now be visible!")
    
    return app.exec()

if __name__ == "__main__":
    main()