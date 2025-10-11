#!/usr/bin/env python3
"""
Minimal test to see the main window
"""
import sys
import os

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from PySide6 import QtWidgets, QtCore
    
    print("🔍 Testing main window import...")
    
    # Import the main window class
    from main_window import ScriptEditorWindow
    
    print("✅ Import successful, creating application...")
    
    app = QtWidgets.QApplication(sys.argv)
    
    print("✅ Creating main window...")
    window = ScriptEditorWindow()
    
    print("✅ Setting window properties...")
    window.setWindowTitle("AI Script Editor - Test")
    window.resize(800, 600)
    
    # Force window to show and raise to top
    print("✅ Showing window...")
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Make sure it's visible
    window.setWindowState(QtCore.Qt.WindowNoState)
    
    print("🎯 Window should now be visible!")
    print("   If you can't see it, try checking your taskbar")
    
    # Keep window open for testing
    sys.exit(app.exec())
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)