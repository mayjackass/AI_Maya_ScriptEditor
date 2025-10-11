#!/usr/bin/env python
"""
Fixed launch script for NEO Script Editor - handles Qt application properly
"""

import sys
import os

def launch_neo_editor():
    """Launch NEO Script Editor safely."""
    
    # Add script directory to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    try:
        print("🔧 Importing Qt...")
        from PySide6 import QtWidgets
        print("✅ PySide6 imported")
        
        print("🔧 Importing main window...")
        from main_window import AiScriptEditor
        print("✅ Main window class imported")
        
        print("🔧 Checking for existing QApplication...")
        app = QtWidgets.QApplication.instance()
        created_new_app = False
        
        if app is None:
            print("🚀 Creating new QApplication...")
            app = QtWidgets.QApplication(sys.argv)
            created_new_app = True
        else:
            print("🔗 Using existing QApplication")
        
        print("🏗️ Creating window instance...")
        window = AiScriptEditor()
        print("✅ Window created successfully")
        
        print("🎯 Showing window...")
        window.show()
        print("✅ Window should now be visible!")
        
        # Only run event loop if we created the app
        if created_new_app:
            print("🔄 Starting event loop...")
            return app.exec()
        else:
            print("✅ Window ready (using existing event loop)")
            return 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = launch_neo_editor()
    sys.exit(exit_code)