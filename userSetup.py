"""
Maya userSetup.py for NEO Script Editor
Place this file in: C:\Users\Burn\Documents\maya\scripts\

This will automatically make the NEO Script Editor available in Maya.
"""

import sys
import os

def setup_neo_editor():
    """Setup NEO Script Editor for Maya"""
    try:
        # Add the ai_script_editor directory to Python path
        neo_path = os.path.join(os.path.dirname(__file__), 'ai_script_editor')
        
        if neo_path not in sys.path:
            sys.path.insert(0, neo_path)
            print("[NEO] ✓ Script Editor path added to sys.path")
        
        # Create launcher function
        def launch_neo_editor():
            """Launch NEO Script Editor in Maya"""
            try:
                from main_window import AiScriptEditor
                window = AiScriptEditor()
                window.show()
                return window
            except Exception as e:
                print(f"[NEO] Launch failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Make it globally available
        import __main__
        __main__.launch_neo_editor = launch_neo_editor
        
        print("[NEO] ✓ Script Editor ready! Type 'launch_neo_editor()' to open")
        
    except Exception as e:
        print(f"[NEO] ✗ Setup failed: {e}")

# Run setup when Maya starts
setup_neo_editor()
