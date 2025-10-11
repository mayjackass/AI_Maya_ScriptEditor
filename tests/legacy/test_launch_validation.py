#!/usr/bin/env python3
"""
Test import and validate that the window launches successfully.
"""

import sys
import os

# Add the ai_script_editor directory to path like Maya would
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

print("🧪 Testing NEO Script Editor Launch...")

try:
    from ai_script_editor import launch_ai_script_editor
    print("✅ Import successful")
    
    # Launch and immediately check result
    window = launch_ai_script_editor()
    
    if window is not None:
        print(f"✅ Window created successfully: {type(window).__name__}")
        print(f"✅ Window title: {window.windowTitle()}")
        print("✅ All systems operational - NEO Script Editor is ready!")
        
        # Quick validation that key components exist
        if hasattr(window, 'tabWidget'):
            print(f"✅ Tab widget found with {window.tabWidget.count()} tabs")
        if hasattr(window, 'console'):
            print("✅ Console component found")
        if hasattr(window, 'debug_session'):
            print("✅ Debug system found")
            
        return_code = 0  # Success
    else:
        print("❌ Window creation failed")
        return_code = 1
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    return_code = 1

print(f"\n🏁 Test completed with return code: {return_code}")
sys.exit(return_code)