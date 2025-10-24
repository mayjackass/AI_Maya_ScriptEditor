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
    from main_window import main
    
    print("Starting NEO Script Editor...")
    
    # Use the main() function which handles Maya parenting
    window = main()
    
    print("NEO Script Editor launched successfully!")
    print("Window should now be visible")
    
    # Don't call sys.exit in Maya - it would close Maya
    # The main() function returns the window for Maya usage
    
except Exception as e:
    print(f"❌ Launch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)