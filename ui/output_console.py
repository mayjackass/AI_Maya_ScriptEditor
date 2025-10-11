from PySide6 import QtWidgets, QtCore, QtGui
import sys
import traceback
from datetime import datetime


class OutputConsole(QtWidgets.QTextEdit):
    """Thread-safe console with colored logs, auto-scroll, and tag support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._auto_scroll = True

        # Style
        self.setStyleSheet("""
            background:#111;
            color:#DDD;
            font-family:Consolas;
            font-size:10pt;
            border:none;
            padding:6px;
        """)

        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # Maya-style console enhancements
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._capture_output = False
        
        # Initialize with welcome message
        self._show_welcome_message()

    # =====================================================
    #   Public API
    # =====================================================
    def append_tagged(self, tag: str, msg: str, color="#9ef"):
        """Append a log line with colored tag."""
        html = f"<span style='color:{color};'><b>{tag}</b></span> {msg}"
        self._append_html_threadsafe(html)

    def append(self, msg: str):
        """Append plain text safely."""
        safe = msg.replace("<", "&lt;").replace(">", "&gt;")
        self._append_html_threadsafe(f"<span style='color:#DDD;'>{safe}</span>")

    def log(self, msg: str, level: str = "info"):
        """Convenience wrapper for different log levels."""
        color = {
            "info": "#9ef",
            "warn": "#fc3",
            "error": "#f66",
            "success": "#9f9",
            "debug": "#888",
        }.get(level.lower(), "#ccc")
        self.append_tagged(level.upper(), msg, color=color)

    # =====================================================
    #   Thread-safe appending and auto-scroll
    # =====================================================
    def _append_html_threadsafe(self, html: str):
        """Append HTML text safely from any thread."""
        QtCore.QMetaObject.invokeMethod(
            self,
            "_insert_html",
            QtCore.Qt.ConnectionType.QueuedConnection,
            QtCore.Q_ARG(str, html),
        )

    @QtCore.Slot(str)
    def _insert_html(self, html: str):
        """Internal slot for queued text insertion."""
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertHtml(html + "<br>")
        if self._auto_scroll:
            self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.ensureCursorVisible()

    # =====================================================
    #   Auto-scroll toggle
    # =====================================================
    def _on_scroll(self):
        sb = self.verticalScrollBar()
        self._auto_scroll = sb.value() == sb.maximum()

    # =====================================================
    #   Context menu (clear / copy)
    # =====================================================
    def _show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.addAction("Copy", self.copy)
        menu.addAction("Clear", self.clear)
        menu.addSeparator()
        
        # Toggle output capture
        if self._capture_output:
            menu.addAction("📴 Disable Output Capture", self.disable_output_capture)
        else:
            menu.addAction("📡 Enable Output Capture", self.enable_output_capture)
            
        menu.exec_(self.mapToGlobal(pos))
    
    # =====================================================
    #   Maya-style Output Capture
    # =====================================================
    def _show_welcome_message(self):
        """Show NEO Script Editor welcome message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        welcome = f"""<span style='color:#58a6ff; font-weight:bold;'>
╭─────────────────────────────────────────────────────────────────╮
│                    NEO Script Editor v2.0                      │
│              Developed by Mayj Amilano with ❤️                │  
│                     Output Console Ready                        │
╰─────────────────────────────────────────────────────────────────╯</span>

<span style='color:#9ef;'>[{timestamp}] Console initialized.</span>
<span style='color:#9f9;'>[{timestamp}] Right-click to enable output capture for print statements.</span>
<span style='color:#fc3;'>[{timestamp}] Run Python/MEL code to see results here!</span>
"""
        self._append_html_threadsafe(welcome)
    
    def enable_output_capture(self):
        """Enable capturing stdout/stderr to console."""
        if not self._capture_output:
            self._capture_output = True
            sys.stdout = ConsoleRedirect(self, "stdout")
            sys.stderr = ConsoleRedirect(self, "stderr")
            self.append_tagged("CAPTURE", "Output capture ENABLED - print() statements will appear here", "#9f9")
    
    def disable_output_capture(self):
        """Disable output capture and restore original streams."""
        if self._capture_output:
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._capture_output = False
            self.append_tagged("CAPTURE", "Output capture DISABLED", "#fc3")
    
    def execute_code_and_capture(self, code, language="python"):
        """Execute code and capture all output like Maya's script editor."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Show the code being executed
        self.append_tagged("EXEC", f"Executing {language} code:", "#58a6ff")
        code_html = f"<span style='color:#ddd; background:#1a1a1a; padding:4px; border-left:3px solid #58a6ff; display:block; margin:4px 0;'><pre>{code}</pre></span>"
        self._append_html_threadsafe(code_html)
        
        # Temporarily enable output capture for execution
        was_capturing = self._capture_output
        if not was_capturing:
            self.enable_output_capture()
        
        try:
            if language.lower() == "python":
                # Execute Python code
                exec_globals = {"__name__": "__main__"}
                exec(code, exec_globals)
                self.append_tagged("SUCCESS", f"Python code executed successfully at {timestamp}", "#9f9")
                
            elif language.lower() == "mel":
                # For MEL, we'd need Maya's mel module
                try:
                    import maya.mel as mel
                    result = mel.eval(code)
                    if result is not None:
                        self.append_tagged("MEL", f"Result: {result}", "#9f9")
                    self.append_tagged("SUCCESS", f"MEL code executed successfully at {timestamp}", "#9f9")
                except ImportError:
                    self.append_tagged("ERROR", "MEL execution requires Maya environment", "#f66")
                except Exception as e:
                    self.append_tagged("ERROR", f"MEL execution error: {str(e)}", "#f66")
                    
        except Exception as e:
            # Show detailed error information
            self.append_tagged("ERROR", f"Execution failed at {timestamp}", "#f66")
            error_details = traceback.format_exc()
            error_html = f"<span style='color:#f66; background:#2a1a1a; padding:4px; border-left:3px solid #f66; display:block; margin:4px 0;'><pre>{error_details}</pre></span>"
            self._append_html_threadsafe(error_html)
        
        # Restore original capture state
        if not was_capturing:
            self.disable_output_capture()


class ConsoleRedirect:
    """Redirect stdout/stderr to console widget."""
    
    def __init__(self, console, stream_name):
        self.console = console
        self.stream_name = stream_name
        
    def write(self, text):
        if text.strip():  # Only log non-empty text
            timestamp = datetime.now().strftime("%H:%M:%S")
            color = "#f66" if self.stream_name == "stderr" else "#ddd"
            tag = "ERROR" if self.stream_name == "stderr" else "OUTPUT"
            self.console.append_tagged(f"{tag}", f"[{timestamp}] {text.strip()}", color)
    
    def flush(self):
        pass
