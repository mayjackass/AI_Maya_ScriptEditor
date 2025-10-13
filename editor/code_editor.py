"""
Advanced Code Editor with VSCode-style Syntax Highlighting & Error Detection
Comprehensive Python, PySide6/Qt, and Maya support with real-time error highlighting
"""
import os, ast, sys, traceback
from PySide6 import QtCore, QtGui, QtWidgets
from .highlighter import PythonHighlighter, MELHighlighter


class _LineNumberArea(QtWidgets.QWidget):
    """Minimal line number area with fold indicators."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.setMouseTracking(True)  # Enable hover detection

    def sizeHint(self):
        return QtCore.QSize(self.code_editor._number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor._paint_line_numbers(event)
    
    def mousePressEvent(self, event):
        """Handle clicks on fold indicators."""
        if event.button() == QtCore.Qt.LeftButton:
            # Calculate which line was clicked
            block = self.code_editor.firstVisibleBlock()
            top = int(self.code_editor.blockBoundingGeometry(block).translated(
                self.code_editor.contentOffset()).top())
            
            while block.isValid():
                bottom = top + int(self.code_editor.blockBoundingRect(block).height())
                
                if event.pos().y() >= top and event.pos().y() <= bottom:
                    # Check if click is in fold indicator area (leftmost 12 pixels)
                    if event.pos().x() <= 12:
                        line_number = block.blockNumber() + 1
                        self.code_editor.toggle_fold(line_number)
                        break
                
                block = block.next()
                top = bottom


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
        
        # Code folding state
        self.folded_blocks = set()  # Set of line numbers that are folded
        
        # Paint optimization for indentation guides
        self._skip_paint_count = 0
        self._cached_char_width = None
        
        # Real-time error checking
        self.error_timer = QtCore.QTimer()
        self.error_timer.timeout.connect(self._check_syntax_errors)
        self.error_timer.setSingleShot(True)
        
        # Connect text changed signal for real-time error checking
        self.textChanged.connect(self._on_text_changed)
        
        # Autocomplete setup
        self.completer = None
        self._setup_autocomplete()
        
        # Inline diff manager for VSCode-style code replacements
        from .inline_diff import InlineDiffManager
        self.inline_diff_manager = InlineDiffManager(self)
        
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
            # Pass error lines to highlighter
            if hasattr(self, 'syntax_errors'):
                error_lines = {e['line'] for e in self.syntax_errors}
                self.highlighter.set_error_lines(error_lines)
        elif self.language == "mel":
            self.highlighter = MELHighlighter(self.document())
        else:
            self.highlighter = None
            
        # Trigger immediate syntax check
        self._check_syntax_errors()
    
    def get_language(self):
        """Get current language setting."""
        return self.language
    
    def _setup_autocomplete(self):
        """Setup autocomplete with Python/MEL keywords and common functions."""
        # Python keywords and built-ins
        python_completions = [
            # Keywords
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield',
            # Common built-in functions
            'print', 'input', 'len', 'range', 'str', 'int', 'float', 'list',
            'dict', 'set', 'tuple', 'bool', 'type', 'isinstance', 'issubclass',
            'open', 'read', 'write', 'close', 'enumerate', 'zip', 'map', 'filter',
            'sorted', 'reversed', 'sum', 'min', 'max', 'abs', 'round', 'pow',
            'all', 'any', 'dir', 'help', 'vars', 'locals', 'globals',
            # Common modules
            'os', 'sys', 'math', 'random', 'datetime', 'json', 'csv', 're',
            'collections', 'itertools', 'functools', 'pathlib', 'argparse',
            # PySide6/Qt
            'QtCore', 'QtGui', 'QtWidgets', 'QApplication', 'QWidget', 'QMainWindow',
            'QPushButton', 'QLabel', 'QLineEdit', 'QTextEdit', 'QVBoxLayout', 'QHBoxLayout',
            # Maya commands (if available)
            'cmds', 'mel', 'pm', 'pymel', 'polySphere', 'polyCube', 'select', 'ls',
            'createNode', 'setAttr', 'getAttr', 'delete', 'duplicate', 'parent',
        ]
        
        # MEL commands
        mel_completions = [
            'print', 'string', 'int', 'float', 'vector', 'matrix',
            'polySphere', 'polyCube', 'polyCylinder', 'polyPlane',
            'select', 'ls', 'delete', 'duplicate', 'parent', 'createNode',
            'setAttr', 'getAttr', 'connectAttr', 'disconnectAttr',
            'xform', 'move', 'rotate', 'scale', 'group', 'instance',
            'file', 'newFile', 'openFile', 'saveFile', 'importFile',
        ]
        
        # Create completer
        self.python_model = QtCore.QStringListModel(python_completions)
        self.mel_model = QtCore.QStringListModel(mel_completions)
        
        self.completer = QtWidgets.QCompleter(self.python_model, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self._insert_completion)
        
        # Style the popup to match VSCode dark theme
        popup = self.completer.popup()
        popup.setStyleSheet("""
            QListView {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #454545;
                selection-background-color: #094771;
                selection-color: #ffffff;
                font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
                font-size: 10pt;
                padding: 2px;
            }
            QListView::item {
                padding: 4px 8px;
                border: none;
            }
            QListView::item:hover {
                background-color: #2a2d2e;
            }
        """)
    
    def _insert_completion(self, completion):
        """Insert the selected completion."""
        cursor = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        cursor.insertText(completion[-extra:])
        self.setTextCursor(cursor)
    
    def _get_text_under_cursor(self):
        """Get the word under cursor for autocomplete."""
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()
    
    def _show_autocomplete(self):
        """Show autocomplete popup."""
        if not self.completer:
            return
        
        # Update completer model based on language
        if self.language == "python":
            self.completer.setModel(self.python_model)
        else:
            self.completer.setModel(self.mel_model)
        
        # Get word under cursor
        completion_prefix = self._get_text_under_cursor()
        
        # Only show if we have at least 1 character
        if len(completion_prefix) < 1:
            self.completer.popup().hide()
            return
        
        # Set completion prefix
        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0)
            )
        
        # Show popup at cursor position
        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(
            self.completer.popup().sizeHintForColumn(0) +
            self.completer.popup().verticalScrollBar().sizeHint().width()
        )
        self.completer.complete(cursor_rect)
        
    def _on_text_changed(self):
        """Handle text changes for real-time error checking."""
        # Debounce error checking - wait 500ms after user stops typing
        self.error_timer.stop()
        self.error_timer.start(500)
        
    def _check_syntax_errors(self):
        """Check for syntax errors and highlight them (VSCode style - multi-pass detection)."""
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
            # Multi-pass error detection like VSCode
            errors = []
            error_lines = set()
            
            # Pass 1: Iterative compile() to find MULTIPLE syntax errors
            # VSCode does this by temporarily "fixing" errors to find more
            temp_code = code
            max_attempts = 10  # Limit to prevent infinite loops
            
            for attempt in range(max_attempts):
                try:
                    compile(temp_code, '<editor>', 'exec')
                    break  # No more errors
                except SyntaxError as e:
                    if e.lineno and e.lineno not in error_lines:
                        errors.append({
                            'line': e.lineno,
                            'column': e.offset or 1,
                            'message': str(e.msg or 'Syntax error'),
                            'type': 'SyntaxError'
                        })
                        error_lines.add(e.lineno)
                        
                        # Temporarily "fix" this line to find more errors
                        temp_lines = temp_code.split('\n')
                        if 1 <= e.lineno <= len(temp_lines):
                            # Comment out the problematic line
                            temp_lines[e.lineno - 1] = f"# TEMP_FIX: {temp_lines[e.lineno - 1]}"
                            temp_code = '\n'.join(temp_lines)
                    else:
                        break  # No new errors found
                except Exception as e:
                    # Other compilation errors (rare)
                    if 1 not in error_lines:
                        errors.append({
                            'line': 1,
                            'column': 1, 
                            'message': f"Compilation error: {str(e)}",
                            'type': 'CompilationError'
                        })
                    break
            
            # Pass 2: Pattern-based detection for common missing syntax
            # Only check lines that don't already have errors
            # NOTE: Be conservative to avoid false positives
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if i in error_lines:
                    continue
                    
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('#'):
                    continue
                
                # Skip lines inside multi-line strings
                if '"""' in line or "'''" in line:
                    continue
                
                # Check for missing colons - but be more careful
                # Only flag if it's clearly a statement that needs a colon
                if (line_stripped.startswith(('if ', 'elif ', 'for ', 'while ', 'def ', 'class ')) and 
                    not line_stripped.endswith(':') and 
                    not line_stripped.endswith('\\') and
                    not line_stripped.endswith(',') and  # Continuation
                    not line_stripped.endswith(('and', 'or')) and  # Boolean continuation
                    not '(' in line_stripped.split()[-1]):  # Function call might continue
                    # Additional check: make sure it's not part of a multi-line expression
                    if i > 1:
                        prev_line = lines[i-2].rstrip() if i-2 < len(lines) else ""
                        if prev_line.endswith(('(', '[', '{', ',', '\\', 'and', 'or')):
                            continue
                    # Check if next line is a continuation (starts with 'and', 'or', or is indented more)
                    if i < len(lines):
                        next_line = lines[i].strip() if i < len(lines) else ""
                        if next_line.startswith(('and ', 'or ', 'not ')):
                            continue
                    errors.append({
                        'line': i,
                        'column': len(line_stripped),
                        'message': 'Missing colon at end of statement',
                        'type': 'SyntaxError'
                    })
                    error_lines.add(i)
                
                # Special check for 'else', 'try', 'except', 'finally' without colon
                elif (line_stripped in ('else', 'try', 'finally') or 
                      line_stripped.startswith('except ')) and not line_stripped.endswith(':'):
                    # Check if it's a continuation
                    if i < len(lines):
                        next_line = lines[i].strip() if i < len(lines) else ""
                        if next_line.startswith(('and ', 'or ')):
                            continue
                    errors.append({
                        'line': i,
                        'column': len(line_stripped),
                        'message': 'Missing colon at end of statement',
                        'type': 'SyntaxError'
                    })
                    error_lines.add(i)
                
                # Check for incomplete expressions - only at end of file or before non-indented line
                elif (line_stripped.endswith((' +', ' -', ' *', ' /', ' =', ' ==', 
                                              ' +=', ' -=', ' *=', ' /=')) and
                      not line_stripped.endswith('\\')):
                    # Check if next line exists and is properly indented (continuation)
                    if i < len(lines):
                        next_line = lines[i].strip() if i < len(lines) else ""
                        if next_line and not next_line.startswith('#'):
                            # Looks like continuation, don't flag as error
                            continue
                    errors.append({
                        'line': i,
                        'column': len(line_stripped),
                        'message': 'Incomplete expression',
                        'type': 'SyntaxError'
                    })
                    error_lines.add(i)
                
                # Check for standalone keywords - only the most obvious cases
                elif line_stripped in ('def', 'class', 'if', 'for', 'while', 'try', 
                                       'import', 'from'):
                    errors.append({
                        'line': i,
                        'column': 1,
                        'message': f'Invalid standalone keyword: {line_stripped}',
                        'type': 'SyntaxError'
                    })
                    error_lines.add(i)
                    
            # Store and highlight errors (limit to first 10 like VSCode)
            self.syntax_errors = errors[:10]
            
            # Format problems for the problems window
            problems = []
            for error in self.syntax_errors:
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
            
            # Update visual error highlighting in the editor
            self._update_error_highlighting()
                
            if not self.syntax_errors:
                self.errorsCleared.emit()
                self.lintProblemsFound.emit([])  # Clear problems window
                
        except Exception as e:
            print(f"Error in syntax checking: {e}")
            import traceback
            traceback.print_exc()
            
    def _highlight_error_line(self, line_num, message):
        """Highlight error line with VSCode-style red underline."""
        # Store error info for the highlighter
        self.error_highlights.append((line_num, message))
        
    def _clear_error_highlights(self):
        """Clear all error highlights."""
        self.error_highlights.clear()
        
    def _update_error_highlighting(self):
        """Update the syntax highlighter with current error details."""
        if self.highlighter and hasattr(self.highlighter, 'set_error_details'):
            # Pass full error details including column information
            self.highlighter.set_error_details(self.syntax_errors)
            # Force rehighlight to show errors
            self.highlighter.rehighlight()
        elif self.highlighter and hasattr(self.highlighter, 'set_error_lines'):
            # Fallback for old API
            error_lines = {e['line'] for e in self.syntax_errors}
            self.highlighter.set_error_lines(error_lines)
            self.highlighter.rehighlight()
        
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
    
    def paintEvent(self, event):
        """Paint indentation guides like VSCode - optimized."""
        super().paintEvent(event)
        
        # Skip indentation guides if typing (performance optimization)
        if hasattr(self, '_skip_paint_count') and self._skip_paint_count > 0:
            self._skip_paint_count -= 1
            return
        
        # Draw indentation guides
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(QtGui.QPen(QtGui.QColor(45, 45, 45), 1))  # Subtle gray lines
        
        # Cache font metrics
        if self._cached_char_width is None:
            fm = self.fontMetrics()
            self._cached_char_width = fm.horizontalAdvance(' ')
        
        indent_width = 4 * self._cached_char_width  # 4 spaces per indent level
        
        # Get visible blocks
        block = self.firstVisibleBlock()
        viewport_height = self.viewport().height()
        block_top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        
        while block.isValid() and block_top <= viewport_height:
            block_bottom = block_top + int(self.blockBoundingRect(block).height())
            
            # Only paint visible blocks
            if block_bottom >= 0:
                text = block.text()
                
                # Fast indentation calculation
                if text:
                    indent_count = len(text) - len(text.lstrip(' \t'))
                    if '\t' in text[:indent_count]:
                        indent_count = text[:indent_count].count('\t') * 4 + text[:indent_count].count(' ')
                    
                    # Draw vertical lines for each indentation level
                    indent_levels = indent_count // 4
                    if indent_levels > 0:
                        for level in range(min(indent_levels, 10)):  # Limit to 10 levels max
                            x = int(level * indent_width)
                            painter.drawLine(x, block_top, x, block_bottom)
            
            # Move to next block
            block = block.next()
            block_top = block_bottom
    
    def _can_fold_line(self, line_number):
        """Check if a line can be folded and if it's currently folded."""
        # Get the block for this line
        block = self.document().findBlockByNumber(line_number - 1)
        if not block.isValid():
            return False, False
        
        text = block.text()
        # Only allow folding for lines that end with ':' (Python) or '{' (MEL-style)
        stripped = text.rstrip()
        if not (stripped.endswith(':') or stripped.endswith('{')):
            return False, False
        
        # Check if next line exists and is more indented
        next_block = block.next()
        if not next_block.isValid():
            return False, False
        
        # Calculate indentation levels
        current_indent = self._get_indent_level(text)
        next_indent = self._get_indent_level(next_block.text())
        
        if next_indent > current_indent:
            is_folded = line_number in self.folded_blocks
            return True, is_folded
        
        return False, False
    
    def _get_indent_level(self, text):
        """Get the indentation level of a line."""
        indent = 0
        for char in text:
            if char == ' ':
                indent += 1
            elif char == '\t':
                indent += 4
            else:
                break
        return indent // 4
    
    def toggle_fold(self, line_number):
        """Toggle folding for a line."""
        can_fold, is_folded = self._can_fold_line(line_number)
        if not can_fold:
            return
        
        if is_folded:
            self._unfold_line(line_number)
        else:
            self._fold_line(line_number)
        
        # Update display
        self.viewport().update()
        self.line_number_area.update()
    
    def _fold_line(self, line_number):
        """Fold (collapse) a block of code."""
        block = self.document().findBlockByNumber(line_number - 1)
        if not block.isValid():
            return
        
        # Get the indentation level of the fold line
        fold_indent = self._get_indent_level(block.text())
        
        # Hide all subsequent blocks that are more indented
        next_block = block.next()
        while next_block.isValid():
            next_indent = self._get_indent_level(next_block.text())
            next_text = next_block.text().strip()
            
            # Stop if we reach a line with same or less indentation (and it's not blank)
            if next_text and next_indent <= fold_indent:
                break
            
            # Hide this block
            next_block.setVisible(False)
            next_block = next_block.next()
        
        # Mark as folded
        self.folded_blocks.add(line_number)
    
    def _unfold_line(self, line_number):
        """Unfold (expand) a block of code."""
        block = self.document().findBlockByNumber(line_number - 1)
        if not block.isValid():
            return
        
        # Get the indentation level of the fold line
        fold_indent = self._get_indent_level(block.text())
        
        # Show all subsequent blocks that were hidden
        next_block = block.next()
        while next_block.isValid():
            next_indent = self._get_indent_level(next_block.text())
            next_text = next_block.text().strip()
            
            # Stop if we reach a line with same or less indentation (and it's not blank)
            if next_text and next_indent <= fold_indent:
                break
            
            # Show this block
            next_block.setVisible(True)
            next_block = next_block.next()
        
        # Mark as unfolded
        self.folded_blocks.discard(line_number)
        
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
                
                # Check if this line can be folded (has indented content below)
                can_fold, is_folded = self._can_fold_line(line_number)
                
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
                
                # Draw fold indicator if line can be folded
                if can_fold:
                    # Draw clickable fold icon (triangle)
                    painter.setPen(QtGui.QPen(QtGui.QColor(150, 150, 150), 1))
                    painter.setBrush(QtGui.QColor(150, 150, 150))
                    
                    center_y = top + self.fontMetrics().height() // 2
                    if is_folded:
                        # Right-pointing triangle (collapsed)
                        points = [
                            QtCore.QPoint(3, center_y - 3),
                            QtCore.QPoint(3, center_y + 3),
                            QtCore.QPoint(8, center_y)
                        ]
                    else:
                        # Down-pointing triangle (expanded)
                        points = [
                            QtCore.QPoint(3, center_y - 2),
                            QtCore.QPoint(8, center_y - 2),
                            QtCore.QPoint(5, center_y + 2)
                        ]
                    painter.drawPolygon(points)
                    painter.setBrush(QtCore.Qt.NoBrush)
                
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
        # Skip paint events during rapid typing (performance optimization)
        self._skip_paint_count = 2  # Skip next 2 paint events
        
        # Handle completer popup
        if self.completer and self.completer.popup().isVisible():
            # Tab accepts the completion
            if event.key() == QtCore.Qt.Key_Tab:
                self.completer.popup().hide()
                self._insert_completion(self.completer.currentCompletion())
                return
            # Escape closes the popup
            elif event.key() == QtCore.Qt.Key_Escape:
                self.completer.popup().hide()
                return
            # Enter/Return should close popup and insert newline normally
            elif event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                self.completer.popup().hide()
                # Continue with normal Enter handling below
        
        # Ctrl+Space to manually trigger autocomplete
        if event.key() == QtCore.Qt.Key_Space and event.modifiers() == QtCore.Qt.ControlModifier:
            self._show_autocomplete()
            return
        
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
        
        # Auto-trigger autocomplete while typing (like VSCode)
        # Trigger on alphanumeric characters and underscore
        if event.text().isalnum() or event.text() == '_':
            # Small delay to avoid showing on every keystroke
            QtCore.QTimer.singleShot(100, self._show_autocomplete)
            
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
        
    def show_inline_replacement(self, replacement_info, new_code):
        """Show VSCode-style inline diff for code replacement"""
        self.inline_diff_manager.show_inline_diff(replacement_info, new_code)
    
    def clear_inline_replacement(self):
        """Clear any active inline diff"""
        self.inline_diff_manager.clear_diff()
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        super().mousePressEvent(event)
        
        # Clear error highlights when user clicks (optional)
        # This gives immediate feedback that user acknowledged the error
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pass  # Keep errors visible for now