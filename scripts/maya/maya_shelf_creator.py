"""
NEO Script Editor - Maya Shelf Creator
=====================================
Automatically creates a "NEO" shelf tab with the standalone NEO Script Editor button.
Uses the Matrix/Morpheus icon from the assets folder.
"""

import sys
import os

# Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    print("[!] Maya not available - this shelf creator requires Maya")
    MAYA_AVAILABLE = False


def create_neo_shelf():
    """
    Create a dedicated "NEO" shelf tab with the standalone NEO Script Editor button
    """
    if not MAYA_AVAILABLE:
        print("[!] This function requires Maya")
        return False
    
    try:
        shelf_name = "NEO"
        
        # Check if NEO shelf already exists
        if cmds.shelfLayout(shelf_name, exists=True):
            print(f"[Maya] NEO shelf already exists")
            # Switch to the NEO shelf
            mel.eval(f'global string $gShelfTopLevel; tabLayout -edit -selectTab "{shelf_name}" $gShelfTopLevel;')
            return True
        
        # Create new shelf
        print(f"[Maya] Creating '{shelf_name}' shelf...")
        
        # Get the main shelf tab layout
        main_shelf = mel.eval('$tempVar = $gShelfTopLevel')
        
        # Create the new shelf tab
        new_shelf = cmds.shelfLayout(
            shelf_name,
            annotation=shelf_name,
            parent=main_shelf
        )
        
        # Get the path to our assets folder (go up two levels from scripts/maya/)
        script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/maya/
        project_root = os.path.dirname(os.path.dirname(script_dir))  # ai_script_editor/
        assets_path = os.path.join(project_root, "assets")
        
        # Use matrix icon specifically
        matrix_icon = os.path.join(assets_path, "matrix.png")
        
        if os.path.exists(matrix_icon):
            icon_path = matrix_icon
            print(f"[Maya] Using NEO matrix icon: {icon_path}")
        else:
            # Fallback to Maya default
            icon_path = "pythonFamily.png"
            print(f"[Warning] Matrix icon not found at {matrix_icon}, using Maya default: {icon_path}")
        
        # Create the NEO Script Editor button
        cmds.shelfButton(
            annotation="Launch NEO Script Editor (Standalone)",
            image1=icon_path,
            label="NEO",
            command="""
# NEO Script Editor - Standalone Launch
try:
    launch_neo_editor()
    print("[NEO] Script Editor launched!")
except:
    print("[NEO] Not available. Make sure userSetup.py is installed.")
    print("[TIP] Try: launch_neo_editor() or check Maya Script Editor for errors.")
            """,
            parent=new_shelf,
            width=35,
            height=35,
            imageOverlayLabel="NEO",
            style="iconOnly",
            marginWidth=1,
            marginHeight=1
        )
        
        # Switch to the new shelf
        mel.eval(f'global string $gShelfTopLevel; tabLayout -edit -selectTab "{shelf_name}" $gShelfTopLevel;')
        
        print(f"[Maya] '{shelf_name}' shelf created successfully!")
        print("[INFO] NEO button created with matrix icon")
        print(f"[TIP] The '{shelf_name}' shelf is now active and ready to use!")
        
        return True
        
    except Exception as e:
        print(f"[Maya] Failed to create NEO shelf: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_neo_shelf():
    """Delete the NEO shelf completely"""
    if not MAYA_AVAILABLE:
        return False
    
    try:
        shelf_name = "NEO"
        
        # Get all shelves
        main_shelf = mel.eval('$tempVar = $gShelfTopLevel')
        shelves = cmds.tabLayout(main_shelf, query=True, childArray=True) or []
        
        # Find and delete NEO shelf
        for shelf in shelves:
            if cmds.shelfLayout(shelf, query=True, annotation=True) == shelf_name:
                cmds.deleteUI(shelf, layout=True)
                print(f"[Maya] '{shelf_name}' shelf deleted")
                return True
        
        print(f"[Maya] '{shelf_name}' shelf not found")
        return False
        
    except Exception as e:
        print(f"[Maya] Failed to delete NEO shelf: {e}")
        return False


def refresh_neo_shelf():
    """Refresh the NEO shelf (delete and recreate)"""
    print("[Maya] Refreshing NEO shelf...")
    delete_neo_shelf()
    return create_neo_shelf()


# Convenience functions
create_shelf = create_neo_shelf
delete_shelf = delete_neo_shelf
refresh_shelf = refresh_neo_shelf


if __name__ == "__main__":
    if MAYA_AVAILABLE:
        create_neo_shelf()
    else:
        print("[!] This module is designed to run inside Maya")
        print("[INFO] Usage in Maya:")
        print("   from maya_shelf_creator import create_neo_shelf")
        print("   create_neo_shelf()")