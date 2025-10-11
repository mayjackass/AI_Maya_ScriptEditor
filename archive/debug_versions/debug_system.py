"""
Python Debugger Integration for NEO Script Editor
Provides debugging capabilities with breakpoints, step-through, and variable inspection.
"""

import sys
import pdb
import traceback
import threading
from contextlib import contextmanager
from PySide6 import QtCore, QtGui, QtWidgets


class DebugSession(QtCore.QObject):
    """Manages a Python debugging session using the built-in pdb debugger."""
    
    # Signals for debug events
    debugStarted = QtCore.Signal()
    debugStopped = QtCore.Signal()
    debugPaused = QtCore.Signal(int)  # line_number
    debugResumed = QtCore.Signal()
    variablesUpdated = QtCore.Signal(dict)  # variable_dict
    outputReceived = QtCore.Signal(str)  # debug_output
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._debugger = None
        self._is_running = False
        self._current_frame = None
        self._breakpoints = {}  # filename -> set of line numbers
        self._step_mode = None  # 'over', 'into', 'out', None
    
    def set_breakpoints(self, file_path, line_numbers):
        """Set breakpoints for a file."""
        self._breakpoints[file_path] = set(line_numbers)
    
    def start_debug(self, file_path, code):
        """Start debugging the given code."""
        if self._is_running:
            self.stop_debug()
        
        try:
            # Create a custom debugger
            self._debugger = CustomDebugger(self)
            
            # Set breakpoints
            if file_path in self._breakpoints:
                for line_num in self._breakpoints[file_path]:
                    self._debugger.set_break(file_path, line_num)
            
            self._is_running = True
            self.debugStarted.emit()
            
            # Execute code in debugger
            self._run_code_in_debugger(file_path, code)
            
        except Exception as e:
            self.outputReceived.emit(f"Debug error: {str(e)}")
            self.stop_debug()
    
    def _run_code_in_debugger(self, file_path, code):
        """Execute code under debugger control."""
        try:
            # Compile the code
            compiled_code = compile(code, file_path, 'exec')
            
            # Create execution namespace
            namespace = {
                '__file__': file_path,
                '__name__': '__main__'
            }
            
            # Run with debugger
            self._debugger.run(compiled_code, namespace, namespace)
            
        except SystemExit:
            pass  # Normal exit
        except Exception as e:
            self.outputReceived.emit(f"Execution error: {str(e)}")
        finally:
            self.stop_debug()
    
    def step_over(self):
        """Step over current line."""
        if self._debugger and self._is_running:
            self._step_mode = 'over'
            self._debugger.set_step()
    
    def step_into(self):
        """Step into function calls."""
        if self._debugger and self._is_running:
            self._step_mode = 'into'
            self._debugger.set_step()
    
    def step_out(self):
        """Step out of current function."""
        if self._debugger and self._is_running:
            self._step_mode = 'out'
            self._debugger.set_return()
    
    def continue_execution(self):
        """Continue execution until next breakpoint."""
        if self._debugger and self._is_running:
            self._step_mode = None
            self._debugger.set_continue()
    
    def stop_debug(self):
        """Stop the debugging session."""
        if self._debugger:
            try:
                self._debugger.set_quit()
            except:
                pass
        
        self._is_running = False
        self._current_frame = None
        self._debugger = None
        self.debugStopped.emit()
    
    def get_variables(self):
        """Get current variables from the debug frame."""
        if self._current_frame:
            locals_dict = self._current_frame.f_locals.copy()
            globals_dict = {k: v for k, v in self._current_frame.f_globals.items() 
                           if not k.startswith('__') or k in ['__file__', '__name__']}
            return {'locals': locals_dict, 'globals': globals_dict}
        return {'locals': {}, 'globals': {}}


class CustomDebugger(pdb.Pdb):
    """Custom debugger that integrates with the NEO Script Editor."""
    
    def __init__(self, session):
        super().__init__()
        self.session = session
    
    def user_line(self, frame):
        """Called when debugger stops at a line."""
        self.session._current_frame = frame
        line_number = frame.f_lineno
        
        # Emit debug paused signal
        self.session.debugPaused.emit(line_number)
        
        # Update variables
        variables = self.session.get_variables()
        self.session.variablesUpdated.emit(variables)
        
        # Call parent to handle stepping
        super().user_line(frame)
    
    def user_return(self, frame, return_value):
        """Called when debugger returns from a function."""
        self.session._current_frame = frame
        super().user_return(frame, return_value)
    
    def user_exception(self, frame, exception_info):
        """Called when an exception occurs."""
        exc_type, exc_value, exc_traceback = exception_info
        self.session.outputReceived.emit(
            f"Exception: {exc_type.__name__}: {exc_value}"
        )
        super().user_exception(frame, exception_info)


class DebugControlPanel(QtWidgets.QWidget):
    """Debug control panel with buttons and variable inspection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.debug_session = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the debug control UI."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Debug control buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.start_btn = QtWidgets.QPushButton("▶️ Start Debug")
        self.start_btn.clicked.connect(self.start_debug)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QtWidgets.QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_debug)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.continue_btn = QtWidgets.QPushButton("▶️ Continue")
        self.continue_btn.clicked.connect(self.continue_execution)
        self.continue_btn.setEnabled(False)
        button_layout.addWidget(self.continue_btn)
        
        layout.addLayout(button_layout)
        
        # Step control buttons
        step_layout = QtWidgets.QHBoxLayout()
        
        self.step_over_btn = QtWidgets.QPushButton("↷ Step Over")
        self.step_over_btn.clicked.connect(self.step_over)
        self.step_over_btn.setEnabled(False)
        step_layout.addWidget(self.step_over_btn)
        
        self.step_into_btn = QtWidgets.QPushButton("↘️ Step Into")
        self.step_into_btn.clicked.connect(self.step_into)
        self.step_into_btn.setEnabled(False)
        step_layout.addWidget(self.step_into_btn)
        
        self.step_out_btn = QtWidgets.QPushButton("↗️ Step Out")
        self.step_out_btn.clicked.connect(self.step_out)
        self.step_out_btn.setEnabled(False)
        step_layout.addWidget(self.step_out_btn)
        
        layout.addLayout(step_layout)
        
        # Variable inspection
        layout.addWidget(QtWidgets.QLabel("Variables:"))
        
        self.variable_tree = QtWidgets.QTreeWidget()
        self.variable_tree.setHeaderLabels(["Name", "Type", "Value"])
        self.variable_tree.setAlternatingRowColors(True)
        layout.addWidget(self.variable_tree)
        
        # Debug output
        layout.addWidget(QtWidgets.QLabel("Debug Output:"))
        
        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setMaximumHeight(100)
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # Apply dark styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                color: #cccccc;
            }
            QPushButton {
                background-color: #0e639c;
                border: 1px solid #007acc;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #555555;
                border-color: #666666;
                color: #888888;
            }
            QTreeWidget {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
        """)
    
    def set_debug_session(self, session):
        """Set the debug session to control."""
        self.debug_session = session
        if session:
            session.debugStarted.connect(self._on_debug_started)
            session.debugStopped.connect(self._on_debug_stopped)
            session.debugPaused.connect(self._on_debug_paused)
            session.variablesUpdated.connect(self._update_variables)
            session.outputReceived.connect(self._add_output)
    
    def start_debug(self):
        """Start debugging the current file."""
        if self.debug_session:
            # This will be connected to the main window's debug start logic
            pass
    
    def stop_debug(self):
        """Stop debugging."""
        if self.debug_session:
            self.debug_session.stop_debug()
    
    def continue_execution(self):
        """Continue execution."""
        if self.debug_session:
            self.debug_session.continue_execution()
    
    def step_over(self):
        """Step over current line."""
        if self.debug_session:
            self.debug_session.step_over()
    
    def step_into(self):
        """Step into function."""
        if self.debug_session:
            self.debug_session.step_into()
    
    def step_out(self):
        """Step out of function."""
        if self.debug_session:
            self.debug_session.step_out()
    
    def _on_debug_started(self):
        """Handle debug session started."""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.continue_btn.setEnabled(True)
        self.step_over_btn.setEnabled(True)
        self.step_into_btn.setEnabled(True)
        self.step_out_btn.setEnabled(True)
        self._add_output("🐛 Debug session started")
    
    def _on_debug_stopped(self):
        """Handle debug session stopped."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)
        self.step_over_btn.setEnabled(False)
        self.step_into_btn.setEnabled(False)
        self.step_out_btn.setEnabled(False)
        self.variable_tree.clear()
        self._add_output("🔴 Debug session stopped")
    
    def _on_debug_paused(self, line_number):
        """Handle debug session paused at line."""
        self._add_output(f"⏸️ Paused at line {line_number}")
    
    def _update_variables(self, variables):
        """Update the variable tree display."""
        self.variable_tree.clear()
        
        # Add locals
        locals_root = QtWidgets.QTreeWidgetItem(["Locals", "", ""])
        self.variable_tree.addTopLevelItem(locals_root)
        
        for name, value in variables.get('locals', {}).items():
            if not name.startswith('__'):  # Skip internal variables
                self._add_variable_item(locals_root, name, value)
        
        # Add globals (filtered)
        globals_root = QtWidgets.QTreeWidgetItem(["Globals", "", ""])
        self.variable_tree.addTopLevelItem(globals_root)
        
        for name, value in variables.get('globals', {}).items():
            if not name.startswith('__') or name in ['__file__', '__name__']:
                self._add_variable_item(globals_root, name, value)
        
        # Expand the trees
        locals_root.setExpanded(True)
        globals_root.setExpanded(True)
    
    def _add_variable_item(self, parent, name, value):
        """Add a variable to the tree."""
        try:
            value_type = type(value).__name__
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            
            item = QtWidgets.QTreeWidgetItem([name, value_type, value_str])
            parent.addChild(item)
        except Exception:
            # Handle cases where str(value) might fail
            item = QtWidgets.QTreeWidgetItem([name, "unknown", "<cannot display>"])
            parent.addChild(item)
    
    def _add_output(self, message):
        """Add message to debug output."""
        self.output_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())