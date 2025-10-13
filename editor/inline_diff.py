"""
VSCode-style Inline Diff Widget
Shows code replacements directly in the editor with Accept/Reject buttons
"""
from PySide6 import QtCore, QtGui, QtWidgets
import difflib


class InlineDiffWidget(QtWidgets.QWidget):
    """Inline diff widget that appears in the editor"""
    
    accepted = QtCore.Signal()
    rejected = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header with buttons
        headerLayout = QtWidgets.QHBoxLayout()
        
        # Info label
        self.infoLabel = QtWidgets.QLabel("💡 Morpheus suggests a fix")
        self.infoLabel.setStyleSheet("""
            QLabel {
                color: #d4d4d4;
                font-size: 12px;
                font-weight: 600;
                padding: 4px;
            }
        """)
        headerLayout.addWidget(self.infoLabel)
        headerLayout.addStretch()
        
        # Accept button
        acceptBtn = QtWidgets.QPushButton("✓ Keep")
        acceptBtn.setStyleSheet("""
            QPushButton {
                background: #238636;
                border: none;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #2ea043;
            }
        """)
        acceptBtn.clicked.connect(self.accepted.emit)
        acceptBtn.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Reject button
        rejectBtn = QtWidgets.QPushButton("✗ Reject")
        rejectBtn.setStyleSheet("""
            QPushButton {
                background: #21262d;
                border: 1px solid #30363d;
                color: #d4d4d4;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #30363d;
            }
        """)
        rejectBtn.clicked.connect(self.rejected.emit)
        rejectBtn.setCursor(QtCore.Qt.PointingHandCursor)
        
        headerLayout.addWidget(acceptBtn)
        headerLayout.addWidget(rejectBtn)
        layout.addLayout(headerLayout)
        
        # Diff display area
        self.diffText = QtWidgets.QTextEdit()
        self.diffText.setReadOnly(True)
        self.diffText.setMaximumHeight(200)
        self.diffText.setStyleSheet("""
            QTextEdit {
                background: #1e1e1e;
                border: 1px solid #30363d;
                border-radius: 4px;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.diffText)
        
        # Style the widget
        self.setStyleSheet("""
            InlineDiffWidget {
                background: #252526;
                border: 2px solid #00ff41;
                border-radius: 6px;
            }
        """)
    
    def setDiffContent(self, old_lines, new_lines):
        """Set the diff content with color coding"""
        html_parts = []
        
        # Show removed lines (red)
        if old_lines:
            html_parts.append('<div style="background: #3f1f1f; padding: 4px; margin-bottom: 4px; border-left: 3px solid #f85149;">')
            for line in old_lines:
                escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_parts.append(f'<span style="color: #f85149;">- {escaped}</span><br>')
            html_parts.append('</div>')
        
        # Show added lines (green)
        if new_lines:
            html_parts.append('<div style="background: #1f3f1f; padding: 4px; border-left: 3px solid #3fb950;">')
            for line in new_lines:
                escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html_parts.append(f'<span style="color: #3fb950;">+ {escaped}</span><br>')
            html_parts.append('</div>')
        
        self.diffText.setHtml(''.join(html_parts))


class InlineDiffManager:
    """Manages inline diff overlays in the code editor"""
    
    def __init__(self, editor):
        self.editor = editor
        self.current_diff = None
        self.replacement_info = None
        self.new_code = None
        
    def show_inline_diff(self, replacement_info, new_code):
        """Show inline diff at the specified line range"""
        # Remove existing diff if any
        self.clear_diff()
        
        # Store the replacement data
        self.replacement_info = replacement_info
        self.new_code = new_code
        
        # Create the diff widget
        self.current_diff = InlineDiffWidget(self.editor)
        self.current_diff.accepted.connect(self._apply_replacement)
        self.current_diff.rejected.connect(self.clear_diff)
        
        # Set diff content
        old_lines = replacement_info['old_code'].split('\n')
        new_lines = new_code.split('\n')
        self.current_diff.setDiffContent(old_lines, new_lines)
        
        # Highlight the affected lines in the editor
        self._highlight_affected_lines(replacement_info['start_line'], replacement_info['end_line'])
        
        # Position the widget in the editor
        self._position_widget(replacement_info['start_line'])
        
        self.current_diff.show()
        
    def _highlight_affected_lines(self, start_line, end_line):
        """Highlight lines that will be replaced with red background"""
        from PySide6.QtWidgets import QTextEdit
        
        cursor = self.editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        
        # Move to start line
        for _ in range(start_line):
            cursor.movePosition(QtGui.QTextCursor.Down)
        
        # Select the range
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        for _ in range(end_line - start_line):
            cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.KeepAnchor)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor)
        
        # Apply red background highlight
        fmt = QtGui.QTextCharFormat()
        fmt.setBackground(QtGui.QColor(63, 31, 31, 100))  # Semi-transparent red
        
        # Store the original selection to restore later
        self.original_selection = cursor
        
        # Create extra selection for highlighting using QTextEdit.ExtraSelection
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.cursor = cursor
        extra_selection.format = fmt
        
        # Apply it - get current selections and add ours
        selections = list(self.editor.extraSelections())
        selections.append(extra_selection)
        self.editor.setExtraSelections(selections)
        
    def _position_widget(self, line_number):
        """Position the diff widget above the affected line"""
        # Get the cursor at the line
        cursor = self.editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        for _ in range(line_number):
            cursor.movePosition(QtGui.QTextCursor.Down)
        
        # Get rectangle of the cursor position
        rect = self.editor.cursorRect(cursor)
        
        # Position the widget
        widget_width = min(600, self.editor.width() - 40)
        self.current_diff.setFixedWidth(widget_width)
        
        # Position above the line
        x = 20
        y = max(10, rect.top() - self.current_diff.sizeHint().height() - 10)
        
        self.current_diff.move(x, y)
        
    def _apply_replacement(self):
        """Apply the code replacement"""
        if not self.replacement_info or not self.new_code:
            return
        
        try:
            current_text = self.editor.toPlainText()
            lines = current_text.split('\n')
            
            # Replace the section
            new_lines = (
                lines[:self.replacement_info['start_line']] +
                self.new_code.split('\n') +
                lines[self.replacement_info['end_line']:]
            )
            
            # Apply to editor
            self.editor.setPlainText('\n'.join(new_lines))
            
            # Move cursor to the replaced section
            cursor = self.editor.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            for _ in range(self.replacement_info['start_line']):
                cursor.movePosition(QtGui.QTextCursor.Down)
            self.editor.setTextCursor(cursor)
            
            # Notify success
            print(f"✅ Replaced lines {self.replacement_info['start_line']+1}-{self.replacement_info['end_line']}")
            
        except Exception as e:
            print(f"Failed to apply replacement: {e}")
        finally:
            self.clear_diff()
    
    def clear_diff(self):
        """Remove the inline diff widget and highlighting"""
        if self.current_diff:
            self.current_diff.deleteLater()
            self.current_diff = None
        
        # Clear highlighting
        self.editor.setExtraSelections([])
        
        self.replacement_info = None
        self.new_code = None
