"""
Inline diff system with floating suggestion widget overlay.
Displays error in red, suggestion in floating green widget below.
"""
from PySide6 import QtCore, QtGui, QtWidgets


class SuggestionWidget(QtWidgets.QWidget):
    """Floating widget that displays the suggestion code below the error line."""
    
    keep_clicked = QtCore.Signal()
    reject_clicked = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make it float on top of parent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        self.setAutoFillBackground(True)
        
        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)
        
        # Code display with green background
        self.code_label = QtWidgets.QLabel()
        self.code_label.setFont(QtGui.QFont("Consolas", 10))
        self.code_label.setTextFormat(QtCore.Qt.PlainText)
        self.code_label.setWordWrap(False)
        self.code_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 255, 0, 30);
                color: #D4D4D4;
                padding: 4px 8px;
                border-left: 3px solid #00ff00;
            }
        """)
        main_layout.addWidget(self.code_label)
        
        # Button container
        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        
        # Keep button
        self.keep_btn = QtWidgets.QPushButton("✓ Keep")
        self.keep_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34d058;
            }
        """)
        self.keep_btn.clicked.connect(self.keep_clicked.emit)
        button_layout.addWidget(self.keep_btn)
        
        # Reject button
        self.reject_btn = QtWidgets.QPushButton("✗ Reject")
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        self.reject_btn.clicked.connect(self.reject_clicked.emit)
        button_layout.addWidget(self.reject_btn)
        
        button_layout.addStretch()
        main_layout.addWidget(button_container)
        
        # Dark theme styling
        self.setStyleSheet("""
            SuggestionWidget {
                background-color: #1e1e1e;
                border: 1px solid #00ff00;
                border-radius: 4px;
            }
        """)
    
    def set_code(self, code_text):
        """Set the suggestion code to display."""
        self.code_label.setText(code_text)


class CopilotInlineDiffOverlay:
    """Manages inline diff with floating overlay widget for suggestions."""
    
    def __init__(self, code_editor):
        self.editor = code_editor
        self.diff_info = None
        self.suggestion_widget = None
        
        print("[OVERLAY] CopilotInlineDiffOverlay initialized")
    
    def show_diff(self, line_number, old_code, new_code):
        """Show inline diff: red background on error line, floating widget with suggestion below."""
        print(f"\n[OVERLAY] 📊 show_diff() called:")
        print(f"   Line: {line_number}")
        print(f"   Old: {old_code[:50]}")
        print(f"   New: {new_code[:50]}")
        
        # Store diff information
        self.diff_info = {
            'line_number': line_number,
            'old_code': old_code,
            'new_code': new_code
        }
        
        # 1. Highlight the ERROR line in RED
        self._apply_error_highlight(line_number)
        
        # 2. Create floating widget with suggestion BELOW the error line
        self._create_suggestion_widget(line_number, new_code)
        
        print(f"[OVERLAY] ✅ Diff displayed: red error + floating green suggestion")
    
    def _apply_error_highlight(self, line_number):
        """Apply red background to the error line."""
        print(f"[OVERLAY] Applying RED highlight to line {line_number}")
        
        cursor = QtGui.QTextCursor(self.editor.document())
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, line_number)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        
        # Create red selection
        red_selection = QtWidgets.QTextEdit.ExtraSelection()
        red_selection.cursor = cursor
        red_selection.format.setBackground(QtGui.QColor(255, 0, 0, 30))  # Subtle red
        red_selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
        
        # Apply via editor's selection management
        self.editor.apply_inline_diff_highlighting([red_selection])
    
    def _create_suggestion_widget(self, error_line_number, suggestion_code):
        """Create floating widget showing suggestion below error line."""
        print(f"[OVERLAY] Creating floating suggestion widget below line {error_line_number}")
        
        # Remove old widget if exists
        if self.suggestion_widget:
            self.suggestion_widget.deleteLater()
            self.suggestion_widget = None
        
        # Create new suggestion widget
        self.suggestion_widget = SuggestionWidget(self.editor)
        self.suggestion_widget.set_code(suggestion_code)
        
        # Connect buttons
        self.suggestion_widget.keep_clicked.connect(self._on_keep)
        self.suggestion_widget.reject_clicked.connect(self._on_reject)
        
        # CRITICAL: Position widget BEFORE showing it
        self._position_widget_below_line(error_line_number)
        
        # Show widget and raise it to top
        self.suggestion_widget.show()
        self.suggestion_widget.raise_()
        self.suggestion_widget.setVisible(True)  # Force visible
        
        print(f"[OVERLAY] ✅ Suggestion widget created, positioned, and made visible")
        print(f"[OVERLAY] Widget geometry: {self.suggestion_widget.geometry()}")
        print(f"[OVERLAY] Widget visible: {self.suggestion_widget.isVisible()}")
    
    def _position_widget_below_line(self, line_number):
        """Position the suggestion widget directly below the specified line."""
        # Get cursor for the error line
        cursor = QtGui.QTextCursor(self.editor.document())
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, line_number)
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock)
        
        # Get rectangle of cursor position (end of error line)
        rect = self.editor.cursorRect(cursor)
        
        # Position widget below the line in EDITOR coordinates (not global)
        widget_x = 10  # Left margin
        widget_y = rect.bottom() + 2   # Just below the line
        
        print(f"[OVERLAY] Positioning widget at editor coords: ({widget_x}, {widget_y})")
        print(f"[OVERLAY] Cursor rect: {rect}, bottom: {rect.bottom()}")
        
        self.suggestion_widget.move(widget_x, widget_y)
        
        # Resize widget to fit content
        self.suggestion_widget.adjustSize()
        
        # Ensure widget width doesn't exceed editor width
        max_width = self.editor.width() - 20
        if self.suggestion_widget.width() > max_width:
            self.suggestion_widget.setFixedWidth(max_width)
        
        print(f"[OVERLAY] Widget size: {self.suggestion_widget.size()}, visible: {self.suggestion_widget.isVisible()}")
    
    def _on_keep(self):
        """User clicked Keep - replace error line with suggestion."""
        print(f"\n[OVERLAY] ✓ Keep clicked")
        
        if not self.diff_info:
            return
        
        line_number = self.diff_info['line_number']
        new_code = self.diff_info['new_code']
        
        # Replace the error line with suggestion
        cursor = QtGui.QTextCursor(self.editor.document())
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, line_number)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        
        # Get indentation from original line
        existing_line = cursor.selectedText()
        indentation = existing_line[:len(existing_line) - len(existing_line.lstrip())]
        
        # Replace with new code
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(indentation + new_code.lstrip())
        cursor.endEditBlock()
        
        print(f"[OVERLAY] Line {line_number} replaced with suggestion")
        
        # Clear diff
        self.clear_diff()
    
    def _on_reject(self):
        """User clicked Reject - just remove the diff display."""
        print(f"\n[OVERLAY] ✗ Reject clicked")
        self.clear_diff()
    
    def clear_diff(self):
        """Clear all diff highlighting and widgets."""
        print(f"[OVERLAY] Clearing diff display")
        
        # Remove red highlighting
        self.editor.apply_inline_diff_highlighting([])
        
        # Remove suggestion widget
        if self.suggestion_widget:
            self.suggestion_widget.deleteLater()
            self.suggestion_widget = None
        
        # Clear diff info
        self.diff_info = None
        
        print(f"[OVERLAY] ✅ Diff cleared")
    
    def update_widget_position(self):
        """Update widget position (call when editor scrolls/resizes)."""
        if self.suggestion_widget and self.diff_info:
            self._position_widget_below_line(self.diff_info['line_number'])
