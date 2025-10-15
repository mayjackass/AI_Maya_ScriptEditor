"""
Chat Manager
Handles Morpheus AI chat interface, provider/model selection, and all AI interactions
"""
import html
import os
import re
import uuid
import difflib
import traceback
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
        
        # Action buttons for code suggestions
        self.actionButtonsWidget = None
        self.currentCodeBlockId = None
        
        # Thinking animation
        self.thinkingTimer = QtCore.QTimer()
        self.thinkingTimer.timeout.connect(self.animate_thinking)
        self.thinkingDots = 0
        
        # AI instances
        self.morpheus = None
        self.morpheus_manager = None
        
        # Offline mode toggle
        self.offline_mode = False
        self.offlineToggle = None
        
        # Code blocks storage
        self._code_blocks = {}
        self._code_block_html = {}
        
        # User messages storage for editing (msg_id -> conversation index in morpheus_manager.chat_history)
        self._user_messages = {}
        
        # Model selector connection tracking
        self._model_selector_connected = False
        
    def build_chat_dock(self):
        """Build Morpheus AI chat dock"""
        # Check for custom icon
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
        
        # New chat button with icon from assets
        self.newChatBtn = QtWidgets.QPushButton(" New")
        new_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "replace.png")
        if os.path.exists(new_icon_path):
            self.newChatBtn.setIcon(QtGui.QIcon(new_icon_path))
            self.newChatBtn.setIconSize(QtCore.QSize(14, 14))
        else:
            self.newChatBtn.setText("✨ New")  # Fallback to emoji if icon not found
        self.newChatBtn.setToolTip("Start new conversation")
        self.newChatBtn.clicked.connect(self.new_conversation)
        
        # Offline mode toggle
        self.offlineToggle = QtWidgets.QPushButton("🌐 Online")
        self.offlineToggle.setCheckable(True)
        self.offlineToggle.setChecked(False)  # Default to online mode
        self.offlineToggle.setToolTip("Toggle between online and offline mode")
        self.offlineToggle.setStyleSheet("""
            QPushButton {
                background: #238636;
                border: 1px solid #2ea043;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2ea043;
            }
            QPushButton:checked {
                background: #da3633;
                border: 1px solid #f85149;
            }
            QPushButton:checked:hover {
                background: #f85149;
            }
        """)
        self.offlineToggle.clicked.connect(self.toggle_offline_mode)
        
        historyLayout.addWidget(self.prevChatBtn)
        historyLayout.addWidget(self.historyLabel)
        historyLayout.addWidget(self.nextChatBtn)
        historyLayout.addStretch()
        historyLayout.addWidget(self.offlineToggle)
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

        # Response indicator
        self.responseIndicator = QtWidgets.QLabel()
        self.responseIndicator.setText("Morpheus is pondering...")
        self.responseIndicator.setStyleSheet("""
            QLabel {
                color: #00ff41;
                font-family: "Segoe UI", Consolas, monospace;
                font-size: 12px;
                padding: 4px 8px;
                background: rgba(0, 255, 65, 0.1);
                border: 1px solid rgba(0, 255, 65, 0.2);
                border-radius: 4px;
            }
        """)
        self.responseIndicator.setVisible(False)
        chatLayout.addWidget(self.responseIndicator)

        # Action buttons widget (hidden by default, appears above input when there's a code suggestion)
        self.actionButtonsWidget = QtWidgets.QWidget()
        actionButtonsLayout = QtWidgets.QHBoxLayout(self.actionButtonsWidget)
        actionButtonsLayout.setContentsMargins(0, 0, 0, 0)
        actionButtonsLayout.setSpacing(8)
        
        self.keepBtn = QtWidgets.QPushButton("Keep")
        self.keepBtn.setToolTip("Apply this code to your editor")
        self.keepBtn.setStyleSheet("""
            QPushButton {
                background: #238636;
                border: 1px solid #2ea043;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        
        self.copyBtn = QtWidgets.QPushButton("Copy")
        self.copyBtn.setToolTip("Copy code to clipboard")
        self.copyBtn.setStyleSheet("""
            QPushButton {
                background: #00cc33;
                border: 1px solid #00ff41;
                color: #000000;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover { background: #00ff41; }
        """)
        
        self.undoBtn = QtWidgets.QPushButton("Undo")
        self.undoBtn.setToolTip("Undo last code change")
        self.undoBtn.setStyleSheet("""
            QPushButton {
                background: #da3633;
                border: 1px solid #f85149;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
            }
            QPushButton:hover { background: #f85149; }
        """)
        
        actionButtonsLayout.addWidget(self.keepBtn)
        actionButtonsLayout.addWidget(self.copyBtn)
        actionButtonsLayout.addWidget(self.undoBtn)
        actionButtonsLayout.addStretch()
        
        self.actionButtonsWidget.setVisible(False)  # Hidden by default
        chatLayout.addWidget(self.actionButtonsWidget)

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
            QComboBox:hover { border-color: #00ff41; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b949e;
            }
            QComboBox QAbstractItemView {
                background: #21262d;
                border: 1px solid #30363d;
                selection-background-color: transparent;
                color: #f0f6fc;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px 8px;
                min-height: 20px;
                border-left: 3px solid transparent;
            }
            QComboBox QAbstractItemView::item:selected {
                border-left: 3px solid #00ff41;
                background: transparent;
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
            QTextEdit:focus { border-color: #00ff41; }
        """)
        
        # Override key press for Enter to send
        self.chatInput.keyPressEvent = self.chat_key_press_event
        
        # Send button (paper plane icon)
        self.sendBtn = QtWidgets.QPushButton("✈")
        self.sendBtn.setFixedSize(40, 60)
        self.sendBtn.setToolTip("Send message (Enter)")
        self.sendBtn.setCursor(QtCore.Qt.PointingHandCursor)
        self.sendBtn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #30363d;
                color: #00ff41;
                border-radius: 6px;
                font-size: 18px;
            }
            QPushButton:hover { 
                background: #30363d;
                border-color: #00ff41;
            }
            QPushButton:disabled {
                color: #484848;
                border-color: #30363d;
            }
        """)
        self.sendBtn.clicked.connect(self.send_message)

        # Create horizontal layout for input and send button
        inputRowLayout = QtWidgets.QHBoxLayout()
        inputRowLayout.setSpacing(8)
        inputRowLayout.addWidget(self.chatInput)
        inputRowLayout.addWidget(self.sendBtn)
        
        inputLayout.addLayout(inputRowLayout)
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
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "morpheus.png")
            if os.path.exists(icon_path):
                # Create small icon HTML for chat messages
                # Convert Windows backslashes to forward slashes for HTML file URL
                icon_url = icon_path.replace('\\', '/')
                self.morpheus_icon_html = f'<img src="file:///{icon_url}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;">'
            else:
                self.morpheus_icon_html = "🤖"
            
            if self.morpheus.client:
                self.chatHistory.append(f"""<div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; color: #00ff41;">{self.morpheus_icon_html} <b>Hello, I'm Morpheus.</b><br><br>
                I'm your AI assistant for Maya scripting. Ask me about Python, MEL, or any coding challenges you're facing.<br><br></div>""")
                # Load previous chat history if available
                if self.morpheus_manager and self.morpheus_manager.chat_history:
                    self.load_current_conversation()
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
        self.add_chat_message("You", message, "#00ff41")
        
        # Show thinking indicator
        self.show_thinking_indicator()
        
        # Clear input
        self.chatInput.clear()
        
        # Disable send button
        self.sendBtn.setEnabled(False)
        
        # Smart detection: Only include code context if user is asking about code
        # Don't include code for greetings, thanks, or general questions
        message_lower = message.lower()
        
        # Keywords that indicate user wants code help
        code_keywords = ['fix', 'error', 'bug', 'wrong', 'broken', 'issue', 'problem', 
                        'explain', 'what does', 'how does', 'why', 'review', 'check',
                        'optimize', 'improve', 'refactor', 'help with', 'this code']
        
        # Keywords that indicate just conversation (don't include code)
        conversation_keywords = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'ok', 
                                'okay', 'cool', 'nice', 'good', 'great', 'bye']
        
        # Check if it's just a greeting/conversation
        is_conversation = any(message_lower.strip().startswith(kw) for kw in conversation_keywords)
        is_conversation = is_conversation or any(kw == message_lower.strip() for kw in conversation_keywords)
        
        # Check if user is asking about code
        is_code_question = any(kw in message_lower for kw in code_keywords)
        
        # Auto-detect and include current editor code (like GitHub Copilot)
        # BUT ONLY if user is actually asking about code
        context = ""
        current_editor = self.parent.tabWidget.currentWidget()
        
        if current_editor and is_code_question and not is_conversation:
            code = current_editor.toPlainText().strip()
            if code:  # Only include if there's actual code
                # Get file info
                tab_index = self.parent.tabWidget.indexOf(current_editor)
                tab_name = self.parent.tabWidget.tabText(tab_index)
                language = current_editor.get_language()
                lang = "python" if language == "python" else "mel"
                
                # Count lines for better AI instruction
                line_count = len(code.split('\n'))
                
                # 🎯 Get current syntax errors (like VS Code diagnostics)
                errors = current_editor.get_syntax_errors() if hasattr(current_editor, 'get_syntax_errors') else []
                error_context = ""
                if errors:
                    error_context = "\n\n[SYNTAX ERRORS DETECTED]:\n"
                    for error in errors[:5]:  # Limit to first 5 errors
                        line_num = error.get('line', 0) + 1  # Convert to 1-based
                        msg = error.get('message', 'Unknown error')
                        error_context += f"  Line {line_num}: {msg}\n"
                
                # Auto-include code context with EXPLICIT instructions for targeted responses
                context = f"""[Current Editor Context - {tab_name} ({language.upper()}) - {line_count} lines]{error_context}

⚠️ IMPORTANT: The code below is for REFERENCE ONLY.
If the user asks to fix/review: ONLY return the 1-5 lines that need fixing.
DO NOT return all {line_count} lines back - only return the problematic section.

```{lang}
{code}
```

[User Question]
{message}

[Response Instructions]
- If fixing an error: Return ONLY the broken line(s) with the fix
- If reviewing: Point out issues and show ONLY the fix
- DO NOT echo back the entire {line_count} lines of code"""

        # Send to Morpheus
        if self.morpheus_manager:
            # If offline mode is enabled, force offline response
            if hasattr(self, 'offline_mode') and self.offline_mode:
                # Force offline mode by using mock response directly
                response = self.morpheus_manager._generate_mock_response(message, context if context else "")
                self.morpheus_manager.record_conversation(message, response)
                QtCore.QTimer.singleShot(500, lambda: self.on_morpheus_response(response))
            else:
                # Send with context if available, otherwise just the message
                self.morpheus_manager.send_message(context if context else message, code if context else "")
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
                # Matrix green color with regular font for better readability
                text_color = "#00ff41"  # Matrix green
                text_style = "font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; color: #00ff41; line-height: 1.4;"
                html_message = f"""
                <div class="morpheus-response" style="margin-bottom: 16px; padding: 8px; border-left: 3px solid {color}; background: rgba(255,255,255,0.03);">
                    <div style="color: {color}; font-weight: 600; margin-bottom: 4px;">
                        {sender_display} <span style="color: #8b949e; font-size: 11px; font-weight: normal;">{timestamp}</span>
                    </div>
                    <div style="{text_style}">
                        {formatted_message}
                    </div>
                </div>
                <br>
                """
                    
            else:
                # User message - store with ID for editing
                msg_id = str(uuid.uuid4())[:8]
                
                formatted_message = html.escape(message).replace('\n', '<br>')
                sender_display = sender
                text_color = "#f0f6fc"
                text_style = "color: #f0f6fc; line-height: 1.4;"
                
                # Make user messages clickable with edit link
                html_message = f"""
                <div id="user-msg-{msg_id}" class="user-message user-msg-{msg_id}" style="margin-bottom: 16px; padding: 8px; border-left: 3px solid {color}; background: rgba(255,255,255,0.03);">
                    <div style="color: {color}; font-weight: 600; margin-bottom: 4px;">
                        {sender_display} <span style="color: #8b949e; font-size: 11px; font-weight: normal;">{timestamp}</span>
                        <a href="edit:{msg_id}" style="color: #58a6ff; text-decoration: none; font-size: 11px; margin-left: 8px;">✎ edit</a>
                    </div>
                    <div style="{text_style}">
                        {formatted_message}
                    </div>
                </div>
                <br>
                """
                
                # Map msg_id to the conversation index in morpheus_manager.chat_history
                # This will be the NEXT index when the response is recorded
                if self.morpheus_manager:
                    conversation_index = len(self.morpheus_manager.chat_history)
                    self._user_messages[msg_id] = {
                        'message': message,
                        'conversation_index': conversation_index
                    }
            
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
            block_id = str(uuid.uuid4())[:8]
            
            # Store code
            self._code_blocks[block_id] = raw_code
            
            # Determine if this is a targeted fix (≤10 lines) or full code
            line_count = len(raw_code.split('\n'))
            is_targeted = line_count <= 10
            
            # Format code block with indicator
            escaped_code = html.escape(raw_code)
            placeholder = f"___CODE_BLOCK_{block_id}___"
            
            # Different styling based on code size
            if is_targeted:
                code_type = "Targeted Fix"
                code_type_color = "#238636"  # Green
                badge_bg = "#1f2d1f"
            else:
                code_type = f"Full Code ({line_count} lines)"
                code_type_color = "#1f6feb"  # Blue
                badge_bg = "#1a2332"
            
            code_html = f'''
<div style="margin: 8px 0; border: 1px solid #30363d; border-radius: 4px; background-color: #0d1117; font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;">
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 4px 12px; background-color: #161b22; border-bottom: 1px solid #30363d;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="color: #f0f6fc; font-size: 12px; font-weight: 600;">Python</span>
            <span style="background: {badge_bg}; color: {code_type_color}; padding: 1px 6px; border-radius: 10px; font-size: 10px; font-weight: 600;">{code_type}</span>
        </div>
        <a href="copy_{block_id}" style="color: #00ff41; text-decoration: none; font-size: 12px; font-weight: 500;">Copy code</a>
    </div>
    <div style="padding: 10px;">
        <pre style="margin: 0; color: #e6edf3; font-size: 13px; line-height: 1.4; white-space: pre-wrap; font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;">{escaped_code}</pre>
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
        
        # Show action buttons and notify about code blocks
        if current_placeholders:
            count = len(current_placeholders)
            msg = f"Multiple code suggestions available ({count} blocks)" if count > 1 else "Code suggestion available"
            # 🎯 AUTOMATICALLY show inline diff preview for the latest code block
            if self._code_blocks:
                self.currentCodeBlockId = list(self._code_blocks.keys())[-1]
                latest_code = self._code_blocks[self.currentCodeBlockId]
                QtCore.QTimer.singleShot(100, lambda: self._auto_show_inline_diff(latest_code))
        
        return formatted_message
    
    def handle_code_action(self, url):
        """Handle code action button clicks and edit message links"""
        try:
            url_str = url.toString()
            
            # Handle edit message links
            if url_str.startswith('edit:'):
                msg_id = url_str.replace('edit:', '')
                if msg_id in self._user_messages:
                    # Get original message
                    msg_data = self._user_messages[msg_id]
                    original_message = msg_data['message']
                    
                    print(f"\n=== EDIT CLICKED ===")
                    print(f"Message ID: {msg_id}")
                    print(f"Original message: {original_message[:50]}...")
                    print("====================\n")
                    
                    # Remove this conversation and ALL conversations after it (like ChatGPT)
                    self.remove_message_and_response(msg_id)
                    
                    # Show edit dialog
                    self.show_edit_message_dialog(original_message)
                return
            
            if '_' not in url_str:
                return
                
            action, block_id = url_str.split('_', 1)
            
            if block_id not in self._code_blocks:
                QtWidgets.QMessageBox.information(self.parent, "Code Block Not Found", 
                    f"The requested code block '{block_id}' could not be found.")
                return
                
            code = self._code_blocks[block_id]
            
            # Only handle copy action now
            if action == "copy":
                self.copy_code_to_clipboard(code)
            
            # Ensure chat is preserved
            QtCore.QTimer.singleShot(100, self.ensure_chat_preserved)
                
        except Exception as e:
            QtWidgets.QMessageBox.information(self.parent, "Action Error", f"Failed to handle code action: {str(e)}")
    
    def copy_code_to_clipboard(self, code):
        """Copy code to clipboard"""
        try:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(code)
            self.parent.dock_manager.console.append_tagged("SUCCESS", "[OK] Code copied to clipboard!", "#28a745")
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to copy code: {e}", "#dc3545")

    def undo_editor_change(self):
        """Undo last change in editor"""
        try:
            editor = self.get_active_editor()
            if editor:
                editor.undo()
                self.parent.dock_manager.console.append_tagged("SUCCESS", "↶ Undo applied!", "#28a745")
            else:
                self.parent.dock_manager.console.append_tagged("WARNING", "No active editor. Create or open a file first.", "#fd7e14")
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to undo: {e}", "#dc3545")
    
    def _keep_and_hide(self, code):
        """Keep code and hide action buttons"""
        self.keep_as_fix(code)
        self.actionButtonsWidget.setVisible(False)
    
    def _copy_and_hide(self, code):
        """Copy code and hide action buttons"""
        self.copy_code_to_clipboard(code)
        self.actionButtonsWidget.setVisible(False)
    
    def _undo_and_hide(self):
        """Undo and hide action buttons"""
        self.undo_editor_change()
        self.actionButtonsWidget.setVisible(False)
    
    def _auto_show_inline_diff(self, code):
        """Automatically show inline diff preview when AI suggests code"""
        try:
            editor = self.get_active_editor()
            if not editor:
                return
            
            current_code = editor.toPlainText()
            
            # Only auto-show for non-empty editors
            if not current_code.strip():
                return
            
            print(f"\n🔍 _auto_show_inline_diff() called")
            print(f"   AI suggested code: {code[:100]}...")
            
            # 🎯 Get current syntax errors (like GitHub Copilot uses VS Code diagnostics)
            errors = editor.get_syntax_errors() if hasattr(editor, 'get_syntax_errors') else []
            hint_line = None
            
            if errors:
                # Error line numbers from syntax checker are 1-based, convert to 0-based for editor
                error_line_1based = errors[0].get('line', 1)
                hint_line = error_line_1based - 1  # Convert to 0-based
                error_msg = errors[0].get('message', 'Unknown error')
                print(f"   🎯 Found {len(errors)} error(s)")
                print(f"   🔴 First error at line {error_line_1based} (1-based) = line {hint_line} (0-based): {error_msg}")
                print(f"   💡 Will use 0-based line {hint_line} as the target for inline diff")
                
                # 🎯 FORCE use the error line - don't do similarity matching!
                # This is exactly what GitHub Copilot does
                current_lines = current_code.split('\n')
                if 0 <= hint_line < len(current_lines):
                    replacement_info = {
                        'start_line': hint_line,
                        'end_line': hint_line + 1,
                        'old_code': current_lines[hint_line],
                        'match_quality': 1.0  # Forced match
                    }
                    print(f"   ✅ Using error line {hint_line} (0-based) directly (GitHub Copilot style)")
                    print(f"   Old code: {current_lines[hint_line][:80]}...")
                    
                    # Show inline diff preview with red/green highlighting
                    editor.show_inline_replacement(replacement_info, code)
                    self.parent.dock_manager.console.append_tagged("MORPHEUS", "[INFO] Inline diff preview shown in editor", "#00ff41")
                    return
            else:
                # Fallback to cursor position
                cursor = editor.textCursor()
                hint_line = cursor.blockNumber()  # 0-based
                print(f"   📍 No errors found, using cursor position at line {hint_line}")
            
            # Try to find matching code to replace
            replacement_info = self.find_code_to_replace(current_code, code, hint_line=hint_line)
            
            if replacement_info:
                print(f"   ✅ Found replacement at line {replacement_info.get('start_line')}")
                print(f"   Old code matched: {replacement_info.get('old_code')[:80]}...")
                
                # Show inline diff preview with red/green highlighting
                editor.show_inline_replacement(replacement_info, code)
                self.parent.dock_manager.console.append_tagged("MORPHEUS", "[INFO] Inline diff preview shown in editor", "#00ff41")
            else:
                print(f"   ❌ No match found for AI code")
            
        except Exception as e:
            print(f"Auto inline diff error: {e}")
            traceback.print_exc()

    def keep_as_fix(self, code):
        """Show inline replacement preview for code fixes"""
        try:
            editor = self.get_active_editor()
            if not editor:
                self.parent.dock_manager.console.append_tagged("WARNING", "No active editor. Create or open a file first.", "#fd7e14")
                return
            
            current_code = editor.toPlainText()
            
            # If editor is empty, just insert the code
            if not current_code.strip():
                editor.setPlainText(code)
                self.parent.dock_manager.console.append_tagged("SUCCESS", "[OK] Code inserted!", "#28a745")
                return
            
            # Try to find the best match for replacement
            replacement_info = self.find_code_to_replace(current_code, code)
            
            if replacement_info:
                # Show inline diff preview in the editor with red/green highlighting
                editor.show_inline_replacement(replacement_info, code)
                self.parent.dock_manager.console.append_tagged("INFO", "[INFO] Review the suggested changes in the editor", "#00ff41")
            else:
                # If no match found, insert at cursor position
                cursor = editor.textCursor()
                cursor.insertText("\n" + code + "\n")
                editor.setTextCursor(cursor)
                self.parent.dock_manager.console.append_tagged("SUCCESS", "[OK] Code inserted at cursor!", "#28a745")
                
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to apply fix: {e}", "#dc3545")
    
    def find_code_to_replace(self, current_code, suggested_code, hint_line=None):
        """Find the best matching code section to replace - optimized for targeted fixes with context awareness
        
        Args:
            current_code: The full current code in the editor
            suggested_code: The AI-suggested fix code
            hint_line: Optional line number (0-based) where user's cursor is, as a hint for the error location
        """
        current_lines = current_code.split('\n')
        suggested_lines = suggested_code.split('\n')
        
        # 🎯 Strategy 0: If hint_line provided, check that line first
        if hint_line is not None and 0 <= hint_line < len(current_lines):
            print(f"   🎯 Strategy 0: Checking hint line {hint_line}")
            hint_line_text = current_lines[hint_line].strip()
            suggested_line = suggested_lines[0].strip() if len(suggested_lines) > 0 else ""
            
            if len(hint_line_text) >= 5 and len(suggested_line) >= 5:
                similarity = difflib.SequenceMatcher(None, hint_line_text, suggested_line).ratio()
                print(f"      Hint line: '{hint_line_text[:60]}...'")
                print(f"      Suggested: '{suggested_line[:60]}...'")
                print(f"      Similarity: {similarity:.2f}")
                
                # If somewhat similar (60%+), use the hint line
                if similarity >= 0.6:
                    print(f"   ✅ Strategy 0 SUCCESS: Using hint line {hint_line}")
                    return {
                        'start_line': hint_line,
                        'end_line': hint_line + 1,
                        'old_code': current_lines[hint_line],
                        'match_quality': similarity
                    }
        
        # Strategy 1: Smart line matching with context (for single-line fixes)
        if len(suggested_lines) == 1:
            # Single line fix - need to be smart about which occurrence
            suggested_line = suggested_lines[0].strip()
            
            # Skip if suggested line is too short (likely not meaningful)
            if len(suggested_line) < 5:
                print(f"   ⚠️ Strategy 1 skipped: suggested line too short ({len(suggested_line)} chars)")
                return None
            
            # Look for lines that are SIMILAR but not exact (the fixed version)
            best_match_line = -1
            best_similarity = 0
            
            print(f"   🔍 Strategy 1: Looking for line similar to: '{suggested_line[:60]}...'")
            
            for i, current_line in enumerate(current_lines):
                current_stripped = current_line.strip()
                
                # Skip very short lines (unlikely to be meaningful)
                if len(current_stripped) < 5:
                    continue
                
                # Skip exact matches (we want to find the broken version)
                if current_stripped == suggested_line:
                    continue
                
                # Calculate similarity (looking for "almost the same")
                similarity = difflib.SequenceMatcher(None, 
                    current_stripped, 
                    suggested_line).ratio()
                
                # If very similar (75-95%), this is likely the broken line
                if 0.75 <= similarity < 1.0 and similarity > best_similarity:
                    best_match_line = i
                    best_similarity = similarity
                    print(f"      Line {i}: similarity {similarity:.2f} - '{current_stripped[:60]}...'")
            
            if best_match_line >= 0 and best_similarity >= 0.75:
                # Found the broken line that needs fixing
                print(f"   ✅ Strategy 1 match: line {best_match_line}, similarity {best_similarity:.2f}")
                return {
                    'start_line': best_match_line,
                    'end_line': best_match_line + 1,
                    'old_code': current_lines[best_match_line],
                    'match_quality': best_similarity
                }
            else:
                print(f"   ❌ Strategy 1 failed: best similarity was {best_similarity:.2f}")
        
        # Strategy 2: Try exact substring match (for multi-line targeted fixes)
        suggested_text = suggested_code.strip()
        if len(suggested_lines) > 1 and suggested_text in current_code:
            # Find the position of the exact match
            start_pos = current_code.find(suggested_text)
            lines_before = current_code[:start_pos].count('\n')
            lines_in_match = suggested_text.count('\n') + 1
            
            return {
                'start_line': lines_before,
                'end_line': lines_before + lines_in_match,
                'old_code': suggested_text,  # Exact match, so old = new
                'match_quality': 1.0  # Perfect match
            }
        
        # Strategy 3: Use difflib to find similar sections (for modified fixes)
        matcher = difflib.SequenceMatcher(None, current_lines, suggested_lines)
        
        # Find the longest matching block
        match = matcher.find_longest_match(0, len(current_lines), 0, len(suggested_lines))
        
        # Lower threshold for small fixes (AI now returns only the problem area)
        min_match_size = min(2, len(suggested_lines) - 1)  # At least 2 lines or suggested-1
        
        if match.size >= min_match_size:  
            # Found a section to replace
            start_line = match.a
            end_line = start_line + match.size
            
            # For small suggested fixes, don't expand context too much
            if len(suggested_lines) <= 5:
                # Small fix - minimal context
                context_start = max(0, start_line)
                context_end = min(len(current_lines), end_line + 1)
            else:
                # Larger fix - include more context
                context_start = max(0, start_line - 2)
                context_end = min(len(current_lines), end_line + 2)
            
            return {
                'start_line': context_start,
                'end_line': context_end,
                'old_code': '\n'.join(current_lines[context_start:context_end]),
                'match_quality': match.size / max(len(suggested_lines), 1)
            }
        
        # Strategy 3: Try fuzzy matching for single-line or very small fixes
        if len(suggested_lines) <= 3:
            best_match_ratio = 0
            best_match_line = -1
            
            for i, current_line in enumerate(current_lines):
                # Compare each line
                ratio = difflib.SequenceMatcher(None, current_line.strip(), suggested_lines[0].strip()).ratio()
                if ratio > best_match_ratio and ratio > 0.6:  # 60% similarity threshold
                    best_match_ratio = ratio
                    best_match_line = i
            
            if best_match_line >= 0:
                # Found a fuzzy match
                return {
                    'start_line': best_match_line,
                    'end_line': best_match_line + len(suggested_lines),
                    'old_code': '\n'.join(current_lines[best_match_line:best_match_line + len(suggested_lines)]),
                    'match_quality': best_match_ratio
                }
        
        return None
    
    def show_replacement_preview(self, editor, replacement_info, new_code):
        """Show VSCode-style diff preview dialog"""
        from .dialog_styles import apply_dark_theme
        
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("Preview Changes")
        dialog.setMinimumSize(800, 600)
        
        # Apply consistent dark theme
        apply_dark_theme(dialog)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Title
        title = QtWidgets.QLabel("📝 Preview code replacement")
        layout.addWidget(title)
        
        # Create split view
        splitWidget = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        
        # Left side - Current code (what will be removed)
        leftLayout = QtWidgets.QVBoxLayout()
        leftLabel = QtWidgets.QLabel(f"🔴 Current (Lines {replacement_info['start_line']+1}-{replacement_info['end_line']})")
        leftLayout.addWidget(leftLabel)
        
        oldCodeView = QtWidgets.QTextEdit()
        oldCodeView.setReadOnly(True)
        oldCodeView.setPlainText(replacement_info['old_code'])
        oldCodeView.setStyleSheet(oldCodeView.styleSheet() + "background: #2d1f1f;")  # Red tint
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(leftLayout)
        leftLayout.addWidget(oldCodeView)
        
        # Right side - New code (what will be added)
        rightLayout = QtWidgets.QVBoxLayout()
        rightLabel = QtWidgets.QLabel("🟢 Suggested (replacement)")
        rightLayout.addWidget(rightLabel)
        
        newCodeView = QtWidgets.QTextEdit()
        newCodeView.setReadOnly(True)
        newCodeView.setPlainText(new_code)
        newCodeView.setStyleSheet(newCodeView.styleSheet() + "background: #1f2d1f;")  # Green tint
        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(rightLayout)
        rightLayout.addWidget(newCodeView)
        
        splitWidget.addWidget(leftWidget)
        splitWidget.addWidget(rightWidget)
        layout.addWidget(splitWidget)
        
        # Info label
        match_quality = replacement_info['match_quality'] * 100
        infoLabel = QtWidgets.QLabel(f"ℹ️ Match confidence: {match_quality:.0f}% | This will replace lines {replacement_info['start_line']+1}-{replacement_info['end_line']}")
        infoLabel.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: normal; padding: 8px;")
        layout.addWidget(infoLabel)
        
        # Buttons
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        
        cancelBtn = QtWidgets.QPushButton("Cancel")
        cancelBtn.setObjectName("cancelBtn")
        cancelBtn.clicked.connect(dialog.reject)
        
        acceptBtn = QtWidgets.QPushButton("✓ Keep Changes")
        acceptBtn.clicked.connect(dialog.accept)
        
        buttonLayout.addWidget(cancelBtn)
        buttonLayout.addWidget(acceptBtn)
        layout.addLayout(buttonLayout)
        
        # Show dialog and apply if accepted
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.apply_replacement(editor, replacement_info, new_code)
    
    def show_replacement_options(self, editor, code):
        """Show options when no direct match is found"""
        dialog = QtWidgets.QMessageBox(self.parent)
        dialog.setWindowTitle("How to apply this code?")
        dialog.setStyleSheet("""
            QMessageBox {
                background: #0d1117;
            }
            QLabel {
                color: #f0f6fc;
                font-size: 13px;
            }
        """)
        dialog.setIcon(QtWidgets.QMessageBox.Question)
        dialog.setText("Could not find matching code to replace.\n\nHow would you like to apply the suggested code?")
        
        replaceAllBtn = dialog.addButton("Replace All", QtWidgets.QMessageBox.DestructiveRole)
        appendBtn = dialog.addButton("Append to End", QtWidgets.QMessageBox.AcceptRole)
        cancelBtn = dialog.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
        
        dialog.exec_()
        clicked = dialog.clickedButton()
        
        if clicked == replaceAllBtn:
            editor.setPlainText(code)
            self.parent.dock_manager.console.append_tagged("SUCCESS", "🔧 Replaced entire content!", "#28a745")
        elif clicked == appendBtn:
            cursor = editor.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText("\n\n" + code)
            self.parent.dock_manager.console.append_tagged("SUCCESS", "➕ Code appended to end!", "#28a745")
    
    def apply_replacement(self, editor, replacement_info, new_code):
        """Apply the replacement to the editor"""
        try:
            current_text = editor.toPlainText()
            lines = current_text.split('\n')
            
            # Replace the section
            new_lines = (
                lines[:replacement_info['start_line']] +
                new_code.split('\n') +
                lines[replacement_info['end_line']:]
            )
            
            # Apply to editor
            editor.setPlainText('\n'.join(new_lines))
            
            # Move cursor to the replaced section
            cursor = editor.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            for _ in range(replacement_info['start_line']):
                cursor.movePosition(QtGui.QTextCursor.Down)
            editor.setTextCursor(cursor)
            
            self.parent.dock_manager.console.append_tagged(
                "SUCCESS", 
                f"✅ Replaced lines {replacement_info['start_line']+1}-{replacement_info['end_line']}!", 
                "#28a745"
            )
        except Exception as e:
            self.parent.dock_manager.console.append_tagged("ERROR", f"Failed to apply replacement: {e}", "#dc3545")

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
        self.responseIndicator.setText(f"Morpheus is pondering{dots}")
        self.thinkingDots += 1

    def chat_key_press_event(self, event):
        """Handle Enter key in chat input"""
        if event.key() == QtCore.Qt.Key_Return and not (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.send_message()
        else:
            QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)

    def toggle_offline_mode(self):
        """Toggle between online and offline mode"""
        self.offline_mode = self.offlineToggle.isChecked()
        
        if self.offline_mode:
            self.offlineToggle.setText("📵 Offline")
            self.add_chat_message("System", "Switched to offline mode. Morpheus will use built-in responses.", "#f0f6fc")
        else:
            self.offlineToggle.setText("🌐 Online")
            self.add_chat_message("System", "Switched to online mode. Morpheus will use AI responses.", "#f0f6fc")

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
        """Clear chat display and tracking"""
        self.chatHistory.clear()
        self._user_messages.clear()  # Clear edit tracking when clearing chat
        self._code_blocks.clear()
        self._code_block_html.clear()

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
        
        # Clear code blocks and user messages tracking
        self._code_blocks.clear()
        self._code_block_html.clear()
        self._user_messages.clear()  # Clear edit message tracking when reloading
        
        # Load conversation
        if self.morpheus_manager.current_chat_index >= 0:
            current_conversation = self.morpheus_manager.get_current_conversation()
            if current_conversation and isinstance(current_conversation, dict):
                if 'user' in current_conversation and 'ai' in current_conversation:
                    self.add_chat_message("You", current_conversation['user'], "#00ff41")
                    self.add_chat_message("Morpheus", current_conversation['ai'], "#238636")
        else:
            # Load all conversations
            full_history = self.morpheus_manager.chat_history
            if full_history and isinstance(full_history, list):
                for entry in full_history:
                    if isinstance(entry, dict):
                        if 'user' in entry and 'ai' in entry:
                            self.add_chat_message("You", entry['user'], "#00ff41")
                            self.add_chat_message("Morpheus", entry['ai'], "#238636")
                        elif 'role' in entry and 'content' in entry:
                            if entry['role'] == 'user':
                                self.add_chat_message("You", entry['content'], "#00ff41")
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
        from .dialog_styles import apply_dark_theme
        
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("AI Provider Settings")
        dialog.setMinimumWidth(500)
        
        # Apply consistent dark theme
        apply_dark_theme(dialog)
        
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
        cancel_btn.setObjectName("cancelBtn")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_settings():
            provider = "claude" if "Claude" in provider_combo.currentText() else "openai"
            settings.setValue("AI_PROVIDER", provider)
            
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
    
    def remove_message_and_response(self, msg_id):
        """Remove a conversation and ALL conversations after it (like ChatGPT edit)"""
        try:
            if msg_id not in self._user_messages:
                print(f"Message ID {msg_id} not found in storage")
                return
            
            if not self.morpheus_manager:
                print("No morpheus_manager available")
                return
            
            # Get the conversation index
            msg_data = self._user_messages[msg_id]
            conversation_index = msg_data['conversation_index']
            
            print(f"\n=== REMOVING CONVERSATIONS ===")
            print(f"Message ID: {msg_id}")
            print(f"Conversation index: {conversation_index}")
            print(f"Total conversations before: {len(self.morpheus_manager.chat_history)}")
            print(f"Removing {len(self.morpheus_manager.chat_history) - conversation_index} conversations")
            
            # Remove from morpheus_manager.chat_history (this is the persistent storage)
            self.morpheus_manager.chat_history = self.morpheus_manager.chat_history[:conversation_index]
            
            # Also update the persistent memory
            if hasattr(self.morpheus_manager, 'memory') and 'conversations' in self.morpheus_manager.memory:
                self.morpheus_manager.memory['conversations'] = self.morpheus_manager.chat_history.copy()
                self.morpheus_manager._save_memory()
            
            # Clear user messages mapping for removed conversations
            self._user_messages = {
                mid: data for mid, data in self._user_messages.items()
                if data['conversation_index'] < conversation_index
            }
            
            # Reload the chat display
            self.load_current_conversation()
            
            print(f"Total conversations after: {len(self.morpheus_manager.chat_history)}")
            print("==============================\n")
            
        except Exception as e:
            print(f"Error removing conversations: {e}")
            import traceback
            traceback.print_exc()
            print(f"Error removing messages: {e}")
            import traceback
            traceback.print_exc()
            print(f"Error removing message: {e}")
            import traceback
            traceback.print_exc()
            print(f"Error removing message: {e}")
            import traceback
            traceback.print_exc()
    
    def show_edit_message_dialog(self, original_message):
        """Show dialog to edit and resend a message"""
        from .dialog_styles import apply_dark_theme
        
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("Edit Message")
        dialog.setMinimumSize(500, 300)
        
        apply_dark_theme(dialog)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Label
        label = QtWidgets.QLabel("Edit your message and send it to Morpheus again:")
        label.setStyleSheet("color: #c9d1d9; font-size: 13px;")
        layout.addWidget(label)
        
        # Text edit with original message
        text_edit = QtWidgets.QPlainTextEdit()
        text_edit.setPlainText(original_message)
        text_edit.setStyleSheet("""
            QPlainTextEdit {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                color: #c9d1d9;
                font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
            QPlainTextEdit:focus {
                border-color: #58a6ff;
            }
        """)
        layout.addWidget(text_edit, 1)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #21262d;
                border: 1px solid #30363d;
                color: #c9d1d9;
                padding: 6px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #30363d;
                border-color: #8b949e;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        send_btn = QtWidgets.QPushButton("Send to Morpheus")
        send_btn.setStyleSheet("""
            QPushButton {
                background: #238636;
                border: 1px solid #2ea043;
                color: white;
                padding: 6px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2ea043;
            }
        """)
        
        def send_edited_message():
            edited_text = text_edit.toPlainText().strip()
            if edited_text:
                # Clear input and set edited message
                self.chatInput.clear()
                self.chatInput.setPlainText(edited_text)
                # Send the message
                self.send_message()
                dialog.accept()
        
        send_btn.clicked.connect(send_edited_message)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(send_btn)
        layout.addLayout(button_layout)
        
        # Focus on text edit and select all
        text_edit.setFocus()
        text_edit.selectAll()
        
        dialog.exec()
