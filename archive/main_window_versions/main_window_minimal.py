# ai_script_editor/main_window.py
"""
AI Script Editor - Modular Main Window
Clean, optimized main window using component modules
"""
import os
from PySide6 import QtCore, QtGui, QtWidgets

# Load OpenAI key early
settings = QtCore.QSettings("AI_Script_Editor", "settings")
stored_key = settings.value("OPENAI_API_KEY", "")
if stored_key:
    os.environ["OPENAI_API_KEY"] = stored_key

# Import component modules
from ui.components import UIManager, FileManager, SyntaxManager, AIManager

DARK_STYLE = """
QWidget { background: #1E1E1E; color: #DDD; font-family: Consolas; }
QMenuBar, QToolBar { background-color:#2D2D30; }
QTextEdit { border: 1px solid #333; background: #252526; }
QPushButton { background: #2D2D30; color: #EEE; border-radius: 4px; padding: 4px 8px; }
QPushButton:hover { background: #3E3E42; }
QTabBar::tab { background: #2D2D30; color: #DDD; padding: 6px 12px; }
QTabBar::tab:selected { background: #3E3E42; }
"""


class AiScriptEditor(QtWidgets.QMainWindow):
    """Modular AI Script Editor - Clean and Fast."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEO Script Editor v2.2 - Modular")
        self.resize(1200, 700)
        self.setStyleSheet(DARK_STYLE)
        
        # Initialize component managers
        self._init_managers()
        
        # Setup UI and connections
        self._setup_ui()
        self._setup_connections()
        
    def _init_managers(self):
        """Initialize all component managers."""
        self.ui_manager = UIManager(self)
        self.file_manager = FileManager(self)
        self.syntax_manager = SyntaxManager(self)
        self.ai_manager = AIManager(self)
        
    def _setup_ui(self):
        """Setup UI using component managers."""
        # Setup all UI components in correct order
        self.ui_manager.setup_ui()
        
        # Create initial tab (only if tabWidget exists)
        if hasattr(self, 'tabWidget'):
            self.file_manager.new_tab()
        
    def _setup_connections(self):
        """Setup signal connections."""
        # Setup AI manager connections (includes chat key press handling)
        self.ai_manager.setup_connections()
        
        # Tab widget connections
        if hasattr(self, 'tabWidget'):
            self.tabWidget.tabCloseRequested.connect(self.file_manager._close_tab)
            self.tabWidget.currentChanged.connect(self.file_manager._on_tab_changed)
        
        # Language selector
        if hasattr(self, 'languageCombo'):
            self.languageCombo.currentTextChanged.connect(self.file_manager._language_changed)
        
        # Explorer double-click
        if hasattr(self, 'explorerView'):
            self.explorerView.doubleClicked.connect(self.file_manager._on_explorer_double_clicked)


# Entry point
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    window.show()
    return app.exec()


if __name__ == "__main__":
    main()