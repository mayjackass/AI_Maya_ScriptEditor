# ai_script_editor/__init__.py
"""
NEO Script Editor – Maya integration launcher
Compatible with Maya 2022-2024 (PySide2) and Maya 2025+ (PySide6)
"""

import sys
import os


def launch_ai_script_editor():
    """Launch the full NEO Script Editor UI."""
    try:
        # Add current directory to Python path for proper imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import Qt compatibility layer
        from qt_compat import QtWidgets, QT_VERSION
        
        # Try different import patterns
        try:
            from ai_script_editor.main_window import AiScriptEditor
        except ImportError:
            # Fallback for Maya environment
            from main_window import AiScriptEditor

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        win = AiScriptEditor()
        win.show()

        print(f"NEO Script Editor v3.2 Beta launched successfully (Qt {QT_VERSION}).")
        return win

    except Exception as e:
        import traceback
        print("Failed to launch NEO Script Editor:", e)
        print("# Traceback (most recent call last):")
        for line in traceback.format_exc().splitlines():
            print(f"# {line}")
        return None
