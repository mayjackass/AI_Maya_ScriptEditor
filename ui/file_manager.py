"""
File Manager
Handles all file operations (new, open, save, tab management)
"""
import os
from PySide6 import QtWidgets, QtCore, QtGui


class FileManager:
    """Manages file operations and tab management"""
    
    def __init__(self, parent, tab_widget, language_combo):
        """
        Initialize FileManager
        
        Args:
            parent: Main window instance
            tab_widget: QTabWidget for code editors
            language_combo: QComboBox for language selection
        """
        self.parent = parent
        self.tab_widget = tab_widget
        self.language_combo = language_combo
        
        # Recent files tracking
        self.settings = QtCore.QSettings("NEO", "ScriptEditor")
        self.max_recent_files = 10
        
        # Create icons for Python and MEL
        self._create_language_icons()
    
    def _create_language_icons(self):
        """Create icons for Python and MEL languages from assets folder"""
        # Get the base directory (parent of ui folder)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Load Python icon from assets
        python_icon_path = os.path.join(base_dir, "assets", "python.png")
        if os.path.exists(python_icon_path):
            self.python_icon = QtGui.QIcon(python_icon_path)
        else:
            # Fallback to emoji if file not found
            python_pixmap = QtGui.QPixmap(16, 16)
            python_pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(python_pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            font = QtGui.QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(python_pixmap.rect(), QtCore.Qt.AlignCenter, "🐍")
            painter.end()
            self.python_icon = QtGui.QIcon(python_pixmap)
        
        # Load MEL icon from assets
        mel_icon_path = os.path.join(base_dir, "assets", "mel.png")
        if os.path.exists(mel_icon_path):
            self.mel_icon = QtGui.QIcon(mel_icon_path)
        else:
            # Fallback to emoji if file not found
            mel_pixmap = QtGui.QPixmap(16, 16)
            mel_pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(mel_pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
            font = QtGui.QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(mel_pixmap.rect(), QtCore.Qt.AlignCenter, "📜")
            painter.end()
            self.mel_icon = QtGui.QIcon(mel_pixmap)
    
    def _set_tab_icon(self, index, language):
        """Set the icon for a tab based on language
        
        Args:
            index: Tab index
            language: 'python' or 'mel'
        """
        if language.lower() == "python":
            self.tab_widget.setTabIcon(index, self.python_icon)
        else:
            self.tab_widget.setTabIcon(index, self.mel_icon)
        
    def new_file(self):
        """Create new file"""
        try:
            from editor.code_editor import CodeEditor
            editor = CodeEditor()
            lang = self.language_combo.currentText()
            if "Python" in lang:
                editor.set_language("python")
                content = ""  # Start with empty file
                language = "python"
            else:
                editor.set_language("mel")
                content = ""  # Start with empty file
                language = "mel"
            editor.setPlainText(content)
            
            # Set placeholder text with instructions (like VSCode)
            if "Python" in lang:
                editor.setPlaceholderText(
                    "# Start typing Python code...\n"
                    "# - Press Ctrl+Space for autocomplete\n"
                    "# - Syntax errors will be highlighted in red\n"
                    "# - Use Ctrl+F to find/replace"
                )
            else:
                editor.setPlaceholderText(
                    "// Start typing MEL code...\n"
                    "// - MEL syntax highlighting enabled\n"
                    "// - Use Ctrl+F to find/replace"
                )
            
            # Connect problems signal for problems window
            if hasattr(editor, 'lintProblemsFound'):
                editor.lintProblemsFound.connect(self.parent._update_problems)
        except:
            editor = QtWidgets.QTextEdit()
            editor.setPlainText("")
            language = "python"
        
        index = self.tab_widget.addTab(editor, "untitled")
        self._set_tab_icon(index, language)
        self.tab_widget.setCurrentIndex(index)
    
    def open_file(self, file_path=None):
        """Open file"""
        if not file_path:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.parent, "Open File", "", "All Files (*)"
            )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    from editor.code_editor import CodeEditor
                    editor = CodeEditor()
                    if file_path.endswith('.py'):
                        editor.set_language("python")
                        language = "python"
                    elif file_path.endswith('.mel'):
                        editor.set_language("mel")
                        language = "mel"
                    else:
                        language = "python"  # Default to Python
                    
                    # Connect problems signal for problems window
                    if hasattr(editor, 'lintProblemsFound'):
                        editor.lintProblemsFound.connect(self.parent._update_problems)
                except:
                    editor = QtWidgets.QTextEdit()
                    language = "python"
                
                editor.setPlainText(content)
                tab_name = os.path.basename(file_path)
                index = self.tab_widget.addTab(editor, tab_name)
                self._set_tab_icon(index, language)
                self.tab_widget.setCurrentIndex(index)
                
                # Track file path for this tab (for session persistence)
                if hasattr(self.parent, 'tab_file_paths'):
                    self.parent.tab_file_paths[index] = file_path
                
                # Add to recent files
                self.add_recent_file(file_path)
                
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
                QtWidgets.QMessageBox.warning(self.parent, "Error", f"Failed to open: {e}")
    
    def open_folder(self):
        """Open folder and update explorer"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self.parent, "Open Folder", "", QtWidgets.QFileDialog.ShowDirsOnly
        )
        if folder_path:
            try:
                # Update the explorer dock to show the selected folder
                if hasattr(self.parent, 'dock_manager') and self.parent.dock_manager:
                    dock_manager = self.parent.dock_manager
                    
                    # Access the file model and tree view directly from dock_manager
                    if hasattr(dock_manager, 'fileModel') and hasattr(dock_manager, 'explorerView'):
                        # Set the root path to the selected folder
                        index = dock_manager.fileModel.setRootPath(folder_path)
                        dock_manager.explorerView.setRootIndex(index)
                        dock_manager.explorerView.expand(index)
                        
                        # Show the explorer dock if it's hidden
                        if hasattr(dock_manager, 'explorer_dock') and not dock_manager.explorer_dock.isVisible():
                            dock_manager.explorer_dock.setVisible(True)
                        
                        print(f"[FileManager] Opened folder: {folder_path}")
                    else:
                        QtWidgets.QMessageBox.information(
                            self.parent, "Info", 
                            f"Explorer not fully initialized. Selected folder:\n{folder_path}"
                        )
                else:
                    QtWidgets.QMessageBox.information(
                        self.parent, "Info", 
                        f"Dock manager not available. Selected folder:\n{folder_path}"
                    )
                    
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.parent, "Error", f"Failed to open folder: {e}")
                import traceback
                traceback.print_exc()
    
    def save_file(self):
        """Save current file"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.parent, "Save File", "", "All Files (*)"
            )
            if file_path:
                try:
                    content = current_widget.toPlainText()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    tab_name = os.path.basename(file_path)
                    current_index = self.tab_widget.currentIndex()
                    self.tab_widget.setTabText(current_index, tab_name)
                    
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self.parent, "Error", f"Failed to save: {e}")
    
    def save_file_as(self):
        """Save current file as (always prompt for location)"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.parent, "Save File As", "", "All Files (*)"
            )
            if file_path:
                try:
                    content = current_widget.toPlainText()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    tab_name = os.path.basename(file_path)
                    current_index = self.tab_widget.currentIndex()
                    self.tab_widget.setTabText(current_index, tab_name)
                    
                    # Track file path for this tab (for session persistence)
                    if hasattr(self.parent, 'tab_file_paths'):
                        self.parent.tab_file_paths[current_index] = file_path
                    
                    # Update language based on file extension
                    if hasattr(current_widget, 'set_language'):
                        if file_path.endswith('.py'):
                            current_widget.set_language("python")
                            self.language_combo.setCurrentText("🐍 Python")
                            self._set_tab_icon(current_index, "python")
                        elif file_path.endswith('.mel'):
                            current_widget.set_language("mel")
                            self.language_combo.setCurrentText("📜 MEL")
                            self._set_tab_icon(current_index, "mel")
                    
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self.parent, "Error", f"Failed to save: {e}")
    
    def close_tab(self, index):
        """Close tab and clean up its problems"""
        # Get the editor widget before closing
        editor_widget = self.tab_widget.widget(index)
        
        # Remove problems for this editor from the main window tracker
        if editor_widget and hasattr(self.parent, 'editor_problems'):
            editor_id = id(editor_widget)
            if editor_id in self.parent.editor_problems:
                del self.parent.editor_problems[editor_id]
                # Refresh the problems display for current tab
                if hasattr(self.parent, '_refresh_current_tab_problems'):
                    self.parent._refresh_current_tab_problems()
        
        # Close the tab
        if self.tab_widget.count() <= 1:
            self.new_file()
        self.tab_widget.removeTab(index)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'get_language'):
            lang = current_widget.get_language()
            if lang == "python":
                self.language_combo.setCurrentText("🐍 Python")
            else:
                self.language_combo.setCurrentText("📜 MEL")
        
        # Refresh problems display to show only current tab's problems
        if hasattr(self.parent, '_refresh_current_tab_problems'):
            self.parent._refresh_current_tab_problems()
    
    def on_language_changed(self, text):
        """Handle language change"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'set_language'):
            current_index = self.tab_widget.currentIndex()
            if "Python" in text:
                current_widget.set_language("python")
                self._set_tab_icon(current_index, "python")
                # Update placeholder text for Python
                if hasattr(current_widget, 'setPlaceholderText') and not current_widget.toPlainText():
                    current_widget.setPlaceholderText(
                        "# Start typing Python code...\n"
                        "# - Press Ctrl+Space for autocomplete\n"
                        "# - Syntax errors will be highlighted in red\n"
                        "# - Use Ctrl+F to find/replace"
                    )
            else:
                current_widget.set_language("mel")
                self._set_tab_icon(current_index, "mel")
                # Update placeholder text for MEL
                if hasattr(current_widget, 'setPlaceholderText') and not current_widget.toPlainText():
                    current_widget.setPlaceholderText(
                        "// Start typing MEL code...\n"
                        "// - MEL syntax highlighting enabled\n"
                        "// - Use Ctrl+F to find/replace"
                    )
    
    def on_explorer_double_clicked(self, index, file_model):
        """Handle explorer double-click"""
        file_path = file_model.filePath(index)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    from editor.code_editor import CodeEditor
                    editor = CodeEditor()
                    if file_path.endswith('.py'):
                        editor.set_language("python")
                        language = "python"
                    elif file_path.endswith('.mel'):
                        editor.set_language("mel")
                        language = "mel"
                    else:
                        language = "python"  # Default
                    
                    # Connect problems signal for problems window
                    if hasattr(editor, 'lintProblemsFound'):
                        editor.lintProblemsFound.connect(self.parent._update_problems)
                except:
                    editor = QtWidgets.QTextEdit()
                    language = "python"
                
                editor.setPlainText(content)
                tab_name = os.path.basename(file_path)
                index = self.tab_widget.addTab(editor, tab_name)
                self._set_tab_icon(index, language)
                self.tab_widget.setCurrentIndex(index)
                
            except Exception as e:
                print(f"Explorer file open error: {e}")
    
    def get_recent_files(self):
        """Get list of recent files"""
        recent = self.settings.value("recent_files", [])
        if not isinstance(recent, list):
            recent = []
        # Filter out files that no longer exist
        return [f for f in recent if os.path.exists(f)]
    
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if not file_path or not os.path.exists(file_path):
            return
        
        recent = self.get_recent_files()
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
        
        # Add to front
        recent.insert(0, file_path)
        
        # Keep only max recent files
        recent = recent[:self.max_recent_files]
        
        # Save
        self.settings.setValue("recent_files", recent)
        
        # Update menu
        if hasattr(self.parent, 'menu_manager'):
            self.parent.menu_manager.update_recent_files_menu()
    
    def clear_recent_files(self):
        """Clear all recent files"""
        self.settings.setValue("recent_files", [])
        if hasattr(self.parent, 'menu_manager'):
            self.parent.menu_manager.update_recent_files_menu()
    
    def open_recent_file(self, file_path):
        """Open a file from recent files list"""
        if os.path.exists(file_path):
            self.open_file(file_path)
        else:
            # File no longer exists, remove from recent
            recent = self.get_recent_files()
            if file_path in recent:
                recent.remove(file_path)
                self.settings.setValue("recent_files", recent)
                if hasattr(self.parent, 'menu_manager'):
                    self.parent.menu_manager.update_recent_files_menu()
