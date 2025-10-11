"""
AI Script Editor – Refactored Code Editor
Compatible with Maya 2020–2026 (PySide2/PySide6)
Supports inline AI ghost suggestions, linting, and Maya command autocorrect.
"""

import os, re, ast, threading, difflib
from PySide6 import QtCore, QtGui, QtWidgets
from .highlighter import PythonHighlighter


class CodeEditor(QtWidgets.QPlainTextEdit):
    """Advanced code editor with line numbers, ghost text and AI assist."""

    requestAICompletion = QtCore.Signal(str)   # emitted with context string
    lintProblemsFound = QtCore.Signal(list)    # emitted when linting issues found
    
    # Debugging signals
    breakpointToggled = QtCore.Signal(int, bool)  # line_number, is_set
    debugRequested = QtCore.Signal(str)           # file_path
    stepRequested = QtCore.Signal(str)            # step_type: 'over', 'into', 'out'

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
        
        # --- Hover tooltip functionality
        self.setMouseTracking(True)  # Enable mouse tracking for hover
        self._hover_timer = QtCore.QTimer()
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._show_hover_tooltip)
        self._hover_position = QtCore.QPoint()
        self._syntax_docs = self._load_syntax_documentation()
        
        # --- Indentation guides
        self._show_indent_guides = True  # Enable indentation guides
        self._tab_size = 4  # Default tab size for indentation calculation
        
        # --- Debugging system
        self._breakpoints = set()  # Set of line numbers with breakpoints
        self._current_debug_line = None  # Current line being debugged
        self._debug_mode = False  # Whether debugging is active
        self._debug_session = None  # Debug session object

    def _load_syntax_documentation(self):
        """Load comprehensive syntax documentation for Python and Maya/MEL."""
        return {
            # Python Keywords
            'def': 'Define a function\n\ndef function_name(parameters):\n    """Function body"""\n    return value',
            'class': 'Define a class\n\nclass ClassName(BaseClass):\n    """Class body"""\n    def __init__(self):',
            'if': 'Conditional statement\n\nif condition:\n    # code block\nelif other_condition:\n    # code block\nelse:\n    # default block',
            'elif': 'Else if - additional condition in if statement\n\nif condition:\n    pass\nelif other_condition:\n    # this block executes if other_condition is True',
            'else': 'Default case in if statement or exception handler\n\nif condition:\n    pass\nelse:\n    # executes when condition is False',
            'for': 'Loop over iterable objects\n\nfor item in iterable:\n    # process each item\n\nfor i in range(10):\n    # loop 10 times',
            'while': 'Loop while condition is True\n\nwhile condition:\n    # code block\n    # update condition to avoid infinite loop',
            'try': 'Exception handling block\n\ntry:\n    # risky code\nexcept Exception as e:\n    # handle error\nfinally:\n    # cleanup code',
            'except': 'Handle exceptions in try block\n\ntry:\n    risky_operation()\nexcept ValueError as e:\n    # handle ValueError\nexcept Exception as e:\n    # handle other errors',
            'finally': 'Code that always runs after try/except\n\ntry:\n    risky_code()\nexcept:\n    handle_error()\nfinally:\n    # always executes (cleanup)',
            'return': 'Return value from function\n\nreturn value  # exit function with value\nreturn  # exit function with None',
            'yield': 'Create generator function\n\ndef generator():\n    yield value  # pause and return value\n    yield another  # resume here next time',
            'import': 'Import modules or packages\n\nimport module_name\nfrom package import specific_item\nimport module as alias',
            'from': 'Import specific items from module\n\nfrom module import function\nfrom package import Class, function\nfrom . import relative_module',
            'as': 'Create alias for imported module\n\nimport numpy as np\nfrom collections import defaultdict as dd\nexcept ValueError as e:',
            'with': 'Context manager for resource handling\n\nwith open("file.txt") as f:\n    content = f.read()\n# file automatically closed',
            'lambda': 'Anonymous function\n\nlambda x: x * 2  # function that doubles input\nsorted(items, key=lambda x: x.name)',
            'global': 'Access global variable in function\n\nglobal variable_name\nvariable_name = new_value  # modifies global',
            'nonlocal': 'Access enclosing scope variable\n\ndef outer():\n    x = 1\n    def inner():\n        nonlocal x\n        x = 2  # modifies outer x',
            'pass': 'Null operation - placeholder\n\nif condition:\n    pass  # do nothing\n\nclass EmptyClass:\n    pass  # placeholder class',
            'break': 'Exit loop immediately\n\nfor item in items:\n    if condition:\n        break  # exit loop',
            'continue': 'Skip to next iteration\n\nfor item in items:\n    if skip_condition:\n        continue  # skip this iteration\n    process(item)',
            
            # Python Built-ins
            'print': 'Output text to console\n\nprint("Hello World")\nprint(variable, end="")\nprint(a, b, sep=", ")',
            'len': 'Get length of sequence\n\nlen("string")  # 6\nlen([1,2,3])  # 3\nlen({"a":1})  # 1',
            'range': 'Generate sequence of numbers\n\nrange(5)  # 0,1,2,3,4\nrange(1,6)  # 1,2,3,4,5\nrange(0,10,2)  # 0,2,4,6,8',
            'list': 'Create list from iterable\n\nlist()  # empty list\nlist("abc")  # ["a","b","c"]\nlist(range(3))  # [0,1,2]',
            'dict': 'Create dictionary\n\ndict()  # empty dict\ndict(a=1, b=2)  # {"a":1,"b":2}\ndict([("a",1),("b",2)])',
            'str': 'Convert to string\n\nstr(123)  # "123"\nstr([1,2])  # "[1, 2]"\nstr(True)  # "True"',
            'int': 'Convert to integer\n\nint("123")  # 123\nint(3.14)  # 3\nint("ff", 16)  # 255 (hex)',
            'float': 'Convert to floating point\n\nfloat("3.14")  # 3.14\nfloat(5)  # 5.0\nfloat("inf")  # infinity',
            'bool': 'Convert to boolean\n\nbool(1)  # True\nbool(0)  # False\nbool([])  # False\nbool([1])  # True',
            'type': 'Get object type\n\ntype(123)  # <class "int">\ntype("hi")  # <class "str">\ntype([])  # <class "list">',
            'isinstance': 'Check if object is instance of type\n\nisinstance(x, int)  # True if x is integer\nisinstance(x, (int,float))  # True if x is int or float',
            'hasattr': 'Check if object has attribute\n\nhasattr(obj, "method")  # True if obj.method exists\nhasattr(obj, "attribute")',
            'getattr': 'Get object attribute\n\ngetattr(obj, "attr")  # obj.attr\ngetattr(obj, "attr", default)  # with default value',
            'setattr': 'Set object attribute\n\nsetattr(obj, "name", value)  # obj.name = value\nsetattr(obj, attr_name, new_value)',
            'open': 'Open file for reading/writing\n\nopen("file.txt", "r")  # read mode\nopen("file.txt", "w")  # write mode\nopen("file.txt", "a")  # append mode',
            
            # Maya Python API
            'cmds': 'Maya Commands - Main Maya Python API\n\nimport maya.cmds as cmds\ncmds.polyCube()  # create cube\ncmds.move(0,5,0)  # move object',
            'polyCube': 'Create polygon cube\n\ncmds.polyCube()  # default cube\ncmds.polyCube(name="myCube", width=2, height=3, depth=4)',
            'polyPlane': 'Create polygon plane\n\ncmds.polyPlane()  # default plane\ncmds.polyPlane(name="ground", width=10, height=10)',
            'polySphere': 'Create polygon sphere\n\ncmds.polySphere()  # default sphere\ncmds.polySphere(name="ball", radius=2, subdivisions=20)',
            'move': 'Move objects in 3D space\n\ncmds.move(x, y, z)  # absolute position\ncmds.move(x, y, z, relative=True)  # relative movement',
            'rotate': 'Rotate objects\n\ncmds.rotate(x, y, z)  # absolute rotation\ncmds.rotate(45, 0, 0, relative=True)  # relative rotation',
            'scale': 'Scale objects\n\ncmds.scale(x, y, z)  # scale factors\ncmds.scale(2, 2, 2)  # double size\ncmds.scale(1, 2, 1)  # stretch Y',
            'select': 'Select objects in scene\n\ncmds.select("objectName")  # select by name\ncmds.select(clear=True)  # clear selection\ncmds.select(all=True)  # select all',
            'ls': 'List objects in scene\n\ncmds.ls()  # list all objects\ncmds.ls(selection=True)  # selected objects\ncmds.ls(type="transform")  # by type',
            'delete': 'Delete objects from scene\n\ncmds.delete("objectName")  # delete by name\ncmds.delete(cmds.ls(sl=True))  # delete selected',
            'duplicate': 'Duplicate objects\n\ncmds.duplicate()  # duplicate selected\ncmds.duplicate("objectName", name="newName")',
            'group': 'Group objects together\n\ncmds.group()  # group selected objects\ncmds.group("obj1", "obj2", name="myGroup")',
            'parent': 'Parent objects\n\ncmds.parent("child", "parent")  # make child under parent\ncmds.parent("obj", world=True)  # unparent to world',
            'getAttr': 'Get attribute value\n\ncmds.getAttr("object.attribute")  # get value\ncmds.getAttr("pCube1.translateX")  # get X position',
            'setAttr': 'Set attribute value\n\ncmds.setAttr("object.attribute", value)  # set value\ncmds.setAttr("pCube1.translateY", 5)  # set Y position',
            'connectAttr': 'Connect attributes\n\ncmds.connectAttr("source.attr", "dest.attr")  # connect attributes\ncmds.connectAttr("locator1.tx", "cube1.rx")',
            'listConnections': 'List attribute connections\n\ncmds.listConnections("object.attr")  # list connections\ncmds.listConnections("pCube1", source=True, destination=False)',
            
            # Maya MEL Keywords  
            'global': 'MEL: Declare global variable\n\nglobal proc myProc() { }\nglobal string $myVar;\nglobal float $values[];',
            'proc': 'MEL: Define procedure (function)\n\nproc myProcedure() {\n    // code here\n}\n\nproc string getName() {\n    return "name";\n}',
            'string': 'MEL: String data type\n\nstring $name = "Maya";\nstring $path = `workspace -query -rootDirectory`;\nstring $items[];',
            'int': 'MEL: Integer data type\n\nint $count = 10;\nint $numbers[] = {1, 2, 3, 4};\nint $result = $a + $b;',
            'float': 'MEL: Floating point data type\n\nfloat $value = 3.14;\nfloat $position[] = {0.0, 1.5, -2.3};\nfloat $time = `currentTime -query`;',
            'vector': 'MEL: Vector data type (3 floats)\n\nvector $pos = <<1.0, 2.0, 3.0>>;\nvector $normal = unit($pos);\nfloat $x = $pos.x;',
            
            # PySide6/Qt
            'QWidget': 'Base class for all UI objects\n\nfrom PySide6.QtWidgets import QWidget\nwidget = QWidget()\nwidget.show()',
            'QMainWindow': 'Main application window\n\nfrom PySide6.QtWidgets import QMainWindow\nwindow = QMainWindow()\nwindow.setCentralWidget(widget)',
            'QVBoxLayout': 'Vertical box layout\n\nlayout = QVBoxLayout()\nlayout.addWidget(widget1)\nlayout.addWidget(widget2)',
            'QHBoxLayout': 'Horizontal box layout\n\nlayout = QHBoxLayout()\nlayout.addWidget(widget1)\nlayout.addWidget(widget2)',
            'QPushButton': 'Clickable button widget\n\nbutton = QPushButton("Click Me")\nbutton.clicked.connect(my_function)\nlayout.addWidget(button)',
            'QLabel': 'Text display widget\n\nlabel = QLabel("Hello World")\nlabel.setText("New Text")\nlabel.setStyleSheet("color: blue;")',
            'QLineEdit': 'Single line text input\n\nedit = QLineEdit()\nedit.setText("default text")\ntext = edit.text()',
            'Signal': 'Qt signal for communication\n\nfrom PySide6.QtCore import Signal\nclass MyClass(QObject):\n    mySignal = Signal(str)',
            'Slot': 'Qt slot decorator\n\nfrom PySide6.QtCore import Slot\n@Slot()\ndef my_slot(self):\n    # slot function',
            
            # Common Patterns
            '__init__': 'Class constructor method\n\nclass MyClass:\n    def __init__(self, param):\n        self.param = param\n        # initialization code',
            '__str__': 'String representation method\n\ndef __str__(self):\n    return f"MyClass({self.param})"\n# Called by str() and print()',
            '__repr__': 'Developer string representation\n\ndef __repr__(self):\n    return f"MyClass(param={self.param!r})"\n# Called by repr() and debugger',
            'self': 'Reference to current instance\n\nclass MyClass:\n    def method(self):\n        self.attribute = value\n        return self.other_method()',
            'cls': 'Reference to current class (classmethod)\n\n@classmethod\ndef create(cls, data):\n    instance = cls()\n    return instance'
        }

        # --- Ghost text overlay
        self.ghost_label = QtWidgets.QLabel(self)
        self.ghost_label.setStyleSheet("color:#777;font-style:italic;")
        self.ghost_label.hide()
        
        # --- VS Code style inline search widget
        self.search_widget = None
        self._create_search_widget()
        
        # --- Error tracking for line numbers
        self._error_lines = set()  # Track lines with errors

        # --- Timers and thread control
        self._typing_timer = QtCore.QTimer()
        self._typing_timer.setInterval(1000)
        self._typing_timer.setSingleShot(True)
        self._typing_timer.timeout.connect(self._trigger_ai)

        self._last_ai_request = ""
        self._lint_thread = None

        # --- Consolidated text change handler
        self.textChanged.connect(self._on_text_changed_unified)

        # --- Suggestion buffer
        self._ghost_text = ""
        self._stop_lint_flag = threading.Event()
        
        # --- Autocomplete setup
        self._completer = None
        self._setup_autocomplete()
        
        # --- Ensure line numbers are initialized
        QtCore.QTimer.singleShot(100, self._initialize_display)

    def _on_text_changed_unified(self):
        """Unified handler for all text change events."""        
        # Call all the handlers that were previously connected separately
        try:
            self.update_error_highlights()
        except Exception as e:
            print(f"[ERROR] update_error_highlights failed: {e}")
            
        try:
            self._on_text_changed()
        except Exception as e:
            print(f"[ERROR] _on_text_changed failed: {e}")
            
        try:
            self._schedule_lint()
        except Exception as e:
            print(f"[ERROR] _schedule_lint failed: {e}")
            
        # Update indentation guides when text changes
        if hasattr(self, '_show_indent_guides') and self._show_indent_guides:
            self.update()  # Trigger repaint to update indentation guides

    def _initialize_display(self):
        """Initialize display elements after widget construction."""
        self._update_number_area_width()
        self.number_area.update()
        self.number_area.repaint()  # Force immediate repaint
        self._highlight_current_line()
        
        # Schedule another update to ensure visibility  
        QtCore.QTimer.singleShot(100, self._refresh_display)
        
    def _refresh_display(self):
        """Additional display refresh for proper initialization."""
        if hasattr(self, 'number_area') and self.number_area:
            self.number_area.update()
            self.number_area.repaint()

    # ============================================================
    #  Autocomplete Setup
    # ============================================================
    def _setup_autocomplete(self):
        """Setup Python autocomplete with Maya commands."""
        # Python built-in keywords and functions
        python_keywords = [
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 
            'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'pass',
            'break', 'continue', 'True', 'False', 'None', 'and', 'or', 'not', 'in',
            'is', 'lambda', 'global', 'nonlocal', 'assert', 'del', 'raise'
        ]
        
        # Python built-in functions
        python_builtins = [
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'tuple', 'set',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed',
            'sum', 'min', 'max', 'abs', 'round', 'type', 'isinstance', 'hasattr',
            'getattr', 'setattr', 'dir', 'vars', 'open', 'input'
        ]
        
        # Common Maya commands
        maya_commands = [
            'cmds.polyCube', 'cmds.polySphere', 'cmds.polyCylinder', 'cmds.polyPlane',
            'cmds.move', 'cmds.rotate', 'cmds.scale', 'cmds.duplicate', 'cmds.delete',
            'cmds.select', 'cmds.ls', 'cmds.listRelatives', 'cmds.parent', 'cmds.group',
            'cmds.createNode', 'cmds.connectAttr', 'cmds.disconnectAttr', 'cmds.getAttr',
            'cmds.setAttr', 'cmds.addAttr', 'cmds.deleteAttr', 'cmds.hide', 'cmds.showHidden',
            'cmds.xform', 'cmds.makeIdentity', 'cmds.freeze', 'cmds.refresh', 'cmds.undo',
            'cmds.redo', 'cmds.file', 'cmds.newFile', 'cmds.openFile', 'cmds.saveFile'
        ]
        
        # Combine all completions
        all_completions = python_keywords + python_builtins + maya_commands
        
        # Create completer
        self._completer = QtWidgets.QCompleter(all_completions)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.activated.connect(self._insert_completion)
        
        # Style the completer popup
        popup = self._completer.popup()
        popup.setStyleSheet("""
            QListView {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
                font-family: Consolas, monospace;
                font-size: 10pt;
            }
            QListView::item {
                padding: 4px;
                border-bottom: 1px solid #3e3e42;
            }
            QListView::item:selected {
                background-color: #094771;
                color: white;
            }
        """)
    
    def _insert_completion(self, completion):
        """Insert the selected completion."""
        cursor = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        cursor.insertText(completion[-extra:])
        self.setTextCursor(cursor)
    
    def _text_under_cursor(self):
        """Get the word under cursor for completion."""
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    # ============================================================
    #  Line Numbers
    # ============================================================
    def _update_number_area_width(self, _=None):
        digits = len(str(max(1, self.blockCount())))
        fm = self.fontMetrics()
        
        # Ensure minimum width for new editors (at least 3 digits worth of space)
        min_digits = max(3, digits)
        
        # Increased margin to ensure line numbers are fully visible
        # Extra space for error indicators (red dots) and padding
        width = 25 + fm.horizontalAdvance('9') * (min_digits + 1)
        self.setViewportMargins(width, 0, 0, 0)
        
        # Update the line number area widget geometry
        if hasattr(self, 'number_area'):
            cr = self.contentsRect()
            self.number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), width - 5, cr.height()))

    def _ensure_line_numbers_visible(self):
        """Ensure line numbers are properly visible, especially for new tabs."""
        self._update_number_area_width()
        if hasattr(self, 'number_area'):
            self.number_area.update()

    def _update_number_area(self, rect, dy):
        if dy:
            self.number_area.scroll(0, dy)
        else:
            self.number_area.update(0, rect.y(), self.number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_number_area_width()

    def showEvent(self, event):
        """Ensure line numbers are properly displayed when widget is shown."""
        super().showEvent(event)
        # Force line number area update when editor becomes visible
        QtCore.QTimer.singleShot(10, self._ensure_line_numbers_visible)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Handle line number area resize
        cr = self.contentsRect()
        self.number_area.setGeometry(QtCore.QRect(
            cr.left(), cr.top(),
            self._number_area_width(), cr.height()
        ))
        # Handle search widget positioning
        self._position_search_widget()

    def _number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        fm = self.fontMetrics()
        return 10 + fm.horizontalAdvance('9') * digits

    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw indentation guides
        if self._show_indent_guides:
            self._draw_indentation_guides(event)
        
        # Draw ghost text overlay
        if self._ghost_text:
            painter = QtGui.QPainter(self.viewport())
            cursor_rect = self.cursorRect()
            painter.setPen(QtGui.QColor("#777"))
            painter.setFont(self.font())
            painter.drawText(
                cursor_rect.topRight() + QtCore.QPoint(4, self.fontMetrics().ascent()),
                self._ghost_text
            )
            painter.end()

    def _draw_indentation_guides(self, event):
        """Draw vertical indentation guide lines similar to VS Code."""
        painter = QtGui.QPainter(self.viewport())
        
        # Use a subtle color for indentation guides
        guide_color = QtGui.QColor("#404040")  # Subtle gray
        painter.setPen(QtGui.QPen(guide_color, 1, QtCore.Qt.DotLine))
        
        # Get font metrics for character width calculation
        fm = self.fontMetrics()
        char_width = fm.horizontalAdvance(' ')
        indent_width = char_width * self._tab_size
        
        # Get the visible area and content offset
        viewport_rect = event.rect()
        content_offset = self.contentOffset()
        
        # Calculate the first visible block
        first_visible_block = self.firstVisibleBlock()
        if not first_visible_block.isValid():
            painter.end()
            return
        
        # Get line number area width to offset the guides
        line_number_width = self._calculate_line_number_area_width()
        
        # Collect all indentation levels in visible area
        visible_indents = set()
        block = first_visible_block
        
        # First pass: collect all indentation levels
        while block.isValid():
            block_rect = self.blockBoundingGeometry(block).translated(content_offset)
            
            if block_rect.top() > viewport_rect.bottom():
                break
                
            if block_rect.bottom() >= viewport_rect.top():
                line_text = block.text()
                if line_text.strip():  # Only process non-empty lines
                    indent_level = self._get_indentation_level(line_text)
                    if indent_level > 0:
                        # Add all levels up to this indentation
                        for level in range(1, indent_level + 1):
                            visible_indents.add(level)
            
            block = block.next()
        
        # Second pass: draw continuous vertical lines
        if visible_indents:
            viewport_top = viewport_rect.top()
            viewport_bottom = viewport_rect.bottom()
            
            # Draw each indentation level as a continuous line
            for level in sorted(visible_indents):
                x_pos = line_number_width + (level * indent_width)
                
                # Draw continuous vertical line for this indentation level
                line_start = QtCore.QPoint(int(x_pos), viewport_top)
                line_end = QtCore.QPoint(int(x_pos), viewport_bottom)
                painter.drawLine(line_start, line_end)
        
        painter.end()
    
    def _get_indentation_level(self, line_text):
        """Calculate the indentation level of a line."""
        if not line_text:
            return 0
            
        # Count leading spaces and tabs
        spaces = 0
        for char in line_text:
            if char == ' ':
                spaces += 1
            elif char == '\t':
                spaces += self._tab_size  # Convert tabs to spaces
            else:
                break
        
        # Calculate indentation level
        return spaces // self._tab_size
    
    def set_indentation_guides_visible(self, visible):
        """Toggle visibility of indentation guides."""
        self._show_indent_guides = visible
        self.update()  # Trigger repaint
    
    def set_tab_size(self, size):
        """Set the tab size for indentation calculation."""
        self._tab_size = max(1, size)  # Ensure positive tab size
        self.update()  # Trigger repaint

    # ============================================================
    #  Debugging and Breakpoints
    # ============================================================
    
    def toggle_breakpoint(self, line_number):
        """Toggle breakpoint on the specified line."""
        if line_number in self._breakpoints:
            self._breakpoints.remove(line_number)
            self.breakpointToggled.emit(line_number, False)
        else:
            self._breakpoints.add(line_number)
            self.breakpointToggled.emit(line_number, True)
        
        # Update line number area to show/hide breakpoint
        self.number_area.update()
    
    def set_breakpoint(self, line_number, enabled=True):
        """Set or clear a breakpoint on the specified line."""
        if enabled:
            if line_number not in self._breakpoints:
                self._breakpoints.add(line_number)
                self.breakpointToggled.emit(line_number, True)
        else:
            if line_number in self._breakpoints:
                self._breakpoints.remove(line_number)
                self.breakpointToggled.emit(line_number, False)
        
        self.number_area.update()
    
    def get_breakpoints(self):
        """Get all breakpoint line numbers."""
        return sorted(list(self._breakpoints))
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints."""
        for line_num in list(self._breakpoints):
            self.breakpointToggled.emit(line_num, False)
        self._breakpoints.clear()
        self.number_area.update()
    
    def set_current_debug_line(self, line_number):
        """Set the current line being debugged (yellow arrow)."""
        self._current_debug_line = line_number
        self.number_area.update()
        
        # Scroll to make the debug line visible
        if line_number:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
            for _ in range(line_number - 1):
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Down)
            self.setTextCursor(cursor)
            self.centerCursor()
    
    def clear_debug_line(self):
        """Clear the current debug line indicator."""
        self._current_debug_line = None
        self.number_area.update()
    
    def start_debug_session(self, session):
        """Start a debugging session."""
        self._debug_session = session
        self._debug_mode = True
    
    def stop_debug_session(self):
        """Stop the current debugging session."""
        self._debug_session = None
        self._debug_mode = False
        self.clear_debug_line()
    
    def is_debugging(self):
        """Check if currently in debug mode."""
        return self._debug_mode

    def _highlight_current_line(self):
        sel = QtWidgets.QTextEdit.ExtraSelection()
        line_color = QtGui.QColor("#2A2D2E")
        sel.format.setBackground(line_color)
        sel.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel])

    def highlight_replacement(self, start_pos, end_pos, duration=3000):
        """Highlight a text replacement with green background for specified duration."""
        cursor = QtGui.QTextCursor(self.document())
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        
        # Create highlight selection
        sel = QtWidgets.QTextEdit.ExtraSelection()
        sel.format.setBackground(QtGui.QColor("#2d5a1e"))  # Green background
        sel.format.setForeground(QtGui.QColor("#ffffff"))  # White text
        sel.cursor = cursor
        
        # Apply highlight
        current_selections = self.extraSelections()
        current_selections.append(sel)
        self.setExtraSelections(current_selections)
        
        # Remove highlight after duration
        QtCore.QTimer.singleShot(duration, lambda: self._remove_highlight(sel))
    
    def highlight_error(self, line_number, message="", duration=5000):
        """Highlight a line with error styling and optional message."""
        cursor = QtGui.QTextCursor(self.document())
        cursor.movePosition(QtGui.QTextCursor.Start)
        
        # Move to specific line
        for _ in range(line_number - 1):
            cursor.movePosition(QtGui.QTextCursor.Down)
        
        # Select the entire line
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        
        # Create error highlight
        sel = QtWidgets.QTextEdit.ExtraSelection()
        sel.format.setBackground(QtGui.QColor("#5d1a1a"))  # Red background
        sel.format.setForeground(QtGui.QColor("#ffcdd2"))  # Light red text
        sel.format.setUnderlineColor(QtGui.QColor("#f44336"))  # Red underline
        sel.format.setUnderlineStyle(QtGui.QTextCharFormat.UnderlineStyle.WaveUnderline)
        sel.cursor = cursor
        
        # Apply highlight
        current_selections = self.extraSelections()
        current_selections.append(sel)
        self.setExtraSelections(current_selections)
        
        # Show tooltip if message provided
        if message:
            self.setToolTip(f"Line {line_number}: {message}")
            # Position cursor at the error line
            self.setTextCursor(cursor)
        
        # Remove highlight after duration
        QtCore.QTimer.singleShot(duration, lambda: self._remove_highlight(sel))
    
    def _remove_highlight(self, selection_to_remove):
        """Remove a specific highlight selection."""
        current_selections = self.extraSelections()
        if selection_to_remove in current_selections:
            current_selections.remove(selection_to_remove)
            self.setExtraSelections(current_selections)
    
    def clear_all_highlights(self):
        """Clear all extra highlights except current line."""
        self._highlight_current_line()  # Keep only current line highlight
    
    def clear_error_highlights(self):
        """Clear only error highlights, keep other highlights."""
        # Only clear if we actually have errors to clear
        if not self._error_lines:
            return
            
        current_selections = self.extraSelections()
        # Keep only non-error selections (current line highlight)
        non_error_selections = []
        for sel in current_selections:
            # Check if this is the current line highlight (different background color)
            bg_color = sel.format.background().color().name().lower()
            if bg_color == "#2a2d2e" or not sel.format.hasProperty(QtGui.QTextFormat.Property.TextUnderlineStyle):
                non_error_selections.append(sel)
        
        self.setExtraSelections(non_error_selections)
        # Clear tooltips only if we had errors
        self.setToolTip("")
        
        # Clear error line tracking
        self._error_lines.clear()
        self.number_area.update()  # Refresh line numbers to remove error dots
    
    def check_syntax_errors(self, emit_signal=True):
        """Check for syntax errors and highlight them VS Code style - enhanced to catch multiple errors."""
        text = self.toPlainText()
        print(f"[DEBUG] check_syntax_errors called with {len(text)} chars")
        
        if not text.strip():
            print("[DEBUG] Empty text, clearing highlights")
            self.clear_error_highlights()
            if emit_signal:
                self.lintProblemsFound.emit([])
            return []
        
        errors = []
        lines = text.splitlines()
        print(f"[DEBUG] Checking {len(lines)} lines for syntax errors")
        
        # First try compiling the whole text to catch major syntax errors
        try:
            compile(text, '<editor>', 'exec')
        except SyntaxError as e:
            print(f"[DEBUG] Main compile error: {e.msg} at line {e.lineno}")
            if e.lineno and e.lineno <= len(lines):
                error_info = {
                    'line': e.lineno,
                    'column': e.offset or 1,
                    'message': e.msg or 'Syntax error',
                    'type': 'SyntaxError',
                    'severity': 'error'
                }
                errors.append(error_info)
                self._highlight_syntax_error(e.lineno, e.offset or 1, e.msg or 'Syntax error')
        
        # Rely only on main Python compiler - no individual line checking
        # This prevents all false positives from line-by-line validation
        print(f"[DEBUG] Using only main Python compiler for error detection")
        
        print(f"[DEBUG] Total errors found: {len(errors)}")
        
        # Clear highlights if no errors
        if not errors:
            self.clear_error_highlights()
        
        # Disable line-by-line checking to avoid false positives with PEP 8 style code
        # Python's main compiler handles all real syntax errors properly
        print(f"[DEBUG] Skipping line-by-line validation to prevent false positives")
        
        # Remove duplicate errors for same line
        unique_errors = []
        seen_lines = set()
        for error in errors:
            if error['line'] not in seen_lines:
                unique_errors.append(error)
                seen_lines.add(error['line'])
        
        if emit_signal:
            self.lintProblemsFound.emit(unique_errors)
        return unique_errors
        
    def _check_line_syntax_issues(self, line, line_num, existing_errors):
        """Check individual line for syntax issues."""
        # Don't skip - we want to detect multiple types of errors on the same line
        found_error = False
                
        # Check for unmatched brackets/parentheses
        open_chars = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for i, char in enumerate(line):
            if char in open_chars:
                stack.append((char, i))
            elif char in open_chars.values():
                if not stack:
                    error_info = {
                        'line': line_num,
                        'column': i + 1,
                        'message': f"Unmatched closing '{char}'",
                        'type': 'SyntaxError',
                        'severity': 'error'
                    }
                    existing_errors.append(error_info)
                    self._highlight_syntax_error(line_num, i + 1, f"Unmatched closing '{char}'")
                    return True
                else:
                    expected = open_chars[stack[-1][0]]
                    if char != expected:
                        error_info = {
                            'line': line_num,
                            'column': i + 1,
                            'message': f"Expected '{expected}', found '{char}'",
                            'type': 'SyntaxError',
                            'severity': 'error'
                        }
                        existing_errors.append(error_info)
                        self._highlight_syntax_error(line_num, i + 1, f"Expected '{expected}', found '{char}'")
                        return True
                    stack.pop()
        
        # Check for unclosed brackets
        if stack:
            char, pos = stack[-1]
            error_info = {
                'line': line_num,
                'column': pos + 1,
                'message': f"Unclosed '{char}'",
                'type': 'SyntaxError',
                'severity': 'error'
            }
            existing_errors.append(error_info)
            self._highlight_syntax_error(line_num, pos + 1, f"Unclosed '{char}'")
            found_error = True
        
        # Only focus on bracket matching - let main compiler handle other syntax errors
        
        return found_error
    
    def _is_valid_statement(self, line_stripped):
        """Check if a line is a valid Python statement - very conservative to avoid false positives."""
        # Empty lines and comments are always valid
        if not line_stripped or line_stripped.startswith('#'):
            return True
        
        # Only flag very obvious nonsense - single random words
        if ' ' not in line_stripped and '(' not in line_stripped and '=' not in line_stripped and '.' not in line_stripped:
            # Single word that might be nonsense
            obvious_nonsense = ['asd', 'asdf', 'qwe', 'qwer', 'xyz', 'sad', 'ddd', 'hhh', 'kkk', 'asdsad', 'jasdj']
            if line_stripped.lower() in obvious_nonsense:
                return False
        
        # Everything else is considered potentially valid - let Python compiler handle real errors
        return True

    def _highlight_syntax_error(self, line_number, column, message):
        """Highlight syntax error with VS Code style red wavy underline."""
        cursor = QtGui.QTextCursor(self.document())
        cursor.movePosition(QtGui.QTextCursor.Start)
        
        # Move to the specific line
        for _ in range(line_number - 1):
            cursor.movePosition(QtGui.QTextCursor.Down)
        
        # Move to the specific column if available
        if column > 1:
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, column - 1)
        
        # Select the word or character at error position
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        if not cursor.hasSelection():
            # If no word, select the character
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 1)
        
        # Create VS Code style error highlight
        sel = QtWidgets.QTextEdit.ExtraSelection()
        sel.format.setUnderlineColor(QtGui.QColor("#f14c4c"))  # VS Code red
        sel.format.setUnderlineStyle(QtGui.QTextCharFormat.UnderlineStyle.WaveUnderline)
        sel.format.setBackground(QtGui.QColor("rgba(244, 76, 76, 0.1)"))  # Very subtle red background
        sel.cursor = cursor
        
        # Apply the highlight
        current_selections = self.extraSelections()
        current_selections.append(sel)
        self.setExtraSelections(current_selections)
        
        # Set tooltip with error message
        self.setToolTip(f"Line {line_number}: {message}")
        
        # Track error line for red dot display
        self._error_lines.add(line_number)
        self.number_area.update()  # Refresh line numbers to show error dots
    
    def _create_search_widget(self):
        """Create VS Code style inline search widget."""
        self.search_widget = QtWidgets.QWidget(self)
        self.search_widget.setStyleSheet("""
            QWidget {
                background: #252526;
                border: 1px solid #3e3e42;
                border-radius: 4px;
            }
            QLineEdit {
                background: #3c3c3c;
                border: 1px solid #464647;
                color: #cccccc;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QLineEdit:focus { border-color: #007acc; }
            QPushButton {
                background: #3c3c3c;
                border: 1px solid #464647;
                color: #cccccc;
                padding: 4px 8px;
                border-radius: 3px;
                min-width: 24px;
            }
            QPushButton:hover { background: #464647; }
            QPushButton:pressed { background: #007acc; }
        """)
        
        layout = QtWidgets.QHBoxLayout(self.search_widget)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)
        
        # Search input
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Find...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._find_next)
        layout.addWidget(self.search_input)
        
        # Navigation buttons
        prev_btn = QtWidgets.QPushButton("↑")
        prev_btn.setToolTip("Previous (Shift+Enter)")
        prev_btn.clicked.connect(self._find_previous)
        layout.addWidget(prev_btn)
        
        next_btn = QtWidgets.QPushButton("↓")
        next_btn.setToolTip("Next (Enter)")
        next_btn.clicked.connect(self._find_next)
        layout.addWidget(next_btn)
        
        # Close button
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setToolTip("Close (Escape)")
        close_btn.clicked.connect(self._hide_search)
        layout.addWidget(close_btn)
        
        # Position and hide initially
        self.search_widget.hide()
        self._position_search_widget()
        
    def _position_search_widget(self):
        """Position search widget at top-right like VS Code."""
        if self.search_widget:
            self.search_widget.resize(300, 32)
            self.search_widget.move(self.width() - 320, 10)
            
    def show_search(self):
        """Show the inline search widget (called by Ctrl+F)."""
        self.search_widget.show()
        self._position_search_widget()
        self.search_input.setFocus()
        self.search_input.selectAll()
        
    def _hide_search(self):
        """Hide the search widget."""
        self.search_widget.hide()
        self.setFocus()
        
    def _on_search_text_changed(self, text):
        """Handle search text changes."""
        if text:
            self._find_next(wrap=False)
            
    def _find_next(self, wrap=True):
        """Find next occurrence of search text."""
        text = self.search_input.text()
        if not text:
            return
            
        cursor = self.textCursor()
        found_cursor = self.document().find(text, cursor)
        
        if found_cursor.isNull() and wrap:
            # Wrap around to beginning
            found_cursor = self.document().find(text)
            
        if not found_cursor.isNull():
            self.setTextCursor(found_cursor)
            
    def _find_previous(self):
        """Find previous occurrence of search text."""
        text = self.search_input.text()
        if not text:
            return
            
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        found_cursor = self.document().find(text, cursor, QtGui.QTextDocument.FindBackward)
        
        if not found_cursor.isNull():
            self.setTextCursor(found_cursor)
            
    def keyPressEvent(self, event):
        """Handle key press events for search functionality."""
        if event.key() == QtCore.Qt.Key_F and event.modifiers() == QtCore.Qt.ControlModifier:
            self.show_search()
            event.accept()
            return
        elif event.key() == QtCore.Qt.Key_Escape and self.search_widget.isVisible():
            self._hide_search()
            event.accept()
            return
            
        super().keyPressEvent(event)
    
    def update_error_highlights(self):
        """Update error highlights when text changes."""
        # Use a timer to avoid checking on every keystroke
        if not hasattr(self, '_error_check_timer'):
            self._error_check_timer = QtCore.QTimer()
            self._error_check_timer.setSingleShot(True)
            self._error_check_timer.timeout.connect(self._delayed_syntax_check)
        
        # Restart timer (debounce) - use shorter delay for testing
        self._error_check_timer.start(500)  # Check after 0.5 seconds of inactivity
        
    def _delayed_syntax_check(self):
        """Perform syntax check after delay."""
        try:
            print("[DEBUG] Running delayed syntax check")
            result = self.check_syntax_errors(emit_signal=True)
            print(f"[DEBUG] Syntax check found {len(result)} errors")
        except Exception as e:
            print(f"[ERROR] Syntax check failed: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    #  Typing / AI Triggering
    # ============================================================
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        # Handle autocomplete
        if self._completer and self._completer.popup().isVisible():
            # Accept completion ONLY on Tab
            if e.key() == QtCore.Qt.Key.Key_Tab:
                # Get current selection and insert it
                current = self._completer.popup().currentIndex()
                if current.isValid():
                    completion = self._completer.completionModel().data(current)
                    self._insert_completion(completion)
                    self._completer.popup().hide()
                    return
            
            # Enter/Return should close popup and create new line
            if e.key() in (QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return):
                self._completer.popup().hide()
                # Let the event continue to create new line
            
            # Keys that should close the popup
            if e.key() in (QtCore.Qt.Key.Key_Escape, QtCore.Qt.Key.Key_Backtab):
                self._completer.popup().hide()
                e.ignore()
                return
        
        # Accept or clear ghost suggestion
        if e.key() == QtCore.Qt.Key.Key_Tab and self._ghost_text:
            self._accept_ghost()
            return
        if e.key() == QtCore.Qt.Key.Key_Escape and self._ghost_text:
            self._ghost_text = ""
            self.viewport().update()
            return

        # Manual autocomplete trigger (Ctrl + Space)
        if e.key() == QtCore.Qt.Key.Key_Space and e.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self._trigger_autocomplete()
            return

        super().keyPressEvent(e)
        self._typing_timer.start()
        
        # Auto-trigger autocomplete on typing
        if e.text().isalpha() or e.text() == '.':
            self._trigger_autocomplete()
        
        # Trigger real-time error checking for certain keys
        if e.key() in (QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Colon, 
                       QtCore.Qt.Key.Key_ParenRight, QtCore.Qt.Key.Key_BracketRight, 
                       QtCore.Qt.Key.Key_BraceRight):
            self.update_error_highlights()

        # Manual AI inline trigger (Ctrl + Shift + Space)
        if (e.key() == QtCore.Qt.Key.Key_Space and 
            e.modifiers() == (QtCore.Qt.KeyboardModifier.ControlModifier | QtCore.Qt.KeyboardModifier.ShiftModifier)):
            ctx = self._get_context()
            if hasattr(self.parent(), "copilot"):
                self.parent().copilot.send_prompt("Continue this code snippet", context=ctx)
            return
    
    def _trigger_autocomplete(self):
        """Trigger autocomplete popup."""
        if not self._completer:
            return
            
        completion_prefix = self._text_under_cursor()
        if completion_prefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completion_prefix)
            popup = self._completer.popup()
            popup.setCurrentIndex(self._completer.completionModel().index(0, 0))
        
        if len(completion_prefix) >= 1:  # Show after 1 character
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(self._completer.popup().sizeHintForColumn(0) 
                                + self._completer.popup().verticalScrollBar().sizeHint().width())
            self._completer.complete(cursor_rect)

    def _on_text_changed(self):
        self._typing_timer.start()
        self._stop_lint_flag.set()  # cancel any old lint thread

    def _trigger_ai(self):
        text = self._get_context()
        if not text.strip():
            return
        if text == self._last_ai_request:
            return
        self._last_ai_request = text
        self.requestAICompletion.emit(text)

    def show_ghost_text(self, suggestion: str):
        self._ghost_text = suggestion.strip().replace("\n", " ")
        self.viewport().update()

    def _accept_ghost(self):
        if not self._ghost_text:
            return
        cursor = self.textCursor()
        cursor.insertText(self._ghost_text)
        self._ghost_text = ""
        self.viewport().update()

    # ============================================================
    #  Hover Tooltip Functionality
    # ============================================================
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover tooltips."""
        super().mouseMoveEvent(event)
        
        # Store hover position and start timer for tooltip
        self._hover_position = event.pos()
        self._hover_timer.stop()
        self._hover_timer.start(800)  # 800ms delay before showing tooltip
    
    def leaveEvent(self, event):
        """Hide tooltip when mouse leaves editor."""
        super().leaveEvent(event)
        self._hover_timer.stop()
        QtWidgets.QToolTip.hideText()
    
    def _show_hover_tooltip(self):
        """Show tooltip with syntax information at hover position."""
        # Get cursor position from mouse coordinates
        cursor_at_mouse = self.cursorForPosition(self._hover_position)
        cursor_pos = cursor_at_mouse.position()
        
        # Get the word under mouse cursor
        word_info = self._get_word_at_position(cursor_pos)
        if not word_info:
            return
            
        word, start_pos, end_pos = word_info
        
        # First try to get function signature if applicable
        signature_info = self._get_function_signature_at_cursor(cursor_pos)
        tooltip_text = signature_info if signature_info else self._get_syntax_tooltip(word)
        
        if tooltip_text:
            # Convert position to global coordinates for tooltip
            global_pos = self.mapToGlobal(self._hover_position)
            
            # Style the tooltip to match VS Code appearance
            styled_tooltip = self._style_tooltip(word, tooltip_text)
            QtWidgets.QToolTip.showText(global_pos, styled_tooltip, self)
    
    def _get_word_at_position(self, position):
        """Get the word and its boundaries at the given text position."""
        cursor = self.textCursor()
        cursor.setPosition(position)
        
        # Select the word under cursor
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        
        if cursor.hasSelection():
            word = cursor.selectedText()
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            
            # Only return if it's a valid identifier-like word
            if word and (word.isalpha() or '_' in word or word.replace('_', '').replace('.', '').isalnum()):
                return word, start_pos, end_pos
        
        return None
    
    def _get_function_signature_at_cursor(self, cursor_pos):
        """Try to get function signature if cursor is on a function definition."""
        cursor = self.textCursor()
        cursor.setPosition(cursor_pos)
        
        # Get the current line
        block = cursor.block()
        line_text = block.text().strip()
        
        # Check if it's a function definition
        if line_text.startswith('def ') and '(' in line_text:
            # Extract function signature
            if ')' in line_text:
                signature = line_text[line_text.find('def '):line_text.find(')')+1]
                return f"Function definition:\n{signature}"
        elif line_text.startswith('class ') and ':' in line_text:
            # Class definition
            class_def = line_text[:line_text.find(':')]
            return f"Class definition:\n{class_def}"
        
        return None
    
    def _get_syntax_tooltip(self, word):
        """Get tooltip text for a given word/syntax element."""
        # Direct lookup in documentation
        if word in self._syntax_docs:
            return self._syntax_docs[word]
        
        # Detect current language based on highlighter
        is_mel = self._is_mel_context()
        
        # Language-specific lookups
        if is_mel:
            return self._get_mel_tooltip(word)
        else:
            return self._get_python_tooltip(word)
    
    def _is_mel_context(self):
        """Check if current editor is in MEL mode."""
        from .highlighter import MELHighlighter
        return isinstance(self.highlighter, MELHighlighter)
    
    def _get_mel_tooltip(self, word):
        """Get MEL-specific tooltip information."""
        # MEL variable indicators
        if word.startswith('$'):
            return f"MEL variable: {word}\n\nMEL variables start with $ symbol\nExample: string $myVar = \"value\";"
        
        # MEL procedures and commands
        mel_commands = {
            'polyCube': 'MEL: Create polygon cube\n\npolyCube -name "myCube" -width 2 -height 2 -depth 2;\npolyCube -ch 1 -o 1 -w 1 -h 1 -d 1;',
            'move': 'MEL: Move objects\n\nmove 0 5 0 "objectName";\nmove -relative 1 0 0;',
            'rotate': 'MEL: Rotate objects\n\nrotate 45 0 0 "objectName";\nrotate -relative 0 90 0;',
            'scale': 'MEL: Scale objects\n\nscale 2 2 2 "objectName";\nscale -pivot 0 0 0 1.5 1.5 1.5;',
            'select': 'MEL: Select objects\n\nselect "objectName";\nselect -clear;\nselect -all;',
            'ls': 'MEL: List objects\n\nls;\nls -selection;\nls -type "transform";',
            'delete': 'MEL: Delete objects\n\ndelete "objectName";\ndelete `ls -sl`;',
            'print': 'MEL: Output to script editor\n\nprint("Hello World\\n");\nprint($variable + "\\n");',
            'size': 'MEL: Get array size\n\nint $count = size($array);\nif (size($selection) > 0) { ... }',
            'clear': 'MEL: Clear array\n\nclear($array);\n// removes all elements from array',
            'source': 'MEL: Execute script file\n\nsource "script.mel";\nsource `workspace -query -rootDirectory` + "scripts/myScript.mel";'
        }
        
        if word in mel_commands:
            return mel_commands[word]
        
        # MEL data types
        if word in ['string', 'int', 'float', 'vector', 'matrix']:
            return self._syntax_docs.get(word, f"MEL data type: {word}")
        
        # MEL control structures
        if word in ['if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default']:
            return f"MEL control structure: {word}\n\nSee MEL documentation for syntax details"
        
        return f"MEL identifier: {word}\n\nRefer to Maya MEL documentation\nHelp → Maya Help → MEL Commands"
    
    def _get_python_tooltip(self, word):
        """Get Python-specific tooltip information."""
        # Maya commands (if it looks like a Maya command)
        if word.startswith(('poly', 'create', 'make', 'list', 'get', 'set', 'connect')):
            if word in self._syntax_docs:
                return self._syntax_docs[word]
            else:
                return f"Maya command: {word}\n\nUse Maya's help documentation for details:\nhelp(cmds.{word})"
        
        # PySide6/Qt classes (if it starts with Q)
        if word.startswith('Q') and len(word) > 1:
            if word in self._syntax_docs:
                return self._syntax_docs[word]
            else:
                return f"Qt/PySide6 class: {word}\n\nQt user interface class\nfrom PySide6.QtWidgets import {word}"
        
        # Python builtins check
        try:
            if hasattr(__builtins__, word):
                builtin_obj = getattr(__builtins__, word)
                if callable(builtin_obj) and hasattr(builtin_obj, '__doc__') and builtin_obj.__doc__:
                    # Clean up the docstring
                    doc = builtin_obj.__doc__.split('\n')[0]  # First line only
                    return f"Built-in function: {word}\n\n{doc}"
        except:
            pass
        
        # Check if it's a common Python pattern
        if word.startswith('__') and word.endswith('__'):
            return f"Magic method: {word}\n\nPython special method (dunder method)\nDefines special behavior for objects"
        
        # Python modules and libraries
        python_modules = {
            'os': 'Operating system interface\n\nimport os\nos.path.join("folder", "file")\nos.getcwd()  # current directory',
            'sys': 'System-specific parameters\n\nimport sys\nsys.path  # module search paths\nsys.argv  # command line arguments',
            're': 'Regular expressions\n\nimport re\nre.search(pattern, string)\nre.findall(pattern, string)',
            'math': 'Mathematical functions\n\nimport math\nmath.sqrt(16)  # 4.0\nmath.pi  # 3.14159...',
            'random': 'Random number generation\n\nimport random\nrandom.randint(1, 10)\nrandom.choice(items)',
            'json': 'JSON data handling\n\nimport json\njson.loads(string)  # parse JSON\njson.dumps(data)  # create JSON',
            'datetime': 'Date and time handling\n\nimport datetime\ndatetime.datetime.now()\ndatetime.date.today()'
        }
        
        if word in python_modules:
            return python_modules[word]
        
        return None
    
    def _style_tooltip(self, word, tooltip_text):
        """Style the tooltip to look like VS Code."""
        # Create rich text with VS Code-like styling
        styled = f"""
        <div style="
            background-color: #252526; 
            color: #cccccc; 
            padding: 8px; 
            border: 1px solid #454545; 
            border-radius: 3px;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            max-width: 400px;
        ">
            <div style="color: #4EC9B0; font-weight: bold; margin-bottom: 4px;">
                {word}
            </div>
            <div style="color: #d4d4d4; white-space: pre-wrap; line-height: 1.4;">
                {tooltip_text}
            </div>
        </div>
        """
        return styled

    # ============================================================
    #  Context and Linting
    # ============================================================
    def _get_context(self):
        cur = self.textCursor()
        doc = self.document()
        block = cur.blockNumber()
        start = max(0, block - 20)
        end = min(doc.blockCount(), block + 20)
        lines = [doc.findBlockByNumber(i).text() for i in range(start, end)]
        return "\n".join(lines)

    def _schedule_lint(self):
        """Start lint thread with stop flag for rapid editing."""
        self._stop_lint_flag.set()  # stop any running thread
        self._stop_lint_flag = threading.Event()
        t = threading.Thread(target=self._lint_worker, args=(self._stop_lint_flag,), daemon=True)
        t.start()
        self._lint_thread = t

    def _lint_worker(self, stop_flag):
        code = self.toPlainText()
        problems = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            problems.append({"lineno": e.lineno, "msg": e.msg})

        # Maya cmds autocorrect (safe import)
        maya_suggestions = []
        if "cmds." in code:
            try:
                import maya.cmds as cmds
                funcs = dir(cmds)
                for ln, line in enumerate(code.splitlines(), start=1):
                    if stop_flag.is_set():
                        return
                    m = re.search(r"cmds\.([a-zA-Z_]+)", line)
                    if m:
                        name = m.group(1)
                        if name not in funcs:
                            closest = difflib.get_close_matches(name, funcs, n=1)
                            if closest:
                                maya_suggestions.append({
                                    "lineno": ln,
                                    "msg": f"Unknown Maya cmd '{name}'. Did you mean '{closest[0]}'?"
                                })
            except Exception:
                pass

        problems += maya_suggestions

        if not stop_flag.is_set():
            # ✅ SAFER cross-version fix: no Q_ARG, runs safely on main Qt thread
            QtCore.QTimer.singleShot(0, lambda: self._emit_lint_results(problems))

    @QtCore.Slot(object)
    def _emit_lint_results(self, problems):
        self.lintProblemsFound.emit(problems)


class _LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor._number_area_width(), 0)

    def paintEvent(self, event):
        editor = self.editor
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtGui.QColor("#2D2D30"))

        block = editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top())
        bottom = top + int(editor.blockBoundingRect(block).height())
        fm_height = editor.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_num = block_number + 1
                number = str(line_num)
                
                # Check for breakpoint on this line
                has_breakpoint = line_num in editor._breakpoints
                
                # Check for current debug line
                is_current_debug_line = editor._current_debug_line == line_num
                
                # Check if this line has errors
                has_error = hasattr(editor, '_error_lines') and line_num in editor._error_lines
                
                # Draw breakpoint indicator
                if has_breakpoint:
                    painter.setBrush(QtGui.QBrush(QtGui.QColor("#d73a49")))  # Red breakpoint
                    painter.setPen(QtCore.Qt.NoPen)
                    bp_size = 8
                    bp_x = 4
                    bp_y = top + (fm_height - bp_size) // 2
                    painter.drawEllipse(bp_x, bp_y, bp_size, bp_size)
                
                # Draw current debug line indicator (yellow arrow)
                if is_current_debug_line:
                    painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffcc02")))  # Yellow debug indicator
                    painter.setPen(QtCore.Qt.NoPen)
                    arrow_size = 6
                    arrow_x = 15
                    arrow_y = top + (fm_height - arrow_size) // 2
                    # Draw triangle pointing right
                    points = [
                        QtCore.QPoint(arrow_x, arrow_y),
                        QtCore.QPoint(arrow_x, arrow_y + arrow_size),
                        QtCore.QPoint(arrow_x + arrow_size, arrow_y + arrow_size // 2)
                    ]
                    painter.drawPolygon(points)
                
                # Draw error indicator (takes precedence for line number color)
                if has_error:
                    # Draw red error dot
                    painter.setBrush(QtGui.QBrush(QtGui.QColor("#f14c4c")))
                    painter.setPen(QtCore.Qt.NoPen)
                    dot_size = 4
                    dot_x = self.width() - 12
                    dot_y = top + (fm_height - dot_size) // 2
                    painter.drawEllipse(dot_x, dot_y, dot_size, dot_size)
                    
                    # Draw line number in red
                    painter.setPen(QtGui.QColor("#f14c4c"))
                elif is_current_debug_line:
                    # Draw line number in yellow for current debug line
                    painter.setPen(QtGui.QColor("#ffcc02"))
                elif has_breakpoint:
                    # Draw line number in white for breakpoints
                    painter.setPen(QtGui.QColor("#ffffff"))
                else:
                    painter.setPen(QtGui.QColor("#858585"))
                    
                painter.drawText(0, top, self.width() - 20, fm_height,
                                 QtCore.Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(editor.blockBoundingRect(block).height())
            block_number += 1

    def mousePressEvent(self, event):
        """Handle mouse clicks in line number area for breakpoint toggling."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Calculate which line was clicked
            editor = self.editor
            block = editor.firstVisibleBlock()
            top = editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top()
            bottom = top + editor.blockBoundingRect(block).height()
            
            click_y = event.pos().y()
            line_number = 1
            
            # Find the line number that was clicked
            while block.isValid():
                if top <= click_y <= bottom:
                    line_number = block.blockNumber() + 1
                    break
                block = block.next()
                top = bottom
                bottom = top + editor.blockBoundingRect(block).height()
            
            # Toggle breakpoint on this line
            editor.toggle_breakpoint(line_number)
        
        super().mousePressEvent(event)
