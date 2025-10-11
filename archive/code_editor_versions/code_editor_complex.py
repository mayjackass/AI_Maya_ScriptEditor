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
        
        # Single additional update to handle timing issues
        QtCore.QTimer.singleShot(10, lambda: self.number_area.update())

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
        """Paint line numbers in the line number area with error indicators."""
        painter = QtGui.QPainter(self.number_area)
        painter.fillRect(event.rect(), QtGui.QColor("#2d2d30"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                # Check if this line has an error
                has_error = hasattr(self, '_error_lines') and block_number in self._error_lines
                
                if has_error:
                    # Draw red background for error line numbers
                    error_rect = QtCore.QRect(0, top, self.number_area.width(), self.fontMetrics().height())
                    painter.fillRect(error_rect, QtGui.QColor("#3c1e1e"))  # Dark red background
                    
                    # Draw red dot indicator
                    dot_size = 6
                    dot_x = 3
                    dot_y = top + (self.fontMetrics().height() - dot_size) // 2
                    painter.setBrush(QtGui.QColor("#ff4444"))  # Red dot
                    painter.setPen(QtCore.Qt.NoPen)
                    painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
                    
                    # Draw line number in red
                    painter.setPen(QtGui.QColor("#ff6b6b"))
                else:
                    # Normal line number color
                    painter.setPen(QtGui.QColor("#858585"))
                
                painter.drawText(0, top, self.number_area.width() - 5, 
                               self.fontMetrics().height(),
                               QtCore.Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def _highlight_current_line(self):
        """Highlight the current line while preserving error selections - optimized."""
        # Get ALL current error selections first - NEVER lose them
        error_selections = []
        
        # Check all possible sources of error selections
        if hasattr(self, '_error_selections') and self._error_selections:
            error_selections.extend(self._error_selections)
        if hasattr(self, '_stored_error_selections') and self._stored_error_selections:
            error_selections.extend(self._stored_error_selections)
        if hasattr(self, '_all_error_selections') and self._all_error_selections:
            error_selections.extend(self._all_error_selections)
        
        # Also preserve existing error selections from current state
        current_selections = self.extraSelections()
        for sel in current_selections:
            underline_color = sel.format.underlineColor()
            if underline_color.isValid() and underline_color == QtGui.QColor("#ff0000"):
                if sel not in error_selections:
                    error_selections.append(sel)
        
        # Remove duplicates while preserving order
        unique_errors = []
        for sel in error_selections:
            if sel not in unique_errors:
                unique_errors.append(sel)
        
        # Start with error selections (highest priority)
        extra_selections = list(unique_errors)

        # Add current line highlight ONLY if not readonly
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor("#2d2d30").lighter(120)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        # Apply all selections with error selections taking priority
        self.setExtraSelections(extra_selections)
        
        # Re-store error selections to ensure they persist
        if unique_errors:
            self._error_selections = list(unique_errors)
            self._stored_error_selections = list(unique_errors)

    def keyPressEvent(self, event):
        """Handle key press events for editor functionality and auto-suggestions."""
        # Handle Ctrl+F for find
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_F:
            self._show_find_dialog()
            return
            
        # Handle Ctrl+Space for manual completion
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Space:
            self._trigger_auto_complete()
            return
            
        # Handle completion popup navigation
        if hasattr(self, '_completion_popup') and self._completion_popup.isVisible():
            if event.key() == QtCore.Qt.Key_Escape:
                self._completion_popup.hide()
                return
            elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                current_item = self._completion_popup.currentItem()
                if current_item:
                    self._insert_completion(current_item)
                return
            elif event.key() == QtCore.Qt.Key_Up:
                current_row = self._completion_popup.currentRow()
                if current_row > 0:
                    self._completion_popup.setCurrentRow(current_row - 1)
                return
            elif event.key() == QtCore.Qt.Key_Down:
                current_row = self._completion_popup.currentRow()
                if current_row < self._completion_popup.count() - 1:
                    self._completion_popup.setCurrentRow(current_row + 1)
                return
        
        # Handle basic editor functionality
        super().keyPressEvent(event)
        
        # Auto-suggest disabled for better typing performance
        # Re-enable with Ctrl+Space for manual completion only
        pass

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

    # Auto-suggest and AI completion methods
    def _check_auto_suggest(self):
        """Check if we should show auto-suggestions."""
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        current_word = cursor.selectedText()
        
        # Get the line content for context
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        line_content = cursor.selectedText().strip()
        
        # Trigger suggestions for Python keywords and common patterns
        if len(current_word) >= 2 or line_content.endswith(('.', '(', 'import ', 'from ')):
            self._show_auto_suggest(current_word, line_content)
    
    def _trigger_auto_complete(self):
        """Manually trigger auto-completion with Ctrl+Space."""
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        current_word = cursor.selectedText()
        
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.LineUnderCursor) 
        line_content = cursor.selectedText().strip()
        
        self._show_auto_suggest(current_word, line_content, manual=True)
    
    def _show_auto_suggest(self, current_word, line_content, manual=False):
        """Show auto-suggestion popup with context-aware suggestions."""
        suggestions = self._get_suggestions(current_word, line_content, manual)
        
        if not suggestions:
            return
            
        # Create completion popup
        if not hasattr(self, '_completion_popup'):
            self._completion_popup = QtWidgets.QListWidget()
            self._completion_popup.setWindowFlags(QtCore.Qt.WindowType.Popup)
            self._completion_popup.setStyleSheet("""
                QListWidget {
                    background: #252526;
                    color: #cccccc;
                    border: 1px solid #464647;
                    font-family: Consolas, monospace;
                    font-size: 10pt;
                    selection-background-color: #094771;
                }
                QListWidget::item {
                    padding: 4px 8px;
                    border-bottom: 1px solid #2d2d30;
                }
                QListWidget::item:hover {
                    background: #2a2d2e;
                }
            """)
            self._completion_popup.itemClicked.connect(self._insert_completion)
            self._completion_popup.itemActivated.connect(self._insert_completion)
        
        # Populate suggestions
        self._completion_popup.clear()
        for suggestion in suggestions[:10]:  # Limit to 10 items
            item = QtWidgets.QListWidgetItem(suggestion)
            item.setData(QtCore.Qt.UserRole, suggestion)
            self._completion_popup.addItem(item)
        
        # Position popup near cursor
        cursor_rect = self.cursorRect()
        popup_pos = self.mapToGlobal(cursor_rect.bottomLeft())
        self._completion_popup.move(popup_pos)
        self._completion_popup.resize(200, min(200, len(suggestions) * 25))
        self._completion_popup.show()
        self._completion_popup.setCurrentRow(0)
    
    def _get_suggestions(self, current_word, line_content, manual=False):
        """Get context-aware suggestions for auto-completion."""
        suggestions = []
        
        # Python keywords and built-ins
        python_keywords = [
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 
            'finally', 'with', 'import', 'from', 'as', 'return', 'yield', 'break', 
            'continue', 'pass', 'raise', 'assert', 'lambda', 'global', 'nonlocal',
            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'
        ]
        
        # Python built-in functions
        python_builtins = [
            'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'set',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'max', 'min', 'sum',
            'abs', 'round', 'pow', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr'
        ]
        
        # Maya/MEL specific commands (when in MEL mode)
        maya_commands = [
            'select', 'move', 'rotate', 'scale', 'duplicate', 'delete', 'ls', 'listRelatives',
            'xform', 'getAttr', 'setAttr', 'connectAttr', 'disconnectAttr', 'createNode',
            'polyCube', 'polySphere', 'polyCylinder', 'polyPlane', 'curve', 'surface'
        ]
        
        current_lower = current_word.lower()
        
        # Context-specific suggestions
        if 'import' in line_content:
            # Common Python modules
            import_suggestions = [
                'os', 'sys', 'json', 'math', 'random', 'datetime', 'collections',
                'itertools', 'functools', 'operator', 'pathlib', 'subprocess',
                'maya.cmds', 'maya.mel', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'
            ]
            suggestions.extend([s for s in import_suggestions if s.lower().startswith(current_lower)])
        
        elif line_content.endswith('.'):
            # Common method suggestions
            method_suggestions = [
                'append()', 'extend()', 'insert()', 'remove()', 'pop()', 'index()', 'count()',
                'sort()', 'reverse()', 'clear()', 'copy()', 'keys()', 'values()', 'items()',
                'get()', 'update()', 'setdefault()', 'strip()', 'split()', 'join()', 'replace()',
                'upper()', 'lower()', 'startswith()', 'endswith()', 'find()', 'format()'
            ]
            suggestions.extend([s for s in method_suggestions if s.lower().startswith(current_lower)])
        
        else:
            # General keywords and built-ins
            suggestions.extend([s for s in python_keywords if s.lower().startswith(current_lower)])
            suggestions.extend([s for s in python_builtins if s.lower().startswith(current_lower)])
            
            # Add Maya commands if it looks like Maya context
            if any(maya_word in line_content.lower() for maya_word in ['cmds', 'maya', 'mel']):
                suggestions.extend([s for s in maya_commands if s.lower().startswith(current_lower)])
        
        # Code snippets for common patterns
        if manual or len(current_word) >= 3:
            snippets = {
                'def': 'def function_name():\n    pass',
                'class': 'class ClassName:\n    def __init__(self):\n        pass',
                'if': 'if condition:\n    pass',
                'for': 'for item in iterable:\n    pass',
                'while': 'while condition:\n    pass',
                'try': 'try:\n    pass\nexcept Exception as e:\n    pass',
                'with': 'with open("file.txt", "r") as f:\n    content = f.read()',
            }
            
            for key, snippet in snippets.items():
                if key.lower().startswith(current_lower):
                    suggestions.append(f"{key} (snippet)")
        
        return sorted(list(set(suggestions)))
    
    def _insert_completion(self, item):
        """Insert the selected completion."""
        suggestion = item.data(QtCore.Qt.UserRole)
        
        # Handle snippets
        if '(snippet)' in suggestion:
            suggestion = suggestion.replace(' (snippet)', '')
            snippets = {
                'def': 'def function_name():\n    pass',
                'class': 'class ClassName:\n    def __init__(self):\n        pass',
                'if': 'if condition:\n    pass',
                'for': 'for item in iterable:\n    pass',
                'while': 'while condition:\n    pass',
                'try': 'try:\n    pass\nexcept Exception as e:\n    pass',
                'with': 'with open("file.txt", "r") as f:\n    content = f.read()',
            }
            
            if suggestion in snippets:
                # Remove current word and insert snippet
                cursor = self.textCursor()
                cursor.select(QtGui.QTextCursor.WordUnderCursor)
                cursor.removeSelectedText()
                cursor.insertText(snippets[suggestion])
        else:
            # Regular completion
            cursor = self.textCursor()
            cursor.select(QtGui.QTextCursor.WordUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(suggestion)
        
        # Hide popup
        if hasattr(self, '_completion_popup'):
            self._completion_popup.hide()

    def request_ai_completion(self):
        """Request AI completion for more complex suggestions."""
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        context = cursor.selectedText()
        self.requestAICompletion.emit(context)

    def insert_suggestion(self, suggestion):
        """Insert AI-generated suggestion."""
        cursor = self.textCursor()
        cursor.insertText(suggestion)

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