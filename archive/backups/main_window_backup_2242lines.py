# AI Script Editor - Complete Modular Version
# All functionality from bloated version but organized into modules
import os, difflib, html
from functools import partial
from PySide6 import QtWidgets, QtCore, QtGui

# --- Ensure OpenAI key is loaded before Morpheus init ---
settings = QtCore.QSettings("AI_Script_Editor", "settings")
stored_key = settings.value("OPENAI_API_KEY", "")
if stored_key:
    os.environ["OPENAI_API_KEY"] = stored_key
    print("[OpenAI] API key injected successfully before Morpheus init.")
else:
    print("[!] No stored OpenAI key found. Set one via Settings -> API Key.")

# Internal imports - exact from bloated version  
try:
    from editor.code_editor import CodeEditor
    from editor.highlighter import PythonHighlighter, MELHighlighter
    from model.hierarchy import CodeHierarchyModel
    from ui.output_console import OutputConsole
    from ai.chat import AIMorpheus
    from ai.copilot_manager import MorpheusManager
    print("[OK] All core components imported successfully")
except ImportError as e:
    print(f"[!] Import warning: {e} (using fallbacks)")

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
    """Complete AI Script Editor - All functionality from bloated version but modular"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 NEO Script Editor v2.2 - Complete Modular")
        self.resize(1200, 700)
        self.setStyleSheet(DARK_STYLE)

        # Initialize thinking animation timer (exact from bloated version)
        self.thinkingTimer = QtCore.QTimer()
        self.thinkingTimer.timeout.connect(self._animate_thinking)
        self.thinkingDots = 0

        # Initialize code blocks storage for action buttons
        self._code_blocks = {}
        self._code_block_html = {}
        
        # Track if model selector signal is connected
        self._model_selector_connected = False

        # Initialize components exactly as in bloated version
        self._setup_central_widget()
        self._setup_floating_code_actions()
        self._setup_dock_widgets()
        self._setup_menu_system()
        self._setup_toolbar()
        self._setup_connections()
        self._init_hierarchy()
        
        print("[OK] AI Script Editor initialized with all bloated features!")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts - Esc to close find/replace"""
        if event.key() == QtCore.Qt.Key_Escape:
            if hasattr(self, 'findReplaceWidget') and self.findReplaceWidget.isVisible():
                self._hide_find_replace()
                event.accept()
                return
        super().keyPressEvent(event)
    
    def _setup_central_widget(self):
        """Setup central tabbed editor - exact from bloated version"""
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
        self.languageCombo.addItem("� MEL", "MEL") 
        self.languageCombo.setCurrentIndex(0)  # Default to Python
        self.languageCombo.setToolTip("Select script language")
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
        
        # VS Code-style Find/Replace widget (hidden by default)
        self._setup_find_replace_widget(centralLayout)
        
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        centralLayout.addWidget(self.tabWidget)
        
        self.setCentralWidget(centralWidget)
    
    def _setup_find_replace_widget(self, parent_layout):
        """Setup VS Code-style find/replace widget"""
        # Container for find/replace widget
        self.findReplaceWidget = QtWidgets.QWidget()
        self.findReplaceWidget.setStyleSheet("""
            QWidget {
                background: #2d2d30;
                border-bottom: 1px solid #3e3e42;
            }
            QLineEdit {
                background: #3c3c3c;
                border: 1px solid #3e3e42;
                color: #cccccc;
                padding: 4px 8px;
                border-radius: 2px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background: #0e639c;
                color: #ffffff;
                border: 1px solid #007acc;
                padding: 4px 12px;
                border-radius: 2px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #1177bb;
            }
            QPushButton:pressed {
                background: #0d5a8f;
            }
            QCheckBox {
                color: #cccccc;
                font-size: 11px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3e3e42;
                border-radius: 2px;
                background: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background: #007acc;
                border-color: #007acc;
            }
        """)
        
        mainLayout = QtWidgets.QVBoxLayout(self.findReplaceWidget)
        mainLayout.setContentsMargins(8, 6, 8, 6)
        mainLayout.setSpacing(4)
        
        # Find row
        findLayout = QtWidgets.QHBoxLayout()
        findLayout.setSpacing(6)
        
        # Toggle replace button (VS Code style)
        self.toggleReplaceBtn = QtWidgets.QPushButton("▶")
        self.toggleReplaceBtn.setFixedSize(20, 20)
        self.toggleReplaceBtn.setToolTip("Toggle Replace")
        self.toggleReplaceBtn.clicked.connect(self._toggle_replace_mode)
        self.toggleReplaceBtn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #cccccc;
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #3e3e42;
            }
        """)
        findLayout.addWidget(self.toggleReplaceBtn)
        
        findLabel = QtWidgets.QLabel("🔍")
        findLabel.setFixedWidth(20)
        findLayout.addWidget(findLabel)
        
        self.findInput = QtWidgets.QLineEdit()
        self.findInput.setPlaceholderText("Find")
        self.findInput.setMinimumWidth(250)
        self.findInput.returnPressed.connect(self._find_next)
        self.findInput.textChanged.connect(self._on_find_text_changed)  # Real-time highlight
        findLayout.addWidget(self.findInput)
        
        self.findPrevBtn = QtWidgets.QPushButton("⬆")
        self.findPrevBtn.setFixedSize(28, 26)
        self.findPrevBtn.setToolTip("Previous Match (Shift+F3)")
        self.findPrevBtn.clicked.connect(self._find_previous)
        findLayout.addWidget(self.findPrevBtn)
        
        self.findNextBtn = QtWidgets.QPushButton("⬇")
        self.findNextBtn.setFixedSize(28, 26)
        self.findNextBtn.setToolTip("Next Match (F3)")
        self.findNextBtn.clicked.connect(self._find_next)
        findLayout.addWidget(self.findNextBtn)
        
        self.matchCaseCheck = QtWidgets.QCheckBox("Aa")
        self.matchCaseCheck.setToolTip("Match Case")
        findLayout.addWidget(self.matchCaseCheck)
        
        self.wholeWordCheck = QtWidgets.QCheckBox("Ab|")
        self.wholeWordCheck.setToolTip("Match Whole Word")
        findLayout.addWidget(self.wholeWordCheck)
        
        self.regexCheck = QtWidgets.QCheckBox(".*")
        self.regexCheck.setToolTip("Use Regular Expression")
        findLayout.addWidget(self.regexCheck)
        
        self.findMatchLabel = QtWidgets.QLabel("")
        self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        findLayout.addWidget(self.findMatchLabel)
        
        findLayout.addStretch()
        
        closeBtn = QtWidgets.QPushButton("✕")
        closeBtn.setFixedSize(32, 32)
        closeBtn.setToolTip("Close (Esc)")
        closeBtn.clicked.connect(self._hide_find_replace)
        closeBtn.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                border: 1px solid #3e3e42;
                color: #cccccc;
                font-size: 20px;
                font-weight: bold;
                border-radius: 2px;
            }
            QPushButton:hover {
                background: #f48771;
                color: #ffffff;
                border-color: #f48771;
            }
            QPushButton:pressed {
                background: #d16957;
            }
        """)
        findLayout.addWidget(closeBtn)
        
        mainLayout.addLayout(findLayout)
        
        # Replace row (initially hidden)
        self.replaceRow = QtWidgets.QWidget()
        replaceLayout = QtWidgets.QHBoxLayout(self.replaceRow)
        replaceLayout.setContentsMargins(0, 0, 0, 0)
        replaceLayout.setSpacing(6)
        
        # Spacer to align with find input
        spacer = QtWidgets.QLabel("")
        spacer.setFixedWidth(20)
        replaceLayout.addWidget(spacer)
        
        replaceLabel = QtWidgets.QLabel("🔄")
        replaceLabel.setFixedWidth(20)
        replaceLayout.addWidget(replaceLabel)
        
        self.replaceInput = QtWidgets.QLineEdit()
        self.replaceInput.setPlaceholderText("Replace")
        self.replaceInput.setMinimumWidth(250)
        replaceLayout.addWidget(self.replaceInput)
        
        self.replaceBtn = QtWidgets.QPushButton("Replace")
        self.replaceBtn.setFixedHeight(26)
        self.replaceBtn.clicked.connect(self._replace_current)
        replaceLayout.addWidget(self.replaceBtn)
        
        self.replaceAllBtn = QtWidgets.QPushButton("Replace All")
        self.replaceAllBtn.setFixedHeight(26)
        self.replaceAllBtn.clicked.connect(self._replace_all)
        replaceLayout.addWidget(self.replaceAllBtn)
        
        replaceLayout.addStretch()
        
        mainLayout.addWidget(self.replaceRow)
        self.replaceRow.hide()
        
        parent_layout.addWidget(self.findReplaceWidget)
        self.findReplaceWidget.hide()

    def _setup_floating_code_actions(self):
        """Setup floating code actions - exact from bloated version"""
        self.floating_actions = QtWidgets.QWidget(self)
        self.floating_actions.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.floating_actions.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.floating_actions.setStyleSheet("""
            QWidget {
                background: rgba(45, 45, 48, 220);
                border-radius: 8px;
                border: 1px solid #58a6ff;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(self.floating_actions)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        ai_btn = QtWidgets.QPushButton("🧠 AI Suggest")
        ai_btn.setStyleSheet("""
            QPushButton {
                background: #21262d;
                color: #58a6ff;
                border: 1px solid #30363d;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover { background: #30363d; }
        """)
        layout.addWidget(ai_btn)
        
        fix_btn = QtWidgets.QPushButton("🔧 Quick Fix")
        fix_btn.setStyleSheet(ai_btn.styleSheet())
        layout.addWidget(fix_btn)
        
        self.floating_actions.resize(180, 32)
        self.floating_actions.hide()
        
    def _setup_dock_widgets(self):
        """Setup dock widgets - exact from bloated version"""
        self._build_console_dock()
        self._build_problems_dock()
        self._build_explorer_dock()
        self._build_chat_dock()
    
    def _build_console_dock(self):
        """Build output console dock - exact from bloated version"""
        try:
            self.console = OutputConsole()
            self.console.enable_output_capture()
            self.console.append_tagged("INFO", "🌟 NEO Script Editor Console - Enhanced with PySide6/Qt Intelligence!", "#58a6ff")
            self.console.append_tagged("SUCCESS", "[OK] Advanced syntax highlighting with complete PySide6/Qt support enabled", "#28a745")
            self.console.append_tagged("SUCCESS", "[OK] Real-time error detection with VSCode-style problem indicators active", "#28a745")
        except:
            self.console = QtWidgets.QTextEdit()
            self.console.setPlainText("Console ready (fallback mode)")
            
        console_dock = QtWidgets.QDockWidget("Output Console", self)
        console_dock.setObjectName("ConsoleDock")
        console_dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        console_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        console_dock.setWidget(self.console)
        console_dock.visibilityChanged.connect(lambda visible: self._sync_console_action(visible))
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, console_dock)
        self.console_dock = console_dock
        
    def _build_problems_dock(self):
        """Build problems dock - exact from bloated version"""
        self.problemsList = QtWidgets.QTreeWidget()
        self.problemsList.setHeaderLabels(["Type", "Message", "Line", "File"])
        self.problemsList.setRootIsDecorated(False)
        self.problemsList.setAlternatingRowColors(True)
        self.problemsList.setStyleSheet("""
            QTreeWidget {
                background: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                selection-background-color: #264f78;
            }
            QHeaderView::section {
                background: #2d2d30;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #3e3e42;
            }
        """)
        
        problems_dock = QtWidgets.QDockWidget("Problems", self)
        problems_dock.setObjectName("ProblemsDock")
        problems_dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        problems_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        problems_dock.setWidget(self.problemsList)
        problems_dock.visibilityChanged.connect(lambda visible: self._sync_problems_action(visible))
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, problems_dock)
        self.problems_dock = problems_dock
        
    def _build_explorer_dock(self):
        """Build file explorer dock - exact from bloated version"""
        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setRootPath("")
        
        self.explorerView = QtWidgets.QTreeView()
        self.explorerView.setModel(self.fileModel)
        self.explorerView.setRootIndex(self.fileModel.index(os.getcwd()))
        
        self.explorerView.hideColumn(1)  # Size
        self.explorerView.hideColumn(2)  # Type  
        self.explorerView.hideColumn(3)  # Date Modified
        
        explorer_dock = QtWidgets.QDockWidget("Explorer", self)
        explorer_dock.setObjectName("ExplorerDock")
        explorer_dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        explorer_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        explorer_dock.setWidget(self.explorerView)
        explorer_dock.visibilityChanged.connect(lambda visible: self._sync_explorer_action(visible))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, explorer_dock)
        self.explorer_dock = explorer_dock
        
    def _build_chat_dock(self):
        """Build Morpheus AI chat dock - exact from bloated version"""
        chatDock = QtWidgets.QDockWidget("[AI] Morpheus AI", self)
        chatDock.setObjectName("MorpheusDock")
        chatDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)  # Allow docking anywhere!
        chatDock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )

        # Create chat widget container
        chatWidget = QtWidgets.QWidget(chatDock)
        chatLayout = QtWidgets.QVBoxLayout(chatWidget)
        chatLayout.setContentsMargins(6, 6, 6, 6)
        chatLayout.setSpacing(6)

        # Chat history navigation (at top)
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

        # Chat history display (renamed to match bloated version)
        self.chatHistory = QtWidgets.QTextBrowser()
        self.chatHistory.setOpenExternalLinks(False)
        self.chatHistory.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
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
                color: #f0f6fc;
            }
        """)
        chatLayout.addWidget(self.chatHistory, 1)

        # Response indicator (thinking...)
        self.responseIndicator = QtWidgets.QLabel()
        self.responseIndicator.setText("🤖 Morpheus is thinking...")
        self.responseIndicator.setStyleSheet("""
            QLabel {
                color: #7c3aed;
                font-family: "Segoe UI", Consolas, monospace;
                font-size: 12px;
                padding: 4px 8px;
                background: rgba(124, 58, 237, 0.1);
                border: 1px solid rgba(124, 58, 237, 0.2);
                border-radius: 4px;
            }
        """)
        self.responseIndicator.setVisible(False)
        chatLayout.addWidget(self.responseIndicator)

        # Input area
        inputWidget = QtWidgets.QWidget()
        inputLayout = QtWidgets.QVBoxLayout(inputWidget)
        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.setSpacing(4)

        # Provider selector (NEW!)
        provider_layout = QtWidgets.QHBoxLayout()
        provider_layout.setSpacing(8)
        
        provider_label = QtWidgets.QLabel("AI Provider:")
        provider_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        self.provider_selector = QtWidgets.QComboBox()
        self.provider_selector.addItems(["GPT-4o (OpenAI)", "Claude Sonnet (Anthropic)"])
        self.provider_selector.setStyleSheet("""
            QComboBox {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 4px 8px;
                color: #f0f6fc;
                font-size: 11px;
            }
            QComboBox:hover {
                border-color: #58a6ff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b949e;
            }
        """)
        
        # Model selector (NEW!)
        model_label = QtWidgets.QLabel("Model:")
        model_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        self.model_selector = QtWidgets.QComboBox()
        self.model_selector.setStyleSheet("""
            QComboBox {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 4px 8px;
                color: #f0f6fc;
                font-size: 11px;
            }
            QComboBox:hover {
                border-color: #58a6ff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b949e;
            }
        """)
        
        # Load saved provider preference
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        self.provider_selector.setCurrentText("Claude Sonnet (Anthropic)" if current_provider == "claude" else "GPT-4o (OpenAI)")
        
        # Connect to update provider and model list on change
        self.provider_selector.currentTextChanged.connect(self._on_provider_changed)
        
        # Initialize model list based on current provider
        self._update_model_list()
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_selector, 1)
        provider_layout.addWidget(model_label)
        provider_layout.addWidget(self.model_selector, 1)
        
        inputLayout.addLayout(provider_layout)

        # Text input
        self.chatInput = QtWidgets.QTextEdit()
        self.chatInput.setMaximumHeight(60)
        self.chatInput.setPlaceholderText("Ask Morpheus anything about your code...")
        self.chatInput.setStyleSheet("""
            QTextEdit {
                background: #21262d;
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
        
        # Connect Enter key to send message
        self.chatInput.keyPressEvent = self._chat_key_press_event
        
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
        """)
        self.sendBtn.clicked.connect(self._send_message)

        inputLayout.addWidget(self.chatInput)
        inputLayout.addWidget(self.sendBtn)
        chatLayout.addWidget(inputWidget)

        chatDock.setWidget(chatWidget)
        chatDock.visibilityChanged.connect(lambda visible: self._sync_morpheus_action(visible))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, chatDock)
        self.chat_dock = chatDock

        # Initialize Morpheus AI system (exact from bloated version)
        try:
            # First initialize AIMorpheus for OpenAI client
            self.morpheus = AIMorpheus(self)
            
            # Then initialize MorpheusManager for orchestration
            from ai.copilot_manager import MorpheusManager
            self.morpheus_manager = MorpheusManager(self)
            self.morpheus_manager.contextUpdated.connect(lambda msg:
                                                       self.console.append(f"[AI] Context updated: {msg[:50]}..."))
            self.morpheus_manager.historyUpdated.connect(self._on_history_updated)
            self.morpheus_manager.responseReady.connect(self._on_morpheus_response)
            
            if self.morpheus.client:
                self.chatHistory.append("[AI] <b>Morpheus AI</b> is ready! Ask me anything about your code.<br><br>")
            else:
                self.chatHistory.append("[!] <b>Morpheus AI</b> - No OpenAI API key found. Set your API key in Settings.<br><br>")
        except Exception as e:
            print(f"Morpheus AI initialization failed: {e}")
            self.chatHistory.append(f"[X] <b>Morpheus AI initialization failed:</b> {e}<br><br>")
            self.morpheus = None
            self.morpheus_manager = None

    def _setup_menu_system(self):
        """Setup complete menu system - exact from bloated version"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QtGui.QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QtGui.QAction("&Open", self)
        open_action.setShortcut("Ctrl+O") 
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QtGui.QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QtGui.QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QtGui.QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QtGui.QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QtGui.QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QtGui.QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QtGui.QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QtGui.QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QtGui.QAction("🔍 &Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self._show_find)
        edit_menu.addAction(find_action)
        
        replace_action = QtGui.QAction("🔄 &Replace", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self._show_replace)
        edit_menu.addAction(replace_action)
        
        find_next_action = QtGui.QAction("Find &Next", self)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(self._find_next)
        edit_menu.addAction(find_next_action)
        
        find_prev_action = QtGui.QAction("Find &Previous", self)
        find_prev_action.setShortcut("Shift+F3")
        find_prev_action.triggered.connect(self._find_previous)
        edit_menu.addAction(find_prev_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        # Add dock panel visibility toggles
        self.toggle_explorer_action = QtGui.QAction("📁 Explorer", self)
        self.toggle_explorer_action.setCheckable(True)
        self.toggle_explorer_action.setChecked(True)
        self.toggle_explorer_action.setShortcut("Ctrl+Shift+E")
        self.toggle_explorer_action.triggered.connect(lambda: self._toggle_dock("ExplorerDock"))
        view_menu.addAction(self.toggle_explorer_action)
        
        self.toggle_morpheus_action = QtGui.QAction("🤖 Morpheus AI Chat", self)
        self.toggle_morpheus_action.setCheckable(True)
        self.toggle_morpheus_action.setChecked(True)
        self.toggle_morpheus_action.setShortcut("Ctrl+Shift+M")
        self.toggle_morpheus_action.triggered.connect(lambda: self._toggle_dock("MorpheusDock"))
        view_menu.addAction(self.toggle_morpheus_action)
        
        self.toggle_console_action = QtGui.QAction("📟 Output Console", self)
        self.toggle_console_action.setCheckable(True)
        self.toggle_console_action.setChecked(True)
        self.toggle_console_action.setShortcut("Ctrl+Shift+C")
        self.toggle_console_action.triggered.connect(lambda: self._toggle_dock("ConsoleDock"))
        view_menu.addAction(self.toggle_console_action)
        
        self.toggle_problems_action = QtGui.QAction("⚠️ Problems", self)
        self.toggle_problems_action.setCheckable(True)
        self.toggle_problems_action.setChecked(True)
        self.toggle_problems_action.setShortcut("Ctrl+Shift+U")
        self.toggle_problems_action.triggered.connect(lambda: self._toggle_dock("ProblemsDock"))
        view_menu.addAction(self.toggle_problems_action)
        
        view_menu.addSeparator()
        
        # Add "Hide All Panels" and "Show All Panels" options
        hide_all_action = QtGui.QAction("🙈 Hide All Panels", self)
        hide_all_action.setShortcut("Ctrl+Shift+H")
        hide_all_action.triggered.connect(self._hide_all_panels)
        view_menu.addAction(hide_all_action)
        
        show_all_action = QtGui.QAction("👁️ Show All Panels", self)
        show_all_action.setShortcut("Ctrl+Shift+A")  # Changed from Ctrl+Shift+S (conflicts with Save As)
        show_all_action.triggered.connect(self._show_all_panels)
        view_menu.addAction(show_all_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings menu item
        settings_action = QtGui.QAction("⚙️ &Settings", self)
        settings_action.triggered.connect(self._show_settings_dialog)
        tools_menu.addAction(settings_action)
        
        tools_menu.addSeparator()
        
        syntax_check_action = QtGui.QAction("&Syntax Check", self)
        syntax_check_action.setShortcut("F7")
        syntax_check_action.triggered.connect(self._syntax_check)
        tools_menu.addAction(syntax_check_action)
        
        run_script_action = QtGui.QAction("&Run Script", self)
        run_script_action.setShortcut("F5")
        run_script_action.triggered.connect(self._run_script)
        tools_menu.addAction(run_script_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QtGui.QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Setup complete toolbar - exact from bloated version"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        toolbar.addAction(self._create_action("📄", "New File (Ctrl+N)", self._new_file))
        toolbar.addAction(self._create_action("📁", "Open File (Ctrl+O)", self._open_file))
        toolbar.addAction(self._create_action("💾", "Save File (Ctrl+S)", self._save_file))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("↶", "Undo (Ctrl+Z)", self._undo))
        toolbar.addAction(self._create_action("↷", "Redo (Ctrl+Y)", self._redo))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("[AI]", "Morpheus AI Chat (Ctrl+M)", self._show_morpheus_chat))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("🔍", "Syntax Check (F7)", self._syntax_check))
        toolbar.addAction(self._create_action("▶️", "Run Script (F5)", self._run_script))
        
    def _create_action(self, icon_text, tooltip, slot):
        """Helper to create toolbar actions"""
        action = QtGui.QAction(icon_text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(slot)
        return action

    def _setup_connections(self):
        """Setup all connections - exact from bloated version"""
        self.languageCombo.currentTextChanged.connect(self._language_changed)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.tabWidget.currentChanged.connect(self._on_tab_changed)
        self.explorerView.doubleClicked.connect(self._on_explorer_double_clicked)
        self.problemsList.itemDoubleClicked.connect(self._on_problem_double_clicked)
        
        # Create initial tab
        self._new_file()
        
    def _init_hierarchy(self):
        """Initialize hierarchy model - exact from bloated version"""
        try:
            self.hierarchy_model = CodeHierarchyModel()
            # Note: MorpheusManager is initialized in _build_chat_dock, don't duplicate here
        except Exception as e:
            print(f"Hierarchy initialization warning: {e}")
        except:
            print("Using fallback mode")
    
    def _setup_ui(self):
        """Setup UI components."""
        # Central widget
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Language selector
        lang_widget = QtWidgets.QWidget()
        lang_layout = QtWidgets.QHBoxLayout(lang_widget)
        
        self.languageCombo = QtWidgets.QComboBox()
        self.languageCombo.addItem("🐍 Python")
        self.languageCombo.addItem("📜 MEL")
        
        lang_layout.addWidget(QtWidgets.QLabel("Language:"))
        lang_layout.addWidget(self.languageCombo)
        lang_layout.addStretch()
        
        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        
        layout.addWidget(lang_widget)
        layout.addWidget(self.tabWidget)
        self.setCentralWidget(central_widget)
        
        # Dock widgets
        self._setup_docks()
        
        # Menu and toolbar
        self._setup_menus()
        
        # Status bar
        self.statusBar().showMessage("[OK] Ready!")
        
        # Initial tab
        self._new_file()
    
    def _setup_docks(self):
        """Setup dock widgets."""
        # Console
        try:
            self.console = OutputConsole()
        except:
            self.console = QtWidgets.QTextEdit()
            self.console.setPlainText("Console ready...")
            
        console_dock = QtWidgets.QDockWidget("Console", self)
        console_dock.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, console_dock)
        
        # Problems
        self.problems = QtWidgets.QTreeWidget()
        self.problems.setHeaderLabels(["Type", "Message", "Line"])
        problems_dock = QtWidgets.QDockWidget("Problems", self)
        problems_dock.setWidget(self.problems)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, problems_dock)
        
        # Explorer
        self.explorer = QtWidgets.QTreeView()
        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setRootPath("")
        self.explorer.setModel(self.fileModel)
        self.explorer.setRootIndex(self.fileModel.index(os.getcwd()))
        
        explorer_dock = QtWidgets.QDockWidget("Explorer", self)
        explorer_dock.setWidget(self.explorer)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, explorer_dock)
        
        # Chat dock is built in _build_chat_dock method
    
    def _setup_menus(self):
        """Setup menus and toolbar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QtGui.QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QtGui.QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QtGui.QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        run_action = QtGui.QAction("&Run", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._run_script)
        tools_menu.addAction(run_action)
        
        # Toolbar
        toolbar = self.addToolBar("Main")
        toolbar.addAction(new_action)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(run_action)
    
    def _new_file(self):
        """Create new file."""
        try:
            editor = CodeEditor()
            lang = self.languageCombo.currentText()
            if "Python" in lang:
                editor.set_language("python")
                content = "#!/usr/bin/env python3\n# New Python script\nprint('Hello World!')\n"
            else:
                editor.set_language("mel")
                content = "// New MEL script\nprint(\"Hello World!\\n\");\n"
            editor.setPlainText(content)
            
            # Connect problems signal for problems window
            if hasattr(editor, 'lintProblemsFound'):
                editor.lintProblemsFound.connect(self._update_problems)
        except:
            editor = QtWidgets.QTextEdit()
            editor.setPlainText("# New file\nprint('Hello World!')\n")
        
        index = self.tabWidget.addTab(editor, "untitled")
        self.tabWidget.setCurrentIndex(index)
    
    def _open_file(self):
        """Open file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    editor = CodeEditor()
                    if file_path.endswith('.py'):
                        editor.set_language("python")
                    elif file_path.endswith('.mel'):
                        editor.set_language("mel")
                    
                    # Connect problems signal for problems window
                    if hasattr(editor, 'lintProblemsFound'):
                        editor.lintProblemsFound.connect(self._update_problems)
                except:
                    editor = QtWidgets.QTextEdit()
                
                editor.setPlainText(content)
                tab_name = os.path.basename(file_path)
                index = self.tabWidget.addTab(editor, tab_name)
                self.tabWidget.setCurrentIndex(index)
                
                # Force rehighlight after tab is shown to ensure proper state tracking
                # Use QTimer to delay rehighlight until after the event loop processes the tab change
                if hasattr(editor, 'highlighter') and editor.highlighter:
                    def delayed_rehighlight():
                        # Reset all block states first
                        editor.highlighter._reset_all_block_states()
                        # Then rehighlight the entire document
                        editor.highlighter.rehighlight()
                    QtCore.QTimer.singleShot(50, delayed_rehighlight)
                
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to open: {e}")
    
    def _save_file(self):
        """Save current file."""
        current_widget = self.tabWidget.currentWidget()
        if current_widget:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save File", "", "All Files (*)"
            )
            if file_path:
                try:
                    content = current_widget.toPlainText()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    tab_name = os.path.basename(file_path)
                    current_index = self.tabWidget.currentIndex()
                    self.tabWidget.setTabText(current_index, tab_name)
                    
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save: {e}")
    
    def _run_script(self):
        """Run current script."""
        current_widget = self.tabWidget.currentWidget()
        if current_widget:
            code = current_widget.toPlainText()
            try:
                if hasattr(self.console, 'execute_code_and_capture'):
                    self.console.execute_code_and_capture(code, "python")
                else:
                    exec(code)
                    print("Code executed successfully")
            except Exception as e:
                print(f"Execution error: {e}")
    
    def _show_morpheus(self):
        """Show Morpheus chat."""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if "Morpheus" in dock.windowTitle():
                dock.show()
                dock.raise_()
                break

    # ============================================================================
    # Additional Event Handlers from Bloated Version
    # ============================================================================

    def _save_as_file(self):
        """Save as file - exact from bloated version"""
        self._save_file()

    def _close_tab(self, index):
        """Close tab - exact from bloated version"""
        if self.tabWidget.count() <= 1:
            self._new_file()
        self.tabWidget.removeTab(index)

    def _on_tab_changed(self, index):
        """Handle tab change - exact from bloated version"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'get_language'):
            lang = current_widget.get_language()
            if lang == "python":
                self.languageCombo.setCurrentText("🐍 Python")
            else:
                self.languageCombo.setCurrentText("📜 MEL")

    def _language_changed(self, text):
        """Handle language change - exact from bloated version"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'set_language'):
            if "Python" in text:
                current_widget.set_language("python")
            else:
                current_widget.set_language("mel")

    def _on_explorer_double_clicked(self, index):
        """Handle explorer double-click - exact from bloated version"""
        file_path = self.fileModel.filePath(index)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    editor = CodeEditor()
                    if file_path.endswith('.py'):
                        editor.set_language("python")
                    elif file_path.endswith('.mel'):
                        editor.set_language("mel")
                except:
                    editor = QtWidgets.QTextEdit()
                
                editor.setPlainText(content)
                tab_name = os.path.basename(file_path)
                index = self.tabWidget.addTab(editor, tab_name)
                self.tabWidget.setCurrentIndex(index)
                
            except Exception as e:
                print(f"Explorer file open error: {e}")

    def _on_problem_double_clicked(self, item, column):
        """Handle problem double-click - exact from bloated version"""
        # Navigate to problem location in code
        pass

    # Edit menu actions - exact from bloated version
    def _undo(self):
        """Undo action"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'undo'):
            current_widget.undo()

    def _redo(self):
        """Redo action"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'redo'):
            current_widget.redo()

    def _cut(self):
        """Cut action"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'cut'):
            current_widget.cut()

    def _copy(self):
        """Copy action"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'copy'):
            current_widget.copy()

    def _paste(self):
        """Paste action"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'paste'):
            current_widget.paste()

    # View menu actions - exact from bloated version
    def _toggle_console(self):
        """Toggle console dock visibility"""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if "Console" in dock.windowTitle():
                dock.setVisible(not dock.isVisible())
                break

    def _toggle_dock(self, dock_name):
        """Toggle visibility of a specific dock panel"""
        dock_map = {
            "ExplorerDock": (self.explorer_dock, self.toggle_explorer_action),
            "MorpheusDock": (self.chat_dock, self.toggle_morpheus_action),
            "ConsoleDock": (self.console_dock, self.toggle_console_action),
            "ProblemsDock": (self.problems_dock, self.toggle_problems_action)
        }
        
        if dock_name in dock_map:
            dock, action = dock_map[dock_name]
            is_visible = dock.isVisible()
            dock.setVisible(not is_visible)
            action.setChecked(not is_visible)
    
    def _hide_all_panels(self):
        """Hide all dock panels to maximize editor space"""
        self.explorer_dock.hide()
        self.chat_dock.hide()
        self.console_dock.hide()
        self.problems_dock.hide()
        
        self.toggle_explorer_action.setChecked(False)
        self.toggle_morpheus_action.setChecked(False)
        self.toggle_console_action.setChecked(False)
        self.toggle_problems_action.setChecked(False)
    
    def _show_all_panels(self):
        """Show all dock panels"""
        self.explorer_dock.show()
        self.chat_dock.show()
        self.console_dock.show()
        self.problems_dock.show()
        
        self.toggle_explorer_action.setChecked(True)
        self.toggle_morpheus_action.setChecked(True)
        self.toggle_console_action.setChecked(True)
        self.toggle_problems_action.setChecked(True)
    
    def _sync_explorer_action(self, visible):
        """Keep Explorer menu item in sync with dock visibility"""
        if hasattr(self, 'toggle_explorer_action'):
            self.toggle_explorer_action.setChecked(visible)
    
    def _sync_morpheus_action(self, visible):
        """Keep Morpheus AI menu item in sync with dock visibility"""
        if hasattr(self, 'toggle_morpheus_action'):
            self.toggle_morpheus_action.setChecked(visible)
    
    def _sync_console_action(self, visible):
        """Keep Output Console menu item in sync with dock visibility"""
        if hasattr(self, 'toggle_console_action'):
            self.toggle_console_action.setChecked(visible)
    
    def _sync_problems_action(self, visible):
        """Keep Problems menu item in sync with dock visibility"""
        if hasattr(self, 'toggle_problems_action'):
            self.toggle_problems_action.setChecked(visible)
    
    # ============================================================================
    # Find/Replace Methods (VS Code Style)
    # ============================================================================
    
    def _show_find(self):
        """Show find widget (Ctrl+F)"""
        self.findReplaceWidget.show()
        self.replaceRow.hide()
        self.toggleReplaceBtn.setText("▶")
        self.findInput.setFocus()
        self.findInput.selectAll()
        
        # Pre-fill with selected text if any
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'textCursor'):
            cursor = current_widget.textCursor()
            if cursor.hasSelection():
                self.findInput.setText(cursor.selectedText())
    
    def _show_replace(self):
        """Show find and replace widget (Ctrl+H)"""
        self.findReplaceWidget.show()
        self.replaceRow.show()
        self.toggleReplaceBtn.setText("▼")
        self.findInput.setFocus()
        self.findInput.selectAll()
        
        # Pre-fill with selected text if any
        current_widget = self.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'textCursor'):
            cursor = current_widget.textCursor()
            if cursor.hasSelection():
                self.findInput.setText(cursor.selectedText())
    
    def _toggle_replace_mode(self):
        """Toggle replace row visibility"""
        if self.replaceRow.isVisible():
            self.replaceRow.hide()
            self.toggleReplaceBtn.setText("▶")
        else:
            self.replaceRow.show()
            self.toggleReplaceBtn.setText("▼")
    
    def _hide_find_replace(self):
        """Hide find/replace widget"""
        self.findReplaceWidget.hide()
        
        # Clear all highlights when closing
        current_widget = self.tabWidget.currentWidget()
        if current_widget:
            if hasattr(current_widget, 'setExtraSelections'):
                current_widget.setExtraSelections([])
            current_widget.setFocus()
    
    def _find_next(self):
        """Find next occurrence"""
        current_widget = self.tabWidget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'find'):
            return
        
        search_text = self.findInput.text()
        if not search_text:
            return
        
        # Build find flags
        flags = QtGui.QTextDocument.FindFlags()
        if self.matchCaseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.wholeWordCheck.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        
        # Try to find
        found = current_widget.find(search_text, flags)
        
        if not found:
            # Wrap around from beginning
            cursor = current_widget.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            current_widget.setTextCursor(cursor)
            found = current_widget.find(search_text, flags)
            
            if not found:
                self.findMatchLabel.setText("No matches found")
                self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
            else:
                self.findMatchLabel.setText("Wrapped")
                self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        else:
            self._update_match_count()
    
    def _find_previous(self):
        """Find previous occurrence"""
        current_widget = self.tabWidget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'find'):
            return
        
        search_text = self.findInput.text()
        if not search_text:
            return
        
        # Build find flags with backward flag
        flags = QtGui.QTextDocument.FindBackward
        if self.matchCaseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.wholeWordCheck.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        
        # Try to find
        found = current_widget.find(search_text, flags)
        
        if not found:
            # Wrap around from end
            cursor = current_widget.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            current_widget.setTextCursor(cursor)
            found = current_widget.find(search_text, flags)
            
            if not found:
                self.findMatchLabel.setText("No matches found")
                self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
            else:
                self.findMatchLabel.setText("Wrapped")
                self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        else:
            self._update_match_count()
    
    def _replace_current(self):
        """Replace current selection"""
        current_widget = self.tabWidget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'textCursor'):
            return
        
        cursor = current_widget.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.findInput.text():
            cursor.insertText(self.replaceInput.text())
            # Find next after replacing
            self._find_next()
    
    def _replace_all(self):
        """Replace all occurrences"""
        current_widget = self.tabWidget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'toPlainText'):
            return
        
        search_text = self.findInput.text()
        replace_text = self.replaceInput.text()
        
        if not search_text:
            return
        
        # Get all text
        text = current_widget.toPlainText()
        
        # Count occurrences
        if self.matchCaseCheck.isChecked():
            count = text.count(search_text)
        else:
            count = text.lower().count(search_text.lower())
        
        if count == 0:
            self.findMatchLabel.setText("No matches found")
            self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
            return
        
        # Replace all
        if self.matchCaseCheck.isChecked():
            new_text = text.replace(search_text, replace_text)
        else:
            # Case-insensitive replace
            import re
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            new_text = pattern.sub(replace_text, text)
        
        # Update document
        current_widget.setPlainText(new_text)
        
        self.findMatchLabel.setText(f"Replaced {count} occurrence{'s' if count > 1 else ''}")
        self.findMatchLabel.setStyleSheet("color: #4ec9b0; font-size: 11px;")
    
    def _update_match_count(self):
        """Update match count label"""
        current_widget = self.tabWidget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'toPlainText'):
            return
        
        search_text = self.findInput.text()
        if not search_text:
            self.findMatchLabel.setText("")
            return
        
        text = current_widget.toPlainText()
        
        if self.matchCaseCheck.isChecked():
            count = text.count(search_text)
        else:
            count = text.lower().count(search_text.lower())
        
        if count > 0:
            self.findMatchLabel.setText(f"{count} match{'es' if count > 1 else ''}")
            self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        else:
            self.findMatchLabel.setText("No matches")
            self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
    
    def _on_find_text_changed(self, text):
        """Handle real-time highlighting as user types in find field"""
        if not text:
            # Clear all highlights
            self.findMatchLabel.setText("")
            current_widget = self.tabWidget.currentWidget()
            if current_widget and hasattr(current_widget, 'setExtraSelections'):
                current_widget.setExtraSelections([])
            return
        
        current_widget = self.tabWidget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'toPlainText'):
            return
        
        # Highlight all matches
        extra_selections = []
        
        # Build find flags
        flags = QtGui.QTextDocument.FindFlags()
        if self.matchCaseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.wholeWordCheck.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        
        # Find all occurrences
        cursor = QtGui.QTextCursor(current_widget.document())
        highlight_color = QtGui.QColor("#ffd33d")  # VS Code yellow highlight
        
        while True:
            cursor = current_widget.document().find(text, cursor, flags)
            if cursor.isNull():
                break
            
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(highlight_color)
            selection.format.setForeground(QtGui.QColor("#000000"))  # Black text
            extra_selections.append(selection)
        
        current_widget.setExtraSelections(extra_selections)
        
        # Update match count
        self._update_match_count()

    # AI menu actions - exact from bloated version
    def _show_morpheus_chat(self):
        """Show Morpheus AI chat"""
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if "Morpheus" in dock.windowTitle():
                dock.show()
                dock.raise_()
                break

    # Tools menu actions - exact from bloated version
    def _syntax_check(self):
        """Run syntax check on current file"""
        current_widget = self.tabWidget.currentWidget()
        if current_widget:
            code = current_widget.toPlainText()
            try:
                compile(code, '<string>', 'exec')
                QtWidgets.QMessageBox.information(self, "Syntax Check", "No syntax errors found!")
            except SyntaxError as e:
                QtWidgets.QMessageBox.warning(self, "Syntax Error", f"Syntax error at line {e.lineno}: {e.msg}")

    # Help menu actions - exact from bloated version  
    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(self, "About NEO Script Editor", 
            """[NEO] Script Editor v2.2 - Complete Modular Edition

[*] Features:
• Complete modular architecture with ALL original bloated features
• Enhanced syntax highlighting with PySide6/Qt support  
• Real-time error detection with VSCode-style indicators
• Comprehensive Maya Python API integration
• Morpheus AI chat integration
• Advanced code editor with all modern features
• All dock widgets: Console, Problems, Explorer, Morpheus Chat
• Complete menu system with all original functionality
• Clean, optimized, and maintainable codebase

[SUCCESS] All functionalities from the original bloated version but with clean, modular design!""")

    def _send_message(self):
        """Send message to Morpheus AI - exact from bloated version."""
        message = self.chatInput.toPlainText().strip()
        if not message:
            return

        # Add user message to history
        self._add_chat_message("You", message, "#58a6ff")
        
        # Show thinking indicator
        self._show_thinking_indicator()
        
        # Clear input
        self.chatInput.clear()
        
        # Disable send button while processing
        self.sendBtn.setEnabled(False)
        
        # Get context 
        context = ""
        current_editor = self.tabWidget.currentWidget()
        
        # Auto-include current code if asking about errors, syntax, bugs, or fixes
        auto_context_keywords = ['error', 'syntax', 'bug', 'fix', 'wrong', 'issue', 'problem', 'incorrect', 'mistake']
        should_auto_include = any(keyword in message.lower() for keyword in auto_context_keywords)
        
        if should_auto_include and current_editor:
            context = current_editor.toPlainText()

        # Send to Morpheus using initialized manager
        if hasattr(self, 'morpheus_manager') and self.morpheus_manager:
            self.morpheus_manager.send_message(message, context)
        else:
            self._add_chat_message("Morpheus", "AI service not available. Please check your API key.", "#ff6b6b")
            self.sendBtn.setEnabled(True)

    def _add_chat_message(self, sender, message, color="#f0f6fc"):
        """Add a message to the chat history with enhanced code formatting and actions - exact from bloated version."""
        import html
        timestamp = QtCore.QTime.currentTime().toString("hh:mm")
        
        try:
            # Format Morpheus messages specially (process code blocks)
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

    def _on_morpheus_response(self, response):
        """Handle response from MorpheusManager - exact from bloated version."""
        self._hide_thinking_indicator()
        self._add_chat_message("Morpheus", response, "#238636")

    def _format_morpheus_message(self, message):
        """Format Morpheus message exactly like GitHub Copilot - truly clean and readable."""
        import re
        import html
        
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
        if current_placeholders:
            # Collect all code blocks for comprehensive fix processing
            all_code_blocks = list(self._code_blocks.values())
            
            if all_code_blocks:
                # Notify user about available actions
                if len(all_code_blocks) > 1:
                    self.console.append_tagged("COPILOT", f"Multiple code suggestions available ({len(all_code_blocks)} blocks) - click Copy/Apply/Keep buttons", "#58a6ff")
                else:
                    self.console.append_tagged("COPILOT", "Code suggestion available - click Copy/Apply/Keep buttons", "#58a6ff")
        
        return formatted_message

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

    def _copy_code_to_clipboard(self, code):
        """Copy code to system clipboard."""
        try:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(code)
            self.console.append_tagged("SUCCESS", "📋 Code copied to clipboard!", "#28a745")
        except Exception as e:
            self.console.append_tagged("ERROR", f"Failed to copy code: {e}", "#dc3545")

    def _apply_code_to_editor(self, code):
        """Apply code to the current editor tab."""
        try:
            editor = self._active_editor()
            if editor:
                cursor = editor.textCursor()
                cursor.insertText(code)
                self.console.append_tagged("SUCCESS", "✅ Code applied to editor!", "#28a745")
            else:
                self.console.append_tagged("WARNING", "No active editor found. Please create or open a file first.", "#fd7e14")
        except Exception as e:
            self.console.append_tagged("ERROR", f"Failed to apply code: {e}", "#dc3545")

    def _keep_as_fix(self, code):
        """Keep code as a fix (replace current editor content)."""
        try:
            editor = self._active_editor()
            if editor:
                # Replace entire content
                editor.setPlainText(code)
                self.console.append_tagged("SUCCESS", "🔧 Code applied as fix (replaced content)!", "#28a745")
            else:
                self.console.append_tagged("WARNING", "No active editor found. Please create or open a file first.", "#fd7e14")
        except Exception as e:
            self.console.append_tagged("ERROR", f"Failed to apply fix: {e}", "#dc3545")

    def _show_info_message(self, title, message):
        """Show an information message dialog."""
        QtWidgets.QMessageBox.information(self, title, message)

    def _active_editor(self):
        """Get the currently active editor widget."""
        from editor.code_editor import CodeEditor
        w = self.tabWidget.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def _update_problems(self, problems):
        """Update the problems list with linting results - exact from bloated version."""
        try:
            if not hasattr(self, 'problemsList') or not self.problemsList:
                print("⚠️ Problems list not available")
                return
                
            self.problemsList.clear()
            
            for problem in problems:
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
        """Navigate to the line when a problem is double-clicked - exact from bloated version."""
        try:
            if not item:
                return
                
            # Get the line number from the item data
            line_num = item.data(2, QtCore.Qt.UserRole)
            if not line_num or line_num == 0:
                # Try to parse from text if data not available
                try:
                    line_num = int(item.text(2))
                except:
                    return
            
            # Get the active editor
            editor = self._active_editor()
            if not editor:
                return
            
            # Navigate to the line
            cursor = editor.textCursor()
            block = editor.document().findBlockByLineNumber(line_num - 1)  # 0-based
            cursor.setPosition(block.position())
            editor.setTextCursor(cursor)
            editor.setFocus()
            
            # Optionally highlight the line briefly
            editor.centerCursor()
            
        except Exception as e:
            print(f"Error navigating to problem: {e}")
        self.sendBtn.setEnabled(True)

    def _show_thinking_indicator(self):
        """Show thinking indicator with animation - exact from bloated version."""
        self.responseIndicator.setVisible(True)
        self.thinkingDots = 0
        self.thinkingTimer.start(500)  # Update every 500ms
        
    def _hide_thinking_indicator(self):
        """Hide thinking indicator - exact from bloated version."""
        self.thinkingTimer.stop()
        self.responseIndicator.setVisible(False)
        self.sendBtn.setEnabled(True)  # Re-enable send button
        
    def _animate_thinking(self):
        """Animate the thinking indicator - exact from bloated version."""
        dots = "." * (self.thinkingDots % 4)
        self.responseIndicator.setText(f"🤖 Morpheus is thinking{dots}")
        self.thinkingDots += 1

    def _chat_key_press_event(self, event):
        """Handle key press events in chat input - Enter to send."""
        if event.key() == QtCore.Qt.Key_Return and not (event.modifiers() & QtCore.Qt.ShiftModifier):
            # Enter without Shift = send message
            self._send_message()
        else:
            # Let the default behavior handle other keys (including Shift+Enter for new line)
            QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)

    def _prev_conversation(self):
        """Navigate to previous conversation."""
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.previous_conversation()
            self._load_current_conversation()
            self._update_history_info()

    def _next_conversation(self):
        """Navigate to next conversation."""
        if hasattr(self, 'morpheus_manager'):
            result = self.morpheus_manager.next_conversation()
            self._load_current_conversation()
            self._update_history_info()

    def _new_conversation(self):
        """Start a new conversation."""
        if hasattr(self, 'morpheus_manager'):
            self.morpheus_manager.new_conversation()
        self._clear_chat()
        self._update_history_info()

    def _clear_chat(self):
        """Clear chat history display - exact from bloated version."""
        self.chatHistory.clear()

    def _on_history_updated(self, chat_history):
        """Handle history updates from Morpheus manager - exact from bloated version."""
        self._update_history_info()
        # Only reload if chat is empty but we have history
        if (self.chatHistory.toPlainText().strip() == "" and 
            hasattr(self, 'morpheus_manager') and 
            self.morpheus_manager.chat_history):
            self._load_current_conversation()

    def _load_current_conversation(self):
        """Load the current conversation history - exact from bloated version."""
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
        """Update the history navigation info - exact from bloated version."""
        if hasattr(self, 'morpheus_manager'):
            current, total = self.morpheus_manager.get_conversation_info()
            
            # Update label - show "All" when viewing all conversations
            if self.morpheus_manager.current_chat_index == -1:
                label_text = f"All/{total}"
            else:
                label_text = f"{current}/{total}"
            
            self.historyLabel.setText(label_text)
            
            # Enable/disable navigation buttons
            # Previous: enabled if we have history and (viewing all OR not at first conversation)
            prev_enabled = total > 0 and (self.morpheus_manager.current_chat_index == -1 or 
                                         self.morpheus_manager.current_chat_index > 0)
            
            # Next: enabled if we have history AND we're viewing a specific conversation (not "All")
            next_enabled = (total > 0 and 
                           self.morpheus_manager.current_chat_index != -1 and 
                           self.morpheus_manager.current_chat_index < total - 1)
            
            self.prevChatBtn.setEnabled(prev_enabled)
            self.nextChatBtn.setEnabled(next_enabled)
        else:
            self.historyLabel.setText("1/1")
            if hasattr(self, 'prevChatBtn'):
                self.prevChatBtn.setEnabled(False)
            if hasattr(self, 'nextChatBtn'):
                self.nextChatBtn.setEnabled(False)

    def _on_provider_changed(self, text):
        """Handle AI provider selection change."""
        # Determine provider from selection
        provider = "claude" if "Claude" in text else "openai"
        
        # Update morpheus provider
        if hasattr(self, 'morpheus'):
            self.morpheus.provider = provider
            self.morpheus.client = self.morpheus._make_client()
            
            # Save preference
            settings = QtCore.QSettings("AI_Script_Editor", "settings")
            settings.setValue("AI_PROVIDER", provider)
            
            # Update model list for the new provider
            self._update_model_list()
            
            # Show status message
            provider_name = "Claude Sonnet" if provider == "claude" else "GPT-4o"
            if self.morpheus.client:
                print(f"✓ Switched to {provider_name}")
            else:
                print(f"⚠ Switched to {provider_name} but no API key found. Set it in Tools → Settings")

    def _update_model_list(self):
        """Update model selector based on current provider."""
        if not hasattr(self, 'model_selector'):
            return
        
        # Block signals while updating to prevent unnecessary triggers
        self.model_selector.blockSignals(True)
        self.model_selector.clear()
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        
        if current_provider == "openai":
            # OpenAI models
            models = [
                ("GPT-4o Mini (Fast, Cheap)", "gpt-4o-mini"),
                ("GPT-4o (Most Capable)", "gpt-4o"),
                ("GPT-4 Turbo", "gpt-4-turbo"),
                ("o1-preview (Reasoning)", "o1-preview"),
                ("o1-mini (Fast Reasoning)", "o1-mini"),
            ]
            for display_name, model_id in models:
                self.model_selector.addItem(display_name, model_id)
            
            # Load saved model or default to gpt-4o-mini
            saved_model = settings.value("OPENAI_MODEL", "gpt-4o-mini")
            for i in range(self.model_selector.count()):
                if self.model_selector.itemData(i) == saved_model:
                    self.model_selector.setCurrentIndex(i)
                    break
        else:
            # Claude models
            models = [
                ("Claude Sonnet 4 (Latest)", "claude-sonnet-4-20250514"),
                ("Claude Opus 4 (Most Capable)", "claude-opus-4-20250514"),
                ("Claude Sonnet 3.5 (Legacy)", "claude-3-5-sonnet-20241022"),
                ("Claude Haiku 3.5 (Fast)", "claude-3-5-haiku-20241022"),
            ]
            for display_name, model_id in models:
                self.model_selector.addItem(display_name, model_id)
            
            # Load saved model or default to sonnet 4
            saved_model = settings.value("CLAUDE_MODEL", "claude-sonnet-4-20250514")
            for i in range(self.model_selector.count()):
                if self.model_selector.itemData(i) == saved_model:
                    self.model_selector.setCurrentIndex(i)
                    break
        
        # Connect model change event (use flag to avoid disconnect warnings)
        self.model_selector.blockSignals(False)
        if hasattr(self, '_model_selector_connected') and self._model_selector_connected:
            try:
                self.model_selector.currentIndexChanged.disconnect(self._on_model_changed)
            except (RuntimeError, TypeError):
                pass  # Signal wasn't connected
        
        self.model_selector.currentIndexChanged.connect(self._on_model_changed)
        self._model_selector_connected = True

    def _on_model_changed(self, index):
        """Handle model selection change."""
        if not hasattr(self, 'model_selector') or index < 0:
            return
            
        model_id = self.model_selector.itemData(index)
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        
        # Save the selected model
        if current_provider == "openai":
            settings.setValue("OPENAI_MODEL", model_id)
        else:
            settings.setValue("CLAUDE_MODEL", model_id)
        
        # Update morpheus to use the new model
        if hasattr(self, 'morpheus'):
            self.morpheus.current_model = model_id
        
        print(f"✓ Switched to model: {self.model_selector.currentText()}")

    def _show_settings_dialog(self):
        """Show AI provider settings dialog."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("AI Provider Settings")
        dialog.setMinimumWidth(500)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Provider selection
        provider_group = QtWidgets.QGroupBox("AI Provider")
        provider_layout = QtWidgets.QVBoxLayout()
        
        provider_combo = QtWidgets.QComboBox()
        provider_combo.addItems(["OpenAI (GPT-4o)", "Claude (Anthropic)"])
        
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        provider_combo.setCurrentText("Claude (Anthropic)" if current_provider == "claude" else "OpenAI (GPT-4o)")
        
        provider_layout.addWidget(QtWidgets.QLabel("Select AI Provider:"))
        provider_layout.addWidget(provider_combo)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # OpenAI settings
        openai_group = QtWidgets.QGroupBox("OpenAI Settings")
        openai_layout = QtWidgets.QFormLayout()
        
        openai_key_input = QtWidgets.QLineEdit()
        openai_key_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        openai_key_input.setPlaceholderText("sk-...")
        openai_key_input.setText(settings.value("OPENAI_API_KEY", ""))
        
        openai_layout.addRow("API Key:", openai_key_input)
        openai_layout.addRow("", QtWidgets.QLabel('<a href="https://platform.openai.com/api-keys">Get API Key</a>'))
        openai_group.setLayout(openai_layout)
        layout.addWidget(openai_group)
        
        # Anthropic (Claude) settings
        claude_group = QtWidgets.QGroupBox("Anthropic (Claude) Settings")
        claude_layout = QtWidgets.QFormLayout()
        
        claude_key_input = QtWidgets.QLineEdit()
        claude_key_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        claude_key_input.setPlaceholderText("sk-ant-...")
        claude_key_input.setText(settings.value("ANTHROPIC_API_KEY", ""))
        
        claude_layout.addRow("API Key:", claude_key_input)
        claude_layout.addRow("", QtWidgets.QLabel('<a href="https://console.anthropic.com/settings/keys">Get API Key</a>'))
        claude_group.setLayout(claude_layout)
        layout.addWidget(claude_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_settings():
            # Save provider
            provider = "claude" if "Claude" in provider_combo.currentText() else "openai"
            settings.setValue("AI_PROVIDER", provider)
            
            # Save API keys
            if openai_key_input.text():
                settings.setValue("OPENAI_API_KEY", openai_key_input.text())
                os.environ["OPENAI_API_KEY"] = openai_key_input.text()
            
            if claude_key_input.text():
                settings.setValue("ANTHROPIC_API_KEY", claude_key_input.text())
                os.environ["ANTHROPIC_API_KEY"] = claude_key_input.text()
            
            # Reconnect AI with new settings
            if hasattr(self, 'morpheus'):
                self.morpheus.provider = provider
                self.morpheus.client = self.morpheus._make_client()
                if self.morpheus.client:
                    QtWidgets.QMessageBox.information(
                        self, 
                        "Success", 
                        f"Successfully connected to {provider.upper()}!"
                    )
                else:
                    QtWidgets.QMessageBox.warning(
                        self, 
                        "Warning", 
                        f"Settings saved but failed to connect to {provider.upper()}. Check your API key."
                    )
            
            dialog.accept()
        
        save_btn.clicked.connect(save_settings)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

def main():
    """Main entry point."""
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    window.show()
    return app.exec()

if __name__ == "__main__":
    main()
