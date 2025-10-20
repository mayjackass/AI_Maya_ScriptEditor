"""
Maya Dockable NEO Script Editor
===============================
Creates a dockable version of the NEO Script Editor that integrates with Maya's UI
like the built-in script editor, allowing you to dock it and see the viewport below.
"""

import sys
import os
from functools import partial

# Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
    from PySide6 import QtWidgets, QtCore
    MAYA_AVAILABLE = True
except ImportError:
    print("[!] Maya not available - this launcher requires Maya")
    MAYA_AVAILABLE = False

# Add our script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
neo_root_dir = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels to ai_script_editor root
if neo_root_dir not in sys.path:
    sys.path.insert(0, neo_root_dir)

try:
    from main_window import AiScriptEditor
    print("[Maya] Successfully imported NEO Script Editor")
except ImportError as e:
    print(f"[ERROR] Failed to import NEO Script Editor: {e}")
    AiScriptEditor = None


class MayaDockableNeoEditor(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    """
    Maya-dockable wrapper for the NEO Script Editor
    This creates a workspace control that can be docked like Maya's script editor
    """
    
    CONTROL_NAME = "neoScriptEditorWorkspaceControl"
    WINDOW_TITLE = "NEO Script Editor"
    
    def __init__(self, parent=None):
        super(MayaDockableNeoEditor, self).__init__(parent=parent)
        
        # Check if we have the NEO Script Editor available
        if AiScriptEditor is None:
            self.setWindowTitle("NEO Script Editor - Import Error")
            layout = QtWidgets.QVBoxLayout(self)
            error_label = QtWidgets.QLabel("Error: Could not import NEO Script Editor\nCheck installation path")
            layout.addWidget(error_label)
            return
        
        # Set up the main layout
        self.setObjectName(self.CONTROL_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        
        # Create main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create the NEO Script Editor instance properly embedded
        try:
            print("[Maya] Creating NEO Script Editor for dockable use...")
            
            # Create NEO Script Editor instance
            self.neo_editor = AiScriptEditor()
            print("[Maya] NEO Script Editor instance created")
            
            # CRITICAL: Hide the standalone window that gets created automatically
            self.neo_editor.hide()
            
            # Extract the central widget content instead of trying to embed the whole window
            central_widget = self.neo_editor.centralWidget()
            if central_widget:
                # Remove from original parent and add to our layout
                central_widget.setParent(None)
                central_widget.setParent(self)
                layout.addWidget(central_widget)
                print("[Maya] NEO Script Editor content embedded successfully")
            else:
                # Fallback: embed the whole editor but force it to be a widget
                self.neo_editor.setParent(self)
                self.neo_editor.setWindowFlags(QtCore.Qt.Widget)
                layout.addWidget(self.neo_editor)
                print("[Maya] NEO Script Editor embedded as fallback")
            
            print("[Maya] NEO Script Editor embedded in workspace control")
            
        except Exception as e:
            print(f"[ERROR] Failed to create NEO Script Editor: {e}")
            error_label = QtWidgets.QLabel(f"Error creating NEO Script Editor:\n{str(e)}")
            layout.addWidget(error_label)
    
    def dockCloseEventTriggered(self):
        """Called when the dock is closed"""
        print("[Maya] NEO Script Editor dock closed")
        # Save session before closing
        if hasattr(self.neo_editor, '_save_session'):
            self.neo_editor._save_session()


def create_workspace_control():
    """
    Create or show the NEO Script Editor workspace control
    Similar to how Maya's script editor works
    """
    if not MAYA_AVAILABLE:
        print("[!] This function requires Maya")
        return None
    
    control_name = MayaDockableNeoEditor.CONTROL_NAME
    
    # Check if workspace control already exists
    if cmds.workspaceControl(control_name, query=True, exists=True):
        # If it exists, just make it visible
        cmds.workspaceControl(control_name, edit=True, visible=True)
        print(f"[Maya] Showing existing {control_name}")
        return control_name
    
    # Create new workspace control
    try:
        # Create the dockable widget
        neo_dock = MayaDockableNeoEditor()
        
        # Create workspace control
        # Create workspace control with the widget
        workspace_control = cmds.workspaceControl(
            control_name,
            label=MayaDockableNeoEditor.WINDOW_TITLE,
            widthProperty="free",
            heightProperty="free",
            # Initial size
            initialWidth=800,
            initialHeight=600,
            # Docking behavior - start docked to the right like script editor
            dockToMainWindow=('right', 1),
            # Allow tabbing with other panels
            tabToControl=('ScriptEditor', -1),  # Tab with script editor if available
            # UI properties
            uiScript=f"import maya.cmds as cmds; print('[Maya] {control_name} UI script called')",
            retain=False,  # Don't retain when Maya restarts
            visible=True
        )
        
        # Set the dockable widget as the content
        neo_dock.show()
        
        print(f"[Maya] Created workspace control: {control_name}")
        print("[Maya] NEO Script Editor is now dockable like the built-in script editor!")
        print("[Maya] You can drag it around, dock it, or tab it with other panels")
        
        return workspace_control
        
    except Exception as e:
        print(f"[!] Failed to create workspace control: {e}")
        import traceback
        traceback.print_exc()
        return None


def show_neo_editor_docked():
    """
    Main function to show the dockable NEO Script Editor
    This is the function you call from Maya
    """
    if not MAYA_AVAILABLE:
        print("[!] This function must be run inside Maya")
        return None
    
    print("🚀 Launching Maya-dockable NEO Script Editor...")
    
    try:
        control = create_workspace_control()
        if control:
            print("✅ NEO Script Editor is now docked and ready!")
            print("💡 Tip: You can drag it around, dock it anywhere, or tab it with other panels")
            print("💡 Try docking it at the top to have your editor above the viewport!")
            return control
        else:
            print("❌ Failed to create dockable NEO Script Editor")
            return None
            
    except Exception as e:
        print(f"❌ Error launching dockable NEO Script Editor: {e}")
        import traceback
        traceback.print_exc()
        return None


def hide_neo_editor():
    """Hide the NEO Script Editor workspace control"""
    if not MAYA_AVAILABLE:
        return
    
    control_name = MayaDockableNeoEditor.CONTROL_NAME
    if cmds.workspaceControl(control_name, query=True, exists=True):
        cmds.workspaceControl(control_name, edit=True, visible=False)
        print("[Maya] NEO Script Editor hidden")


def delete_neo_editor():
    """Completely delete the NEO Script Editor workspace control"""
    if not MAYA_AVAILABLE:
        return
    
    control_name = MayaDockableNeoEditor.CONTROL_NAME
    if cmds.workspaceControl(control_name, query=True, exists=True):
        cmds.deleteUI(control_name, control=True)
        print("[Maya] NEO Script Editor workspace control deleted")


# Convenience function for easy Maya integration
launch_neo_docked = show_neo_editor_docked


if __name__ == "__main__":
    # If run directly in Maya
    if MAYA_AVAILABLE:
        show_neo_editor_docked()
    else:
        print("[!] This module is designed to run inside Maya")
        print("[!] To use outside Maya, use main_window.py or run.py instead")