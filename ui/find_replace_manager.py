"""
Find/Replace Manager - VS Code Style
Handles all find/replace widget creation and operations
"""
import os
from PySide6 import QtWidgets, QtCore, QtGui


class FindReplaceManager:
    """Manages VS Code-style find and replace functionality"""
    
    def __init__(self, parent, tab_widget):
        """
        Initialize FindReplaceManager
        
        Args:
            parent: Main window instance
            tab_widget: QTabWidget containing code editors
        """
        self.parent = parent
        self.tab_widget = tab_widget
        self.findReplaceWidget = None
        self.findInput = None
        self.replaceInput = None
        self.replaceRow = None
        self.toggleReplaceBtn = None
        self.findMatchLabel = None
        self.matchCaseCheck = None
        self.wholeWordCheck = None
        self.regexCheck = None
        
    def setup_widget(self, parent_layout):
        """Setup VS Code-style find/replace widget"""
        # Container for find/replace widget
        self.findReplaceWidget = QtWidgets.QWidget()
        self.findReplaceWidget.setStyleSheet("""
            QWidget {
                background: #2d2d30;
                border-bottom: 1px solid #3e3e42;
            }
            QLineEdit {
                background: #3c3c3c;
                border: 1px solid #3e3e42;
                color: #cccccc;
                padding: 4px 8px;
                border-radius: 2px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff41;
            }
            QPushButton {
                background: #00cc33;
                color: #000000;
                border: 1px solid #00ff41;
                padding: 4px 12px;
                border-radius: 2px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #00ff41;
            }
            QPushButton:pressed {
                background: #00aa2b;
            }
            QCheckBox {
                color: #cccccc;
                font-size: 11px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3e3e42;
                border-radius: 2px;
                background: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background: #00ff41;
                border-color: #00ff41;
            }
        """)
        
        mainLayout = QtWidgets.QVBoxLayout(self.findReplaceWidget)
        mainLayout.setContentsMargins(8, 6, 8, 6)
        mainLayout.setSpacing(4)
        
        # Find row
        findLayout = QtWidgets.QHBoxLayout()
        findLayout.setSpacing(6)
        
        # Toggle replace button (VS Code style)
        self.toggleReplaceBtn = QtWidgets.QPushButton("▶")
        self.toggleReplaceBtn.setFixedSize(20, 20)
        self.toggleReplaceBtn.setToolTip("Toggle Replace")
        self.toggleReplaceBtn.clicked.connect(self.toggle_replace_mode)
        self.toggleReplaceBtn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #cccccc;
                font-size: 10px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #3e3e42;
            }
        """)
        findLayout.addWidget(self.toggleReplaceBtn)
        
        # Find icon
        findIconLabel = QtWidgets.QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "find.png")
        if os.path.exists(icon_path):
            pixmap = QtGui.QPixmap(icon_path).scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            findIconLabel.setPixmap(pixmap)
        else:
            findIconLabel.setText("🔍")
        findIconLabel.setFixedWidth(20)
        findLayout.addWidget(findIconLabel)
        
        self.findInput = QtWidgets.QLineEdit()
        self.findInput.setPlaceholderText("Find")
        self.findInput.setMinimumWidth(250)
        self.findInput.returnPressed.connect(self.find_next)
        self.findInput.textChanged.connect(self.on_find_text_changed)  # Real-time highlight
        findLayout.addWidget(self.findInput)
        
        # Previous button with icon
        self.findPrevBtn = QtWidgets.QPushButton()
        self.findPrevBtn.setFixedSize(28, 26)
        self.findPrevBtn.setToolTip("Previous Match (Shift+F3)")
        prev_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "previous.png")
        if os.path.exists(prev_icon_path):
            self.findPrevBtn.setIcon(QtGui.QIcon(prev_icon_path))
            self.findPrevBtn.setIconSize(QtCore.QSize(16, 16))
        else:
            self.findPrevBtn.setText("⬆")
        self.findPrevBtn.clicked.connect(self.find_previous)
        findLayout.addWidget(self.findPrevBtn)
        
        # Next button with icon
        self.findNextBtn = QtWidgets.QPushButton()
        self.findNextBtn.setFixedSize(28, 26)
        self.findNextBtn.setToolTip("Next Match (F3)")
        next_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "next.png")
        if os.path.exists(next_icon_path):
            self.findNextBtn.setIcon(QtGui.QIcon(next_icon_path))
            self.findNextBtn.setIconSize(QtCore.QSize(16, 16))
        else:
            self.findNextBtn.setText("⬇")
        self.findNextBtn.clicked.connect(self.find_next)
        findLayout.addWidget(self.findNextBtn)
        
        self.matchCaseCheck = QtWidgets.QCheckBox("Aa")
        self.matchCaseCheck.setToolTip("Match Case")
        findLayout.addWidget(self.matchCaseCheck)
        
        self.wholeWordCheck = QtWidgets.QCheckBox("Ab|")
        self.wholeWordCheck.setToolTip("Match Whole Word")
        findLayout.addWidget(self.wholeWordCheck)
        
        self.regexCheck = QtWidgets.QCheckBox(".*")
        self.regexCheck.setToolTip("Use Regular Expression")
        findLayout.addWidget(self.regexCheck)
        
        self.findMatchLabel = QtWidgets.QLabel("")
        self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        findLayout.addWidget(self.findMatchLabel)
        
        findLayout.addStretch()
        
        closeBtn = QtWidgets.QPushButton("✕")
        closeBtn.setFixedSize(32, 32)
        closeBtn.setToolTip("Close (Esc)")
        closeBtn.clicked.connect(self.hide_find_replace)
        closeBtn.setStyleSheet("""
            QPushButton {
                background: #3c3c3c;
                border: 1px solid #3e3e42;
                color: #cccccc;
                font-size: 20px;
                font-weight: bold;
                border-radius: 2px;
            }
            QPushButton:hover {
                background: #f48771;
                color: #ffffff;
                border-color: #f48771;
            }
            QPushButton:pressed {
                background: #d16957;
            }
        """)
        findLayout.addWidget(closeBtn)
        
        mainLayout.addLayout(findLayout)
        
        # Replace row (initially hidden)
        self.replaceRow = QtWidgets.QWidget()
        replaceLayout = QtWidgets.QHBoxLayout(self.replaceRow)
        replaceLayout.setContentsMargins(0, 0, 0, 0)
        replaceLayout.setSpacing(6)
        
        # Spacer to align with find input
        spacer = QtWidgets.QLabel("")
        spacer.setFixedWidth(20)
        replaceLayout.addWidget(spacer)
        
        # Replace icon
        replaceIconLabel = QtWidgets.QLabel()
        replace_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "replace.png")
        if os.path.exists(replace_icon_path):
            pixmap = QtGui.QPixmap(replace_icon_path).scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            replaceIconLabel.setPixmap(pixmap)
        else:
            replaceIconLabel.setText("🔄")
        replaceIconLabel.setFixedWidth(20)
        replaceLayout.addWidget(replaceIconLabel)
        
        self.replaceInput = QtWidgets.QLineEdit()
        self.replaceInput.setPlaceholderText("Replace")
        self.replaceInput.setMinimumWidth(250)
        replaceLayout.addWidget(self.replaceInput)
        
        # Replace button with icon
        self.replaceBtn = QtWidgets.QPushButton()
        if os.path.exists(replace_icon_path):
            self.replaceBtn.setIcon(QtGui.QIcon(replace_icon_path))
            self.replaceBtn.setIconSize(QtCore.QSize(16, 16))
        self.replaceBtn.setText("Replace")
        self.replaceBtn.setFixedHeight(26)
        self.replaceBtn.clicked.connect(self.replace_current)
        replaceLayout.addWidget(self.replaceBtn)
        
        # Replace All button with icon
        self.replaceAllBtn = QtWidgets.QPushButton()
        if os.path.exists(replace_icon_path):
            self.replaceAllBtn.setIcon(QtGui.QIcon(replace_icon_path))
            self.replaceAllBtn.setIconSize(QtCore.QSize(16, 16))
        self.replaceAllBtn.setText("Replace All")
        self.replaceAllBtn.setFixedHeight(26)
        self.replaceAllBtn.clicked.connect(self.replace_all)
        replaceLayout.addWidget(self.replaceAllBtn)
        
        replaceLayout.addStretch()
        
        mainLayout.addWidget(self.replaceRow)
        self.replaceRow.hide()
        
        parent_layout.addWidget(self.findReplaceWidget)
        self.findReplaceWidget.hide()
    
    def show_find(self):
        """Show find widget (Ctrl+F)"""
        self.findReplaceWidget.show()
        self.replaceRow.hide()
        self.toggleReplaceBtn.setText("▶")
        self.findInput.setFocus()
        self.findInput.selectAll()
        
        # Pre-fill with selected text if any
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'textCursor'):
            cursor = current_widget.textCursor()
            if cursor.hasSelection():
                self.findInput.setText(cursor.selectedText())
    
    def show_replace(self):
        """Show find and replace widget (Ctrl+H)"""
        self.findReplaceWidget.show()
        self.replaceRow.show()
        self.toggleReplaceBtn.setText("▼")
        self.findInput.setFocus()
        self.findInput.selectAll()
        
        # Pre-fill with selected text if any
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, 'textCursor'):
            cursor = current_widget.textCursor()
            if cursor.hasSelection():
                self.findInput.setText(cursor.selectedText())
    
    def toggle_replace_mode(self):
        """Toggle replace row visibility"""
        if self.replaceRow.isVisible():
            self.replaceRow.hide()
            self.toggleReplaceBtn.setText("▶")
        else:
            self.replaceRow.show()
            self.toggleReplaceBtn.setText("▼")
    
    def hide_find_replace(self):
        """Hide find/replace widget"""
        self.findReplaceWidget.hide()
        
        # Clear all highlights when closing
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            if hasattr(current_widget, 'setExtraSelections'):
                current_widget.setExtraSelections([])
            current_widget.setFocus()
    
    def find_next(self):
        """Find next occurrence"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'find'):
            return
        
        search_text = self.findInput.text()
        if not search_text:
            return
        
        # Build find flags
        flags = QtGui.QTextDocument.FindFlags()
        if self.matchCaseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.wholeWordCheck.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        
        # Try to find
        found = current_widget.find(search_text, flags)
        
        if not found:
            # Wrap around from beginning
            cursor = current_widget.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            current_widget.setTextCursor(cursor)
            found = current_widget.find(search_text, flags)
            
            if not found:
                self.findMatchLabel.setText("No matches found")
                self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
            else:
                self.findMatchLabel.setText("Wrapped")
                self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        else:
            self.update_match_count()
    
    def find_previous(self):
        """Find previous occurrence"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'find'):
            return
        
        search_text = self.findInput.text()
        if not search_text:
            return
        
        # Build find flags with backward flag
        flags = QtGui.QTextDocument.FindBackward
        if self.matchCaseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.wholeWordCheck.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        
        # Try to find
        found = current_widget.find(search_text, flags)
        
        if not found:
            # Wrap around from end
            cursor = current_widget.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            current_widget.setTextCursor(cursor)
            found = current_widget.find(search_text, flags)
            
            if not found:
                self.findMatchLabel.setText("No matches found")
                self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
            else:
                self.findMatchLabel.setText("Wrapped")
                self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        else:
            self.update_match_count()
    
    def replace_current(self):
        """Replace current selection"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'textCursor'):
            return
        
        cursor = current_widget.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.findInput.text():
            cursor.insertText(self.replaceInput.text())
            # Find next after replacing
            self.find_next()
    
    def replace_all(self):
        """Replace all occurrences"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'toPlainText'):
            return
        
        search_text = self.findInput.text()
        replace_text = self.replaceInput.text()
        
        if not search_text:
            return
        
        # Get all text
        text = current_widget.toPlainText()
        
        # Count occurrences
        if self.matchCaseCheck.isChecked():
            count = text.count(search_text)
        else:
            count = text.lower().count(search_text.lower())
        
        if count == 0:
            self.findMatchLabel.setText("No matches found")
            self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
            return
        
        # Replace all
        if self.matchCaseCheck.isChecked():
            new_text = text.replace(search_text, replace_text)
        else:
            # Case-insensitive replace
            import re
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            new_text = pattern.sub(replace_text, text)
        
        # Update document
        current_widget.setPlainText(new_text)
        
        self.findMatchLabel.setText(f"Replaced {count} occurrence{'s' if count > 1 else ''}")
        self.findMatchLabel.setStyleSheet("color: #4ec9b0; font-size: 11px;")
    
    def update_match_count(self):
        """Update match count label"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'toPlainText'):
            return
        
        search_text = self.findInput.text()
        if not search_text:
            self.findMatchLabel.setText("")
            return
        
        text = current_widget.toPlainText()
        
        if self.matchCaseCheck.isChecked():
            count = text.count(search_text)
        else:
            count = text.lower().count(search_text.lower())
        
        if count > 0:
            self.findMatchLabel.setText(f"{count} match{'es' if count > 1 else ''}")
            self.findMatchLabel.setStyleSheet("color: #858585; font-size: 11px;")
        else:
            self.findMatchLabel.setText("No matches")
            self.findMatchLabel.setStyleSheet("color: #f48771; font-size: 11px;")
    
    def on_find_text_changed(self, text):
        """Handle real-time highlighting as user types in find field"""
        if not text:
            # Clear all highlights
            self.findMatchLabel.setText("")
            current_widget = self.tab_widget.currentWidget()
            if current_widget and hasattr(current_widget, 'setExtraSelections'):
                current_widget.setExtraSelections([])
            return
        
        current_widget = self.tab_widget.currentWidget()
        if not current_widget or not hasattr(current_widget, 'toPlainText'):
            return
        
        # Highlight all matches
        extra_selections = []
        
        # Build find flags
        flags = QtGui.QTextDocument.FindFlags()
        if self.matchCaseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if self.wholeWordCheck.isChecked():
            flags |= QtGui.QTextDocument.FindWholeWords
        
        # Find all occurrences
        cursor = QtGui.QTextCursor(current_widget.document())
        highlight_color = QtGui.QColor("#00ff41")  # Matrix green highlight
        
        while True:
            cursor = current_widget.document().find(text, cursor, flags)
            if cursor.isNull():
                break
            
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(highlight_color)
            selection.format.setForeground(QtGui.QColor("#000000"))  # Black text for contrast
            extra_selections.append(selection)
        
        current_widget.setExtraSelections(extra_selections)
        
        # Update match count
        self.update_match_count()
    
    def is_visible(self):
        """Check if find/replace widget is visible"""
        return self.findReplaceWidget and self.findReplaceWidget.isVisible()
