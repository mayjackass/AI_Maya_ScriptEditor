# ai_script_editor/main_window.py
from functools import partial
import os, difflib, html
from PySide6 import QtCore, QtGui, QtWidgets

# --- Ensure OpenAI key is loaded before Morpheus init ---
settings = QtCore.QSettings("AI_Script_Editor", "settings")
stored_key = settings.value("OPENAI_API_KEY", "")
if stored_key:
    os.environ["OPENAI_API_KEY"] = stored_key
    print("🔑 OpenAI key injected successfully before Morpheus init.")
else:
    print("⚠️ No stored OpenAI key found. Set one via Settings → API Key.")

# Internal imports
from editor.code_editor import CodeEditor
from editor.highlighter import PythonHighlighter, MELHighlighter
from model.hierarchy import CodeHierarchyModel
from ui.output_console import OutputConsole
from ai.chat import AIMorpheus
from ai.copilot_manager import MorpheusManager

DARK_STYLE = """
QWidget { background: #1E1E1E; color: #DDD; font-family: Segoe UI, Consolas; }
QMenuBar, QMenu, QToolBar { font-size: 11pt; background-color:#2D2D30; }
QTextBrowser, QTextEdit { border: 1px solid #333; border-radius: 4px; }
QPushButton { background: #2D2D30; color: #EEE; border-radius: 4px; padding: 4px 8px; }
QPushButton:hover { background: #3E3E42; }
QLineEdit { background: #252526; border: 1px solid #333; color: #EEE; border-radius: 4px; padding: 3px; }
QDockWidget::title { background: #252526; padding: 4px; }
QTabBar::tab { background: #2D2D30; color: #DDD; padding: 6px 12px; border:1px solid #3E3E42; }
QTabBar::tab:selected { background: #3E3E42; }
"""

class AiScriptEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEO Script Editor v2.0")
        self.resize(1200, 700)
        self.setStyleSheet(DARK_STYLE)

        # --------------------------
        # Central Tabbed Editor with Language Selector
        # --------------------------
        centralWidget = QtWidgets.QWidget()
        centralLayout = QtWidgets.QVBoxLayout(centralWidget)
        centralLayout.setContentsMargins(0, 0, 0, 0)
        centralLayout.setSpacing(0)
        
        # Tab bar header with language selector
        tabHeader = QtWidgets.QWidget()
        tabHeaderLayout = QtWidgets.QHBoxLayout(tabHeader)
        tabHeaderLayout.setContentsMargins(8, 4, 8, 4)
        tabHeaderLayout.setSpacing(8)
        
        # Language selector with icons
        langLabel = QtWidgets.QLabel("Language:")
        langLabel.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        tabHeaderLayout.addWidget(langLabel)
        
        self.languageCombo = QtWidgets.QComboBox()
        self.languageCombo.addItem("🐍 Python", "Python")
        self.languageCombo.addItem("📜 MEL", "MEL") 
        self.languageCombo.setCurrentIndex(0)  # Default to Python
        self.languageCombo.setToolTip("Select script language")
        self.languageCombo.currentTextChanged.connect(self._language_changed)
        self.languageCombo.setStyleSheet("""
            QComboBox {
                background: #21262d;
                border: 1px solid #30363d;
                color: #f0f6fc;
                padding: 4px 8px;
                border-radius: 4px;
                min-width: 100px;
                font-size: 11px;
            }
            QComboBox:hover { border-color: #58a6ff; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: url(none); }
        """)
        tabHeaderLayout.addWidget(self.languageCombo)
        tabHeaderLayout.addStretch()
        
        centralLayout.addWidget(tabHeader)
        
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        centralLayout.addWidget(self.tabWidget)
        
        self.setCentralWidget(centralWidget)

        # --------------------------
        # Dock Widgets
        # --------------------------
        self._build_console_dock()  # Create console first
        self._build_problems_dock()
        self._build_explorer_dock()  # Now explorer can use console
        self._build_chat_dock()

        # --------------------------
        # Menu Bar & Toolbar
        # --------------------------
        self._build_menu()
        self._build_toolbar()

        # =======================================================
        # ✅ Load OpenAI API key FIRST before creating Morpheus
        # =======================================================
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        saved_key = settings.value("OPENAI_API_KEY", None)

        if saved_key:
            os.environ["OPENAI_API_KEY"] = str(saved_key)
            self.console.append("🔑 API key applied for session.\n")
        else:
            self.console.append("⚠️ No saved API key found. Set one under Settings → API Key.\n")

        # =======================================================
        # Now safely initialize Morpheus
        # =======================================================
        self.morpheus = AIMorpheus(self)
        if not self.morpheus.client:
            self.console.append("⚠️ No active OpenAI client. Set your API key via Settings → API Key.\n")
        
        # --------------------------
        # CoPython Manager
        # --------------------------
        self.morpheus_manager = MorpheusManager(self)
        self.morpheus_manager.contextUpdated.connect(lambda msg:
            self.console.append(f"[Memory Updated] {msg[:80]}...")
        )
        self.morpheus_manager.historyUpdated.connect(lambda: self._update_history_info())

        # Create one default tab
        self.new_tab("untitled", "")
        

    # =========================================================
    # Docks and UI Layout
    # =========================================================
    def _build_explorer_dock(self):
        self.hierarchyModel = CodeHierarchyModel()
        self.explorerView = QtWidgets.QTreeView()
        self.explorerView.setModel(self.hierarchyModel)
        self.explorerView.setHeaderHidden(True)
        self.explorerView.doubleClicked.connect(self._on_explorer_double_clicked)
        dock = QtWidgets.QDockWidget("Explorer", self)
        dock.setWidget(self.explorerView)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        
    def _on_explorer_double_clicked(self, index):
        """Handle double-click on explorer items to open files."""
        if not index.isValid():
            return
            
        # Get the file path from the model
        file_path = self.hierarchyModel.filePath(index)
        
        if file_path and os.path.isfile(file_path):
            # Check if it's a Python or MEL file
            if file_path.lower().endswith(('.py', '.mel')):
                try:
                    # Read the file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create a new tab with the file content
                    filename = os.path.basename(file_path)
                    editor = self.new_tab(filename, content)
                    
                    # Store the full file path in the editor for saving
                    editor.filename = file_path
                    
                    # Set the appropriate language based on file extension
                    if file_path.lower().endswith('.mel'):
                        self.languageCombo.setCurrentText("📜 MEL")
                    else:
                        self.languageCombo.setCurrentText("🐍 Python")
                    
                    self.console.append(f"📂 Opened file: {filename}")
                    
                except Exception as e:
                    self.console.append(f"❌ Error opening file {filename}: {str(e)}")
                    QtWidgets.QMessageBox.warning(self, "File Error", f"Could not open file:\n{str(e)}")

    def _build_problems_dock(self):
        self.problemsList = QtWidgets.QListWidget()
        dock = QtWidgets.QDockWidget("Problems", self)
        dock.setWidget(self.problemsList)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)

    def _build_console_dock(self):
        self.console = OutputConsole()
        dock = QtWidgets.QDockWidget("Output", self)
        dock.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)


    # ==========================================================
    # Morpheus Chat Dock  (Exact VS Code Replica)
    # ==========================================================
    def _build_chat_dock(self):
        """Create Morpheus AI chat interface matching VS Code's design exactly."""
        chatDock = QtWidgets.QDockWidget("Morpheus Chat", self)
        chatDock.setObjectName("MorpheusDock")
        chatDock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        chatDock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetMovable
        )

        # ---------- container
        chatWidget = QtWidgets.QWidget(chatDock)
        chatLayout = QtWidgets.QVBoxLayout(chatWidget)
        chatLayout.setContentsMargins(6, 6, 6, 6)
        chatLayout.setSpacing(6)

        # ---------- chat history navigation (at top)
        historyLayout = QtWidgets.QHBoxLayout()
        historyLayout.setSpacing(4)
        historyLayout.setContentsMargins(8, 4, 8, 4)
        
        # Navigation buttons
        self.prevChatBtn = QtWidgets.QPushButton("◀")
        self.prevChatBtn.setFixedSize(24, 24)
        self.prevChatBtn.setToolTip("Previous conversation")
        self.prevChatBtn.clicked.connect(self._prev_conversation)
        
        self.nextChatBtn = QtWidgets.QPushButton("▶")
        self.nextChatBtn.setFixedSize(24, 24)
        self.nextChatBtn.setToolTip("Next conversation")
        self.nextChatBtn.clicked.connect(self._next_conversation)
        
        # History info label
        self.historyLabel = QtWidgets.QLabel("1/1")
        self.historyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.historyLabel.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        # New chat button
        self.newChatBtn = QtWidgets.QPushButton("✨ New")
        self.newChatBtn.setToolTip("Start new conversation")
        self.newChatBtn.clicked.connect(self._new_conversation)
        
        historyLayout.addWidget(self.prevChatBtn)
        historyLayout.addWidget(self.historyLabel)
        historyLayout.addWidget(self.nextChatBtn)
        historyLayout.addStretch()
        historyLayout.addWidget(self.newChatBtn)
        
        chatLayout.addLayout(historyLayout)

        # ---------- chat history display
        self.chatHistory = QtWidgets.QTextBrowser()
        self.chatHistory.setOpenExternalLinks(False)
        self.chatHistory.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.chatHistory.setStyleSheet("""
            QTextBrowser {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        chatLayout.addWidget(self.chatHistory, 1)

        # ---------- input area
        inputWidget = QtWidgets.QWidget()
        inputLayout = QtWidgets.QVBoxLayout(inputWidget)
        inputLayout.setContentsMargins(0, 8, 0, 0)
        inputLayout.setSpacing(8)

        # Context checkbox
        self.contextCheckbox = QtWidgets.QCheckBox("📋 Include current code context")
        self.contextCheckbox.setChecked(True)
        self.contextCheckbox.setStyleSheet("""
            QCheckBox {
                color: #f0f6fc;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background: #238636;
                border: 1px solid #30363d;
                border-radius: 3px;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC45NyAwLjk3TDMuNzUgOC4xOUwxLjAzIDUuNDciIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        inputLayout.addWidget(self.contextCheckbox)

        # Text input area
        self.chatInput = QtWidgets.QTextEdit()
        self.chatInput.setPlaceholderText("Ask Morpheus anything about your code...")
        self.chatInput.setMaximumHeight(100)
        self.chatInput.setStyleSheet("""
            QTextEdit {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                color: #f0f6fc;
                font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #58a6ff;
            }
        """)
        self.chatInput.keyPressEvent = self._chat_key_press_event
        inputLayout.addWidget(self.chatInput)

        # Button area
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setSpacing(8)

        # Send button
        self.sendBtn = QtWidgets.QPushButton("Send")
        self.sendBtn.setStyleSheet("""
            QPushButton {
                background: #238636;
                border: 1px solid #30363d;
                color: white;
                padding: 6px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2ea043;
            }
            QPushButton:pressed {
                background: #1a6928;
            }
            QPushButton:disabled {
                background: #30363d;
                color: #8b949e;
            }
        """)
        self.sendBtn.clicked.connect(self._send_message)

        # Clear button
        clearBtn = QtWidgets.QPushButton("Clear")
        clearBtn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #30363d;
                color: #f0f6fc;
                padding: 6px 16px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #21262d;
                border-color: #58a6ff;
            }
        """)
        clearBtn.clicked.connect(self._clear_chat)

        buttonLayout.addStretch()
        buttonLayout.addWidget(clearBtn)
        buttonLayout.addWidget(self.sendBtn)
        inputLayout.addLayout(buttonLayout)

        chatLayout.addWidget(inputWidget)
        chatDock.setWidget(chatWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, chatDock)

        # Connect to morpheus manager
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.responseReady.connect(self._on_morpheus_response)

    # =========================================================
    # Menu
    # =========================================================
    def _build_menu(self):
        mb = self.menuBar()

        # File menu
        fileMenu = mb.addMenu("&File")
        fileMenu.addAction("New", lambda: self.new_tab("untitled", ""), QtGui.QKeySequence.New)
        fileMenu.addAction("Open...", self._open_file, QtGui.QKeySequence.Open)
        fileMenu.addAction("Save", self._save_file, QtGui.QKeySequence.Save)
        fileMenu.addAction("Save As...", self._save_file_as, QtGui.QKeySequence.SaveAs)
        fileMenu.addSeparator()
        fileMenu.addAction("Exit", self.close, QtGui.QKeySequence.Quit)

        # Edit menu
        editMenu = mb.addMenu("&Edit")
        editMenu.addAction("Undo", self._undo, QtGui.QKeySequence.Undo)
        editMenu.addAction("Redo", self._redo, QtGui.QKeySequence.Redo)
        editMenu.addSeparator()
        editMenu.addAction("Cut", self._cut, QtGui.QKeySequence.Cut)
        editMenu.addAction("Copy", self._copy, QtGui.QKeySequence.Copy)
        editMenu.addAction("Paste", self._paste, QtGui.QKeySequence.Paste)
        editMenu.addSeparator()
        editMenu.addAction("Find", self._editor_search, QtGui.QKeySequence.Find)
        editMenu.addAction("Find and Replace", self._show_find_replace, QtGui.QKeySequence("Ctrl+H"))

        # Run menu
        runMenu = mb.addMenu("&Run")
        runScriptAct = runMenu.addAction("Run Script", self._run_script, QtGui.QKeySequence("F5"))
        runScriptAct.setStatusTip("Run current script (Python or MEL)")
        runSelectionAct = runMenu.addAction("Run Selection", self._run_selection, QtGui.QKeySequence("F9"))
        runSelectionAct.setStatusTip("Run selected code (Python or MEL)")
        runMenu.addSeparator()
        runMenu.addAction("Clear Console", self._clear_console)

        # Tools menu
        toolsMenu = mb.addMenu("&Tools")
        toolsMenu.addAction("Format Code", self._format_code, QtGui.QKeySequence("Ctrl+Shift+F"))
        toolsMenu.addAction("Toggle Comments", self._toggle_comments, QtGui.QKeySequence("Ctrl+/"))
        toolsMenu.addSeparator()
        toolsMenu.addAction("Check Syntax Errors", self._check_syntax_errors, QtGui.QKeySequence("Ctrl+E"))
        toolsMenu.addAction("Clear Error Highlights", self._clear_error_highlights, QtGui.QKeySequence("Ctrl+Shift+E"))

        # View menu
        viewMenu = mb.addMenu("&View")
        for dock in self.findChildren(QtWidgets.QDockWidget):
            act = dock.toggleViewAction()
            viewMenu.addAction(act)

        # Settings menu
        settingsMenu = mb.addMenu("&Settings")
        apiKeyAct = QtGui.QAction("API Key...", self)
        apiKeyAct.triggered.connect(self._set_api_key_dialog)
        settingsMenu.addAction(apiKeyAct)
        
        # File menu - add Open Folder option
        fileMenu.addSeparator()
        openFolderAct = QtGui.QAction("Open Folder...", self)
        openFolderAct.triggered.connect(self._open_folder)
        fileMenu.addAction(openFolderAct)
        
        # Help menu
        helpMenu = mb.addMenu("&Help")
        aboutAct = QtGui.QAction("About NEO Script Editor", self)
        aboutAct.triggered.connect(self._show_about)
        helpMenu.addAction(aboutAct)

    # =========================================================
    # Toolbar
    # =========================================================
    def _build_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
        # File operations
        newAct = toolbar.addAction("📄 New", lambda: self.new_tab("untitled", ""))
        newAct.setShortcut(QtGui.QKeySequence.New)
        
        openAct = toolbar.addAction("📂 Open", self._open_file)
        openAct.setShortcut(QtGui.QKeySequence.Open)
        
        saveAct = toolbar.addAction("💾 Save", self._save_file)
        saveAct.setShortcut(QtGui.QKeySequence.Save)
        
        toolbar.addSeparator()
        
        # Run operations
        runAct = toolbar.addAction("▶️ Run", self._run_script)
        runAct.setShortcut(QtGui.QKeySequence("F5"))
        runAct.setToolTip("Run current script - Python or MEL (F5)")
        
        runSelAct = toolbar.addAction("🎯 Run Selection", self._run_selection)
        runSelAct.setShortcut(QtGui.QKeySequence("F9"))
        runSelAct.setToolTip("Run selected code - Python or MEL (F9)")
        
        toolbar.addSeparator()
        
        # Error checking operations
        errorAct = toolbar.addAction("🔍 Check Errors", self._check_syntax_errors)
        errorAct.setShortcut(QtGui.QKeySequence("Ctrl+E"))
        errorAct.setToolTip("Check for syntax errors (Ctrl+E)")
        
        clearErrorsAct = toolbar.addAction("✨ Clear Highlights", self._clear_error_highlights)
        clearErrorsAct.setShortcut(QtGui.QKeySequence("Ctrl+Shift+E"))
        clearErrorsAct.setToolTip("Clear error highlights (Ctrl+Shift+E)")
        
        toolbar.addSeparator()
        
        # Tools
        formatAct = toolbar.addAction("✨ Format", self._format_code)
        formatAct.setShortcut(QtGui.QKeySequence("Ctrl+Shift+F"))
        formatAct.setToolTip("Format code (Ctrl+Shift+F)")
        
        toolbar.addSeparator()
        
        # Console
        clearAct = toolbar.addAction("🗑️ Clear Console", self._clear_console)
        clearAct.setToolTip("Clear output console")

    # =========================================================
    # Tab + File System
    # =========================================================
    def new_tab(self, title, content=""):
        editor = CodeEditor()
        editor.setPlainText(content)
        
        # Set highlighter based on current language selection
        current_lang = "Python"  # Default
        if hasattr(self, 'languageCombo'):
            current_lang = self.languageCombo.currentData() or self.languageCombo.currentText()
            
        if "MEL" in current_lang:
            editor.highlighter = MELHighlighter(editor.document())
            tab_title = f"📜 {title}"
        else:
            editor.highlighter = PythonHighlighter(editor.document())
            tab_title = f"🐍 {title}"
        
        # Store the language in the editor for reference
        editor.setProperty("language", current_lang)
        
        # Connect editor signals for linting and autocomplete
        editor.textChanged.connect(lambda: self._on_text_changed(editor))
        editor.lintProblemsFound.connect(self._update_problems)
        
        # Enable autocomplete
        editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
        
        idx = self.tabWidget.addTab(editor, tab_title)
        self.tabWidget.setCurrentIndex(idx)
        return editor

    def _active_editor(self):
        w = self.tabWidget.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def _close_tab(self, index):
        widget = self.tabWidget.widget(index)
        self.tabWidget.removeTab(index)
        widget.deleteLater()
        if self.tabWidget.count() == 0:
            self.new_tab("untitled", "")

    def _open_file(self):
        file_filter = "All Script Files (*.py *.mel);;Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Script File", os.getcwd(), file_filter)
        if not path: return
        
        # Auto-detect language based on file extension
        if path.lower().endswith('.mel'):
            self.languageCombo.setCurrentText("MEL")
        elif path.lower().endswith('.py'):
            self.languageCombo.setCurrentText("Python")
            
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Check if file is already open
            for i in range(self.tabWidget.count()):
                editor = self.tabWidget.widget(i)
                if hasattr(editor, 'filename') and editor.filename == path:
                    self.tabWidget.setCurrentIndex(i)
                    return
                    
            editor = self.new_tab(os.path.basename(path), content)
            editor.filename = path
            self.console.append(f"📂 Opened: {os.path.basename(path)}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not open file: {str(e)}")

    def _open_folder(self):
        """Open a folder in the explorer."""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            # Update the hierarchy model with the selected folder
            self.hierarchyModel.setRootPath(folder_path)
            self.explorerView.setRootIndex(self.hierarchyModel.index(folder_path))
            
            if hasattr(self.console, 'append'):
                self.console.append(f"📁 Loaded folder: {folder_path}")
            else:
                print(f"[DEBUG] Loaded folder: {folder_path}")  # Fallback to print

    def _language_changed(self):
        """Handle language selection change."""
        current_editor = self._active_editor()
        if current_editor:
            current_lang = self.languageCombo.currentData() or self.languageCombo.currentText()
            
            # Update highlighter
            if "MEL" in current_lang:
                current_editor.highlighter = MELHighlighter(current_editor.document())
                icon = "📜"
            else:
                current_editor.highlighter = PythonHighlighter(current_editor.document())
                icon = "🐍"
            
            # Update tab title
            current_index = self.tabWidget.currentIndex()
            if current_index >= 0:
                current_title = self.tabWidget.tabText(current_index)
                # Remove existing icon and add new one
                title_without_icon = current_title.split(" ", 1)[1] if " " in current_title else current_title
                new_title = f"{icon} {title_without_icon}"
                self.tabWidget.setTabText(current_index, new_title)
            
            current_editor.setProperty("language", current_lang)

    # =========================================================
    # File Operations
    # =========================================================
    def _save_file(self):
        editor = self._active_editor()
        if not editor:
            return

        if hasattr(editor, 'filename') and editor.filename:
            # File already has a path, save directly
            try:
                with open(editor.filename, 'w', encoding='utf-8') as file:
                    file.write(editor.toPlainText())
                self.console.append(f"💾 Saved: {os.path.basename(editor.filename)}")
                editor.document().setModified(False)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Could not save file: {str(e)}")
        else:
            # New file, prompt for location
            self._save_file_as()

    def _save_file_as(self):
        editor = self._active_editor()
        if not editor:
            return

        file_filter = "Python Files (*.py);;MEL Files (*.mel);;All Files (*.*)"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File As", "", file_filter)
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(editor.toPlainText())
                
                editor.filename = path
                
                # Update tab title
                filename = os.path.basename(path)
                current_index = self.tabWidget.currentIndex()
                
                # Auto-detect language and set appropriate icon
                if path.lower().endswith('.mel'):
                    self.languageCombo.setCurrentText("📜 MEL")
                    tab_title = f"📜 {filename}"
                else:
                    self.languageCombo.setCurrentText("🐍 Python")
                    tab_title = f"🐍 {filename}"
                
                self.tabWidget.setTabText(current_index, tab_title)
                self.console.append(f"💾 Saved as: {filename}")
                editor.document().setModified(False)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Could not save file: {str(e)}")

    # =========================================================
    # Edit Operations
    # =========================================================
    def _undo(self):
        editor = self._active_editor()
        if editor:
            editor.undo()

    def _redo(self):
        editor = self._active_editor()
        if editor:
            editor.redo()

    def _cut(self):
        editor = self._active_editor()
        if editor:
            editor.cut()

    def _copy(self):
        editor = self._active_editor()
        if editor:
            editor.copy()

    def _paste(self):
        editor = self._active_editor()
        if editor:
            editor.paste()

    # =========================================================
    # Search & Replace
    # =========================================================
    def _editor_search(self):
        """Open search dialog."""
        editor = self._active_editor()
        if not editor:
            return
            
        text, ok = QtWidgets.QInputDialog.getText(self, "Find", "Search for:")
        if ok and text:
            if editor.find(text):
                self.console.append(f"🔍 Found: '{text}'")
            else:
                self.console.append(f"❌ Not found: '{text}'")
                
    def _show_find_replace(self):
        """Show find and replace dialog."""
        editor = self._active_editor()
        if not editor:
            return
            
        # Create find/replace dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Find and Replace")
        dialog.setModal(True)
        dialog.resize(400, 150)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Find field
        find_layout = QtWidgets.QHBoxLayout()
        find_layout.addWidget(QtWidgets.QLabel("Find:"))
        find_edit = QtWidgets.QLineEdit()
        find_layout.addWidget(find_edit)
        layout.addLayout(find_layout)
        
        # Replace field
        replace_layout = QtWidgets.QHBoxLayout()
        replace_layout.addWidget(QtWidgets.QLabel("Replace:"))
        replace_edit = QtWidgets.QLineEdit()
        replace_layout.addWidget(replace_edit)
        layout.addLayout(replace_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        find_btn = QtWidgets.QPushButton("Find")
        replace_btn = QtWidgets.QPushButton("Replace")
        replace_all_btn = QtWidgets.QPushButton("Replace All")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        
        button_layout.addWidget(find_btn)
        button_layout.addWidget(replace_btn)
        button_layout.addWidget(replace_all_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def find_text():
            if editor.find(find_edit.text()):
                self.console.append(f"🔍 Found: '{find_edit.text()}'")
            else:
                self.console.append(f"❌ Not found: '{find_edit.text()}'")
        
        def replace_text():
            cursor = editor.textCursor()
            if cursor.hasSelection():
                cursor.insertText(replace_edit.text())
                self.console.append(f"🔄 Replaced: '{find_edit.text()}' with '{replace_edit.text()}'")
        
        def replace_all_text():
            text = editor.toPlainText()
            find_str = find_edit.text()
            replace_str = replace_edit.text()
            
            if find_str in text:
                new_text = text.replace(find_str, replace_str)
                editor.setPlainText(new_text)
                count = text.count(find_str)
                self.console.append(f"🔄 Replaced {count} occurrences of '{find_str}' with '{replace_str}'")
            else:
                self.console.append(f"❌ Text '{find_str}' not found")
        
        find_btn.clicked.connect(find_text)
        replace_btn.clicked.connect(replace_text)
        replace_all_btn.clicked.connect(replace_all_text)
        cancel_btn.clicked.connect(dialog.close)
        
        dialog.show()

    # =========================================================
    # Code Execution
    # =========================================================
    def _run_script(self):
        """Execute the current script."""
        editor = self._active_editor()
        if not editor:
            return

        # Get current language
        current_lang = getattr(editor, 'language', None) or editor.property("language") or "Python"
        
        code = editor.toPlainText()
        if not code.strip():
            self.console.append("⚠️ No code to execute")
            return

        self.console.append(f"▶️ Running {current_lang} script...")
        
        if "MEL" in str(current_lang):
            self._execute_mel_code(code)
        else:
            self._execute_python_code(code)

    def _run_selection(self):
        """Execute only the selected code."""
        editor = self._active_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text.strip():
            self.console.append("⚠️ No code selected")
            return

        # Get current language
        current_lang = getattr(editor, 'language', None) or editor.property("language") or "Python"
        
        self.console.append(f"▶️ Running selected {current_lang} code...")
        
        if "MEL" in str(current_lang):
            self._execute_mel_code(selected_text)
        else:
            self._execute_python_code(selected_text)

    def _execute_python_code(self, code):
        """Execute Python code safely."""
        try:
            # Create a local namespace for execution
            local_namespace = {}
            
            # Execute the code
            exec(code, {"__name__": "__main__"}, local_namespace)
            self.console.append("✅ Python execution completed")
            
        except Exception as e:
            error_msg = f"❌ Python error: {str(e)}"
            self.console.append(error_msg)
            
            # Add to problems list
            self.problemsList.addItem(f"Runtime Error: {str(e)}")

    def _execute_mel_code(self, code):
        """Execute MEL code (Maya command language)."""
        try:
            # Check if we're in Maya environment
            try:
                import maya.mel as mel
                # Execute MEL command
                result = mel.eval(code)
                if result:
                    self.console.append(f"✅ MEL Result: {result}")
                else:
                    self.console.append("✅ MEL execution completed")
                    
            except ImportError:
                # Not in Maya environment
                self.console.append("⚠️ MEL execution requires Maya environment")
                self.console.append(f"📝 MEL Code: {code[:100]}..." if len(code) > 100 else f"📝 MEL Code: {code}")
                
        except Exception as e:
            error_msg = f"❌ MEL error: {str(e)}"
            self.console.append(error_msg)
            self.problemsList.addItem(f"MEL Error: {str(e)}")

    # =========================================================
    # Code Tools
    # =========================================================
    def _format_code(self):
        """Format the current code."""
        editor = self._active_editor()
        if not editor:
            return

        current_lang = getattr(editor, 'language', None) or editor.property("language") or "Python"
        
        if "Python" in str(current_lang):
            self._format_python_code(editor)
        else:
            self.console.append("⚠️ Code formatting only available for Python")

    def _format_python_code(self, editor):
        """Format Python code using basic indentation rules."""
        code = editor.toPlainText()
        
        try:
            # Basic Python formatting
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    formatted_lines.append('')
                    continue
                
                # Decrease indent for certain keywords
                if stripped.startswith(('except', 'elif', 'else', 'finally')):
                    current_indent = max(0, indent_level - 1)
                elif stripped.startswith(('return', 'break', 'continue', 'pass', 'raise')):
                    current_indent = indent_level
                else:
                    current_indent = indent_level
                
                # Add formatted line
                formatted_line = '    ' * current_indent + stripped
                formatted_lines.append(formatted_line)
                
                # Increase indent after certain keywords
                if stripped.endswith(':') and any(stripped.startswith(kw) for kw in 
                    ['def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']):
                    indent_level = current_indent + 1
            
            # Set formatted code
            formatted_code = '\n'.join(formatted_lines)
            editor.setPlainText(formatted_code)
            self.console.append("✨ Code formatted successfully")
            
        except Exception as e:
            self.console.append(f"❌ Formatting error: {str(e)}")

    def _toggle_comments(self):
        """Toggle comments on selected lines."""
        editor = self._active_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        
        # Get current language to determine comment syntax
        current_lang = getattr(editor, 'language', None) or editor.property("language") or "Python"
        comment_char = '//' if "MEL" in str(current_lang) else '#'
        
        # If no selection, work with current line
        if not cursor.hasSelection():
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
        
        selected_text = cursor.selectedText()
        lines = selected_text.split('\u2029')  # Qt uses this for line breaks in selected text
        
        # Check if lines are commented
        all_commented = all(line.strip().startswith(comment_char) for line in lines if line.strip())
        
        modified_lines = []
        for line in lines:
            if all_commented:
                # Uncomment
                if line.strip().startswith(comment_char):
                    # Find the comment character and remove it (with optional space)
                    comment_pos = line.find(comment_char)
                    new_line = line[:comment_pos] + line[comment_pos + len(comment_char):].lstrip(' ')
                    modified_lines.append(new_line)
                else:
                    modified_lines.append(line)
            else:
                # Comment
                if line.strip():  # Only comment non-empty lines
                    # Find first non-space character
                    first_char_pos = len(line) - len(line.lstrip())
                    new_line = line[:first_char_pos] + comment_char + ' ' + line[first_char_pos:]
                    modified_lines.append(new_line)
                else:
                    modified_lines.append(line)
        
        # Replace selected text
        new_text = '\u2029'.join(modified_lines)
        cursor.insertText(new_text)
        
        action = "Uncommented" if all_commented else "Commented"
        self.console.append(f"💬 {action} {len([l for l in lines if l.strip()])} lines")

    def _check_syntax_errors(self):
        """Check for syntax errors in the current code."""
        editor = self._active_editor()
        if not editor:
            return

        current_lang = getattr(editor, 'language', None) or editor.property("language") or "Python"
        code = editor.toPlainText()
        
        self.problemsList.clear()
        
        if "Python" in str(current_lang):
            self._check_python_syntax(code)
        elif "MEL" in str(current_lang):
            self._check_mel_syntax(code)

    def _check_python_syntax(self, code):
        """Check Python syntax."""
        try:
            compile(code, '<string>', 'exec')
            self.console.append("✅ No Python syntax errors found")
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            self.problemsList.addItem(f"Syntax Error: {error_msg}")
            self.console.append(f"❌ Python syntax error: {error_msg}")
        except Exception as e:
            error_msg = f"Compilation error: {str(e)}"
            self.problemsList.addItem(error_msg)
            self.console.append(f"❌ {error_msg}")

    def _check_mel_syntax(self, code):
        """Basic MEL syntax checking."""
        errors = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue
                
            # Basic MEL syntax checks
            if stripped.endswith(';'):
                continue
            elif any(stripped.startswith(kw) for kw in ['if', 'for', 'while', 'proc']):
                if not stripped.endswith('{') and '{' not in stripped:
                    errors.append(f"Line {i}: Missing opening brace after control statement")
            elif stripped == '}':
                continue
            else:
                errors.append(f"Line {i}: Missing semicolon")
        
        if errors:
            for error in errors:
                self.problemsList.addItem(f"MEL Syntax: {error}")
            self.console.append(f"❌ Found {len(errors)} MEL syntax issues")
        else:
            self.console.append("✅ No MEL syntax errors found")

    def _clear_error_highlights(self):
        """Clear error highlights from the editor."""
        self.problemsList.clear()
        self.console.append("✨ Error highlights cleared")

    def _clear_console(self):
        """Clear the output console."""
        self.console.clear()

    # =========================================================
    # Text Change Handling
    # =========================================================
    def _on_text_changed(self, editor):
        """Handle text changes for live linting."""
        # Basic implementation - you can enhance this
        pass

    def _update_problems(self, problems):
        """Update the problems list with linting results."""
        self.problemsList.clear()
        for problem in problems:
            self.problemsList.addItem(problem)

    # =========================================================
    # Chat Functions
    # =========================================================
    def _send_message(self):
        """Send message to Morpheus AI."""
        message = self.chatInput.toPlainText().strip()
        if not message:
            return

        # Add user message to history
        self._add_chat_message("You", message, "#58a6ff")
        
        # Clear input
        self.chatInput.clear()
        
        # Get context if requested
        context = ""
        if self.contextCheckbox.isChecked():
            editor = self._active_editor()
            if editor:
                context = editor.toPlainText()

        # Send to Morpheus
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.send_message(message, context)
        else:
            self._add_chat_message("Morpheus", "AI service not available. Please check your API key.", "#ff6b6b")

    def _add_chat_message(self, sender, message, color="#f0f6fc"):
        """Add a message to the chat history."""
        timestamp = QtCore.QTime.currentTime().toString("hh:mm")
        
        html_message = f"""
        <div style="margin-bottom: 12px; padding: 8px; border-left: 3px solid {color}; background: rgba(255,255,255,0.03);">
            <div style="color: {color}; font-weight: 600; margin-bottom: 4px;">
                {sender} <span style="color: #8b949e; font-size: 11px; font-weight: normal;">{timestamp}</span>
            </div>
            <div style="color: #f0f6fc; line-height: 1.4;">
                {html.escape(message).replace('\n', '<br>')}
            </div>
        </div>
        """
        
        self.chatHistory.insertHtml(html_message)
        
        # Scroll to bottom
        scrollbar = self.chatHistory.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _chat_key_press_event(self, event):
        """Handle key press events in chat input."""
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self._send_message()
        else:
            # Call parent method for normal text editing
            QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)

    def _clear_chat(self):
        """Clear chat history."""
        self.chatHistory.clear()

    def _on_morpheus_response(self, response):
        """Handle response from Morpheus AI."""
        self._add_chat_message("Morpheus", response, "#238636")

    def _new_conversation(self):
        """Start a new conversation."""
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.new_conversation()
        self._clear_chat()
        self._update_history_info()

    def _prev_conversation(self):
        """Go to previous conversation."""
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.previous_conversation()
            self._load_current_conversation()

    def _next_conversation(self):
        """Go to next conversation."""
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.next_conversation()
            self._load_current_conversation()

    def _load_current_conversation(self):
        """Load the current conversation history."""
        if hasattr(self, 'morpheus_manager'):
            history = self.morpheus_manager.get_current_conversation()
            self.chatHistory.clear()
            
            for entry in history:
                if entry['role'] == 'user':
                    self._add_chat_message("You", entry['content'], "#58a6ff")
                else:
                    self._add_chat_message("Morpheus", entry['content'], "#238636")

    def _update_history_info(self):
        """Update the history navigation info."""
        if hasattr(self, 'morpheus_manager'):
            current, total = self.morpheus_manager.get_conversation_info()
            self.historyLabel.setText(f"{current}/{total}")
            
            # Enable/disable navigation buttons
            self.prevChatBtn.setEnabled(current > 1)
            self.nextChatBtn.setEnabled(current < total)

    # =========================================================
    # Settings
    # =========================================================
    def _set_api_key_dialog(self):
        """Show API key setting dialog."""
        current_key = os.environ.get("OPENAI_API_KEY", "")
        
        dialog = QtWidgets.QInputDialog()
        dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        dialog.setTextEchoMode(QtWidgets.QLineEdit.Password)
        dialog.setWindowTitle("Set OpenAI API Key")
        dialog.setLabelText("Enter your OpenAI API Key:")
        dialog.setTextValue(current_key)
        
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            api_key = dialog.textValue().strip()
            
            if api_key:
                # Save to settings
                settings = QtCore.QSettings("AI_Script_Editor", "settings")
                settings.setValue("OPENAI_API_KEY", api_key)
                
                # Set environment variable
                os.environ["OPENAI_API_KEY"] = api_key
                
                try:
                    # Reinitialize Morpheus
                    self.morpheus = AIMorpheus(self)
                    
                    if self.morpheus.client:
                        self.console.append("✅ API key updated successfully!")
                        self.console.append("✅ OpenAI client reinitialized successfully.\n")
                    else:
                        self.console.append("⚠️ Failed to initialize OpenAI client.\n")
                except Exception as e:
                    self.console.append(f"❌ API key update error: {e}\n")

    def _show_about(self):
        """Show About dialog."""
        about_text = """
        <h2>NEO Script Editor v2.0</h2>
        <p><b>Advanced Python & MEL Script Editor for Maya</b></p>
        <p>Features:</p>
        <ul>
            <li>🐍 Python & MEL syntax highlighting</li>
            <li>🤖 AI-powered Morpheus chat assistant</li>
            <li>📁 File explorer with project management</li>
            <li>🔍 Advanced search and replace</li>
            <li>✨ Code formatting and linting</li>
            <li>🎯 Smart code execution</li>
        </ul>
        <p>Built with PySide6 and OpenAI GPT-4</p>
        """
        
        QtWidgets.QMessageBox.about(self, "About NEO Script Editor", about_text)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = AiScriptEditor()
    win.show()
    app.exec()