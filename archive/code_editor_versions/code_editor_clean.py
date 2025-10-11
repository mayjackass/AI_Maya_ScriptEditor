"""
AI Script Editor – Clean Code Editor
Compatible with Maya 2020–2026 (PySide2/PySide6)
Basic code editor with line numbers and syntax highlighting.
"""

import os
from PySide6 import QtCore, QtGui, QtWidgets
from .highlighter import PythonHighlighter


class _LineNumberArea(QtWidgets.QWidget):
    """Widget to display line numbers next to the code editor."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.code_editor._number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor._paint_line_numbers(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    """Basic code editor with line numbers and syntax highlighting."""

    requestAICompletion = QtCore.Signal(str)   # emitted with context string
    lintProblemsFound = QtCore.Signal(list)    # emitted when linting issues found

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QtGui.QFont("Consolas", 10)
        font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 10pt;
                line-height: 1.5;
                selection-background-color: #264F78;
                border: none;
            }
        """)
        fm = QtGui.QFontMetrics(font)
        self.setTabStopDistance(4 * fm.horizontalAdvance(' '))
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        
        # Syntax error tracking
        self.syntax_errors = []
        self.error_timer = QtCore.QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self._check_syntax_errors)
        
        # Connect text changes to syntax checking
        self.textChanged.connect(self._on_text_changed)
        self.highlighter = PythonHighlighter(self.document())

        # --- Line number area
        self.number_area = _LineNumberArea(self)
        self.blockCountChanged.connect(self._update_number_area_width)
        self.updateRequest.connect(self._update_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        
        # Force initial line number area width calculation
        self._update_number_area_width(0)
        
        # Ensure proper sizing on widget show
        QtCore.QTimer.singleShot(0, self._ensure_line_numbers_visible)

        # --- Ghost text overlay
        self.ghost_label = QtWidgets.QLabel(self)
        self.ghost_label.setStyleSheet("color:#777;font-style:italic;")
        self.ghost_label.hide()

    def _ensure_line_numbers_visible(self):
        """Ensure line numbers are properly visible after widget initialization."""
        self._update_number_area_width(0)
        self.number_area.update()
        
        # Force a second update after a short delay to handle timing issues
        QtCore.QTimer.singleShot(10, self._ensure_line_numbers_visible)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Handle line number area resize
        cr = self.contentsRect()
        self.number_area.setGeometry(QtCore.QRect(
            cr.left(), cr.top(),
            self._number_area_width(), cr.height()
        ))

    def _number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        fm = self.fontMetrics()
        return 10 + fm.horizontalAdvance('9') * digits

    def _update_number_area_width(self, _):
        """Update the viewport margins to accommodate line numbers."""
        self.setViewportMargins(self._number_area_width(), 0, 0, 0)

    def _update_number_area(self, rect, dy):
        """Update the line number area when the editor is scrolled."""
        if dy:
            self.number_area.scroll(0, dy)
        else:
            self.number_area.update(0, rect.y(), self.number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_number_area_width(0)

    def _paint_line_numbers(self, event):
        """Paint line numbers in the line number area."""
        painter = QtGui.QPainter(self.number_area)
        painter.fillRect(event.rect(), QtGui.QColor("#2d2d30"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QtGui.QColor("#858585"))
                painter.drawText(0, top, self.number_area.width() - 5, 
                               self.fontMetrics().height(),
                               QtCore.Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def _highlight_current_line(self):
        """Highlight the current line where the cursor is positioned."""
        extra_selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor("#2d2d30").lighter(120)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def keyPressEvent(self, event):
        """Handle key press events for editor functionality."""
        # Handle Ctrl+F for find
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_F:
            self._show_find_dialog()
            return
        
        # Handle basic editor functionality
        super().keyPressEvent(event)

    def _show_find_dialog(self):
        """Show a simple find dialog."""
        text, ok = QtWidgets.QInputDialog.getText(self, 'Find', 'Find text:')
        if ok and text:
            # Simple find functionality
            cursor = self.textCursor()
            found = self.find(text)
            if not found:
                # If not found from current position, search from beginning
                cursor.movePosition(QtGui.QTextCursor.Start)
                self.setTextCursor(cursor)
                self.find(text)

    # AI-related methods (simplified/disabled)
    def request_ai_completion(self):
        """Request AI completion (disabled in clean version)."""
        pass

    def insert_suggestion(self, suggestion):
        """Insert AI suggestion (disabled in clean version)."""
        pass

    def clear_ghost_text(self):
        """Clear ghost text (disabled in clean version)."""
        self.ghost_label.hide()

    def set_ghost_text(self, text):
        """Set ghost text (disabled in clean version)."""
        pass

    # File operations
    def load_file(self, file_path):
        """Load file content into the editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.setPlainText(content)
            return True
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not load file: {e}")
            return False

    def save_file(self, file_path):
        """Save editor content to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            return True
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not save file: {e}")
            return False

    def get_current_line_number(self):
        """Get the current line number (1-indexed)."""
        return self.textCursor().blockNumber() + 1

    def goto_line(self, line_number):
        """Go to a specific line number (1-indexed)."""
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, line_number - 1)
        self.setTextCursor(cursor)
        self.centerCursor()

    def _on_text_changed(self):
        """Handle text changes to trigger syntax checking."""
        # Debounce syntax checking to avoid excessive calls
        self.error_timer.start(500)  # Check after 500ms of no typing

    def _check_syntax_errors(self):
        """Check for Python syntax errors and highlight them."""
        code = self.toPlainText()
        self.syntax_errors = []
        
        if not code.strip():
            self._update_error_highlights()
            return
        
        try:
            # Try to compile the code to catch syntax errors
            compile(code, '<editor>', 'exec')
            # If compilation succeeds, clear any existing errors
            self.syntax_errors = []
        except SyntaxError as e:
            # Handle syntax errors
            error_info = {
                'line': e.lineno or 1,
                'column': e.offset or 1,
                'message': str(e.msg) if e.msg else 'Syntax error',
                'type': 'SyntaxError'
            }
            self.syntax_errors = [error_info]
        except Exception as e:
            # Handle other compilation errors
            error_info = {
                'line': 1,
                'column': 1,
                'message': str(e),
                'type': 'CompileError'
            }
            self.syntax_errors = [error_info]
        
        # Update visual error indicators
        self._update_error_highlights()
        
        # Emit signal with problems for the problems panel
        self.lintProblemsFound.emit(self.syntax_errors)

    def _update_error_highlights(self):
        """Update visual error highlights in the editor."""
        # Get existing selections (like current line highlight)
        extra_selections = []
        
        # Add current line highlight if no errors on current line
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor("#2d2d30").lighter(120)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        # Add error highlights (red wavy underlines)
        for error in self.syntax_errors:
            selection = QtWidgets.QTextEdit.ExtraSelection()
            
            # Red wavy underline format
            error_format = QtGui.QTextCharFormat()
            error_format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
            error_format.setUnderlineColor(QtGui.QColor("#ff4444"))  # Red color
            selection.format = error_format
            
            # Position cursor at error line
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, error['line'] - 1)
            
            # Select the entire line or specific position if column is available
            if error.get('column', 0) > 0:
                cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, error['column'] - 1)
                cursor.movePosition(QtGui.QTextCursor.EndOfWord, QtGui.QTextCursor.KeepAnchor)
            else:
                cursor.select(QtGui.QTextCursor.LineUnderCursor)
            
            selection.cursor = cursor
            extra_selections.append(selection)
        
        # Apply all selections
        self.setExtraSelections(extra_selections)

    def get_syntax_errors(self):
        """Get current syntax errors."""
        return self.syntax_errors

    def clear_syntax_errors(self):
        """Clear syntax error highlights."""
        self.syntax_errors = []
        self._update_error_highlights()