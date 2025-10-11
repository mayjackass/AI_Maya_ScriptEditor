#!/usr/bin/env python3
"""
Test the launch function directly like Maya would call it.
"""

import sys
import os

# Add the ai_script_editor directory to path like Maya would
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # Go up one level to simulate Maya's scripts folder

# Add both paths to simulate Maya environment
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

print("Testing Maya-style import...")
print(f"Script directory: {script_dir}")
print(f"Parent directory: {parent_dir}")

try:
    # Test importing the __init__ module directly
    from ai_script_editor import launch_ai_script_editor
    
    print("✅ Successfully imported launch function")
    
    # Test launching the editor
    print("Attempting to launch NEO Script Editor...")
    window = launch_ai_script_editor()
    
    if window:
        print("✅ NEO Script Editor launched successfully!")
        print("Window type:", type(window))
        
        # Give it a moment to initialize, then close
        import time
        time.sleep(2)
        if hasattr(window, 'close'):
            window.close()
        print("✅ Window closed successfully")
    else:
        print("❌ Failed to launch NEO Script Editor")
        
except Exception as e:
    import traceback
    print(f"❌ Launch test failed: {e}")
    print("Full traceback:")
    traceback.print_exc()

print("\nTest completed.")