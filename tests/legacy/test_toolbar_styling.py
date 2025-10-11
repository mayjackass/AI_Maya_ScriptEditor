#!/usr/bin/env python3
"""
Test the new organized toolbar and VS Code styling.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore
from main_window import AiScriptEditor

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Create and show the main window
    window = AiScriptEditor()
    window.show()
    
    print("NEO Script Editor with organized toolbars and VS Code styling!")
    print("Features:")
    print("✅ Organized toolbars (File, Debug, Run)")
    print("✅ VS Code color theme (gray, white, blue highlights)")
    print("✅ Professional status bar with file info")
    print("✅ Clean icon layout")
    print("✅ Hover effects and proper spacing")
    
    sys.exit(app.exec())