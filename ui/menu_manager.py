"""
Menu Manager
Handles all menu bar creation and menu actions
"""
from PySide6 import QtWidgets, QtGui, QtCore


class MenuManager:
    """Manages menu bar and all menu actions"""
    
    def __init__(self, parent):
        """
        Initialize MenuManager
        
        Args:
            parent: Main window instance (AiScriptEditor)
        """
        self.parent = parent
        
        # Store menu action references
        self.toggle_explorer_action = None
        self.toggle_morpheus_action = None
        self.toggle_console_action = None
        self.toggle_problems_action = None
        
    def setup_menus(self):
        """Setup complete menu system"""
        menubar = self.parent.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QtGui.QAction("&New", self.parent)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.parent.file_manager.new_file())
        file_menu.addAction(new_action)
        
        open_action = QtGui.QAction("&Open File...", self.parent)
        open_action.setShortcut("Ctrl+O") 
        open_action.triggered.connect(lambda: self.parent.file_manager.open_file())
        file_menu.addAction(open_action)
        
        open_folder_action = QtGui.QAction("Open &Folder...", self.parent)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(lambda: self.parent.file_manager.open_folder())
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QtGui.QAction("&Save", self.parent)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.parent.file_manager.save_file())
        file_menu.addAction(save_action)
        
        save_as_action = QtGui.QAction("Save &As...", self.parent)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(lambda: self.parent.file_manager.save_file())
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QtGui.QAction("E&xit", self.parent)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QtGui.QAction("&Undo", self.parent)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QtGui.QAction("&Redo", self.parent)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QtGui.QAction("Cu&t", self.parent)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QtGui.QAction("&Copy", self.parent)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QtGui.QAction("&Paste", self.parent)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QtGui.QAction("🔍 &Find", self.parent)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(lambda: self.parent.find_replace_manager.show_find())
        edit_menu.addAction(find_action)
        
        replace_action = QtGui.QAction("🔄 &Replace", self.parent)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(lambda: self.parent.find_replace_manager.show_replace())
        edit_menu.addAction(replace_action)
        
        find_next_action = QtGui.QAction("Find &Next", self.parent)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(lambda: self.parent.find_replace_manager.find_next())
        edit_menu.addAction(find_next_action)
        
        find_prev_action = QtGui.QAction("Find &Previous", self.parent)
        find_prev_action.setShortcut("Shift+F3")
        find_prev_action.triggered.connect(lambda: self.parent.find_replace_manager.find_previous())
        edit_menu.addAction(find_prev_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        # Add dock panel visibility toggles
        self.toggle_explorer_action = QtGui.QAction("📁 Explorer", self.parent)
        self.toggle_explorer_action.setCheckable(True)
        self.toggle_explorer_action.setChecked(True)
        self.toggle_explorer_action.setShortcut("Ctrl+Shift+E")
        self.toggle_explorer_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("ExplorerDock"))
        view_menu.addAction(self.toggle_explorer_action)
        
        # Morpheus AI with custom icon
        import os
        morpheus_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "morpheus.png")
        if os.path.exists(morpheus_icon_path):
            morpheus_icon = QtGui.QIcon(morpheus_icon_path)
            self.toggle_morpheus_action = QtGui.QAction(morpheus_icon, "Morpheus AI Chat", self.parent)
        else:
            self.toggle_morpheus_action = QtGui.QAction("🤖 Morpheus AI Chat", self.parent)
        self.toggle_morpheus_action.setCheckable(True)
        self.toggle_morpheus_action.setChecked(True)
        self.toggle_morpheus_action.setShortcut("Ctrl+Shift+M")
        self.toggle_morpheus_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("MorpheusDock"))
        view_menu.addAction(self.toggle_morpheus_action)
        
        self.toggle_console_action = QtGui.QAction("📟 Output Console", self.parent)
        self.toggle_console_action.setCheckable(True)
        self.toggle_console_action.setChecked(True)
        self.toggle_console_action.setShortcut("Ctrl+Shift+C")
        self.toggle_console_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("ConsoleDock"))
        view_menu.addAction(self.toggle_console_action)
        
        self.toggle_problems_action = QtGui.QAction("⚠️ Problems", self.parent)
        self.toggle_problems_action.setCheckable(True)
        self.toggle_problems_action.setChecked(True)
        self.toggle_problems_action.setShortcut("Ctrl+Shift+U")
        self.toggle_problems_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("ProblemsDock"))
        view_menu.addAction(self.toggle_problems_action)
        
        view_menu.addSeparator()
        
        # Add "Hide All Panels" and "Show All Panels" options
        hide_all_action = QtGui.QAction("🙈 Hide All Panels", self.parent)
        hide_all_action.setShortcut("Ctrl+Shift+H")
        hide_all_action.triggered.connect(lambda: self.parent.dock_manager.hide_all_panels())
        view_menu.addAction(hide_all_action)
        
        show_all_action = QtGui.QAction("👁️ Show All Panels", self.parent)
        show_all_action.setShortcut("Ctrl+Shift+A")
        show_all_action.triggered.connect(lambda: self.parent.dock_manager.show_all_panels())
        view_menu.addAction(show_all_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings menu item
        settings_action = QtGui.QAction("⚙️ &Settings", self.parent)
        settings_action.triggered.connect(lambda: self.parent.chat_manager.show_settings_dialog())
        tools_menu.addAction(settings_action)
        
        tools_menu.addSeparator()
        
        syntax_check_action = QtGui.QAction("&Syntax Check", self.parent)
        syntax_check_action.setShortcut("F7")
        syntax_check_action.triggered.connect(self._syntax_check)
        tools_menu.addAction(syntax_check_action)
        
        run_script_action = QtGui.QAction("&Run Script", self.parent)
        run_script_action.setShortcut("F5")
        run_script_action.triggered.connect(self._run_script)
        tools_menu.addAction(run_script_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QtGui.QAction("&About", self.parent)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    # Edit menu actions
    def _undo(self):
        """Undo action"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'undo'):
            current_widget.undo()

    def _redo(self):
        """Redo action"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'redo'):
            current_widget.redo()

    def _cut(self):
        """Cut action"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'cut'):
            current_widget.cut()

    def _copy(self):
        """Copy action"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'copy'):
            current_widget.copy()

    def _paste(self):
        """Paste action"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget and hasattr(current_widget, 'paste'):
            current_widget.paste()
    
    # Tools menu actions
    def _syntax_check(self):
        """Run syntax check on current file"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget:
            code = current_widget.toPlainText()
            try:
                compile(code, '<string>', 'exec')
                QtWidgets.QMessageBox.information(self.parent, "Syntax Check", "No syntax errors found!")
            except SyntaxError as e:
                QtWidgets.QMessageBox.warning(self.parent, "Syntax Error", f"Syntax error at line {e.lineno}: {e.msg}")
    
    def _run_script(self):
        """Run current script"""
        current_widget = self.parent.tabWidget.currentWidget()
        if current_widget:
            code = current_widget.toPlainText()
            try:
                if hasattr(self.parent.console, 'execute_code_and_capture'):
                    self.parent.console.execute_code_and_capture(code, "python")
                else:
                    exec(code)
                    print("Code executed successfully")
            except Exception as e:
                print(f"Execution error: {e}")
    
    # Help menu actions
    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(self.parent, "About NEO Script Editor", 
            """[NEO] Script Editor v2.2 - Complete Modular Edition

[*] Features:
• Complete modular architecture with ALL original features
• Enhanced syntax highlighting with PySide6/Qt support  
• Real-time error detection with VSCode-style indicators
• Comprehensive Maya Python API integration
• Morpheus AI chat integration with OpenAI & Claude
• Advanced code editor with VS Code-style find/replace
• All dock widgets: Console, Problems, Explorer, Morpheus Chat
• Complete menu system with all functionality
• Clean, optimized, and maintainable codebase

[SUCCESS] All functionalities preserved with clean, modular design!""")
