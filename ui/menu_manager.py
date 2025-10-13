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
        
        # Open Recent submenu
        self.recent_menu = file_menu.addMenu("Open &Recent")
        self.update_recent_files_menu()
        
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
        
        find_action = QtGui.QAction("&Find", self.parent)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(lambda: self.parent.find_replace_manager.show_find())
        edit_menu.addAction(find_action)
        
        replace_action = QtGui.QAction("&Replace", self.parent)
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
        self.toggle_explorer_action = QtGui.QAction("Explorer", self.parent)
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
            self.toggle_morpheus_action = QtGui.QAction("Morpheus AI Chat", self.parent)
        self.toggle_morpheus_action.setCheckable(True)
        self.toggle_morpheus_action.setChecked(True)
        self.toggle_morpheus_action.setShortcut("Ctrl+Shift+M")
        self.toggle_morpheus_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("MorpheusDock"))
        view_menu.addAction(self.toggle_morpheus_action)
        
        self.toggle_console_action = QtGui.QAction("Output Console", self.parent)
        self.toggle_console_action.setCheckable(True)
        self.toggle_console_action.setChecked(True)
        self.toggle_console_action.setShortcut("Ctrl+Shift+C")
        self.toggle_console_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("ConsoleDock"))
        view_menu.addAction(self.toggle_console_action)
        
        self.toggle_problems_action = QtGui.QAction("Problems", self.parent)
        self.toggle_problems_action.setCheckable(True)
        self.toggle_problems_action.setChecked(True)
        self.toggle_problems_action.setShortcut("Ctrl+Shift+U")
        self.toggle_problems_action.triggered.connect(lambda: self.parent.dock_manager.toggle_dock("ProblemsDock"))
        view_menu.addAction(self.toggle_problems_action)
        
        view_menu.addSeparator()
        
        # Add "Hide All Panels" and "Show All Panels" options
        hide_all_action = QtGui.QAction("Hide All Panels", self.parent)
        hide_all_action.setShortcut("Ctrl+Shift+H")
        hide_all_action.triggered.connect(lambda: self.parent.dock_manager.hide_all_panels())
        view_menu.addAction(hide_all_action)
        
        show_all_action = QtGui.QAction("Show All Panels", self.parent)
        show_all_action.setShortcut("Ctrl+Shift+A")
        show_all_action.triggered.connect(lambda: self.parent.dock_manager.show_all_panels())
        view_menu.addAction(show_all_action)
        
        # Debug Menu
        debug_menu = menubar.addMenu("&Debug")
        
        run_debug_action = QtGui.QAction("Run with &Breakpoints", self.parent)
        run_debug_action.setShortcut("F5")
        run_debug_action.setToolTip("Execute code and pause at breakpoints")
        run_debug_action.triggered.connect(self._run_with_breakpoints)
        debug_menu.addAction(run_debug_action)
        
        debug_menu.addSeparator()
        
        toggle_breakpoint_action = QtGui.QAction("Toggle &Breakpoint", self.parent)
        toggle_breakpoint_action.setShortcut("F9")
        toggle_breakpoint_action.setToolTip("Add/remove breakpoint at current line")
        toggle_breakpoint_action.triggered.connect(self._toggle_breakpoint)
        debug_menu.addAction(toggle_breakpoint_action)
        
        clear_breakpoints_action = QtGui.QAction("&Clear All Breakpoints", self.parent)
        clear_breakpoints_action.setShortcut("Ctrl+Shift+F9")
        clear_breakpoints_action.triggered.connect(self._clear_all_breakpoints)
        debug_menu.addAction(clear_breakpoints_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Settings menu item
        settings_action = QtGui.QAction("&Settings", self.parent)
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
        
        beta_info_action = QtGui.QAction("Beta Information", self.parent)
        beta_info_action.triggered.connect(self._show_beta_info)
        help_menu.addAction(beta_info_action)
        
        help_menu.addSeparator()
        
        docs_action = QtGui.QAction("&Documentation", self.parent)
        docs_action.triggered.connect(self._open_documentation)
        help_menu.addAction(docs_action)
        
        github_action = QtGui.QAction("&GitHub Repository", self.parent)
        github_action.triggered.connect(self._open_github)
        help_menu.addAction(github_action)
        
        help_menu.addSeparator()
        
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
    def _show_beta_info(self):
        """Show beta information dialog"""
        if hasattr(self.parent, 'beta_manager'):
            self.parent.beta_manager.show_about_beta(self.parent)
    
    def _open_documentation(self):
        """Open documentation URL"""
        import webbrowser
        webbrowser.open("https://github.com/mayjackass/AI_Maya_ScriptEditor#readme")
    
    def _open_github(self):
        """Open GitHub repository"""
        import webbrowser
        webbrowser.open("https://github.com/mayjackass/AI_Maya_ScriptEditor")
    
    def _show_about(self):
        """Show enhanced about dialog"""
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("About NEO Script Editor")
        dialog.setMinimumSize(600, 700)
        dialog.setMaximumSize(600, 700)
        
        # Apply Matrix theme styling
        dialog.setStyleSheet("""
            QDialog {
                background: #000000;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background: #00ff41;
                border: 1px solid #00ff41;
                color: #000000;
                padding: 8px 24px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #00cc33;
                border: 1px solid #00cc33;
            }
            QTextBrowser {
                background: #000000;
                border: 1px solid #00ff41;
                border-radius: 6px;
                color: #ffffff;
                padding: 12px;
            }
            QTextBrowser QScrollBar:vertical {
                background: #000000;
                border: 1px solid #00ff41;
                width: 12px;
                border-radius: 6px;
            }
            QTextBrowser QScrollBar::handle:vertical {
                background: #00ff41;
                border-radius: 5px;
                min-height: 20px;
            }
            QTextBrowser QScrollBar::handle:vertical:hover {
                background: #00cc33;
            }
            QTextBrowser QScrollBar::add-line:vertical,
            QTextBrowser QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QTextBrowser QScrollBar::add-page:vertical,
            QTextBrowser QScrollBar::sub-page:vertical {
                background: #000000;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo/Title Section
        titleLayout = QtWidgets.QVBoxLayout()
        titleLayout.setSpacing(8)
        
        # Title
        titleLabel = QtWidgets.QLabel("⚡ NEO Script Editor")
        titleLabel.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #00ff41;
            letter-spacing: 1px;
        """)
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        # Version
        versionLabel = QtWidgets.QLabel("Version 3.0 Beta • Testing Release")
        versionLabel.setStyleSheet("""
            font-size: 14px;
            color: #00ff41;
            font-weight: 600;
        """)
        versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        # Tagline
        taglineLabel = QtWidgets.QLabel("AI-Powered Maya Script Editor with VSCode-Style Features")
        taglineLabel.setStyleSheet("""
            font-size: 13px;
            color: #888888;
            font-style: italic;
            margin-top: 4px;
        """)
        taglineLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        # Beta warning
        betaWarningLabel = QtWidgets.QLabel("⚠️ BETA RELEASE - For Testing Purposes Only")
        betaWarningLabel.setStyleSheet("""
            font-size: 12px;
            color: #00ff41;
            font-weight: 600;
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid #00ff41;
            border-radius: 4px;
            padding: 6px 12px;
            margin-top: 8px;
        """)
        betaWarningLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        titleLayout.addWidget(titleLabel)
        titleLayout.addWidget(versionLabel)
        titleLayout.addWidget(taglineLabel)
        titleLayout.addWidget(betaWarningLabel)
        layout.addLayout(titleLayout)
        
        # Separator
        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.HLine)
        separator1.setStyleSheet("background: #00ff41; max-height: 1px;")
        layout.addWidget(separator1)
        
        # Author Section
        authorLayout = QtWidgets.QVBoxLayout()
        authorLayout.setSpacing(4)
        
        authorTitleLabel = QtWidgets.QLabel("DEVELOPED BY")
        authorTitleLabel.setStyleSheet("""
            font-size: 11px;
            color: #00ff41;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        authorTitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        authorNameLabel = QtWidgets.QLabel("Mayj Amilano")
        authorNameLabel.setStyleSheet("""
            font-size: 18px;
            color: #ffffff;
            font-weight: 600;
        """)
        authorNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        authorHandleLabel = QtWidgets.QLabel("(@mayjackass)")
        authorHandleLabel.setStyleSheet("""
            font-size: 13px;
            color: #888888;
            font-weight: 400;
        """)
        authorHandleLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        githubLabel = QtWidgets.QLabel('🔗 <a href="https://github.com/mayjackass" style="color: #00ff41; text-decoration: none;">github.com/mayjackass</a>')
        githubLabel.setStyleSheet("font-size: 12px;")
        githubLabel.setAlignment(QtCore.Qt.AlignCenter)
        githubLabel.setOpenExternalLinks(True)
        
        copyrightLabel = QtWidgets.QLabel("© 2025 • All Rights Reserved")
        copyrightLabel.setStyleSheet("""
            font-size: 11px;
            color: #888888;
            margin-top: 4px;
        """)
        copyrightLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        authorLayout.addWidget(authorTitleLabel)
        authorLayout.addWidget(authorNameLabel)
        authorLayout.addWidget(authorHandleLabel)
        authorLayout.addWidget(githubLabel)
        authorLayout.addWidget(copyrightLabel)
        layout.addLayout(authorLayout)
        
        # Separator
        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.HLine)
        separator2.setStyleSheet("background: #00ff41; max-height: 1px;")
        layout.addWidget(separator2)
        
        # Features Section
        featuresLabel = QtWidgets.QLabel("KEY FEATURES")
        featuresLabel.setStyleSheet("""
            font-size: 11px;
            color: #00ff41;
            font-weight: 600;
            letter-spacing: 1px;
            margin-bottom: 8px;
        """)
        layout.addWidget(featuresLabel)
        
        # Features list
        featuresBrowser = QtWidgets.QTextBrowser()
        featuresBrowser.setMaximumHeight(220)
        featuresBrowser.setOpenExternalLinks(False)
        
        featuresBrowser.setHtml("""
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #000000; }
                .feature { margin-bottom: 8px; line-height: 1.6; }
                .feature-title { color: #00ff41; font-weight: 600; }
                .text { color: #ffffff; font-size: 12px; }
            </style>
            <div class="feature">
                <span class="feature-title">Morpheus AI</span> — 
                <span class="text">Integrated AI assistant with OpenAI & Claude support, auto-context detection</span>
            </div>
            <div class="feature">
                <span class="feature-title">VSCode-Style Editor</span> — 
                <span class="text">Advanced syntax highlighting, autocomplete, inline diff preview</span>
            </div>
            <div class="feature">
                <span class="feature-title">Real-Time Analysis</span> — 
                <span class="text">Multi-pass error detection (up to 10 errors), instant syntax validation</span>
            </div>
            <div class="feature">
                <span class="feature-title">Smart Code Matching</span> — 
                <span class="text">Intelligent code replacement with visual diff preview</span>
            </div>
            <div class="feature">
                <span class="feature-title">Python & MEL</span> — 
                <span class="text">Dual language support with tab icons and language-specific features</span>
            </div>
            <div class="feature">
                <span class="feature-title">Problems Panel</span> — 
                <span class="text">Tab-focused error tracking, column-based error positioning</span>
            </div>
            <div class="feature">
                <span class="feature-title">Modern UI</span> — 
                <span class="text">Dark theme, customizable docks, clean GitHub-style interface</span>
            </div>
            <div class="feature">
                <span class="feature-title">High Performance</span> — 
                <span class="text">Optimized text rendering, lag-free typing, efficient syntax parsing</span>
            </div>
        """)
        layout.addWidget(featuresBrowser)
        
        # Separator
        separator3 = QtWidgets.QFrame()
        separator3.setFrameShape(QtWidgets.QFrame.HLine)
        separator3.setStyleSheet("background: #00ff41; max-height: 1px;")
        layout.addWidget(separator3)
        
        # Tech Stack
        techLabel = QtWidgets.QLabel("BUILT WITH")
        techLabel.setStyleSheet("""
            font-size: 11px;
            color: #00ff41;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        layout.addWidget(techLabel)
        
        techStackLabel = QtWidgets.QLabel("Python 3.9+ • PySide6/Qt • OpenAI API • Anthropic Claude • difflib")
        techStackLabel.setStyleSheet("""
            font-size: 12px;
            color: #888888;
            margin-bottom: 8px;
        """)
        techStackLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(techStackLabel)
        
        # Close button
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        
        closeBtn = QtWidgets.QPushButton("Close")
        closeBtn.clicked.connect(dialog.accept)
        closeBtn.setCursor(QtCore.Qt.PointingHandCursor)
        
        buttonLayout.addWidget(closeBtn)
        buttonLayout.addStretch()
        layout.addLayout(buttonLayout)
        
        # Show dialog
        dialog.exec()
    
    def update_recent_files_menu(self):
        """Update the Open Recent submenu with current recent files"""
        self.recent_menu.clear()
        
        recent_files = self.parent.file_manager.get_recent_files()
        
        if not recent_files:
            no_recent_action = QtGui.QAction("No Recent Files", self.parent)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
        else:
            for i, file_path in enumerate(recent_files):
                # Show just filename with shortcut number
                filename = QtCore.QFileInfo(file_path).fileName()
                action = QtGui.QAction(f"{i+1}. {filename}", self.parent)
                action.setToolTip(file_path)  # Show full path in tooltip
                action.triggered.connect(lambda checked, fp=file_path: self.parent.file_manager.open_recent_file(fp))
                self.recent_menu.addAction(action)
            
            # Add separator and Clear Recent
            self.recent_menu.addSeparator()
            clear_action = QtGui.QAction("Clear Recent Files", self.parent)
            clear_action.triggered.connect(self.parent.file_manager.clear_recent_files)
            self.recent_menu.addAction(clear_action)
    
    # Debug menu actions
    def _run_with_breakpoints(self):
        """Run code with breakpoints (F5)."""
        self.parent.debug_manager.run_with_breakpoints()
    
    def _toggle_breakpoint(self):
        """Toggle breakpoint at current line (F9)."""
        editor = self.parent.debug_manager.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            line_number = cursor.blockNumber() + 1
            editor.toggle_breakpoint(line_number)
        else:
            QtWidgets.QMessageBox.warning(
                self.parent, "No Editor",
                "No active editor found."
            )
    
    def _clear_all_breakpoints(self):
        """Clear all breakpoints (Ctrl+Shift+F9)."""
        self.parent.debug_manager.clear_all_breakpoints()
