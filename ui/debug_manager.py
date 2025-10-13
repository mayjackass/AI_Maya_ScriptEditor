"""
Debug Manager
Handles debugging functionality with breakpoints (VSCode-style)
"""
import sys
import traceback
from PySide6 import QtWidgets, QtCore


class DebugManager:
    """Manages debugging with breakpoints"""
    
    def __init__(self, parent):
        """
        Initialize DebugManager
        
        Args:
            parent: Main window instance
        """
        self.parent = parent
        self.is_debugging = False
        self.debug_locals = {}
        self.debug_globals = {}
        
    def get_current_editor(self):
        """Get the currently active code editor."""
        current_widget = self.parent.tabs.currentWidget()
        if hasattr(current_widget, 'toPlainText'):  # Check if it's an editor
            return current_widget
        return None
    
    def run_with_breakpoints(self):
        """Execute code with breakpoint support."""
        editor = self.get_current_editor()
        if not editor:
            QtWidgets.QMessageBox.warning(
                self.parent, "Debug Error", 
                "No active editor found."
            )
            return
        
        # Get breakpoints
        breakpoints = editor.get_breakpoints()
        if not breakpoints:
            QtWidgets.QMessageBox.information(
                self.parent, "Debug Info",
                "No breakpoints set. Click in the left margin to add breakpoints."
            )
            return
        
        # Get code
        code = editor.toPlainText()
        if not code.strip():
            return
        
        # Set debugging flag
        self.is_debugging = True
        editor.clear_current_debug_line()
        
        try:
            # Prepare globals and locals
            self.debug_globals = {'__name__': '__main__'}
            self.debug_locals = {}
            
            # Add Maya commands if available
            try:
                import maya.cmds as cmds
                import pymel.core as pm
                self.debug_globals['cmds'] = cmds
                self.debug_globals['pm'] = pm
            except:
                pass
            
            # Compile code
            compiled = compile(code, '<editor>', 'exec')
            
            # Execute with tracing for breakpoints
            sys.settrace(self._trace_function)
            exec(compiled, self.debug_globals, self.debug_locals)
            sys.settrace(None)
            
            # Clear debug line
            editor.clear_current_debug_line()
            
            # Show completion message
            QtWidgets.QMessageBox.information(
                self.parent, "Debug Complete",
                f"Code executed successfully.\nBreakpoints hit: {len(breakpoints)}"
            )
            
        except Exception as e:
            sys.settrace(None)
            editor.clear_current_debug_line()
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            QtWidgets.QMessageBox.critical(
                self.parent, "Debug Error", error_msg
            )
        finally:
            self.is_debugging = False
    
    def _trace_function(self, frame, event, arg):
        """Trace function for breakpoint handling."""
        if event == 'line':
            editor = self.get_current_editor()
            if not editor:
                return None
            
            # Get current line number
            lineno = frame.f_lineno
            
            # Check if this line has a breakpoint
            if lineno in editor.breakpoints:
                # Highlight the line
                editor.set_current_debug_line(lineno)
                
                # Show dialog with local variables
                self._show_breakpoint_dialog(frame, lineno)
        
        return self._trace_function if self.is_debugging else None
    
    def _show_breakpoint_dialog(self, frame, lineno):
        """Show dialog when breakpoint is hit."""
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle(f"Breakpoint Hit - Line {lineno}")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Info label
        info_label = QtWidgets.QLabel(f"<b>Breakpoint at line {lineno}</b>")
        layout.addWidget(info_label)
        
        # Variables tree
        var_label = QtWidgets.QLabel("Local Variables:")
        layout.addWidget(var_label)
        
        var_tree = QtWidgets.QTreeWidget()
        var_tree.setHeaderLabels(["Variable", "Value", "Type"])
        var_tree.setColumnWidth(0, 150)
        var_tree.setColumnWidth(1, 250)
        
        # Add local variables
        for name, value in frame.f_locals.items():
            if not name.startswith('__'):
                item = QtWidgets.QTreeWidgetItem([
                    name,
                    str(value)[:100],  # Truncate long values
                    type(value).__name__
                ])
                var_tree.addTopLevelItem(item)
        
        layout.addWidget(var_tree)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        continue_btn = QtWidgets.QPushButton("Continue (F5)")
        continue_btn.setShortcut("F5")
        continue_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(continue_btn)
        
        stop_btn = QtWidgets.QPushButton("Stop Debugging")
        stop_btn.clicked.connect(lambda: self._stop_debugging(dialog))
        button_layout.addWidget(stop_btn)
        
        layout.addLayout(button_layout)
        
        # Show dialog
        dialog.exec()
    
    def _stop_debugging(self, dialog):
        """Stop debugging session."""
        self.is_debugging = False
        editor = self.get_current_editor()
        if editor:
            editor.clear_current_debug_line()
        dialog.reject()
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints from current editor."""
        editor = self.get_current_editor()
        if editor:
            editor.clear_all_breakpoints()
            QtWidgets.QMessageBox.information(
                self.parent, "Breakpoints Cleared",
                "All breakpoints have been cleared."
            )
