"""
Manual shelf debugging and fixing script for NEO Script Editor
Run this directly in Maya Script Editor to debug and fix shelf issues
"""

import maya.cmds as cmds
import maya.mel as mel
import os

def debug_current_shelf():
    """Debug current NEO shelf state"""
    print("=" * 60)
    print("NEO SHELF DEBUG INFORMATION")
    print("=" * 60)
    
    shelf_name = "NEO"
    
    # Check if shelf exists
    if cmds.shelfLayout(shelf_name, exists=True):
        print(f"✓ '{shelf_name}' shelf EXISTS")
        
        # Get shelf buttons
        buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        print(f"📊 Found {len(buttons)} items on shelf:")
        
        for i, button in enumerate(buttons):
            try:
                obj_type = cmds.objectTypeUI(button)
                if obj_type == "shelfButton":
                    label = cmds.shelfButton(button, query=True, label=True) or "No Label"
                    annotation = cmds.shelfButton(button, query=True, annotation=True) or "No Annotation"
                    image = cmds.shelfButton(button, query=True, image1=True) or "No Image"
                    print(f"  🔹 Button {i+1}: '{label}'")
                    print(f"     Annotation: {annotation}")
                    print(f"     Image: {image}")
                else:
                    print(f"  📌 Item {i+1}: {obj_type} - {button}")
            except Exception as e:
                print(f"  ❌ Item {i+1}: Error reading - {e}")
    else:
        print(f"❌ '{shelf_name}' shelf does NOT exist")
    
    # Check for matrix icon
    print("\n" + "=" * 60)
    print("MATRIX ICON SEARCH")
    print("=" * 60)
    
    # Get script location
    try:
        import maya_shelf_creator
        script_path = maya_shelf_creator.__file__
        script_dir = os.path.dirname(script_path)
        print(f"📁 Script location: {script_dir}")
        
        # Try asset paths
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(script_dir)), "assets", "matrix.png"),
            os.path.join(os.path.dirname(script_dir), "assets", "matrix.png"),
            os.path.join(os.path.dirname(script_dir), "..", "assets", "matrix.png"),
            os.path.join(os.path.dirname(script_dir), "..", "..", "assets", "matrix.png")
        ]
        
        found_icon = None
        for i, path in enumerate(possible_paths):
            exists = os.path.exists(path)
            status = "✓ EXISTS" if exists else "❌ NOT FOUND"
            print(f"  {i+1}. {path}")
            print(f"     {status}")
            if exists and not found_icon:
                found_icon = path
        
        if found_icon:
            print(f"\n🎯 MATRIX ICON FOUND: {found_icon}")
        else:
            print(f"\n❌ MATRIX ICON NOT FOUND in any location")
            
    except Exception as e:
        print(f"❌ Error checking paths: {e}")

def fix_neo_shelf():
    """Fix NEO shelf - delete old and create new one with matrix icon"""
    print("\n" + "=" * 60)
    print("FIXING NEO SHELF")
    print("=" * 60)
    
    shelf_name = "NEO"
    
    # Delete existing shelf
    try:
        if cmds.shelfLayout(shelf_name, exists=True):
            cmds.deleteUI(shelf_name, layout=True)
            print("✓ Deleted existing NEO shelf")
        else:
            print("ℹ No existing NEO shelf to delete")
    except Exception as e:
        print(f"⚠ Error deleting shelf: {e}")
    
    # Create new shelf
    try:
        print("🔧 Creating new NEO shelf...")
        
        # Get main shelf
        main_shelf = mel.eval('$tempVar = $gShelfTopLevel')
        
        # Create shelf
        new_shelf = cmds.shelfLayout(
            shelf_name,
            annotation=shelf_name,
            parent=main_shelf
        )
        
        # Find matrix icon
        matrix_icon = None
        try:
            import maya_shelf_creator
            script_path = maya_shelf_creator.__file__
            script_dir = os.path.dirname(script_path)
            
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(script_dir)), "assets", "matrix.png"),
                os.path.join(os.path.dirname(script_dir), "assets", "matrix.png"),
                os.path.join(os.path.dirname(script_dir), "..", "assets", "matrix.png"),
                os.path.join(os.path.dirname(script_dir), "..", "..", "assets", "matrix.png")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    matrix_icon = path
                    break
        except:
            pass
        
        # Set icon
        if matrix_icon:
            icon_path = matrix_icon
            print(f"✓ Using matrix icon: {icon_path}")
        else:
            icon_path = "pythonFamily.png"
            print(f"⚠ Matrix icon not found, using Maya default: {icon_path}")
        
        # Create NEO button
        cmds.shelfButton(
            annotation="Launch NEO Script Editor (Standalone)",
            image1=icon_path,
            label="NEO",
            command="""
# NEO Script Editor - Standalone Launch
try:
    launch_neo_editor()
    print("[SUCCESS] NEO Script Editor launched!")
except:
    print("[ERROR] NEO not available. Make sure userSetup.py is installed.")
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
        
        # Switch to shelf
        mel.eval(f'global string $gShelfTopLevel; tabLayout -edit -selectTab "{shelf_name}" $gShelfTopLevel;')
        
        print("✅ NEO shelf created successfully!")
        print("🎯 Only NEO button should be visible (no Maya Script Editor button)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating shelf: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run the functions
if __name__ == "__main__":
    debug_current_shelf()
    
    response = input("\nWould you like to fix the shelf? (y/n): ")
    if response.lower() in ['y', 'yes']:
        fix_neo_shelf()
        print("\n" + "=" * 60)
        print("FINAL SHELF STATE")
        print("=" * 60)
        debug_current_shelf()

print("\n" + "=" * 80)
print("MANUAL COMMANDS:")
print("To debug: debug_current_shelf()")
print("To fix:   fix_neo_shelf()")
print("=" * 80)