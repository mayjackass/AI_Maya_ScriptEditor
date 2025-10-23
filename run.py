#!/usr/bin/env python
"""
Simple launcher for NEO Script Editor
Compatible with Maya 2022-2024 (PySide2) and Maya 2025+ (PySide6)
"""

import sys
import os

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import and run
try:
    from qt_compat import QtWidgets, QT_VERSION, app_exec
    from main_window import AiScriptEditor
    
    print("Starting NEO Script Editor...")
    print(f"Using Qt version: {QT_VERSION}")
    
    # Create application
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    window.show()
    
    print("NEO Script Editor launched successfully!")
    print("Window should now be visible")
    
    sys.exit(app_exec(app))
    
except Exception as e:
    print(f"❌ Launch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)