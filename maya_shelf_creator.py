"""
NEO Script Editor - Maya Shelf Creator
=====================================
Automatically creates a "NEO" shelf tab with the dockable NEO Script Editor button.
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
    Create a dedicated "NEO" shelf tab with the dockable NEO Script Editor button
    """
    if not MAYA_AVAILABLE:
        print("[!] This function requires Maya")
        return False
    
    try:
        shelf_name = "NEO"
        
        # Check if NEO shelf already exists
        existing_shelves = cmds.shelfLayout(query=True, childArray=True) or []
        shelf_exists = any(cmds.shelfLayout(shelf, query=True, annotation=True) == shelf_name 
                          for shelf in existing_shelves if cmds.shelfLayout(shelf, exists=True))
        
        if shelf_exists:
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(script_dir, "assets")
        
        # Try different icon options
        icon_options = [
            os.path.join(assets_path, "matrix.png"),
            os.path.join(assets_path, "morpheus.png"),
            "pythonFamily.png",  # Maya default Python icon
            "menuIconWindow.png"  # Maya default window icon
        ]
        
        icon_path = None
        for icon in icon_options:
            if os.path.exists(icon):
                icon_path = icon
                break
        
        if not icon_path:
            icon_path = icon_options[2]  # Use Maya default
            print(f"[Warning] NEO icons not found, using Maya default: {icon_path}")
        else:
            print(f"[Maya] Using NEO icon: {icon_path}")
        
        # Create the NEO Script Editor button
        cmds.shelfButton(
            annotation="Launch NEO Script Editor (Dockable)",
            image1=icon_path,
            label="NEO",
            command="""
# NEO Script Editor - Dockable Launch
try:
    neo_docked()
    print("✅ NEO Script Editor launched!")
except:
    print("❌ NEO not available. Make sure userSetup.py is installed.")
    print("💡 Try: launch_neo_docked() or check Maya Script Editor for errors.")
            """,
            parent=new_shelf,
            width=35,
            height=35,
            imageOverlayLabel="NEO",
            style="iconOnly",
            marginWidth=1,
            marginHeight=1
        )
        
        # Add a separator
        cmds.separator(parent=new_shelf, width=10, style="shelf")
        
        # Create additional useful buttons
        
        # Hide NEO button
        cmds.shelfButton(
            annotation="Hide NEO Script Editor",
            image1=os.path.join(assets_path, "syntax_error.png") if os.path.exists(os.path.join(assets_path, "syntax_error.png")) else "visibilityOff.png",
            label="Hide",
            command="""
try:
    hide_neo_docked()
    print("👁️ NEO Script Editor hidden")
except:
    print("❌ Could not hide NEO Script Editor")
            """,
            parent=new_shelf,
            width=32,
            height=32,
            imageOverlayLabel="Hide",
            style="iconOnly"
        )
        
        # Standalone NEO button
        cmds.shelfButton(
            annotation="Launch NEO Script Editor (Standalone Window)",
            image1=icon_path,
            label="NEO Win",
            command="""
try:
    launch_neo_editor()
    print("🪟 NEO Script Editor (standalone) launched!")
except:
    print("❌ NEO standalone not available")
            """,
            parent=new_shelf,
            width=32,
            height=32,
            imageOverlayLabel="Win",
            style="iconOnly"
        )
        
        # Add separator
        cmds.separator(parent=new_shelf, width=10, style="shelf")
        
        # Maya Script Editor button (for comparison)
        cmds.shelfButton(
            annotation="Maya Script Editor (for comparison)",
            image1="commandButton.png",
            label="Maya SE",
            command="ScriptEditor;",
            parent=new_shelf,
            width=32,
            height=32,
            imageOverlayLabel="Maya",
            style="iconOnly"
        )
        
        # Switch to the new shelf
        mel.eval(f'global string $gShelfTopLevel; tabLayout -edit -selectTab "{shelf_name}" $gShelfTopLevel;')
        
        print(f"✅ [Maya] '{shelf_name}' shelf created successfully!")
        print("🎯 [Buttons created:]")
        print("   • NEO (large) - Launch dockable NEO Script Editor")
        print("   • Hide - Hide the docked NEO Script Editor")
        print("   • Win - Launch standalone NEO Script Editor")
        print("   • Maya - Maya's built-in Script Editor")
        print(f"💡 [Tip] The '{shelf_name}' shelf is now active and ready to use!")
        
        return True
        
    except Exception as e:
        print(f"❌ [Maya] Failed to create NEO shelf: {e}")
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
                print(f"🗑️ [Maya] '{shelf_name}' shelf deleted")
                return True
        
        print(f"[Maya] '{shelf_name}' shelf not found")
        return False
        
    except Exception as e:
        print(f"❌ [Maya] Failed to delete NEO shelf: {e}")
        return False


def refresh_neo_shelf():
    """Refresh the NEO shelf (delete and recreate)"""
    print("🔄 [Maya] Refreshing NEO shelf...")
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
        print("📖 Usage in Maya:")
        print("   from maya_shelf_creator import create_neo_shelf")
        print("   create_neo_shelf()")