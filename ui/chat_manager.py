"""
Chat Manager
Handles Morpheus AI chat interface, provider/model selection, and all AI interactions
"""
import html
import re
from PySide6 import QtWidgets, QtCore, QtGui


class ChatManager:
    """Manages Morpheus AI chat interface and AI provider integration"""
    
    def __init__(self, parent):
        """
        Initialize ChatManager
        
        Args:
            parent: Main window instance
        """
        self.parent = parent
        
        # Chat UI widgets
        self.chatHistory = None
        self.chatInput = None
        self.sendBtn = None
        self.responseIndicator = None
        self.prevChatBtn = None
        self.nextChatBtn = None
        self.newChatBtn = None
        self.historyLabel = None
        self.provider_selector = None
        self.model_selector = None
        
        # Thinking animation
        self.thinkingTimer = QtCore.QTimer()
        self.thinkingTimer.timeout.connect(self.animate_thinking)
        self.thinkingDots = 0
        
        # AI instances
        self.morpheus = None
        self.morpheus_manager = None
        
        # Code blocks storage
        self._code_blocks = {}
        self._code_block_html = {}
        
        # Model selector connection tracking
        self._model_selector_connected = False
        
    def build_chat_dock(self):
        """Build Morpheus AI chat dock"""
        # Check for custom icon
        import os
        from PySide6 import QtGui
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "morpheus.png")
        
        # Create dock
        chatDock = QtWidgets.QDockWidget(self.parent)
        chatDock.setObjectName("MorpheusDock")
        chatDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        chatDock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | 
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable
        )
        
        # Create custom title widget with buttons (no icon to avoid clutter)
        titleWidget = QtWidgets.QWidget()
        titleLayout = QtWidgets.QHBoxLayout(titleWidget)
        titleLayout.setContentsMargins(8, 4, 8, 4)
        titleLayout.setSpacing(6)
        
        # Add title text only
        titleLabel = QtWidgets.QLabel("Morpheus AI")
        titleLabel.setStyleSheet("color: #f0f6fc; font-weight: 500; font-size: 13px;")
        
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()
        
        # Add float/detach button
        floatBtn = QtWidgets.QPushButton("⇄")
        floatBtn.setFixedSize(24, 24)
        floatBtn.setToolTip("Float/Dock")
        floatBtn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8b949e;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #30363d; color: #f0f6fc; }
        """)
        floatBtn.clicked.connect(lambda: chatDock.setFloating(not chatDock.isFloating()))
        
        # Add close button
        closeBtn = QtWidgets.QPushButton("✕")
        closeBtn.setFixedSize(24, 24)
        closeBtn.setToolTip("Close")
        closeBtn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8b949e;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #da3633; color: white; }
        """)
        closeBtn.clicked.connect(chatDock.close)
        
        titleLayout.addWidget(floatBtn)
        titleLayout.addWidget(closeBtn)
        
        chatDock.setTitleBarWidget(titleWidget)
        
        # Create chat widget container
        chatWidget = QtWidgets.QWidget(chatDock)
        chatLayout = QtWidgets.QVBoxLayout(chatWidget)
        chatLayout.setContentsMargins(6, 6, 6, 6)
        chatLayout.setSpacing(6)

        # Chat history navigation
        historyLayout = QtWidgets.QHBoxLayout()
        historyLayout.setSpacing(4)
        historyLayout.setContentsMargins(8, 4, 8, 4)
        
        self.prevChatBtn = QtWidgets.QPushButton("◀")
        self.prevChatBtn.setFixedSize(24, 24)
        self.prevChatBtn.setToolTip("Previous conversation")
        self.prevChatBtn.clicked.connect(self.prev_conversation)
        
        self.nextChatBtn = QtWidgets.QPushButton("▶")
        self.nextChatBtn.setFixedSize(24, 24)
        self.nextChatBtn.setToolTip("Next conversation")
        self.nextChatBtn.clicked.connect(self.next_conversation)
        
        self.historyLabel = QtWidgets.QLabel("1/1")
        self.historyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.historyLabel.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        self.newChatBtn = QtWidgets.QPushButton("✨ New")
        self.newChatBtn.setToolTip("Start new conversation")
        self.newChatBtn.clicked.connect(self.new_conversation)
        
        historyLayout.addWidget(self.prevChatBtn)
        historyLayout.addWidget(self.historyLabel)
        historyLayout.addWidget(self.nextChatBtn)
        historyLayout.addStretch()
        historyLayout.addWidget(self.newChatBtn)
        
        chatLayout.addLayout(historyLayout)

        # Chat history display
        self.chatHistory = QtWidgets.QTextBrowser()
        self.chatHistory.setOpenExternalLinks(False)
        self.chatHistory.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.chatHistory.anchorClicked.connect(self.handle_code_action)
        self.chatHistory.setStyleSheet("""
            QTextBrowser {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
                font-size: 13px;
                line-height: 1.5;
                color: #f0f6fc;
            }
        """)
        chatLayout.addWidget(self.chatHistory, 1)

        # Response indicator (use Morpheus icon text for consistency)
        self.responseIndicator = QtWidgets.QLabel()
        self.responseIndicator.setText("⏳ Morpheus is pondering...")
        self.responseIndicator.setStyleSheet("""
            QLabel {
                color: #7c3aed;
                font-family: "Segoe UI", Consolas, monospace;
                font-size: 12px;
                padding: 4px 8px;
                background: rgba(124, 58, 237, 0.1);
                border: 1px solid rgba(124, 58, 237, 0.2);
                border-radius: 4px;
            }
        """)
        self.responseIndicator.setVisible(False)
        chatLayout.addWidget(self.responseIndicator)

        # Input area
        inputWidget = QtWidgets.QWidget()
        inputLayout = QtWidgets.QVBoxLayout(inputWidget)
        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.setSpacing(4)

        # Provider & Model selectors
        provider_layout = QtWidgets.QHBoxLayout()
        provider_layout.setSpacing(8)
        
        provider_label = QtWidgets.QLabel("AI Provider:")
        provider_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        self.provider_selector = QtWidgets.QComboBox()
        self.provider_selector.addItems(["GPT-4o (OpenAI)", "Claude Sonnet (Anthropic)"])
        self.provider_selector.setStyleSheet("""
            QComboBox {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 4px 8px;
                color: #f0f6fc;
                font-size: 11px;
            }
            QComboBox:hover { border-color: #58a6ff; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b949e;
            }
        """)
        
        model_label = QtWidgets.QLabel("Model:")
        model_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        self.model_selector = QtWidgets.QComboBox()
        self.model_selector.setStyleSheet(self.provider_selector.styleSheet())
        
        # Load saved provider preference
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        self.provider_selector.setCurrentText("Claude Sonnet (Anthropic)" if current_provider == "claude" else "GPT-4o (OpenAI)")
        
        # Connect provider change
        self.provider_selector.currentTextChanged.connect(self.on_provider_changed)
        
        # Initialize model list
        self.update_model_list()
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_selector, 1)
        provider_layout.addWidget(model_label)
        provider_layout.addWidget(self.model_selector, 1)
        
        inputLayout.addLayout(provider_layout)

        # Text input
        self.chatInput = QtWidgets.QTextEdit()
        self.chatInput.setMaximumHeight(60)
        self.chatInput.setPlaceholderText("Ask Morpheus anything about your code...")
        self.chatInput.setStyleSheet("""
            QTextEdit {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                color: #f0f6fc;
                font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
                font-size: 13px;
            }
            QTextEdit:focus { border-color: #58a6ff; }
        """)
        
        # Override key press for Enter to send
        self.chatInput.keyPressEvent = self.chat_key_press_event
        
        # Send button
        self.sendBtn = QtWidgets.QPushButton("Send")
        self.sendBtn.setStyleSheet("""
            QPushButton {
                background: #238636;
                border: 1px solid #30363d;
                color: white;
                padding: 6px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        self.sendBtn.clicked.connect(self.send_message)

        inputLayout.addWidget(self.chatInput)
        inputLayout.addWidget(self.sendBtn)
        chatLayout.addWidget(inputWidget)

        chatDock.setWidget(chatWidget)
        chatDock.visibilityChanged.connect(lambda visible: self.parent.dock_manager.sync_morpheus_action(visible))
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, chatDock)
        
        # Store reference
        self.parent.dock_manager.chat_dock = chatDock

        # Initialize Morpheus AI
        self.initialize_morpheus()
        
        return chatDock
    
    def initialize_morpheus(self):
        """Initialize Morpheus AI system"""
        try:
            from ai.chat import AIMorpheus
            from ai.copilot_manager import MorpheusManager
            
            self.morpheus = AIMorpheus(self.parent)
            self.morpheus_manager = MorpheusManager(self.parent)
            
            self.morpheus_manager.contextUpdated.connect(
                lambda msg: (self.parent.dock_manager.console.append(f"[AI] Context updated: {msg[:50]}...") 
                           if hasattr(self.parent.dock_manager, 'console') and self.parent.dock_manager.console else None)
            )
            self.morpheus_manager.historyUpdated.connect(self.on_history_updated)
            self.morpheus_manager.responseReady.connect(self.on_morpheus_response)
            
            # Load Morpheus icon for messages
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "morpheus.png")
            if os.path.exists(icon_path):
                # Create small icon HTML for chat messages
                self.morpheus_icon_html = f'<img src="file:///{icon_path}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;">'
            else:
                self.morpheus_icon_html = "🤖"
            
            if self.morpheus.client:
                self.chatHistory.append(f"""{self.morpheus_icon_html} <b>Welcome, Neo.</b><br><br>
                <i>I can only show you the door. You're the one that has to walk through it.</i><br><br>
                Ask me anything about your code.<br><br>""")
            else:
                self.chatHistory.append(f"[!] <b>Morpheus AI</b> - No API key found. Set your API key in Tools → Settings.<br><br>")
        except Exception as e:
            print(f"Morpheus AI initialization failed: {e}")
            self.chatHistory.append(f"[X] <b>Morpheus AI initialization failed:</b> {e}<br><br>")
            self.morpheus = None
            self.morpheus_manager = None
    
    def send_message(self):
        """Send message to Morpheus AI"""
        message = self.chatInput.toPlainText().strip()
        if not message:
            return

        # Add user message
        self.add_chat_message("You", message, "#58a6ff")
        
        # Show thinking indicator
        self.show_thinking_indicator()
        
        # Clear input
        self.chatInput.clear()
        
        # Disable send button
        self.sendBtn.setEnabled(False)
        
        # Get context
        context = ""
        current_editor = self.parent.tabWidget.currentWidget()
        
        # Auto-include code for error/bug questions
        auto_keywords = ['error', 'syntax', 'bug', 'fix', 'wrong', 'issue', 'problem', 'incorrect', 'mistake']
        should_auto_include = any(kw in message.lower() for kw in auto_keywords)
        
        if should_auto_include and current_editor:
            context = current_editor.toPlainText()

        # Send to Morpheus
        if self.morpheus_manager:
            self.morpheus_manager.send_message(message, context)
        else:
            self.add_chat_message("Morpheus", "AI service not available. Check your API key.", "#ff6b6b")
            self.sendBtn.setEnabled(True)
    
    def add_chat_message(self, sender, message, color="#f0f6fc"):
        """Add message to chat history"""
        timestamp = QtCore.QTime.currentTime().toString("hh:mm")
        
        try:
            # Format Morpheus messages (process code blocks)
            if sender == "Morpheus":
                formatted_message = self.format_morpheus_message(message)
                # Use Morpheus icon instead of text
                sender_display = f"{self.morpheus_icon_html} {sender}"
            else:
                formatted_message = html.escape(message).replace('\n', '<br>')
                sender_display = sender
            
            html_message = f"""
            <div style="margin-bottom: 16px; padding: 8px; border-left: 3px solid {color}; background: rgba(255,255,255,0.03);">
                <div style="color: {color}; font-weight: 600; margin-bottom: 4px;">
                    {sender_display} <span style="color: #8b949e; font-size: 11px; font-weight: normal;">{timestamp}</span>
                </div>
                <div style="color: #f0f6fc; line-height: 1.4;">
                    {formatted_message}
                </div>
            </div>
            <br>
            """
            
            cursor = self.chatHistory.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertHtml(html_message)
            
            # Scroll to bottom
            scrollbar = self.chatHistory.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            # Fallback
            simple_message = f"\n{sender} [{timestamp}]: {message}\n"
            cursor = self.chatHistory.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(simple_message)
            print(f"Chat formatting error: {e}")
    
    def format_morpheus_message(self, message):
        """Format Morpheus message with code block actions"""
        # Pattern for code blocks
        code_block_pattern = r'```(?:python|py)?\s*(.*?)```'
        
        # Store placeholders
        current_placeholders = {}
        
        def extract_and_store_code(match):
            raw_code = match.group(1).strip()
            if not raw_code:
                return ""
            
            # Generate unique ID
            import uuid
            block_id = str(uuid.uuid4())[:8]
            
            # Store code
            self._code_blocks[block_id] = raw_code
            
            # Format code block
            escaped_code = html.escape(raw_code)
            placeholder = f"___CODE_BLOCK_{block_id}___"
            
            code_html = f'''
<div style="margin: 16px 0; border: 1px solid #30363d; border-radius: 6px; background-color: #0d1117; font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;">
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; background-color: #161b22; border-bottom: 1px solid #30363d;">
        <span style="color: #f0f6fc; font-size: 14px; font-weight: 600;">Python</span>
        <div style="display: flex; gap: 16px;">
            <a href="copy_{block_id}" style="color: #58a6ff; text-decoration: none; font-size: 14px;">Copy code</a>
            <a href="apply_{block_id}" style="color: #238636; text-decoration: none; font-size: 14px;">Apply to editor</a>
            <a href="fix_{block_id}" style="color: #f85149; text-decoration: none; font-size: 14px;">Keep as fix</a>
        </div>
    </div>
    <div style="padding: 16px;">
        <pre style="margin: 0; color: #e6edf3; font-size: 14px; line-height: 1.5; white-space: pre-wrap; font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;">{escaped_code}</pre>
    </div>
</div>
'''
            
            self._code_block_html[placeholder] = code_html
            current_placeholders[placeholder] = code_html
            
            return placeholder
        
        # Replace code blocks with placeholders
        processed_message = re.sub(code_block_pattern, extract_and_store_code, message, flags=re.DOTALL)
        
        # Escape HTML
        formatted_message = html.escape(processed_message)
        
        # Replace placeholders with code blocks
        for placeholder, code_html in current_placeholders.items():
            formatted_message = formatted_message.replace(placeholder, code_html)
        
        # Convert newlines
        formatted_message = formatted_message.replace('\n', '<br>')
        
        # Notify about code blocks
        if current_placeholders:
            count = len(current_placeholders)
            msg = f"Multiple code suggestions available ({count} blocks)" if count > 1 else "Code suggestion available"
            self.parent.dock_manager.console.append_tagged("MORPHEUS", f"{msg} - click Copy/Apply/Keep buttons", "#58a6ff")
        
        return formatted_message
    
    def handle_code_action(self, url):
        """Handle code action button clicks"""
        try:
            url_str = url.toString()
            
            if '_' not in url_str:
                return
                
            action, block_id = url_str.split('_', 1)
            
            if block_id not in self._code_blocks:
                QtWidgets.QMessageBox.information(self.parent, "Code Block Not Found", 
                    f"The requested code block '{block_id}' could not be found.")
                return
                
            code = self._code_blocks[block_id]
            
            if action == "copy":
                self.copy_code_to_clipboard(code)
            elif action == "apply":
                self.apply_code_to_editor(code)
            elif action == "fix":
                self.keep_as_fix(code)
            
            # Ensure chat is preserved
            QtCore.QTimer.singleShot(100, self.ensure_chat_preserved)
                
        except Exception as e:
            QtWidgets.QMessageBox.information(self.parent, "Action Error", f"Failed to handle code action: {str(e)}")
    
    def copy_code_to_clipboard(self, code):
        """Copy code to clipboard"""
        try:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(code)
            self.parent.dock_manager.console.append_tagged("SUCCESS", "📋 Code copied to clipboard!", "#28a745")
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to copy code: {e}", "#dc3545")

    def apply_code_to_editor(self, code):
        """Apply code to current editor"""
        try:
            editor = self.get_active_editor()
            if editor:
                cursor = editor.textCursor()
                cursor.insertText(code)
                self.parent.dock_manager.console.append_tagged("SUCCESS", "✅ Code applied to editor!", "#28a745")
            else:
                self.parent.dock_manager.console.append_tagged("WARNING", "No active editor. Create or open a file first.", "#fd7e14")
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to apply code: {e}", "#dc3545")

    def keep_as_fix(self, code):
        """Replace editor content with code"""
        try:
            editor = self.get_active_editor()
            if editor:
                editor.setPlainText(code)
                self.parent.dock_manager.console.append_tagged("SUCCESS", "🔧 Code applied as fix (replaced content)!", "#28a745")
            else:
                self.parent.dock_manager.console.append_tagged("WARNING", "No active editor. Create or open a file first.", "#fd7e14")
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to apply fix: {e}", "#dc3545")

    def get_active_editor(self):
        """Get active editor widget"""
        from editor.code_editor import CodeEditor
        w = self.parent.tabWidget.currentWidget()
        return w if isinstance(w, CodeEditor) else None
    
    def ensure_chat_preserved(self):
        """Ensure chat history is preserved"""
        if self.chatHistory.toPlainText().strip() == "":
            print("Chat was cleared, reloading...")
            self.load_current_conversation()
    
    def on_morpheus_response(self, response):
        """Handle Morpheus response"""
        self.hide_thinking_indicator()
        self.add_chat_message("Morpheus", response, "#238636")
    
    def show_thinking_indicator(self):
        """Show thinking indicator"""
        self.responseIndicator.setVisible(True)
        self.thinkingDots = 0
        self.thinkingTimer.start(500)
        
    def hide_thinking_indicator(self):
        """Hide thinking indicator"""
        self.thinkingTimer.stop()
        self.responseIndicator.setVisible(False)
        self.sendBtn.setEnabled(True)
        
    def animate_thinking(self):
        """Animate thinking indicator"""
        dots = "." * (self.thinkingDots % 4)
        self.responseIndicator.setText(f"⏳ Morpheus is pondering{dots}")
        self.thinkingDots += 1

    def chat_key_press_event(self, event):
        """Handle Enter key in chat input"""
        if event.key() == QtCore.Qt.Key_Return and not (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.send_message()
        else:
            QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)

    # History navigation
    def prev_conversation(self):
        """Navigate to previous conversation"""
        if self.morpheus_manager:
            self.morpheus_manager.previous_conversation()
            self.load_current_conversation()
            self.update_history_info()

    def next_conversation(self):
        """Navigate to next conversation"""
        if self.morpheus_manager:
            self.morpheus_manager.next_conversation()
            self.load_current_conversation()
            self.update_history_info()

    def new_conversation(self):
        """Start new conversation"""
        if self.morpheus_manager:
            self.morpheus_manager.new_conversation()
        self.clear_chat()
        self.update_history_info()

    def clear_chat(self):
        """Clear chat display"""
        self.chatHistory.clear()

    def on_history_updated(self, chat_history):
        """Handle history updates"""
        self.update_history_info()
        if (self.chatHistory.toPlainText().strip() == "" and 
            self.morpheus_manager and self.morpheus_manager.chat_history):
            self.load_current_conversation()

    def load_current_conversation(self):
        """Load current conversation history"""
        if not self.morpheus_manager:
            return
            
        self.chatHistory.clear()
        
        # Clear code blocks
        self._code_blocks.clear()
        self._code_block_html.clear()
        
        # Load conversation
        if self.morpheus_manager.current_chat_index >= 0:
            current_conversation = self.morpheus_manager.get_current_conversation()
            if current_conversation and isinstance(current_conversation, dict):
                if 'user' in current_conversation and 'ai' in current_conversation:
                    self.add_chat_message("You", current_conversation['user'], "#58a6ff")
                    self.add_chat_message("Morpheus", current_conversation['ai'], "#238636")
        else:
            # Load all conversations
            full_history = self.morpheus_manager.chat_history
            if full_history and isinstance(full_history, list):
                for entry in full_history:
                    if isinstance(entry, dict):
                        if 'user' in entry and 'ai' in entry:
                            self.add_chat_message("You", entry['user'], "#58a6ff")
                            self.add_chat_message("Morpheus", entry['ai'], "#238636")
                        elif 'role' in entry and 'content' in entry:
                            if entry['role'] == 'user':
                                self.add_chat_message("You", entry['content'], "#58a6ff")
                            else:
                                self.add_chat_message("Morpheus", entry['content'], "#238636")
        
        self.update_history_info()

    def update_history_info(self):
        """Update history navigation info"""
        if not self.morpheus_manager:
            self.historyLabel.setText("1/1")
            self.prevChatBtn.setEnabled(False)
            self.nextChatBtn.setEnabled(False)
            return
            
        current, total = self.morpheus_manager.get_conversation_info()
        
        if self.morpheus_manager.current_chat_index == -1:
            label_text = f"All/{total}"
        else:
            label_text = f"{current}/{total}"
        
        self.historyLabel.setText(label_text)
        
        # Enable/disable buttons
        prev_enabled = total > 0 and (self.morpheus_manager.current_chat_index == -1 or 
                                     self.morpheus_manager.current_chat_index > 0)
        next_enabled = (total > 0 and self.morpheus_manager.current_chat_index != -1 and 
                       self.morpheus_manager.current_chat_index < total - 1)
        
        self.prevChatBtn.setEnabled(prev_enabled)
        self.nextChatBtn.setEnabled(next_enabled)

    # Provider/Model management
    def on_provider_changed(self, text):
        """Handle provider selection change"""
        provider = "claude" if "Claude" in text else "openai"
        
        if self.morpheus:
            self.morpheus.provider = provider
            self.morpheus.client = self.morpheus._make_client()
            
            settings = QtCore.QSettings("AI_Script_Editor", "settings")
            settings.setValue("AI_PROVIDER", provider)
            
            self.update_model_list()
            
            provider_name = "Claude Sonnet" if provider == "claude" else "GPT-4o"
            if self.morpheus.client:
                print(f"✓ Switched to {provider_name}")
            else:
                print(f"⚠ Switched to {provider_name} but no API key found")

    def update_model_list(self):
        """Update model selector based on current provider"""
        if not self.model_selector:
            return
        
        self.model_selector.blockSignals(True)
        self.model_selector.clear()
        
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        
        if current_provider == "openai":
            models = [
                ("GPT-4o Mini (Fast, Cheap)", "gpt-4o-mini"),
                ("GPT-4o (Most Capable)", "gpt-4o"),
                ("GPT-4 Turbo", "gpt-4-turbo"),
                ("o1-preview (Reasoning)", "o1-preview"),
                ("o1-mini (Fast Reasoning)", "o1-mini"),
            ]
            saved_model = settings.value("OPENAI_MODEL", "gpt-4o-mini")
        else:
            models = [
                ("Claude Sonnet 4 (Latest)", "claude-sonnet-4-20250514"),
                ("Claude Opus 4 (Most Capable)", "claude-opus-4-20250514"),
                ("Claude Sonnet 3.5 (Legacy)", "claude-3-5-sonnet-20241022"),
                ("Claude Haiku 3.5 (Fast)", "claude-3-5-haiku-20241022"),
            ]
            saved_model = settings.value("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        
        for display_name, model_id in models:
            self.model_selector.addItem(display_name, model_id)
        
        for i in range(self.model_selector.count()):
            if self.model_selector.itemData(i) == saved_model:
                self.model_selector.setCurrentIndex(i)
                break
        
        self.model_selector.blockSignals(False)
        
        # Reconnect signal
        if self._model_selector_connected:
            try:
                self.model_selector.currentIndexChanged.disconnect(self.on_model_changed)
            except (RuntimeError, TypeError):
                pass
        
        self.model_selector.currentIndexChanged.connect(self.on_model_changed)
        self._model_selector_connected = True

    def on_model_changed(self, index):
        """Handle model selection change"""
        if not self.model_selector or index < 0:
            return
            
        model_id = self.model_selector.itemData(index)
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        
        if current_provider == "openai":
            settings.setValue("OPENAI_MODEL", model_id)
        else:
            settings.setValue("CLAUDE_MODEL", model_id)
        
        if self.morpheus:
            self.morpheus.current_model = model_id
        
        print(f"✓ Switched to model: {self.model_selector.currentText()}")

    def show_settings_dialog(self):
        """Show AI provider settings dialog"""
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("AI Provider Settings")
        dialog.setMinimumWidth(500)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Provider selection
        provider_group = QtWidgets.QGroupBox("AI Provider")
        provider_layout = QtWidgets.QVBoxLayout()
        
        provider_combo = QtWidgets.QComboBox()
        provider_combo.addItems(["OpenAI (GPT-4o)", "Claude (Anthropic)"])
        
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        current_provider = settings.value("AI_PROVIDER", "openai")
        provider_combo.setCurrentText("Claude (Anthropic)" if current_provider == "claude" else "OpenAI (GPT-4o)")
        
        provider_layout.addWidget(QtWidgets.QLabel("Select AI Provider:"))
        provider_layout.addWidget(provider_combo)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # OpenAI settings
        openai_group = QtWidgets.QGroupBox("OpenAI Settings")
        openai_layout = QtWidgets.QFormLayout()
        
        openai_key_input = QtWidgets.QLineEdit()
        openai_key_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        openai_key_input.setPlaceholderText("sk-...")
        openai_key_input.setText(settings.value("OPENAI_API_KEY", ""))
        
        openai_layout.addRow("API Key:", openai_key_input)
        openai_layout.addRow("", QtWidgets.QLabel('<a href="https://platform.openai.com/api-keys">Get API Key</a>'))
        openai_group.setLayout(openai_layout)
        layout.addWidget(openai_group)
        
        # Anthropic settings
        claude_group = QtWidgets.QGroupBox("Anthropic (Claude) Settings")
        claude_layout = QtWidgets.QFormLayout()
        
        claude_key_input = QtWidgets.QLineEdit()
        claude_key_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        claude_key_input.setPlaceholderText("sk-ant-...")
        claude_key_input.setText(settings.value("ANTHROPIC_API_KEY", ""))
        
        claude_layout.addRow("API Key:", claude_key_input)
        claude_layout.addRow("", QtWidgets.QLabel('<a href="https://console.anthropic.com/settings/keys">Get API Key</a>'))
        claude_group.setLayout(claude_layout)
        layout.addWidget(claude_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_settings():
            provider = "claude" if "Claude" in provider_combo.currentText() else "openai"
            settings.setValue("AI_PROVIDER", provider)
            
            import os
            if openai_key_input.text():
                settings.setValue("OPENAI_API_KEY", openai_key_input.text())
                os.environ["OPENAI_API_KEY"] = openai_key_input.text()
            
            if claude_key_input.text():
                settings.setValue("ANTHROPIC_API_KEY", claude_key_input.text())
                os.environ["ANTHROPIC_API_KEY"] = claude_key_input.text()
            
            if self.morpheus:
                self.morpheus.provider = provider
                self.morpheus.client = self.morpheus._make_client()
                if self.morpheus.client:
                    QtWidgets.QMessageBox.information(dialog, "Success", 
                        f"Successfully connected to {provider.upper()}!")
                else:
                    QtWidgets.QMessageBox.warning(dialog, "Warning", 
                        f"Settings saved but failed to connect to {provider.upper()}. Check your API key.")
            
            dialog.accept()
        
        save_btn.clicked.connect(save_settings)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
