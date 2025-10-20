"""
NEO Script Editor - Complete Maya Setup
======================================
One-click setup for NEO Script Editor with shelf integration.

Run this once in Maya to set up everything:
- Dockable NEO Script Editor
- NEO shelf tab with buttons using NEO logo
- All convenience functions
"""

import sys
import os

# Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    print("[!] Maya not available - this setup script requires Maya")
    MAYA_AVAILABLE = False

# Add our script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)


def complete_neo_setup():
    """
    Complete setup for NEO Script Editor in Maya
    - Creates shelf tab with NEO logo buttons
    - Sets up all convenience functions
    - Launches dockable NEO Script Editor
    """
    if not MAYA_AVAILABLE:
        print("[!] This function requires Maya")
        return False
    
    print("🚀 Starting complete NEO Script Editor setup...")
    
    try:
        # Step 1: Setup functions (like userSetup.py would do)
        print("📦 [1/3] Setting up NEO functions...")
        
        def launch_neo_editor():
            """Launch NEO Script Editor as standalone window"""
            try:
                from main_window import AiScriptEditor
                window = AiScriptEditor()
                window.show()
                print("✅ [NEO] Standalone Script Editor launched")
                return window
            except Exception as e:
                print(f"❌ [NEO] Standalone launch failed: {e}")
                return None
        
        def create_neo_shelf():
            """Create NEO shelf tab with buttons"""
            try:
                from maya_shelf_creator import create_neo_shelf
                return create_neo_shelf()
            except Exception as e:
                print(f"❌ [NEO] Shelf creation failed: {e}")
                return False
        
        # Make functions globally available
        import __main__
        __main__.launch_neo_editor = launch_neo_editor
        __main__.create_neo_shelf = create_neo_shelf
        
        print("   ✅ NEO functions installed globally")
        
        # Step 2: Create NEO shelf with logo buttons
        print("🎨 [2/3] Creating NEO shelf with logo buttons...")
        shelf_success = create_neo_shelf()
        
        if shelf_success:
            print("   ✅ NEO shelf created with logo buttons")
        else:
            print("   ⚠️ NEO shelf creation had issues (but functions still work)")
        
        # Step 3: Launch standalone NEO Script Editor
        print("🪟 [3/3] Launching standalone NEO Script Editor...")
        editor_window = launch_neo_editor()
        
        if editor_window:
            print("   ✅ NEO Script Editor launched (standalone always-on-top)")
        else:
            print("   ⚠️ NEO Script Editor launch had issues")
        
        # Success summary
        print("")
        print("🎉 NEO Script Editor setup complete!")
        print("📖 What was installed:")
        print("   • NEO shelf tab with logo buttons")
        print("   • Standalone NEO Script Editor (always on top)")
        print("   • Global convenience functions")
        print("")
        print("🎯 Available commands:")
        print("   • launch_neo_editor()  - Launch standalone editor")
        print("   • create_neo_shelf()   - Recreate shelf if needed")
        print("")
        print("💡 Pro tip: NEO editor stays on top for easy access!")
        print("💡 Click the NEO button in the shelf anytime to reopen")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def launch_neo_editor():
    """Launch NEO Script Editor as standalone always-on-top window"""
    try:
        # Add paths
        neo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if neo_dir not in sys.path:
            sys.path.insert(0, neo_dir)
        
        from main_window import AiScriptEditor
        window = AiScriptEditor()
        window.show()
        print("✅ [NEO] Standalone Script Editor launched")
        return window
    except Exception as e:
        print(f"❌ [NEO] Standalone launch failed: {e}")
        return None


def create_neo_shelf():
    """Create NEO shelf tab with buttons"""
    try:
        from maya_shelf_creator import create_neo_shelf
        return create_neo_shelf()
    except Exception as e:
        print(f"❌ [NEO] Shelf creation failed: {e}")
        return False


def quick_neo_launch():
    """Quick launch - just open NEO without full setup"""
    try:
        return launch_neo_editor()
    except Exception as e:
        print(f"❌ Quick launch failed: {e}")
        return None


# Convenience aliases
setup_neo = complete_neo_setup
install_neo = complete_neo_setup
neo_setup = complete_neo_setup


if __name__ == "__main__":
    if MAYA_AVAILABLE:
        complete_neo_setup()
    else:
        print("[!] This module is designed to run inside Maya")
        print("📖 Usage in Maya:")
        print("   from complete_setup import complete_neo_setup")
        print("   complete_neo_setup()")