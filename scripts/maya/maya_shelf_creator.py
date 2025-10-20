"""
NEO Script Editor - Maya Shelf Creator (Fixed)
============================================
Creates the NEO shelf with buttons for Maya integration
"""

import os

# Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False


def create_neo_shelf():
    """Create the NEO shelf tab with buttons"""
    if not MAYA_AVAILABLE:
        print("[ERROR] This function requires Maya")
        return False
    
    print("[NEO] Creating NEO shelf...")
    
    try:
        # Get the main shelf tab layout
        shelf_tab_layout = mel.eval('$gShelfTopLevel')
        
        # Check if NEO shelf already exists and delete it
        existing_shelves = cmds.shelfTabLayout(shelf_tab_layout, query=True, childArray=True) or []
        if "NEO" in existing_shelves:
            print("[NEO] Removing existing NEO shelf...")
            cmds.deleteUI("NEO", layout=True)
        
        # Create new NEO shelf tab
        print("[NEO] Creating new NEO shelf tab...")
        shelf = cmds.shelfLayout("NEO", parent=shelf_tab_layout)
        
        # Get the assets path for icons
        assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        neo_icon = os.path.join(assets_path, "matrix.png") if os.path.exists(os.path.join(assets_path, "matrix.png")) else "pythonFamily.png"
        
        # Add NEO button
        cmds.shelfButton(
            parent=shelf,
            label="NEO",
            annotation="Launch NEO Script Editor",
            image=neo_icon,
            command="complete_neo_setup()",
            sourceType="python"
        )
        
        # Set the new shelf as active
        cmds.shelfTabLayout(shelf_tab_layout, edit=True, selectTab="NEO")
        
        print("[SUCCESS] NEO shelf created successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create NEO shelf: {e}")
        return False


if __name__ == "__main__":
    create_neo_shelf()