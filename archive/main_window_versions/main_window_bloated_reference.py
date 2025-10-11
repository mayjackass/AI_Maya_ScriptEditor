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
        self.tabWidget.currentChanged.connect(self._on_tab_changed)
        centralLayout.addWidget(self.tabWidget)
        
        self.setCentralWidget(centralWidget)

        # --------------------------
        # Floating Code Actions (GitHub Copilot Style)
        # --------------------------
        self._setup_floating_code_actions()

        # --------------------------
        # Dock Widgets
        # --------------------------
        self._build_console_dock()  # Create console first
        self._build_problems_dock_safe()  # Re-enabled with safety checks
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
        self.morpheus_manager.historyUpdated.connect(self._on_history_updated)
        # Connect response signal immediately
        self.morpheus_manager.responseReady.connect(self._on_morpheus_response)

        # Create one default tab
        self.new_tab("untitled", "")
        
        # Initialize code blocks storage for action buttons
        self._code_blocks = {}
        
        # Initialize preview state
        self._preview_applied = False
        self._original_content = ""
        self._original_cursor_position = 0
        self._preview_changes = []
        
        # Add Morpheus introduction after UI is ready
        QtCore.QTimer.singleShot(1000, self._morpheus_introduction)
        
        # Ensure floating actions are initially hidden
        if hasattr(self, 'floatingActions'):
            self.floatingActions.setVisible(False)

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

    def _build_problems_dock_safe(self):
        """Build problems dock with comprehensive error handling."""
        try:
            print("🔧 Creating Problems dock...")
            
            # Create the tree widget
            self.problemsList = QtWidgets.QTreeWidget()
            print("   ✅ TreeWidget created")
            
            # Set headers
            self.problemsList.setHeaderLabels(["Type", "Message", "Line", "File"])
            self.problemsList.setRootIsDecorated(False)
            self.problemsList.setAlternatingRowColors(True)
            print("   ✅ Headers and properties set")
            
            # Connect signals safely
            try:
                self.problemsList.itemDoubleClicked.connect(self._on_problem_double_clicked)
                print("   ✅ Double-click signal connected")
            except Exception as e:
                print(f"   ⚠️ Double-click connection failed: {e}")
            
            # Apply styling safely
            try:
                self.problemsList.setStyleSheet("""
                    QTreeWidget {
                        background-color: #252526;
                        color: #cccccc;
                        border: none;
                        font-size: 11px;
                    }
                    QTreeWidget::item {
                        padding: 4px;
                        border-bottom: 1px solid #3c3c3c;
                    }
                    QTreeWidget::item:selected {
                        background-color: #094771;
                    }
                    QHeaderView::section {
                        background-color: #2d2d30;
                        color: #cccccc;
                        padding: 4px;
                        border: 1px solid #3c3c3c;
                    }
                """)
                print("   ✅ Styling applied")
            except Exception as e:
                print(f"   ⚠️ Styling failed: {e}")
                
            # Create dock widget
            dock = QtWidgets.QDockWidget("Problems", self)
            dock.setWidget(self.problemsList)
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
            print("   ✅ Dock widget added")
            
            # Initialize problems list safely
            try:
                self.clear_problems()
                print("   ✅ Problems list initialized")
            except Exception as e:
                print(f"   ⚠️ Problems initialization failed: {e}")
                
            print("✅ Problems dock created successfully")
            
        except Exception as e:
            print(f"❌ Problems dock creation failed: {e}")
            # Create a simple fallback
            try:
                self.problemsList = QtWidgets.QListWidget()
                simple_dock = QtWidgets.QDockWidget("Problems (Simple)", self)
                simple_dock.setWidget(self.problemsList)
                self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, simple_dock)
                print("✅ Fallback problems list created")
            except Exception as fallback_error:
                print(f"❌ Even fallback failed: {fallback_error}")
                self.problemsList = None

    def clear_problems(self):
        """Clear the problems list safely."""
        try:
            if hasattr(self, 'problemsList') and self.problemsList:
                if isinstance(self.problemsList, QtWidgets.QTreeWidget):
                    self.problemsList.clear()
                elif isinstance(self.problemsList, QtWidgets.QListWidget):
                    self.problemsList.clear()
        except Exception as e:
            print(f"⚠️ Failed to clear problems: {e}")

    def _build_console_dock(self):
        self.console = OutputConsole()
        
        # Enable output capture by default for better user experience
        self.console.enable_output_capture()
        
        # Add a test message to demonstrate the enhanced console
        test_code = """# NEO Script Editor Enhanced Console Test
print("🎯 Console output capture is working!")
print("✨ This is just like Maya's Script Editor")
for i in range(3):
    print(f"   → Test output {i+1}")
    
# Test variables
result = 42 * 2
print(f"🔢 Calculation result: {result}")
"""
        self.console.execute_code_and_capture(test_code, "python")
        
        dock = QtWidgets.QDockWidget("Output Console", self)
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
        
        # Connect link clicked signal for code action buttons
        self.chatHistory.anchorClicked.connect(self._handle_code_action)
        
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

        # ---------- response indicator
        self.responseIndicator = QtWidgets.QLabel()
        self.responseIndicator.setText("🤖 Morpheus is thinking...")
        self.responseIndicator.setStyleSheet("""
            QLabel {
                color: #58a6ff;
                font-size: 12px;
                font-style: italic;
                padding: 4px 8px;
                background: rgba(88, 166, 255, 0.1);
                border: 1px solid rgba(88, 166, 255, 0.3);
                border-radius: 4px;
            }
        """)
        self.responseIndicator.setVisible(False)  # Hidden by default
        chatLayout.addWidget(self.responseIndicator)

        # Animation timer for thinking indicator
        self.thinkingTimer = QtCore.QTimer()
        self.thinkingTimer.timeout.connect(self._animate_thinking)
        self.thinkingDots = 0

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
        self.chatInput.setPlaceholderText("Ask Morpheus anything about your code... (Press Enter to send, Shift+Enter for new line)")
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

        # Signal connection is now made earlier in constructor

    def resizeEvent(self, event):
        """Handle window resize to reposition floating actions."""
        super().resizeEvent(event)
        if hasattr(self, 'floatingActions'):
            self._position_floating_actions()

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
        
        # Optional auto syntax checking (enabled with lightweight highlighting)
        auto_check_enabled = True  # Lightweight VS Code-style error detection
        
        if auto_check_enabled:
            if not hasattr(editor, '_syntax_timer'):
                editor._syntax_timer = QtCore.QTimer()
                editor._syntax_timer.setSingleShot(True)
                editor._syntax_timer.timeout.connect(lambda: self._auto_check_syntax(editor))
            
            editor.textChanged.connect(lambda: editor._syntax_timer.start(800))  # 800ms - VS Code-like responsiveness
        
        # Re-enable problems connection if available
        if hasattr(editor, 'lintProblemsFound'):
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
    
    def _on_tab_changed(self, index):
        """Handle tab change to reposition floating actions."""
        if hasattr(self, 'floatingActions') and self.floatingActions.isVisible():
            # Small delay to ensure tab switch is complete
            QtCore.QTimer.singleShot(10, self._position_floating_actions)

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
        """Execute Python code with Maya-style console output capture."""
        try:
            # Use the enhanced console's execution method
            self.console.execute_code_and_capture(code, "python")
            
        except Exception as e:
            # Fallback error handling
            error_msg = f"❌ Execution system error: {str(e)}"
            self.console.append_tagged("ERROR", error_msg, "#f66")
            
            # Add to problems list
            self.problemsList.addItem(f"System Error: {str(e)}")

    def _execute_mel_code(self, code):
        """Execute MEL code with Maya-style console output capture."""
        try:
            # Use the enhanced console's execution method
            self.console.execute_code_and_capture(code, "mel")
                
        except Exception as e:
            error_msg = f"❌ MEL system error: {str(e)}"
            self.console.append_tagged("ERROR", error_msg, "#f66")
            self.problemsList.addItem(f"MEL System Error: {str(e)}")

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

    def _auto_check_syntax(self, editor):
        """VS Code-style syntax checking - fast and silent."""
        if not editor:
            return
            
        try:
            code = editor.toPlainText().strip()
            
            if not code:
                self.clear_problems()
                self._clear_error_highlights(editor)
                return
                
            if len(code) > 2000:
                return
                
            problems = self._get_python_syntax_errors_fast(code)
            
            # Update UI silently
            self._update_problems(problems)
            self._highlight_syntax_errors(editor, problems)
            
        except Exception:
            pass

    def _check_syntax_errors(self):
        """Manually check for syntax errors in the current code."""
        editor = self._active_editor()
        if not editor:
            return

        # Force immediate syntax check 
        code = editor.toPlainText()
        problems = self._get_python_syntax_errors(code)  # Use full detection for manual check
        
        # Update problems panel
        self._update_problems(problems)
        
        # Force visual highlighting
        self._highlight_syntax_errors(editor, problems)
        
        # Console feedback only
        if problems:
            self.console.append(f"❌ Found {len(problems)} syntax errors:")
            for i, p in enumerate(problems[:5], 1):  # Show first 5 errors
                self.console.append(f"   {i}. Line {p['line']}: {p['message']}")
            if len(problems) > 5:
                self.console.append(f"   ... and {len(problems) - 5} more errors")
        else:
            self.console.append("✅ No syntax errors found")

    def _get_python_syntax_errors_fast(self, code):
        """VS Code-style multiple error detection - fast and comprehensive."""
        problems = []
        
        if not code.strip():
            return problems
        
        lines = code.split('\n')
        
        # Multi-pass approach like VS Code
        temp_code = code
        error_lines = set()
        
        # Pass 1: Get all compile errors by iteratively fixing them
        for attempt in range(5):  # Limit attempts
            try:
                compile(temp_code, '<string>', 'exec')
                break
            except SyntaxError as e:
                if e.lineno and e.lineno not in error_lines:
                    problems.append({
                        'type': 'Error',
                        'message': e.msg or 'Syntax error',
                        'line': e.lineno,
                        'file': 'Current File'
                    })
                    error_lines.add(e.lineno)
                    
                    # Fix this line temporarily to find more errors
                    temp_lines = temp_code.split('\n')
                    if 1 <= e.lineno <= len(temp_lines):
                        temp_lines[e.lineno - 1] = f"# FIXED: {temp_lines[e.lineno - 1]}"
                        temp_code = '\n'.join(temp_lines)
                else:
                    break
        
        # Pass 2: Quick pattern check for missed errors  
        for i, line in enumerate(lines, 1):
            if i in error_lines:
                continue
                
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue
                
            # Common syntax errors VS Code catches
            if (line_stripped.startswith(('if ', 'elif ', 'def ', 'for ', 'while ', 'class ')) 
                and not line_stripped.endswith(':') and not line_stripped.endswith('\\')):
                problems.append({
                    'type': 'Error',
                    'message': 'Missing colon after statement',
                    'line': i,
                    'file': 'Current File'
                })
            elif line_stripped.endswith(('+', '-', '*', '/', '=')):
                problems.append({
                    'type': 'Error', 
                    'message': 'Incomplete expression',
                    'line': i,
                    'file': 'Current File'
                })
        
        return problems[:10]  # Limit to 10 errors like VS Code
    
    def _get_python_syntax_errors(self, code):
        """Get ALL Python syntax errors using MULTI-PASS enhanced detection."""
        problems = []
        
        if not code.strip():
            return problems
        
        lines = code.split('\n')
        
        # PASS 1: Collect ALL compile errors by fixing and re-checking
        remaining_code = code
        checked_lines = set()
        
        for attempt in range(10):  # Limit attempts to prevent infinite loop
            try:
                compile(remaining_code, '<string>', 'exec')
                break  # No more compile errors
            except SyntaxError as e:
                if e.lineno and e.lineno not in checked_lines:
                    problems.append({
                        'type': 'Error', 
                        'message': e.msg or 'Syntax error',
                        'line': e.lineno,
                        'file': 'Current File'
                    })
                    checked_lines.add(e.lineno)
                    
                    # Try to fix this error and continue checking
                    temp_lines = remaining_code.split('\n')
                    if 1 <= e.lineno <= len(temp_lines):
                        # Comment out the error line to find more errors
                        temp_lines[e.lineno - 1] = f"# TEMP_FIX: {temp_lines[e.lineno - 1]}"
                        remaining_code = '\n'.join(temp_lines)
                else:
                    break  # Same line error, stop to prevent loop
        
        # PASS 2: Pattern-based detection for additional issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            # Skip if already found by compiler
            if any(p['line'] == i for p in problems):
                continue
                
            error_found = False
            error_msg = ""
            
            # Check for missing colons after control statements
            if (line_stripped.startswith(('if ', 'elif ', 'for ', 'while ', 'def ', 'class ', 'try:', 'except', 'finally:', 'with ')) 
                and not line_stripped.endswith(':') and not line_stripped.endswith('\\') 
                and 'else:' not in line_stripped):
                error_found = True
                error_msg = 'Missing colon after control statement'
                
            # Check for incomplete expressions (ending with operators)
            elif line_stripped.endswith(('+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', 'and', 'or')):
                error_found = True
                error_msg = 'Incomplete expression'
                
            # Check for unclosed parentheses/brackets
            elif ('(' in line_stripped and ')' not in line_stripped and 
                  not line_stripped.endswith(('\\', ',', ':'))):
                error_found = True
                error_msg = 'Unclosed parenthesis'
                
            # Check for invalid indentation patterns
            elif line_stripped and i > 1:
                prev_line = lines[i-2].strip() if i > 1 else ""
                if (prev_line.endswith(':') and line_stripped and 
                    not line.startswith('    ') and not line.startswith('\t')):
                    error_found = True
                    error_msg = 'Expected indented block'
            
            # Add error if found
            if error_found:
                problems.append({
                    'type': 'Error',
                    'message': error_msg,
                    'line': i,
                    'file': 'Current File'
                })
            
        return problems
    
    def _highlight_syntax_errors(self, editor, problems):
        """VS Code-style multiple error highlighting - precise and efficient."""
        try:
            # Clear previous highlights
            editor.setExtraSelections([])
            
            # Store error lines for line numbers
            if not hasattr(editor, '_error_lines'):
                editor._error_lines = set()
            editor._error_lines.clear()
            
            if not problems:
                return
            
            # VS Code-style error format
            error_format = QtGui.QTextCharFormat()
            error_format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
            error_format.setUnderlineColor(QtGui.QColor("#ff0000"))
            
            selections = []
            document = editor.document()
            
            # Highlight up to 5 errors like VS Code
            for problem in problems[:5]:
                line_num = problem.get('line', 1) - 1
                if line_num < 0:
                    continue
                    
                editor._error_lines.add(line_num)
                
                block = document.findBlockByNumber(line_num)
                if not block.isValid():
                    continue
                    
                line_text = block.text()
                stripped = line_text.strip()
                if not stripped:
                    continue
                
                msg = problem.get('message', '').lower()
                
                # VS Code-style precise error positioning
                if 'missing colon' in msg or 'expected' in msg:
                    # Underline end of statement where colon should be
                    start_pos = len(line_text.rstrip()) - 1
                    length = 1
                elif 'incomplete' in msg:
                    # Find the problematic operator
                    for op in ['+', '-', '*', '/', '=']:
                        pos = line_text.rfind(op)
                        if pos >= 0:
                            start_pos = pos
                            length = 1
                            break
                    else:
                        start_pos = len(line_text.rstrip()) - 1
                        length = 1
                elif 'parenthesis' in msg or 'bracket' in msg:
                    # Find unclosed bracket
                    for char in ['(', '[', '{']:
                        pos = line_text.find(char)
                        if pos >= 0:
                            start_pos = pos
                            length = 1
                            break
                    else:
                        start_pos = len(line_text) - len(line_text.lstrip())
                        length = len(stripped)
                else:
                    # Default: underline the problematic token
                    start_pos = len(line_text) - len(line_text.lstrip())
                    first_word = stripped.split()[0] if stripped.split() else stripped
                    length = min(len(first_word), len(stripped))
                
                # Create precise selection
                cursor = QtGui.QTextCursor(block)
                cursor.setPosition(block.position() + start_pos)
                cursor.setPosition(block.position() + start_pos + length, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format = error_format
                selection.cursor = cursor
                selections.append(selection)
            
            # Apply all selections at once
            editor.setExtraSelections(selections)
                
        except Exception:
            pass
    
    def _clear_error_highlights(self, editor):
        """Clear all error highlighting from the editor."""
        try:
            print("🧹 Clearing error highlights...")
            
            if hasattr(editor, '_error_selections'):
                editor._error_selections = []
                
            if hasattr(editor, '_error_lines'):
                editor._error_lines.clear()
                
            # Clear all extra selections to remove error highlights
            editor.setExtraSelections([])
            print("  ✅ Cleared all extra selections")
                
            # Trigger line number area repaint
            if hasattr(editor, 'number_area'):
                editor.number_area.update()
        except Exception as e:
            print(f"Error clearing highlights: {e}")
        
    def _check_python_syntax(self, code):
        """Legacy method - check Python syntax and update console."""
        problems = self._get_python_syntax_errors(code)
        
        if problems:
            for problem in problems:
                self.console.append(f"❌ Python syntax error: Line {problem['line']}: {problem['message']}")
        else:
            self.console.append("✅ No Python syntax errors found")

    def _get_mel_syntax_errors(self, code):
        """Get MEL syntax errors as problem objects."""
        problems = []
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
                    problems.append({
                        'type': 'Error',
                        'message': 'Missing opening brace after control statement',
                        'line': i,
                        'file': 'Current File'
                    })
            elif stripped == '}':
                continue
            else:
                problems.append({
                    'type': 'Error',
                    'message': 'Missing semicolon',
                    'line': i,
                    'file': 'Current File'
                })
                
        return problems
        
    def _check_mel_syntax(self, code):
        """Legacy method - check MEL syntax and update console."""
        problems = self._get_mel_syntax_errors(code)
        
        if problems:
            for problem in problems:
                self.console.append(f"❌ MEL syntax issue: Line {problem['line']}: {problem['message']}")
        else:
            self.console.append("✅ No MEL syntax issues found")



    def _clear_console(self):
        """Clear the output console."""
        self.console.clear()

    # =========================================================
    # Text Change Handling
    # =========================================================
    def _on_text_changed(self, editor):
        """Handle text changes for live linting."""
        try:
            print(f"📝 Text changed in editor, starting syntax check timer...")
            
            # Clear any previous timer
            if hasattr(editor, '_syntax_timer') and editor._syntax_timer:
                editor._syntax_timer.stop()
                
            # Start new timer for debounced syntax checking
            if hasattr(editor, '_syntax_timer'):
                editor._syntax_timer.start(3000)  # 3 second delay
                print("  ✅ Syntax check timer started (1 second)")
            else:
                print("  ❌ No syntax timer found on editor")
                
        except Exception as e:
            print(f"❌ Error in text changed handler: {e}")
            import traceback
            traceback.print_exc()

    def _update_problems(self, problems):
        """Update the problems list with linting results."""
        try:
            if not hasattr(self, 'problemsList') or not self.problemsList:
                print("⚠️ Problems list not available")
                return
                
            self.problemsList.clear()
            
            for problem in problems:
                if isinstance(self.problemsList, QtWidgets.QTreeWidget):
                    # Create tree widget item with proper columns
                    item = QtWidgets.QTreeWidgetItem()
                    
                    # Set the columns: Type, Message, Line, File
                    item.setText(0, problem.get('type', 'Error'))  # Type (Error/Warning)
                    item.setText(1, problem.get('message', 'Unknown error'))  # Message
                    item.setText(2, str(problem.get('line', 0)))  # Line number as text
                    item.setText(3, problem.get('file', 'Current File'))  # File name
                    
                    # Store line number as user data for navigation
                    item.setData(2, QtCore.Qt.UserRole, problem.get('line', 0))
                    
                    # Set error icon and color
                    if problem.get('type') == 'Error':
                        item.setForeground(0, QtGui.QBrush(QtGui.QColor("#f48771")))  # Red for errors
                    else:
                        item.setForeground(0, QtGui.QBrush(QtGui.QColor("#ffcc02")))  # Yellow for warnings
                    
                    self.problemsList.addTopLevelItem(item)
                    
                elif isinstance(self.problemsList, QtWidgets.QListWidget):
                    # Fallback to simple list widget
                    problem_text = f"{problem.get('type', 'Error')}: {problem.get('message', 'Unknown error')} (Line {problem.get('line', 0)})"
                    self.problemsList.addItem(problem_text)
            
            # Update window title with error count
            error_count = len([p for p in problems if p.get('type') == 'Error'])
            warning_count = len([p for p in problems if p.get('type') == 'Warning'])
            
            if error_count > 0 or warning_count > 0:
                status = f"Problems: {error_count} errors, {warning_count} warnings"
                self.statusBar().showMessage(status)
            else:
                self.statusBar().showMessage("No problems detected")
                
        except Exception as e:
            print(f"❌ Error updating problems: {e}")
            # Try to show error in status bar at least
            try:
                self.statusBar().showMessage("Error updating problems list")
            except:
                pass

    def _on_problem_double_clicked(self, item, column):
        """Navigate to the line when a problem is double-clicked."""
        try:
            if not item:
                return
                
            line_number = None
            
            # Handle TreeWidget items
            if hasattr(item, 'data') and callable(item.data):
                line_number = item.data(2, QtCore.Qt.UserRole)  # Line number stored as user data
            
            # Handle ListWidget items (fallback)
            elif hasattr(item, 'text'):
                # Try to extract line number from text
                import re
                text = item.text()
                match = re.search(r'Line (\d+)', text)
                if match:
                    line_number = int(match.group(1))
            
            if line_number is not None and line_number > 0:
                # Get current editor
                current_editor = self._get_current_editor()
                if current_editor:
                    # Navigate to the line (convert to 0-based index)
                    cursor = current_editor.textCursor()
                    cursor.movePosition(QtGui.QTextCursor.Start)
                    cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, line_number - 1)
                    current_editor.setTextCursor(cursor)
                    current_editor.centerCursor()
                    current_editor.setFocus()
                    print(f"✅ Navigated to line {line_number}")
                    
        except Exception as e:
            print(f"❌ Problem navigation failed: {e}")

    # =========================================================
    # Chat Functions
    # =========================================================
    def _send_message(self):
        """Send message to Morpheus AI."""
        message = self.chatInput.toPlainText().strip()
        if not message:
            return

        # Hide any existing floating actions
        self._hide_floating_actions()

        # Add user message to history
        self._add_chat_message("You", message, "#58a6ff")
        
        # Show response indicator and start animation
        self._show_thinking_indicator()
        
        # Clear input
        self.chatInput.clear()
        
        # Disable send button while processing
        self.sendBtn.setEnabled(False)
        
        # Get context if requested OR if asking about code analysis
        context = ""
        editor = self._active_editor()
        
        # Auto-include current code if asking about errors, syntax, bugs, or fixes
        auto_context_keywords = ['error', 'syntax', 'bug', 'fix', 'wrong', 'issue', 'problem', 'incorrect', 'mistake']
        should_auto_include = any(keyword in message.lower() for keyword in auto_context_keywords)
        
        if self.contextCheckbox.isChecked() or should_auto_include:
            if editor:
                context = editor.toPlainText()
                if should_auto_include and not self.contextCheckbox.isChecked():
                    # Auto-included context, let user know
                    self.console.append_tagged("SYSTEM", "🔍 Auto-included current code for analysis", "#858585")

        # Send to Morpheus
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.send_message(message, context)
        else:
            self._add_chat_message("Morpheus", "AI service not available. Please check your API key.", "#ff6b6b")
            self._hide_thinking_indicator()

    def _add_chat_message(self, sender, message, color="#f0f6fc"):
        """Add a message to the chat history with enhanced code formatting and actions."""
        timestamp = QtCore.QTime.currentTime().toString("hh:mm")
        
        try:
            # Check if this is a Morpheus message that might contain code
            if sender == "Morpheus":
                formatted_message = self._format_morpheus_message(message)
            else:
                # Simple formatting for user messages
                formatted_message = html.escape(message).replace('\n', '<br>')
            
            # Create message container
            html_message = f"""
            <div style="margin-bottom: 16px; padding: 8px; border-left: 3px solid {color}; background: rgba(255,255,255,0.03);">
                <div style="color: {color}; font-weight: 600; margin-bottom: 4px;">
                    {sender} <span style="color: #8b949e; font-size: 11px; font-weight: normal;">{timestamp}</span>
                </div>
                <div style="color: #f0f6fc; line-height: 1.4;">
                    {formatted_message}
                </div>
            </div>
            <br>
            """
            
            # Store current content and append new message
            current_content = self.chatHistory.toHtml()
            
            # Position cursor at end and insert new content
            cursor = self.chatHistory.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertHtml(html_message)
            
            # Scroll to bottom
            scrollbar = self.chatHistory.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            # Fallback: simple text message if HTML formatting fails
            simple_message = f"\n{sender} [{timestamp}]: {message}\n"
            cursor = self.chatHistory.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(simple_message)
            print(f"Chat formatting error: {e}")

    def _format_morpheus_message(self, message):
        """Format Morpheus message exactly like GitHub Copilot - truly clean and readable."""
        import re
        
        # Initialize persistent storage if needed
        if not hasattr(self, '_code_blocks'):
            self._code_blocks = {}
        if not hasattr(self, '_code_block_html'):
            self._code_block_html = {}
        
        # Pattern to match code blocks (```python or ``` followed by code)
        code_block_pattern = r'```(?:python|py)?\s*(.*?)```'
        
        # Store placeholders for this specific message
        current_placeholders = {}
        
        def extract_and_store_code(match):
            # Get the RAW, CLEAN code 
            raw_code = match.group(1).strip()
            if not raw_code:
                return ""
            
            # Generate unique ID for this code block
            import uuid
            block_id = str(uuid.uuid4())[:8]
            
            # Store CLEAN code for copying/applying (persistent storage)
            self._code_blocks[block_id] = raw_code
            
            # TRUE GitHub Copilot style - exactly like VS Code
            escaped_code = html.escape(raw_code)
            
            # Use a placeholder that we'll replace after HTML processing
            placeholder = f"___CODE_BLOCK_{block_id}___"
            
            # Store the complete formatted block (both persistent and local)
            code_html = f'''
<div style="margin: 16px 0; border: 1px solid #30363d; border-radius: 6px; background-color: #0d1117; font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;">
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; background-color: #161b22; border-bottom: 1px solid #30363d;">
        <span style="color: #f0f6fc; font-size: 14px; font-weight: 600;">Python</span>
        <div style="display: flex; gap: 16px;">
            <a href="copy_{block_id}" style="color: #58a6ff; text-decoration: none; font-size: 14px;">Copy code</a>
            <a href="apply_{block_id}" style="color: #238636; text-decoration: none; font-size: 14px;">Apply to editor</a>
            <a href="fix_{block_id}" style="color: #f85149; text-decoration: none; font-size: 14px;">Keep as fix</a>
        </div>
    </div>
    <div style="padding: 16px;">
        <pre style="margin: 0; color: #e6edf3; font-size: 14px; line-height: 1.5; white-space: pre-wrap; font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;">{escaped_code}</pre>
    </div>
</div>
'''
            
            # Store in both persistent and current message placeholders
            self._code_block_html[placeholder] = code_html
            current_placeholders[placeholder] = code_html
            
            return placeholder
        
        # Step 1: Replace code blocks with placeholders
        processed_message = re.sub(code_block_pattern, extract_and_store_code, message, flags=re.DOTALL)
        
        # Step 2: Escape HTML for regular text
        formatted_message = html.escape(processed_message)
        
        # Step 3: Replace placeholders with actual code blocks (after HTML escaping)
        # Use current placeholders to avoid conflicts with old messages
        for placeholder, code_html in current_placeholders.items():
            formatted_message = formatted_message.replace(placeholder, code_html)
        
        # Step 4: Convert newlines to proper line breaks
        formatted_message = formatted_message.replace('\n', '<br>')
        
        # Step 5: Show floating actions if code blocks were found
        if current_placeholders and hasattr(self, 'floatingActions'):
            # Collect all code blocks for comprehensive fix processing
            all_code_blocks = list(self._code_blocks.values())
            
            if all_code_blocks:
                # Combine all code blocks for comprehensive error fixing
                combined_code = '\n'.join(all_code_blocks)
                
                # Notify user about available actions
                if len(all_code_blocks) > 1:
                    self.console.append_tagged("COPILOT", f"Multiple code suggestions available ({len(all_code_blocks)} blocks) - use floating buttons in editor corner or press ESC to hide", "#58a6ff")
                else:
                    self.console.append_tagged("COPILOT", "Code suggestion available - use floating buttons in editor corner or press ESC to hide", "#58a6ff")
                
                # Delay showing floating actions to ensure UI is ready
                QtCore.QTimer.singleShot(100, lambda: self._show_floating_actions(combined_code))
        
        return formatted_message

    def _apply_simple_highlighting(self, code):
        """Apply very simple, safe Python syntax highlighting."""
        import re
        
        # Start with properly escaped code
        highlighted_code = html.escape(code)
        
        # Only apply very basic, safe highlighting to avoid QTextBrowser issues
        # Keywords in purple
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'try', 'except', 'return']
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            highlighted_code = re.sub(pattern, f'<b style="color:#c678dd">{keyword}</b>', highlighted_code)
        
        # Comments in green
        highlighted_code = re.sub(r'(#[^\n]*)', r'<i style="color:#5c6370">\1</i>', highlighted_code)
        
        return highlighted_code

    def _apply_python_highlighting(self, code):
        """Apply basic Python syntax highlighting to code."""
        import re
        
        # First, escape the code for safe HTML display
        highlighted_code = html.escape(code)
        
        # Apply syntax highlighting with proper HTML spans
        # Python keywords
        keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 
                   'import', 'from', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'lambda',
                   'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False', 'self']
        
        for keyword in keywords:
            pattern = r'\b(' + re.escape(keyword) + r')\b'
            highlighted_code = re.sub(pattern, r'<span style="color:#ff79c6">\1</span>', highlighted_code)
        
        # Strings (more careful regex to avoid conflicts)
        highlighted_code = re.sub(r'(&quot;[^&]*?&quot;|&#x27;[^&]*?&#x27;)', r'<span style="color:#f1fa8c">\1</span>', highlighted_code)
        
        # Comments
        highlighted_code = re.sub(r'(#[^\n]*)', r'<span style="color:#6272a4">\1</span>', highlighted_code)
        
        # Numbers
        highlighted_code = re.sub(r'\b(\d+\.?\d*)\b', r'<span style="color:#bd93f9">\1</span>', highlighted_code)
        
        return highlighted_code

    def _chat_key_press_event(self, event):
        """Handle key press events in chat input."""
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            # Send message on Enter (unless Shift is held for new line)
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                # Shift+Enter: Insert new line
                QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)
            else:
                # Enter or Ctrl+Enter: Send message
                self._send_message()
        else:
            # Call parent method for normal text editing
            QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)

    def _clear_chat(self):
        """Clear chat history."""
        self.chatHistory.clear()

    def _morpheus_introduction(self):
        """Display Morpheus introduction message."""
        intro_message = """Hello! I'm Morpheus, your AI coding assistant integrated into the NEO Script Editor.

I was created by Mayj Amilano to help Maya developers like you with:
• Maya scripting and MEL commands
• Python development and best practices  
• Code optimization and debugging
• API documentation and examples
• Creative problem-solving for your projects

This NEO Script Editor was developed by Mayj Amilano with passion and attention to detail, designed specifically to enhance your Maya workflow. Both the editor and I were built to make your coding experience more productive and enjoyable!

💡 Tip: Use the "Include current code context" checkbox below to share your code with me for more accurate help."""
        
        self._add_chat_message("Morpheus", intro_message, "#238636")

    def _on_morpheus_response(self, response):
        """Handle response from Morpheus AI."""
        self._hide_thinking_indicator()
        self._add_chat_message("Morpheus", response, "#238636")
    
    def _on_history_updated(self, chat_history):
        """Handle history updates from Morpheus manager."""
        self._update_history_info()
        # Only reload if chat is empty but we have history
        if (self.chatHistory.toPlainText().strip() == "" and 
            hasattr(self, 'morpheus_manager') and 
            self.morpheus_manager.chat_history):
            self._load_current_conversation()

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
            self._update_history_info()

    def _next_conversation(self):
        """Go to next conversation."""
        if hasattr(self, 'morpheus_manager'):
            result = self.morpheus_manager.next_conversation()
            # If next_conversation returns None, it means we're back to "view all" mode
            self._load_current_conversation()
            self._update_history_info()

    def _load_current_conversation(self):
        """Load the current conversation history."""
        if hasattr(self, 'morpheus_manager'):
            self.chatHistory.clear()
            
            # Also clear code blocks to start fresh
            if hasattr(self, '_code_blocks'):
                self._code_blocks.clear()
            if hasattr(self, '_code_block_html'):
                self._code_block_html.clear()
            
            # Check if we're viewing a specific conversation or all conversations
            if self.morpheus_manager.current_chat_index >= 0:
                # Load specific conversation
                current_conversation = self.morpheus_manager.get_current_conversation()
                if current_conversation and isinstance(current_conversation, dict):
                    if 'user' in current_conversation and 'ai' in current_conversation:
                        self._add_chat_message("You", current_conversation['user'], "#58a6ff")
                        self._add_chat_message("Morpheus", current_conversation['ai'], "#238636")
            else:
                # Load all conversations (current session view)
                full_history = self.morpheus_manager.chat_history
                if full_history and isinstance(full_history, list):
                    for entry in full_history:
                        if isinstance(entry, dict):
                            # Handle different conversation formats
                            if 'user' in entry and 'ai' in entry:
                                # Old format: {'user': message, 'ai': response}
                                self._add_chat_message("You", entry['user'], "#58a6ff")
                                self._add_chat_message("Morpheus", entry['ai'], "#238636")
                            elif 'role' in entry and 'content' in entry:
                                # New format: {'role': 'user'/'assistant', 'content': message}
                                if entry['role'] == 'user':
                                    self._add_chat_message("You", entry['content'], "#58a6ff")
                                else:
                                    self._add_chat_message("Morpheus", entry['content'], "#238636")
            
            self._update_history_info()

    def _update_history_info(self):
        """Update the history navigation info."""
        if hasattr(self, 'morpheus_manager'):
            current, total = self.morpheus_manager.get_conversation_info()
            
            # Update label - show "All" when viewing all conversations
            if self.morpheus_manager.current_chat_index == -1:
                self.historyLabel.setText(f"All/{total}")
            else:
                self.historyLabel.setText(f"{current}/{total}")
            
            # Enable/disable navigation buttons
            # Previous: enabled if we have history and not at first conversation
            self.prevChatBtn.setEnabled(total > 0 and 
                                      (self.morpheus_manager.current_chat_index == -1 or 
                                       self.morpheus_manager.current_chat_index > 0))
            
            # Next: enabled if we have history and not at last conversation or in "view all" mode
            self.nextChatBtn.setEnabled(total > 0 and 
                                      (self.morpheus_manager.current_chat_index == -1 or 
                                       self.morpheus_manager.current_chat_index < total - 1))

    def _handle_code_action(self, url):
        """Handle clicks on code action buttons (Copy, Apply, Keep Fix)."""
        try:
            url_str = url.toString()
            
            # Parse the action and block ID
            if '_' not in url_str:
                return
                
            action, block_id = url_str.split('_', 1)
            
            # Initialize code blocks if not exists
            if not hasattr(self, '_code_blocks'):
                self._code_blocks = {}
            
            # Get the stored code
            if block_id not in self._code_blocks:
                self._show_info_message("Code Block Not Found", f"The requested code block '{block_id}' could not be found.")
                return
                
            code = self._code_blocks[block_id]
            
            if action == "copy":
                self._copy_code_to_clipboard(code)
                
            elif action == "apply":
                self._apply_code_to_editor(code)
                
            elif action == "fix":
                self._keep_as_fix(code)
            
            # Check if chat got cleared and reload if necessary
            QtCore.QTimer.singleShot(100, self._ensure_chat_preserved)
                
        except Exception as e:
            self._show_info_message("Action Error", f"Failed to handle code action: {str(e)}")
    
    def _ensure_chat_preserved(self):
        """Ensure chat history is preserved after actions."""
        if self.chatHistory.toPlainText().strip() == "":
            print("Chat was cleared, reloading conversation...")
            self._load_current_conversation()
    
    def _show_thinking_indicator(self):
        """Show the thinking indicator with animation."""
        self.responseIndicator.setVisible(True)
        self.thinkingDots = 0
        self.thinkingTimer.start(500)  # Update every 500ms
        
    def _hide_thinking_indicator(self):
        """Hide the thinking indicator."""
        self.thinkingTimer.stop()
        self.responseIndicator.setVisible(False)
        self.sendBtn.setEnabled(True)  # Re-enable send button
        
    def _animate_thinking(self):
        """Animate the thinking indicator."""
        dots = "." * (self.thinkingDots % 4)
        self.responseIndicator.setText(f"🤖 Morpheus is thinking{dots}")
        self.thinkingDots += 1

    # =========================================================
    # Floating Code Actions (GitHub Copilot Style)
    # =========================================================
    def _setup_floating_code_actions(self):
        """Create anchored code action buttons like GitHub Copilot in VS Code."""
        # Create action widget container anchored to main window
        self.floatingActions = QtWidgets.QWidget(self)
        self.floatingActions.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        self.floatingActions.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Create horizontal layout for buttons
        actionLayout = QtWidgets.QHBoxLayout(self.floatingActions)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.setSpacing(2)
        
        # GitHub Copilot style button styling - compact and anchored
        button_style = """
            QPushButton {
                background: rgba(30, 30, 30, 0.98);
                border: 1px solid #454545;
                border-radius: 3px;
                color: #cccccc;
                padding: 3px 6px;
                font-size: 10px;
                font-weight: 500;
                min-width: 45px;
                max-height: 20px;
                margin: 0px;
            }
            QPushButton:hover {
                background: rgba(45, 45, 45, 0.98);
                border-color: #007ACC;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: rgba(0, 122, 204, 0.3);
            }
        """
        
        # Keep button (green - positive action)
        self.floatingKeepBtn = QtWidgets.QPushButton("Keep")
        self.floatingKeepBtn.setStyleSheet(button_style + """
            QPushButton {
                background: rgba(22, 163, 74, 0.9);
                border-color: #16a34a;
            }
            QPushButton:hover {
                background: rgba(34, 197, 94, 0.95);
                border-color: #22c55e;
            }
        """)
        self.floatingKeepBtn.setToolTip("Keep this code suggestion")
        self.floatingKeepBtn.clicked.connect(self._floating_keep_action)
        
        # Copy button (blue - neutral action)
        self.floatingCopyBtn = QtWidgets.QPushButton("Copy")
        self.floatingCopyBtn.setStyleSheet(button_style)
        self.floatingCopyBtn.setToolTip("Copy suggested code to clipboard")
        self.floatingCopyBtn.clicked.connect(self._floating_copy_action)
        
        # Undo button (orange - undo preview)
        self.floatingUndoBtn = QtWidgets.QPushButton("Undo")
        self.floatingUndoBtn.setStyleSheet(button_style + """
            QPushButton {
                background: rgba(251, 146, 60, 0.9);
                border-color: #f59e0b;
            }
            QPushButton:hover {
                background: rgba(251, 191, 36, 0.95);
                border-color: #fbbf24;
            }
        """)
        self.floatingUndoBtn.setToolTip("Undo code preview")
        self.floatingUndoBtn.clicked.connect(self._floating_undo_action)
        
        # Add buttons to layout in logical order: Keep, Copy, Undo
        actionLayout.addWidget(self.floatingKeepBtn)
        actionLayout.addWidget(self.floatingCopyBtn)
        actionLayout.addWidget(self.floatingUndoBtn)
        
        # Initially hidden
        self.floatingActions.setVisible(False)
        
        # Store current code for floating actions
        self.current_floating_code = ""
        
        # Add keyboard shortcut to hide floating actions (ESC key)
        hide_shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self)
        hide_shortcut.activated.connect(self._escape_key_handler)
        
    def _position_floating_actions(self):
        """Position actions anchored to bottom-right corner of the active code editor."""
        if hasattr(self, 'floatingActions') and self.floatingActions.isVisible():
            # Get the current active editor widget inside the tab
            current_editor = self._get_current_editor()
            if current_editor and hasattr(self, 'tabWidget') and self.tabWidget.count() > 0:
                # Map editor coordinates to main window coordinates
                editor_global_pos = current_editor.mapTo(self, QtCore.QPoint(0, 0))
                editor_width = current_editor.width()
                editor_height = current_editor.height()
                
                button_width = self.floatingActions.sizeHint().width()
                button_height = self.floatingActions.sizeHint().height()
                
                # Position exactly at bottom-right corner of editor (anchored to corner)
                x = editor_global_pos.x() + editor_width - button_width - 2
                y = editor_global_pos.y() + editor_height - button_height - 2
                
                self.floatingActions.setGeometry(x, y, button_width, button_height)
                self.floatingActions.raise_()  # Bring to front
    
    def _show_floating_actions(self, code):
        """Show code comparison dialog and handle user decision."""
        self.current_floating_code = code
        
        # Get current editor code for comparison
        current_editor = self._get_current_editor()
        if not current_editor:
            return
            
        current_code = current_editor.toPlainText()
        
        # Show comparison dialog
        if self._show_code_comparison_dialog(current_code, code):
            # User chose to apply - show preview first
            self._show_code_preview(current_editor, current_code, code)
            self.console.append_tagged("COPILOT", "💡 Code preview applied - Keep to accept, Undo to revert", "#58a6ff")
        else:
            # User cancelled
            self.console.append_tagged("COPILOT", "Code suggestion cancelled", "#f59e0b")
        
    def _hide_floating_actions(self):
        """Hide floating action buttons with fade effect."""
        if hasattr(self, 'floatingActions') and self.floatingActions.isVisible():
            # Fade out animation
            self.fade_out_animation = QtCore.QPropertyAnimation(self.floatingActions, b"windowOpacity")
            self.fade_out_animation.setDuration(150)
            self.fade_out_animation.setStartValue(1.0)
            self.fade_out_animation.setEndValue(0.0)
            self.fade_out_animation.finished.connect(lambda: self.floatingActions.setVisible(False))
            self.fade_out_animation.start()
            
        # Clean up preview state
        self._preview_applied = False
        self._preview_changes = []
        self.current_floating_code = ""
    
    def _escape_key_handler(self):
        """Handle ESC key - revert preview and hide actions."""
        if hasattr(self, '_preview_applied') and self._preview_applied:
            self._revert_code_preview()
            self.console.append_tagged("COPILOT", "Code preview reverted", "#f59e0b")
        self._hide_floating_actions()

    def _show_inline_code_preview(self, suggested_code):
        """Show VS Code Copilot-style inline preview with Keep/Apply buttons."""
        current_editor = self._get_current_editor()
        if not current_editor:
            return False
            
        # Store original code for revert
        self.original_code = current_editor.toPlainText()
        
        # Apply suggested code as preview (with special formatting)
        self._apply_inline_diff_preview(current_editor, self.original_code, suggested_code)
        
        # Show inline action buttons
        self._show_inline_action_buttons(current_editor)
        
        return True
    
    def _apply_inline_diff_preview(self, editor, original_code, suggested_code):
        """Apply Git Copilot-style smart diff preview - ALWAYS show line-by-line changes."""
        try:
            import difflib
            
            original_lines = original_code.split('\n')
            suggested_lines = suggested_code.split('\n')
            
            # Calculate minimal changes
            changes = self._calculate_minimal_changes(original_lines, suggested_lines)
            
            # ALWAYS use Git Copilot-style diff highlighting (never whole code replacement)
            self._apply_git_copilot_style_diff(editor, original_lines, suggested_lines, changes)
                
        except Exception as e:
            print(f"Error creating diff preview: {e}")
            # Fallback: show Git Copilot style even for errors
            self._apply_git_copilot_style_diff(editor, original_code.split('\n'), suggested_code.split('\n'), {'changed_lines': [], 'added_lines': [], 'removed_lines': []})
    
    def _calculate_minimal_changes(self, original_lines, suggested_lines):
        """Calculate what actually changed between original and suggested code with intelligent syntax fix detection."""
        import difflib
        
        # Get detailed diff using SequenceMatcher
        matcher = difflib.SequenceMatcher(None, original_lines, suggested_lines)
        changes = {
            'is_minimal': True,
            'changed_lines': [],
            'added_lines': [],
            'removed_lines': [],
            'total_changes': 0,
            'fix_type': 'unknown'
        }
        
        opcodes = list(matcher.get_opcodes())
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'replace':
                # Lines were modified - check if it's a simple syntax fix
                orig_block = original_lines[i1:i2]
                sugg_block = suggested_lines[j1:j2]
                
                # Detect common syntax fixes
                if len(orig_block) == len(sugg_block) == 1:
                    orig_line = orig_block[0].strip()
                    sugg_line = sugg_block[0].strip()
                    
                    # Detect specific fix types
                    if orig_line.endswith('(') and sugg_line.endswith('):'):
                        changes['fix_type'] = 'missing_colon'
                    elif orig_line.count('"') % 2 != 0 and sugg_line.count('"') % 2 == 0:
                        changes['fix_type'] = 'unterminated_string'
                    elif 'print(' in orig_line and 'print(' in sugg_line and orig_line != sugg_line:
                        changes['fix_type'] = 'syntax_correction'
                    elif len(orig_line) > 0 and len(sugg_line) > 0:
                        # Calculate similarity to detect minor fixes
                        similarity = difflib.SequenceMatcher(None, orig_line, sugg_line).ratio()
                        if similarity > 0.8:
                            changes['fix_type'] = 'minor_syntax_fix'
                
                for i, (orig_line, new_line) in enumerate(zip(orig_block, sugg_block)):
                    changes['changed_lines'].append({
                        'line_num': i1 + i,
                        'original': orig_line,
                        'suggested': new_line,
                        'fix_type': changes['fix_type']
                    })
                changes['total_changes'] += max(len(orig_block), len(sugg_block))
                
            elif tag == 'delete':
                # Lines were removed
                for i in range(i1, i2):
                    changes['removed_lines'].append({
                        'line_num': i,
                        'content': original_lines[i]
                    })
                changes['total_changes'] += (i2 - i1)
                
            elif tag == 'insert':
                # Lines were added  
                for i in range(j1, j2):
                    changes['added_lines'].append({
                        'line_num': i,
                        'content': suggested_lines[i]
                    })
                changes['total_changes'] += (j2 - j1)
        
        # Smart minimal detection based on fix type and change size
        total_lines = max(len(original_lines), len(suggested_lines))
        change_ratio = changes['total_changes'] / total_lines if total_lines > 0 else 0
        
        # More generous minimal detection for syntax fixes
        if changes['fix_type'] in ['missing_colon', 'unterminated_string', 'minor_syntax_fix', 'syntax_correction']:
            changes['is_minimal'] = (changes['total_changes'] <= 10 and 
                                   change_ratio <= 0.5 and 
                                   len(changes['changed_lines']) <= 5)
        else:
            changes['is_minimal'] = (changes['total_changes'] <= 5 and 
                                   change_ratio <= 0.3 and 
                                   len(changes['changed_lines']) <= 3)
        
        return changes
    
    def _apply_inline_diff_highlighting(self, editor, original_code, suggested_code, changes):
        """Apply VS Code Copilot-style inline preview showing only specific changes."""
        
        # Don't replace entire code - show contextual changes like Git Copilot
        original_lines = original_code.split('\n')
        suggested_lines = suggested_code.split('\n')
        
        # Create a preview that shows ONLY the changed sections with context
        preview_lines = []
        context_range = 2  # Show 2 lines before and after changes
        
        # Collect all change line numbers
        all_change_lines = set()
        for change in changes['changed_lines']:
            all_change_lines.add(change['line_num'])
        for change in changes['added_lines']:
            all_change_lines.add(change['line_num'])
        for change in changes['removed_lines']:
            all_change_lines.add(change['line_num'])
        
        if not all_change_lines:
            # No changes detected, just show the suggestion as-is
            editor.setPlainText(suggested_code)
            return
        
        # Create contextual preview showing changes with surrounding lines
        min_change = min(all_change_lines)
        max_change = max(all_change_lines)
        
        # Determine preview range with context
        start_line = max(0, min_change - context_range)
        end_line = min(len(original_lines), max_change + context_range + 1)
        
        # Build preview showing original code with highlighted changes inline
        preview_text = ""
        
        for i in range(len(original_lines)):
            line = original_lines[i]
            
            # Check if this line has changes
            changed_line = None
            for change in changes['changed_lines']:
                if change['line_num'] == i:
                    changed_line = change
                    break
            
            if changed_line:
                # Show both original (grayed out) and new (highlighted)
                preview_text += f"  {line}\n"  # Original line (will be grayed)
                preview_text += f"+ {changed_line['suggested']}\n"  # New line (will be highlighted)
            elif i in [change['line_num'] for change in changes['removed_lines']]:
                # Removed line (show with minus)
                preview_text += f"- {line}\n"
            elif any(i == change['line_num'] for change in changes['added_lines']):
                # Added line (show with plus)
                added_change = next(change for change in changes['added_lines'] if change['line_num'] == i)
                preview_text += f"+ {added_change['content']}\n"
            else:
                # Unchanged line (show only if in context range)
                if start_line <= i <= end_line:
                    preview_text += f"  {line}\n"
        
        # Apply the contextual preview to editor
        editor.setPlainText(preview_text)
        
        # Now apply syntax highlighting to show the diff
        document = editor.document()
        extra_selections = []
        
        # Highlight different types of changes
        block = document.firstBlock()
        while block.isValid():
            text = block.text()
            
            if text.startswith('+ '):
                # Added/changed line - green background
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format.setBackground(QtGui.QColor("#1e3a1e"))  # Dark green
                selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                extra_selections.append(selection)
                
            elif text.startswith('- '):
                # Removed line - red background
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format.setBackground(QtGui.QColor("#3a1e1e"))  # Dark red
                selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                extra_selections.append(selection)
                
            block = block.next()
        
        # Apply all highlighting
        editor.setExtraSelections(extra_selections)
        
        # Mark as preview applied
        self._preview_applied = True
        self._preview_changes = changes
    
    def _apply_git_copilot_style_diff(self, editor, original_lines, suggested_lines, changes):
        """Apply TRUE Git Copilot-style inline diff showing line-by-line changes."""
        import difflib
        
        # Create unified diff like Git Copilot
        differ = difflib.unified_diff(
            original_lines, 
            suggested_lines, 
            lineterm='',
            n=3  # Show 3 lines of context
        )
        
        diff_lines = list(differ)[2:]  # Skip the file header lines
        
        if not diff_lines:
            # No changes detected, show original code
            editor.setPlainText('\n'.join(original_lines))
            return
        
        # Build Git Copilot-style preview
        preview_lines = []
        
        for line in diff_lines:
            if line.startswith('@@'):
                # Line number info - show as comment
                preview_lines.append(f"# {line}")
            elif line.startswith('-'):
                # Removed line - show with strikethrough styling 
                preview_lines.append(f"  {line[1:]}")  # Original line (will be styled)
            elif line.startswith('+'):
                # Added line - show with green highlighting
                preview_lines.append(f"+ {line[1:]}")  # New line with + prefix
            elif line.startswith(' '):
                # Context line - show unchanged
                preview_lines.append(f"  {line[1:]}")
            else:
                # Other diff info
                preview_lines.append(f"  {line}")
        
        # Set the Git Copilot-style diff text
        preview_text = '\n'.join(preview_lines)
        editor.setPlainText(preview_text)
        
        # Apply Git Copilot-style highlighting
        document = editor.document()
        extra_selections = []
        
        block = document.firstBlock()
        while block.isValid():
            text = block.text()
            
            if text.startswith('+ '):
                # Added/changed line - green background like GitHub
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format.setBackground(QtGui.QColor("#1e3a1e"))  # GitHub green
                selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                extra_selections.append(selection)
                
            elif text.startswith('# @@'):
                # Line number info - blue background
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format.setBackground(QtGui.QColor("#1e2a3a"))  # GitHub blue
                selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                extra_selections.append(selection)
                
            block = block.next()
        
        # Apply highlighting
        editor.setExtraSelections(extra_selections)
        
        # Store original code for revert functionality
        editor._original_code = '\n'.join(original_lines)
        
        # Mark as preview applied
        self._preview_applied = True
        self._preview_changes = changes
        
        # Add subtle border to indicate preview mode
        editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 10pt;
                line-height: 1.5;
                selection-background-color: #264F78;
                border: 2px solid #58a6ff;
                border-radius: 2px;
            }
        """)
        
        print(f"🎨 Applied Git Copilot diff: {len(diff_lines)} diff lines shown")
    
    def _show_code_comparison_dialog(self, current_code, suggested_code):
        """Show dialog comparing current code vs suggested code."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Code Comparison - Morpheus Suggestion")
        dialog.setModal(True)
        dialog.resize(1000, 600)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Remove header completely to maximize space for code comparison
        
        # Create splitter for side-by-side comparison
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Current code panel
        current_panel = QtWidgets.QWidget()
        current_layout = QtWidgets.QVBoxLayout(current_panel)
        current_layout.setContentsMargins(5, 5, 5, 5)
        current_layout.addWidget(QtWidgets.QLabel("📝 Current"))
        
        current_editor = QtWidgets.QTextEdit()
        current_editor.setPlainText(current_code)
        current_editor.setReadOnly(True)
        current_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.2;
            }
        """)
        current_layout.addWidget(current_editor)
        
        # Apply diff highlighting to current code
        self._apply_diff_highlighting(current_editor, current_code, suggested_code, is_original=True)
        splitter.addWidget(current_panel)
        
        # Suggested code panel
        suggested_panel = QtWidgets.QWidget()
        suggested_layout = QtWidgets.QVBoxLayout(suggested_panel)
        suggested_layout.setContentsMargins(5, 5, 5, 5)
        suggested_layout.addWidget(QtWidgets.QLabel("✨ Suggested"))
        
        suggested_editor = QtWidgets.QTextEdit()
        suggested_editor.setPlainText(suggested_code)
        suggested_editor.setReadOnly(True)
        suggested_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.2;
            }
        """)
        suggested_layout.addWidget(suggested_editor)
        
        # Apply diff highlighting to suggested code
        self._apply_diff_highlighting(suggested_editor, current_code, suggested_code, is_original=False)
        splitter.addWidget(suggested_panel)
        
        # Set equal sizes
        splitter.setSizes([500, 500])
        
        # Compact button panel
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 5, 0, 0)
        
        # Compact info label
        info_label = QtWidgets.QLabel("Apply to preview changes in editor")
        info_label.setStyleSheet("color: #888; font-size: 11px; margin: 0px;")
        button_layout.addWidget(info_label)
        
        button_layout.addStretch()
        
        # Compact buttons
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #777; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QtWidgets.QPushButton("Apply to Editor")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #2d8f40; }
        """)
        apply_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        # Show dialog and return result
        return dialog.exec_() == QtWidgets.QDialog.Accepted
    
    def _show_code_preview(self, editor, original_code, suggested_code):
        """Apply only the specific changes, not the entire code."""
        # Store original code for reverting
        self.original_code = original_code
        
        # Apply ONLY the specific changes, not entire code replacement
        self._apply_targeted_changes(editor, original_code, suggested_code)
        
        # Show floating Keep/Undo buttons
        self._show_preview_buttons()
        
        # Mark as preview mode
        self._preview_applied = True
    
    def _apply_targeted_changes(self, editor, original_code, suggested_code):
        """Apply only the specific line changes, not entire code replacement."""
        import difflib
        
        original_lines = original_code.splitlines()
        suggested_lines = suggested_code.splitlines()
        
        # Get diff operations
        differ = difflib.unified_diff(original_lines, suggested_lines, lineterm='')
        diff_lines = list(differ)
        
        if not diff_lines:
            return  # No changes
            
        # Parse the diff to find actual changes
        changes = []
        i = 0
        while i < len(diff_lines):
            line = diff_lines[i]
            if line.startswith('@@'):
                # Parse line numbers from @@ -start,count +start,count @@
                parts = line.split()
                if len(parts) >= 2:
                    old_info = parts[1].replace('-', '').split(',')
                    new_info = parts[2].replace('+', '').split(',')
                    old_start = int(old_info[0]) - 1  # Convert to 0-based
                    new_start = int(new_info[0]) - 1  # Convert to 0-based
                    
                    # Collect the actual changes
                    i += 1
                    old_lines = []
                    new_lines = []
                    
                    while i < len(diff_lines) and not diff_lines[i].startswith('@@'):
                        change_line = diff_lines[i]
                        if change_line.startswith('-'):
                            old_lines.append(change_line[1:])
                        elif change_line.startswith('+'):
                            new_lines.append(change_line[1:])
                        elif change_line.startswith(' '):
                            # Context line - ignore
                            pass
                        i += 1
                    
                    if old_lines or new_lines:
                        changes.append({
                            'old_start': old_start,
                            'old_lines': old_lines,
                            'new_lines': new_lines
                        })
                    continue
            i += 1
        
        # Apply changes in reverse order to maintain line numbers
        current_text = editor.toPlainText()
        current_lines = current_text.splitlines()
        
        for change in reversed(changes):
            old_start = change['old_start']
            old_count = len(change['old_lines'])
            new_lines = change['new_lines']
            
            # Replace the specific lines
            if old_count > 0:
                # Remove old lines
                del current_lines[old_start:old_start + old_count]
            
            # Insert new lines
            for j, new_line in enumerate(new_lines):
                current_lines.insert(old_start + j, new_line)
        
        # Set the modified text
        editor.setPlainText('\n'.join(current_lines))
    
    def _show_preview_buttons(self):
        """Show Keep/Undo buttons after preview is applied."""
        if not hasattr(self, 'floatingActions'):
            self._create_floating_buttons()
        
        # Position and show buttons
        self._position_floating_buttons()
        self.floatingActions.setVisible(True)
    
    def _create_floating_buttons(self):
        """Create floating action buttons if they don't exist."""
        if hasattr(self, 'floatingActions'):
            return  # Already created
            
        # Create the floating actions widget (reuse existing code)
        button_style = """
            QPushButton {
                background: rgba(88, 166, 255, 0.9);
                color: white;
                border: 2px solid #58a6ff;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: rgba(88, 166, 255, 0.95);
                border-color: #79c0ff;
            }
            QPushButton:pressed {
                background: rgba(88, 166, 255, 1.0);
            }
        """
        
        self.floatingActions = QtWidgets.QWidget(self)
        self.floatingActions.setStyleSheet("""
            QWidget {
                background: rgba(22, 22, 22, 0.95);
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        self.floatingActions.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        actionLayout = QtWidgets.QHBoxLayout(self.floatingActions)
        actionLayout.setContentsMargins(8, 8, 8, 8)
        actionLayout.setSpacing(8)
        
        # Keep button (green - accept changes)
        self.floatingKeepBtn = QtWidgets.QPushButton("✅ Keep")
        self.floatingKeepBtn.setStyleSheet(button_style + """
            QPushButton {
                background: rgba(22, 163, 74, 0.9);
                border-color: #16a34a;
            }
            QPushButton:hover {
                background: rgba(34, 197, 94, 0.95);
                border-color: #22c55e;
            }
        """)
        self.floatingKeepBtn.setToolTip("Keep and finalize these changes")
        self.floatingKeepBtn.clicked.connect(self._floating_keep_action)
        
        # Undo button (red - revert changes)
        self.floatingUndoBtn = QtWidgets.QPushButton("❌ Undo")
        self.floatingUndoBtn.setStyleSheet(button_style + """
            QPushButton {
                background: rgba(239, 68, 68, 0.9);
                border-color: #ef4444;
            }
            QPushButton:hover {
                background: rgba(248, 113, 113, 0.95);
                border-color: #f87171;
            }
        """)
        self.floatingUndoBtn.setToolTip("Undo and revert to original code")
        self.floatingUndoBtn.clicked.connect(self._floating_undo_action)
        
        # Add buttons to layout
        actionLayout.addWidget(self.floatingKeepBtn)
        actionLayout.addWidget(self.floatingUndoBtn)
        
        # Initially hidden
        self.floatingActions.setVisible(False)
        
        print("🔘 Floating Keep/Undo buttons created and connected")
    
    def _position_floating_buttons(self):
        """Position floating buttons in the editor corner."""
        if not hasattr(self, 'floatingActions'):
            return
            
        current_editor = self._get_current_editor()
        if not current_editor:
            return
            
        # Position in top-right corner of editor
        editor_rect = current_editor.geometry()
        button_width = self.floatingActions.sizeHint().width()
        button_height = self.floatingActions.sizeHint().height()
        
        # Position in top-right with some margin
        x = editor_rect.x() + editor_rect.width() - button_width - 20
        y = editor_rect.y() + 20
        
        self.floatingActions.setGeometry(x, y, button_width, button_height)
        self.floatingActions.raise_()  # Bring to front
    
    def _apply_diff_highlighting(self, editor, original_code, suggested_code, is_original=True):
        """Apply highlighting to show only the lines that changed between versions."""
        import difflib
        
        original_lines = original_code.split('\n')
        suggested_lines = suggested_code.split('\n')
        
        # Get unified diff to find changed lines
        matcher = difflib.SequenceMatcher(None, original_lines, suggested_lines)
        changed_line_nums = set()
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('replace', 'delete', 'insert'):
                if is_original:
                    # For original code, highlight the lines being removed/changed
                    for line_num in range(i1, i2):
                        changed_line_nums.add(line_num)
                else:
                    # For suggested code, highlight the lines being added/changed
                    for line_num in range(j1, j2):
                        changed_line_nums.add(line_num)
        
        if not changed_line_nums:
            return  # No changes to highlight
        
        # Apply highlighting to changed lines only
        document = editor.document()
        extra_selections = []
        
        for line_num in changed_line_nums:
            block = document.findBlockByNumber(line_num)
            if block.isValid():
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                if is_original:
                    # Red background for removed/changed lines in original
                    selection.format.setBackground(QtGui.QColor("#3a1e1e"))  # Dark red
                else:
                    # Green background for added/changed lines in suggested
                    selection.format.setBackground(QtGui.QColor("#1e3a1e"))  # Dark green
                
                selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                extra_selections.append(selection)
        
        editor.setExtraSelections(extra_selections)
    
    def _apply_contextual_preview(self, editor, original_code, suggested_code, changes):
        """Apply preview showing context around changes."""
        # For larger changes, still apply the code but with clear preview styling
        editor.setPlainText(suggested_code)
        
        # More prominent preview styling for larger changes
        editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d2818;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 10pt;
                line-height: 1.5;
                selection-background-color: #264F78;
                border: 2px solid #2ea043;
                border-radius: 4px;
            }
        """)
        
        # Store preview state
        editor._is_preview_mode = True
        editor._original_code = original_code
        editor._diff_changes = changes
        
        print(f"📝 Applied contextual preview: {changes['total_changes']} total changes")
    
    def _apply_simple_preview(self, editor, original_code, suggested_code):
        """Fallback simple preview."""
        editor.setPlainText(suggested_code)
        editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 10pt;
                line-height: 1.5;
                selection-background-color: #264F78;
                border: 2px solid #f59e0b;
                border-radius: 4px;
            }
        """)
        
        editor._is_preview_mode = True
        editor._original_code = original_code
    
    def _show_inline_action_buttons(self, editor):
        """Show Keep/Apply action buttons inline with the editor."""
        # Create action buttons widget
        if not hasattr(self, '_inline_actions'):
            self._inline_actions = QtWidgets.QWidget(self)
            self._inline_actions.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
            self._inline_actions.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
            self._inline_actions.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    border: 2px solid #58a6ff;
                    border-radius: 8px;
                    padding: 6px;
                }
                QPushButton {
                    background-color: #238636;
                    color: white;
                    border: 1px solid #2ea043;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 11px;
                    margin: 2px;
                    min-width: 70px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #2ea043;
                    border: 1px solid #40d865;
                }
                QPushButton#reject {
                    background-color: #da3633;
                    border: 1px solid #f85149;
                }
                QPushButton#reject:hover {
                    background-color: #f85149;
                    border: 1px solid #ff7b72;
                }
                QLabel {
                    color: #58a6ff;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 2px 4px;
                }
            """)
            
            # Create layout and buttons
            layout = QtWidgets.QHBoxLayout(self._inline_actions)
            layout.setContentsMargins(8, 4, 8, 4)
            
            # Info label
            info_label = QtWidgets.QLabel("🤖 Copilot Suggestion")
            info_label.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 11px;")
            layout.addWidget(info_label)
            
            layout.addStretch()
            
            # Keep button (accept changes)
            keep_btn = QtWidgets.QPushButton("Keep")
            keep_btn.clicked.connect(self._keep_inline_changes)
            layout.addWidget(keep_btn)
            
            # Undo button (revert changes) 
            undo_btn = QtWidgets.QPushButton("Undo")
            undo_btn.setObjectName("reject")
            undo_btn.clicked.connect(self._undo_inline_changes)
            layout.addWidget(undo_btn)
        
        # Position the action buttons above the editor
        self._position_inline_actions(editor)
        self._inline_actions.show()
        self._inline_actions.raise_()
    
    def _position_inline_actions(self, editor):
        """Position inline action buttons to be fully visible."""
        if hasattr(self, '_inline_actions'):
            # Get editor position relative to main window
            editor_pos = editor.mapTo(self, QtCore.QPoint(0, 0))
            editor_size = editor.size()
            
            # Calculate button size
            button_width = 280
            button_height = 36
            
            # Position at top-right of editor with margin, ensuring it's visible
            x = editor_pos.x() + editor_size.width() - button_width - 20
            y = editor_pos.y() + 15
            
            # Ensure buttons don't go outside the main window
            main_window_size = self.size()
            if x + button_width > main_window_size.width():
                x = main_window_size.width() - button_width - 10
            if x < 10:
                x = 10
            if y < 10:
                y = 10
            
            self._inline_actions.move(x, y)
            self._inline_actions.resize(button_width, button_height)
            
            # Ensure the widget is on top
            self._inline_actions.raise_()
    
    def _keep_inline_changes(self):
        """Keep the inline changes (accept the AI suggestion)."""
        current_editor = self._get_current_editor()
        if current_editor and hasattr(current_editor, '_is_preview_mode'):
            # Remove preview styling
            current_editor.setStyleSheet("""
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
            
            # Clear preview state
            delattr(current_editor, '_is_preview_mode')
            if hasattr(current_editor, '_original_code'):
                delattr(current_editor, '_original_code')
            
            # Hide action buttons
            self._hide_inline_actions()
            
            self.console.append_tagged("COPILOT", "✅ AI suggestion accepted", "#2ea043")
    
    def _undo_inline_changes(self):
        """Undo the inline changes (revert to original)."""
        current_editor = self._get_current_editor()
        if current_editor and hasattr(current_editor, '_is_preview_mode'):
            # Restore original code
            if hasattr(current_editor, '_original_code'):
                current_editor.setPlainText(current_editor._original_code)
                delattr(current_editor, '_original_code')
            
            # Remove preview styling
            current_editor.setStyleSheet("""
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
            
            # Clear preview state
            delattr(current_editor, '_is_preview_mode')
            
            # Hide action buttons
            self._hide_inline_actions()
            
            self.console.append_tagged("COPILOT", "↩️ AI suggestion reverted", "#f59e0b")
    
    def _hide_inline_actions(self):
        """Hide inline action buttons."""
        if hasattr(self, '_inline_actions'):
            self._inline_actions.hide()
    
    def resizeEvent(self, event):
        """Handle window resize - reposition inline actions if visible."""
        super().resizeEvent(event)
        if hasattr(self, '_inline_actions') and self._inline_actions.isVisible():
            current_editor = self._get_current_editor()
            if current_editor:
                self._position_inline_actions(current_editor)
    
    def _floating_keep_action(self):
        """Handle Keep button - finalize the code changes."""
        if hasattr(self, '_preview_applied') and self._preview_applied:
            # Code is already applied, just finalize it
            self._preview_applied = False
            self.original_code = None  # Clear revert data
            self.console.append_tagged("COPILOT", "✅ Code changes accepted and finalized", "#22c55e")
        else:
            self.console.append_tagged("COPILOT", "⚠️ No preview to keep", "#f59e0b")
        self._hide_floating_actions()
    
    def _floating_copy_action(self):
        """Handle Copy button."""
        if self.current_floating_code:
            self._copy_code_to_clipboard(self.current_floating_code)
            self.console.append_tagged("COPILOT", "📋 Code copied to clipboard", "#58a6ff")
        else:
            self.console.append_tagged("COPILOT", "⚠️ No code to copy", "#f59e0b")
    
    def _floating_undo_action(self):
        """Handle Undo button - revert to original code."""
        current_editor = self._get_current_editor()
        if not current_editor:
            self.console.append_tagged("COPILOT", "⚠️ No active editor", "#f59e0b")
            self._hide_floating_actions()
            return
            
        if hasattr(self, 'original_code') and self.original_code is not None:
            # Revert to original code
            current_editor.setPlainText(self.original_code)
            self._preview_applied = False
            self.original_code = None
            self.console.append_tagged("COPILOT", "↩️ Changes reverted to original code", "#f59e0b")
        else:
            self.console.append_tagged("COPILOT", "⚠️ No original code to revert to", "#f59e0b")
        self._hide_floating_actions()

    def _apply_code_preview(self, code):
        """Apply intelligent diff-based preview like GitHub Copilot (only shows changes)."""
        current_editor = self._get_current_editor()
        if not current_editor:
            return False
            
        # Store original content for undo
        self._original_content = current_editor.toPlainText()
        self._original_cursor_position = current_editor.textCursor().position()
        
        # Analyze if this is a fix/improvement vs new code
        current_text = self._original_content.strip()
        suggested_code = code.strip()
        
        if not current_text:
            # Empty editor - just insert the code normally
            return self._apply_simple_preview(code)
        
        # Try to find intelligent insertions/replacements
        changes = self._find_code_changes(current_text, suggested_code)
        
        if not changes:
            # Fallback to simple insertion at cursor
            return self._apply_simple_preview(code)
        
        # Apply diff-based changes with preview highlighting
        return self._apply_diff_preview(changes)
    
    def _apply_simple_preview(self, code):
        """Apply simple preview insertion at cursor position."""
        current_editor = self._get_current_editor()
        cursor = current_editor.textCursor()
        
        # If there's selected text, we'll replace it
        if cursor.hasSelection():
            self._preview_start_pos = cursor.selectionStart()
            self._preview_end_pos = cursor.selectionEnd()
            self._replaced_text = cursor.selectedText()
        else:
            # Insert at current cursor position
            self._preview_start_pos = cursor.position()
            self._preview_end_pos = cursor.position()
            self._replaced_text = ""
            
        # Insert the code with special formatting to show it's a preview
        cursor.insertText(code)
        
        # Select the inserted text to highlight it as a preview
        cursor.setPosition(self._preview_start_pos)
        cursor.setPosition(self._preview_start_pos + len(code), QtGui.QTextCursor.KeepAnchor)
        current_editor.setTextCursor(cursor)
        
        # Apply preview styling (GitHub Copilot-like)
        char_format = QtGui.QTextCharFormat()
        char_format.setBackground(QtGui.QColor(58, 166, 255, 30))  # Light blue background
        char_format.setProperty(QtGui.QTextFormat.OutlinePen, QtGui.QPen(QtGui.QColor(58, 166, 255), 1))
        cursor.setCharFormat(char_format)
        
        self._preview_applied = True
        self._preview_length = len(code)
        self._preview_changes = [{'start': self._preview_start_pos, 'length': len(code)}]
        
        return True

    def _find_code_changes(self, current_code, suggested_code):
        """Find intelligent changes between current and suggested code with smart detection."""
        import difflib
        import re
        
        current_lines = current_code.split('\n')
        suggested_lines = suggested_code.split('\n')
        
        # Collect all types of changes for comprehensive error fixing
        all_changes = []
        
        # First, try to detect function/method fixes
        function_changes = self._find_function_changes(current_code, suggested_code)
        if function_changes:
            all_changes.extend(function_changes)
        
        # Also try block-level changes (if, for, while, try, etc.)
        block_changes = self._find_block_changes(current_lines, suggested_lines)
        if block_changes:
            all_changes.extend(block_changes)
        
        # Also try line-by-line diff for remaining issues
        line_changes = self._find_line_changes(current_lines, suggested_lines)
        if line_changes:
            all_changes.extend(line_changes)
        
        # Return all changes found, or fall back to line changes if nothing else worked
        return all_changes if all_changes else line_changes

    def _is_function_replacement(self, current_code, suggested_code):
        """Check if the suggestion is replacing a function or method."""
        import re
        
        # Look for function definitions in both codes
        func_pattern = r'^(?:\s*)def\s+(\w+)\s*\([^)]*\):'
        
        current_funcs = set(re.findall(func_pattern, current_code, re.MULTILINE))
        suggested_funcs = set(re.findall(func_pattern, suggested_code, re.MULTILINE))
        
        # If they have functions in common, it might be a replacement
        return bool(current_funcs & suggested_funcs)

    def _find_function_changes(self, current_code, suggested_code):
        """Find function-level replacements for better preview."""
        import re
        
        current_lines = current_code.split('\n')
        suggested_lines = suggested_code.split('\n')
        
        # Find all functions in current code
        func_pattern = r'^(\s*)def\s+(\w+)\s*\([^)]*\):'
        changes = []
        
        current_func_lines = {}
        for i, line in enumerate(current_lines):
            match = re.match(func_pattern, line)
            if match:
                func_name = match.group(2)
                indent = len(match.group(1))
                
                # Find the end of this function
                func_start = i
                func_end = len(current_lines)
                
                for j in range(i + 1, len(current_lines)):
                    next_line = current_lines[j]
                    if (next_line.strip() and 
                        not next_line.startswith(' ' * (indent + 1)) and
                        not next_line.startswith('\t' * (indent // 4 + 1))):
                        func_end = j
                        break
                
                current_func_lines[func_name] = (func_start, func_end)
        
        # Find corresponding functions in suggested code
        for i, line in enumerate(suggested_lines):
            match = re.match(func_pattern, line)
            if match:
                func_name = match.group(2)
                if func_name in current_func_lines:
                    # This is a replacement - find the new function body
                    indent = len(match.group(1))
                    
                    # Find the end of the suggested function
                    func_start = i
                    func_end = len(suggested_lines)
                    
                    for j in range(i + 1, len(suggested_lines)):
                        next_line = suggested_lines[j]
                        if (next_line.strip() and 
                            not next_line.startswith(' ' * (indent + 1)) and
                            not next_line.startswith('\t' * (indent // 4 + 1))):
                            func_end = j
                            break
                    
                    # Add the function replacement as a change
                    new_function_lines = suggested_lines[func_start:func_end]
                    old_start, old_end = current_func_lines[func_name]
                    
                    changes.append({
                        'type': 'function_replacement',
                        'function_name': func_name,
                        'old_start': old_start,
                        'old_end': old_end,
                        'new_content': '\n'.join(new_function_lines)
                    })
        
        return changes

    def _find_block_changes(self, current_lines, suggested_lines):
        """Find block-level changes (if, for, while, etc.)."""
        # Simple implementation for now - can be enhanced later
        return []

    def _find_line_changes(self, current_lines, suggested_lines):
        """Find line-by-line changes using difflib."""
        import difflib
        
        # Use sequence matcher for better change detection
        matcher = difflib.SequenceMatcher(None, current_lines, suggested_lines)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Lines being replaced
                for idx, (old_line, new_line) in enumerate(zip(current_lines[i1:i2], suggested_lines[j1:j2])):
                    if old_line.strip() != new_line.strip():  # Ignore whitespace-only changes
                        changes.append({
                            'type': 'line_replacement',
                            'line_number': i1 + idx,
                            'content': new_line,
                            'original_line': old_line
                        })
            elif tag == 'insert':
                # New lines being inserted
                for idx, new_line in enumerate(suggested_lines[j1:j2]):
                    changes.append({
                        'type': 'line_insertion',
                        'line_number': i1 + idx,
                        'content': new_line,
                        'original_line': ""
                    })
        
        return changes

    def _apply_diff_preview(self, changes):
        """Apply diff-based preview showing only the specific changes."""
        current_editor = self._get_current_editor()
        current_text = current_editor.toPlainText()
        lines = current_text.split('\n')
        
        self._preview_changes = []
        
        # Handle different change types
        for change in changes:
            if change['type'] == 'function_replacement':
                self._apply_function_preview(change, current_editor, lines)
            elif change['type'] in ['line_replacement', 'line_insertion']:
                self._apply_line_preview(change, current_editor, lines)
        
        self._preview_applied = True
        return True

    def _apply_function_preview(self, change, current_editor, lines):
        """Apply function-level preview replacement."""
        old_start = change['old_start']
        old_end = change['old_end']
        new_content = change['new_content']
        
        # Calculate character positions
        start_pos = sum(len(lines[i]) + 1 for i in range(old_start))
        end_pos = sum(len(lines[i]) + 1 for i in range(old_end))
        
        # Select the old function
        cursor = current_editor.textCursor()
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        
        # Store original content for undo
        original_content = cursor.selectedText()
        
        # Replace with new function
        cursor.insertText(new_content)
        
        # Track this change
        self._preview_changes.append({
            'start': start_pos,
            'length': len(new_content),
            'original': original_content,
            'type': 'function'
        })
        
        # Apply preview styling (yellow/orange for function changes)
        cursor.setPosition(start_pos)
        cursor.setPosition(start_pos + len(new_content), QtGui.QTextCursor.KeepAnchor)
        
        char_format = QtGui.QTextCharFormat()
        char_format.setBackground(QtGui.QColor(251, 146, 60, 40))  # Orange background for function changes
        char_format.setProperty(QtGui.QTextFormat.OutlinePen, QtGui.QPen(QtGui.QColor(251, 146, 60), 2))
        cursor.setCharFormat(char_format)

    def _apply_line_preview(self, change, current_editor, lines):
        """Apply line-level preview changes."""
        line_num = change.get('line_number', 0)
        if line_num >= len(lines):
            return
            
        # Calculate character position for this line
        char_pos = sum(len(lines[i]) + 1 for i in range(line_num))
        
        # Create cursor for this position
        cursor = current_editor.textCursor()
        cursor.setPosition(char_pos)
        
        if change['type'] == 'line_replacement':
            original_line = change['original_line']
            new_line = change['content']
            
            # Select the entire line to replace
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            line_start = cursor.selectionStart()
            line_end = cursor.selectionEnd()
            
            # Replace with new content
            cursor.insertText(new_line)
            
            # Track this change for highlighting and undo
            self._preview_changes.append({
                'start': line_start,
                'length': len(new_line),
                'original': original_line,
                'type': 'line'
            })
            
            # Apply preview styling (green for line changes)
            cursor.setPosition(line_start)
            cursor.setPosition(line_start + len(new_line), QtGui.QTextCursor.KeepAnchor)
            
            char_format = QtGui.QTextCharFormat()
            char_format.setBackground(QtGui.QColor(34, 197, 94, 40))  # Green background for line changes
            char_format.setProperty(QtGui.QTextFormat.OutlinePen, QtGui.QPen(QtGui.QColor(34, 197, 94), 1))
            cursor.setCharFormat(char_format)
        
        elif change['type'] == 'line_insertion':
            new_line = change['content']
            
            # Insert new line
            cursor.insertText(new_line + '\n')
            
            # Track this change
            self._preview_changes.append({
                'start': char_pos,
                'length': len(new_line) + 1,
                'original': "",
                'type': 'insertion'
            })
            
            # Apply preview styling (blue for insertions)
            cursor.setPosition(char_pos)
            cursor.setPosition(char_pos + len(new_line), QtGui.QTextCursor.KeepAnchor)
            
            char_format = QtGui.QTextCharFormat()
            char_format.setBackground(QtGui.QColor(59, 130, 246, 40))  # Blue background for insertions
            char_format.setProperty(QtGui.QTextFormat.OutlinePen, QtGui.QPen(QtGui.QColor(59, 130, 246), 1))
            cursor.setCharFormat(char_format)

    def _revert_code_preview(self):
        """Revert the code preview to original state."""
        current_editor = self._get_current_editor()
        if not current_editor or not hasattr(self, '_original_content'):
            return
            
        # Restore original content completely
        current_editor.setPlainText(self._original_content)
        
        # Restore cursor position
        cursor = current_editor.textCursor()
        cursor.setPosition(self._original_cursor_position)
        current_editor.setTextCursor(cursor)
        
        # Clear preview state
        self._preview_applied = False
        self._preview_changes = []
        
    def _commit_code_preview(self):
        """Commit the preview (remove special formatting, keep the code)."""
        current_editor = self._get_current_editor()
        if not current_editor or not hasattr(self, '_preview_applied') or not self._preview_applied:
            return
            
        # Clear formatting from all preview changes
        if hasattr(self, '_preview_changes') and self._preview_changes:
            # Handle diff-based changes
            for change in self._preview_changes:
                cursor = current_editor.textCursor()
                cursor.setPosition(change['start'])
                cursor.setPosition(change['start'] + change['length'], QtGui.QTextCursor.KeepAnchor)
                
                # Clear formatting
                char_format = QtGui.QTextCharFormat()
                cursor.setCharFormat(char_format)
        else:
            # Handle simple insertion
            cursor = current_editor.textCursor()
            if hasattr(self, '_preview_start_pos') and hasattr(self, '_preview_length'):
                cursor.setPosition(self._preview_start_pos)
                cursor.setPosition(self._preview_start_pos + self._preview_length, QtGui.QTextCursor.KeepAnchor)
                
                # Clear formatting
                char_format = QtGui.QTextCharFormat()
                cursor.setCharFormat(char_format)
                
                # Position cursor at end of inserted code
                cursor.setPosition(self._preview_start_pos + self._preview_length)
                current_editor.setTextCursor(cursor)
        
        # Clear preview state
        self._preview_applied = False
        self._preview_changes = []

    def _copy_code_to_clipboard(self, code):
        """Copy code to system clipboard."""
        try:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(code)
            self.console.append_tagged("COPY", "Clean code copied to clipboard successfully", "#22c55e")
        except Exception as e:
            self.console.append_tagged("ERROR", f"Failed to copy code: {str(e)}", "#ef4444")

    def _apply_code_to_editor(self, code):
        """Apply code directly to the current editor tab."""
        try:
            current_editor = self._get_current_editor()
            if not current_editor:
                self.console.append_tagged("WARNING", "No editor tab open - please create or select an editor first", "#f59e0b")
                return
                
            # Get current cursor position
            cursor = current_editor.textCursor()
            
            # Insert clean code at cursor position
            cursor.insertText(code)
            
            # Select the inserted text for easy review
            start_pos = cursor.position() - len(code)
            cursor.setPosition(start_pos)
            cursor.setPosition(start_pos + len(code), QtGui.QTextCursor.KeepAnchor)
            current_editor.setTextCursor(cursor)
            
            lines_count = code.count('\n') + 1
            self.console.append_tagged("APPLY", f"Code applied to editor ({lines_count} lines inserted and selected for review)", "#22c55e")
            
        except Exception as e:
            self.console.append_tagged("ERROR", f"Failed to apply code: {str(e)}", "#ef4444")

    def _keep_as_fix(self, code):
        """Keep code as a fix and apply it to the current editor."""
        try:
            current_editor = self._get_current_editor()
            if not current_editor:
                self.console.append_tagged("WARNING", "No editor tab open - please create or select an editor first", "#f59e0b")
                return
                
            # Apply the fix code directly
            cursor = current_editor.textCursor()
            cursor.insertText(code)
            
            # Select the inserted code
            start_pos = cursor.position() - len(code)
            cursor.setPosition(start_pos)
            cursor.setPosition(start_pos + len(code), QtGui.QTextCursor.KeepAnchor)
            current_editor.setTextCursor(cursor)
            
            lines_count = code.count('\n') + 1
            self.console.append_tagged("FIX", f"Code fix applied to editor ({lines_count} lines) - review and modify as needed", "#f59e0b")
            
        except Exception as e:
            self.console.append_tagged("ERROR", f"Failed to apply fix: {str(e)}", "#ef4444")

    def _show_fix_preview_dialog(self, current_content, fix_code, editor):
        """Show a dialog to preview and apply code fixes."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Code Fix Preview")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(DARK_STYLE)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Header
        header_label = QtWidgets.QLabel("Review and Apply Code Fix")
        header_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f0f6fc; padding: 8px;")
        layout.addWidget(header_label)
        
        # Tabs for before/after comparison
        tab_widget = QtWidgets.QTabWidget()
        
        # Before tab
        before_tab = QtWidgets.QTextEdit()
        before_tab.setPlainText(current_content)
        before_tab.setReadOnly(True)
        before_tab.setStyleSheet("background: #1e1e1e; color: #ddd; font-family: Consolas, monospace;")
        tab_widget.addTab(before_tab, "📄 Current Code")
        
        # Fix tab  
        fix_tab = QtWidgets.QTextEdit()
        fix_tab.setPlainText(fix_code)
        fix_tab.setStyleSheet("background: #1e1e1e; color: #ddd; font-family: Consolas, monospace;")
        tab_widget.addTab(fix_tab, "🔧 Suggested Fix")
        
        # Preview tab (merged result)
        preview_tab = QtWidgets.QTextEdit()
        merged_content = self._merge_code_intelligently(current_content, fix_code)
        preview_tab.setPlainText(merged_content)
        preview_tab.setStyleSheet("background: #1e1e1e; color: #ddd; font-family: Consolas, monospace;")
        tab_widget.addTab(preview_tab, "👁️ Preview Result")
        
        layout.addWidget(tab_widget)
        
        # Options
        options_layout = QtWidgets.QHBoxLayout()
        
        replace_radio = QtWidgets.QRadioButton("Replace entire content")
        append_radio = QtWidgets.QRadioButton("Append to end")
        merge_radio = QtWidgets.QRadioButton("Smart merge (recommended)")
        merge_radio.setChecked(True)
        
        options_layout.addWidget(replace_radio)
        options_layout.addWidget(append_radio)
        options_layout.addWidget(merge_radio)
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        apply_btn = QtWidgets.QPushButton("✅ Apply Fix")
        apply_btn.setStyleSheet("QPushButton { background: #238636; color: white; padding: 8px 16px; border-radius: 4px; }")
        
        cancel_btn = QtWidgets.QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("QPushButton { background: #da3633; color: white; padding: 8px 16px; border-radius: 4px; }")
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        # Connect buttons
        def apply_fix():
            try:
                if replace_radio.isChecked():
                    editor.setPlainText(fix_code)
                elif append_radio.isChecked():
                    editor.setPlainText(current_content + "\n\n# Added by Morpheus AI\n" + fix_code)
                else:  # Smart merge
                    editor.setPlainText(merged_content)
                
                self._show_info_message("Fix Applied!", "Code fix has been applied successfully.")
                dialog.accept()
                
            except Exception as e:
                self._show_info_message("Apply Error", f"Failed to apply fix: {str(e)}")
        
        apply_btn.clicked.connect(apply_fix)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Update preview when option changes
        def update_preview():
            if replace_radio.isChecked():
                preview_tab.setPlainText(fix_code)
            elif append_radio.isChecked():
                preview_tab.setPlainText(current_content + "\n\n# Added by Morpheus AI\n" + fix_code)
            else:
                preview_tab.setPlainText(merged_content)
        
        replace_radio.toggled.connect(update_preview)
        append_radio.toggled.connect(update_preview)
        merge_radio.toggled.connect(update_preview)
        
        dialog.exec()

    def _merge_code_intelligently(self, current_content, fix_code):
        """Intelligently merge fix code with current content."""
        import re
        
        # Simple intelligent merging:
        # 1. If fix_code contains function definitions, try to replace existing ones
        # 2. If it's imports, add to top
        # 3. Otherwise, append with clear separation
        
        fix_lines = fix_code.strip().split('\n')
        current_lines = current_content.split('\n')
        
        # Check if fix contains imports
        if any(line.strip().startswith(('import ', 'from ')) for line in fix_lines):
            # Add imports at the top (after existing imports)
            import_end = 0
            for i, line in enumerate(current_lines):
                if line.strip().startswith(('import ', 'from ', '#')):
                    import_end = i + 1
            
            current_lines.insert(import_end, "")
            current_lines.insert(import_end + 1, "# Added by Morpheus AI")
            for line in fix_lines:
                current_lines.insert(import_end + 2, line)
                import_end += 1
            
            return '\n'.join(current_lines)
        
        # Check if fix contains function definitions
        func_pattern = r'^def\s+(\w+)\s*\('
        fix_functions = []
        for line in fix_lines:
            match = re.match(func_pattern, line.strip())
            if match:
                fix_functions.append(match.group(1))
        
        if fix_functions:
            # Try to replace existing functions
            result_lines = []
            i = 0
            while i < len(current_lines):
                line = current_lines[i]
                match = re.match(func_pattern, line.strip())
                
                if match and match.group(1) in fix_functions:
                    # Skip existing function
                    indent_level = len(line) - len(line.lstrip())
                    i += 1
                    while i < len(current_lines):
                        next_line = current_lines[i]
                        if (next_line.strip() and 
                            (len(next_line) - len(next_line.lstrip())) <= indent_level and 
                            not next_line.strip().startswith(('"""', "'''", '#'))):
                            break
                        i += 1
                    continue
                else:
                    result_lines.append(line)
                    i += 1
            
            # Add the fix code
            result_lines.extend(["", "# Updated by Morpheus AI"] + fix_lines)
            return '\n'.join(result_lines)
        
        # Default: append with separation
        return current_content + "\n\n# Added by Morpheus AI\n" + fix_code

    def _get_current_editor(self):
        """Get the currently active code editor."""
        try:
            # Use the same pattern as the existing code
            w = self.tabWidget.currentWidget()
            return w if isinstance(w, CodeEditor) else None
        except Exception as e:
            print(f"[DEBUG] Error getting current editor: {e}")
            return None

    def _show_info_message(self, title, message):
        """Show an informational message dialog."""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setStyleSheet(DARK_STYLE)
        msg_box.exec()

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