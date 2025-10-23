"""
AI Script Editor - Refactored Modular Version
Main window now delegates to manager modules for clean architecture

Compatible with:
- Maya 2022-2024 (PySide2 / Qt 5)
- Maya 2025+ (PySide6 / Qt 6)
"""
import os

# Qt compatibility layer - works with both PySide2 and PySide6
from qt_compat import QtWidgets, QtCore, QtGui, QT_VERSION

# --- Ensure OpenAI key is loaded before Morpheus init ---
settings = QtCore.QSettings("AI_Script_Editor", "settings")
stored_key = settings.value("OPENAI_API_KEY", "")
if stored_key:
    os.environ["OPENAI_API_KEY"] = stored_key
    print("[OpenAI] API key injected successfully before Morpheus init.")
else:
    print("[!] No stored OpenAI key found. Set one via Settings -> API Key.")

# Internal imports
try:
    from editor.code_editor import CodeEditor
    from editor.highlighter import PythonHighlighter, MELHighlighter
    from ui.output_console import OutputConsole
    from ai.chat import AIMorpheus
    from ai.copilot_manager import MorpheusManager
    
    # Import all manager modules
    from ui.find_replace_manager import FindReplaceManager
    from ui.menu_manager import MenuManager
    from ui.dock_manager import DockManager
    from ui.chat_manager import ChatManager
    from ui.file_manager import FileManager
    from ui.debug_manager import DebugManager
    
    # Import beta/license manager
    from license.beta_manager import BetaManager
    
    print("[OK] All core components imported successfully")
except ImportError as e:
    print(f"[!] Import warning: {e} (using fallbacks)")

DARK_STYLE = """
QWidget { background: #1E1E1E; color: #DDD; font-family: Segoe UI, Consolas; }
QMenuBar, QMenu, QToolBar { font-size: 11pt; background-color:#2D2D30; }
QMenuBar::item:selected { background: #00ff41; color: #000; }
QMenuBar::item:hover { background: #00ff41; color: #000; }
QMenu::item:selected { background: #00ff41; color: #000; }
QMenu::item:hover { background: #00ff41; color: #000; }
QTextBrowser, QTextEdit { border: 1px solid #333; border-radius: 4px; }
QPushButton { background: #2D2D30; color: #EEE; border-radius: 4px; padding: 4px 8px; }
QPushButton:hover { background: #3E3E42; }
QLineEdit { background: #252526; border: 1px solid #333; color: #EEE; border-radius: 4px; padding: 3px; }
QDockWidget::title { background: #252526; padding: 4px; }
QTabBar::tab { background: #2D2D30; color: #DDD; padding: 6px 12px; border:1px solid #3E3E42; }
QTabBar::tab:selected { background: #3E3E42; }
QToolBar { spacing: 8px; padding: 4px; }
QToolButton { 
    background: transparent; 
    color: #ffffff; 
    border: none; 
    border-radius: 4px;
    padding: 6px;
    opacity: 0.8;
}
QToolButton:hover { 
    background: rgba(255, 255, 255, 0.1);
    opacity: 1.0;
}
QToolButton:pressed {
    background: rgba(255, 255, 255, 0.15);
}
"""


class AiScriptEditor(QtWidgets.QMainWindow):
    """NEO Script Editor - Modern Maya script editor with Morpheus AI"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize beta manager first
        self.beta_manager = BetaManager()
        
        # Check if beta is expired (block if needed)
        if self.beta_manager.is_expired():
            self.beta_manager.show_startup_notice(self)
            # Don't initialize the rest of the app
            QtCore.QTimer.singleShot(100, self.close)
            return
        
        # Update window title with beta status
        base_title = "NEO Script Editor v3.2 - Morpheus AI"
        self.setWindowTitle(base_title + self.beta_manager.get_title_suffix())
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "matrix.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Set window flags to keep it on top of Maya (like Maya's script editor)
        try:
            # Try to get Maya's main window as parent for better integration
            import maya.OpenMayaUI as omui
            import shiboken6
            maya_main_window_ptr = omui.MQtUtil.mainWindow()
            if maya_main_window_ptr:
                maya_main_window = shiboken6.wrapInstance(int(maya_main_window_ptr), QtWidgets.QWidget)
                self.setParent(maya_main_window)
                # Use window flags that work well with Maya - stay on top of Maya only
                self.setWindowFlags(
                    QtCore.Qt.Window |  # Use Window instead of Tool for full controls
                    QtCore.Qt.WindowCloseButtonHint |
                    QtCore.Qt.WindowMinimizeButtonHint |
                    QtCore.Qt.WindowMaximizeButtonHint |
                    QtCore.Qt.WindowTitleHint
                )
            else:
                # Fallback if Maya main window not found - still use always on top
                self.setWindowFlags(
                    QtCore.Qt.Window | 
                    QtCore.Qt.WindowStaysOnTopHint |
                    QtCore.Qt.WindowCloseButtonHint |
                    QtCore.Qt.WindowMinimizeButtonHint |
                    QtCore.Qt.WindowMaximizeButtonHint |
                    QtCore.Qt.WindowTitleHint
                )
        except ImportError:
            # Not running in Maya, use standard always-on-top
            self.setWindowFlags(
                QtCore.Qt.Window | 
                QtCore.Qt.WindowStaysOnTopHint |
                QtCore.Qt.WindowCloseButtonHint |
                QtCore.Qt.WindowMinimizeButtonHint |
                QtCore.Qt.WindowMaximizeButtonHint |
                QtCore.Qt.WindowTitleHint
                )
        
        # Performance optimizations to reduce lag during window operations
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, True)  # Optimize painting
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)  # Allow background
        self.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors, True)  # Reduce overhead
        
        # Critical Maya performance fix - use faster update mode
        self.setUpdatesEnabled(True)
        
        # Optimize window for compositing (reduces lag during drag)
        try:
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)  # Disable transparency
            self.setAttribute(QtCore.Qt.WA_NoChildEventsForParent, True)  # Reduce event propagation
        except:
            pass  # Skip if not available in this Qt version
        
        self.resize(1200, 700)
        self.setStyleSheet(DARK_STYLE)        # Track problems per editor/tab
        self.editor_problems = {}  # Dictionary: editor_id -> list of problems
        
        # Track file paths for tabs (for session persistence)
        self.tab_file_paths = {}  # Dictionary: tab_index -> file_path
        
        # Initialize components
        self._setup_central_widget()
        self._setup_floating_code_actions()
        
        # Initialize all manager modules
        self._init_managers()
        
        # Setup UI using managers
        self._setup_ui_with_managers()
        
        # Show beta notice if needed (non-blocking)
        QtCore.QTimer.singleShot(500, lambda: self.beta_manager.show_startup_notice(self))
        
        # Setup status bar with beta info
        self._setup_status_bar()
        
        # Restore previous session (tabs and files) - DEFERRED for faster startup
        QtCore.QTimer.singleShot(500, self._restore_session)
        
        # Initialize chat manager (deferred for faster startup - AI loading is slow)
        QtCore.QTimer.singleShot(100, self._init_chat_manager_deferred)
        
        # Track if session needs saving (dirty flag for performance)
        self._session_dirty = False
        
        # Auto-save session every 3 minutes (reduced frequency for better performance)
        # Only saves if there are actual changes (_session_dirty flag)
        self.auto_save_timer = QtCore.QTimer()
        self.auto_save_timer.timeout.connect(lambda: self._save_session(auto_save=True))
        self.auto_save_timer.start(180000)  # 3 minutes (180 seconds)
        
        print("[OK] AI Script Editor initialized with refactored modular architecture!")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts - Esc to close find/replace"""
        if event.key() == QtCore.Qt.Key_Escape:
            if self.find_replace_manager and self.find_replace_manager.is_visible():
                self.find_replace_manager.hide_find_replace()
                event.accept()
                return
        super().keyPressEvent(event)
    
    def _setup_central_widget(self):
        """Setup central tabbed editor"""
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
        # Load custom icons from assets folder
        python_icon_path = os.path.join(os.path.dirname(__file__), "assets", "python.png")
        mel_icon_path = os.path.join(os.path.dirname(__file__), "assets", "mel.png")
        python_icon = QtGui.QIcon(python_icon_path) if os.path.exists(python_icon_path) else QtGui.QIcon()
        mel_icon = QtGui.QIcon(mel_icon_path) if os.path.exists(mel_icon_path) else QtGui.QIcon()
        
        self.languageCombo.addItem(python_icon, " Python", "Python")
        self.languageCombo.addItem(mel_icon, " MEL", "MEL") 
        self.languageCombo.setCurrentIndex(0)  # Default to Python
        self.languageCombo.setIconSize(QtCore.QSize(16, 16))
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
            QComboBox:hover { border-color: #00ff41; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: url(none); }
            QComboBox QAbstractItemView {
                background: #21262d;
                border: 1px solid #30363d;
                selection-background-color: transparent;
                color: #f0f6fc;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
                min-height: 20px;
                border-left: 3px solid transparent;
            }
            QComboBox QAbstractItemView::item:selected {
                border-left: 3px solid #00ff41;
                background: transparent;
            }
        """)
        tabHeaderLayout.addWidget(self.languageCombo)
        tabHeaderLayout.addStretch()
        
        centralLayout.addWidget(tabHeader)
        
        # Store layout for find/replace widget (will be setup by manager)
        self.centralLayout = centralLayout
        
        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)  # Enable drag-and-drop tab reordering
        
        centralLayout.addWidget(self.tabWidget)
        
        self.setCentralWidget(centralWidget)
    
    def _setup_floating_code_actions(self):
        """Setup floating code actions"""
        self.floating_actions = QtWidgets.QWidget(self)
        self.floating_actions.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.floating_actions.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.floating_actions.setStyleSheet("""
            QWidget {
                background: rgba(45, 45, 48, 220);
                border-radius: 8px;
                border: 1px solid #00ff41;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(self.floating_actions)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        ai_btn = QtWidgets.QPushButton("🧠 AI Suggest")
        ai_btn.setStyleSheet("""
            QPushButton {
                background: #21262d;
                color: #00ff41;
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
    
    def _init_managers(self):
        """Initialize all manager modules"""
        print("[Startup] Initializing managers...")
        # Initialize managers
        self.dock_manager = DockManager(self)
        self.file_manager = FileManager(self, self.tabWidget, self.languageCombo)
        self.find_replace_manager = FindReplaceManager(self, self.tabWidget)
        self.debug_manager = DebugManager(self)
        self.menu_manager = MenuManager(self)
        
        # DEFERRED: Initialize chat manager after window is visible (AI loading can be slow)
        self.chat_manager = None
    def _init_chat_manager_deferred(self):
        """Initialize chat manager after UI is visible (AI loading is slow)"""
        print("[Startup] Initializing chat manager (deferred)...")
        from ui.chat_manager import ChatManager
        self.chat_manager = ChatManager(self)
        
        # Setup chat dock
        self.chat_manager.build_chat_dock()
        
        # Make chat manager widgets available on main window
        self.chatHistory = self.chat_manager.chatHistory
        self.chatInput = self.chat_manager.chatInput
        self.sendBtn = self.chat_manager.sendBtn
        self.morpheus = self.chat_manager.morpheus
        self.morpheus_manager = self.chat_manager.morpheus_manager
        self.chat_dock = self.dock_manager.chat_dock  # Store chat dock reference
        
        print("[Startup] Chat manager ready")
    
    def _setup_ui_with_managers(self):
        """Setup UI using manager modules"""
        print("[Startup] Setting up UI...")
        # Setup find/replace widget (before docks so it's in correct position)
        self.find_replace_manager.setup_widget(self.centralLayout)
        
        # Setup dock widgets (Console, Problems, Explorer) - FAST
        self.dock_manager.setup_docks()
        
        # Make dock manager widgets available directly on main window for compatibility
        self.console = self.dock_manager.console
        self.problemsList = self.dock_manager.problemsList
        self.explorerView = self.dock_manager.explorerView
        self.fileModel = self.dock_manager.fileModel
        self.console_dock = self.dock_manager.console_dock
        self.problems_dock = self.dock_manager.problems_dock
        self.explorer_dock = self.dock_manager.explorer_dock
        
        # Chat dock will be setup by deferred _init_chat_manager_deferred()
        # Placeholder attributes to prevent AttributeError
        self.chatHistory = None
        self.chatInput = None
        self.sendBtn = None
        self.morpheus = None
        self.morpheus_manager = None
        self.chat_dock = None
        
        # Setup menu system (must come after all managers are initialized)
        self.menu_manager.setup_menus()
        
        # Setup toolbar
        self._setup_toolbar()
        
        # Setup connections
        self._setup_connections()
        
        print("[OK] UI setup complete with all managers")
    
    def _setup_toolbar(self):
        """Setup complete toolbar with custom PNG icons"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QtCore.QSize(20, 20))
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        
        toolbar.addAction(self._create_action("📄", "New File (Ctrl+N)", lambda: self.file_manager.new_file(), icon_file="new_file.png"))
        toolbar.addAction(self._create_action("📁", "Open File (Ctrl+O)", lambda: self.file_manager.open_file(), icon_file="open.png"))
        toolbar.addAction(self._create_action("🗂", "Open Folder (Ctrl+Shift+O)", lambda: self.file_manager.open_folder(), icon_file="open_folder.png"))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("💾", "Save (Ctrl+S)", lambda: self.file_manager.save_file(), icon_file="save.png"))
        toolbar.addAction(self._create_action("📝", "Save As (Ctrl+Shift+S)", lambda: self.file_manager.save_file_as(), icon_file="save_as.png"))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("↶", "Undo (Ctrl+Z)", self.menu_manager._undo))
        toolbar.addAction(self._create_action("↷", "Redo (Ctrl+Y)", self.menu_manager._redo))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("🤖", "Morpheus AI Chat", self._show_morpheus_chat, icon_file="morpheus.png"))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("✓", "Syntax Check (F7)", self.menu_manager._syntax_check))
        toolbar.addAction(self._create_action("▶️", "Run Script (F5)", self.menu_manager._run_script, icon_file="run.png"))
        
    def _create_action(self, icon_text, tooltip, slot, icon_file=None):
        """Helper to create toolbar actions with VS Code style white icons"""
        if icon_file:
            # Try to load custom icon from assets folder
            icon_path = os.path.join(os.path.dirname(__file__), "assets", icon_file)
            if os.path.exists(icon_path):
                # Load and resize icon to match toolbar size (18x18 to match emoji icons)
                pixmap = QtGui.QPixmap(icon_path)
                scaled_pixmap = pixmap.scaled(18, 18, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                icon = QtGui.QIcon(scaled_pixmap)
                action = QtGui.QAction(icon, "", self)
                action.setToolTip(tooltip)
                action.triggered.connect(slot)
                return action
            else:
                # Fall back to text icon if file not found
                print(f"[Warning] Icon file not found: {icon_path}, using text fallback")
        
        # Default: use text icon with white color for VS Code style
        action = QtGui.QAction(icon_text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(slot)
        
        # Apply white icon styling
        font = QtGui.QFont()
        font.setPointSize(14)
        action.setFont(font)
        
        return action

    def _setup_connections(self):
        """Setup all connections"""
        self.languageCombo.currentTextChanged.connect(self.file_manager.on_language_changed)
        self.tabWidget.tabCloseRequested.connect(self.file_manager.close_tab)
        self.tabWidget.currentChanged.connect(self._on_tab_changed_mark_dirty)
        self.explorerView.doubleClicked.connect(lambda index: self.file_manager.on_explorer_double_clicked(index, self.fileModel))
        self.problemsList.itemDoubleClicked.connect(self._on_problem_double_clicked)
        
        # Create initial tab (will be removed if session is restored)
        self.file_manager.new_file()
    
    def _on_tab_changed_mark_dirty(self, index):
        """Called when tab changes - mark session dirty and forward to file manager"""
        self._session_dirty = True
        self.file_manager.on_tab_changed(index)
    
    def _mark_session_dirty(self):
        """Mark session as dirty (needs saving)"""
        self._session_dirty = True
        
    def _show_morpheus_chat(self):
        """Show Morpheus AI chat"""
        if hasattr(self.dock_manager, 'chat_dock') and self.dock_manager.chat_dock:
            self.dock_manager.chat_dock.setVisible(True)
            self.dock_manager.chat_dock.raise_()
        else:
            print("[Warning] Morpheus chat dock not initialized")

    def _update_problems(self, problems):
        """Update the problems list with linting results from the editor that sent the signal.
        
        This method stores problems for each editor and displays only the current tab's problems.
        """
        try:
            if not hasattr(self, 'problemsList') or not self.problemsList:
                print("⚠️ Problems list not available")
                return
            
            # CRITICAL FIX: Get the SENDER editor (the one that emitted the signal)
            # NOT the current widget (which might be a different tab)
            sender_editor = self.sender()
            if not sender_editor:
                print("⚠️ No sender editor found for problems signal")
                return
            
            # Get a unique identifier for this editor (use object id)
            editor_id = id(sender_editor)
            
            # Find the tab that contains this editor
            tab_text = "Unknown File"
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i) == sender_editor:
                    tab_text = self.tabWidget.tabText(i)
                    break
            
            # Check if problems actually changed (avoid redundant updates)
            old_problems = self.editor_problems.get(editor_id, [])
            if old_problems == problems:
                # No change, don't update to avoid flashing
                return
            
            # Update problems for this specific editor with filename (make copies to avoid mutation)
            problems_copy = []
            for problem in problems:
                problem_copy = problem.copy()
                problem_copy['file'] = tab_text if tab_text != "untitled" else "Current File"
                problem_copy['editor_id'] = editor_id
                problems_copy.append(problem_copy)
            
            # Store problems for this editor (replaces old problems from same editor)
            self.editor_problems[editor_id] = problems_copy
            
            # Only refresh if this is the current tab
            current_editor = self.tabWidget.currentWidget()
            if current_editor == sender_editor:
                self._refresh_current_tab_problems()
                
        except Exception as e:
            print(f"❌ Error updating problems: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.statusBar().showMessage("Error updating problems list")
            except:
                pass
    
    def _refresh_current_tab_problems(self):
        """Refresh the problems display with only the current tab's problems."""
        try:
            if not hasattr(self, 'problemsList') or not self.problemsList:
                return
            
            # Get the current editor
            current_editor = self.tabWidget.currentWidget()
            if not current_editor:
                self.problemsList.clear()
                self.statusBar().showMessage("No problems detected")
                return
            
            # Get problems for this editor only
            editor_id = id(current_editor)
            current_problems = self.editor_problems.get(editor_id, [])
            
            # Clear and repopulate the problems list with ONLY current tab's problems
            self.problemsList.clear()
            
            for problem in current_problems:
                # Create tree widget item with proper columns
                item = QtWidgets.QTreeWidgetItem()
                
                # Set the columns: Type, Message, Line, File
                item.setText(0, problem.get('type', 'Error'))
                item.setText(1, problem.get('message', 'Unknown error'))
                item.setText(2, str(problem.get('line', 0)))
                item.setText(3, problem.get('file', 'Current File'))
                
                # Store line number and editor_id as user data for navigation
                item.setData(2, QtCore.Qt.UserRole, problem.get('line', 0))
                item.setData(3, QtCore.Qt.UserRole, problem.get('editor_id'))
                
                # Set error icon and color
                if problem.get('type') == 'Error':
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor("#f48771")))
                else:
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor("#ffcc02")))
                
                self.problemsList.addTopLevelItem(item)
            
            # Update status bar with count for CURRENT TAB ONLY
            error_count = len([p for p in current_problems if p.get('type') == 'Error'])
            warning_count = len([p for p in current_problems if p.get('type') == 'Warning'])
            
            if error_count > 0 or warning_count > 0:
                status = f"Problems: {error_count} errors, {warning_count} warnings"
                self.statusBar().showMessage(status)
            else:
                self.statusBar().showMessage("No problems detected")
                
        except Exception as e:
            print(f"❌ Error refreshing current tab problems: {e}")
    
    def _refresh_all_problems(self):
        """Refresh the problems display with all problems from all open editors."""
        try:
            if not hasattr(self, 'problemsList') or not self.problemsList:
                return
            
            # Aggregate all problems from all open editors
            all_problems = []
            for editor_id, editor_problems in self.editor_problems.items():
                all_problems.extend(editor_problems)
            
            # Clear and repopulate the problems list
            self.problemsList.clear()
            
            for problem in all_problems:
                # Create tree widget item with proper columns
                item = QtWidgets.QTreeWidgetItem()
                
                # Set the columns: Type, Message, Line, File
                item.setText(0, problem.get('type', 'Error'))
                item.setText(1, problem.get('message', 'Unknown error'))
                item.setText(2, str(problem.get('line', 0)))
                item.setText(3, problem.get('file', 'Current File'))
                
                # Store line number and editor_id as user data for navigation
                item.setData(2, QtCore.Qt.UserRole, problem.get('line', 0))
                item.setData(3, QtCore.Qt.UserRole, problem.get('editor_id'))
                
                # Set error icon and color
                if problem.get('type') == 'Error':
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor("#f48771")))
                else:
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor("#ffcc02")))
                
                self.problemsList.addTopLevelItem(item)
            
            # Update status bar with count
            error_count = len([p for p in all_problems if p.get('type') == 'Error'])
            warning_count = len([p for p in all_problems if p.get('type') == 'Warning'])
            
            if error_count > 0 or warning_count > 0:
                status = f"Problems: {error_count} errors, {warning_count} warnings"
                self.statusBar().showMessage(status)
            else:
                self.statusBar().showMessage("No problems detected")
                
        except Exception as e:
            print(f"❌ Error refreshing problems: {e}")

    def _on_problem_double_clicked(self, item, column):
        """Navigate to the line when a problem is double-clicked"""
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
            
            # Get the editor_id from the item data (column 3)
            editor_id = item.data(3, QtCore.Qt.UserRole)
            
            # Find the editor widget by ID and switch to its tab
            target_editor = None
            if editor_id:
                for i in range(self.tabWidget.count()):
                    editor = self.tabWidget.widget(i)
                    if id(editor) == editor_id:
                        target_editor = editor
                        self.tabWidget.setCurrentIndex(i)
                        break
            
            # If we couldn't find by ID, use current editor as fallback
            if not target_editor:
                target_editor = self.chat_manager.get_active_editor()
            
            if not target_editor:
                return
            
            # Navigate to the line using block number (0-indexed)
            cursor = target_editor.textCursor()
            block = target_editor.document().findBlockByNumber(line_num - 1)
            
            if block.isValid():
                cursor.setPosition(block.position())
                target_editor.setTextCursor(cursor)
                target_editor.setFocus()
                target_editor.centerCursor()
            
        except Exception as e:
            print(f"Error navigating to problem: {e}")
    
    def _setup_status_bar(self):
        """Setup status bar with beta information"""
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #21262d;
                color: #8b949e;
                border-top: 1px solid #30363d;
                font-size: 10pt;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Add beta status message
        beta_msg = self.beta_manager.get_status_bar_message()
        if beta_msg:
            self.statusBar().showMessage(beta_msg)
            
            # Update status bar periodically (check daily)
            self.status_timer = QtCore.QTimer()
            self.status_timer.timeout.connect(self._update_status_bar)
            self.status_timer.start(86400000)  # 24 hours in milliseconds
    
    def _update_status_bar(self):
        """Update status bar with current beta info"""
        beta_msg = self.beta_manager.get_status_bar_message()
        if beta_msg:
            self.statusBar().showMessage(beta_msg)
    
    def closeEvent(self, event):
        """Save session before closing and stop auto-save timer"""
        print("[Session] closeEvent triggered")
        self._save_session()
        # Stop the auto-save timer when closing
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
            self.auto_save_timer.stop()
            print("[Session] Auto-save timer stopped (window closed)")
        event.accept()
    
    def hideEvent(self, event):
        """Save session when window is hidden and stop auto-save timer (important for Maya)"""
        print("[Session] hideEvent triggered")
        self._save_session()
        # Stop the auto-save timer when hidden
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
            self.auto_save_timer.stop()
            print("[Session] Auto-save timer stopped (window hidden)")
        super().hideEvent(event)
    
    def showEvent(self, event):
        """Called when window is shown - restart auto-save timer"""
        super().showEvent(event)
        # Restart the auto-save timer when window is shown
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
            self.auto_save_timer.start(180000)  # 3 minutes
            print("[Session] Auto-save timer restarted (window shown)")
    
    def moveEvent(self, event):
        """Optimize performance during window move"""
        # Temporarily disable updates on child widgets during move for better performance
        super().moveEvent(event)
    
    def resizeEvent(self, event):
        """Optimize performance during window resize"""
        # Qt handles most optimization automatically, just call parent
        super().resizeEvent(event)
    
    def _save_session(self, auto_save=False):
        """Save current open tabs and content to settings
        
        Args:
            auto_save: If True, this is an automatic background save (less verbose, checks dirty flag)
        """
        try:
            # Skip if window is not visible (closed/hidden)
            if not self.isVisible():
                if not auto_save:
                    print("[Session] Window not visible, skipping session save")
                return
            
            # For auto-save, skip if nothing changed (performance optimization)
            if auto_save and not getattr(self, '_session_dirty', False):
                return  # Silent skip - no changes to save
            
            # Safety check: make sure widgets still exist
            if not hasattr(self, 'tabWidget') or self.tabWidget is None:
                if not auto_save:
                    print("[Session] TabWidget not available, skipping session save")
                return
            
            # Additional Qt object validity check
            try:
                # Test if the C++ object is still valid
                _ = self.tabWidget.count()
            except RuntimeError:
                if not auto_save:
                    print("[Session] TabWidget C++ object deleted, skipping session save")
                return
            
            settings = QtCore.QSettings("AI_Script_Editor", "session")
            
            # Clear all old session data first
            settings.clear()
            
            # Save tab count and active tab
            tab_count = self.tabWidget.count()
        
            # Save explorer state (root path)
            if hasattr(self, 'explorerView') and hasattr(self, 'fileModel'):
                root_index = self.explorerView.rootIndex()
                root_path = self.fileModel.filePath(root_index)
                settings.setValue("explorer_root_path", root_path)
                if not auto_save:
                    print(f"[Session] Explorer root: {root_path}")
            
            if not auto_save:
                print(f"[Session] Saving tabs from {tab_count} total tabs...")
            
            # Save each tab's state
            saved_count = 0
            for i in range(tab_count):
                editor = self.tabWidget.widget(i)
                if isinstance(editor, CodeEditor):
                    content = editor.toPlainText()
                    # Get file path from our tracking dictionary
                    file_path = self.tab_file_paths.get(i, "")
                    
                    # Skip empty untitled tabs - don't save them to session
                    if not content.strip() and not file_path:
                        if not auto_save:
                            print(f"  Tab {i}: Skipping empty untitled tab")
                        continue
                    
                    # Save tab data
                    settings.setValue(f"tab_{saved_count}_file_path", file_path)
                    settings.setValue(f"tab_{saved_count}_language", editor.language)
                    settings.setValue(f"tab_{saved_count}_content", content)
                    settings.setValue(f"tab_{saved_count}_title", self.tabWidget.tabText(i))
                    
                    # Save cursor position
                    cursor = editor.textCursor()
                    settings.setValue(f"tab_{saved_count}_cursor_position", cursor.position())
                    
                    if not auto_save:
                        print(f"  Tab {saved_count}: '{self.tabWidget.tabText(i)}' - {len(content)} chars, file: {file_path or 'untitled'}")
                    saved_count += 1
            
            # Save the actual count of saved tabs (not including skipped empty tabs)
            settings.setValue("tab_count", saved_count)
            settings.setValue("active_tab", min(self.tabWidget.currentIndex(), saved_count - 1) if saved_count > 0 else 0)
            
            settings.sync()  # Force write to disk
            
            # Clear dirty flag after successful save
            self._session_dirty = False
            
            if not auto_save:
                print(f"[Session] Saved {saved_count} tabs successfully to: {settings.fileName()}")
            
        except Exception as e:
            if not auto_save:
                print(f"[Session] Error saving session: {e}")
            # Don't crash the application if session saving fails
    
    def _restore_session(self):
        """Restore tabs from previous session"""
        settings = QtCore.QSettings("AI_Script_Editor", "session")
        
        print(f"[Session] Loading from: {settings.fileName()}")
        
        tab_count = settings.value("tab_count", 0, type=int)
        print(f"[Session] Found {tab_count} tabs to restore")
        
        if tab_count == 0:
            print("[Session] No previous session found")
            return
        
        # Close the default untitled tab if it's empty
        if self.tabWidget.count() == 1:
            first_editor = self.tabWidget.widget(0)
            if isinstance(first_editor, CodeEditor) and not first_editor.toPlainText().strip():
                self.tabWidget.removeTab(0)
        
        # Restore each tab
        restored_count = 0
        for i in range(tab_count):
            file_path = settings.value(f"tab_{i}_file_path", "")
            language = settings.value(f"tab_{i}_language", "python")
            content = settings.value(f"tab_{i}_content", "")
            title = settings.value(f"tab_{i}_title", f"untitled_{i+1}")
            cursor_pos = settings.value(f"tab_{i}_cursor_position", 0, type=int)
            
            print(f"  Tab {i}: '{title}' - {len(content)} chars, file: {file_path or 'untitled'}")
            
            # Skip tabs with no content AND no file path (truly empty untitled tabs)
            if not content.strip() and not file_path:
                print(f"    Skipping empty untitled tab {i}")
                continue
            
            # Create new tab
            if file_path and os.path.exists(file_path):
                # Restore file tab
                print(f"    Opening file: {file_path}")
                self.file_manager.open_file(file_path)
                # File path will be tracked automatically by open_file
            else:
                # Restore untitled tab with content
                print(f"    Creating untitled tab with {len(content)} chars")
                self.file_manager.new_file(language=language)
                new_index = self.tabWidget.count() - 1
                editor = self.tabWidget.widget(new_index)
                if isinstance(editor, CodeEditor):
                    editor.setPlainText(content)
                    self.tabWidget.setTabText(new_index, title)
                    
                    # Restore cursor position
                    cursor = editor.textCursor()
                    cursor.setPosition(min(cursor_pos, len(content)))
                    editor.setTextCursor(cursor)
                    
                    # Track file path if it exists (even though file doesn't exist anymore)
                    if file_path:
                        self.tab_file_paths[new_index] = file_path
            
            restored_count += 1
        
        # Restore active tab
        active_tab = settings.value("active_tab", 0, type=int)
        if 0 <= active_tab < self.tabWidget.count():
            self.tabWidget.setCurrentIndex(active_tab)
        
        # Restore explorer state
        explorer_root_path = settings.value("explorer_root_path", "")
        if explorer_root_path and os.path.exists(explorer_root_path):
            if hasattr(self, 'explorerView') and hasattr(self, 'fileModel'):
                self.explorerView.setRootIndex(self.fileModel.index(explorer_root_path))
                print(f"[Session] Restored explorer root: {explorer_root_path}")
        
        print(f"[Session] Restored {restored_count} tabs")


def main():
    """Main entry point with single-instance check"""
    import sys
    import time
    
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # Close any existing NEO windows before creating new one
    closed_any = False
    for widget in app.allWidgets():
        if widget.__class__.__name__ == "AiScriptEditor":
            try:
                print("[INFO] Closing existing NEO window...")
                widget.close()
                widget.deleteLater()
                closed_any = True
            except:
                pass
    
    # Wait for windows to fully close
    if closed_any:
        app.processEvents()
        time.sleep(0.1)
    
    # Create and show new window
    window = AiScriptEditor()
    window.show()
    
    if __name__ == "__main__":
        return app.exec()
    else:
        return window


if __name__ == "__main__":
    main()
