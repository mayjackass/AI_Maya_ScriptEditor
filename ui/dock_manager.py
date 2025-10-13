"""
Dock Manager
Handles all dock widget creation and visibility management
"""
import os
from PySide6 import QtWidgets, QtCore, QtGui


class VSCodeStyleDelegate(QtWidgets.QStyledItemDelegate):
    """Custom delegate for VSCode-style tree items with file type icons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load icons from assets folder
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        
        # Load actual icon files from assets
        self.python_icon = QtGui.QIcon(os.path.join(assets_path, "python.png"))
        self.mel_icon = QtGui.QIcon(os.path.join(assets_path, "mel.png"))
        self.markdown_icon = QtGui.QIcon(os.path.join(assets_path, "mark-down.png"))
        self.image_icon = QtGui.QIcon(os.path.join(assets_path, "image.png"))
        self.file_icon = QtGui.QIcon(os.path.join(assets_path, "file.png"))  # Default file icon
        self.archive_icon = QtGui.QIcon(os.path.join(assets_path, "archive.png"))  # Archive files
        self.exe_icon = QtGui.QIcon(os.path.join(assets_path, "exe.png"))  # Executable files
        
        # VSCode-style file type icons (using Unicode symbols for types without custom icons)
        self.file_icons = {
            '.json': ('{}', QtGui.QColor(255, 215, 0)),     # JSON
            '.xml': ('<>', QtGui.QColor(255, 140, 0)),      # XML
            '.html': ('🌐', QtGui.QColor(227, 76, 38)),     # HTML
            '.css': ('🎨', QtGui.QColor(86, 156, 214)),     # CSS
            '.js': ('JS', QtGui.QColor(240, 219, 79)),      # JavaScript
            '.ps1': ('💻', QtGui.QColor(0, 122, 204)),      # PowerShell
            '.sh': ('💻', QtGui.QColor(76, 175, 80)),       # Shell
        }
    
    def paint(self, painter, option, index):
        """Custom paint with chevrons and file type icons"""
        # Get the model
        model = index.model()
        
        # Check if this is a directory
        file_info = model.fileInfo(index)
        is_dir = file_info.isDir()
        
        # Draw background
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, QtGui.QColor(51, 51, 51))  # Gray selection
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(option.rect, QtGui.QColor(42, 45, 46))  # VSCode hover color
        
        # Setup text color
        painter.setPen(QtGui.QColor(204, 204, 204))  # VSCode text color
        
        left_offset = 2
        
        # Draw chevron for directories (no folder icon)
        if is_dir:
            tree_view = option.widget
            is_expanded = tree_view.isExpanded(index) if tree_view else False
            
            # Draw chevron (▶ or ▼)
            chevron_rect = QtCore.QRect(option.rect.left() + left_offset, option.rect.top(), 16, option.rect.height())
            painter.save()
            painter.setPen(QtGui.QColor(150, 150, 150))
            painter.setFont(QtGui.QFont("Segoe UI", 8))
            
            if is_expanded:
                # Down chevron
                painter.drawText(chevron_rect, QtCore.Qt.AlignCenter, "▼")
            else:
                # Right chevron
                painter.drawText(chevron_rect, QtCore.Qt.AlignCenter, "▶")
            
            painter.restore()
            
            text_offset = 20
        else:
            # Get file extension and corresponding icon
            filename = file_info.fileName()
            ext = os.path.splitext(filename)[1].lower()
            
            icon_rect = QtCore.QRect(option.rect.left() + left_offset + 16, option.rect.top() + 3, 16, 16)
            
            # Check for files with custom icons from assets
            if ext == '.py':
                # Python icon
                self.python_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext == '.mel':
                # MEL icon
                self.mel_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext == '.md':
                # Markdown icon
                self.markdown_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico']:
                # Image icon
                self.image_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext in ['.txt', '.log', '.ini', '.cfg', '.conf']:
                # Generic file icon for text files
                self.file_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
                # Archive icon
                self.archive_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext in ['.exe', '.bat', '.cmd', '.msi']:
                # Executable icon
                self.exe_icon.paint(painter, icon_rect)
                text_offset = 38
            elif ext in self.file_icons:
                # Use Unicode icon for special file types
                icon_data = self.file_icons[ext]
                icon_char, icon_color = icon_data
                
                icon_rect_text = QtCore.QRect(option.rect.left() + left_offset + 16, option.rect.top(), 18, option.rect.height())
                painter.save()
                painter.setPen(icon_color)
                painter.setFont(QtGui.QFont("Segoe UI", 10))
                painter.drawText(icon_rect_text, QtCore.Qt.AlignCenter, icon_char)
                painter.restore()
                
                text_offset = 38
            else:
                # Default file icon for unknown types
                self.file_icon.paint(painter, icon_rect)
                text_offset = 38
        
        # Draw text (filename)
        text_rect = QtCore.QRect(option.rect.left() + text_offset, option.rect.top(), 
                                option.rect.width() - text_offset, option.rect.height())
        text = index.data(QtCore.Qt.DisplayRole)
        painter.setPen(QtGui.QColor(204, 204, 204))
        painter.drawText(text_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, text)
    
    def sizeHint(self, option, index):
        """Return size hint for items"""
        size = super().sizeHint(option, index)
        size.setHeight(22)  # Fixed height like VSCode
        return size


class VSCodeTreeView(QtWidgets.QTreeView):
    """Custom TreeView with VSCode-style click behavior"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        """Handle mouse press to toggle expand/collapse on single click"""
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                model = self.model()
                file_info = model.fileInfo(index)
                
                # If it's a directory, toggle expand/collapse
                if file_info.isDir():
                    if self.isExpanded(index):
                        self.collapse(index)
                    else:
                        self.expand(index)
                    # Still select the item
                    self.setCurrentIndex(index)
                    return
        
        # For files or other buttons, use default behavior
        super().mousePressEvent(event)


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
            self.console.append_tagged("INFO", "🌟 NEO Script Editor Console - Enhanced with PySide6/Qt Intelligence!", "#00ff41")
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
        """Build file explorer dock with VSCode-style hierarchy"""
        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setRootPath("")
        
        # Use custom tree view with VSCode-style click behavior
        self.explorerView = VSCodeTreeView()
        self.explorerView.setModel(self.fileModel)
        self.explorerView.setRootIndex(self.fileModel.index(os.getcwd()))
        
        self.explorerView.hideColumn(1)  # Size
        self.explorerView.hideColumn(2)  # Type  
        self.explorerView.hideColumn(3)  # Date Modified
        
        # Use custom delegate for VSCode-style appearance (no icons, custom chevrons)
        self.explorerView.setItemDelegate(VSCodeStyleDelegate(self.explorerView))
        
        # Remove default icons
        self.explorerView.setIconSize(QtCore.QSize(0, 0))
        
        # VSCode-style appearance
        self.explorerView.setIndentation(16)  # Compact indentation like VSCode
        self.explorerView.setAnimated(True)  # Smooth expand/collapse
        self.explorerView.setHeaderHidden(True)  # Hide header for cleaner look
        self.explorerView.setRootIsDecorated(False)  # Hide default arrows (we draw custom chevrons)
        self.explorerView.setExpandsOnDoubleClick(False)  # Single-click to expand/collapse (like VSCode)
        self.explorerView.setUniformRowHeights(True)  # Better performance
        
        # VSCode Dark+ theme styling with gray selection
        self.explorerView.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                color: #cccccc;
                border: none;
                outline: none;
                font-size: 13px;
                font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
            }
            QTreeView::item {
                padding: 4px 4px;
                border: none;
                height: 22px;
            }
            QTreeView::item:hover {
                background-color: #2a2d2e;
            }
            QTreeView::item:selected {
                background-color: #333333;
                color: #ffffff;
            }
            QTreeView::item:selected:active {
                background-color: #333333;
            }
            QTreeView::item:selected:!active {
                background-color: #2d2d2d;
            }
        """)
        
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
