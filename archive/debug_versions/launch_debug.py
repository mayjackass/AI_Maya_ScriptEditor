#!/usr/bin/env python
"""
Debug launcher with comprehensive error catching
"""

import sys
import os
import traceback

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

def debug_launch():
    """Launch with detailed error reporting."""
    
    try:
        print("🔧 Step 1: Importing PySide6...")
        from PySide6 import QtWidgets, QtCore, QtGui
        print("✅ PySide6 imported successfully")
        
        print("🔧 Step 2: Creating QApplication...")
        app = QtWidgets.QApplication(sys.argv)
        print("✅ QApplication created")
        
        print("🔧 Step 3: Importing main window...")
        from main_window import AiScriptEditor
        print("✅ AiScriptEditor imported")
        
        print("🔧 Step 4: Creating window instance...")
        try:
            window = AiScriptEditor()
            print("✅ Window instance created")
        except Exception as e:
            print(f"❌ Window creation failed: {e}")
            traceback.print_exc()
            return 1
            
        print("🔧 Step 5: Showing window...")
        try:
            window.show()
            print("✅ Window.show() called")
        except Exception as e:
            print(f"❌ Window.show() failed: {e}")
            traceback.print_exc()
            return 1
            
        print("🔧 Step 6: Raising and activating window...")
        try:
            window.raise_()
            window.activateWindow()
            print("✅ Window raised and activated")
        except Exception as e:
            print(f"❌ Window raise/activate failed: {e}")
            traceback.print_exc()
            
        print("🔧 Step 7: Processing events...")
        try:
            app.processEvents()
            print("✅ Events processed")
        except Exception as e:
            print(f"❌ Event processing failed: {e}")
            traceback.print_exc()
            
        print("🔧 Step 8: Window state check...")
        try:
            print(f"   Window visible: {window.isVisible()}")
            print(f"   Window size: {window.size().width()}x{window.size().height()}")
            print(f"   Window position: ({window.x()}, {window.y()})")
            print(f"   Window title: '{window.windowTitle()}'")
        except Exception as e:
            print(f"❌ Window state check failed: {e}")
            traceback.print_exc()
            
        print("🔧 Step 9: Starting event loop...")
        try:
            print("🎯 If you see this message, the window should be visible!")
            print("   Check your taskbar or try Alt+Tab to find the window")
            return app.exec()
        except Exception as e:
            print(f"❌ Event loop failed: {e}")
            traceback.print_exc()
            return 1
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("=" * 60)
    print("🐛 DEBUG LAUNCHER - DETAILED ERROR REPORTING")
    print("=" * 60)
    exit_code = debug_launch()
    print(f"\n🏁 Process completed with exit code: {exit_code}")
    sys.exit(exit_code)