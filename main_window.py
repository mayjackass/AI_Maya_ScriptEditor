"""
AI Script Editor - Refactored Modular Version
Main window now delegates to manager modules for clean architecture
"""
import os
from PySide6 import QtWidgets, QtCore, QtGui

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
    from model.hierarchy import CodeHierarchyModel
    from ui.output_console import OutputConsole
    from ai.chat import AIMorpheus
    from ai.copilot_manager import MorpheusManager
    
    # Import all manager modules
    from ui.find_replace_manager import FindReplaceManager
    from ui.menu_manager import MenuManager
    from ui.dock_manager import DockManager
    from ui.chat_manager import ChatManager
    from ui.file_manager import FileManager
    
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
    """NEO Script Editor - Modern Maya script editor with Morpheus AI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("�️ NEO Script Editor v3.0 - Morpheus AI")
        self.resize(1200, 700)
        self.setStyleSheet(DARK_STYLE)

        # Initialize components
        self._setup_central_widget()
        self._setup_floating_code_actions()
        
        # Initialize all manager modules
        self._init_managers()
        
        # Setup UI using managers
        self._setup_ui_with_managers()
        
        # Initialize hierarchy
        self._init_hierarchy()
        
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
        self.languageCombo.addItem("🐍 Python", "Python")
        self.languageCombo.addItem("📜 MEL", "MEL") 
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
        
        # Store layout for find/replace widget (will be setup by manager)
        self.centralLayout = centralLayout
        
        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
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
    
    def _init_managers(self):
        """Initialize all manager modules"""
        # Initialize managers
        self.dock_manager = DockManager(self)
        self.file_manager = FileManager(self, self.tabWidget, self.languageCombo)
        self.find_replace_manager = FindReplaceManager(self, self.tabWidget)
        self.menu_manager = MenuManager(self)
        self.chat_manager = ChatManager(self)
        
        print("[OK] All managers initialized")
    
    def _setup_ui_with_managers(self):
        """Setup UI using manager modules"""
        # Setup find/replace widget (before docks so it's in correct position)
        self.find_replace_manager.setup_widget(self.centralLayout)
        
        # Setup dock widgets (Console, Problems, Explorer)
        self.dock_manager.setup_docks()
        
        # Make dock manager widgets available directly on main window for compatibility
        self.console = self.dock_manager.console
        self.problemsList = self.dock_manager.problemsList
        self.explorerView = self.dock_manager.explorerView
        self.fileModel = self.dock_manager.fileModel
        self.console_dock = self.dock_manager.console_dock
        self.problems_dock = self.dock_manager.problems_dock
        self.explorer_dock = self.dock_manager.explorer_dock
        
        # Setup chat dock (handled by ChatManager)
        self.chat_manager.build_chat_dock()
        
        # Make chat manager widgets available on main window
        self.chatHistory = self.chat_manager.chatHistory
        self.chatInput = self.chat_manager.chatInput
        self.sendBtn = self.chat_manager.sendBtn
        self.morpheus = self.chat_manager.morpheus
        self.morpheus_manager = self.chat_manager.morpheus_manager
        self.chat_dock = self.dock_manager.chat_dock  # Store chat dock reference
        
        # Setup menu system (must come after all managers are initialized)
        self.menu_manager.setup_menus()
        
        # Setup toolbar
        self._setup_toolbar()
        
        # Setup connections
        self._setup_connections()
        
        print("[OK] UI setup complete with all managers")
    
    def _setup_toolbar(self):
        """Setup complete toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        toolbar.addAction(self._create_action("📄", "New File (Ctrl+N)", lambda: self.file_manager.new_file()))
        toolbar.addAction(self._create_action("📁", "Open File (Ctrl+O)", lambda: self.file_manager.open_file()))
        toolbar.addAction(self._create_action("🗂", "Open Folder (Ctrl+Shift+O)", lambda: self.file_manager.open_folder()))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("💾", "Save (Ctrl+S)", lambda: self.file_manager.save_file()))
        toolbar.addAction(self._create_action("📝", "Save As (Ctrl+Shift+S)", lambda: self.file_manager.save_file_as()))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("↶", "Undo (Ctrl+Z)", self.menu_manager._undo))
        toolbar.addAction(self._create_action("↷", "Redo (Ctrl+Y)", self.menu_manager._redo))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("🤖", "Morpheus AI Chat", self._show_morpheus_chat, icon_file="morpheus.png"))
        toolbar.addSeparator()
        toolbar.addAction(self._create_action("✓", "Syntax Check (F7)", self.menu_manager._syntax_check))
        toolbar.addAction(self._create_action("▶️", "Run Script (F5)", self.menu_manager._run_script))
        
    def _create_action(self, icon_text, tooltip, slot, icon_file=None):
        """Helper to create toolbar actions"""
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
        
        # Default: use text icon
        action = QtGui.QAction(icon_text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(slot)
        return action

    def _setup_connections(self):
        """Setup all connections"""
        self.languageCombo.currentTextChanged.connect(self.file_manager.on_language_changed)
        self.tabWidget.tabCloseRequested.connect(self.file_manager.close_tab)
        self.tabWidget.currentChanged.connect(self.file_manager.on_tab_changed)
        self.explorerView.doubleClicked.connect(lambda index: self.file_manager.on_explorer_double_clicked(index, self.fileModel))
        self.problemsList.itemDoubleClicked.connect(self._on_problem_double_clicked)
        
        # Create initial tab
        self.file_manager.new_file()
        
    def _init_hierarchy(self):
        """Initialize hierarchy model"""
        try:
            self.hierarchy_model = CodeHierarchyModel()
        except Exception as e:
            print(f"Hierarchy initialization warning: {e}")

    def _show_morpheus_chat(self):
        """Show Morpheus AI chat"""
        if hasattr(self.dock_manager, 'chat_dock') and self.dock_manager.chat_dock:
            self.dock_manager.chat_dock.setVisible(True)
            self.dock_manager.chat_dock.raise_()
        else:
            print("[Warning] Morpheus chat dock not initialized")

    def _update_problems(self, problems):
        """Update the problems list with linting results"""
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
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor("#f48771")))  # Red
                else:
                    item.setForeground(0, QtGui.QBrush(QtGui.QColor("#ffcc02")))  # Yellow
                
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
            try:
                self.statusBar().showMessage("Error updating problems list")
            except:
                pass

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
            
            # Get the active editor
            editor = self.chat_manager.get_active_editor()
            if not editor:
                return
            
            # Navigate to the line
            cursor = editor.textCursor()
            block = editor.document().findBlockByLineNumber(line_num - 1)  # 0-based
            cursor.setPosition(block.position())
            editor.setTextCursor(cursor)
            editor.setFocus()
            
            # Center the cursor
            editor.centerCursor()
            
        except Exception as e:
            print(f"Error navigating to problem: {e}")


def main():
    """Main entry point"""
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    window.show()
    return app.exec()


if __name__ == "__main__":
    main()
