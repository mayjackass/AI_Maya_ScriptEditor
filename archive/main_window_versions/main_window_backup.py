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


# Internal imports - handle different execution contexts
import sys
import os

# Add current directory to path for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Try relative imports first (standalone execution)
    from editor.code_editor import CodeEditor
    from editor.highlighter import PythonHighlighter, MELHighlighter
    from model.hierarchy import CodeHierarchyModel
    from ui.output_console import OutputConsole
    from debug_system import DebugSession, DebugControlPanel
    from ai.chat import AIMorpheus
    from ai.copilot_manager import MorpheusManager
except ImportError:
    # Fallback for Maya or different execution contexts
    try:
        from ai_script_editor.editor.code_editor import CodeEditor
        from ai_script_editor.editor.highlighter import PythonHighlighter, MELHighlighter
        from ai_script_editor.model.hierarchy import CodeHierarchyModel
        from ai_script_editor.ui.output_console import OutputConsole
        from ai_script_editor.debug_system import DebugSession, DebugControlPanel
        from ai_script_editor.ai.chat import AIMorpheus
        from ai_script_editor.ai.copilot_manager import MorpheusManager
    except ImportError as e:
        print(f"Import error: {e}")
        print("Trying to import from current directory...")
        # Last resort - direct imports assuming current directory
        sys.path.insert(0, os.path.join(current_dir, 'editor'))
        sys.path.insert(0, os.path.join(current_dir, 'model'))
        sys.path.insert(0, os.path.join(current_dir, 'ui'))
        sys.path.insert(0, os.path.join(current_dir, 'ai'))
        
        from code_editor import CodeEditor
        from highlighter import PythonHighlighter, MELHighlighter
        from hierarchy import CodeHierarchyModel
        from output_console import OutputConsole
        from debug_system import DebugSession, DebugControlPanel
        from chat import AIMorpheus
        from copilot_manager import MorpheusManager


VSCODE_STYLE = """
/* Main application styling - VS Code theme */
QMainWindow {
    background-color: #1E1E1E;
    color: #CCCCCC;
    font-family: 'Segoe UI', 'Consolas', monospace;
}

/* Menu and toolbar styling */
QMenuBar {
    background-color: #2D2D30;
    color: #CCCCCC;
    border: none;
    font-size: 11pt;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
}
QMenuBar::item:selected {
    background-color: #094771;
    color: white;
}

QMenu {
    background-color: #252526;
    border: 1px solid #3C3C3C;
    color: #CCCCCC;
    font-size: 11pt;
}
QMenu::item {
    padding: 5px 20px;
}
QMenu::item:selected {
    background-color: #094771;
    color: white;
}

/* Toolbar styling - VS Code look */
QToolBar {
    background-color: #2D2D30;
    border: none;
    spacing: 2px;
    padding: 2px;
}
QToolBar::separator {
    background-color: #3C3C3C;
    width: 1px;
    margin: 4px 2px;
}
QToolButton {
    background-color: transparent;
    border: none;
    color: #CCCCCC;
    padding: 4px;
    margin: 1px;
    border-radius: 3px;
    font-size: 16px;
}
QToolButton:hover {
    background-color: #3C3C3C;
    color: white;
}
QToolButton:pressed {
    background-color: #094771;
    color: white;
}

/* Tab styling */
QTabWidget::pane {
    border: 1px solid #3C3C3C;
    background-color: #1E1E1E;
}
QTabBar::tab {
    background-color: #2D2D30;
    color: #CCCCCC;
    padding: 8px 16px;
    border: 1px solid #3C3C3C;
    border-bottom: none;
    margin-right: 1px;
}
QTabBar::tab:selected {
    background-color: #1E1E1E;
    color: white;
    border-bottom: 2px solid #007ACC;
}
QTabBar::tab:hover {
    background-color: #3C3C3C;
}

/* Text editors */
QTextEdit, QPlainTextEdit {
    background-color: #1E1E1E;
    color: #CCCCCC;
    border: 1px solid #3C3C3C;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11pt;
    selection-background-color: #264F78;
}

/* Buttons */
QPushButton {
    background-color: #2D2D30;
    color: #CCCCCC;
    border: 1px solid #3C3C3C;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: 10pt;
}
QPushButton:hover {
    background-color: #3C3C3C;
    border-color: #007ACC;
}
QPushButton:pressed {
    background-color: #094771;
    color: white;
}

/* Input fields */
QLineEdit {
    background-color: #3C3C3C;
    border: 1px solid #5A5A5A;
    color: #CCCCCC;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: 10pt;
}
QLineEdit:focus {
    border-color: #007ACC;
}

/* Dock widgets */
QDockWidget {
    background-color: #252526;
    color: #CCCCCC;
}
QDockWidget::title {
    background-color: #2D2D30;
    color: #CCCCCC;
    padding: 4px;
    text-align: center;
}

/* Tree and list widgets */
QTreeWidget, QListWidget {
    background-color: #252526;
    color: #CCCCCC;
    border: 1px solid #3C3C3C;
    alternate-background-color: #2A2A2A;
}
QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #094771;
    color: white;
}
QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: #2A373F;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #2D2D30;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #424242;
    min-height: 20px;
    border-radius: 6px;
    margin: 1px;
}
QScrollBar::handle:vertical:hover {
    background-color: #4F4F4F;
}

QScrollBar:horizontal {
    background-color: #2D2D30;
    height: 12px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #424242;
    min-width: 20px;
    border-radius: 6px;
    margin: 1px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #4F4F4F;
}

/* Status bar */
QStatusBar {
    background-color: #007ACC;
    color: white;
    border: none;
}
"""

class AiScriptEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEO Script Editor v2.0")
        self.resize(1200, 700)
        self.setStyleSheet(VSCODE_STYLE)

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
        # Debug Session (Create before docks)
        # --------------------------
        self.debug_session = DebugSession(self)
        self.debug_session.debugStarted.connect(self._on_debug_started)
        self.debug_session.debugStopped.connect(self._on_debug_stopped)
        self.debug_session.debugPaused.connect(self._on_debug_paused)

        # --------------------------
        # Dock Widgets
        # --------------------------
        self._build_console_dock()  # Create console first
        self._build_problems_dock()
        self._build_explorer_dock()  # Now explorer can use console
        self._build_debug_dock()     # Debug panel
        self._build_chat_dock()

        # --------------------------
        # Status Bar
        # --------------------------
        self._build_status_bar()

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

        # Status Bar removed - using chat status indicator instead

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
        
        # Load current directory by default
        import os
        current_dir = os.getcwd()
        self._load_folder_in_explorer(current_dir)

    def _build_console_dock(self):
        self.console = OutputConsole(self)
        dock = QtWidgets.QDockWidget("Console", self)
        dock.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)

    def _build_problems_dock(self):
        self.problemsList = QtWidgets.QListWidget()
        dock = QtWidgets.QDockWidget("Problems", self)
        dock.setWidget(self.problemsList)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)

    def _build_debug_dock(self):
        """Create debug panel with breakpoint controls and variable inspection."""
        self.debug_panel = DebugControlPanel(self)
        self.debug_panel.set_debug_session(self.debug_session)
        
        dock = QtWidgets.QDockWidget("Debug", self)
        dock.setWidget(self.debug_panel)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
        # Initially hidden - shown when debugging starts
        dock.setVisible(True)  # Keep visible for easy access

    # ==========================================================
    # Status Bar (VS Code Style)
    # ==========================================================
    def _build_status_bar(self):
        """Create VS Code-style status bar."""
        self.statusbar = self.statusBar()
        
        # Left side - file info
        self.file_info_label = QtWidgets.QLabel("Ready")
        self.file_info_label.setStyleSheet("color: white; padding: 2px 8px;")
        self.statusbar.addWidget(self.file_info_label)
        
        # Add separator
        self.statusbar.addPermanentWidget(QtWidgets.QLabel("|"))
        
        # Line and column position
        self.position_label = QtWidgets.QLabel("Ln 1, Col 1")
        self.position_label.setStyleSheet("color: white; padding: 2px 8px;")
        self.statusbar.addPermanentWidget(self.position_label)
        
        # Language indicator
        self.language_label = QtWidgets.QLabel("Python")
        self.language_label.setStyleSheet("color: white; padding: 2px 8px; font-weight: bold;")
        self.statusbar.addPermanentWidget(self.language_label)
        
        # Encoding indicator
        self.encoding_label = QtWidgets.QLabel("UTF-8")
        self.encoding_label.setStyleSheet("color: white; padding: 2px 8px;")
        self.statusbar.addPermanentWidget(self.encoding_label)

    def _update_status_bar(self):
        """Update status bar with current file information."""
        editor = self._current_editor()
        if editor:
            # Update cursor position
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.position_label.setText(f"Ln {line}, Col {col}")
            
            # Update language
            language = getattr(editor, 'language', 'Python')
            self.language_label.setText(language)
            
            # Update file info
            filename = getattr(editor, 'filename', None)
            if filename:
                import os
                basename = os.path.basename(filename)
                modified = "*" if editor.document().isModified() else ""
                self.file_info_label.setText(f"{basename}{modified}")
            else:
                modified = "*" if editor.document().isModified() else ""
                self.file_info_label.setText(f"untitled{modified}")

    # ==========================================================
    # Morpheus Chat Dock  (Exact VS Code Replica)
    # ==========================================================
    def _build_chat_dock(self):
        """Create right-side Morpheus Chat panel (styled like GitHub Morpheus Chat)."""
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
        self.prevChatBtn.setToolTip("Previous chat (Ctrl+↑)")
        self.prevChatBtn.clicked.connect(self._navigate_chat_history_prev)
        
        self.nextChatBtn = QtWidgets.QPushButton("▶")
        self.nextChatBtn.setFixedSize(24, 24)
        self.nextChatBtn.setToolTip("Next chat (Ctrl+↓)")
        self.nextChatBtn.clicked.connect(self._navigate_chat_history_next)
        
        # History info label
        self.historyInfoLabel = QtWidgets.QLabel("No history")
        self.historyInfoLabel.setStyleSheet("color: #666; font-size: 10px;")
        
        # Clear history button
        self.clearHistoryBtn = QtWidgets.QPushButton("🗑️")
        self.clearHistoryBtn.setFixedSize(24, 24)
        self.clearHistoryBtn.setToolTip("Clear chat history")
        self.clearHistoryBtn.clicked.connect(self._clear_chat_history)
        
        historyLayout.addWidget(self.prevChatBtn)
        historyLayout.addWidget(self.nextChatBtn)
        historyLayout.addWidget(self.historyInfoLabel)
        historyLayout.addStretch()
        historyLayout.addWidget(self.clearHistoryBtn)
        
        chatLayout.addLayout(historyLayout)

        # ---------- chat display (QTextBrowser)
        self.chatDisplay = QtWidgets.QTextBrowser(chatWidget)
        self.chatDisplay.setObjectName("chatDisplay")
        self.chatDisplay.setAcceptRichText(True)
        self.chatDisplay.setOpenExternalLinks(True)
        self.chatDisplay.setReadOnly(True)
        self.chatDisplay.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.chatDisplay.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #f0f6fc;
                border: 1px solid #21262d;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                padding: 12px;
            }
            QScrollBar:vertical { 
                background: #0d1117; 
                width: 10px; 
                border: none;
            }
            QScrollBar::handle:vertical { 
                background: #21262d; 
                border-radius: 5px; 
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { 
                background: #30363d; 
            }
        """)
        chatLayout.addWidget(self.chatDisplay)

        # ---------- suggestion action buttons (initially hidden)
        self.suggestionButtonsWidget = QtWidgets.QWidget(chatWidget)
        self.suggestionButtonsWidget.setVisible(False)  # Hidden by default
        suggestionButtonsLayout = QtWidgets.QHBoxLayout(self.suggestionButtonsWidget)
        suggestionButtonsLayout.setContentsMargins(16, 8, 16, 8)
        suggestionButtonsLayout.setSpacing(8)
        
        # Apply button
        self.applySuggestionBtn = QtWidgets.QPushButton("Apply in Editor", self.suggestionButtonsWidget)
        self.applySuggestionBtn.setCursor(QtCore.Qt.PointingHandCursor)
        self.applySuggestionBtn.setStyleSheet("""
            QPushButton {
                background: #238636;
                color: #ffffff;
                border: 1px solid #1a7f37;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }
            QPushButton:hover { 
                background: #2ea043; 
                border-color: #238636;
            }
            QPushButton:pressed { 
                background: #1a7f37; 
                border-color: #176f2c;
            }
        """)
        self.applySuggestionBtn.clicked.connect(self._apply_suggestion)
        suggestionButtonsLayout.addWidget(self.applySuggestionBtn)
        print(f"[DEBUG] Apply button created and added to layout")
        
        # Copy button
        self.copySuggestionBtn = QtWidgets.QPushButton("Copy", self.suggestionButtonsWidget)
        self.copySuggestionBtn.setCursor(QtCore.Qt.PointingHandCursor)
        self.copySuggestionBtn.setStyleSheet("""
            QPushButton {
                background: #0969da;
                color: #ffffff;
                border: 1px solid #0860ca;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }
            QPushButton:hover { 
                background: #0b7fdb; 
                border-color: #0969da;
            }
            QPushButton:pressed { 
                background: #0860ca; 
                border-color: #0756b3;
            }
        """)
        self.copySuggestionBtn.clicked.connect(self._copy_suggestion)
        suggestionButtonsLayout.addWidget(self.copySuggestionBtn)
        
        # Ignore button
        self.ignoreSuggestionBtn = QtWidgets.QPushButton("Ignore", self.suggestionButtonsWidget)
        self.ignoreSuggestionBtn.setCursor(QtCore.Qt.PointingHandCursor)
        self.ignoreSuggestionBtn.setStyleSheet("""
            QPushButton {
                background: #656d76;
                color: #ffffff;
                border: 1px solid #57606a;
                border-radius: 6px;
                padding: 6px 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }
            QPushButton:hover { 
                background: #6e7681; 
                border-color: #656d76;
            }
            QPushButton:pressed { 
                background: #57606a; 
                border-color: #4c545d;
            }
        """)
        self.ignoreSuggestionBtn.clicked.connect(self._ignore_suggestion)
        suggestionButtonsLayout.addWidget(self.ignoreSuggestionBtn)
        
        suggestionButtonsLayout.addStretch()  # Push buttons to the left
        chatLayout.addWidget(self.suggestionButtonsWidget)
        print(f"[DEBUG] Suggestion buttons widget added to chat layout")
        print(f"[DEBUG] Button layout has {suggestionButtonsLayout.count()} items")

        # ---------- input bar (bottom)
        inputLayout = QtWidgets.QHBoxLayout()
        inputLayout.setSpacing(6)
        inputLayout.setContentsMargins(0, 0, 0, 0)

        self.chatInput = QtWidgets.QLineEdit(chatWidget)
        self.chatInput.setPlaceholderText("Ask Morpheus something... (Press Enter)")
        self.chatInput.setClearButtonEnabled(True)
        self.chatInput.setStyleSheet("""
            QLineEdit {
                background: #21262d;
                border: 1px solid #30363d;
                color: #f0f6fc;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
                font-size: 14px;
            }
            QLineEdit:focus { 
                border: 1px solid #58a6ff; 
                outline: none;
            }
        """)
        inputLayout.addWidget(self.chatInput)

        sendBtn = QtWidgets.QPushButton("Send", chatWidget)
        sendBtn.setFixedWidth(64)
        sendBtn.setCursor(QtCore.Qt.PointingHandCursor)
        sendBtn.setStyleSheet("""
            QPushButton {
                background: #238636;
                color: #ffffff;
                border: 1px solid #238636;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { 
                background: #2ea043; 
                border-color: #2ea043;
            }
            QPushButton:pressed { 
                background: #1a7f37; 
                border-color: #1a7f37;
            }
        """)
        inputLayout.addWidget(sendBtn)
        chatLayout.addLayout(inputLayout)

        # ---------- status indicator (below input, smaller)
        self.statusIndicator = QtWidgets.QLabel("🧠 Ready", chatWidget)
        self.statusIndicator.setStyleSheet("""
            QLabel {
                color: #7c3aed;
                font-family: "Segoe UI", Consolas, monospace;
                font-size: 9pt;
                padding: 2px 6px;
                background: rgba(124, 58, 237, 0.1);
                border-radius: 3px;
                margin: 2px 4px;
            }
        """)
        self.statusIndicator.setAlignment(QtCore.Qt.AlignCenter)
        chatLayout.addWidget(self.statusIndicator)

        chatDock.setWidget(chatWidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, chatDock)

        # ---------- signal connections
        sendBtn.clicked.connect(self._send_prompt)
        self.chatInput.returnPressed.connect(self._send_prompt)

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

        # Debug menu
        debugMenu = mb.addMenu("&Debug")
        debugMenu.addAction("Start Debugging", self._start_debugging, QtGui.QKeySequence("F5"))
        debugMenu.addAction("Stop Debugging", self._stop_debugging, QtGui.QKeySequence("Shift+F5"))
        debugMenu.addSeparator()
        debugMenu.addAction("Toggle Breakpoint", self._toggle_breakpoint, QtGui.QKeySequence("F9"))
        debugMenu.addAction("Clear All Breakpoints", self._clear_all_breakpoints, QtGui.QKeySequence("Ctrl+Shift+F9"))
        debugMenu.addSeparator()
        debugMenu.addAction("Step Over", self._debug_step_over, QtGui.QKeySequence("F10"))
        debugMenu.addAction("Step Into", self._debug_step_into, QtGui.QKeySequence("F11"))
        debugMenu.addAction("Step Out", self._debug_step_out, QtGui.QKeySequence("Shift+F11"))
        debugMenu.addAction("Continue", self._debug_continue, QtGui.QKeySequence("F5"))

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
        
        # Add indentation guide options
        viewMenu.addSeparator()
        
        # Toggle indentation guides
        self.indent_guides_action = QtGui.QAction("Show Indentation Guides", self)
        self.indent_guides_action.setCheckable(True)
        self.indent_guides_action.setChecked(True)  # Default enabled
        self.indent_guides_action.triggered.connect(self._toggle_indentation_guides)
        viewMenu.addAction(self.indent_guides_action)

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
        """Create organized VS Code-style toolbars."""
        # Main toolbar for file operations
        main_toolbar = self.addToolBar("File")
        main_toolbar.setObjectName("FileToolbar")
        main_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        main_toolbar.setIconSize(QtCore.QSize(16, 16))
        
        # File operations group
        self._add_toolbar_action(main_toolbar, "New", "Ctrl+N", self._new_file, "📄", "Create new file")
        self._add_toolbar_action(main_toolbar, "Open", "Ctrl+O", self._open_file, "📁", "Open file")
        self._add_toolbar_action(main_toolbar, "Save", "Ctrl+S", self._save_file, "💾", "Save current file")
        self._add_toolbar_action(main_toolbar, "Save All", "Ctrl+Shift+S", self._save_all_files, "💾", "Save all open files")
        
        main_toolbar.addSeparator()
        
        # Edit operations
        self._add_toolbar_action(main_toolbar, "Undo", "Ctrl+Z", self._undo, "↶", "Undo last action")
        self._add_toolbar_action(main_toolbar, "Redo", "Ctrl+Y", self._redo, "↷", "Redo last action")
        
        main_toolbar.addSeparator()
        
        # Search operations
        self._add_toolbar_action(main_toolbar, "Find", "Ctrl+F", self._editor_search, "🔍", "Find in file")
        self._add_toolbar_action(main_toolbar, "Replace", "Ctrl+H", self._show_find_replace, "🔄", "Find and replace")
        
        # Debug toolbar
        debug_toolbar = self.addToolBar("Debug")
        debug_toolbar.setObjectName("DebugToolbar")
        debug_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        debug_toolbar.setIconSize(QtCore.QSize(16, 16))
        
        # Debug operations
        self._add_toolbar_action(debug_toolbar, "Start Debug", "F5", self._start_debugging, "▶️", "Start debugging (F5)")
        self._add_toolbar_action(debug_toolbar, "Stop Debug", "Shift+F5", self._stop_debugging, "⏹️", "Stop debugging")
        self._add_toolbar_action(debug_toolbar, "Toggle Breakpoint", "F9", self._toggle_breakpoint, "🔴", "Toggle breakpoint")
        
        debug_toolbar.addSeparator()
        
        self._add_toolbar_action(debug_toolbar, "Step Over", "F10", self._debug_step_over, "⏭️", "Step over (F10)")
        self._add_toolbar_action(debug_toolbar, "Step Into", "F11", self._debug_step_into, "⬇️", "Step into (F11)")
        self._add_toolbar_action(debug_toolbar, "Step Out", "Shift+F11", self._debug_step_out, "⬆️", "Step out")
        self._add_toolbar_action(debug_toolbar, "Continue", "F5", self._debug_continue, "▶️", "Continue execution")
        
        # Run toolbar  
        run_toolbar = self.addToolBar("Run")
        run_toolbar.setObjectName("RunToolbar")
        run_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        run_toolbar.setIconSize(QtCore.QSize(16, 16))
        
        # Run operations
        self._add_toolbar_action(run_toolbar, "Run Script", "F5", self._run_script, "▶️", "Run current script (F5)")
        self._add_toolbar_action(run_toolbar, "Run Selection", "F9", self._run_selection, "🎯", "Run selected code (F9)")
        
        run_toolbar.addSeparator()
        
        # Code tools
        self._add_toolbar_action(run_toolbar, "Format Code", "Ctrl+Shift+F", self._format_code, "🎨", "Format code")
        self._add_toolbar_action(run_toolbar, "Check Syntax", "Ctrl+E", self._check_syntax_errors, "✅", "Check syntax errors")
        self._add_toolbar_action(run_toolbar, "Clear Errors", "Ctrl+Shift+E", self._clear_error_highlights, "❌", "Clear error highlights")
        
        run_toolbar.addSeparator()
        
        # Console operations
        self._add_toolbar_action(run_toolbar, "Clear Console", "", self._clear_console, "🗑️", "Clear output console")
        
    def _add_toolbar_action(self, toolbar, text, shortcut, slot, icon_text, tooltip):
        """Helper to add consistent toolbar actions."""
        action = QtGui.QAction(text, self)
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        action.triggered.connect(slot)
        action.setToolTip(f"{tooltip} ({shortcut})" if shortcut else tooltip)
        
        # Create icon with text (will be styled with CSS)
        action.setText(icon_text)
        toolbar.addAction(action)
        return action
        
    def _new_file(self):
        """Create a new file."""
        self.new_tab("untitled", "")
        
    def _save_all_files(self):
        """Save all open files."""
        for i in range(self.tabWidget.count()):
            editor = self.tabWidget.widget(i)
            if hasattr(editor, 'filename') and editor.filename:
                # Save existing files
                self._save_file_at_index(i)
            elif editor.document().isModified():
                # Prompt for new files
                self.tabWidget.setCurrentIndex(i)
                self._save_file_as()
                
    def _save_file_at_index(self, index):
        """Save file at specific tab index."""
        editor = self.tabWidget.widget(index)
        if editor and hasattr(editor, 'filename') and editor.filename:
            try:
                with open(editor.filename, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                editor.document().setModified(False)
                return True
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Save Error", f"Could not save file: {str(e)}")
        return False

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
        
        # Connect cursor position changes for status bar updates
        editor.cursorPositionChanged.connect(self._update_status_bar)
        editor.textChanged.connect(self._update_status_bar)
        
        # Enable autocomplete
        editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
        
        idx = self.tabWidget.addTab(editor, tab_title)
        self.tabWidget.setCurrentIndex(idx)
        
        # Update status bar for new tab
        self._update_status_bar()
        
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
        """Handle tab switching to update status bar."""
        if index >= 0:
            self._update_status_bar()

    def _open_file(self):
        file_filter = "All Script Files (*.py *.mel);;Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Script File", os.getcwd(), file_filter)
        if not path: return
        
        # Auto-detect language based on file extension
        if path.lower().endswith('.mel'):
            self.languageCombo.setCurrentText("MEL")
        elif path.lower().endswith('.py'):
            self.languageCombo.setCurrentText("Python")
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        editor = self.new_tab(os.path.basename(path), content)
        editor.setProperty("filePath", path)
        self.console.append(f"Opened: {path}")

    def _save_file(self):
        editor = self._active_editor()
        if not editor: return
        path = editor.property("filePath")
        if not path:
            return self._save_file_as()
        with open(path, "w", encoding="utf-8") as f:
            f.write(editor.toPlainText())
        
        # Mark as not modified and remove asterisk from tab title
        editor.setProperty("isModified", False)
        self._update_tab_title_for_editor(editor, remove_modification_indicator=True)
        
        self.console.append(f"Saved: {path}")

    def _save_file_as(self):
        editor = self._active_editor()
        if not editor: return
        
        # Set default filter based on current language
        current_lang = self.languageCombo.currentText()
        if current_lang == "MEL":
            file_filter = "MEL Files (*.mel);;Python Files (*.py);;All Files (*)"
            default_ext = ".mel"
        else:
            file_filter = "Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
            default_ext = ".py"
            
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Script File", os.getcwd(), file_filter)
        if not path: return
        
        # Add appropriate extension if not present
        if not (path.lower().endswith('.py') or path.lower().endswith('.mel')):
            path += default_ext
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(editor.toPlainText())
        editor.setProperty("filePath", path)
        
        # Mark as not modified and update tab title
        editor.setProperty("isModified", False)
        tab_title = self._get_tab_title_for_file(os.path.basename(path), editor.property("language"))
        self.tabWidget.setTabText(self.tabWidget.currentIndex(), tab_title)
        
        self.console.append(f"Saved As: {path}")

    # =========================================================
    # AI Copilot Integration
    # =========================================================
    def _send_prompt(self):
        """Send text from chatInput to Copilot."""
        text = self.chatInput.text().strip()
        if not text:
            return
        self.chatInput.clear()
        
        # Update status to thinking
        if hasattr(self, 'statusIndicator'):
            self.statusIndicator.setText("🧐 Thinking...")
            self.statusIndicator.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    font-family: "Segoe UI", Consolas, monospace;
                    font-size: 9pt;
                    padding: 2px 6px;
                    background: rgba(245, 158, 11, 0.1);
                    border-radius: 3px;
                    margin: 2px 4px;
                }
            """)
        
        ctx = ""
        if hasattr(self, "_active_editor"):
            editor = self._active_editor()
            if editor:
                ctx = editor.toPlainText()[-800:]
        if hasattr(self, "morpheus") and self.morpheus:
            self.morpheus.send_prompt(text, context=ctx)


    def _apply_suggestion(self):
        editor = self._active_editor()
        if not editor:
            self.console.append("⚠️ No editor open to apply suggestion.")
            return
        
        # Apply code to editor (replace mode to fix the script)
        ok = self.morpheus.apply_last_suggestion(editor, "replace")
        
        if ok:
            # Show success message in chat
            success_html = '''
<div style="margin:8px 12px; padding:6px 12px; background:#238636; color:white; border-radius:6px; font-size:12px;">
    ✅ Code applied to editor successfully
</div>
            '''
            self.chatDisplay.insertHtml(success_html)
            self.console.append("✅ Code suggestion applied to editor.")
            
        # Hide suggestion buttons
        if hasattr(self, 'suggestionButtonsWidget'):
            self.suggestionButtonsWidget.setVisible(False)
    
    def _copy_suggestion(self):
        """Copy the last suggestion to clipboard."""
        if hasattr(self, "morpheus") and self.morpheus and hasattr(self.morpheus, '_last_suggested_code'):
            if self.morpheus._last_suggested_code:
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(self.morpheus._last_suggested_code)
                
                # Show success message in chat
                success_html = '''
<div style="margin:8px 12px; padding:6px 12px; background:#0969da; color:white; border-radius:6px; font-size:12px;">
    📋 Code copied to clipboard
</div>
                '''
                self.chatDisplay.insertHtml(success_html)
                self.console.append("📋 Code copied to clipboard.")
            else:
                self.console.append("⚠️ No code suggestion to copy.")
        
        # Hide suggestion buttons
        if hasattr(self, 'suggestionButtonsWidget'):
            self.suggestionButtonsWidget.setVisible(False)
    
    def _ignore_suggestion(self):
        """Ignore the current suggestion and hide buttons."""
        # Show ignore message in chat
        ignore_html = '''
<div style="margin:8px 12px; padding:6px 12px; background:#656d76; color:white; border-radius:6px; font-size:12px;">
    ❌ Suggestion ignored
</div>
        '''
        self.chatDisplay.insertHtml(ignore_html)
        self.console.append("❌ Code suggestion ignored.")
        
        # Hide suggestion buttons
        if hasattr(self, 'suggestionButtonsWidget'):
            self.suggestionButtonsWidget.setVisible(False)
        else:
            self.console.append("❌ Failed to apply suggestion.")
    
    def _create_search_dialog(self):
        """Create the search dialog if it doesn't exist."""
        if hasattr(self, 'search_dialog') and self.search_dialog:
            return self.search_dialog
            
        self.search_dialog = QtWidgets.QDialog(self)
        self.search_dialog.setWindowTitle("Find and Replace")
        self.search_dialog.setFixedSize(450, 200)
        self.search_dialog.setStyleSheet(VSCODE_STYLE)
        
        layout = QtWidgets.QVBoxLayout(self.search_dialog)
        
        # Find section
        find_layout = QtWidgets.QHBoxLayout()
        find_layout.addWidget(QtWidgets.QLabel("Find:"))
        self.find_input = QtWidgets.QLineEdit()
        self.find_input.setPlaceholderText("Enter search text...")
        find_layout.addWidget(self.find_input)
        
        find_next_btn = QtWidgets.QPushButton("Find Next")
        find_next_btn.clicked.connect(self._find_next)
        find_layout.addWidget(find_next_btn)
        
        find_prev_btn = QtWidgets.QPushButton("Find Previous")
        find_prev_btn.clicked.connect(self._find_previous)
        find_layout.addWidget(find_prev_btn)
        
        layout.addLayout(find_layout)
        
        # Replace section
        replace_layout = QtWidgets.QHBoxLayout()
        replace_layout.addWidget(QtWidgets.QLabel("Replace:"))
        self.replace_input = QtWidgets.QLineEdit()
        self.replace_input.setPlaceholderText("Enter replacement text...")
        replace_layout.addWidget(self.replace_input)
        
        replace_btn = QtWidgets.QPushButton("Replace")
        replace_btn.clicked.connect(self._replace_current)
        replace_layout.addWidget(replace_btn)
        
        replace_all_btn = QtWidgets.QPushButton("Replace All")
        replace_all_btn.clicked.connect(self._replace_all)
        replace_layout.addWidget(replace_all_btn)
        
        layout.addLayout(replace_layout)
        
        # Options
        options_layout = QtWidgets.QHBoxLayout()
        self.case_sensitive_cb = QtWidgets.QCheckBox("Case sensitive")
        self.whole_word_cb = QtWidgets.QCheckBox("Whole word")
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_word_cb)
        options_layout.addStretch()
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.search_dialog.hide)
        options_layout.addWidget(close_btn)
        
        layout.addLayout(options_layout)
        
        # Connect Enter key to find next
        self.find_input.returnPressed.connect(self._find_next)
        self.replace_input.returnPressed.connect(self._replace_current)
        
        return self.search_dialog
    
    def _show_search(self):
        """Show search dialog and focus on find input."""
        dialog = self._create_search_dialog()
        self.replace_input.setVisible(False)
        # Hide replace buttons
        replace_layout = dialog.layout().itemAt(1).layout()
        replace_layout.itemAt(2).widget().setVisible(False)  # Replace button
        replace_layout.itemAt(3).widget().setVisible(False)  # Replace All button
        dialog.setWindowTitle("Find")
        dialog.setFixedSize(450, 120)
        dialog.show()
        dialog.raise_()
        self.find_input.setFocus()
        self.find_input.selectAll()
    
    def _show_find_replace(self):
        """Show full find and replace dialog."""
        dialog = self._create_search_dialog()
        self.replace_input.setVisible(True)
        # Show replace buttons
        replace_layout = dialog.layout().itemAt(1).layout()
        replace_layout.itemAt(2).widget().setVisible(True)  # Replace button
        replace_layout.itemAt(3).widget().setVisible(True)  # Replace All button
        dialog.setWindowTitle("Find and Replace")
        dialog.setFixedSize(450, 200)
        dialog.show()
        dialog.raise_()
        self.find_input.setFocus()
        self.find_input.selectAll()
    
    def _find_next(self):
        """Find next occurrence of search text."""
        editor = self._active_editor()
        if not editor or not self.find_input.text():
            return
            
        search_text = self.find_input.text()
        flags = QtGui.QTextDocument.FindFlags()
        
        if self.case_sensitive_cb.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.whole_word_cb.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
            
        cursor = editor.textCursor()
        found_cursor = editor.document().find(search_text, cursor, flags)
        
        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
            self.console.append(f"🔍 Found: '{search_text}'")
        else:
            # Try from beginning if not found
            found_cursor = editor.document().find(search_text, 0, flags)
            if not found_cursor.isNull():
                editor.setTextCursor(found_cursor)
                self.console.append(f"🔍 Found: '{search_text}' (wrapped to beginning)")
            else:
                self.console.append(f"⚠️ Not found: '{search_text}'")
    
    def _find_previous(self):
        """Find previous occurrence of search text."""
        editor = self._active_editor()
        if not editor or not self.find_input.text():
            return
            
        search_text = self.find_input.text()
        flags = QtGui.QTextDocument.FindFlags(QtGui.QTextDocument.FindBackward)
        
        if self.case_sensitive_cb.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.whole_word_cb.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
            
        cursor = editor.textCursor()
        found_cursor = editor.document().find(search_text, cursor, flags)
        
        if not found_cursor.isNull():
            editor.setTextCursor(found_cursor)
            self.console.append(f"🔍 Found: '{search_text}'")
        else:
            # Try from end if not found
            cursor.movePosition(QtGui.QTextCursor.End)
            found_cursor = editor.document().find(search_text, cursor, flags)
            if not found_cursor.isNull():
                editor.setTextCursor(found_cursor)
                self.console.append(f"🔍 Found: '{search_text}' (wrapped to end)")
            else:
                self.console.append(f"⚠️ Not found: '{search_text}'")
    
    def _replace_current(self):
        """Replace current selection if it matches search text."""
        editor = self._active_editor()
        if not editor or not self.find_input.text():
            return
            
        cursor = editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            search_text = self.find_input.text()
            
            # Check if selection matches search text (considering case sensitivity)
            matches = False
            if self.case_sensitive_cb.isChecked():
                matches = selected_text == search_text
            else:
                matches = selected_text.lower() == search_text.lower()
                
            if matches:
                cursor.insertText(self.replace_input.text())
                self.console.append(f"🔄 Replaced: '{search_text}' → '{self.replace_input.text()}'")
                self._find_next()  # Find next occurrence
            else:
                self.console.append("⚠️ Selection doesn't match search text")
        else:
            self._find_next()  # Find first occurrence
    
    def _replace_all(self):
        """Replace all occurrences of search text."""
        editor = self._active_editor()
        if not editor or not self.find_input.text():
            return
            
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        content = editor.toPlainText()
        
        if self.case_sensitive_cb.isChecked():
            count = content.count(search_text)
            new_content = content.replace(search_text, replace_text)
        else:
            # Case insensitive replacement
            import re
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            count = len(pattern.findall(content))
            new_content = pattern.sub(replace_text, content)
            
        if new_content != content:
            editor.setPlainText(new_content)
            self.console.append(f"🔄 Replaced {count} occurrences: '{search_text}' → '{replace_text}'")
        else:
            self.console.append(f"⚠️ No occurrences found: '{search_text}'")

    # =========================================================
    # Editor Actions
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
    
    def _find(self):
        # Simple find dialog
        editor = self._active_editor()
        if not editor:
            return
        
        text, ok = QtWidgets.QInputDialog.getText(self, "Find", "Find what:")
        if ok and text:
            cursor = editor.textCursor()
            document = editor.document()
            cursor = document.find(text, cursor)
            if not cursor.isNull():
                editor.setTextCursor(cursor)
            else:
                QtWidgets.QMessageBox.information(self, "Find", "Text not found.")
    
    def _run_script(self):
        """Run the entire current script."""
        editor = self._active_editor()
        if not editor:
            self.console.append("⚠️ No active editor to run.")
            return
        
        code = editor.toPlainText().strip()
        if not code:
            self.console.append("⚠️ No code to run.")
            return
        
        # Check current language
        current_lang = self.languageCombo.currentText()
        self.console.append(f"🚀 Running {current_lang} script...")
        
        if current_lang == "MEL":
            self._run_mel_code(code)
        else:
            self._run_python_code(code)
    
    def _run_python_code(self, code):
        """Execute Python code."""
        # Capture stdout to show print statements and results
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute in Maya's Python environment
            result = exec(code, globals())
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Restore stdout
            sys.stdout = old_stdout
            
            self.console.append("✅ Python script executed successfully.")
            
            # Show any print statements or output
            if output.strip():
                self.console.append("📄 Output:")
                for line in output.strip().split('\n'):
                    if line.strip():
                        self.console.append(f"   {line}")
                        
        except Exception as e:
            # Restore stdout in case of error
            sys.stdout = old_stdout
            
            import traceback
            tb = traceback.format_exc()
            # Extract line number from traceback
            lines = tb.split('\n')
            error_line = None
            for line in lines:
                if 'line ' in line and '<string>' in line:
                    try:
                        error_line = line.split('line ')[1].split(',')[0]
                        break
                    except:
                        pass
            
            if error_line:
                self.console.append(f"❌ Python Error on line {error_line}: {str(e)}")
            else:
                self.console.append(f"❌ Python Error: {str(e)}")
            
            # Show captured output even if there was an error
            output = captured_output.getvalue()
            if output.strip():
                self.console.append("📄 Output before error:")
                for line in output.strip().split('\n'):
                    if line.strip():
                        self.console.append(f"   {line}")
    
    def _run_mel_code(self, code):
        """Execute MEL code using maya.mel.eval()."""
        try:
            import maya.mel as mel
            
            # Execute MEL code
            result = mel.eval(code)
            
            self.console.append("✅ MEL script executed successfully.")
            
            # Show result if it exists and is not None
            if result is not None and str(result).strip():
                self.console.append(f"📄 Result: {result}")
                
        except ImportError:
            self.console.append("❌ Maya not available - cannot execute MEL commands.")
            self.console.append("💡 MEL execution requires running inside Maya.")
        except Exception as e:
            self.console.append(f"❌ MEL Error: {str(e)}")
            
            # Try to provide helpful error information
            error_str = str(e)
            if "line" in error_str.lower():
                self.console.append("💡 Check MEL syntax - semicolons, braces, etc.")
            
    def _run_selection(self):
        """Run only the selected code."""
        editor = self._active_editor()
        if not editor:
            self.console.append("⚠️ No active editor to run selection.")
            return
        
        cursor = editor.textCursor()
        if cursor.hasSelection():
            code = cursor.selectedText().strip()
        else:
            # Run current line if no selection
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            code = cursor.selectedText().strip()
        
        if not code:
            self.console.append("⚠️ No code selected to run.")
            return
        
        # Check current language
        current_lang = self.languageCombo.currentText()
        self.console.append(f"🎯 Running {current_lang} selection...")
        
        if current_lang == "MEL":
            self._run_mel_code(code)
        else:
            self._run_python_selection(code)
    
    def _run_python_selection(self, code):
        """Execute Python selection."""
        # Capture stdout for selection execution too
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            exec(code, globals())
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Restore stdout
            sys.stdout = old_stdout
            
            self.console.append("✅ Python selection executed successfully.")
            
            # Show any print statements or output
            if output.strip():
                self.console.append("📄 Selection output:")
                for line in output.strip().split('\n'):
                    if line.strip():
                        self.console.append(f"   {line}")
                        
        except Exception as e:
            # Restore stdout in case of error
            sys.stdout = old_stdout
            
            self.console.append(f"❌ Error: {str(e)}")
            
            # Show captured output even if there was an error
            output = captured_output.getvalue()
            if output.strip():
                self.console.append("📄 Selection output before error:")
                for line in output.strip().split('\n'):
                    if line.strip():
                        self.console.append(f"   {line}")
    
    def _clear_console(self):
        """Clear the output console."""
        self.console.clear()
        self.console.append("🧹 Console cleared.")
    
    def _lint_code(self):
        """Lint the current code for issues."""
        editor = self._active_editor()
        if not editor:
            return
        
        code = editor.toPlainText()
        if not code.strip():
            return
        
        # Simple syntax check
        try:
            compile(code, "<string>", "exec")
            self.console.append("✅ No syntax errors found.")
        except SyntaxError as e:
            self.console.append(f"❌ Syntax Error: Line {e.lineno}: {e.msg}")
        except Exception as e:
            self.console.append(f"❌ Error: {str(e)}")
    
    def _format_code(self):
        """Basic code formatting."""
        editor = self._active_editor()
        if not editor:
            return
        
        # Simple formatting: fix indentation
        code = editor.toPlainText()
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
                indent_level = max(0, indent_level - 1)
            elif stripped.startswith(('def ', 'class ')) and indent_level > 0:
                indent_level = 0
            
            # Add formatted line
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Increase indent after certain keywords
            if stripped.endswith(':'):
                indent_level += 1
        
        formatted_code = '\n'.join(formatted_lines)
        editor.setPlainText(formatted_code)
        self.console.append("✨ Code formatted.")
    
    def _toggle_comments(self):
        """Toggle line comments for selected lines."""
        editor = self._active_editor()
        if not editor:
            return
        
        cursor = editor.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # Select full lines
        cursor.setPosition(start)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        start_pos = cursor.position()
        
        cursor.setPosition(end)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        end_pos = cursor.position()
        
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        
        selected_text = cursor.selectedText()
        lines = selected_text.split('\u2029')  # Qt paragraph separator
        
        # Check if lines are already commented
        all_commented = all(line.strip().startswith('#') or not line.strip() for line in lines)
        
        modified_lines = []
        for line in lines:
            if all_commented:
                # Uncomment
                if line.strip().startswith('#'):
                    modified_lines.append(line.replace('#', '', 1).lstrip())
                else:
                    modified_lines.append(line)
            else:
                # Comment
                if line.strip():
                    modified_lines.append('# ' + line)
                else:
                    modified_lines.append(line)
        
        cursor.insertText('\n'.join(modified_lines))
    
    def _on_text_changed(self, editor):
        """Handle text changes for auto-linting and mark file as modified."""
        # Mark the file as modified if it has a file path
        file_path = editor.property("filePath")
        if file_path:
            # Find the tab for this editor
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i) == editor:
                    current_title = self.tabWidget.tabText(i)
                    # Add asterisk if not already present
                    if not current_title.endswith(" *"):
                        self.tabWidget.setTabText(i, current_title + " *")
                    break
                    
        # Mark editor as having unsaved changes
        editor.setProperty("isModified", True)
    
    def _language_changed(self, language):
        """Handle language change - update highlighter for active editor."""
        editor = self._active_editor()
        if not editor:
            return
            
        # Update the highlighter based on selected language
        if "MEL" in language:
            editor.highlighter = MELHighlighter(editor.document())
            icon = "📜"
        else:
            editor.highlighter = PythonHighlighter(editor.document())
            icon = "🐍"
            
        # Force re-highlight
        editor.highlighter.rehighlight()
        
        # Update tab title with new icon
        current_index = self.tabWidget.currentIndex()
        if current_index >= 0:
            current_title = self.tabWidget.tabText(current_index)
            # Remove old icon and add new one
            clean_title = current_title.replace("🐍 ", "").replace("📜 ", "")
            new_title = f"{icon} {clean_title}"
            self.tabWidget.setTabText(current_index, new_title)
        
        # Store the language in the editor for reference
        editor.setProperty("language", language)
        
        self.console.append(f"🔧 Language changed to: {language}")
        
    def _editor_search(self):
        """Show search in active editor (VS Code style)."""
        editor = self._active_editor()
        if editor and hasattr(editor, 'show_search'):
            editor.show_search()
    
    def _update_problems(self, problems):
        """Update the problems panel with linting results."""
        self.problemsList.clear()
        
        if not problems:
            # No problems - show success message
            item = QtWidgets.QListWidgetItem("✅ No problems found")
            item.setForeground(QtGui.QColor("#4caf50"))  # Green
            self.problemsList.addItem(item)
            return
        
        # Add problems to the list
        for problem in problems:
            # Create VS Code style problem entry
            severity_icon = "🔴" if problem.get('severity') == 'error' else "🟡"
            problem_text = f"{severity_icon} Line {problem['line']}: {problem['message']}"
            
            item = QtWidgets.QListWidgetItem(problem_text)
            
            # Color code by severity
            if problem.get('severity') == 'error':
                item.setForeground(QtGui.QColor("#f14c4c"))  # VS Code red
            else:
                item.setForeground(QtGui.QColor("#ff9800"))  # Orange for warnings
            
            # Store problem data for click handling
            item.setData(QtCore.Qt.UserRole, problem)
            
            self.problemsList.addItem(item)
        
        # Connect double-click to jump to error
        if not hasattr(self, '_problems_connected'):
            self.problemsList.itemDoubleClicked.connect(self._jump_to_problem)
            self._problems_connected = True
    
    def _jump_to_problem(self, item):
        """Jump to the line with the problem when double-clicked."""
        problem = item.data(QtCore.Qt.UserRole)
        if problem:
            editor = self._current_editor()
            if editor:
                # Move cursor to problem line
                cursor = editor.textCursor()
                cursor.movePosition(QtGui.QTextCursor.Start)
                for _ in range(problem['line'] - 1):
                    cursor.movePosition(QtGui.QTextCursor.Down)
                editor.setTextCursor(cursor)
                editor.setFocus()
    
    def _open_folder(self):
        """Open a folder in the explorer."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self._load_folder_in_explorer(folder)
    
    def _load_folder_in_explorer(self, folder_path):
        """Load folder contents in the explorer view."""
        import os
        if os.path.exists(folder_path):
            # Simple file system model for now
            file_model = QtWidgets.QFileSystemModel()
            file_model.setRootPath(folder_path)
            self.explorerView.setModel(file_model)
            self.explorerView.setRootIndex(file_model.index(folder_path))
            
            # Log to console if it exists
            if hasattr(self, 'console'):
                self.console.append(f"📁 Loaded folder: {folder_path}\n")
            else:
                print(f"[DEBUG] Loaded folder: {folder_path}")  # Fallback to print
    
    def _toggle_indentation_guides(self, checked):
        """Toggle indentation guides in the current editor."""
        editor = self._current_editor()
        if editor and hasattr(editor, 'set_indentation_guides_visible'):
            editor.set_indentation_guides_visible(checked)
            
        # Apply to all editors in tabs
        for i in range(self.tabWidget.count()):
            tab_editor = self.tabWidget.widget(i)
            if hasattr(tab_editor, 'set_indentation_guides_visible'):
                tab_editor.set_indentation_guides_visible(checked)
        
        status = "enabled" if checked else "disabled"
        self.console.append(f"🔲 Indentation guides {status}")

    # ==========================================================
    # Debug Menu Actions
    # ==========================================================
    
    def _start_debugging(self):
        """Start debugging the current file."""
        current_editor = self._current_editor()
        if current_editor and hasattr(current_editor, 'language') and current_editor.language == 'python':
            filename = getattr(current_editor, 'filename', None) or 'untitled.py'
            code = current_editor.toPlainText()
            self.debug_session.start_debug(filename, code)
            self.console.append("🐛 Debug session started")
        else:
            self.console.append("⚠️ Debugging is only available for Python files")
    
    def _stop_debugging(self):
        """Stop the current debug session."""
        if self.debug_session.is_debugging:
            self.debug_session.stop_debug()
            self.console.append("🛑 Debug session stopped")
    
    def _toggle_breakpoint(self):
        """Toggle breakpoint at current line."""
        current_editor = self._current_editor()
        if current_editor and hasattr(current_editor, 'toggle_breakpoint'):
            line_number = current_editor.textCursor().blockNumber() + 1
            current_editor.toggle_breakpoint()
            self.console.append(f"🔴 Breakpoint toggled at line {line_number}")
    
    def _clear_all_breakpoints(self):
        """Clear all breakpoints in current editor."""
        current_editor = self._current_editor()
        if current_editor and hasattr(current_editor, 'clear_all_breakpoints'):
            current_editor.clear_all_breakpoints()
            self.console.append("🧹 All breakpoints cleared")
    
    def _debug_step_over(self):
        """Step over current line."""
        if self.debug_session.is_debugging:
            self.debug_session.step_over()
            self.console.append("👣 Step over")
    
    def _debug_step_into(self):
        """Step into function call."""
        if self.debug_session.is_debugging:
            self.debug_session.step_into()
            self.console.append("👣 Step into")
    
    def _debug_step_out(self):
        """Step out of current function."""
        if self.debug_session.is_debugging:
            self.debug_session.step_out()
            self.console.append("👣 Step out")
    
    def _debug_continue(self):
        """Continue execution until next breakpoint."""
        if self.debug_session.is_debugging:
            self.debug_session.continue_execution()
            self.console.append("▶️ Continue execution")

    # ==========================================================
    # Debug Event Handlers
    # ==========================================================
    
    def _on_debug_started(self):
        """Handle debug session start."""
        self.console.append("🐛 Debug session started")
        
    def _on_debug_stopped(self):
        """Handle debug session stop."""
        self.console.append("🛑 Debug session stopped")
        # Clear debug line indicators in all editors
        for i in range(self.tabWidget.count()):
            editor = self.tabWidget.widget(i)
            if hasattr(editor, 'clear_debug_line'):
                editor.clear_debug_line()
    
    def _on_debug_paused(self, line_number):
        """Handle debug pause at a specific line."""
        current_editor = self._current_editor()
        if current_editor and hasattr(current_editor, 'set_current_debug_line'):
            current_editor.set_current_debug_line(line_number)
        self.console.append(f"⏸️ Debug paused at line {line_number}")
    
    def _show_about(self):
        """Show About dialog."""
        about_text = """
<h2>NEO Script Editor v2.0</h2>
<p><b>AI-Powered Maya Scripting Assistant</b></p>
<p>Created by: <b>Majy Amilano</b></p>
<p>Powered by: <b>Morpheus AI</b></p>
<br>
<p><b>Features:</b></p>
<ul>
<li>🤖 AI-assisted code generation with Morpheus</li>
<li>🎯 Real-time syntax error detection and highlighting</li>
<li>💡 Intelligent code completion and suggestions</li>
<li>🔍 Advanced search and replace functionality</li>
<li>📊 Problems panel with error navigation</li>
<li>🎨 VS Code-style interface and shortcuts</li>
<li>⚡ Maya-specific command integration</li>
</ul>
<br>
<p><i>Enhancing Maya scripting with the power of AI</i></p>
"""
        
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle("About NEO Script Editor")
        msgBox.setTextFormat(QtCore.Qt.RichText)
        msgBox.setText(about_text)
        msgBox.setIconPixmap(QtGui.QPixmap())  # You can add an icon here
        msgBox.exec()
    
    def _navigate_chat_history_prev(self):
        """Navigate to previous chat in history."""
        if hasattr(self, 'morpheus_manager'):
            prev_chat = self.morpheus_manager.get_previous_chat()
            if prev_chat:
                self._load_chat_from_history(prev_chat)
                self._update_history_info()
    
    def _navigate_chat_history_next(self):
        """Navigate to next chat in history."""
        if hasattr(self, 'morpheus_manager'):
            next_chat = self.morpheus_manager.get_next_chat()
            if next_chat:
                self._load_chat_from_history(next_chat)
                self._update_history_info()
    
    def _clear_chat_history(self):
        """Clear all chat history."""
        reply = QtWidgets.QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear all chat history?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            if hasattr(self, 'morpheus_manager'):
                self.morpheus_manager.clear_session_history()
            if hasattr(self, 'morpheus'):
                self.morpheus.clear_chat()
            self._update_history_info()
    
    def _load_chat_from_history(self, chat_data):
        """Load a specific chat from history."""
        if hasattr(self, 'chatDisplay') and hasattr(self, 'chatInput'):
            # Clear current display
            self.chatDisplay.clear()
            
            # Load the historical conversation
            user_msg = chat_data.get('user', '')
            ai_reply = chat_data.get('ai', '')
            
            # Set input to the historical user message
            self.chatInput.setText(user_msg)
            
            # Display the conversation
            if hasattr(self, 'morpheus'):
                # Display user message
                user_html = f'''
<div style="margin:12px 0; padding:15px; background:rgba(33, 150, 243, 0.1); border-radius:8px; border-left:3px solid #2196f3; clear:both; border: 1px solid rgba(33, 150, 243, 0.2);">
    <div style="color:#1565c0; font-size:12px; font-weight:600; margin-bottom:8px; display:flex; align-items:center;">
        <span style="background:#2196f3; color:white; padding:3px 8px; border-radius:4px; margin-right:8px; font-size:10px;">👤 YOU</span>
        <span style="color:#888; font-size:10px;">(From History)</span>
    </div>
    <div style="color:#2c2c2c; font-size:14px; line-height:1.5; font-weight:500;">
        {html.escape(user_msg)}
    </div>
</div>
<div style="height:16px;"></div>
'''
                self.chatDisplay.insertHtml(user_html)
                
                # Display AI response
                self.morpheus._display_response(ai_reply)
    
    def _update_history_info(self):
        """Update the history information display."""
        if hasattr(self, 'morpheus_manager') and hasattr(self, 'historyInfoLabel'):
            info = self.morpheus_manager.get_chat_history_summary()
            self.historyInfoLabel.setText(info)
            
            # Update button states
            if hasattr(self, 'prevChatBtn'):
                self.prevChatBtn.setEnabled(self.morpheus_manager.current_chat_index > 0)
            if hasattr(self, 'nextChatBtn'):
                self.nextChatBtn.setEnabled(
                    self.morpheus_manager.current_chat_index < len(self.morpheus_manager.chat_history) - 1
                )

    # =========================================================
    # Misc Helpers
    # =========================================================
    
    def _set_api_key_dialog(self):
        """Prompt user to input or update the OpenAI API key."""
        dlg = QtWidgets.QInputDialog(self)
        dlg.setWindowTitle("Set OpenAI API Key")
        dlg.setLabelText("Enter your OpenAI API key (starts with 'sk-...'):")
        dlg.resize(480, 100)
        dlg.setTextEchoMode(QtWidgets.QLineEdit.Password)

        if dlg.exec_():
            key = dlg.textValue().strip()
            if not key:
                self.console.append("⚠️ No key entered.\n")
                return

            # Ask whether to save permanently
            persist = (
                QtWidgets.QMessageBox.question(
                    self,
                    "Save API Key?",
                    "Do you want to save this API key for future sessions?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                ) == QtWidgets.QMessageBox.Yes
            )

            self._set_api_key(key, persist)
            self.console.append("🔑 API key applied successfully.\n")

    
    def _set_api_key(self, key: str, persist: bool = False):
        """Apply or update OpenAI API key, with optional persistence."""
        if not key:
            return

        import os
        os.environ["OPENAI_API_KEY"] = key

        # --- Save or remove from QSettings ---
        try:
            settings = QtCore.QSettings("AI_Script_Editor", "settings")
            if persist:
                settings.setValue("OPENAI_API_KEY", key)
                self.console.append("🔒 API key saved for future sessions.\n")
            else:
                settings.remove("OPENAI_API_KEY")
                self.console.append("🔑 API key applied for current session only.\n")
        except Exception as e:
            print(f"[QSettings error] {e}")

        # --- Rebuild or reconnect OpenAI client immediately ---
        try:
            if hasattr(self, "morpheus") and self.morpheus:
                # Preferred method (if using new chat.py)
                if hasattr(self.morpheus, "reconnect"):
                    ok = self.morpheus.reconnect()
                else:
                    # Fallback to old logic
                    self.morpheus.client = self.morpheus._make_client()
                    ok = bool(self.morpheus.client)

                if ok:
                    self.console.append("✅ OpenAI client reinitialized successfully.\n")
                else:
                    self.console.append("⚠️ Failed to initialize OpenAI client.\n")
        except Exception as e:
            self.console.append(f"❌ Copilot reconnection error: {e}\n")
    
    def _current_editor(self):
        """Get the currently active code editor."""
        current_widget = self.tabWidget.currentWidget()
        if hasattr(current_widget, 'codeEditor'):
            return current_widget.codeEditor
        elif isinstance(current_widget, CodeEditor):
            return current_widget
        return None
    
    def _check_syntax_errors(self):
        """Check current editor for syntax errors and highlight them."""
        editor = self._current_editor()
        if editor and hasattr(editor, 'check_syntax_errors'):
            errors = editor.check_syntax_errors(emit_signal=True)
            if not errors:
                QtWidgets.QMessageBox.information(self, "Syntax Check", "✅ No syntax errors found!")
            else:
                error_count = len(errors)
                error_msg = f"❌ Found {error_count} syntax error{'s' if error_count > 1 else ''}:\n\n"
                for err in errors[:3]:  # Show first 3 errors
                    error_msg += f"Line {err['line']}: {err['message']}\n"
                if error_count > 3:
                    error_msg += f"...and {error_count - 3} more errors"
                QtWidgets.QMessageBox.warning(self, "Syntax Errors", error_msg)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No active editor found.")
    
    def _clear_error_highlights(self):
        """Clear all error highlights in current editor."""
        editor = self._current_editor()
        if editor and hasattr(editor, 'clear_error_highlights'):
            editor.clear_error_highlights()
            # Also clear problems panel
            self.problemsList.clear()
            item = QtWidgets.QListWidgetItem("✨ Error highlights cleared")
            item.setForeground(QtGui.QColor("#4caf50"))
            self.problemsList.addItem(item)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No active editor found.")


    def _on_explorer_double_clicked(self, index):
        """Handle double-click on files in the explorer to open them in new tabs."""
        if not index.isValid():
            return
            
        # Get the file system model and file info
        model = self.explorerView.model()
        if not isinstance(model, QtWidgets.QFileSystemModel):
            return
            
        file_info = model.fileInfo(index)
        
        # Only open files, not directories
        if file_info.isDir():
            return
            
        file_path = file_info.absoluteFilePath()
        file_name = file_info.fileName()
        
        # Check if it's a supported file type
        supported_extensions = ['.py', '.mel', '.txt', '.json', '.yaml', '.yml', '.md']
        if not any(file_path.lower().endswith(ext) for ext in supported_extensions):
            self.console.append(f"⚠️ Unsupported file type: {file_name}")
            return
        
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Auto-detect language based on file extension
            if file_path.lower().endswith('.mel'):
                # Set language combo to MEL before creating tab
                if hasattr(self, 'languageCombo'):
                    self.languageCombo.setCurrentText("MEL")
            elif file_path.lower().endswith('.py'):
                # Set language combo to Python before creating tab
                if hasattr(self, 'languageCombo'):
                    self.languageCombo.setCurrentText("Python")
            
            # Check if file is already open in a tab
            existing_tab_index = self._find_tab_by_file_path(file_path)
            if existing_tab_index >= 0:
                # File already open, just switch to that tab
                self.tabWidget.setCurrentIndex(existing_tab_index)
                self.console.append(f"📂 Switched to already open file: {file_name}")
                return
            
            # Create new tab with file content
            editor = self.new_tab(file_name, content)
            
            # Store the file path for saving
            editor.setProperty("filePath", file_path)
            
            # Log success
            self.console.append(f"📂 Opened: {file_name}")
            
            # Focus the editor
            editor.setFocus()
            
        except Exception as e:
            self.console.append(f"❌ Error opening {file_name}: {str(e)}")
            print(f"Error opening file {file_path}: {str(e)}")  # Debug output
    
    def _find_tab_by_file_path(self, file_path):
        """Find if a file is already open in a tab. Returns tab index or -1 if not found."""
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if isinstance(widget, CodeEditor):
                existing_path = widget.property("filePath")
                if existing_path and os.path.normpath(existing_path) == os.path.normpath(file_path):
                    return i
        return -1
    
    def _get_tab_title_for_file(self, filename, language=None):
        """Generate appropriate tab title based on file and language."""
        if not language:
            if filename.lower().endswith('.mel'):
                return f"📜 {filename}"
            else:
                return f"🐍 {filename}"
        elif "MEL" in language:
            return f"📜 {filename}"
        else:
            return f"🐍 {filename}"
    
    def _update_tab_title_for_editor(self, editor, remove_modification_indicator=False):
        """Update the tab title for a specific editor."""
        for i in range(self.tabWidget.count()):
            if self.tabWidget.widget(i) == editor:
                current_title = self.tabWidget.tabText(i)
                
                if remove_modification_indicator and current_title.endswith(" *"):
                    # Remove the modification indicator
                    new_title = current_title[:-2]  # Remove " *"
                    self.tabWidget.setTabText(i, new_title)
                break

    # ==========================================================
    # Debug Event Handlers
    # ==========================================================
    
    def _on_debug_started(self):
        """Handle debug session start."""
        self.console.append("🐛 Debug session started")
        
    def _on_debug_stopped(self):
        """Handle debug session stop."""
        self.console.append("🛑 Debug session stopped")
        # Clear debug line indicators from all editors
        for i in range(self.tabWidget.count()):
            editor = self.tabWidget.widget(i)
            if hasattr(editor, 'clear_debug_line'):
                editor.clear_debug_line()
                
    def _on_debug_paused(self, line_number):
        """Handle debug session pause at specific line."""
        self.console.append(f"⏸️ Debug paused at line {line_number}")
        current_editor = self._current_editor()
        if current_editor and hasattr(current_editor, 'set_current_debug_line'):
            current_editor.set_current_debug_line(line_number)
