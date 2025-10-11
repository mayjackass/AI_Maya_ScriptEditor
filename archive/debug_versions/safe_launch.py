#!/usr/bin/env python
"""
Exception catching launcher to find any silent failures
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Override the default exception handler to catch everything
def custom_except_hook(exc_type, exc_value, exc_traceback):
    print(f"🚨 UNCAUGHT EXCEPTION: {exc_type.__name__}: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_except_hook

def safe_launch():
    """Launch with maximum error catching."""
    
    try:
        print("Step 1: Importing Qt...")
        from PySide6 import QtWidgets, QtCore
        
        print("Step 2: Creating QApplication...")
        app = QtWidgets.QApplication(sys.argv)
        
        print("Step 3: Setting up exception handling...")
        # Install Qt message handler
        def qt_message_handler(mode, context, message):
            print(f"Qt {mode}: {message}")
            
        QtCore.qInstallMessageHandler(qt_message_handler)
        
        print("Step 4: Importing main window...")
        from main_window import AiScriptEditor
        
        print("Step 5: Creating window with try-catch...")
        window = None
        try:
            window = AiScriptEditor()
            print("✅ Window created successfully!")
        except Exception as e:
            print(f"❌ Window creation failed: {e}")
            traceback.print_exc()
            return 1
            
        print("Step 6: Showing window...")
        try:
            window.show()
            print("✅ Window.show() completed")
        except Exception as e:
            print(f"❌ Window.show() failed: {e}")
            traceback.print_exc()
            return 1
            
        print("Step 7: Starting event loop...")
        try:
            print("🎯 Starting Qt event loop - window should be visible!")
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
    print("🛡️ MAXIMUM EXCEPTION CATCHING MODE")
    print("=" * 50)
    
    exit_code = safe_launch()
    print(f"\n🏁 Exit code: {exit_code}")
    
    if exit_code != 0:
        input("Press Enter to continue...")  # Keep console open on error
        
    sys.exit(exit_code)