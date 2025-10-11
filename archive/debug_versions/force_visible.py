#!/usr/bin/env python
"""
Forced visible launcher - ensures window appears and stays visible
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore, QtGui

def force_window_visible():
    """Create and force window to be visible."""
    
    # Create application
    app = QtWidgets.QApplication(sys.argv)
    
    # Import and create window
    from main_window import AiScriptEditor
    window = AiScriptEditor()
    
    # Force window to center of screen and bring to front
    screen = app.primaryScreen().geometry()
    window_size = window.geometry()
    
    # Center the window
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)
    
    # Show and force to front
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Make sure it's not minimized
    window.setWindowState(QtCore.Qt.WindowNoState)
    
    # Force window to top and give it focus
    window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    window.show()  # Show again after flag change
    
    # Remove stay-on-top after a moment
    def remove_top_hint():
        window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        window.show()
        
    QtCore.QTimer.singleShot(1000, remove_top_hint)  # Remove after 1 second
    
    print("🎯 Window should now be forced visible!")
    print(f"   Position: ({window.x()}, {window.y()})")
    print(f"   Size: {window.width()}x{window.height()}")
    print(f"   Visible: {window.isVisible()}")
    print(f"   Active: {window.isActiveWindow()}")
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    print("🚀 FORCING WINDOW TO BE VISIBLE")
    print("=" * 40)
    
    try:
        exit_code = force_window_visible()
        print(f"Application exited with code: {exit_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)