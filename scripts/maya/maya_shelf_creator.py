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
        
        # Get the path to our assets folder 
        # This works both from project source and installed location
        script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/maya/
        
        # Try multiple possible asset paths
        possible_asset_paths = [
            # From installed location: scripts/maya/ -> ai_script_editor/assets/
            os.path.join(os.path.dirname(os.path.dirname(script_dir)), "assets"),
            # From project source: scripts/maya/ -> project_root/assets/
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "assets"),
            # Fallback: look for assets in parent directories
            os.path.join(os.path.dirname(script_dir), "..", "assets"),
            os.path.join(os.path.dirname(script_dir), "..", "..", "assets")
        ]
        
        # Find the matrix icon
        matrix_icon = None
        for assets_path in possible_asset_paths:
            test_path = os.path.join(assets_path, "matrix.png")
            if os.path.exists(test_path):
                matrix_icon = test_path
                print(f"[Maya] Found matrix icon at: {matrix_icon}")
                break
        
        # Set icon path
        if matrix_icon and os.path.exists(matrix_icon):
            icon_path = matrix_icon
            print(f"[Maya] Using NEO matrix icon: {icon_path}")
        else:
            # Fallback to Maya default
            icon_path = "pythonFamily.png"
            print(f"[Warning] Matrix icon not found, using Maya default: {icon_path}")
            print(f"[Debug] Checked paths: {[os.path.join(p, 'matrix.png') for p in possible_asset_paths]}")
        
        # Create the NEO Script Editor button
        cmds.shelfButton(
            annotation="Launch NEO Script Editor (Single Instance)",
            image1=icon_path,
            label="NEO",
            command="""
# NEO Script Editor - Single Instance Launch
try:
    # Close any existing NEO windows
    from PySide6 import QtWidgets
    import time
    app = QtWidgets.QApplication.instance()
    if app:
        closed_any = False
        for widget in app.allWidgets():
            if widget.__class__.__name__ == "NEOMainWindow":
                try:
                    widget.close()
                    widget.deleteLater()
                    closed_any = True
                except:
                    pass
        if closed_any:
            app.processEvents()
            time.sleep(0.1)
    
    # Launch new instance
    launch_neo_editor()
    print("[NEO] Script Editor launched!")
except:
    print("[NEO] Not available. Make sure userSetup.py is installed.")
    print("[TIP] Try: launch_neo_editor_single() or check Maya Script Editor for errors.")
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


def debug_shelf_info():
    """Debug function to show current shelf information"""
    if not MAYA_AVAILABLE:
        print("[!] Maya not available")
        return
    
    try:
        shelf_name = "NEO"
        
        # Check if shelf exists
        if cmds.shelfLayout(shelf_name, exists=True):
            print(f"[Debug] '{shelf_name}' shelf exists")
            
            # Get shelf buttons
            buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
            print(f"[Debug] Found {len(buttons)} buttons on shelf:")
            
            for i, button in enumerate(buttons):
                if cmds.objectTypeUI(button) == "shelfButton":
                    label = cmds.shelfButton(button, query=True, label=True)
                    annotation = cmds.shelfButton(button, query=True, annotation=True)
                    image = cmds.shelfButton(button, query=True, image1=True)
                    print(f"  {i+1}. Label: '{label}', Annotation: '{annotation}', Image: '{image}'")
        else:
            print(f"[Debug] '{shelf_name}' shelf does not exist")
            
        # Show assets path info
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_asset_paths = [
            os.path.join(os.path.dirname(os.path.dirname(script_dir)), "assets"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))), "assets"),
            os.path.join(os.path.dirname(script_dir), "..", "assets"),
            os.path.join(os.path.dirname(script_dir), "..", "..", "assets")
        ]
        
        print(f"[Debug] Script dir: {script_dir}")
        print(f"[Debug] Asset path search:")
        for i, path in enumerate(possible_asset_paths):
            matrix_path = os.path.join(path, "matrix.png")
            exists = os.path.exists(matrix_path)
            print(f"  {i+1}. {matrix_path} - {'EXISTS' if exists else 'NOT FOUND'}")
            
    except Exception as e:
        print(f"[Debug] Error getting shelf info: {e}")


def force_recreate_shelf():
    """Force delete and recreate the NEO shelf"""
    print("[Maya] Force recreating NEO shelf...")
    
    # Delete any existing NEO shelf
    try:
        if cmds.shelfLayout("NEO", exists=True):
            cmds.deleteUI("NEO", layout=True)
            print("[Maya] Deleted existing NEO shelf")
    except:
        pass
    
    # Wait a moment
    cmds.refresh()
    
    # Create new shelf
    result = create_neo_shelf()
    
    # Show debug info
    debug_shelf_info()
    
    return result


# Convenience functions
create_shelf = create_neo_shelf
delete_shelf = delete_neo_shelf
refresh_shelf = refresh_neo_shelf
force_recreate = force_recreate_shelf
debug_shelf = debug_shelf_info


if __name__ == "__main__":
    if MAYA_AVAILABLE:
        create_neo_shelf()
    else:
        print("[!] This module is designed to run inside Maya")
        print("[INFO] Usage in Maya:")
        print("   from maya_shelf_creator import create_neo_shelf")
        print("   create_neo_shelf()")