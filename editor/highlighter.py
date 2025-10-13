"""
Python syntax highlighter — VS Code Dark+ theme.
"""
import re
from PySide6 import QtGui

class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self.rules = []
        self.error_details = {}  # Map of line_number -> {'column': int, 'message': str}
        self._setup_rules()
    
    def set_error_lines(self, error_lines):
        """Set which lines have errors (deprecated - use set_error_details)."""
        self.error_details = {line: {'column': 0, 'message': ''} for line in error_lines}
    
    def set_error_details(self, errors):
        """Set detailed error information including column positions.
        
        Args:
            errors: List of dicts with 'line', 'column', 'message' keys
        """
        self.error_details = {}
        for error in errors:
            self.error_details[error['line']] = {
                'column': error.get('column', 0),
                'message': error.get('message', '')
            }

    def _fmt(self, color, bold=False, italic=False):
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor(color))
        if bold: fmt.setFontWeight(QtGui.QFont.Weight.Bold)
        if italic: fmt.setFontItalic(True)
        return fmt

    def _setup_rules(self):
        # VS Code Dark+ theme colors - comprehensive Python highlighting
        kw = self._fmt("#569CD6", True)           # Keywords (if, def, class, etc.)
        builtin = self._fmt("#C586C0")            # Built-in functions
        builtin_const = self._fmt("#569CD6")      # Built-in constants (True, False, None)
        strfmt = self._fmt("#CE9178")             # Strings
        num = self._fmt("#B5CEA8")                # Numbers
        com = self._fmt("#6A9955", italic=True)   # Comments
        classdef = self._fmt("#4EC9B0", True)     # Class/function names
        funcdef = self._fmt("#DCDCAA")            # Function names
        deco = self._fmt("#C586C0")               # Decorators
        self_param = self._fmt("#569CD6")         # self parameter
        magic = self._fmt("#C586C0")              # Magic methods (__init__, etc.)
        imports = self._fmt("#C586C0")            # import, from keywords
        operators = self._fmt("#D4D4D4")          # Operators
        variables = self._fmt("#9CDCFE")          # Variables
        type_hints = self._fmt("#4EC9B0")         # Type hints
        f_strings = self._fmt("#CE9178")          # f-strings
        
        # Priority order matters! More specific rules first
        
        # Store formats for multi-line string handling
        self.string_format = strfmt
        self.f_string_format = f_strings
        
        # Multi-line string patterns (will be handled specially in highlightBlock)
        self.triple_quote_patterns = [
            (re.compile(r'"""'), strfmt, 1),      # Triple double quotes - state 1
            (re.compile(r"'''"), strfmt, 2),      # Triple single quotes - state 2  
            (re.compile(r'f"""'), f_strings, 3),  # F-string triple double - state 3
            (re.compile(r"f'''"), f_strings, 4),  # F-string triple single - state 4
        ]
        
        # NOTE: Comments are handled separately in highlightBlock() with highest priority
        # to prevent other patterns from overwriting them
        
        # NOTE: Strings (both f-strings and regular strings) are handled separately 
        # in highlightBlock() via _highlight_single_line_strings() to ensure they
        # maintain their color throughout without other patterns interfering
        
        # 5. Numbers (including hex, binary, scientific notation)
        self.rules += [(re.compile(r"\b0[xX][0-9a-fA-F]+\b"), num)]      # Hex
        self.rules += [(re.compile(r"\b0[bB][01]+\b"), num)]             # Binary  
        self.rules += [(re.compile(r"\b0[oO][0-7]+\b"), num)]            # Octal
        self.rules += [(re.compile(r"\b\d+\.\d*([eE][+-]?\d+)?\b"), num)] # Float with exp
        self.rules += [(re.compile(r"\b\d+[eE][+-]?\d+\b"), num)]        # Int with exp
        self.rules += [(re.compile(r"\b\d+\.\d*\b"), num)]               # Float
        self.rules += [(re.compile(r"\b\d+\b"), num)]                    # Integer
        
        # 6. Magic methods and special attributes
        self.rules += [(re.compile(r"\b__\w+__\b"), magic)]
        
        # 7. Decorators
        self.rules += [(re.compile(r"@\w+(\.\w+)*"), deco)]
        
        # 8. Class definitions
        self.rules += [(re.compile(r"\bclass\s+\w+"), classdef)]
        
        # 9. Function definitions  
        self.rules += [(re.compile(r"\bdef\s+\w+"), funcdef)]
        
        # 10. Import statements
        self.rules += [(re.compile(r"\b(import|from)\b"), imports)]
        
        # 11. Keywords (excluding True/False/None which are constants)
        kws = r"\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|global|if|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b"
        self.rules += [(re.compile(kws), kw)]
        
        # 12. Built-in constants
        constants = r"\b(True|False|None|Ellipsis|NotImplemented|__debug__)\b"
        self.rules += [(re.compile(constants), builtin_const)]
        
        # 13. Built-in functions and types
        builtins = r"\b(abs|all|any|ascii|bin|bool|bytearray|bytes|callable|chr|classmethod|compile|complex|delattr|dict|dir|divmod|enumerate|eval|exec|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|isinstance|issubclass|iter|len|list|locals|map|max|memoryview|min|next|object|oct|open|ord|pow|print|property|range|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|vars|zip)\b"
        self.rules += [(re.compile(builtins), builtin)]
        
        # 14. PySide6/Qt Framework - Core Classes
        qt_core = r"\b(QApplication|QCoreApplication|QMainWindow|QWidget|QDialog|QFrame|QLabel|QLineEdit|QPushButton|QCheckBox|QRadioButton|QComboBox|QSpinBox|QDoubleSpinBox|QSlider|QProgressBar|QTextEdit|QPlainTextEdit|QTextBrowser|QListWidget|QTreeWidget|QTableWidget|QTabWidget|QStackedWidget|QSplitter|QScrollArea|QGroupBox|QAction|QMenu|QMenuBar|QToolBar|QStatusBar|QDockWidget)\b"
        self.rules += [(re.compile(qt_core), type_hints)]
        
        # 15. PySide6/Qt Framework - Layouts and Graphics
        qt_layouts = r"\b(QVBoxLayout|QHBoxLayout|QGridLayout|QFormLayout|QBoxLayout|QSizePolicy|QPixmap|QIcon|QFont|QColor|QPalette|QBrush|QPen|QPainter|QRect|QSize|QPoint|QPolygon|QTransform|QMatrix|QRegion|QGraphicsView|QGraphicsScene|QGraphicsItem|QGraphicsPixmapItem|QGraphicsTextItem|QGraphicsRectItem|QGraphicsEllipseItem|QGraphicsLineItem|QGraphicsPolygonItem|QGraphicsPathItem|QGraphicsProxyWidget|QGraphicsEffect|QGraphicsDropShadowEffect|QGraphicsBlurEffect|QGraphicsColorizeEffect|QGraphicsOpacityEffect)\b"
        self.rules += [(re.compile(qt_layouts), type_hints)]
        
        # 16. PySide6/Qt Framework - Events and System
        qt_events = r"\b(QTimer|QThread|QObject|QEvent|QKeyEvent|QMouseEvent|QPaintEvent|QResizeEvent|QCloseEvent|QShowEvent|QHideEvent|QMoveEvent|QDragEnterEvent|QDropEvent|QContextMenuEvent|QWheelEvent|QFocusEvent|QEnterEvent|QLeaveEvent|QActionEvent|QChangeEvent|QChildEvent|QTimerEvent|QEventLoop|QSocketNotifier|QBasicTimer|QElapsedTimer)\b"
        self.rules += [(re.compile(qt_events), type_hints)]
        
        # 17. PySide6/Qt Framework - Dialogs and IO
        qt_dialogs = r"\b(QFileDialog|QMessageBox|QColorDialog|QFontDialog|QInputDialog|QErrorMessage|QProgressDialog|QWizard|QWizardPage|QDir|QFile|QFileInfo|QIODevice|QBuffer|QDataStream|QTextStream|QXmlStreamReader|QXmlStreamWriter|QSettings|QStandardPaths|QStorageInfo|QProcess|QLibrary|QPluginLoader|QUrl|QMimeData|QClipboard|QDrag)\b"
        self.rules += [(re.compile(qt_dialogs), type_hints)]
        
        # 18. PySide6/Qt Framework - Models and Views
        qt_models = r"\b(QSyntaxHighlighter|QTextCharFormat|QTextCursor|QTextDocument|QAbstractItemModel|QStandardItemModel|QFileSystemModel|QSortFilterProxyModel|QModelIndex|QItemSelection|QItemSelectionModel|QAbstractItemView|QListView|QTreeView|QTableView|QHeaderView|QAbstractButton|QToolButton|QCommandLinkButton|QDialogButtonBox|QButtonGroup)\b"
        self.rules += [(re.compile(qt_models), type_hints)]
        
        # 19. PySide6/Qt Framework - Data Types and Meta
        qt_datatypes = r"\b(QDateTime|QDate|QTime|QTimeZone|QLocale|QTranslator|QLibraryInfo|QSysInfo|QOperatingSystemVersion|QVersionNumber|QUuid|QByteArray|QString|QStringList|QChar|QRegExp|QRegularExpression|QRegularExpressionMatch|QRegularExpressionMatchIterator|QVariant|QMetaObject|QMetaMethod|QMetaProperty|QMetaEnum|QMetaType|QJsonDocument|QJsonObject|QJsonArray|QJsonValue|QJsonParseError)\b"
        self.rules += [(re.compile(qt_datatypes), type_hints)]
        
        # 20. PySide6/Qt Framework - Signals and Slots
        qt_signals = r"\b(Signal|Slot|pyqtSignal|pyqtSlot|connect|disconnect|emit|sender|blockSignals)\b"
        self.rules += [(re.compile(qt_signals), magic)]
        
        # 21. PySide6/Qt Framework - Modules
        qt_modules = r"\b(QtCore|QtGui|QtWidgets|QtNetwork|QtSql|QtXml|QtOpenGL|QtMultimedia|QtTest|QtConcurrent|QtDBus|QtHelp|QtDesigner|QtUiTools|QtPrintSupport|QtSvg|QtCharts|QtDataVisualization|QtWebEngine|QtWebEngineWidgets|QtQuick|QtQml|QtPositioning|QtSensors|QtSerialPort|QtBluetooth|QtNfc|QtLocation|QtRemoteObjects|QtWebChannel|QtWebSockets)\b"
        self.rules += [(re.compile(qt_modules), imports)]
        
        # 22. Maya Python API and Commands
        maya_python = r"\b(maya|cmds|pm|pymel|OpenMaya|OpenMayaUI|OpenMayaAnim|OpenMayaFX|OpenMayaRender|MObject|MFn|MDagPath|MSelectionList|MItDag|MItDependencyNodes|MItGeometry|MItMeshPolygon|MItMeshVertex|MItMeshEdge|MItMeshFaceVertex|MItCurveCV|MItSurfaceCV|MItKeyframe|MAnimControl|MAnimMessage|MEventMessage|MNodeMessage|MUiMessage|MDGMessage|MModelMessage|MPolyMessage|MGlobal|MFileIO|MSceneMessage|MTimerMessage|MCommandResult|MArgList|MArgDatabase|MSyntax|MPxCommand|MPxNode|MPxDeformerNode|MPxGeometryFilter|MPxSurfaceShape|MPxLocatorNode|MPxManipContainer|MPxContext|MPxContextCommand|MPxToolCommand|MPxFileTranslator|executeDeferred|evalDeferred|scriptJob|connectAttr|disconnectAttr|getAttr|setAttr|addAttr|deleteAttr|attributeExists|objExists|listAttr|listConnections|listRelatives|listHistory|ls|select|duplicate|delete|group|parent|unparent|instance|reference|file|importFile|exportAll|loadPlugin|unloadPlugin|pluginInfo|nodeType|objectType|rename|hide|show|move|rotate|scale|xform|makeIdentity|polyEvaluate|polyListComponentConversion|filterExpand|hilite|toggle|pickWalk|mel)\b"
        self.rules += [(re.compile(maya_python), type_hints)]
        
        # 23. Popular Python Libraries
        popular_libs = r"\b(numpy|np|pandas|pd|matplotlib|plt|scipy|sklearn|tensorflow|tf|torch|cv2|PIL|Image|requests|json|xml|sqlite3|os|sys|re|math|random|datetime|time|collections|itertools|functools|operator|threading|multiprocessing|subprocess|argparse|logging|unittest|pytest|mock|pathlib|glob|shutil|tempfile|urllib|http|email|base64|hashlib|hmac|secrets|uuid|pickle|csv|configparser|traceback|warnings|contextlib|weakref|copy|types|inspect|ast|dis|gc|platform|socket|ssl|ftplib|smtplib|poplib|imaplib|telnetlib|xmlrpc|http|urllib|tkinter|asyncio|aiohttp|flask|django|fastapi|sqlalchemy|redis|pymongo|psycopg2|mysql|pytest|black|flake8|mypy|pydantic|dataclasses|enum|typing_extensions|click|rich|tqdm|jupyterlab|notebook|ipython|matplotlib|seaborn|plotly|bokeh|altair|streamlit|dash|kivy|pygame|arcade|pyglet|panda3d|blender|bpy|bmesh|mathutils|gpu|gpu_extras|addon_utils)\b"
        self.rules += [(re.compile(popular_libs), type_hints)]
        
        # 24. Python Exceptions
        exceptions = r"\b(ArithmeticError|AssertionError|AttributeError|BaseException|BufferError|BytesWarning|DeprecationWarning|EOFError|Ellipsis|EnvironmentError|Exception|FileExistsError|FileNotFoundError|FloatingPointError|FutureWarning|GeneratorExit|IOError|ImportError|ImportWarning|IndentationError|IndexError|InterruptedError|IsADirectoryError|KeyError|KeyboardInterrupt|LookupError|MemoryError|ModuleNotFoundError|NameError|NotADirectoryError|NotImplemented|NotImplementedError|OSError|OverflowError|PendingDeprecationWarning|PermissionError|ProcessLookupError|RecursionError|ReferenceError|ResourceWarning|RuntimeError|RuntimeWarning|StopAsyncIteration|StopIteration|SyntaxError|SyntaxWarning|SystemError|SystemExit|TabError|TimeoutError|TypeError|UnboundLocalError|UnicodeDecodeError|UnicodeEncodeError|UnicodeError|UnicodeTranslateError|UnicodeWarning|UserWarning|ValueError|Warning|WindowsError|ZeroDivisionError)\b"
        self.rules += [(re.compile(exceptions), builtin)]
        
        # 25. Special parameters and identifiers
        self.rules += [(re.compile(r"\bself\b"), self_param)]
        self.rules += [(re.compile(r"\bcls\b"), self_param)]  # Class method parameter
        
        # 26. Modern Python Type Hints
        type_hints_pattern = r"\b(int|str|float|bool|list|dict|tuple|set|frozenset|bytes|bytearray|memoryview|range|slice|type|object|callable|Iterable|Iterator|Generator|Coroutine|Awaitable|AsyncIterable|AsyncIterator|AsyncGenerator|Sequence|MutableSequence|Set|MutableSet|Mapping|MutableMapping|ItemsView|KeysView|ValuesView|Reversible|Container|Collection|AbstractSet|MappingView|Union|Optional|Any|TypeVar|Generic|Protocol|Literal|Final|ClassVar|NoReturn|Type|Callable|Tuple|List|Dict|Set|FrozenSet|Deque|Counter|OrderedDict|ChainMap|UserDict|UserList|UserString|NamedTuple|TypedDict|Annotated|ParamSpec|Concatenate|TypeAlias|TypeGuard|Self|LiteralString|Never|Required|NotRequired|ReadOnly|Unpack)\b"
        self.rules += [(re.compile(type_hints_pattern), type_hints)]
        
        # 20. Class and function method decorators (enhanced)
        decorator_pattern = r"@[\w\.]+(\([^)]*\))?"
        self.rules += [(re.compile(decorator_pattern), deco)]
        
        # 21. Operators (enhanced)
        operators_pattern = r"(\+\+|--|==|!=|<=|>=|<<|>>|\*\*|//|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<=|>>=|\*\*=|//=|:=|->|<|>|=|\+|-|\*|/|%|&|\||\^|~|@)"
        self.rules += [(re.compile(operators_pattern), operators)]
        
        # 22. String formatting and templates
        format_strings = r"(\{[^}]*\}|%[sdifgGeEcrxXobh%]|\$\w+)"
        self.rules += [(re.compile(format_strings), f_strings)]

    def _reset_all_block_states(self):
        """Reset all block states to -1 (uninitialized) to force fresh highlighting."""
        if not self.document():
            return
        
        block = self.document().firstBlock()
        while block.isValid():
            block.setUserState(-1)
            block = block.next()

    def highlightBlock(self, text):
        """Apply syntax highlighting using proper state management like VS Code.
        
        State values:
        0 = Normal text
        1 = Inside triple double quotes
        2 = Inside triple single quotes  
        3 = Inside f-string triple double quotes
        4 = Inside f-string triple single quotes
        """
        if not text:
            return
        
        # Get the previous block's state
        previous_state = self.previousBlockState()
        if previous_state == -1:
            previous_state = 0
        
        # Track protected characters (inside strings/comments)
        protected = [False] * len(text)
        
        # Start processing from beginning of line
        start_index = 0
        current_state = previous_state
        
        # FIRST: If we're continuing a multi-line string from previous block
        if current_state > 0:
            # We're inside a multi-line string - find the closing delimiter
            if current_state == 1:
                delimiter = '"""'
                format_type = self.string_format
            elif current_state == 2:
                delimiter = "'''"
                format_type = self.string_format
            elif current_state == 3:
                delimiter = '"""'
                format_type = self.f_string_format if hasattr(self, 'f_string_format') else self.string_format
            elif current_state == 4:
                delimiter = "'''"
                format_type = self.f_string_format if hasattr(self, 'f_string_format') else self.string_format
            else:
                # Invalid state, reset
                current_state = 0
                format_type = self.string_format
                delimiter = '"""'
            
            # Look for closing delimiter
            if current_state > 0:
                end_pos = text.find(delimiter, start_index)
                if end_pos >= 0:
                    # Found closing delimiter - format up to and including it
                    end_with_delimiter = end_pos + len(delimiter)
                    self.setFormat(0, end_with_delimiter, format_type)
                    for i in range(0, min(end_with_delimiter, len(text))):
                        protected[i] = True
                    start_index = end_with_delimiter
                    current_state = 0  # Back to normal state
                else:
                    # No closing delimiter found - format entire line and stay in current state
                    self.setFormat(0, len(text), format_type)
                    self.setCurrentBlockState(current_state)
                    return  # CRITICAL: Don't process anything else - we're entirely inside a string
        
        # Process single-line strings first (to protect their content)
        self._highlight_single_line_strings(text, protected, start_index)
        
        # Look for new multi-line string delimiters starting from start_index
        while start_index < len(text) and current_state == 0:
            if protected[start_index]:
                start_index += 1
                continue
            
            # Check for triple-quote delimiters
            found_delimiter = False
            delimiter = None
            new_state = 0
            format_type = self.string_format
            delimiter_start = start_index
            
            # Check if we have enough characters for triple quotes
            if start_index + 2 < len(text):
                three_chars = text[start_index:start_index+3]
                
                # Check for f-string triple quotes (f""" or f''')
                # Must have 'f' immediately before and not be protected
                if (start_index > 0 and 
                    text[start_index - 1].lower() == 'f' and 
                    not protected[start_index - 1] and 
                    (three_chars == '"""' or three_chars == "'''")):
                    # Check if the 'f' is standalone (not part of another word)
                    if start_index == 1 or not text[start_index - 2].isalnum():
                        delimiter = three_chars
                        new_state = 3 if three_chars == '"""' else 4
                        format_type = self.f_string_format if hasattr(self, 'f_string_format') else self.string_format
                        delimiter_start = start_index - 1  # Include the 'f'
                        found_delimiter = True
                
                # Check for regular triple quotes (""" or ''') only if not already found f-string
                if not found_delimiter and (three_chars == '"""' or three_chars == "'''"):
                    delimiter = three_chars
                    new_state = 1 if three_chars == '"""' else 2
                    format_type = self.string_format
                    delimiter_start = start_index
                    found_delimiter = True
            
            if not found_delimiter:
                start_index += 1
                continue
            
            # Found a triple quote - look for closing delimiter
            search_start = start_index + 3  # Start after opening triple quote
            end_pos = text.find(delimiter, search_start)
            
            if end_pos >= 0:
                # Complete multi-line string on same line
                end_with_delimiter = end_pos + len(delimiter)
                self.setFormat(delimiter_start, end_with_delimiter - delimiter_start, format_type)
                for i in range(delimiter_start, min(end_with_delimiter, len(text))):
                    protected[i] = True
                start_index = end_with_delimiter
                current_state = 0  # Stay in normal state
            else:
                # Multi-line string starts here and continues to next block
                self.setFormat(delimiter_start, len(text) - delimiter_start, format_type)
                for i in range(delimiter_start, len(text)):
                    protected[i] = True
                current_state = new_state
                break
        
        # Set the current state for the next block
        self.setCurrentBlockState(current_state)
        
        # Apply comments (only to unprotected text)
        comment_match = re.search(r"#[^\n]*", text)
        if comment_match:
            start = comment_match.start()
            length = len(comment_match.group())
            if not any(protected[start:min(start + length, len(text))]):
                com = self._fmt("#6A9955", italic=True)
                self.setFormat(start, length, com)
                for i in range(start, min(start + length, len(text))):
                    protected[i] = True
        
        # Apply all other rules (keywords, etc.) only to unprotected text
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                if not any(protected[start:min(start + length, len(text))]):
                    self.setFormat(start, length, fmt)
        
        # Apply error highlighting if this line has errors (only underline, preserve colors)
        current_block = self.currentBlock()
        line_number = current_block.blockNumber() + 1  # 1-indexed
        if line_number in self.error_details:
            error_info = self.error_details[line_number]
            error_column = error_info.get('column', 0)
            
            # Calculate where to start the underline
            # If we have a column, use it; otherwise start from first non-whitespace
            if error_column > 0:
                # Python's column is 1-indexed, convert to 0-indexed
                error_start = max(0, error_column - 1)
            else:
                # No column info, start from first non-whitespace
                error_start = len(text) - len(text.lstrip())
            
            # Underline from error position to end of actual content
            error_end = len(text.rstrip())
            error_length = error_end - error_start
            
            if error_length > 0 and error_start < len(text):
                # Apply red wavy underline character by character, preserving existing format
                for i in range(error_start, min(error_start + error_length, len(text))):
                    existing_format = self.format(i)
                    # Create a new format that combines existing colors with error underline
                    combined_format = QtGui.QTextCharFormat(existing_format)
                    combined_format.setUnderlineStyle(QtGui.QTextCharFormat.UnderlineStyle.WaveUnderline)
                    combined_format.setUnderlineColor(QtGui.QColor("#ff0000"))
                    self.setFormat(i, 1, combined_format)
    
    def _highlight_single_line_strings(self, text, formatted, start_index=0):
        """Handle single-line strings (excludes triple quotes completely)."""
        # Process character by character to handle strings properly
        i = start_index
        while i < len(text):
            if formatted[i]:
                i += 1
                continue
            
            # Check for f-string (single or double quote, but NOT triple)
            if i < len(text) - 1 and text[i].lower() == 'f':
                # Must be standalone 'f' (not part of another word)
                if (i == 0 or not text[i-1].isalnum()) and text[i+1] in ('"', "'"):
                    quote_char = text[i+1]
                    # Check it's not a triple quote
                    if i + 3 < len(text) and text[i+1:i+4] == quote_char * 3:
                        i += 1
                        continue
                    # Find closing quote
                    j = i + 2
                    while j < len(text):
                        if text[j] == quote_char:
                            # Check if it's escaped
                            num_backslashes = 0
                            k = j - 1
                            while k >= i + 2 and text[k] == '\\':
                                num_backslashes += 1
                                k -= 1
                            if num_backslashes % 2 == 0:  # Even number of backslashes = not escaped
                                # Found closing quote
                                length = j - i + 1
                                self.setFormat(i, length, self.f_string_format if hasattr(self, 'f_string_format') else self.string_format)
                                for k in range(i, min(i + length, len(text))):
                                    formatted[k] = True
                                i = j + 1
                                break
                        j += 1
                    else:
                        # No closing quote found, treat as incomplete string
                        i += 1
                    continue
            
            # Check for raw string (r"..." or r'...')
            if i < len(text) - 1 and text[i].lower() == 'r':
                if (i == 0 or not text[i-1].isalnum()) and text[i+1] in ('"', "'"):
                    quote_char = text[i+1]
                    # Check it's not a triple quote
                    if i + 3 < len(text) and text[i+1:i+4] == quote_char * 3:
                        i += 1
                        continue
                    # Find closing quote (raw strings don't escape)
                    j = text.find(quote_char, i + 2)
                    if j >= 0:
                        length = j - i + 1
                        self.setFormat(i, length, self.string_format)
                        for k in range(i, min(i + length, len(text))):
                            formatted[k] = True
                        i = j + 1
                        continue
            
            # Check for regular string (single or double quote, but NOT triple)
            if text[i] in ('"', "'"):
                quote_char = text[i]
                # Check it's not a triple quote
                if i + 2 < len(text) and text[i:i+3] == quote_char * 3:
                    i += 1
                    continue
                # Find closing quote
                j = i + 1
                while j < len(text):
                    if text[j] == quote_char:
                        # Check if it's escaped
                        num_backslashes = 0
                        k = j - 1
                        while k >= i + 1 and text[k] == '\\':
                            num_backslashes += 1
                            k -= 1
                        if num_backslashes % 2 == 0:  # Even number of backslashes = not escaped
                            # Found closing quote
                            length = j - i + 1
                            self.setFormat(i, length, self.string_format)
                            for k in range(i, min(i + length, len(text))):
                                formatted[k] = True
                            i = j + 1
                            break
                    j += 1
                else:
                    # No closing quote found, treat as incomplete string to end of line
                    length = len(text) - i
                    self.setFormat(i, length, self.string_format)
                    for k in range(i, len(text)):
                        formatted[k] = True
                    i = len(text)
                continue
            
            i += 1

    



class MELHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self.rules = []
        self._setup_rules()

    def _fmt(self, color, bold=False, italic=False):
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor(color))
        if bold: fmt.setFontWeight(QtGui.QFont.Weight.Bold)
        if italic: fmt.setFontItalic(True)
        return fmt

    def _setup_rules(self):
        # MEL syntax highlighting - VS Code Dark+ theme colors (comprehensive)
        kw = self._fmt("#569CD6", True)           # Keywords
        builtin = self._fmt("#C586C0")            # Built-in functions
        maya_cmd = self._fmt("#4EC9B0")           # Maya commands
        strfmt = self._fmt("#CE9178")             # Strings
        num = self._fmt("#B5CEA8")                # Numbers
        com = self._fmt("#6A9955", italic=True)   # Comments
        procfmt = self._fmt("#DCDCAA")            # Procedures/functions
        varfmt = self._fmt("#9CDCFE")             # Variables
        operators = self._fmt("#D4D4D4")          # Operators
        flags = self._fmt("#C8C8C8")              # Command flags
        
        # Priority order matters! More specific rules first
        
        # 1. Multi-line comments
        self.rules += [(re.compile(r"/\*.*?\*/", re.DOTALL), com)]
        
        # 2. Single line comments
        self.rules += [(re.compile(r"//[^\n]*"), com)]
        
        # 3. Strings (various types)
        self.rules += [(re.compile(r'`[^`]*`'), strfmt)]        # Backtick strings
        self.rules += [(re.compile(r'"[^"]*"'), strfmt)]        # Double quoted
        self.rules += [(re.compile(r"'[^']*'"), strfmt)]        # Single quoted
        
        # 4. Numbers (all formats)
        self.rules += [(re.compile(r"\b\d+\.\d*([eE][+-]?\d+)?\b"), num)]  # Float with exp
        self.rules += [(re.compile(r"\b\d+[eE][+-]?\d+\b"), num)]          # Int with exp
        self.rules += [(re.compile(r"\b\d+\.\d*\b"), num)]                 # Float
        self.rules += [(re.compile(r"\b\d+\b"), num)]                      # Integer
        
        # 5. Procedure definitions
        self.rules += [(re.compile(r"\bproc\s+\w+"), procfmt)]
        
        # 6. MEL control flow keywords
        mel_keywords = r"\b(if|else|for|while|do|switch|case|default|break|continue|return|proc|global|source|eval|catch|int|float|string|vector|matrix|alias|whatIs|exists|size|clear)\b"
        self.rules += [(re.compile(mel_keywords), kw)]
        
        # 7. Maya Geometry Creation Commands
        geometry_cmds = r"\b(polyCube|polySphere|polyCylinder|polyPlane|polyTorus|polyCone|polyPipe|polyHelix|polyPrism|polyPyramid|polyQuad|polyDisc|polyUVRectangle|polyGear|polyChamfer|polyBevel|polyExtrudeFace|polyExtrudeEdge|polyExtrudeVertex|polySubdivide|polySmooth|polyReduce|polyTriangulate|polyQuadrangulate|polyMergeVertex|polySeparate|polyUnite|polyBoolean|polyIntersect|polyDifference|polyUnion)\b"
        self.rules += [(re.compile(geometry_cmds), maya_cmd)]
        
        # 8. Maya NURBS Commands
        nurbs_cmds = r"\b(nurbsPlane|nurbsSphere|nurbsCube|nurbsCylinder|nurbsCone|nurbsTorus|curve|circle|arc|square|surface|loft|extrude|revolve|planarSrf|birail|boundary|trim|untrim|rebuild|degree|spans|insertKnot|removeKnot|editPoint|controlVertex|isoparm|patch|detach|attach|open|close|reverse|projectCurve|intersect|offset|fillet|chamfer)\b"
        self.rules += [(re.compile(nurbs_cmds), maya_cmd)]
        
        # 9. Maya Transform Commands
        transform_cmds = r"\b(move|rotate|scale|xform|makeIdentity|freezeTransformations|resetTransformations|centerPivot|movePivot|rotatePivot|scalePivot|duplicate|instance|group|ungroup|parent|unparent|orientConstraint|pointConstraint|parentConstraint|aimConstraint|scaleConstraint|geometryConstraint|normalConstraint|tangentConstraint|poleVectorConstraint)\b"
        self.rules += [(re.compile(transform_cmds), maya_cmd)]
        
        # 10. Maya Selection Commands  
        selection_cmds = r"\b(select|selectAll|selectNone|selectInvert|selectSimilar|selectHierarchy|selectKey|selectKeyframe|ls|listRelatives|listConnections|listAttr|listHistory|listSets|filterExpand|match|pickWalk|hilite|toggle)\b"
        self.rules += [(re.compile(selection_cmds), maya_cmd)]
        
        # 11. Maya Attribute Commands
        attribute_cmds = r"\b(getAttr|setAttr|addAttr|deleteAttr|connectAttr|disconnectAttr|listConnections|isConnected|connectionInfo|listAttr|attributeExists|attributeQuery|lockNode|unlockNode|hide|show|isolateSelect|displaySmoothness|displayColor)\b"
        self.rules += [(re.compile(attribute_cmds), maya_cmd)]
        
        # 12. Maya Animation Commands
        animation_cmds = r"\b(keyframe|setKeyframe|cutKey|copyKey|pasteKey|scaleKey|snapKey|keyTangent|setInfinity|playbackOptions|currentTime|startTime|endTime|findKeyframe|keyframeStats|animCurve|character|clipLibrary|clip|bakeResults|dopeSheetEditor|graphEditor|timeEditor|playblast)\b"
        self.rules += [(re.compile(animation_cmds), maya_cmd)]
        
        # 13. Maya Rendering Commands
        rendering_cmds = r"\b(render|batchRender|renderSettings|defaultRenderGlobals|renderQuality|renderResolution|renderWindowSelectContext|hwRender|mayaHardware|mentalray|arnold|redshift|vray|createNode|shadingNode|connectNodeToNodeOverride|hyperShade|nodeEditor|outliner|channelBox)\b"
        self.rules += [(re.compile(rendering_cmds), maya_cmd)]
        
        # 14. Maya Deformer Commands
        deformer_cmds = r"\b(bend|twist|wave|flare|squash|taper|sine|cluster|sculpt|proportionalModificationTool|artAttrSkinPaint|skinCluster|bindSkin|unbindSkin|detachSkin|copySkinWeights|blendShape|wrap|shrinkWrap|lattice|ffd|nonLinear|jiggle|tension|muscle|cMuscle|wire|textDeformer)\b"
        self.rules += [(re.compile(deformer_cmds), maya_cmd)]
        
        # 15. Maya Dynamics Commands  
        dynamics_cmds = r"\b(particle|emitter|gravity|turbulence|drag|newton|radial|vortex|uniform|air|volume|dynExpression|goal|instancer|sprite|cloud|tube|sphere|multiPoint|multiStreak|numeric|collision|event|rigid|soft|spring|hinge|nail|pin|barrier|field|fluidEmitter|ocean|pond|wake)\b"
        self.rules += [(re.compile(dynamics_cmds), maya_cmd)]
        
        # 16. Maya UI Commands
        ui_cmds = r"\b(window|showWindow|deleteUI|layout|columnLayout|rowLayout|formLayout|frameLayout|scrollLayout|tabLayout|menuBarLayout|paneLayout|button|checkBox|radioButton|textField|textScrollList|iconTextButton|symbolButton|picture|text|separator|progressBar|slider|intSlider|floatSlider|colorSlider|optionMenu|popupMenu|menuItem|confirmDialog|promptDialog|fileDialog|fileDialog2|progressWindow|waitCursor|refresh)\b"
        self.rules += [(re.compile(ui_cmds), maya_cmd)]
        
        # 17. Maya File I/O Commands
        file_cmds = r"\b(file|newFile|openFile|saveFile|saveAs|importFile|exportAll|exportSelected|reference|createReference|removeReference|loadReference|unloadReference|referenceEdit|referenceQuery|namespace|namespaceInfo|rename|objExists|nodeType|objectType|about|workspace|project|projectViewer)\b"
        self.rules += [(re.compile(file_cmds), maya_cmd)]
        
        # 18. MEL Built-in Functions
        builtin_funcs = r"\b(abs|acos|asin|atan|atan2|ceil|cos|deg_to_rad|exp|floor|log|max|min|pow|rad_to_deg|rand|seed|sin|sqrt|tan|sphrand|noise|smoothstep|clamp|cross|dot|mag|unit|hsv_to_rgb|rgb_to_hsv|size|clear|sort|stringArrayIntersector|stringArrayRemove|stringArrayContains|match|gmatch|substitute|startString|endString|strip|tolower|toupper|capitalize|fromNativePath|toNativePath|dirname|basename|filetest|fopen|fclose|fprint|fread|fwrite|fflush|system|getenv|putenv|date|timerX)\b"
        self.rules += [(re.compile(builtin_funcs), builtin)]
        
        # 19. Command flags (options starting with -)
        self.rules += [(re.compile(r"-\w+"), flags)]
        
        # 20. Variables (starting with $)
        self.rules += [(re.compile(r"\$\w+"), varfmt)]
        
        # 21. Operators
        operators_pattern = r"(\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|\+=|-=|\*=|/=|%=|<|>|=|\+|-|\*|/|%|&|\||\^|~|!)"
        self.rules += [(re.compile(operators_pattern), operators)]

    def highlightBlock(self, text):
        # Apply rules in order - later rules can override earlier ones for proper precedence
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                self.setFormat(start, length, fmt)
