"""
Debug Manager
Handles debugging functionality with breakpoints (VSCode-style)
"""
import sys
import traceback
import os
from qt_compat import QtWidgets, QtCore, QtGui


class DebugStopException(Exception):
    """Exception raised to stop debugging execution"""
    pass


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
        current_widget = self.parent.tabWidget.currentWidget()
        if hasattr(current_widget, 'toPlainText'):  # Check if it's an editor
            return current_widget
        return None
    
    def run_with_breakpoints(self):
        """Execute code with breakpoint support."""
        from .dialog_styles import create_message_box
        
        editor = self.get_current_editor()
        if not editor:
            msg_box = create_message_box(
                self.parent, "Debug Error", 
                "No active editor found.", "warning"
            )
            msg_box.exec()
            return
        
        # Get breakpoints
        breakpoints = editor.get_breakpoints()
        if not breakpoints:
            msg_box = create_message_box(
                self.parent, "Debug Info",
                "ℹ️ No breakpoints set. Click in the left margin to add breakpoints.", "information"
            )
            msg_box.exec()
            return
        
        # Get code
        code = editor.toPlainText()
        if not code.strip():
            return
        
        # Set debugging flag
        self.is_debugging = True
        editor.clear_current_debug_line()
        
        # Get console for output
        console = getattr(self.parent, 'console', None)
        if console:
            console.append(f"\n{'='*50}\n[DEBUG] Debug Mode - Breakpoints: {len(breakpoints)}\n{'='*50}\n")
        
        try:
            # Prepare namespace - use same dict for globals and locals
            # This ensures functions defined in code are available when called
            self.debug_globals = {
                '__name__': '__main__',
                '__builtins__': __builtins__
            }
            self.debug_locals = self.debug_globals  # Use same dict!
            
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
            
            # Redirect stdout/stderr to console if available
            if console:
                import sys
                from io import StringIO
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = StringIO()
                sys.stderr = StringIO()
            
            # Execute with tracing for breakpoints
            # Use same namespace for both globals and locals
            sys.settrace(self._trace_function)
            exec(compiled, self.debug_globals, self.debug_globals)
            sys.settrace(None)
            
            # Restore and capture output
            if console:
                output = sys.stdout.getvalue()
                errors = sys.stderr.getvalue()
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
                if output:
                    console.append(output)
                if errors:
                    console.append(f"<span style='color:#f48771'>{errors}</span>")
            
            # Clear debug line
            editor.clear_current_debug_line()
            
            # Show completion message
            if console:
                console.append(f"\n{'='*50}\n[OK] Debug Complete\n{'='*50}\n")
        
        except DebugStopException:
            # User stopped debugging - this is normal, not an error
            sys.settrace(None)
            
            # Restore stdout/stderr if redirected
            if console and 'old_stdout' in locals():
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            editor.clear_current_debug_line()
            
            if console:
                console.append(f"\n{'='*50}\n⏹️ Debug Stopped by User\n{'='*50}\n")
            
        except Exception as e:
            sys.settrace(None)
            
            # Restore stdout/stderr if redirected
            if console and 'old_stdout' in locals():
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            editor.clear_current_debug_line()
            error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            
            if console:
                console.append(f"<span style='color:#f48771'>[ERROR] Debug Error:\n{error_msg}</span>")
            
            from .dialog_styles import create_message_box
            msg_box = create_message_box(
                self.parent, "Debug Error", f"{error_msg}", "critical"
            )
            msg_box.exec()
        finally:
            self.is_debugging = False
    
    def _trace_function(self, frame, event, arg):
        """Trace function for breakpoint handling."""
        # Check if debugging was stopped
        if not self.is_debugging:
            raise DebugStopException("Debugging stopped by user")
        
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
        from .dialog_styles import apply_dark_theme
        
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle(f"Breakpoint Hit - Line {lineno}")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        # Apply consistent dark theme
        apply_dark_theme(dialog)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Info label
        info_label = QtWidgets.QLabel(f"<b>🔴 Breakpoint at line {lineno}</b>")
        info_label.setStyleSheet("color: #00ff41; font-size: 14px;")
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
        stop_btn.setObjectName("stopBtn")  # For special styling
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
        from .dialog_styles import create_message_box
        
        editor = self.get_current_editor()
        if editor:
            editor.clear_all_breakpoints()
            msg_box = create_message_box(
                self.parent, "Breakpoints Cleared",
                "All breakpoints have been cleared.", "information"
            )
            
            # Set custom icon (suggestion.png)
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            success_icon_path = os.path.join(assets_dir, "suggestion.png")
            if os.path.exists(success_icon_path):
                icon_pixmap = QtGui.QPixmap(success_icon_path)
                msg_box.setIconPixmap(icon_pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            
            msg_box.exec()
