"""
GitHub Copilot-style Inline Diff System
Shows red highlight on error + floating widget with suggestion
"""
from PySide6 import QtCore, QtGui, QtWidgets


class SuggestionWidget(QtWidgets.QWidget):
    """Floating widget showing suggestion code with Keep/Reject buttons."""
    
    keep_clicked = QtCore.Signal()
    reject_clicked = QtCore.Signal()
    
    def __init__(self, parent, suggestion_text):
        super().__init__(parent)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Suggestion code label with solid background
        self.code_label = QtWidgets.QLabel(suggestion_text)
        self.code_label.setFont(QtGui.QFont("Consolas", 10))
        self.code_label.setStyleSheet("""
            QLabel {
                background-color: #1e3a1e;
                color: #90EE90;
                padding: 6px 10px;
                border-left: 3px solid #00ff00;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.code_label)
        
        # Keep button (just checkmark icon)
        keep_btn = QtWidgets.QPushButton("✓")
        keep_btn.setFixedSize(28, 28)
        keep_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #34d058; }
        """)
        keep_btn.clicked.connect(self.keep_clicked.emit)
        layout.addWidget(keep_btn)
        
        # Reject button (just X icon)
        reject_btn = QtWidgets.QPushButton("✗")
        reject_btn.setFixedSize(28, 28)
        reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        reject_btn.clicked.connect(self.reject_clicked.emit)
        layout.addWidget(reject_btn)
        
        self.setStyleSheet("""
            SuggestionWidget {
                background-color: #2d2d2d;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """)
        
        # Initially hidden - will show on hover
        self.hide()


class FloatingButtonWidget(QtWidgets.QWidget):
    """Floating Keep/Reject buttons at bottom-right of editor"""
    
    keep_clicked = QtCore.Signal()
    reject_clicked = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Keep button
        self.keep_btn = QtWidgets.QPushButton(" Keep")
        self.keep_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.keep_btn.clicked.connect(self.keep_clicked.emit)
        layout.addWidget(self.keep_btn)
        
        # Reject button
        self.reject_btn = QtWidgets.QPushButton(" Reject")
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.reject_btn.clicked.connect(self.reject_clicked.emit)
        layout.addWidget(self.reject_btn)
        
        # Shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 100))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class CopilotInlineDiff(QtCore.QObject):
    """Manages inline diff with red highlight + hover-to-show suggestion widget."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.active = False
        self.active_diffs = []
        self.suggestion_widget = None  # Floating widget for suggestion
        self.original_resize = self.editor.resizeEvent
        self.editor.resizeEvent = self._editor_resized
        
        # Install event filter to detect mouse hover
        self.editor.viewport().installEventFilter(self)
        self.editor.viewport().setMouseTracking(True)
    
    def show_diff(self, line_number, old_code, new_code):
        """Show inline diff: red highlight on error line + floating widget with suggestion."""
        # Store diff info
        diff_info = {
            'old_line_num': line_number,
            'new_line_num': line_number,  # Same line - no insertion!
            'old_code': old_code,
            'new_code': new_code
        }
        self.active_diffs.append(diff_info)
        self.active = True
        
        # Apply red highlight to error line via highlighter
        self._apply_all_colors()
        
        # Create floating suggestion widget (but keep it hidden until hover)
        if self.suggestion_widget:
            self.suggestion_widget.deleteLater()
        
        self.suggestion_widget = SuggestionWidget(self.editor, new_code)
        self.suggestion_widget.keep_clicked.connect(lambda: self._on_keep(diff_info))
        self.suggestion_widget.reject_clicked.connect(self._on_reject)
        self.suggestion_widget.adjustSize()
        # Widget will be positioned dynamically on hover
        
        # Center view on the diff
        scroll_cursor = self.editor.textCursor()
        scroll_cursor.movePosition(QtGui.QTextCursor.Start)
        for _ in range(line_number):
            scroll_cursor.movePosition(QtGui.QTextCursor.NextBlock)
        self.editor.setTextCursor(scroll_cursor)
        self.editor.centerCursor()
    
    def _apply_all_colors(self):
        """Apply red background by informing the highlighter (preserves syntax colors!)"""
        if not self.active:
            return
        
        # Tell the highlighter which line needs red background
        if hasattr(self.editor, 'highlighter') and self.editor.highlighter:
            error_lines = []
            for diff_info in self.active_diffs:
                line_num = diff_info['old_line_num'] + 1  # Highlighter uses 1-indexed
                error_lines.append(line_num)
            
            # Set the red highlight lines
            if hasattr(self.editor.highlighter, 'set_copilot_error_lines'):
                self.editor.highlighter.set_copilot_error_lines(error_lines)
            
            # Force re-highlight to apply changes
            self.editor.highlighter.rehighlight()
    
    def _on_keep(self, diff_info):
        """User clicked Keep - replace error line with suggestion."""
        # Replace the error line with suggestion
        cursor = self.editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        for _ in range(diff_info['old_line_num']):
            cursor.movePosition(QtGui.QTextCursor.NextBlock)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        
        # Get indentation
        existing_line = cursor.selectedText()
        indentation = existing_line[:len(existing_line) - len(existing_line.lstrip())]
        
        # Replace
        cursor.beginEditBlock()
        cursor.insertText(indentation + diff_info['new_code'].lstrip())
        cursor.endEditBlock()
        
        self._clear_all()
    
    def _on_reject(self):
        """User clicked Reject - just clear the diff."""
        self._clear_all()
    
    def eventFilter(self, obj, event):
        """Detect mouse hover over red error line to show/hide suggestion widget."""
        if not self.active or not self.suggestion_widget:
            return False
        
        if event.type() == QtCore.QEvent.MouseMove:
            # Get cursor position under mouse
            cursor = self.editor.cursorForPosition(event.pos())
            line_number = cursor.blockNumber()
            
            # Check if hovering over any error line
            is_over_error = any(diff['old_line_num'] == line_number for diff in self.active_diffs)
            
            if is_over_error:
                # Position widget directly below the hovered error line
                cursor_at_line = self.editor.textCursor()
                cursor_at_line.movePosition(QtGui.QTextCursor.Start)
                for _ in range(line_number):
                    cursor_at_line.movePosition(QtGui.QTextCursor.NextBlock)
                
                # Move to end of line to get the bottom position
                cursor_at_line.movePosition(QtGui.QTextCursor.EndOfBlock)
                rect = self.editor.cursorRect(cursor_at_line)
                
                # Position widget right below the line with minimal padding
                widget_x = 10
                widget_y = rect.bottom() + 1  # Just 1 pixel below
                self.suggestion_widget.move(widget_x, widget_y)
                
                if not self.suggestion_widget.isVisible():
                    self.suggestion_widget.show()
                    self.suggestion_widget.raise_()
            else:
                if self.suggestion_widget.isVisible():
                    self.suggestion_widget.hide()
        
        return False
    
    def _clear_all(self):
        """Clear all diff state"""
        self.active = False
        self.active_diffs.clear()
        
        # Clear highlighter's Copilot error lines
        if hasattr(self.editor, 'highlighter') and self.editor.highlighter:
            if hasattr(self.editor.highlighter, 'clear_copilot_error_lines'):
                self.editor.highlighter.clear_copilot_error_lines()
                self.editor.highlighter.rehighlight()
        
        # Hide suggestion widget
        if self.suggestion_widget:
            self.suggestion_widget.deleteLater()
            self.suggestion_widget = None
        
        # Clear inline diff selections using the editor's method
        if hasattr(self.editor, 'apply_inline_diff_highlighting'):
            self.editor.apply_inline_diff_highlighting([])
        else:
            self.editor.setExtraSelections([])
    
    def _editor_resized(self, event):
        """Handle editor resize event"""
        if self.original_resize:
            self.original_resize(event)
