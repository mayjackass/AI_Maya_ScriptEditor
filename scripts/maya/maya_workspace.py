"""
NEO Script Editor - Maya Workspace Control Integration
Provides native Maya dockable window (drag-to-dock like Script Editor)
"""
import sys
import os


def launch_neo_as_workspace():
    """
    Launch NEO as a Maya workspace control (dockable window)
    This creates a window that can be dragged to dock, just like Maya's Script Editor
    """
    try:
        from maya import cmds
        import maya.OpenMayaUI as omui
        
        # Add NEO to path
        neo_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if neo_dir not in sys.path:
            sys.path.insert(0, neo_dir)
        
        from qt_compat import QtWidgets
        from main_window import AiScriptEditor
        
        # Workspace control name
        workspace_name = "NEOScriptEditorWorkspace"
        
        # Delete existing workspace if it exists
        if cmds.workspaceControl(workspace_name, exists=True):
            cmds.deleteUI(workspace_name)
        
        # Create the NEO window
        neo_window = AiScriptEditor()
        
        # Get the Qt window pointer
        neo_window_ptr = int(neo_window.winId())
        
        # Wrap it in a Maya workspace control
        cmds.workspaceControl(
            workspace_name,
            retain=False,  # Don't save with scene
            floating=True,  # Start floating (user can drag to dock)
            uiScript="",  # No UI script needed, we already created it
            widthProperty="free",
            heightProperty="free",
            initialWidth=1200,
            initialHeight=700,
            label="NEO Script Editor"
        )
        
        # Show the window
        neo_window.show()
        
        print("✅ [NEO] Launched as workspace control (drag to dock anywhere)")
        return neo_window
        
    except Exception as e:
        print(f"❌ [NEO] Workspace launch failed: {e}")
        print("[NEO] Falling back to regular window...")
        import traceback
        traceback.print_exc()
        
        # Fallback to regular window
        from main_window import main
        return main()


if __name__ == "__main__":
    launch_neo_as_workspace()
