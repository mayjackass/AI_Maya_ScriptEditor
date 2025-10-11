#!/usr/bin/env python3
"""
Debug version of the modular main window to find the exact failure point
"""
import sys
import os

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    print("🔍 Step 1: Importing PySide6...")
    from PySide6 import QtWidgets, QtCore, QtGui
    print("✅ PySide6 imported successfully")

    print("🔍 Step 2: Importing main window...")
    from main_window import ScriptEditorWindow
    print("✅ Main window class imported")

    print("🔍 Step 3: Creating QApplication...")
    app = QtWidgets.QApplication(sys.argv)
    print("✅ QApplication created")

    print("🔍 Step 4: Creating window instance...")
    
    # Let's create a minimal version first to test basic Qt
    class MinimalWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Debug - Minimal Window")
            self.setGeometry(100, 100, 400, 300)
            
            # Just a text widget
            central = QtWidgets.QTextEdit()
            central.setPlainText("Debug: This is a minimal test window")
            self.setCentralWidget(central)
            
            print("✅ Minimal window created successfully")

    print("🔍 Step 4a: Testing minimal window...")
    minimal_window = MinimalWindow()
    minimal_window.show()
    minimal_window.raise_()
    print("✅ Minimal window shown - if you can see this, Qt is working")
    
    # Close minimal window and try the full one
    minimal_window.close()
    
    print("🔍 Step 4b: Now testing full ScriptEditorWindow...")
    try:
        window = ScriptEditorWindow()
        print("✅ ScriptEditorWindow created successfully")
        
        print("🔍 Step 5: Showing window...")
        window.show()
        window.raise_()
        window.activateWindow()
        print("✅ Window shown successfully")
        
        print("🎯 Full AI Script Editor should now be visible!")
        
    except Exception as e:
        print(f"❌ Error creating ScriptEditorWindow: {e}")
        import traceback
        traceback.print_exc()
        
        # Fall back to minimal window
        print("🔄 Falling back to minimal window...")
        fallback = MinimalWindow()
        fallback.setWindowTitle("AI Script Editor - Fallback Mode")
        fallback.show()
        window = fallback

    # Run the app
    sys.exit(app.exec())

except Exception as e:
    print(f"❌ Critical error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)