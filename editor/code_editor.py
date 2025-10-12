"""
Advanced Code Editor with VSCode-style Syntax Highlighting & Error Detection
Comprehensive Python, PySide6/Qt, and Maya support with real-time error highlighting
"""
import os, ast, sys, traceback
from PySide6 import QtCore, QtGui, QtWidgets
from .highlighter import PythonHighlighter, MELHighlighter


class _LineNumberArea(QtWidgets.QWidget):
    """Minimal line number area."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.code_editor._number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor._paint_line_numbers(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    """Advanced code editor with VSCode-style features and error detection."""

    # Signals
    errorDetected = QtCore.Signal(int, str)  # line, message
    errorsCleared = QtCore.Signal()
    lintProblemsFound = QtCore.Signal(list)  # List of problem dictionaries

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Advanced font setup with multiple fallbacks
        font = QtGui.QFont()
        font_families = ["Cascadia Code", "Fira Code", "Source Code Pro", "Consolas", "Monaco", "Courier New"]
        for family in font_families:
            font.setFamily(family)
            if QtGui.QFontDatabase.hasFamily(family):
                break
        font.setPointSize(11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # VSCode Dark+ theme styling
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: "Cascadia Code", "Fira Code", "Source Code Pro", Consolas, monospace;
                font-size: 11pt;
                selection-background-color: #264F78;
                border: none;
                line-height: 1.4;
            }
        """)
        
        # Enhanced tab settings
        fm = QtGui.QFontMetrics(font)
        self.setTabStopDistance(4 * fm.horizontalAdvance(' '))
        
        # Enable undo/redo
        self.setUndoRedoEnabled(True)
        
        # Syntax highlighting
        self.highlighter = None
        self.language = "python"  # Default language
        
        # Error tracking
        self.syntax_errors = []
        self.error_highlights = []
        
        # Real-time error checking
        self.error_timer = QtCore.QTimer()
        self.error_timer.timeout.connect(self._check_syntax_errors)
        self.error_timer.setSingleShot(True)
        
        # Connect text changed signal for real-time error checking
        self.textChanged.connect(self._on_text_changed)
        
        # Enhanced line number area
        self.line_number_area = _LineNumberArea(self)
        self.line_number_area.show()  # Ensure it's visible
        
        # Connect signals
        self.blockCountChanged.connect(self._update_number_area_width)
        self.updateRequest.connect(self._update_number_area)
        self.cursorPositionChanged.connect(self._update_number_area_width)
        
        self._update_number_area_width()
        self.line_number_area.update()  # Force initial update
        
        # Initialize syntax highlighting
        self.set_language("python")
        
    def set_language(self, language):
        """Set syntax highlighting language."""
        self.language = language.lower()
        
        if self.highlighter:
            self.highlighter.setDocument(None)
            
        if self.language == "python":
            self.highlighter = PythonHighlighter(self.document())
        elif self.language == "mel":
            self.highlighter = MELHighlighter(self.document())
        else:
            self.highlighter = None
            
        # Trigger immediate syntax check
        self._check_syntax_errors()
        
    def _on_text_changed(self):
        """Handle text changes for real-time error checking."""
        # Debounce error checking - wait 500ms after user stops typing
        self.error_timer.stop()
        self.error_timer.start(500)
        
    def _check_syntax_errors(self):
        """Check for syntax errors and highlight them (VSCode style)."""
        if self.language != "python":
            return
            
        # Clear previous errors
        self._clear_error_highlights()
        self.syntax_errors.clear()
        
        code = self.toPlainText()
        if not code.strip():
            self.errorsCleared.emit()
            return
            
        try:
            # Multi-pass error detection
            errors = []
            
            # Pass 1: Try to compile the whole file
            try:
                compile(code, '<editor>', 'exec')
            except SyntaxError as e:
                if e.lineno:
                    errors.append({
                        'line': e.lineno,
                        'column': e.offset or 1,
                        'message': str(e.msg or 'Syntax error'),
                        'type': 'SyntaxError'
                    })
            except Exception as e:
                errors.append({
                    'line': 1,
                    'column': 1, 
                    'message': f"Compilation error: {str(e)}",
                    'type': 'CompilationError'
                })
                
            # Pass 2: Line-by-line validation to find ALL errors
            # This catches errors that compile() misses after the first error
            lines = code.splitlines()
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip empty lines and comments
                if not line_stripped or line_stripped.startswith('#'):
                    continue
                
                # Skip if we already found an error on this line
                if any(err['line'] == line_num for err in errors):
                    continue
                
                # Check for obvious syntax errors
                # Unmatched/incomplete syntax
                if line_stripped.endswith(':') and line_stripped.count(':') > 1:
                    # Multiple colons (likely incomplete statement)
                    errors.append({
                        'line': line_num,
                        'column': 1,
                        'message': 'invalid syntax',
                        'type': 'SyntaxError'
                    })
                    continue
                
                # Check for invalid standalone syntax
                invalid_starts = [';', ':', ',', ')', ']', '}']
                if any(line_stripped.startswith(c) for c in invalid_starts):
                    errors.append({
                        'line': line_num,
                        'column': 1,
                        'message': 'invalid syntax',
                        'type': 'SyntaxError'
                    })
                    continue
                
                # Try to compile individual line to catch more errors
                try:
                    # Add pass to make incomplete statements valid
                    test_code = line + "\n    pass" if line_stripped.endswith(':') else line
                    compile(test_code, f'<line {line_num}>', 'exec')
                except SyntaxError as e:
                    # Only add if not a continuation error (IndentationError from our test)
                    if not isinstance(e, IndentationError) or 'pass' not in str(e.msg):
                        errors.append({
                            'line': line_num,
                            'column': e.offset or 1,
                            'message': str(e.msg or 'invalid syntax'),
                            'type': 'SyntaxError'
                        })
                except:
                    pass
                    
            # Store and highlight errors
            self.syntax_errors = errors
            
            # Format problems for the problems window
            problems = []
            for error in errors:
                self._highlight_error_line(error['line'], error['message'])
                self.errorDetected.emit(error['line'], error['message'])
                
                # Add to problems list with proper format
                problems.append({
                    'type': 'Error',
                    'message': error['message'],
                    'line': error['line'],
                    'file': 'Current File'
                })
            
            # Emit all problems at once for the problems window
            self.lintProblemsFound.emit(problems)
                
            if not errors:
                self.errorsCleared.emit()
                self.lintProblemsFound.emit([])  # Clear problems window
                
        except Exception as e:
            print(f"Error in syntax checking: {e}")
            
    def _check_line_syntax_issues(self, line, line_num, existing_errors):
        """Check for line-specific syntax issues."""
        line_stripped = line.strip()
        
        # Skip if this line already has an error
        if any(err['line'] == line_num for err in existing_errors):
            return True
            
        # Common syntax issues VSCode catches
        issues = []
        
        # Skip lines with triple quotes - they're handled by compile() and AST
        if '"""' in line or "'''" in line:
            return False
        
        # Skip comment lines for quote checking
        if line_stripped.startswith('#'):
            return False
        
        # Unclosed brackets/parentheses (simple check)
        open_chars = {'(': ')', '[': ']', '{': '}'}
        stack = []
        in_string = False
        string_char = None
        
        for i, char in enumerate(line):
            # Handle string contexts
            if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            # Only check brackets outside of strings
            if not in_string:
                if char in open_chars:
                    stack.append((char, i))
                elif char in open_chars.values():
                    if not stack:
                        issues.append(f"Unexpected closing '{char}'")
                    else:
                        expected = open_chars[stack[-1][0]]
                        if char == expected:
                            stack.pop()
                        else:
                            issues.append(f"Mismatched brackets: expected '{expected}', got '{char}'")
            
        # Don't check for unterminated quotes - too many false positives with multi-line strings
        # Let compile() and AST handle string errors properly
            
        # Invalid indentation patterns
        if line.startswith(' ') and line.startswith('\t'):
            issues.append("Mixed tabs and spaces in indentation")
            
        # Common keyword issues
        if line_stripped.endswith(':') and not any(kw in line_stripped for kw in 
            ['if', 'elif', 'else', 'for', 'while', 'def', 'class', 'try', 'except', 'finally', 'with']):
            if '=' not in line_stripped:  # Not a dictionary
                issues.append("Invalid use of colon")
                
        # Add issues to existing errors
        for issue in issues:
            existing_errors.append({
                'line': line_num,
                'column': 1,
                'message': issue,
                'type': 'SyntaxWarning'
            })
            
        return len(issues) > 0
        
    def _highlight_error_line(self, line_num, message):
        """Highlight error line with VSCode-style red underline."""
        # Get the block for the error line
        block = self.document().findBlockByLineNumber(line_num - 1)
        if not block.isValid():
            return
            
        # Create format for error highlighting
        error_format = QtGui.QTextCharFormat()
        error_format.setUnderlineStyle(QtGui.QTextCharFormat.UnderlineStyle.WaveUnderline)
        error_format.setUnderlineColor(QtGui.QColor("#ff0000"))  # Red wavy underline
        error_format.setToolTip(f"Line {line_num}: {message}")
        
        # Apply formatting to the entire line
        cursor = QtGui.QTextCursor(block)
        cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
        
        # Store the highlight for later removal
        self.error_highlights.append((cursor, error_format))
        
        # Apply the format
        cursor.mergeCharFormat(error_format)
        
    def _clear_error_highlights(self):
        """Clear all error highlights."""
        # Remove previous error formatting
        for cursor, _ in self.error_highlights:
            # Reset format
            normal_format = QtGui.QTextCharFormat()
            cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
            cursor.setCharFormat(normal_format)
            
        self.error_highlights.clear()
        
    def get_syntax_errors(self):
        """Get current syntax errors."""
        return self.syntax_errors.copy()
        
    def clear_syntax_errors(self):
        """Clear syntax error highlights."""
        self._clear_error_highlights()
        self.syntax_errors.clear()
        self.errorsCleared.emit()
        
    def _number_area_width(self):
        """Calculate line number area width."""
        digits = len(str(max(1, self.blockCount())))
        # Ensure minimum width of 50 pixels for visibility
        width = 15 + self.fontMetrics().horizontalAdvance('9') * max(digits, 3)
        return max(width, 50)
        
    def _update_number_area_width(self):
        """Update line number area width."""
        self.setViewportMargins(self._number_area_width(), 0, 0, 0)
        
    def _update_number_area(self, rect, dy):
        """Update line number area."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                       self.line_number_area.width(), 
                                       rect.height())
            
        if rect.contains(self.viewport().rect()):
            self._update_number_area_width()
            
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QtCore.QRect(cr.left(), cr.top(), 
                        self._number_area_width(), cr.height())
        )
        
    def _paint_line_numbers(self, event):
        """Paint line numbers with VSCode-style error indicators."""
        painter = QtGui.QPainter(self.line_number_area)
        # Use slightly lighter background than editor for visibility
        painter.fillRect(event.rect(), QtGui.QColor(37, 37, 38))
        
        # Draw right border
        painter.setPen(QtGui.QColor(45, 45, 45))
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        # Setup fonts and colors
        font = QtGui.QFont("Consolas", 9)
        painter.setFont(font)
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_number = block_number + 1
                number = str(line_number)
                
                # Check if this line has an error
                has_error = any(error['line'] == line_number for error in self.syntax_errors)
                
                if has_error:
                    # Draw error indicator (red background)
                    error_rect = QtCore.QRect(0, top, self.line_number_area.width(), 
                                            self.fontMetrics().height())
                    painter.fillRect(error_rect, QtGui.QColor(80, 20, 20, 100))
                    painter.setPen(QtGui.QColor(255, 100, 100))  # Light red text
                    
                    # Draw error icon (small circle)
                    icon_rect = QtCore.QRect(2, top + 2, 8, 8)
                    painter.fillRect(icon_rect, QtGui.QColor(255, 0, 0))
                else:
                    painter.setPen(QtGui.QColor(100, 100, 100))  # Normal gray
                
                # Draw line number
                text_rect = QtCore.QRect(12, top, self.line_number_area.width() - 17, 
                                       self.fontMetrics().height())
                painter.drawText(text_rect, QtCore.Qt.AlignRight, number)
                               
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
            
    def keyPressEvent(self, event):
        """Enhanced key press handling with smart indentation and auto-completion."""
        cursor = self.textCursor()
        
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            # Smart auto-indentation
            current_line = cursor.block().text()
            indent = ""
            
            # Get current indentation
            for char in current_line:
                if char in (' ', '\t'):
                    indent += char
                else:
                    break
                    
            # Smart indentation rules for Python
            line_stripped = current_line.strip()
            if line_stripped.endswith(':'):
                # Increase indent after colon
                indent += "    "
            elif line_stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                # Decrease indent after control statements (next line)
                if len(indent) >= 4:
                    indent = indent[:-4]
            elif line_stripped in ('else:', 'elif', 'except:', 'finally:'):
                # Same level as corresponding if/try
                if len(indent) >= 4:
                    indent = indent[:-4]
                    
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            
        elif event.key() == QtCore.Qt.Key_Tab:
            # Smart tab handling
            if cursor.hasSelection():
                # Indent selection
                self._indent_selection(True)
            else:
                # Insert 4 spaces or align to next tab stop
                super().keyPressEvent(event)
                
        elif event.key() == QtCore.Qt.Key_Backtab:
            # Shift+Tab - unindent
            if cursor.hasSelection():
                self._indent_selection(False)
            else:
                # Remove indentation
                current_line = cursor.block().text()
                pos = cursor.positionInBlock()
                if pos > 0 and current_line[pos-1] == ' ':
                    # Remove up to 4 spaces
                    remove_count = min(4, pos)
                    for i in range(remove_count):
                        if pos > 0 and current_line[pos-1] == ' ':
                            cursor.deletePreviousChar()
                            pos -= 1
                        else:
                            break
                            
        elif event.key() == QtCore.Qt.Key_BraceLeft:
            # Auto-close braces
            super().keyPressEvent(event)
            if self._should_auto_close():
                cursor.insertText("}")
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left)
                self.setTextCursor(cursor)
                
        elif event.key() == QtCore.Qt.Key_ParenLeft:
            # Auto-close parentheses
            super().keyPressEvent(event)
            if self._should_auto_close():
                cursor.insertText(")")
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left)
                self.setTextCursor(cursor)
                
        elif event.key() == QtCore.Qt.Key_BracketLeft:
            # Auto-close square brackets
            super().keyPressEvent(event)
            if self._should_auto_close():
                cursor.insertText("]")
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left)
                self.setTextCursor(cursor)
                
        elif event.key() == QtCore.Qt.Key_QuoteDbl:
            # Auto-close double quotes
            super().keyPressEvent(event)
            if self._should_auto_close():
                cursor.insertText('"')
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left)
                self.setTextCursor(cursor)
                
        else:
            super().keyPressEvent(event)
            
    def _indent_selection(self, increase=True):
        """Indent or unindent selected text."""
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # Select full lines
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
        start_line = cursor.position()
        
        cursor.setPosition(end)
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.EndOfLine)
        end_line = cursor.position()
        
        cursor.setPosition(start_line)
        cursor.setPosition(end_line, QtGui.QTextCursor.MoveMode.KeepAnchor)
        
        # Get selected text
        text = cursor.selectedText()
        lines = text.split('\u2029')  # Qt paragraph separator
        
        # Indent/unindent each line
        new_lines = []
        for line in lines:
            if increase:
                new_lines.append("    " + line)
            else:
                # Remove up to 4 leading spaces
                if line.startswith("    "):
                    new_lines.append(line[4:])
                elif line.startswith("   "):
                    new_lines.append(line[3:])
                elif line.startswith("  "):
                    new_lines.append(line[2:])
                elif line.startswith(" "):
                    new_lines.append(line[1:])
                else:
                    new_lines.append(line)
                    
        # Replace text
        cursor.insertText('\u2029'.join(new_lines))
        
    def _should_auto_close(self):
        """Check if we should auto-close brackets/quotes."""
        cursor = self.textCursor()
        # Don't auto-close if we're inside a string or comment
        # This is a simplified check - could be enhanced
        return True  # For now, always auto-close
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        super().mousePressEvent(event)
        
        # Clear error highlights when user clicks (optional)
        # This gives immediate feedback that user acknowledged the error
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pass  # Keep errors visible for now