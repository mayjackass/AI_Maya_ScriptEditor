#!/usr/bin/env python3
"""
Test the import fixes for Maya integration.
"""

import sys
import os

# Test the Maya-style import
try:
    # Add the ai_script_editor directory to path like Maya would
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    print("Testing import from ai_script_editor module...")
    print(f"Script directory: {script_dir}")
    print(f"Python path includes: {script_dir in sys.path}")
    
    # Import the launcher
    import ai_script_editor
    
    print("✅ Successfully imported ai_script_editor module")
    
    # Test launching the editor
    print("Attempting to launch NEO Script Editor...")
    window = ai_script_editor.launch_ai_script_editor()
    
    if window:
        print("✅ NEO Script Editor launched successfully!")
        print("Window type:", type(window))
    else:
        print("❌ Failed to launch NEO Script Editor")
        
except Exception as e:
    import traceback
    print(f"❌ Import test failed: {e}")
    print("Full traceback:")
    traceback.print_exc()

print("\nTest completed.")