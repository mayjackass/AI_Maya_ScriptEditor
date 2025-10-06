"""
AI Script Editor v2.0 — Personal Edition
Developed by: Mayj Amilano

Maya 2026 / PySide6 / OpenAI v1.x

A lightweight Python script editor with 
AI-assisted code completion and linting.
"""

import os, sys, re, io, tempfile, threading, subprocess, contextlib
from functools import partial
from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import difflib
import shutil

# Optional OpenAI import (v1.x only)
try:
    from openai import OpenAI
    _CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    _CLIENT = None
    print("⚠️  OpenAI SDK not available:", e)

from .ai_key_manager import decrypt_api_key, show_key_dialog


# ----------------------------------------------------------------------
# Dark theme stylesheet
# ----------------------------------------------------------------------
CHARCOAL_STYLE = """
QWidget{background:#252526;color:#ccc;font-family:Consolas;}
QPlainTextEdit, QTextEdit{background:#1E1E1E;color:#DDD;
    selection-background-color:#264F78;border:none;}
QScrollBar:vertical{background:#2D2D30;width:8px;}
QScrollBar::handle:vertical{background:#3E3E42;border-radius:4px;}
QPushButton{background:#3A3D41;padding:4px;border-radius:4px;}
QPushButton:hover{background:#505356;}
QComboBox{background:#2D2D30;color:#CCC;padding:2px;}
QLineEdit{background:#1E1E1E;color:#DDD;padding:4px;border:1px solid #3E3E42;}
QLabel{color:#ccc;}
"""


# ----------------------------------------------------------------------
#  Line Number Area Widget
# ----------------------------------------------------------------------
class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint(event)


# ----------------------------------------------------------------------
#  Improved Python Syntax Highlighter (for PySide6)
# ----------------------------------------------------------------------
class PythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        self._build_rules()
        self.triple_single = re.compile("'''")
        self.triple_double = re.compile('"""')
        self.string_fmt = self._fmt("#CE9178")

    def _fmt(self, color, bold=False, italic=False):
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor(color))
        if bold:
            fmt.setFontWeight(QtGui.QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _build_rules(self):
        # Define colors inspired by VSCode Dark+
        keyword_fmt = self._fmt("#569CD6", True)
        builtin_fmt = self._fmt("#C586C0")
        classdef_fmt = self._fmt("#4EC9B0", True)
        comment_fmt = self._fmt("#6A9955", italic=True)
        string_fmt = self._fmt("#CE9178")
        number_fmt = self._fmt("#B5CEA8")
        decorator_fmt = self._fmt("#C586C0", True)

        # Keyword rule
        keywords = r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
        self.rules.append((re.compile(keywords), keyword_fmt))

        # Builtins (len, range, print, etc.)
        builtins = r'\b(len|range|print|type|dir|set|list|dict|tuple|int|float|str|bool|super|isinstance|enumerate|zip|map|filter|any|all|sum|min|max|abs)\b'
        self.rules.append((re.compile(builtins), builtin_fmt))

        # Numbers
        self.rules.append((re.compile(r'\b[0-9]+(\.[0-9]+)?\b'), number_fmt))

        # Strings (single and double quotes)
        self.rules.append((re.compile(r'(\"[^\"]*\"|\'[^\']*\')'), string_fmt))

        # Comments
        self.rules.append((re.compile(r'#[^\n]*'), comment_fmt))

        # Class and def definitions
        self.rules.append((re.compile(r'\bclass\s+(\w+)'), classdef_fmt))
        self.rules.append((re.compile(r'\bdef\s+(\w+)'), classdef_fmt))

        # Decorators
        self.rules.append((re.compile(r'@\w+'), decorator_fmt))

    def highlightBlock(self, text):
        """Highlight syntax per block, supporting multi-line strings."""
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

        # Handle multi-line triple-quoted strings
        self._apply_multiline_string(text, self.triple_single, 1)
        self._apply_multiline_string(text, self.triple_double, 2)

    def _apply_multiline_string(self, text, delimiter, state):
        start = 0
        add = 0
        if self.previousBlockState() == state:
            match = delimiter.search(text)
            if match:
                end = match.end()
                self.setFormat(0, end, self.string_fmt)
                self.setCurrentBlockState(0)
                add = end
            else:
                self.setFormat(0, len(text), self.string_fmt)
                self.setCurrentBlockState(state)
                return

        while True:
            match = delimiter.search(text, start + add)
            if not match:
                break
            end_match = delimiter.search(text, match.end())
            if not end_match:
                self.setFormat(match.start(), len(text) - match.start(), self.string_fmt)
                self.setCurrentBlockState(state)
                break
            else:
                self.setFormat(match.start(), end_match.end() - match.start(), self.string_fmt)
                start = end_match.end()
                self.setCurrentBlockState(0)

# ----------------------------------------------------------------------
#  Code Editor (With Line Numbers & Ghost Completions)
# ----------------------------------------------------------------------
class CodeEditor(QtWidgets.QPlainTextEdit):
    requestAICompletion = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QtGui.QFont("Consolas", 11)
        font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
        self.setFont(font)
        fm = QtGui.QFontMetrics(font)
        self.setTabStopDistance(4 * fm.horizontalAdvance(' '))
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        # --- Line Number Support
        self.number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # --- Ghost AI Overlay
        self.aiOverlay = QtWidgets.QLabel(self)
        self.aiOverlay.setStyleSheet("color:#5A5AFF;font-style:italic;")
        self.aiOverlay.hide()

        # --- Syntax Highlight
        self.highlighter = PythonHighlighter(self.document())

    # ------------------------------------------------------------------
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        fm = self.fontMetrics()
        return 10 + fm.horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.number_area.scroll(0, dy)
        else:
            self.number_area.update(0, rect.y(), self.number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(),
                                                  self.line_number_area_width(), cr.height()))

    def line_number_area_paint(self, event):
        painter = QtGui.QPainter(self.number_area)
        painter.fillRect(event.rect(), QtGui.QColor("#2D2D30"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        fm_height = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QtGui.QColor("#858585"))
                painter.drawText(0, top, self.number_area.width()-4,
                                 fm_height, QtCore.Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        selection = QtWidgets.QTextEdit.ExtraSelection()
        line_color = QtGui.QColor("#2A2D2E")
        selection.format.setBackground(line_color)
        selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    # ------------------------------------------------------------------
    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key.Key_Space and \
           ev.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            ctx = "\n".join(self.toPlainText().splitlines()[-8:])
            self.requestAICompletion.emit(ctx)
            return
        if ev.key() == QtCore.Qt.Key.Key_Tab and self.aiOverlay.isVisible():
            cur = self.textCursor()
            cur.insertText(self.aiOverlay.text())
            self.aiOverlay.hide()
            return
        super().keyPressEvent(ev)

    def show_ghost(self, text):
        rect = self.cursorRect()
        self.aiOverlay.setGeometry(rect.x()+4, rect.y()+2, 600, 20)
        self.aiOverlay.setText(text)
        self.aiOverlay.show()

    # Safe text accessor used by run/lint routines
    def toPlainTextSafe(self):
        try:
            return self.toPlainText()
        except Exception:
            return ""


# ----------------------------------------------------------------------
#  Output Console (Displays Run Results & Errors)
# ----------------------------------------------------------------------
class OutputConsole(QtWidgets.QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("background:#1E1E1E;color:#C8C8C8;font-family:Consolas;")
        self.setFont(QtGui.QFont("Consolas", 10))

    def write(self, text):
        self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def flush(self):  # for stdout interface
        pass


# ----------------------------------------------------------------------
#  Key chord manager (handles two-stroke shortcuts like Ctrl+K Ctrl+O)
# ----------------------------------------------------------------------
class KeyChordManager(QtCore.QObject):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent = parent_window
        self._expected = None
        self._callback = None
        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._cancel)
        self._shortcuts = []

    def add_chord(self, first_seq, second_seq, callback, timeout=1500):
        """
        first_seq/second_seq are strings that Qt understands, e.g. "Ctrl+K", "Ctrl+O" or "O".
        callback is called when chord is matched.
        """
        sc = QtWidgets.QShortcut(QtGui.QKeySequence(first_seq), self.parent)
        sc.activated.connect(lambda: self._start_wait(second_seq, callback, timeout))
        self._shortcuts.append(sc)

    def _start_wait(self, expected, cb, timeout):
        self._expected = expected
        self._callback = cb
        self.parent.installEventFilter(self)
        self._timer.start(timeout)

    def _cancel(self):
        try:
            self.parent.removeEventFilter(self)
        except Exception:
            pass
        self._expected = None
        self._callback = None
        self._timer.stop()

    def eventFilter(self, obj, event):
        if self._expected and event.type() == QtCore.QEvent.Type.KeyPress:
            seq = self._event_to_seq(event)
            if not seq:
                return False
            # Compare case-insensitive normalized
            if QtGui.QKeySequence(seq).toString() == QtGui.QKeySequence(self._expected).toString():
                try:
                    self._callback()
                finally:
                    self._cancel()
                return True
            else:
                # Wrong second key -> cancel
                self._cancel()
        return False

    def _event_to_seq(self, ev):
        mods = []
        m = ev.modifiers()
        if m & QtCore.Qt.KeyboardModifier.ControlModifier:
            mods.append("Ctrl")
        if m & QtCore.Qt.KeyboardModifier.ShiftModifier:
            mods.append("Shift")
        if m & QtCore.Qt.KeyboardModifier.AltModifier:
            mods.append("Alt")
        key = QtGui.QKeySequence(ev.key()).toString()
        if not key:
            return None
        return "+".join(mods + [key])


# ----------------------------------------------------------------------
#  Code hierarchy model: folders -> .py files -> top-level classes/functions
# ----------------------------------------------------------------------
class CodeHierarchyModel(QtGui.QStandardItemModel):
    FILE_ROLE = QtCore.Qt.UserRole + 1
    LINE_ROLE = QtCore.Qt.UserRole + 2
    TYPE_ROLE = QtCore.Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Explorer"])
        self._folder_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon)
        self._file_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon)
        self._class_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowRight)  # fallback
        self._func_icon = parent.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)  # fallback

    def build_from_folder(self, folder, include_hidden=False):
        import ast
        self.clear()
        self.setHorizontalHeaderLabels(["Explorer"])
        root_item = self.invisibleRootItem()

        for dirpath, dirnames, filenames in os.walk(folder):
            # optionally skip hidden dirs
            rel = os.path.relpath(dirpath, folder)
            # find parent item for this dir
            parent_item = root_item
            if rel != ".":
                parts = rel.split(os.sep)
                parent_item = self._ensure_path(root_item, parts)

            # add python files only
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                if not include_hidden and fn.startswith("."):
                    continue
                full = os.path.join(dirpath, fn)
                file_item = QtGui.QStandardItem(self._file_icon, fn)
                file_item.setData(full, self.FILE_ROLE)
                file_item.setData("file", self.TYPE_ROLE)
                parent_item.appendRow(file_item)

                # try parse top-level defs/classes
                try:
                    with open(full, "r", encoding="utf-8") as f:
                        src = f.read()
                    tree = ast.parse(src)
                    for node in tree.body:
                        if isinstance(node, ast.FunctionDef):
                            it = QtGui.QStandardItem(self._func_icon, f"def {node.name}()")
                            it.setData(full, self.FILE_ROLE)
                            it.setData(getattr(node, "lineno", 1), self.LINE_ROLE)
                            it.setData("function", self.TYPE_ROLE)
                            file_item.appendRow(it)
                        elif isinstance(node, ast.ClassDef):
                            it = QtGui.QStandardItem(self._class_icon, f"class {node.name}")
                            it.setData(full, self.FILE_ROLE)
                            it.setData(getattr(node, "lineno", 1), self.LINE_ROLE)
                            it.setData("class", self.TYPE_ROLE)
                            file_item.appendRow(it)
                except Exception:
                    # if parsing fails, ignore symbols for that file
                    continue

    def _ensure_path(self, root_item, parts):
        cur = root_item
        for p in parts:
            found = None
            for i in range(cur.rowCount()):
                child = cur.child(i)
                if child.text() == p and child.data(self.TYPE_ROLE) == "dir":
                    found = child
                    break
            if not found:
                new = QtGui.QStandardItem(self._folder_icon, p)
                new.setData(None, self.FILE_ROLE)
                new.setData("dir", self.TYPE_ROLE)
                cur.appendRow(new)
                cur = new
            else:
                cur = found
        return cur

    # ------------------------------------------------------------------
    def new_tab(self, text="untitled", path=None, content=""):
         ed = CodeEditor()
         ed.requestAICompletion.connect(self._inline_ai)
         if path:
             ed.setPlainText(content)
             idx = self.tabWidget.addTab(ed, os.path.basename(path))
             ed.setProperty("filePath", path)
         else:
             ed.setPlainText(content)
             idx = self.tabWidget.addTab(ed, text)
         self.tabWidget.setCurrentIndex(idx)
         self.editor = ed
         return ed
 
    def open_file_in_tab(self, path, line=None):
         try:
             if not os.path.isfile(path):
                 return
             # If file already open, activate its tab
             for i in range(self.tabWidget.count()):
                 w = self.tabWidget.widget(i)
                 if w.property("filePath") == path:
                    self.tabWidget.setCurrentIndex(i)
                    # if a line was provided, move cursor
                    if line:
                        ed = self.tabWidget.widget(i)
                        try:
                            c = ed.textCursor()
                            ln = max(1, int(line)) - 1
                            block = ed.document().findBlockByNumber(ln)
                            c.setPosition(block.position())
                            ed.setTextCursor(c)
                        except Exception:
                            pass
                    return
             with open(path, "r", encoding="utf-8") as f:
                 data = f.read()
             name = os.path.basename(path)
             ed = self.new_tab(name, path=path, content=data)
             ed.setProperty("filePath", path)
             self.tabWidget.setTabText(self.tabWidget.indexOf(ed), name)
             # update explorer to show folder of the opened file
             folder = os.path.dirname(path)
             if folder:
                # rebuild hierarchy model for the file's folder and switch view to it
                try:
                    self.hierarchyModel.build_from_folder(folder)
                    self.explorerView.setModel(self.hierarchyModel)
                except Exception:
                    # fallback to filesystem view
                    try:
                        self.explorerView.setModel(self.explorer_fs_model)
                        self.explorerView.setRootIndex(self.explorer_fs_model.index(folder))
                    except Exception:
                        pass
             # add to recent list
             self._add_recent_file(path)
             # if caller requested a line, jump there
             if line:
                try:
                    ln = max(1, int(line)) - 1
                    c = ed.textCursor()
                    block = ed.document().findBlockByNumber(ln)
                    c.setPosition(block.position())
                    ed.setTextCursor(c)
                except Exception:
                    pass
         except Exception as e:
             self.console.append(f"[Open error] {e}\n")
 
    def _open_folder_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
        if folder:
            self.open_folder(folder)

    def open_folder(self, folder):
        """Set explorer to the selected folder and show code hierarchy."""
        try:
            if not os.path.isdir(folder):
                return
            # prefer hierarchy view (folders -> files -> classes/functions)
            try:
                self.hierarchyModel.build_from_folder(folder)
                self.explorerView.setModel(self.hierarchyModel)
            except Exception:
                # fallback: plain filesystem listing
                self.explorerView.setModel(self.explorer_fs_model)
                self.explorer_fs_model.setRootPath(folder)
                self.explorerView.setRootIndex(self.explorer_fs_model.index(folder))
            self.console.append(f"Explorer root: {folder}\n")
            # persist last opened folder
            self.settings.setValue("lastFolder", folder)
        except Exception as e:
            self.console.append(f"[Folder error] {e}\n")

    def _on_explorer_double_clicked(self, index):
        try:
            model = index.model()
            # First try CodeHierarchyModel data roles (itemFromIndex may not exist on QFileSystemModel)
            item = None
            try:
                item = model.itemFromIndex(index)
            except Exception:
                item = None

            if item is not None:
                path = item.data(CodeHierarchyModel.FILE_ROLE)
                line = item.data(CodeHierarchyModel.LINE_ROLE)
                if path:
                    self.open_file_in_tab(path, line=line)
                    return

            # fallback to filesystem model if present
            try:
                # QFileSystemModel exposes filePath; other models may not
                path = model.filePath(index)
                if path and os.path.isfile(path):
                    self.open_file_in_tab(path)
                    return
            except Exception:
                pass
        except Exception as e:
            # avoid raising errors during UI events
            try:
                self.console.append(f"[Explorer click error] {e}\n")
            except Exception:
                pass


# ----------------------------------------------------------------------
#  Redirect stdout/stderr context manager
# ----------------------------------------------------------------------
@contextlib.contextmanager
def redirect_output(console_widget):
    """Redirect sys.stdout and sys.stderr to the given QTextEdit console."""
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = console_widget
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err


# ----------------------------------------------------------------------
#  Main Window —  with File/Edit menus + Search
# ----------------------------------------------------------------------
class AiScriptEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Script Editor v2 — Personal Edition")
        self.resize(1200, 800)
        self.setStyleSheet(CHARCOAL_STYLE)

        api_key = decrypt_api_key()
        if not api_key:
            api_key = show_key_dialog(self)
        if api_key:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        else:
            self._client = None

        # --- Central editor tab system
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.setCentralWidget(self.tabWidget)

        # --- Output console dock
        self.console = OutputConsole()
        dock_console = QtWidgets.QDockWidget("Output", self)
        dock_console.setWidget(self.console)
        dock_console.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_console)

        # --- Create initial tab
        self.new_tab("untitled")

        # --- Search bar (hidden by default)
        self.searchBar = QtWidgets.QWidget()
        search_layout = QtWidgets.QHBoxLayout(self.searchBar)
        search_layout.setContentsMargins(4, 2, 4, 2)
        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setPlaceholderText("Find...")
        self.searchNextBtn = QtWidgets.QPushButton("Next")
        self.searchPrevBtn = QtWidgets.QPushButton("Previous")
        self.searchCloseBtn = QtWidgets.QPushButton("✕")
        self.searchCloseBtn.setFixedWidth(24)
        for w in (self.searchEdit, self.searchNextBtn, self.searchPrevBtn, self.searchCloseBtn):
            w.setStyleSheet("background:#2D2D30;color:#DDD;border:1px solid #3E3E42;")
        search_layout.addWidget(QtWidgets.QLabel("Find:"))
        search_layout.addWidget(self.searchEdit, 1)
        search_layout.addWidget(self.searchPrevBtn)
        search_layout.addWidget(self.searchNextBtn)
        search_layout.addWidget(self.searchCloseBtn)
        self.searchBar.hide()
        self.addToolBarBreak()
        searchToolbar = QtWidgets.QToolBar("Search")
        searchToolbar.setMovable(False)
        searchToolbar.addWidget(self.searchBar)
        self.addToolBar(QtCore.Qt.TopToolBarArea, searchToolbar)

        # --- Toolbar with Run/Lint
        tb = self.addToolBar("Tools")

        run_act = tb.addAction("Run")
        run_act.setShortcut(QtGui.QKeySequence("Ctrl+Return"))
        run_act.setStatusTip("Run current script (Ctrl+Enter)")
        run_act.triggered.connect(self._run_script)

        lint_act = tb.addAction("Lint")
        lint_act.setShortcut(QtGui.QKeySequence("Ctrl+Shift+L"))
        lint_act.setStatusTip("Lint script for syntax errors (Ctrl+Shift+L)")
        lint_act.triggered.connect(self._lint_script)

        # ------------------------------------------------------------------
        # Menu Bar
        # ------------------------------------------------------------------
        mb = self.menuBar()

        # === File menu ===
        fileMenu = mb.addMenu("&File")

        newAct = QtGui.QAction("New", self, shortcut="Ctrl+N", triggered=self._new_file)
        openAct = QtGui.QAction("Open...", self, shortcut="Ctrl+O", triggered=self._open_file_dialog)
        openFolderAct = QtGui.QAction("Open Folder...", self, shortcut="Ctrl+K, Ctrl+O", triggered=self._open_folder_dialog)
        saveAct = QtGui.QAction("Save", self, shortcut="Ctrl+S", triggered=self._save_file)
        saveAsAct = QtGui.QAction("Save As...", self, shortcut="Ctrl+Shift+S", triggered=self._save_file_as)
        exitAct = QtGui.QAction("Exit", self, triggered=self.close)

        fileMenu.addActions([newAct, openAct, openFolderAct])
        fileMenu.addSeparator()
        fileMenu.addActions([saveAct, saveAsAct])
        fileMenu.addSeparator()
        fileMenu.addAction(exitAct)

        # === Edit menu ===
        editMenu = mb.addMenu("&Edit")

        undoAct = QtGui.QAction("Undo", self, shortcut="Ctrl+Z", triggered=lambda: self._active_editor().undo())
        redoAct = QtGui.QAction("Redo", self, shortcut="Ctrl+Y", triggered=lambda: self._active_editor().redo())
        copyAct = QtGui.QAction("Copy", self, shortcut="Ctrl+C", triggered=lambda: self._active_editor().copy())
        pasteAct = QtGui.QAction("Paste", self, shortcut="Ctrl+V", triggered=lambda: self._active_editor().paste())
        cutAct = QtGui.QAction("Cut", self, shortcut="Ctrl+X", triggered=lambda: self._active_editor().cut())
        selectAllAct = QtGui.QAction("Select All", self, shortcut="Ctrl+A", triggered=lambda: self._active_editor().selectAll())

        editMenu.addActions([undoAct, redoAct])
        editMenu.addSeparator()
        editMenu.addActions([cutAct, copyAct, pasteAct])
        editMenu.addSeparator()
        editMenu.addAction(selectAllAct)
    
        # === Help menu ===
        help_menu = mb.addMenu("&Help")
        about_act = help_menu.addAction("About")
        github_act = help_menu.addAction("Visit GitHub")
        key_act = help_menu.addAction("Set API Key…")

        about_act.triggered.connect(lambda: QtWidgets.QMessageBox.information(
            self, "About AI Script Editor",
            "AI Script Editor v3\nMaya 2026 / PySide6\n\nDeveloped by Mayj Amilano\n© 2025 All rights reserved."
        ))
        github_act.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(
            QtCore.QUrl("https://github.com/mayjackass/AI_Maya_ScriptEditor/tree/main")  # update soon
        ))
        key_act.triggered.connect(lambda: show_key_dialog(self))


        # --- Explorer Dock (Left)
        self.explorer_fs_model = QtWidgets.QFileSystemModel()
        root_path = os.getcwd()
        self.explorer_fs_model.setRootPath(root_path)
        self.explorer_fs_model.setNameFilters(["*.py"])
        self.explorer_fs_model.setNameFilterDisables(False)

        self.hierarchyModel = CodeHierarchyModel(self)
        try:
            self.hierarchyModel.build_from_folder(root_path)
        except Exception:
            pass

        self.explorerView = QtWidgets.QTreeView()
        self.explorerView.setModel(self.hierarchyModel)
        self.explorerView.doubleClicked.connect(self._on_explorer_double_clicked)
        self.explorerView.setHeaderHidden(True)
        self.explorerView.setAnimated(True)
        self.explorerView.setIndentation(12)

        explorerDock = QtWidgets.QDockWidget("Explorer", self)
        explorerDock.setWidget(self.explorerView)
        explorerDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, explorerDock)

        # --- AI Chat Dock (Right)
        self._build_ai_chat_dock()

        # --- Status bar
        self.statusBar().showMessage("Ready")

        # --- Search connections
        self.searchEdit.returnPressed.connect(self._find_next)
        self.searchNextBtn.clicked.connect(self._find_next)
        self.searchPrevBtn.clicked.connect(lambda: self._find_next(backward=True))
        self.searchCloseBtn.clicked.connect(self._toggle_search)

        # Shortcuts for search toggle
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), self, self._toggle_search)

    # ------------------------------------------------------------------
    #  AI Copilot Chat Dock  (streaming GPT panel with prompt + output)
    # ------------------------------------------------------------------
    def _build_ai_chat_dock(self):
        """Creates the right-side AI Copilot dock panel."""
        try:
            self.chatDock = QtWidgets.QDockWidget("Copilot Chat", self)
            self.chatDock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
            chatWidget = QtWidgets.QWidget()
            chatLayout = QtWidgets.QVBoxLayout(chatWidget)
            chatLayout.setContentsMargins(6, 6, 6, 6)
            chatLayout.setSpacing(4)

            # Chat display area
            self.chatDisplay = QtWidgets.QTextBrowser()
            self.chatDisplay.setStyleSheet(
                "background:#1E1E1E;color:#DDD;font-family:Consolas;font-size:10pt;"
            )
            self.chatDisplay.setOpenExternalLinks(True)
            self.chatDisplay.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

            # Input row
            self.prompt = QtWidgets.QLineEdit()
            self.prompt.setPlaceholderText("Ask AI (e.g. 'optimize this function')...")
            sendBtn = QtWidgets.QPushButton("Send")
            sendBtn.setToolTip("Send prompt to AI (Enter)")
            self.applySuggestionBtn = QtWidgets.QPushButton("Apply Suggestion")
            self.applySuggestionBtn.setVisible(False)

            sendRow = QtWidgets.QHBoxLayout()
            sendRow.addWidget(self.prompt, 1)
            sendRow.addWidget(sendBtn)
            sendRow.addWidget(self.applySuggestionBtn)

            chatLayout.addWidget(self.chatDisplay, 1)
            chatLayout.addLayout(sendRow)
            self.chatDock.setWidget(chatWidget)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.chatDock)

            # --- Connect logic ---
            sendBtn.clicked.connect(self._send_prompt)
            self.prompt.returnPressed.connect(self._send_prompt)
            self.applySuggestionBtn.clicked.connect(self._apply_suggestion)

            self.statusBar().showMessage("AI Chat ready.")
        except Exception as e:
            print(f"[AI Chat Dock Error] {e}")


    # ------------------------------------------------------------------
    # --- File & Edit Menus
    # ------------------------------------------------------------------
    def _build_file_menu(self, mb):
        file_menu = mb.addMenu("&File")

        new_act = QtGui.QAction("New", self, shortcut="Ctrl+N", triggered=lambda: self.new_tab("untitled"))
        open_act = QtGui.QAction("Open...", self, shortcut="Ctrl+O", triggered=self._open_file_dialog)
        save_act = QtGui.QAction("Save", self, shortcut="Ctrl+S", triggered=self._save_file)
        saveas_act = QtGui.QAction("Save As...", self, shortcut="Ctrl+Shift+S", triggered=self._save_file_as)

        file_menu.addActions([new_act, open_act, save_act, saveas_act])
        file_menu.addSeparator()
        exit_act = QtGui.QAction("Exit", self, triggered=self.close)
        file_menu.addAction(exit_act)

    def _build_edit_menu(self, mb):
        edit_menu = mb.addMenu("&Edit")

        undo_act = QtGui.QAction("Undo", self, shortcut="Ctrl+Z", triggered=lambda: self._editor_action("undo"))
        redo_act = QtGui.QAction("Redo", self, shortcut="Ctrl+Y", triggered=lambda: self._editor_action("redo"))
        cut_act = QtGui.QAction("Cut", self, shortcut="Ctrl+X", triggered=lambda: self._editor_action("cut"))
        copy_act = QtGui.QAction("Copy", self, shortcut="Ctrl+C", triggered=lambda: self._editor_action("copy"))
        paste_act = QtGui.QAction("Paste", self, shortcut="Ctrl+V", triggered=lambda: self._editor_action("paste"))
        find_act = QtGui.QAction("Find", self, shortcut="Ctrl+F", triggered=self._toggle_search)

        edit_menu.addActions([undo_act, redo_act])
        edit_menu.addSeparator()
        edit_menu.addActions([cut_act, copy_act, paste_act])
        edit_menu.addSeparator()
        edit_menu.addAction(find_act)

    # ------------------------------------------------------------------
    def _editor_action(self, action):
        editor = self.tabWidget.currentWidget()
        if not editor:
            return
        method = getattr(editor, action, None)
        if callable(method):
            method()

    # ------------------------------------------------------------------
    # --- Search System
    # ------------------------------------------------------------------
    def _toggle_search(self):
        self.searchBar.setVisible(not self.searchBar.isVisible())
        if self.searchBar.isVisible():
            self.searchEdit.setFocus()

    def _find_next(self, backward=False):
        editor = self.tabWidget.currentWidget()
        if not editor:
            return
        query = self.searchEdit.text()
        if not query:
            return
        flags = QtGui.QTextDocument.FindFlag(0)
        if backward:
            flags |= QtGui.QTextDocument.FindFlag.FindBackward
        found = editor.find(query, flags)
        if not found:
            # restart search from top
            cursor = editor.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start if not backward else QtGui.QTextCursor.End)
            editor.setTextCursor(cursor)
            editor.find(query, flags)

    # ------------------------------------------------------------------
    # --- File Ops
    # ------------------------------------------------------------------
    def _active_editor(self):
        """Return the current text editor widget."""
        return self.tabWidget.currentWidget()

    def _new_file(self):
        self.new_tab("untitled")
    
    def _open_file_dialog(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Python File", os.getcwd(), "Python Files (*.py)")
        if path:
            self._open_file_in_tab(path)

    def _save_file(self):
        editor = self.tabWidget.currentWidget()
        if not editor:
            return
        path = getattr(editor, "filePath", None)
        if not path:
            return self._save_file_as()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            self.statusBar().showMessage(f"💾 Saved: {os.path.basename(path)}", 3000)
        except Exception as e:
            self.console.append(f"[Save error] {e}\n")

    def _save_file_as(self):
        editor = self.tabWidget.currentWidget()
        if not editor:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", os.getcwd(), "Python Files (*.py)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            editor.filePath = path
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), os.path.basename(path))
            self.statusBar().showMessage(f"💾 Saved As: {os.path.basename(path)}", 3000)
        except Exception as e:
            self.console.append(f"[Save As error] {e}\n")
    
    def _show_about_dialog(self):
        about_text = (
            "<b>AI Script Editor — Personal Edition</b><br><br>"
            "A PySide6-based intelligent script editor for Autodesk Maya.<br>"
            "Features:<br>"
            "• Syntax highlighting<br>"
            "• Integrated AI chat (OpenAI GPT)<br>"
            "• Linting, run output, and explorer dock<br>"
            "• VS Code–style shortcuts and UI<br><br>"
            "<i>Developed by:</i> <b>MayJohn 'Mayj' Amilano</b><br>"
            "<i>GitHub:</i> <a href='https://github.com/YOUR_GITHUB_USERNAME/ai-script-editor'>github.com/YOUR_GITHUB_USERNAME/ai-script-editor</a><br>"
            "<i>Version:</i> 2.0 <br>"
        )
        QtWidgets.QMessageBox.about(self, "About AI Script Editor", about_text)



    # ------------------------------------------------------------------
    def new_tab(self, title="untitled", content=""):
        ed = CodeEditor()
        # set content if provided and ensure highlighter runs
        if content:
            try:
                ed.setPlainText(content)
                if hasattr(ed, "highlighter"):
                    try:
                        ed.highlighter.rehighlight()
                    except Exception:
                        pass
            except Exception:
                pass
        idx = self.tabWidget.addTab(ed, title)
        self.tabWidget.setCurrentIndex(idx)
        return ed

    def _close_tab(self, idx):
        w = self.tabWidget.widget(idx)
        self.tabWidget.removeTab(idx)
        w.deleteLater()

    # ------------------------------------------------------------------
    def _run_script(self):
        """Execute code from the active editor inside Maya."""
        import maya.utils, traceback
        ed = self.tabWidget.currentWidget()
        if not ed:
            return
        code = ed.toPlainTextSafe()
        self.console.clear()
        self.console.append("▶ Running script…\n")

        def run_in_maya():
            with redirect_output(self.console):
                try:
                    # execute with a proper globals dict so "__name__ == '__main__'"
                    g = {"__name__": "__main__", "__file__": "<AI Script Editor>"}
                    g["__builtins__"] = __builtins__
                    exec(compile(code, "<AI Script Editor>", "exec"), g, g)
                    print("\n✅ Execution finished.\n")
                except Exception:
                    traceback.print_exc()
            self.statusBar().showMessage("Ready", 3000)

        maya.utils.executeDeferred(run_in_maya)

    # ------------------------------------------------------------------
    def _lint_script(self):
        import ast
        ed = self.tabWidget.currentWidget()
        if not ed:
            return
        self.console.clear()
        self.console.append("🔍 Linting code...\n")
        try:
            ast.parse(ed.toPlainTextSafe())
            self.console.append("✅ No syntax errors detected.\n")
        except SyntaxError as e:
            self.console.append(f"❌ SyntaxError: {e.msg} at line {e.lineno}\n")


    # ------------------------------------------------------------------
    def _send_prompt(self):
        """Send a prompt to the AI Copilot, with editor context awareness and inline streaming."""
        prompt_text = self.prompt.text().strip()
        if not prompt_text:
            return

        editor = self.tabWidget.currentWidget()
        context = ""
        if editor:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                context = cursor.selectedText()
            else:
                # fallback: grab surrounding ~80 lines of context
                doc = editor.document()
                block = cursor.blockNumber()
                start = max(0, block - 40)
                end = min(doc.blockCount(), block + 40)
                for i in range(start, end):
                    context += doc.findBlockByNumber(i).text() + "\n"

        if not context.strip():
            context = "(No specific code context provided.)"

        full_prompt = f"You are assisting inside Maya’s Script Editor.\nUser’s request: {prompt_text}\n\nRelevant code context:\n{context}"

        # Warn if OpenAI client missing
        if not _CLIENT:
            self.chatDisplay.append(
                "⚠️ <i>OpenAI client not available.</i><br>"
                "Please set the environment variable <b>OPENAI_API_KEY</b> and ensure <b>openai>=1.0.0</b> is installed.\n"
            )
            return

        self.chatDisplay.append(f"<b>You:</b> {prompt_text}\n")
        self.prompt.clear()
        self.statusBar().showMessage("🧠 Thinking...")

        # Auto-scroll to bottom as the chat grows
        def scroll_to_bottom():
            self.chatDisplay.verticalScrollBar().setValue(
                self.chatDisplay.verticalScrollBar().maximum()
            )

        def stream_response():
            full_reply = ""
            code_mode = False
            ghost_buffer = ""
            try:
                stream_api = getattr(getattr(_CLIENT, "chat", None), "completions", None)
                if stream_api and hasattr(stream_api, "stream"):
                    with stream_api.stream(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": full_prompt}],
                        temperature=0.5,
                    ) as stream:
                        for event in stream:
                            frag = ""
                            try:
                                if getattr(event, "type", None) == "message.delta":
                                    frag = getattr(event.data.delta, "content", "") or ""
                                else:
                                    frag = getattr(event, "delta", "") or getattr(event, "content", "")
                            except Exception:
                                pass

                            if not frag:
                                continue

                            full_reply += frag
                            QtCore.QMetaObject.invokeMethod(
                                self.chatDisplay,
                                "insertPlainText",
                                QtCore.Qt.ConnectionType.QueuedConnection,
                                QtCore.Q_ARG(str, frag),
                            )
                            QtCore.QMetaObject.invokeMethod(
                                self.chatDisplay,
                                "ensureCursorVisible",
                                QtCore.Qt.ConnectionType.QueuedConnection,
                            )

                            # detect code blocks
                            if "```" in frag:
                                code_mode = not code_mode
                                if not code_mode and ghost_buffer:
                                    QtCore.QMetaObject.invokeMethod(
                                        editor,
                                        "show_ghost",
                                        QtCore.Qt.ConnectionType.QueuedConnection,
                                        QtCore.Q_ARG(str, ghost_buffer.strip()),
                                    )
                                    ghost_buffer = ""
                                continue

                            if code_mode:
                                ghost_buffer += frag

                            QtCore.QMetaObject.invokeMethod(
                                self.chatDisplay,
                                "verticalScrollBar",
                                QtCore.Qt.ConnectionType.QueuedConnection,
                            )

                    # Finished streaming
                    if ghost_buffer:
                        QtCore.QMetaObject.invokeMethod(
                            editor,
                            "show_ghost",
                            QtCore.Qt.ConnectionType.QueuedConnection,
                            QtCore.Q_ARG(str, ghost_buffer.strip()),
                        )

                else:
                    # fallback non-streaming (if using older API)
                    if stream_api and hasattr(stream_api, "create"):
                        resp = stream_api.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": full_prompt}],
                            temperature=0.6,
                        )
                        text = (
                            getattr(resp.choices[0].message, "content", None)
                            or resp["choices"][0]["message"]["content"]
                        )
                        full_reply = text
                        QtCore.QMetaObject.invokeMethod(
                            self.chatDisplay,
                            "append",
                            QtCore.Qt.ConnectionType.QueuedConnection,
                            QtCore.Q_ARG(str, text),
                        )
                    else:
                        raise RuntimeError("OpenAI client missing streaming/create API")

            except Exception as e:
                full_reply = f"[Error] {e}"
                QtCore.QMetaObject.invokeMethod(
                    self.chatDisplay,
                    "append",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                    QtCore.Q_ARG(str, full_reply),
                )
            finally:
                QtCore.QMetaObject.invokeMethod(
                    self.statusBar(),
                    "clearMessage",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                )
                QtCore.QMetaObject.invokeMethod(
                    self.chatDisplay,
                    "ensureCursorVisible",
                    QtCore.Qt.ConnectionType.QueuedConnection,
                )

        threading.Thread(target=stream_response, daemon=True).start()


    # ------------------------------------------------------------------
    def _open_folder_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder", os.getcwd())
        if folder:
            self._open_folder(folder)

    def _open_folder(self, folder):
        """Load a directory in the left explorer."""
        if not hasattr(self, "explorerView"):
            self.console.append("⚠️ Explorer not initialized.\n")
            return
        if not os.path.isdir(folder):
            self.console.append("⚠️ Invalid folder.\n")
            return
        try:
            self.hierarchyModel.build_from_folder(folder)
            self.explorerView.setModel(self.hierarchyModel)
            self.console.append(f"📂 Explorer root: {folder}\n")
        except Exception as e:
            self.console.append(f"[Folder error] {e}\n")
    
    def _on_explorer_double_clicked(self, index):
        """Handle double-clicks in Explorer to open files."""
        try:
            model = index.model()
            path = None
            line = None

            # Handle both hierarchy and file system models
            if hasattr(model, "itemFromIndex"):
                item = model.itemFromIndex(index)
                if item:
                    path = item.data(CodeHierarchyModel.FILE_ROLE)
                    line = item.data(CodeHierarchyModel.LINE_ROLE)
            if not path and hasattr(model, "filePath"):
                path = model.filePath(index)

            if path and os.path.isfile(path):
                self._open_file_in_tab(path, line)
        except Exception as e:
            self.console.append(f"[Explorer click error] {e}\n")
    
    def _open_file_in_tab(self, path, line=None):
        """Open a .py file in a new tab."""
        if not os.path.isfile(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        name = os.path.basename(path)
        ed = CodeEditor()
        ed.setPlainText(data)
        # ensure syntax highlighter updates immediately
        if hasattr(ed, "highlighter"):
            try:
                ed.highlighter.rehighlight()
            except Exception:
                pass
        idx = self.tabWidget.addTab(ed, name)
        self.tabWidget.setCurrentIndex(idx)
        if line:
             try:
                 ln = max(1, int(line)) - 1
                 c = ed.textCursor()
                 block = ed.document().findBlockByNumber(ln)
                 c.setPosition(block.position())
                 ed.setTextCursor(c)
             except Exception:
                 pass
        self.console.append(f"📄 Opened: {name}\n")

    def _apply_suggestion(self):
        """Apply the latest AI suggestion into the active editor (replace selection or insert)."""
        try:
            code = getattr(self, "latest_suggestion", None)
            if not code:
                try:
                    self.chatDisplay.append("<i>No suggestion available to apply.</i>\n")
                except Exception:
                    pass
                return
            ed = getattr(self, "tabWidget", None)
            if not ed:
                try:
                    self.chatDisplay.append("<i>No active editor to apply suggestion.</i>\n")
                except Exception:
                    pass
                return
            editor = self.tabWidget.currentWidget()
            if not editor:
                try:
                    self.chatDisplay.append("<i>No active editor to apply suggestion.</i>\n")
                except Exception:
                    pass
                return
            tc = editor.textCursor()
            if tc.hasSelection():
                tc.insertText(code)
            else:
                tc.insertText(code)
            editor.setTextCursor(tc)
            try:
                self.chatDisplay.append("<i>✅ Suggestion applied to editor.</i>\n")
            except Exception:
                pass
            # hide button and clear stored suggestion
            try:
                self.applySuggestionBtn.setVisible(False)
            except Exception:
                pass
            self.latest_suggestion = None
        except Exception as e:
            try:
                self.chatDisplay.append(f"[Apply error] {e}\n")
            except Exception:
                pass

def launch_ai_script_editor():
    """Module entrypoint for userSetup.py — instantiate and show the main window."""
    global _AI_SCRIPT_EDITOR_WINDOW
    try:
        if "_AI_SCRIPT_EDITOR_WINDOW" in globals() and _AI_SCRIPT_EDITOR_WINDOW is not None:
            try:
                _AI_SCRIPT_EDITOR_WINDOW.show()
            except Exception:
                pass
            return _AI_SCRIPT_EDITOR_WINDOW
    except Exception:
        pass

    try:
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    except Exception:
        app = None

    # Prefer explicit AiScriptEditor class
    WindowClass = globals().get("AiScriptEditor")
    if not WindowClass:
        # fallback: find first QMainWindow subclass (skip helper classes)
        import inspect
        for name, obj in globals().items():
            if inspect.isclass(obj):
                try:
                    if issubclass(obj, QtWidgets.QMainWindow) and obj.__name__ not in (
                        "LineNumberArea", "CodeEditor", "OutputConsole", "KeyChordManager", "CodeHierarchyModel", "PythonHighlighter"
                    ):
                        WindowClass = obj
                        break
                except Exception:
                    continue

    if not WindowClass:
        print("launch_ai_script_editor: no suitable main window class found in module")
        return None

    try:
        _AI_SCRIPT_EDITOR_WINDOW = WindowClass()
        _AI_SCRIPT_EDITOR_WINDOW.show()
        print(f"launch_ai_script_editor: launched {getattr(WindowClass, '__name__', str(WindowClass))}")
        return _AI_SCRIPT_EDITOR_WINDOW
    except Exception as e:
        print("launch_ai_script_editor: failed to create window:", e)
        return None


