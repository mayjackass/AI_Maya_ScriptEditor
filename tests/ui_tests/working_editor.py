#!/usr/bin/env python3
"""
Working AI Script Editor - Modular Version
Uses the working managers with a complete but stable UI
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from PySide6 import QtWidgets, QtCore, QtGui

# Import our working managers
from ui.components.ui_manager import UIManager
from ui.components.file_manager import FileManager  
from ui.components.syntax_manager import SyntaxManager
from ui.components.ai_manager import AIManager

# Import the enhanced editor
from editor.code_editor import CodeEditor

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

class WorkingAIEditor(QtWidgets.QMainWindow):
    """Working AI Script Editor with all modular components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 AI Script Editor v2.2 - Modular (Working)")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(DARK_STYLE)
        
        print("🔍 Initializing modular AI Script Editor...")
        
        # Initialize managers (we know these work)
        self._init_managers()
        
        # Setup complete UI
        self._setup_complete_ui()
        
        # Setup connections
        self._setup_connections()
        
        print("✅ Modular AI Script Editor initialized successfully!")
        
    def _init_managers(self):
        """Initialize all working managers."""
        print("🔍 Initializing managers...")
        self.ui_manager = UIManager(self)
        self.file_manager = FileManager(self)
        self.syntax_manager = SyntaxManager(self)
        self.ai_manager = AIManager(self)
        print("✅ All managers initialized")
        
    def _setup_complete_ui(self):
        """Setup complete UI with all components."""
        print("🔍 Setting up complete UI...")
        
        # Create dock widgets first (needed by central widget)
        self._setup_dock_widgets()
        
        # Create central widget with tabs
        self._setup_central_widget()
        
        # Create menu bar
        self._setup_menu_bar()
        
        # Create toolbar
        self._setup_toolbar()
        
        # Status bar
        self.statusBar().showMessage("✅ AI Script Editor ready with enhanced features!")
        
        print("✅ Complete UI setup finished")
        
    def _setup_central_widget(self):
        """Setup central tabbed editor."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Language selector header
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        lang_label = QtWidgets.QLabel("Language:")
        lang_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        header_layout.addWidget(lang_label)
        
        self.languageCombo = QtWidgets.QComboBox()
        self.languageCombo.addItems(["🐍 Python", "🔧 MEL Script"])
        self.languageCombo.currentTextChanged.connect(self._on_language_changed)
        header_layout.addWidget(self.languageCombo)
        
        header_layout.addStretch()
        
        # Add buttons
        new_btn = QtWidgets.QPushButton("📄 New")
        new_btn.clicked.connect(self._new_file)
        header_layout.addWidget(new_btn)
        
        open_btn = QtWidgets.QPushButton("📁 Open")
        open_btn.clicked.connect(self._open_file)
        header_layout.addWidget(open_btn)
        
        save_btn = QtWidgets.QPushButton("💾 Save")
        save_btn.clicked.connect(self._save_file)
        header_layout.addWidget(save_btn)
        
        layout.addWidget(header_widget)
        
        # Tab widget for editors
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        layout.addWidget(self.tabWidget)
        
        # Create initial tab
        self._new_file()
        
    def _setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QtGui.QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QtGui.QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QtGui.QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QtGui.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # AI menu
        ai_menu = menubar.addMenu("AI")
        
        morpheus_action = QtGui.QAction("Chat with Morpheus", self)
        morpheus_action.triggered.connect(self._show_morpheus_chat)
        ai_menu.addAction(morpheus_action)
        
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        # File operations
        new_action = QtGui.QAction("📄", self)
        new_action.setToolTip("New File (Ctrl+N)")
        new_action.triggered.connect(self._new_file)
        toolbar.addAction(new_action)
        
        open_action = QtGui.QAction("📁", self)
        open_action.setToolTip("Open File (Ctrl+O)")
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)
        
        save_action = QtGui.QAction("💾", self)
        save_action.setToolTip("Save File (Ctrl+S)")
        save_action.triggered.connect(self._save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # AI operations
        morpheus_action = QtGui.QAction("🤖", self)
        morpheus_action.setToolTip("Chat with Morpheus AI")
        morpheus_action.triggered.connect(self._show_morpheus_chat)
        toolbar.addAction(morpheus_action)
        
    def _setup_dock_widgets(self):
        """Setup dock widgets for output, problems, etc."""
        # Output dock
        output_dock = QtWidgets.QDockWidget("Output", self)
        self.output_console = QtWidgets.QTextBrowser()
        self.output_console.append("🚀 AI Script Editor Output Console")
        self.output_console.append("✅ Enhanced syntax highlighting enabled")
        self.output_console.append("✅ Real-time error detection active")
        self.output_console.append("✅ All modular components loaded")
        output_dock.setWidget(self.output_console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, output_dock)
        
        # Problems dock
        problems_dock = QtWidgets.QDockWidget("Problems", self)
        self.problems_list = QtWidgets.QListWidget()
        problems_dock.setWidget(self.problems_list)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, problems_dock)
        
        # Explorer dock
        explorer_dock = QtWidgets.QDockWidget("Explorer", self)
        self.explorer_tree = QtWidgets.QTreeView()
        
        # Set up file system model
        self.file_model = QtWidgets.QFileSystemModel()
        self.file_model.setRootPath(os.getcwd())
        self.explorer_tree.setModel(self.file_model)
        self.explorer_tree.setRootIndex(self.file_model.index(os.getcwd()))
        self.explorer_tree.doubleClicked.connect(self._on_file_double_clicked)
        
        explorer_dock.setWidget(self.explorer_tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, explorer_dock)
        
        # Tabify bottom docks
        self.tabifyDockWidget(output_dock, problems_dock)
        output_dock.raise_()
        
    def _setup_connections(self):
        """Setup signal connections."""
        pass  # Managers handle their own connections
        
    def _new_file(self):
        """Create new file tab."""
        try:
            editor = CodeEditor()
            
            # Set language
            lang = self.languageCombo.currentText()
            if "Python" in lang:
                editor.set_language("python")
            else:
                editor.set_language("mel")
            
            # Connect signals
            if hasattr(editor, 'errorDetected'):
                editor.errorDetected.connect(self._on_error_detected)
            if hasattr(editor, 'errorsCleared'):
                editor.errorsCleared.connect(self._on_errors_cleared)
            
            # Add initial content
            if "Python" in lang:
                editor.setPlainText("""#!/usr/bin/env python3
\"\"\"
AI Script Editor - Enhanced Python Development
Features: VSCode-style syntax highlighting, real-time error detection
\"\"\"

# PySide6/Qt imports - enhanced highlighting
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Signal, Slot

# Maya imports (if available)
try:
    import maya.cmds as cmds
    print("Maya integration available")
except ImportError:
    print("Maya not available - standalone mode")

# Your Python code here...
class MyWidget(QtWidgets.QWidget):
    # Signal definition
    dataChanged = Signal(str)
    
    def __init__(self):
        super().__init__()
        print("Widget created with enhanced syntax highlighting!")

# Test the enhanced features!
""")
            else:
                editor.setPlainText("""// MEL Script - AI Script Editor
// Enhanced MEL syntax highlighting enabled

global proc myMelProcedure() {
    // Your MEL code here
    print("Enhanced MEL highlighting active!\\n");
    
    // Create some objects
    polyCube -name "testCube";
    move 0 5 0;
}

// Call the procedure
myMelProcedure();
""")
            
            index = self.tabWidget.addTab(editor, "untitled")
            self.tabWidget.setCurrentIndex(index)
            
            self.output_console.append(f"✅ New {lang.split()[1] if len(lang.split()) > 1 else 'file'} file created")
            
        except Exception as e:
            self.output_console.append(f"❌ Error creating file: {e}")
            
    def _open_file(self):
        """Open file dialog."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        )
        
        if file_path and self.file_manager:
            self.file_manager.open_file(file_path)
            
    def _save_file(self):
        """Save current file."""
        if self.file_manager:
            self.file_manager.save_current_tab()
            
    def _close_tab(self, index):
        """Close tab."""
        if self.tabWidget.count() <= 1:
            self._new_file()
        self.tabWidget.removeTab(index)
        
    def _on_language_changed(self, language):
        """Handle language change."""
        current_editor = self.tabWidget.currentWidget()
        if current_editor and hasattr(current_editor, 'set_language'):
            if "Python" in language:
                current_editor.set_language("python")
            else:
                current_editor.set_language("mel")
                
    def _on_file_double_clicked(self, index):
        """Handle file explorer double-click."""
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path) and self.file_manager:
            self.file_manager.open_file(file_path)
            
    def _on_error_detected(self, line, message):
        """Handle error detection."""
        self.problems_list.addItem(f"Line {line}: {message}")
        
    def _on_errors_cleared(self):
        """Handle errors cleared."""
        self.problems_list.clear()
        
    def _show_morpheus_chat(self):
        """Show Morpheus AI chat."""
        if hasattr(self.ai_manager, 'show_morpheus_chat'):
            self.ai_manager.show_morpheus_chat()
        else:
            self.output_console.append("🤖 Morpheus AI chat coming soon...")

def main():
    print("🚀 Starting Working AI Script Editor (Modular Version)...")
    
    app = QtWidgets.QApplication(sys.argv)
    
    window = WorkingAIEditor()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("🎯 AI Script Editor is now running!")
    print("✨ Features available:")
    print("   • Enhanced syntax highlighting with PySide6/Qt support")
    print("   • Real-time error detection with VSCode-style indicators")
    print("   • Complete modular architecture")
    print("   • File explorer, output console, problems panel")
    print("   • Maya integration support")
    print("   • Morpheus AI integration")
    
    return app.exec()

if __name__ == "__main__":
    main()