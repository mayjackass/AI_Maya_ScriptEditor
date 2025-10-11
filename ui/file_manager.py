"""
File Manager
Handles all file operations (new, open, save, tab management)
"""
import os
from PySide6 import QtWidgets, QtCore


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
        
    def new_file(self):
        """Create new file"""
        try:
            from editor.code_editor import CodeEditor
            editor = CodeEditor()
            lang = self.language_combo.currentText()
            if "Python" in lang:
                editor.set_language("python")
                content = "#!/usr/bin/env python3\n# New Python script\nprint('Hello World!')\n"
            else:
                editor.set_language("mel")
                content = "// New MEL script\nprint(\"Hello World!\\n\");\n"
            editor.setPlainText(content)
            
            # Connect problems signal for problems window
            if hasattr(editor, 'lintProblemsFound'):
                editor.lintProblemsFound.connect(self.parent._update_problems)
        except:
            editor = QtWidgets.QTextEdit()
            editor.setPlainText("# New file\nprint('Hello World!')\n")
        
        index = self.tab_widget.addTab(editor, "untitled")
        self.tab_widget.setCurrentIndex(index)
    
    def open_file(self):
        """Open file"""
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
                    elif file_path.endswith('.mel'):
                        editor.set_language("mel")
                    
                    # Connect problems signal for problems window
                    if hasattr(editor, 'lintProblemsFound'):
                        editor.lintProblemsFound.connect(self.parent._update_problems)
                except:
                    editor = QtWidgets.QTextEdit()
                
                editor.setPlainText(content)
                tab_name = os.path.basename(file_path)
                index = self.tab_widget.addTab(editor, tab_name)
                self.tab_widget.setCurrentIndex(index)
                
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
                    
                    # Update language based on file extension
                    if hasattr(current_widget, 'set_language'):
                        if file_path.endswith('.py'):
                            current_widget.set_language("python")
                            self.language_combo.setCurrentText("🐍 Python")
                        elif file_path.endswith('.mel'):
                            current_widget.set_language("mel")
                            self.language_combo.setCurrentText("📜 MEL")
                    
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self.parent, "Error", f"Failed to save: {e}")
    
    def close_tab(self, index):
        """Close tab"""
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
    
    def on_language_changed(self, text):
        """Handle language change"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'set_language'):
            if "Python" in text:
                current_widget.set_language("python")
            else:
                current_widget.set_language("mel")
    
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
                    elif file_path.endswith('.mel'):
                        editor.set_language("mel")
                except:
                    editor = QtWidgets.QTextEdit()
                
                editor.setPlainText(content)
                tab_name = os.path.basename(file_path)
                index = self.tab_widget.addTab(editor, tab_name)
                self.tab_widget.setCurrentIndex(index)
                
            except Exception as e:
                print(f"Explorer file open error: {e}")
