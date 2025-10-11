"""
Dock Manager
Handles all dock widget creation and visibility management
"""
import os
from PySide6 import QtWidgets, QtCore


class DockManager:
    """Manages all dock widgets (Console, Problems, Explorer, Chat)"""
    
    def __init__(self, parent):
        """
        Initialize DockManager
        
        Args:
            parent: Main window instance
        """
        self.parent = parent
        self.console_dock = None
        self.problems_dock = None
        self.explorer_dock = None
        self.chat_dock = None
        
        # References to widgets
        self.console = None
        self.problemsList = None
        self.explorerView = None
        self.fileModel = None
        
    def setup_docks(self):
        """Setup all dock widgets"""
        self.build_console_dock()
        self.build_problems_dock()
        self.build_explorer_dock()
        # Chat dock is built by ChatManager
    
    def build_console_dock(self):
        """Build output console dock"""
        try:
            from ui.output_console import OutputConsole
            self.console = OutputConsole()
            # Note: enable_output_capture() disabled to prevent app freezing issues
            self.console.append_tagged("INFO", "🌟 NEO Script Editor Console - Enhanced with PySide6/Qt Intelligence!", "#58a6ff")
            self.console.append_tagged("SUCCESS", "[OK] Advanced syntax highlighting with complete PySide6/Qt support enabled", "#28a745")
            self.console.append_tagged("SUCCESS", "[OK] Real-time error detection with VSCode-style problem indicators active", "#28a745")
        except Exception as e:
            print(f"[!] OutputConsole initialization failed: {e}, using fallback")
            self.console = QtWidgets.QTextEdit()
            self.console.setPlainText("Console ready (fallback mode)")
            
        self.console_dock = QtWidgets.QDockWidget("Output Console", self.parent)
        self.console_dock.setObjectName("ConsoleDock")
        self.console_dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.console_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        self.console_dock.setWidget(self.console)
        self.console_dock.visibilityChanged.connect(self.sync_console_action)
        self.parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.console_dock)
        
    def build_problems_dock(self):
        """Build problems dock"""
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
        
        self.problems_dock = QtWidgets.QDockWidget("Problems", self.parent)
        self.problems_dock.setObjectName("ProblemsDock")
        self.problems_dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.problems_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        self.problems_dock.setWidget(self.problemsList)
        self.problems_dock.visibilityChanged.connect(self.sync_problems_action)
        self.parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.problems_dock)
        
    def build_explorer_dock(self):
        """Build file explorer dock"""
        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setRootPath("")
        
        self.explorerView = QtWidgets.QTreeView()
        self.explorerView.setModel(self.fileModel)
        self.explorerView.setRootIndex(self.fileModel.index(os.getcwd()))
        
        self.explorerView.hideColumn(1)  # Size
        self.explorerView.hideColumn(2)  # Type  
        self.explorerView.hideColumn(3)  # Date Modified
        
        self.explorer_dock = QtWidgets.QDockWidget("Explorer", self.parent)
        self.explorer_dock.setObjectName("ExplorerDock")
        self.explorer_dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.explorer_dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        self.explorer_dock.setWidget(self.explorerView)
        self.explorer_dock.visibilityChanged.connect(self.sync_explorer_action)
        self.parent.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.explorer_dock)
    
    def toggle_dock(self, dock_name):
        """Toggle visibility of a specific dock panel"""
        dock_map = {
            "ExplorerDock": (self.explorer_dock, self.parent.menu_manager.toggle_explorer_action),
            "MorpheusDock": (self.chat_dock, self.parent.menu_manager.toggle_morpheus_action),
            "ConsoleDock": (self.console_dock, self.parent.menu_manager.toggle_console_action),
            "ProblemsDock": (self.problems_dock, self.parent.menu_manager.toggle_problems_action)
        }
        
        if dock_name in dock_map:
            dock, action = dock_map[dock_name]
            is_visible = dock.isVisible()
            dock.setVisible(not is_visible)
            action.setChecked(not is_visible)
    
    def hide_all_panels(self):
        """Hide all dock panels to maximize editor space"""
        self.explorer_dock.hide()
        if self.chat_dock:
            self.chat_dock.hide()
        self.console_dock.hide()
        self.problems_dock.hide()
        
        self.parent.menu_manager.toggle_explorer_action.setChecked(False)
        self.parent.menu_manager.toggle_morpheus_action.setChecked(False)
        self.parent.menu_manager.toggle_console_action.setChecked(False)
        self.parent.menu_manager.toggle_problems_action.setChecked(False)
    
    def show_all_panels(self):
        """Show all dock panels"""
        self.explorer_dock.show()
        if self.chat_dock:
            self.chat_dock.show()
        self.console_dock.show()
        self.problems_dock.show()
        
        self.parent.menu_manager.toggle_explorer_action.setChecked(True)
        self.parent.menu_manager.toggle_morpheus_action.setChecked(True)
        self.parent.menu_manager.toggle_console_action.setChecked(True)
        self.parent.menu_manager.toggle_problems_action.setChecked(True)
    
    def sync_explorer_action(self, visible):
        """Keep Explorer menu item in sync with dock visibility"""
        if hasattr(self.parent, 'menu_manager') and self.parent.menu_manager.toggle_explorer_action:
            self.parent.menu_manager.toggle_explorer_action.setChecked(visible)
    
    def sync_morpheus_action(self, visible):
        """Keep Morpheus AI menu item in sync with dock visibility"""
        if hasattr(self.parent, 'menu_manager') and self.parent.menu_manager.toggle_morpheus_action:
            self.parent.menu_manager.toggle_morpheus_action.setChecked(visible)
    
    def sync_console_action(self, visible):
        """Keep Output Console menu item in sync with dock visibility"""
        if hasattr(self.parent, 'menu_manager') and self.parent.menu_manager.toggle_console_action:
            self.parent.menu_manager.toggle_console_action.setChecked(visible)
    
    def sync_problems_action(self, visible):
        """Keep Problems menu item in sync with dock visibility"""
        if hasattr(self.parent, 'menu_manager') and self.parent.menu_manager.toggle_problems_action:
            self.parent.menu_manager.toggle_problems_action.setChecked(visible)
