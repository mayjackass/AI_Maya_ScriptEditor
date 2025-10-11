#!/usr/bin/env python
"""
Simple test to isolate the window creation issue
"""

import sys
import os

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔧 Step 1: Importing PySide6...")
    from PySide6 import QtWidgets, QtCore
    print("✅ PySide6 imported successfully")
    
    print("🔧 Step 2: Creating QApplication...")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    print("✅ QApplication created successfully")
    
    print("🔧 Step 3: Importing main window...")
    from main_window import AiScriptEditor
    print("✅ AiScriptEditor imported successfully")
    
    print("🔧 Step 4: Creating window instance...")
    window = AiScriptEditor()
    print("✅ AiScriptEditor instance created successfully")
    
    print("🔧 Step 5: Showing window...")
    window.show()
    print("✅ Window shown successfully")
    
    print("🔧 Step 6: Starting event loop...")
    print("🎯 Window should be visible now!")
    
    # Simple event loop without exec to avoid hanging
    app.processEvents()
    print("✅ Event processing completed")
    
    print("\n🎉 SUCCESS: All steps completed without errors!")
    print("If you don't see the window, there might be a display issue.")
    
    # Keep it alive briefly to test
    import time
    time.sleep(2)
    app.processEvents()
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)