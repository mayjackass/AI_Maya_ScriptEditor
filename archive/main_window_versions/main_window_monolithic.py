# ai_script_editor/main_window.py
"""
AI Script Editor - Performance Optimized with Full Features
Balanced version: Fast performance + Essential functionality
"""
import os
from PySide6 import QtCore, QtGui, QtWidgets

# Load OpenAI key first
settings = QtCore.QSettings("AI_Script_Editor", "settings")
stored_key = settings.value("OPENAI_API_KEY", "")
if stored_key:
    os.environ["OPENAI_API_KEY"] = stored_key
    print("🔑 OpenAI key injected successfully.")

# Internal imports
from editor.code_editor import CodeEditor
from editor.highlighter import PythonHighlighter, MELHighlighter
from model.hierarchy import CodeHierarchyModel
from ui.output_console import OutputConsole
from ai.chat import AIMorpheus
from ai.copilot_manager import MorpheusManager

DARK_STYLE = """
QWidget { background: #1E1E1E; color: #DDD; font-family: Segoe UI, Consolas; }
QMenuBar, QMenu, QToolBar { font-size: 11pt; background-color:#2D2D30; }
QTextBrowser, QTextEdit { border: 1px solid #333; border-radius: 4px; background: #252526; }
QPushButton { background: #2D2D30; color: #EEE; border-radius: 4px; padding: 4px 8px; }
QPushButton:hover { background: #3E3E42; }
QLineEdit { background: #252526; border: 1px solid #333; color: #EEE; border-radius: 4px; padding: 3px; }
QDockWidget::title { background: #252526; padding: 4px; }
QTabBar::tab { background: #2D2D30; color: #DDD; padding: 6px 12px; border:1px solid #3E3E42; }
QTabBar::tab:selected { background: #3E3E42; }
QComboBox { background: #21262d; border: 1px solid #30363d; color: #f0f6fc; padding: 4px 8px; border-radius: 4px; }
QComboBox:hover { border-color: #58a6ff; }
QTreeView { background: #1E1E1E; color: #DDD; border: 1px solid #333; }
"""

class AiScriptEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEO Script Editor v2.1 - Performance Optimized")
        self.resize(1200, 700)
        self.setStyleSheet(DARK_STYLE)
        
        # Performance optimized: Single timer for syntax checking
        self.syntax_timer = QtCore.QTimer()
        self.syntax_timer.setSingleShot(True)
        self.syntax_timer.timeout.connect(self._quick_syntax_check)
        
        self._setup_ui()
        self._setup_connections()
        self._setup_ai_components()
        
    def _setup_ui(self):
        """Setup complete UI with all essential features."""
        # Central tabbed editor with language selector
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Header with language selector
        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        self.languageCombo = QtWidgets.QComboBox()
        self.languageCombo.addItem("🐍 Python", "Python")
        self.languageCombo.addItem("📜 MEL", "MEL")
        self.languageCombo.setCurrentIndex(0)
        self.languageCombo.setToolTip("Select script language")
        
        header_layout.addWidget(QtWidgets.QLabel("Language:"))
        header_layout.addWidget(self.languageCombo)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setTabsClosable(True)
        layout.addWidget(self.tabWidget)
        
        self.setCentralWidget(central_widget)
        
        # Build all dock widgets
        self._build_console_dock()
        self._build_problems_dock()
        self._build_explorer_dock()
        self._build_chat_dock()
        
        # Build menu and toolbar
        self._build_menu()
        self._build_toolbar()
        
        # Create initial tab
        self.new_tab("untitled", "")
        
    def _setup_connections(self):
        """Setup essential connections."""
        self.tabWidget.tabCloseRequested.connect(self._close_tab)
        self.tabWidget.currentChanged.connect(self._on_tab_changed)
        self.languageCombo.currentTextChanged.connect(self._language_changed)
        
    def _setup_ai_components(self):
        """Setup AI components after UI is ready."""
        # Initialize Morpheus
        self.morpheus = AIMorpheus(self)
        if not self.morpheus.client:
            self.console.append("⚠️ No active OpenAI client. Set your API key via Settings → API Key.\n")
        
        # Initialize Morpheus Manager
        self.morpheus_manager = MorpheusManager(self)
        self.morpheus_manager.responseReady.connect(self._on_morpheus_response)
        
        # Add Morpheus introduction
        QtCore.QTimer.singleShot(1000, self._morpheus_introduction)

    def _build_console_dock(self):
        """Build console dock."""
        self.console = OutputConsole()
        self.console.setMaximumHeight(120)
        console_dock = QtWidgets.QDockWidget("Console", self)
        console_dock.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, console_dock)
        
    def _build_problems_dock(self):
        """Build problems dock."""
        self.problemsTree = QtWidgets.QTreeWidget()
        self.problemsTree.setHeaderLabels(["Type", "Message", "Line", "File"])
        self.problemsTree.setMaximumHeight(150)
        
        problems_dock = QtWidgets.QDockWidget("Problems", self)
        problems_dock.setWidget(self.problemsTree)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, problems_dock)
        
    def _build_explorer_dock(self):
        """Build file explorer dock."""
        self.hierarchyModel = CodeHierarchyModel()
        self.explorerView = QtWidgets.QTreeView()
        self.explorerView.setModel(self.hierarchyModel)
        self.explorerView.setHeaderHidden(True)
        self.explorerView.doubleClicked.connect(self._on_explorer_double_clicked)
        
        explorer_dock = QtWidgets.QDockWidget("Explorer", self)
        explorer_dock.setWidget(self.explorerView)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, explorer_dock)
        
    def _build_chat_dock(self):
        """Build AI chat dock."""
        chat_widget = QtWidgets.QWidget()
        chat_layout = QtWidgets.QVBoxLayout(chat_widget)
        
        self.chatDisplay = QtWidgets.QTextBrowser()
        self.chatDisplay.setMaximumHeight(200)
        
        self.chatInput = QtWidgets.QLineEdit()
        self.chatInput.setPlaceholderText("Ask Morpheus...")
        self.chatInput.returnPressed.connect(self._send_chat_message)
        
        chat_layout.addWidget(self.chatDisplay)
        chat_layout.addWidget(self.chatInput)
        
        chat_dock = QtWidgets.QDockWidget("AI Chat", self)
        chat_dock.setWidget(chat_widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, chat_dock)
        
    def _build_menu(self):
        """Build complete menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("New Tab", self._new_tab_action, "Ctrl+T")
        file_menu.addAction("New File", lambda: self.new_tab("untitled", ""), "Ctrl+N")
        file_menu.addAction("Open File", self._open_file, "Ctrl+O")
        file_menu.addAction("Save", self._save_file, "Ctrl+S")
        file_menu.addAction("Save As", self._save_as_file, "Ctrl+Shift+S")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close, "Ctrl+Q")
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("Undo", self._undo, "Ctrl+Z")
        edit_menu.addAction("Redo", self._redo, "Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", self._cut, "Ctrl+X")
        edit_menu.addAction("Copy", self._copy, "Ctrl+C")
        edit_menu.addAction("Paste", self._paste, "Ctrl+V")
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("Check Syntax", self._quick_syntax_check, "F5")
        view_menu.addAction("Run Script", self._run_script, "F6")
        
        # AI menu
        ai_menu = menubar.addMenu("&AI")
        ai_menu.addAction("Chat with Morpheus", self._focus_chat, "Ctrl+M")
        ai_menu.addAction("Ask About Code", self._ask_about_code, "Ctrl+Shift+A")
        
        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        settings_menu.addAction("API Key", self._set_api_key)
        settings_menu.addAction("Preferences", self._show_preferences)
        
    def _build_toolbar(self):
        """Build toolbar with essential actions."""
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        
        # File actions
        toolbar.addAction("New", lambda: self.new_tab("untitled", ""))
        toolbar.addAction("Open", self._open_file)
        toolbar.addAction("Save", self._save_file)
        toolbar.addSeparator()
        
        # Code actions  
        toolbar.addAction("Run", self._run_script)
        toolbar.addAction("Check", self._quick_syntax_check)
        toolbar.addSeparator()
        
        # AI actions
        toolbar.addAction("Morpheus", self._focus_chat)
        
    def new_tab(self, filename, content=""):
        """Add new editor tab."""
        editor = CodeEditor()
        editor.setPlainText(content)
        
        # Connect text changes with optimized debouncing (performance optimized)
        editor.textChanged.connect(lambda: self.syntax_timer.start(1000))
        
        # Set highlighter based on language
        lang = self.languageCombo.currentText()
        if "Python" in lang:
            highlighter = PythonHighlighter(editor.document())
        else:
            highlighter = MELHighlighter(editor.document())
            
        tab_index = self.tabWidget.addTab(editor, filename)
        self.tabWidget.setCurrentIndex(tab_index)
        
        return editor
        
    def _close_tab(self, index):
        """Close tab."""
        self.tabWidget.removeTab(index)
        if self.tabWidget.count() == 0:
            self.new_tab("untitled", "")
            
    def _on_tab_changed(self, index):
        """Handle tab change."""
        if index >= 0:
            self._quick_syntax_check()
            
    def _language_changed(self):
        """Change language for current tab."""
        current_editor = self.tabWidget.currentWidget()
        if not current_editor:
            return
            
        lang = self.languageCombo.currentText()
        if "Python" in lang:
            highlighter = PythonHighlighter(current_editor.document())
        else:
            highlighter = MELHighlighter(current_editor.document())
            
    # File operations
    def _new_tab_action(self):
        """Create new tab."""
        self.new_tab("untitled", "")
        
    def _open_file(self):
        """Open file dialog."""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor = self.new_tab(os.path.basename(filename), content)
                editor.filename = filename  # Store full path for saving
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Could not open file: {e}")
                
    def _save_file(self):
        """Save current file."""
        current_editor = self.tabWidget.currentWidget()
        if not current_editor:
            return
            
        if hasattr(current_editor, 'filename'):
            # File already has a path
            try:
                with open(current_editor.filename, 'w', encoding='utf-8') as f:
                    f.write(current_editor.toPlainText())
                self.console.append(f"✅ Saved: {current_editor.filename}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Could not save file: {e}")
        else:
            # New file, need Save As
            self._save_as_file()
            
    def _save_as_file(self):
        """Save as dialog."""
        current_editor = self.tabWidget.currentWidget()
        if not current_editor:
            return
            
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", "", "Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(current_editor.toPlainText())
                current_editor.filename = filename
                tab_index = self.tabWidget.currentIndex()
                self.tabWidget.setTabText(tab_index, os.path.basename(filename))
                self.console.append(f"✅ Saved: {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Could not save file: {e}")
                
    # Edit operations
    def _undo(self):
        current_editor = self.tabWidget.currentWidget()
        if current_editor:
            current_editor.undo()
            
    def _redo(self):
        current_editor = self.tabWidget.currentWidget()
        if current_editor:
            current_editor.redo()
            
    def _cut(self):
        current_editor = self.tabWidget.currentWidget()
        if current_editor:
            current_editor.cut()
            
    def _copy(self):
        current_editor = self.tabWidget.currentWidget()
        if current_editor:
            current_editor.copy()
            
    def _paste(self):
        current_editor = self.tabWidget.currentWidget()
        if current_editor:
            current_editor.paste()
            
    def _run_script(self):
        """Run current script."""
        current_editor = self.tabWidget.currentWidget()
        if not current_editor:
            return
            
        code = current_editor.toPlainText()
        lang = self.languageCombo.currentText()
        
        try:
            if "Python" in lang:
                exec(code)
                self.console.append("✅ Python script executed successfully")
            else:
                self.console.append("ℹ️ MEL script execution not implemented yet")
        except Exception as e:
            self.console.append(f"❌ Error: {str(e)}")
            
    # Explorer functionality
    def _on_explorer_double_clicked(self, index):
        """Handle double-click on explorer items to open files."""
        if not index.isValid():
            return
            
        file_path = self.hierarchyModel.filePath(index)
        
        if file_path and os.path.isfile(file_path):
            if file_path.lower().endswith(('.py', '.mel')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    filename = os.path.basename(file_path)
                    editor = self.new_tab(filename, content)
                    editor.filename = file_path
                    
                    if file_path.lower().endswith('.mel'):
                        self.languageCombo.setCurrentText("📜 MEL")
                    else:
                        self.languageCombo.setCurrentText("🐍 Python")
                        
                except Exception as e:
                    self.console.append(f"❌ Error opening file: {e}")
                    
    # AI functionality
    def _send_chat_message(self):
        """Send message to Morpheus."""
        message = self.chatInput.text().strip()
        if not message:
            return
            
        self.chatInput.clear()
        self.chatDisplay.append(f"<b>You:</b> {message}")
        
        try:
            current_editor = self.tabWidget.currentWidget()
            code_context = current_editor.toPlainText() if current_editor else ""
            
            # Send message to Morpheus (response will come via signal)
            self.morpheus_manager.send_message(message, code_context)
            
        except Exception as e:
            self.chatDisplay.append(f"<b>Morpheus:</b> Error: {str(e)}")
            
    def _on_morpheus_response(self, response):
        """Handle Morpheus AI response."""
        self.chatDisplay.append(f"<b>Morpheus:</b> {response}")
            
    def _focus_chat(self):
        """Focus on chat input."""
        self.chatInput.setFocus()
        
    def _ask_about_code(self):
        """Ask Morpheus about selected code."""
        current_editor = self.tabWidget.currentWidget()
        if not current_editor:
            return
            
        cursor = current_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.chatInput.setText(f"Explain this code: {selected_text}")
            self._send_chat_message()
        else:
            self.chatInput.setText("Explain this code")
            self.chatInput.setFocus()
            
    def _on_morpheus_response(self, response):
        """Handle Morpheus response."""
        self.chatDisplay.append(f"<b>Morpheus:</b> {response}")
        
    def _morpheus_introduction(self):
        """Show Morpheus introduction."""
        intro = """
        🤖 <b>Morpheus AI is ready!</b><br>
        I can help you with:<br>
        • Code analysis and debugging<br>
        • Python/MEL syntax assistance<br>
        • Code optimization suggestions<br>
        • Maya scripting guidance<br><br>
        Just type your question below! 🚀
        """
        self.chatDisplay.append(intro)
        
    # Settings
    def _set_api_key(self):
        """Set OpenAI API key."""
        key, ok = QtWidgets.QInputDialog.getText(
            self, "OpenAI API Key", "Enter your OpenAI API key:", 
            QtWidgets.QLineEdit.Password
        )
        if ok and key:
            settings = QtCore.QSettings("AI_Script_Editor", "settings")
            settings.setValue("OPENAI_API_KEY", key)
            os.environ["OPENAI_API_KEY"] = key
            self.console.append("🔑 API key updated successfully!")
            
    def _show_preferences(self):
        """Show preferences dialog."""
        QtWidgets.QMessageBox.information(self, "Preferences", "Preferences dialog coming soon!")
            
    def _quick_syntax_check(self):
        """OPTIMIZED syntax checking - fast and minimal but with multiple error detection."""
        current_editor = self.tabWidget.currentWidget()
        if not current_editor:
            return
            
        code = current_editor.toPlainText().strip()
        if not code or len(code) > 3000:  # Skip large files for performance
            return
            
        problems = []
        
        # OPTIMIZED: Simple compile-based check with multi-error detection
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            problems.append({
                'type': 'Error',
                'message': str(e.msg or 'Syntax error'),
                'line': e.lineno or 1,
                'file': 'Current File'
            })
            
            # Quick additional checks for common issues
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if i == e.lineno:
                    continue  # Skip the line we already found
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    # Check for missing colons
                    if stripped.startswith(('if ', 'for ', 'while ', 'def ', 'class ')) and not stripped.endswith(':'):
                        problems.append({
                            'type': 'Error', 
                            'message': 'Missing colon',
                            'line': i,
                            'file': 'Current File'
                        })
                    # Limit to 5 errors for performance
                    if len(problems) >= 5:
                        break
        except:
            pass  # Ignore other errors
        
        # Update problems panel
        self.problemsTree.clear()
        for problem in problems:
            item = QtWidgets.QTreeWidgetItem([
                problem['type'],
                problem['message'],
                str(problem['line']),
                problem['file']
            ])
            if problem['type'] == 'Error':
                item.setForeground(0, QtGui.QColor("#ff6b6b"))
            self.problemsTree.addTopLevelItem(item)
            
        # VS Code-style multiple red underlines
        selections = []
        if problems and hasattr(current_editor, 'setExtraSelections'):
            for problem in problems[:3]:  # Limit to 3 visual highlights for performance
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
                selection.format.setUnderlineColor(QtGui.QColor("#ff0000"))
                
                cursor = current_editor.textCursor()
                block = current_editor.document().findBlockByNumber(problem['line'] - 1)
                if block.isValid():
                    cursor.setPosition(block.position())
                    cursor.select(QtGui.QTextCursor.LineUnderCursor)
                    selection.cursor = cursor
                    selections.append(selection)
            
            current_editor.setExtraSelections(selections)
        else:
            if hasattr(current_editor, 'setExtraSelections'):
                current_editor.setExtraSelections([])

# Entry point
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    window.show()
    return app.exec()

if __name__ == "__main__":
    main()