"""
Advanced Code Editor with VSCode-style Syntax Highlighting & Error Detection
Comprehensive Python, PySide6/Qt, and Maya support with real-time error highlighting
"""
import os, ast, sys, traceback
from PySide6 import QtCore, QtGui, QtWidgets
from .highlighter import PythonHighlighter, MELHighlighter
from .hover_docs import get_documentation


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
                    line_number = block.blockNumber() + 1
                    click_x = event.pos().x()
                    
                    # Check if click is in fold indicator area (leftmost 8 pixels)
                    if click_x <= 8:
                        self.code_editor.toggle_fold(line_number)
                        break
                    # Check if click is in breakpoint area (8-17 pixels from left)
                    elif 8 < click_x <= 17:
                        self.code_editor.toggle_breakpoint(line_number)
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
        self.enable_folding = True  # Re-enabled with lazy calculation
        self._foldable_lines_cache = {}  # Cache: {line_number: (can_fold, is_folded)}
        self._cache_valid = False  # Track if cache needs refresh
        
        # Breakpoints tracking (VSCode-style debugging)
        self.breakpoints = set()  # Set of line numbers with breakpoints
        self.current_debug_line = None  # Currently executing line during debug
        
        # Paint optimization for indentation guides
        self._skip_paint_count = 0
        self._cached_char_width = None
        self.enable_indentation_guides = False  # Disabled by default for better Maya performance
        
        # Real-time error checking
        self.error_timer = QtCore.QTimer()
        self.error_timer.timeout.connect(self._check_syntax_errors)
        self.error_timer.setSingleShot(True)
        
        # Connect text changed signal for real-time error checking
        self.textChanged.connect(self._on_text_changed)
        
        # Autocomplete setup
        self.completer = None
        self._setup_autocomplete()
        
        # 🎯 Copilot-style inline diff with red/green highlighting
        from .copilot_inline_diff import CopilotInlineDiff
        self.inline_diff_manager = CopilotInlineDiff(self)
        
        # Enhanced line number area
        self.line_number_area = _LineNumberArea(self)
        self.line_number_area.show()  # Ensure it's visible
        
        # Connect signals
        self.blockCountChanged.connect(self._update_number_area_width)
        self.updateRequest.connect(self._update_number_area)
        # Remove cursorPositionChanged to reduce repaints (performance optimization for Maya)
        # self.cursorPositionChanged.connect(self._update_number_area_width)
        
        self._update_number_area_width()
        self.line_number_area.update()  # Force initial update
        
        # Enable hover tooltips for error messages
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        
        # Morpheus suggestion widget
        self._morpheus_suggestion_widget = None
        self._current_suggestion_line = None
        
        # Initialize syntax highlighting
        self.set_language("python")
        
        # Store inline diff selections so they don't get cleared
        self.inline_diff_selections = []
        
    def apply_inline_diff_highlighting(self, selections):
        """Apply inline diff highlighting that persists"""
        print(f"[CODE_EDITOR] apply_inline_diff_highlighting() called with {len(selections)} selections")
        self.inline_diff_selections = selections
        self._refresh_all_selections()
    
    def _refresh_all_selections(self):
        """Refresh all extra selections including inline diffs"""
        all_selections = self.inline_diff_selections[:]
        # Add any other selections here (current line, search results, etc.)
        print(f"[CODE_EDITOR] _refresh_all_selections() - applying {len(all_selections)} selections")
        self.setExtraSelections(all_selections)
        print(f"[CODE_EDITOR] setExtraSelections() completed")
        
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
    
    def get_syntax_errors(self):
        """Get list of current syntax errors with line numbers"""
        return getattr(self, 'syntax_errors', [])
    
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
        # Invalidate folding cache when text changes
        self._cache_valid = False
        
        # Debounce error checking - wait 1500ms after user stops typing (longer for Maya performance)
        self.error_timer.stop()
        self.error_timer.start(1500)  # Increased from 500ms for better Maya performance
        
    def _check_syntax_errors(self):
        """Check for syntax errors and highlight them (VSCode style - multi-pass detection)."""
        if self.language != "python":
            return
        
            
        # Clear previous errors
        self._clear_error_highlights()
        self.syntax_errors.clear()
        
        # Clear red background from previous errors
        if self.highlighter and hasattr(self.highlighter, 'clear_copilot_error_lines'):
            self.highlighter.clear_copilot_error_lines()
        
        code = self.toPlainText()
        
        if not code.strip():
            if self.highlighter:
                self.highlighter.rehighlight()
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
            # NOTE: Be VERY conservative to avoid false positives - only check most obvious cases
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
                
                # Check for standalone keywords ONLY - no other pattern checks to avoid false positives
                # These are lines that are JUST the keyword with nothing else
                if line_stripped in ('def', 'class', 'if', 'elif', 'for', 'while', 'try', 'else', 'finally',
                                    'import', 'from', 'except'):
                    errors.append({
                        'line': i,
                        'column': 1,
                        'message': f'Incomplete statement: {line_stripped}',
                        'type': 'SyntaxError'
                    })
                    error_lines.add(i)
                    
            # Store and highlight errors (limit to first 10 like VSCode)
            self.syntax_errors = errors[:10]
            
            # Get all lines for validation
            all_lines = code.split('\n')
            
            # Format problems for the problems window
            problems = []
            for error in self.syntax_errors:
                # Get the line number Python reported
                line_num = error['line']
                error_message = error['message']
                
                # Validate line number is within bounds
                if line_num < 1 or line_num > len(all_lines):
                    continue
                
                # Get line text from QTextDocument
                block = self.document().findBlockByLineNumber(line_num - 1)
                line_text = block.text() if block.isValid() else ""
                
                # Highlight and emit
                self._highlight_error_line(line_num, error_message)
                self.errorDetected.emit(line_num, error_message)
                
                # Add to problems list
                problems.append({
                    'type': 'Error',
                    'message': error_message,
                    'line': line_num,
                    'file': 'Current File',
                    'line_text': line_text
                })
            
            # Emit all problems at once for the problems window
            self.lintProblemsFound.emit(problems)
            
            # Update visual error highlighting in the editor
            self._update_error_highlighting()
                
            if not self.syntax_errors:
                # Clear red background when no errors
                if self.highlighter and hasattr(self.highlighter, 'clear_copilot_error_lines'):
                    self.highlighter.clear_copilot_error_lines()
                    self.highlighter.rehighlight()
                
                self.errorsCleared.emit()
                self.lintProblemsFound.emit([])  # Clear problems window
                
        except Exception as e:
            print(f"Error in syntax checking: {e}")
            import traceback
            traceback.print_exc()
    
    def _find_actual_error_line(self, all_lines, reported_line, error_message):
        """Find the actual line with the error when Python's compile() reports wrong line.
        
        Python's SyntaxError.lineno is sometimes incorrect, especially after multi-pass
        detection with temporary line comments. This method searches nearby lines to find
        the line that actually contains code that could cause the reported error.
        
        Args:
            all_lines: List of all code lines (split from code string)
            reported_line: Line number Python's compile() reported (1-indexed)
            error_message: The error message from Python
            
        Returns:
            int: The actual line number where the error likely is (1-indexed)
        """
        # Ensure reported line is valid
        if reported_line < 1 or reported_line > len(all_lines):
            return max(1, min(reported_line, len(all_lines)))
        
        reported_text = all_lines[reported_line - 1].strip()
        error_msg_lower = error_message.lower()
        
        # Check if the reported line makes sense for the error
        # If it's a comment, docstring, or blank, it's likely wrong
        is_likely_wrong = (
            not reported_text or  # Blank line
            reported_text.startswith('#') or  # Comment
            reported_text.startswith('"""') or reported_text.startswith("'''") or  # Docstring start
            reported_text == '"""' or reported_text == "'''" or  # Docstring end
            (reported_text.startswith('"') and reported_text.endswith('"') and len(reported_text) > 2) or  # String line
            (reported_text.startswith("'") and reported_text.endswith("'") and len(reported_text) > 2)  # String line
        )
        
        # CRITICAL: For "unmatched ')'" errors, search ENTIRE FILE for lines with mismatched parentheses
        # Python often reports the wrong line (where parsing stops), not where the extra paren is
        if 'unmatched' in error_msg_lower and ')' in error_msg_lower:
            print(f"[SEARCH] Looking for unmatched ')' error (reported line {reported_line})...")
            
            # Strategy: Search BACKWARDS from reported line first (errors often occur earlier)
            # Then search forward if nothing found
            candidates = []
            
            # Search from start of file to reported line (backwards priority)
            for line_num in range(1, reported_line + 1):
                line_text = all_lines[line_num - 1].strip()
                
                # Skip empty, comments, docstrings
                if (not line_text or line_text.startswith('#') or 
                    line_text.startswith('"""') or line_text.startswith("'''")):
                    continue
                
                # Count parentheses on this line
                open_count = line_text.count('(')
                close_count = line_text.count(')')
                
                # If this line has more closing than opening parens, it's the error
                if close_count > open_count:
                    # Calculate priority: prefer lines closer to start of file (where defs/inits are)
                    distance_from_start = line_num
                    priority = close_count - open_count  # How many extra closing parens
                    candidates.append((line_num, line_text, priority, distance_from_start))
            
            # If we found candidates, return the best one (highest priority, closest to start)
            if candidates:
                # Sort by priority (descending), then by distance from start (ascending)
                candidates.sort(key=lambda x: (-x[2], x[3]))
                best_line_num = candidates[0][0]
                best_line_text = candidates[0][1]
                print(f"[OK] Found line {best_line_num} with unmatched ')': '{best_line_text[:60]}'")
                print(f"   Opens: {best_line_text.count('(')}, Closes: {best_line_text.count(')')}")
                return best_line_num
            
            # If still not found, search entire file
            print(f"[WARN] No unmatched ')' found before line {reported_line}, searching entire file...")
            for line_num in range(1, len(all_lines) + 1):
                line_text = all_lines[line_num - 1].strip()
                
                # Skip empty, comments, docstrings
                if (not line_text or line_text.startswith('#') or 
                    line_text.startswith('"""') or line_text.startswith("'''")):
                    continue
                
                # Count parentheses
                open_count = line_text.count('(')
                close_count = line_text.count(')')
                
                if close_count > open_count:
                    print(f"[OK] Found line {line_num} with unmatched ')': '{line_text[:60]}'")
                    return line_num
        
        # If the reported line looks reasonable, use it
        if not is_likely_wrong:
            return reported_line
        
        print(f"[SEARCH] Line {reported_line} looks wrong ('{reported_text[:50]}...'), searching nearby lines...")
        
        # Search nearby lines (±10 lines) for code that could cause this error
        search_range = 10
        start_search = max(1, reported_line - search_range)
        end_search = min(len(all_lines), reported_line + search_range)
        
        # Common error patterns to look for
        error_patterns = {
            'unmatched': [')', ']', '}', '(', '[', '{'],  # Unmatched brackets
            'invalid syntax': [')', '(', 'super(', 'self.', 'def ', 'class ', 'if ', 'for ', 'while '],
            'unexpected': [')', ']', '}'],
            'expected': ['def ', 'class ', 'if ', 'elif ', 'else:', 'try:', 'except', 'finally:'],
            'indent': [],  # Indentation errors - use reported line
        }
        
        # Determine which patterns to look for based on error message
        search_patterns = []
        for key, patterns in error_patterns.items():
            if key in error_msg_lower:
                search_patterns.extend(patterns)
        
        # If no specific patterns, search for any non-empty code line
        if not search_patterns:
            search_patterns = None  # Will match any code line
        
        # Search for the best candidate line
        best_candidate = reported_line
        best_score = -1
        
        for line_num in range(start_search, end_search + 1):
            if line_num < 1 or line_num > len(all_lines):
                continue
            
            line_text = all_lines[line_num - 1].strip()
            
            # Skip empty lines and comments
            if not line_text or line_text.startswith('#'):
                continue
            
            # Skip docstrings
            if line_text.startswith('"""') or line_text.startswith("'''"):
                continue
            
            # Calculate score for this line
            score = 0
            
            # Prefer lines with actual code
            if line_text:
                score += 1
            
            # Prefer lines closer to reported line (but prefer AFTER for unmatched errors)
            distance = abs(line_num - reported_line)
            if 'unmatched' in error_msg_lower and line_num > reported_line:
                # Boost lines AFTER reported line for unmatched errors
                score += (search_range - distance) + 5
            else:
                score += (search_range - distance)
            
            # If we have specific patterns, prefer lines containing them
            if search_patterns:
                for pattern in search_patterns:
                    if pattern in line_text:
                        score += 10  # Big boost for matching pattern
            
            # Special boost for lines with parentheses (common error location)
            if '(' in line_text or ')' in line_text:
                score += 3
            
            if score > best_score:
                best_score = score
                best_candidate = line_num
        
        if best_candidate != reported_line:
            print(f"[OK] Found better candidate at line {best_candidate}: '{all_lines[best_candidate-1].strip()[:50]}...'")
        
        return best_candidate
            
    def _highlight_error_line(self, line_num, message):
        """Highlight error line with VSCode-style red underline."""
        # Store error info for the highlighter
        self.error_highlights.append((line_num, message))
        
    def _clear_error_highlights(self):
        """Clear all error highlights."""
        self.error_highlights.clear()
        
    def _update_error_highlighting(self):
        """Update the syntax highlighter with current error details and apply red background."""
        if self.highlighter and hasattr(self.highlighter, 'set_error_details'):
            # Pass full error details including column information
            self.highlighter.set_error_details(self.syntax_errors)
            
            # Also apply Copilot-style red background to error lines
            error_lines = [e['line'] for e in self.syntax_errors]
            if hasattr(self.highlighter, 'set_copilot_error_lines'):
                self.highlighter.set_copilot_error_lines(error_lines)
            
            # Force rehighlight to show errors
            self.highlighter.rehighlight()
        elif self.highlighter and hasattr(self.highlighter, 'set_error_lines'):
            # Fallback for old API
            error_lines = {e['line'] for e in self.syntax_errors}
            self.highlighter.set_error_lines(error_lines)
            
            # Also try to apply red background
            if hasattr(self.highlighter, 'set_copilot_error_lines'):
                self.highlighter.set_copilot_error_lines(list(error_lines))
            
            self.highlighter.rehighlight()
        
    def get_syntax_errors(self):
        """Get current syntax errors."""
        return self.syntax_errors.copy()
        
    def clear_syntax_errors(self):
        """Clear syntax error highlights including red background."""
        self._clear_error_highlights()
        self.syntax_errors.clear()
        
        # Clear red background highlighting
        if self.highlighter and hasattr(self.highlighter, 'clear_copilot_error_lines'):
            self.highlighter.clear_copilot_error_lines()
            self.highlighter.rehighlight()
        
        self.errorsCleared.emit()
        
    def _number_area_width(self):
        """Calculate line number area width (ultra-compact VSCode-style)."""
        digits = len(str(max(1, self.blockCount())))
        # Ultra-compact: fold(8px) + breakpoint(10px) + line_number + padding(2px)
        width = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return width
        
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
        
        # Skip if indentation guides are disabled (for max performance)
        if not self.enable_indentation_guides:
            return
        
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
        """Check if a line can be folded and if it's currently folded - OPTIMIZED with caching."""
        # Return cached result if available and cache is valid
        if self._cache_valid and line_number in self._foldable_lines_cache:
            return self._foldable_lines_cache[line_number]
        
        # Calculate fold state
        block = self.document().findBlockByNumber(line_number - 1)
        if not block.isValid():
            result = (False, False)
            self._foldable_lines_cache[line_number] = result
            return result
        
        text = block.text()
        # Only allow folding for lines that end with ':' (Python) or '{' (MEL-style)
        stripped = text.rstrip()
        if not (stripped.endswith(':') or stripped.endswith('{')):
            result = (False, False)
            self._foldable_lines_cache[line_number] = result
            return result
        
        # Check if next line exists and is more indented
        next_block = block.next()
        if not next_block.isValid():
            result = (False, False)
            self._foldable_lines_cache[line_number] = result
            return result
        
        # Calculate indentation levels
        current_indent = self._get_indent_level(text)
        next_indent = self._get_indent_level(next_block.text())
        
        if next_indent > current_indent:
            is_folded = line_number in self.folded_blocks
            result = (True, is_folded)
            self._foldable_lines_cache[line_number] = result
            return result
        
        result = (False, False)
        self._foldable_lines_cache[line_number] = result
        return result
    
    def _build_fold_cache_for_visible_lines(self):
        """Build folding cache for currently visible lines only - OPTIMIZED."""
        if self._cache_valid:
            return  # Cache already valid
        
        # Clear old cache
        self._foldable_lines_cache.clear()
        
        # Only cache visible lines
        block = self.firstVisibleBlock()
        viewport_height = self.viewport().height()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        
        while block.isValid() and top <= viewport_height:
            line_number = block.blockNumber() + 1
            # This will cache the result
            self._can_fold_line(line_number)
            
            block = block.next()
            top += int(self.blockBoundingRect(block).height()) if block.isValid() else 0
        
        self._cache_valid = True
    
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
        
        # Invalidate cache since fold state changed
        self._cache_valid = False
    
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
        
        # Invalidate cache since fold state changed
        self._cache_valid = False
    
    def toggle_breakpoint(self, line_number):
        """Toggle breakpoint on/off for a line (VSCode-style) - OPTIMIZED."""
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)
        
        # Only update line number area, not entire viewport (performance)
        self.line_number_area.update()
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints - OPTIMIZED."""
        if self.breakpoints:  # Only update if there were breakpoints
            self.breakpoints.clear()
            self.line_number_area.update()
    
    def get_breakpoints(self):
        """Get list of all breakpoint line numbers."""
        return sorted(list(self.breakpoints))
    
    def set_current_debug_line(self, line_number):
        """Set the currently executing line during debugging - OPTIMIZED."""
        old_line = self.current_debug_line
        self.current_debug_line = line_number
        
        # Only update if changed
        if old_line != line_number:
            self.line_number_area.update()
        
        # Scroll to the line
        if line_number:
            cursor = QtGui.QTextCursor(self.document().findBlockByNumber(line_number - 1))
            self.setTextCursor(cursor)
            self.centerCursor()
    
    def clear_current_debug_line(self):
        """Clear the current debug line indicator - OPTIMIZED."""
        if self.current_debug_line is not None:
            self.current_debug_line = None
            self.line_number_area.update()
        
    def _paint_line_numbers(self, event):
        """Paint line numbers with VSCode-style error indicators and breakpoints - OPTIMIZED."""
        painter = QtGui.QPainter(self.line_number_area)
        # Use slightly lighter background than editor for visibility
        painter.fillRect(event.rect(), QtGui.QColor(37, 37, 38))
        
        # Draw right border
        painter.setPen(QtGui.QColor(45, 45, 45))
        painter.drawLine(event.rect().topRight(), event.rect().bottomRight())
        
        # Build folding cache for visible lines if needed (lazy evaluation)
        if self.enable_folding and not self._cache_valid:
            self._build_fold_cache_for_visible_lines()
        
        # Pre-convert sets to optimize lookups
        breakpoints = self.breakpoints  # Direct reference
        has_breakpoints = len(breakpoints) > 0
        has_errors = len(self.syntax_errors) > 0
        current_debug = self.current_debug_line
        
        # Build error line set for O(1) lookup instead of O(n) list comprehension
        if has_errors:
            error_lines = {error['line'] for error in self.syntax_errors}
        else:
            error_lines = set()
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(
            self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        # Setup fonts and colors once
        font = QtGui.QFont("Consolas", 9)
        painter.setFont(font)
        font_height = self.fontMetrics().height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_number = block_number + 1
                
                # Fast O(1) lookups
                has_error = line_number in error_lines if has_errors else False
                has_breakpoint = line_number in breakpoints if has_breakpoints else False
                is_debug_line = line_number == current_debug
                
                # Skip expensive folding checks completely unless enabled
                can_fold = False
                is_folded = False
                if self.enable_folding:
                    can_fold, is_folded = self._can_fold_line(line_number)
                
                # Draw current debug line background (yellow) - full width
                if is_debug_line:
                    debug_rect = QtCore.QRect(0, top, self.line_number_area.width(), font_height)
                    painter.fillRect(debug_rect, QtGui.QColor(200, 200, 0, 50))
                
                # Set color based on error status (no visual indicator to avoid confusion with breakpoints)
                if has_error:
                    painter.setPen(QtGui.QColor(255, 100, 100))  # Light red text for line numbers with errors
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
                
                # Draw breakpoint (red circle) - ultra-compact spacing
                if has_breakpoint:
                    painter.setPen(QtCore.Qt.NoPen)
                    painter.setBrush(QtGui.QColor(220, 60, 60))
                    center_y = top + font_height // 2
                    # Position breakpoint very close to line numbers
                    painter.drawEllipse(QtCore.QPoint(13, center_y), 3, 3)
                    painter.setBrush(QtCore.Qt.NoBrush)
                    painter.setPen(QtGui.QColor(100, 100, 100))
                
                # Draw line number - minimal spacing
                painter.drawText(18, top, self.line_number_area.width() - 20, 
                               font_height, QtCore.Qt.AlignRight, str(line_number))
                               
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
            
    def keyPressEvent(self, event):
        """Enhanced key press handling with smart indentation and auto-completion."""
        # Skip paint events during rapid typing (performance optimization)
        self._skip_paint_count = 5  # Skip next 5 paint events for smoother typing
        
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
        line_number = replacement_info.get('start_line', replacement_info.get('line', 0))
        old_code = replacement_info.get('old_code', '')
        
        # If old_code is empty, try to get it from the editor
        if not old_code:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            for _ in range(line_number):
                cursor.movePosition(QtGui.QTextCursor.NextBlock)
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            old_code = cursor.selectedText()
        
        # Call show_diff with line_number, old_code, new_code
        self.inline_diff_manager.show_diff(line_number, old_code, new_code)
    
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
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events to show AI-powered suggestions on hover over errors and documentation tooltips."""
        super().mouseMoveEvent(event)
        
        # Get cursor position at mouse location
        cursor = self.cursorForPosition(event.pos())
        line_number = cursor.blockNumber() + 1  # 1-indexed
        
        # Get the main window to access Problems window data
        main_window = self._get_main_window()
        if not main_window:
            return
        
        # Get editor ID and problems for this editor from Problems window
        editor_id = id(self)
        editor_problems = main_window.editor_problems.get(editor_id, [])
        
        # Check if this line has an error in the Problems window
        error_info = None
        for problem in editor_problems:
            if problem.get('line') == line_number:
                error_info = problem
                break
        
        if error_info:
            # Show error tooltip and start/continue hover timer for Morpheus suggestion
            self._handle_error_hover(error_info, line_number, event)
        else:
            # No error on this line - check for documentation tooltip
            self._handle_documentation_hover(cursor, event)
            self._reset_morpheus_timer()
            self._hide_morpheus_suggestion()
    
    def _handle_documentation_hover(self, cursor, event):
        """Show VS Code-style documentation tooltip with syntax highlighting and Pylance integration."""
        # Select the word under cursor
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        word = cursor.selectedText().strip()
        
        if not word:
            QtWidgets.QToolTip.hideText()
            return
        
        # Get full code text and cursor position for intelligent analysis
        code_text = self.toPlainText()
        cursor_pos = cursor.position()
        
        # Try Pylance first if available
        pylance_info = self._get_pylance_hover_info(word, cursor_pos)
        
        if pylance_info:
            # Use Pylance information
            tooltip_text = self._format_pylance_tooltip(word, pylance_info)
        else:
            # Fallback to our documentation system
            from .hover_docs import get_documentation
            result = get_documentation(word, code_text, cursor_pos)
            
            if result[0] is None:
                QtWidgets.QToolTip.hideText()
                return
            
            colored_signature, description, doc_type = result
            tooltip_text = self._format_custom_tooltip(word, colored_signature, description, doc_type)
        
        QtWidgets.QToolTip.showText(event.globalPosition().toPoint(), tooltip_text, self)
    
    def _get_pylance_hover_info(self, word, position):
        """Get hover information from Pylance if available."""
        try:
            # Try to get hover info from Pylance LSP
            # This would integrate with VS Code's language server
            # For now, return None to use fallback
            return None
        except:
            return None
    
    def _format_pylance_tooltip(self, word, pylance_info):
        """Format tooltip using Pylance information."""
        import os
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        suggestion_icon = os.path.join(assets_dir, 'suggestion.png')
        
        # Build tooltip with transparent background
        tooltip_text = f"<div style='padding:8px; border:1px solid #30363d; border-radius:4px; max-width:500px'>"
        
        # Icon and word name
        tooltip_text += f"<div style='margin-bottom:6px'>"
        tooltip_text += f"<img src='{suggestion_icon}' width='14' height='14' style='vertical-align:middle'> "
        tooltip_text += f"<b style='color:#d4d4d4; font-size:13px'>{word}</b></div>"
        
        # Pylance content
        tooltip_text += f"<div style='color:#cccccc; font-size:12px'>{pylance_info}</div>"
        tooltip_text += "</div>"
        
        return tooltip_text
    
    def _format_custom_tooltip(self, word, colored_signature, description, doc_type):
        """Format tooltip using custom documentation with appropriate icons."""
        import os
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        
        # Map doc types to icon files based on available assets
        icon_map = {
            'function': 'suggestion.png',     # Functions get suggestion icon
            'class': 'file.png',              # Classes get file icon
            'method': 'suggestion.png',       # Methods get suggestion icon
            'keyword': 'python.png',          # Keywords get Python icon
            'builtin': 'python.png',          # Built-ins get Python icon
            'module': 'open_folder.png'       # Modules get folder icon
        }
        icon_file = icon_map.get(doc_type, 'suggestion.png')
        icon_path = os.path.join(assets_dir, icon_file)
        
        # Build tooltip without background colors (fully transparent)
        tooltip_text = f"<div style='padding:10px; max-width:500px'>"
        
        # Icon and word name
        tooltip_text += f"<div style='margin-bottom:8px'>"
        tooltip_text += f"<img src='{icon_path}' width='16' height='16' style='vertical-align:middle'> "
        tooltip_text += f"<b style='color:#ffffff; font-size:13px'>{word}</b>"
        
        # Add type label
        type_labels = {
            'function': 'function',
            'class': 'class',
            'method': 'method',
            'keyword': 'keyword',
            'builtin': 'built-in',
            'module': 'module'
        }
        type_label = type_labels.get(doc_type, '')
        if type_label:
            tooltip_text += f" <span style='color:#a0a0a0; font-size:11px; font-style:italic'>({type_label})</span>"
        
        tooltip_text += "</div>"
        
        # Colored signature (no background)
        tooltip_text += colored_signature
        
        # Description
        if description:
            # Replace newlines with <br> for HTML
            desc_html = description.replace('\n', '<br>')
            tooltip_text += f"<div style='margin-top:8px; color:#e0e0e0; font-size:11px; line-height:1.5'>{desc_html}</div>"
        
        tooltip_text += "</div>"
        
        return tooltip_text
    
    def _handle_error_hover(self, error_info, line_number, event):
        """Handle hovering over an error line using Problems window data."""
        # Initialize timer if needed
        if not hasattr(self, '_morpheus_hover_timer'):
            self._morpheus_hover_timer = QtCore.QTimer()
            self._morpheus_hover_timer.setSingleShot(True)
            self._morpheus_hover_timer.timeout.connect(self._on_morpheus_hover_timeout)
            self._hover_error_info = None
        
        # Check if we're hovering on a new line
        if self._current_suggestion_line != line_number:
            # New line - reset and start timer
            self._current_suggestion_line = line_number
            self._hover_error_info = error_info  # Store the problem from Problems window
            self._morpheus_hover_timer.stop()
            self._morpheus_hover_timer.start(2000)
            
            # Get icon paths
            import os
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
            error_icon = os.path.join(assets_dir, 'syntax_error.png')
            suggestion_icon = os.path.join(assets_dir, 'suggestion.png')
            morpheus_icon = os.path.join(assets_dir, 'morpheus.png')
            
            # Show immediate tooltip with icons
            error_message = error_info['message']
            tooltip_text = f"<b style='color:#f48771'><img src='{error_icon}' width='16' height='16'> Syntax Error:</b><br>{error_message}"
            tooltip_text += f"<br><i style='color:#888'>Line {line_number}</i>"
            
            # Add basic suggestion
            suggestion = self._generate_error_suggestion(error_message, line_number)
            if suggestion:
                tooltip_text += f"<br><br><b style='color:#58a6ff'><img src='{suggestion_icon}' width='16' height='16'> Suggestion:</b><br>{suggestion}"
            
            # Check if Morpheus is available
            if self._is_morpheus_available():
                tooltip_text += f"<br><br><i style='color:#888'><img src='{morpheus_icon}' width='16' height='16'> Hover for 2s to get Morpheus suggestion...</i>"
            else:
                tooltip_text += f"<br><br><i style='color:#888'><img src='{morpheus_icon}' width='16' height='16'> Turn Morpheus online to get AI suggestions</i>"
            
            QtWidgets.QToolTip.showText(event.globalPosition().toPoint(), tooltip_text, self)
        elif not self._morpheus_hover_timer.isActive():
            # Same line, timer not active
            if not (self._morpheus_suggestion_widget and self._morpheus_suggestion_widget.isVisible()):
                # Not showing widget yet - restart timer
                self._hover_error_info = error_info
                self._morpheus_hover_timer.start(2000)
    
    def _reset_morpheus_timer(self):
        """Reset the Morpheus hover timer."""
        if hasattr(self, '_morpheus_hover_timer'):
            self._morpheus_hover_timer.stop()
        self._current_suggestion_line = None
        self._hover_error_info = None
    
    def _on_morpheus_hover_timeout(self):
        """Called after hovering on error for 2 seconds - uses Problems window data."""
        if self._current_suggestion_line and hasattr(self, '_hover_error_info') and self._hover_error_info:
            # Use the error info from Problems window that we stored
            print(f"[TIMER] Timer fired for line {self._current_suggestion_line} from Problems window")
            self._request_morpheus_suggestion(self._hover_error_info, self._current_suggestion_line)
        else:
            print(f"[WARN] Timer fired but no error info stored")
    
    def _request_morpheus_suggestion(self, error_info, line_number):
        """Request AI suggestion from Morpheus using Problems window data.
        
        The error_info already comes from Problems window, so we use it directly.
        """
        # Check if Morpheus is available
        if not self._is_morpheus_available():
            print("[WARN] Morpheus is not available")
            return
        
        # Use the error_info that was passed from Problems window
        actual_line = error_info.get('line', line_number)
        error_message = error_info.get('message', 'Syntax error')
        
        # CRITICAL: Use the line text that was stored when error was detected
        # NOT the current line text (which may have been edited)
        stored_line_text = error_info.get('line_text', None)
        
        if stored_line_text is None:
            # Fallback: read current line if no stored text (shouldn't happen)
            cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(actual_line - 1))
            line_text = cursor.block().text()
            print(f"[WARN] No stored line_text, reading current: '{line_text.strip()}'")
        else:
            line_text = stored_line_text
        
        print(f"=" * 50)
        print(f"[PROBLEMS] WINDOW DATA:")
        print(f"   Line from Problems: {actual_line}")
        print(f"   Error from Problems: {error_message}")
        print(f"   Original Line Text: '{line_text.strip()}'")
        print(f"=" * 50)
        
        # Get surrounding context using CURRENT editor content
        context_lines = []
        for i in range(max(0, actual_line - 4), min(self.document().blockCount(), actual_line + 3)):
            block = self.document().findBlockByLineNumber(i)
            prefix = ">>> " if (i + 1) == actual_line else "    "
            context_lines.append(f"{prefix}Line {i+1}: {block.text()}")
        
        print(f"[CONTEXT] Around line {actual_line}:")
        for ctx_line in context_lines:
            print(f"   {ctx_line}")
        print(f"=" * 50)
        
        # Build context string
        context = '\n'.join([self.document().findBlockByLineNumber(i).text() 
                            for i in range(max(0, actual_line - 4), min(self.document().blockCount(), actual_line + 3))])
        
        # Request suggestion from Morpheus with the ORIGINAL line text from Problems window
        self._request_morpheus_fix_async(error_message, line_text, context, actual_line)
    
    def _get_main_window(self):
        """Get the main window instance."""
        try:
            # Traverse up the parent hierarchy to find the main window
            widget = self
            while widget:
                parent = widget.parent()
                if parent is None:
                    # We've reached the top - this should be the main window
                    return widget
                widget = parent
            return None
        except:
            return None
    
    def _is_morpheus_available(self):
        """Check if Morpheus AI is available."""
        try:
            # Check if we have access to main window with Morpheus
            if hasattr(self, 'parent') and self.parent():
                main_window = self.parent()
                while main_window.parent():
                    main_window = main_window.parent()
                
                if hasattr(main_window, 'chat_manager') and main_window.chat_manager:
                    return True
            return False
        except:
            return False
    
    def _request_morpheus_fix_async(self, error_message, line_text, context, line_number):
        """Request fix from Morpheus AI asynchronously."""
        try:
            # Get main window
            main_window = self.parent()
            while main_window.parent():
                main_window = main_window.parent()
            
            if not hasattr(main_window, 'chat_manager') or not main_window.chat_manager:
                return
            
            # Create prompt for Morpheus - be extremely specific
            prompt = f"""Fix this syntax error. Return ONLY the corrected code line.

Error: {error_message}
Broken: {line_text.strip()}

Reply with just the fixed line. No explanations. No quotes. No markdown.
If the error is "invalid syntax" on "def test", reply with: def test():
If the error is "expected ':'" on "if x == 5", reply with: if x == 5:"""
            
            # Send to Morpheus asynchronously
            QtCore.QTimer.singleShot(100, lambda: self._send_morpheus_request(main_window, prompt, line_number, line_text))
            
        except Exception as e:
            print(f"Error requesting Morpheus suggestion: {e}")
    
    def _send_morpheus_request(self, main_window, prompt, line_number, original_line):
        """Send request to Morpheus and handle response."""
        try:
            # Store original line for reference
            self._original_error_line = original_line
            self._error_line_number = line_number
            
            # Get Morpheus
            morpheus = main_window.chat_manager.morpheus
            if not morpheus or not morpheus.client:
                print("[WARN] Morpheus client not available")
                return
            
            print(f"[MORPHEUS] Sending request to Morpheus ({morpheus.provider})...")
            
            # Get response directly from API
            try:
                system_msg = "You fix syntax errors. Return ONLY the corrected code line. NO explanations. NO markdown. NO docstrings. Just the fixed code."
                
                if morpheus.provider == "claude":
                    response = morpheus.client.messages.create(
                        model=morpheus.current_model,
                        max_tokens=100,  # Shorter to force concise response
                        system=system_msg,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    suggestion = response.content[0].text.strip()
                else:  # openai
                    response = morpheus.client.chat.completions.create(
                        model=morpheus.current_model,
                        max_tokens=100,  # Shorter to force concise response
                        temperature=0,  # More deterministic
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    suggestion = response.choices[0].message.content.strip()
                
                print(f"[OK] Got Morpheus response: {suggestion[:50]}...")
                
                # Extract code from response
                extracted = self._extract_code_from_response(suggestion)
                
                if extracted and extracted.strip() != original_line.strip():
                    # Schedule UI update on main thread
                    QtCore.QTimer.singleShot(0, lambda: self._show_morpheus_suggestion(extracted, line_number, original_line))
                else:
                    print("[WARN] No valid suggestion extracted")
                    
            except Exception as e:
                print(f"[ERROR] Morpheus API error: {e}")
                
        except Exception as e:
            print(f"Error sending Morpheus request: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_code_from_response(self, response):
        """Extract code from Morpheus response - handles multiple formats."""
        import re
        
        print(f"[EXTRACT] Extracting from response: {response[:100]}...")
        
        # Remove any quotes wrapping the entire response
        cleaned = response.strip()
        if cleaned.startswith('"""') and cleaned.endswith('"""'):
            cleaned = cleaned[3:-3].strip()
        elif cleaned.startswith("'''") and cleaned.endswith("'''"):
            cleaned = cleaned[3:-3].strip()
        elif cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1].strip()
        elif cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1].strip()
        
        # Strategy 1: Look for markdown code blocks
        code_match = re.search(r'```(?:python)?\s*(.*?)\s*```', cleaned, re.DOTALL)
        if code_match:
            extracted = code_match.group(1).strip()
            # If multiple lines, take the first non-empty, non-comment line
            lines = [l.strip() for l in extracted.split('\n') if l.strip() and not l.strip().startswith('#')]
            if lines:
                result = lines[0]
                print(f"[OK] Extracted from markdown: {result}")
                return result
        
        # Strategy 2: Remove common explanatory prefixes
        prefixes_to_remove = [
            r'^(?:Here\'s|Here is|The fixed|The corrected|Fixed|Corrected)\s+.*?:\s*',
            r'^.*?should be:\s*',
            r'^.*?change.*?to:\s*',
            r'^Response:\s*',
            r'^Answer:\s*',
        ]
        for prefix_pattern in prefixes_to_remove:
            cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Strategy 3: If response has multiple lines, try to find the actual code line
        lines = cleaned.split('\n')
        code_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Skip comments
            if line.startswith('#'):
                continue
            # Skip docstrings (triple quotes at start/end)
            if line.startswith('"""') or line.startswith("'''"):
                continue
            # Skip lines that look like explanations (contain common words without code symbols)
            if not any(char in line for char in ['(', ')', '=', ':', '[', ']', '{', '}']):
                if len(line.split()) > 5:  # Likely an explanation sentence
                    continue
            code_lines.append(line)
        
        if code_lines:
            result = code_lines[0]
            print(f"[OK] Extracted from multi-line: {result}")
            return result
        
        # Strategy 4: Just return the cleaned response
        print(f"[WARN] Returning cleaned response: {cleaned}")
        return cleaned
    
    def _show_morpheus_suggestion(self, suggestion, line_number, original_line):
        """Show Morpheus suggestion with green highlighting and action buttons."""
        from PySide6 import QtCore, QtGui, QtWidgets
        import os
        
        print(f"=" * 50)
        print(f"[SUGGESTION] SHOWING SUGGESTION WIDGET:")
        print(f"   Line from Problems window: {line_number}")
        print(f"   Original line text: '{original_line.strip()}'")
        print(f"   Morpheus suggestion: '{suggestion.strip()}'")
        
        # Verify the line number matches what's in the editor
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line_number - 1))
        current_line_text = cursor.block().text()
        print(f"   Current editor line {line_number}: '{current_line_text.strip()}'")
        print(f"=" * 50)
        
        # Hide any existing suggestion widget
        self._hide_morpheus_suggestion()
        
        self._morpheus_suggestion_widget = QtWidgets.QWidget(self)
        self._morpheus_suggestion_widget.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self._morpheus_suggestion_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        layout = QtWidgets.QVBoxLayout(self._morpheus_suggestion_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container without border - using dialog theme colors
        container = QtWidgets.QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
        """)
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)
        
        # Header with Morpheus icon
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(6)
        
        # Load Morpheus icon
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        morpheus_icon_path = os.path.join(assets_path, 'morpheus.png')
        
        if os.path.exists(morpheus_icon_path):
            icon_label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(morpheus_icon_path).scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("border: none; background: transparent;")
            header_layout.addWidget(icon_label)
        
        header_text = QtWidgets.QLabel("Morpheus AI Suggestion")
        header_text.setStyleSheet("color: #00ff41; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        
        # Add buttons to header (right side) - smaller size
        # Accept button (check icon) - using dialog theme green
        accept_btn = QtWidgets.QPushButton("✓")
        accept_btn.setToolTip("Accept suggestion")
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff41;
                color: #0d1117;
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 12px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #00cc33;
            }
        """)
        # Store line_number in closure to ensure it's captured correctly
        captured_line = line_number
        accept_btn.clicked.connect(lambda: self._accept_morpheus_suggestion(suggestion, captured_line))
        print(f"   Accept button will apply to line: {captured_line}")
        header_layout.addWidget(accept_btn)
        
        # Reject button (X icon) - red color
        reject_btn = QtWidgets.QPushButton("✗")
        reject_btn.setToolTip("Reject suggestion")
        reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #da3633;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 12px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #f85149;
            }
        """)
        reject_btn.clicked.connect(self._hide_morpheus_suggestion)
        header_layout.addWidget(reject_btn)
        
        header_widget = QtWidgets.QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("border: none; background: transparent;")
        container_layout.addWidget(header_widget)
        
        # Original line (red background)
        original_label = QtWidgets.QLabel(f"− {original_line.strip()}")
        original_label.setStyleSheet("""
            background-color: rgba(255, 0, 0, 0.2);
            color: #ff6b6b;
            padding: 4px 8px;
            border-radius: 2px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10px;
            border: none;
        """)
        original_label.setWordWrap(False)
        container_layout.addWidget(original_label)
        
        # Suggested line (green background)
        suggestion_label = QtWidgets.QLabel(f"+ {suggestion.strip()}")
        suggestion_label.setStyleSheet("""
            background-color: rgba(0, 255, 65, 0.2);
            color: #00ff41;
            padding: 4px 8px;
            border-radius: 2px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10px;
            border: none;
        """)
        suggestion_label.setWordWrap(False)
        container_layout.addWidget(suggestion_label)
        
        layout.addWidget(container)
        
        # Position widget near the error line
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line_number - 1))
        rect = self.cursorRect(cursor)
        global_pos = self.mapToGlobal(rect.topLeft())
        
        self._morpheus_suggestion_widget.adjustSize()
        self._morpheus_suggestion_widget.move(global_pos.x() + 50, global_pos.y() - 10)
        self._morpheus_suggestion_widget.show()
    
    def _accept_morpheus_suggestion(self, suggestion, line_number):
        """Apply the Morpheus suggestion to the code, preserving indentation."""
        print(f"=" * 50)
        print(f"[APPLY] APPLYING SUGGESTION:")
        print(f"   THIS EDITOR ID: {id(self)}")
        print(f"   Line number from Problems window: {line_number}")
        print(f"   Morpheus suggestion: '{suggestion}'")
        
        # SIMPLE: Just use the line number directly - don't search!
        # The line_number comes from Problems window and is for THIS editor
        actual_line_number = line_number
        
        # Get current editor content
        code = self.toPlainText()
        lines = code.split('\n')
        
        # Validate line number is within bounds
        if actual_line_number < 1 or actual_line_number > len(lines):
            print(f"   [ERROR] Line {actual_line_number} is out of bounds (1-{len(lines)})")
            self._hide_morpheus_suggestion()
            return
        
        # Get the cursor for the line using 0-indexed block number
        block_index = actual_line_number - 1
        print(f"   Block index (0-indexed): {block_index}")
        
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(block_index))
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
        
        original_text = cursor.selectedText()
        print(f"   Line {actual_line_number} CURRENT content: '{original_text}'")
        
        # Calculate indentation from original line (count leading spaces/tabs)
        indent = len(original_text) - len(original_text.lstrip())
        indent_str = original_text[:indent]  # Preserve actual indent chars (spaces or tabs)
        print(f"   Indentation: {indent} chars")
        
        # Clean the suggestion - remove any leading/trailing whitespace
        clean_suggestion = suggestion.strip()
        print(f"   Clean suggestion: '{clean_suggestion}'")
        
        # Apply the original indentation to the cleaned suggestion
        indented_suggestion = indent_str + clean_suggestion
        print(f"   Final text: '{indented_suggestion}'")
        print(f"=" * 50)
        
        # Replace the line content (not including the newline)
        cursor.insertText(indented_suggestion)
        
        # Hide suggestion widget
        self._hide_morpheus_suggestion()
        
        # Show success message
        if hasattr(self.parent(), 'dock_manager'):
            main_window = self.parent()
            while main_window.parent():
                main_window = main_window.parent()
            if hasattr(main_window, 'dock_manager'):
                main_window.dock_manager.console.append_tagged("SUCCESS", 
                    "✓ Morpheus suggestion applied!", "#00ff41")
    
    def _hide_morpheus_suggestion(self):
        """Hide the Morpheus suggestion widget."""
        if self._morpheus_suggestion_widget:
            self._morpheus_suggestion_widget.hide()
            self._morpheus_suggestion_widget.deleteLater()
            self._morpheus_suggestion_widget = None
        self._current_suggestion_line = None
    
    def _generate_error_suggestion(self, error_message, line_number):
        """Generate a helpful suggestion based on the error message."""
        # Get the line content
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line_number - 1))
        line_text = cursor.block().text().strip()
        
        # Common error patterns and suggestions
        if "incomplete statement" in error_message.lower():
            if "def" in line_text:
                return "Add function name and parameters: <code>def function_name():</code>"
            elif "class" in line_text:
                return "Add class name: <code>class ClassName:</code>"
            elif "if" in line_text or "elif" in line_text:
                return "Add condition: <code>if condition:</code>"
            elif "for" in line_text:
                return "Add loop variable: <code>for item in iterable:</code>"
            elif "while" in line_text:
                return "Add condition: <code>while condition:</code>"
            elif "try" in line_text:
                return "Add code block after try:"
            elif "except" in line_text:
                return "Add exception type: <code>except ExceptionType:</code>"
        
        elif "invalid syntax" in error_message.lower():
            if ":" not in line_text and any(kw in line_text for kw in ["def", "class", "if", "for", "while", "elif", "else", "try", "except", "finally"]):
                return "Add colon (:) at the end of the line"
            elif line_text.count("(") != line_text.count(")"):
                return "Check for unmatched parentheses"
            elif line_text.count("[") != line_text.count("]"):
                return "Check for unmatched brackets"
            elif line_text.count("{") != line_text.count("}"):
                return "Check for unmatched braces"
        
        elif "expected" in error_message.lower():
            if ":" in error_message:
                return "Add colon (:) at the end of the control statement"
            elif "(" in error_message or ")" in error_message:
                return "Check parentheses - ensure they are properly matched"
        
        # Generic suggestion
        return "Check syntax and indentation on this line"