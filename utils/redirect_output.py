import sys
import contextlib
from PySide6 import QtCore, QtGui

@contextlib.contextmanager
def redirect_output(widget):
    """Redirect sys.stdout and sys.stderr into a QTextEdit/QTextBrowser-like widget.

    Usage:
      with redirect_output(my_console):
          print("hello")
    """
    class _Writer:
        def __init__(self, w):
            self.w = w
        def write(self, text):
            if not text:
                return
            try:
                QtCore.QMetaObject.invokeMethod(
                    self.w,
                    "insertPlainText",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                    QtCore.Q_ARG(str, str(text))
                )
                QtCore.QMetaObject.invokeMethod(
                    self.w,
                    "ensureCursorVisible",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                )
            except Exception:
                # fallback: attempt synchronous append (may only work on main thread)
                try:
                    self.w.moveCursor(QtGui.QTextCursor.MoveOperation.End)
                    self.w.insertPlainText(str(text))
                    self.w.ensureCursorVisible()
                except Exception:
                    pass
        def flush(self):
            pass

    old_out, old_err = sys.stdout, sys.stderr
    writer = _Writer(widget)
    sys.stdout = writer
    sys.stderr = writer
    try:
        yield
    finally:
        sys.stdout = old_out
        sys.stderr = old_err

class AICophylot:
    def __init__(self, parent_window, client=None):
        self.window = parent_window
        self.client = client
    def send_prompt(self, prompt_text, context=""):
        # move your _send_prompt streaming logic here, but call back into window to append messages / show suggestions
        with redirect_output(self.window.chatDisplay):
            print(prompt_text)
        raise RuntimeError("PLACEHOLDER: paste streaming logic here (use parent_window.chatDisplay and parent_window.applySuggestionBtn)")