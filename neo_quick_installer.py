"""
NEO Script Editor - Simple Drag & Drop Installer
===============================================

SIMPLE INSTALLATION:
Just drag this file into Maya's viewport and everything installs automatically!

What this does:
- Creates NEO shelf with launch button  
- Adds NEO menu to Maya menu bar
- Sets up userSetup.py integration
- Launches NEO Script Editor instantly

For full installation from GitHub, use neo_installer.py instead.
This is the lightweight version for immediate Maya workflow enhancement.
"""

import maya.cmds as cmds
import maya.mel as mel
import os
import sys

def quick_neo_setup():
    """Quick NEO setup for immediate use"""
    
    print("🚀 NEO Script Editor - Quick Setup")
    print("="*50)
    
    try:
        # Get Maya scripts directory
        maya_scripts = cmds.internalVar(userScriptDir=True)
        print(f"Maya Scripts: {maya_scripts}")
        
        # Create quick NEO shelf
        create_quick_neo_shelf()
        
        # Add NEO menu
        add_neo_menu()
        
        # Setup userSetup integration
        setup_quick_user_setup()
        
        # Show success message
        show_quick_success()
        
        print("✅ Quick NEO setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Quick setup failed: {e}")
        show_error_dialog(str(e))
        return False

def create_quick_neo_shelf():
    """Create quick NEO shelf"""
    
    shelf_name = "NEO_Quick"
    
    # Remove existing shelf
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name, layout=True)
    
    # Create new shelf
    shelf = cmds.shelfLayout(shelf_name, parent="ShelfLayout")
    
    # NEO Editor button
    cmds.shelfButton(
        parent=shelf,
        label="NEO",
        annotation="Launch NEO Script Editor Window",
        image="pythonFamily.png",
        command=create_neo_window_command(),
        sourceType="python"
    )
    
    # Docked Editor button
    cmds.shelfButton(
        parent=shelf,
        label="Dock",
        annotation="Create Dockable NEO Editor",
        image="dockRight.png", 
        command=create_docked_command(),
        sourceType="python"
    )
    
    # GitHub button
    cmds.shelfButton(
        parent=shelf,
        label="GitHub",
        annotation="Download Full NEO Script Editor",
        image="UVEditorSnapshot.png",
        command=create_github_command(),
        sourceType="python"
    )
    
    print("✅ Quick NEO shelf created")

def add_neo_menu():
    """Add NEO menu to Maya menu bar"""
    
    try:
        main_menu = mel.eval('$tempVar = $gMainWindow')
        
        # Remove existing menu
        if cmds.menu("quickNeoMenu", exists=True):
            cmds.deleteUI("quickNeoMenu", menu=True)
        
        # Create NEO menu
        neo_menu = cmds.menu(
            "quickNeoMenu",
            label="NEO",
            parent=main_menu,
            tearOff=True
        )
        
        # Add menu items
        cmds.menuItem(
            label="Launch NEO Window",
            command=create_neo_window_command(),
            parent=neo_menu,
            image="pythonFamily.png"
        )
        
        cmds.menuItem(
            label="Create Dockable Editor",
            command=create_docked_command(),
            parent=neo_menu,
            image="dockRight.png"
        )
        
        cmds.menuItem(divider=True, parent=neo_menu)
        
        cmds.menuItem(
            label="Download Full Version",
            command=create_github_command(),
            parent=neo_menu
        )
        
        cmds.menuItem(divider=True, parent=neo_menu)
        
        cmds.menuItem(
            label="About Quick NEO",
            command="show_quick_about()",
            parent=neo_menu
        )
        
        print("✅ NEO menu added")
        
    except Exception as e:
        print(f"⚠️ Menu creation failed: {e}")

def setup_quick_user_setup():
    """Setup userSetup.py integration"""
    
    try:
        maya_scripts = cmds.internalVar(userScriptDir=True)
        user_setup_path = os.path.join(maya_scripts, "userSetup.py")
        
        # NEO integration code
        neo_code = '''
# NEO Script Editor Quick Integration (Auto-added)
def quick_neo_functions():
    """Setup quick NEO functions"""
    import __main__
    __main__.launch_quick_neo = lambda: quick_neo_editor()
    __main__.create_neo_dock = lambda: create_docked_neo()
    __main__.show_quick_about = lambda: quick_about_dialog()

def quick_neo_editor():
    """Launch quick NEO editor"""
    try:
        # Simple script editor window
        if cmds.window("quickNeoEditor", exists=True):
            cmds.deleteUI("quickNeoEditor", window=True)
        
        window = cmds.window(
            "quickNeoEditor",
            title="NEO Script Editor (Quick)",
            widthHeight=(800, 600),
            resizeToFitChildren=True
        )
        
        form = cmds.formLayout()
        
        # Text editor
        text_field = cmds.scrollField(
            wordWrap=False,
            text="# NEO Script Editor - Quick Version\\n# Download full version from GitHub\\n\\nimport maya.cmds as cmds\\ncmds.polySphere()",
            font="fixedWidthFont"
        )
        
        # Buttons
        run_btn = cmds.button(
            label="Execute",
            command=lambda x: execute_neo_code(text_field)
        )
        
        clear_btn = cmds.button(
            label="Clear",
            command=lambda x: cmds.scrollField(text_field, edit=True, text="")
        )
        
        github_btn = cmds.button(
            label="Download Full Version", 
            command=lambda x: show_github_info()
        )
        
        # Layout
        cmds.formLayout(form, edit=True,
            attachForm=[(text_field, "top", 5), (text_field, "left", 5), (text_field, "right", 5),
                       (run_btn, "left", 5), (run_btn, "bottom", 5),
                       (clear_btn, "bottom", 5), (github_btn, "right", 5), (github_btn, "bottom", 5)],
            attachControl=[(text_field, "bottom", 5, run_btn)],
            attachPosition=[(run_btn, "right", 2, 33), (clear_btn, "left", 2, 33), (clear_btn, "right", 2, 66), (github_btn, "left", 2, 66)]
        )
        
        cmds.showWindow(window)
        print("✅ Quick NEO editor launched")
        
    except Exception as e:
        print(f"❌ Quick NEO launch failed: {e}")

def execute_neo_code(text_field):
    """Execute code from text field"""
    try:
        code = cmds.scrollField(text_field, query=True, text=True)
        exec(code, {"__name__": "__main__", "cmds": cmds})
        print("✅ Code executed successfully")
    except Exception as e:
        print(f"❌ Execution error: {e}")
        cmds.error(f"Script error: {e}")

def create_docked_neo():
    """Create simple docked editor"""
    try:
        # Simple dockable window
        if cmds.dockControl("quickNeoDoc", exists=True):
            cmds.deleteUI("quickNeoDoc", control=True)
        
        if cmds.window("quickNeoDockWin", exists=True):
            cmds.deleteUI("quickNeoDockWin", window=True)
        
        window = cmds.window("quickNeoDockWin", title="NEO Docked")
        
        form = cmds.formLayout()
        text_field = cmds.scrollField(
            text="# NEO Docked Editor\\nimport maya.cmds as cmds\\ncmds.polySphere()",
            font="fixedWidthFont"
        )
        run_btn = cmds.button(
            label="Run",
            command=lambda x: execute_neo_code(text_field)
        )
        
        cmds.formLayout(form, edit=True,
            attachForm=[(text_field, "top", 0), (text_field, "left", 0), (text_field, "right", 0),
                       (run_btn, "left", 0), (run_btn, "right", 0), (run_btn, "bottom", 0)],
            attachControl=[(text_field, "bottom", 0, run_btn)]
        )
        
        cmds.dockControl(
            "quickNeoDoc",
            label="NEO Editor",
            area="top",
            content=window,
            allowedArea=["top", "bottom", "left", "right"]
        )
        
        print("✅ Docked NEO editor created")
        
    except Exception as e:
        print(f"❌ Docked editor failed: {e}")

def show_github_info():
    """Show GitHub download info"""
    cmds.confirmDialog(
        title="Download Full NEO Script Editor",
        message=(
            "🚀 Get the complete NEO Script Editor experience!\\n\\n"
            "Full Version Features:\\n"
            "• AI Assistant (OpenAI/Claude integration)\\n"
            "• Advanced syntax highlighting\\n"
            "• 320+ Maya command validation\\n"
            "• Auto-completion and IntelliSense\\n"
            "• Integrated help system\\n"
            "• Advanced error detection\\n\\n"
            "📥 Download from:\\n"
            "github.com/mayjackass/AI_Maya_ScriptEditor\\n\\n"
            "💡 Or use the full drag & drop installer:\\n"
            "neo_installer.py"
        ),
        button=["Got it!"]
    )

def quick_about_dialog():
    """Show quick about dialog"""
    cmds.confirmDialog(
        title="NEO Script Editor (Quick)",
        message=(
            "NEO Script Editor - Quick Version\\n"
            '"Take the red pill and see how deep the rabbit hole goes..."\\n\\n'
            "This is a lightweight version for immediate use.\\n\\n"
            "🔥 Quick Features:\\n"
            "• Simple Maya script editor\\n"
            "• Dockable interface\\n" 
            "• Easy shelf integration\\n\\n"
            "For the full experience with AI assistance,\\n"
            "download from GitHub!\\n\\n"
            "Developer: Mayj Amilano (@mayjackass)\\n"
            "Version: Quick 1.0"
        ),
        button=["Close"]
    )

try:
    import maya.cmds as cmds
    quick_neo_functions()
    print("✅ Quick NEO functions loaded")
except:
    pass
'''
        
        # Check if userSetup.py exists
        if os.path.exists(user_setup_path):
            # Read existing file
            with open(user_setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if NEO is already integrated
            if "quick_neo_functions" not in content:
                # Append NEO code
                with open(user_setup_path, 'a', encoding='utf-8') as f:
                    f.write(neo_code)
                print("✅ Added NEO integration to existing userSetup.py")
            else:
                print("✅ NEO integration already exists")
        else:
            # Create new userSetup.py
            with open(user_setup_path, 'w', encoding='utf-8') as f:
                f.write(neo_code)
            print("✅ Created new userSetup.py with NEO integration")
        
        # Execute the functions now
        exec(neo_code.replace("import __main__", ""))
        
    except Exception as e:
        print(f"⚠️ userSetup.py integration failed: {e}")

def create_neo_window_command():
    """Create command for NEO window button"""
    return "try:\\n  quick_neo_editor()\\nexcept:\\n  exec(open(r'" + __file__.replace('\\', '/') + "').read()); quick_neo_editor()"

def create_docked_command():
    """Create command for docked button"""
    return "try:\\n  create_neo_dock()\\nexcept:\\n  exec(open(r'" + __file__.replace('\\', '/') + "').read()); create_neo_dock()"

def create_github_command():
    """Create command for GitHub button"""
    return "show_github_info()" if 'cmds' in globals() else "print('Visit: github.com/mayjackass/AI_Maya_ScriptEditor')"

def show_quick_success():
    """Show quick setup success"""
    cmds.confirmDialog(
        title="Quick NEO Setup Complete!",
        message=(
            "🎉 NEO Script Editor Quick Setup Complete!\\n\\n"
            "✅ What was added:\\n"
            "• NEO_Quick shelf with launch buttons\\n"
            "• NEO menu in menu bar\\n"
            "• Maya startup integration\\n\\n"
            "🚀 Quick Start:\\n"
            "• Click 'NEO' button in shelf to launch editor\\n"
            "• Click 'Dock' to create dockable version\\n"
            "• Use NEO menu for all options\\n\\n"
            "💡 Want more features?\\n"
            "Download the full version from GitHub for:\\n"
            "• AI Assistant integration\\n"
            "• Advanced syntax highlighting\\n"
            "• Maya command validation\\n"
            "• And much more!\\n\\n"
            "Enjoy coding with NEO! 🚀"
        ),
        button=["Awesome!"]
    )

def show_error_dialog(error):
    """Show error dialog"""
    cmds.confirmDialog(
        title="Quick Setup Error",
        message=(
            f"❌ Quick setup encountered an error:\\n\\n{error}\\n\\n"
            "You can still:\\n"
            "• Try running the setup again\\n"
            "• Use Maya's built-in Script Editor\\n"
            "• Download full NEO from GitHub\\n\\n"
            "GitHub: github.com/mayjackass/AI_Maya_ScriptEditor"
        ),
        button=["OK"]
    )

# =============================================================================
# Drag & Drop Entry Point
# =============================================================================

def onMayaDroppedPythonFile(*args, **kwargs):
    """Entry point for drag & drop"""
    print("🎯 NEO Script Editor Quick Installer Activated!")
    return quick_neo_setup()

# Alternative entry points
def main():
    """Main entry point"""
    onMayaDroppedPythonFile()

if __name__ == "__main__":
    main()

# Instructions embedded in file
"""
🎯 NEO SCRIPT EDITOR - QUICK INSTALLER

DRAG & DROP INSTALLATION:
1. Drag this file into Maya's viewport
2. Click through the setup wizard  
3. Start using NEO immediately!

WHAT YOU GET:
✓ Simple NEO script editor window
✓ Dockable editor interface
✓ NEO shelf with buttons
✓ NEO menu integration
✓ Maya startup integration

MAYA COMMANDS (After installation):
• quick_neo_editor() - Launch NEO window
• create_neo_dock()  - Create docked editor

PERFECT FOR:
• Quick Maya script editing
• Simple workflow enhancement  
• Testing before full installation
• Lightweight Maya integration

WANT MORE FEATURES?
Download the full version from:
github.com/mayjackass/AI_Maya_ScriptEditor

Features in full version:
• AI Assistant (OpenAI/Claude)
• Advanced syntax highlighting
• 320+ Maya command validation
• Auto-completion and IntelliSense
• Integrated help and documentation

Author: Mayj Amilano (@mayjackass)
Version: Quick 1.0 - October 2025
"""