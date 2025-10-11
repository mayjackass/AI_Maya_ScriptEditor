#!/usr/bin/env python
"""
Simple launcher that mimics exactly how main_window.py works
"""

import sys
import os

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import and run exactly like main_window.py does
try:
    from PySide6 import QtWidgets
    from main_window import AiScriptEditor
    
    print("🚀 Starting NEO Script Editor...")
    
    # Use the exact same pattern as main_window.py
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    window.show()
    
    print("✅ NEO Script Editor launched successfully!")
    print("🎯 Window should now be visible")
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"❌ Launch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)