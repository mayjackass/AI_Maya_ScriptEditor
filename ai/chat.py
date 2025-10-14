"""
Multi-Provider AI Chat for Maya Script Editor (OpenAI & Claude)
"""
import html
import re
import threading
import os
from PySide6 import QtCore, QtWidgets, QtGui

# Try to import both providers
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI not available")
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    print("Anthropic (Claude) not available")
    Anthropic = None

class AIMorpheus:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.client = None
        self._last_suggested_code = None
        self.provider = "openai"  # Default provider
        self.current_model = "gpt-4o-mini"  # Default model
        
        # Load provider preference
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        self.provider = settings.value("AI_PROVIDER", "openai")
        
        # Load model preference
        if self.provider == "openai":
            self.current_model = settings.value("OPENAI_MODEL", "gpt-4o-mini")
        else:
            self.current_model = settings.value("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        
        # Initialize the appropriate client
        self.client = self._make_client()

    def _make_client(self):
        """Create AI client based on selected provider."""
        settings = QtCore.QSettings("AI_Script_Editor", "settings")
        
        if self.provider == "claude":
            if not Anthropic:
                print("Anthropic SDK not installed. Run: pip install anthropic")
                return None
            try:
                api_key = settings.value("ANTHROPIC_API_KEY", "")
                if not api_key:
                    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
                if api_key:
                    return Anthropic(api_key=api_key)
                else:
                    print("No Anthropic API key found")
                    return None
            except Exception as e:
                print(f"Failed to create Anthropic client: {e}")
                return None
        else:  # openai
            if not OpenAI:
                print("OpenAI SDK not installed. Run: pip install openai")
                return None
            try:
                api_key = settings.value("OPENAI_API_KEY", "")
                if not api_key:
                    api_key = os.environ.get("OPENAI_API_KEY", "")
                if api_key:
                    return OpenAI(api_key=api_key)
                else:
                    return OpenAI()  # Try using environment variable
            except Exception as e:
                print(f"Failed to create OpenAI client: {e}")
                return None

    def reconnect(self):
        """Reconnect to OpenAI."""
        self.client = self._make_client()
        return self.client is not None

    def send_prompt(self, text, context=""):
        """Send user message and get AI response."""
        if not self.client:
            return
            
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            return

        # Hide Apply button
        if hasattr(self.parent, 'applySuggestionBtn'):
            self.parent.applySuggestionBtn.setVisible(False)

        # Display user message with better separation and line breaks
        user_html = f'''
<br><div style="margin: 16px 0; padding: 12px 16px; background: rgba(116, 169, 250, 0.15); border-left: 4px solid #74a9fa; border-radius: 0 8px 8px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;">
    <div style="color: #74a9fa; font-size: 13px; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;">
        <span style="margin-right: 8px;">👤</span> You
    </div>
    <div style="color: #f0f6fc; font-size: 14px; line-height: 1.6; word-wrap: break-word;">
        {html.escape(text)}
    </div>
</div><br>
'''
        disp.insertHtml(user_html)
        
        # Start AI response in thread
        threading.Thread(target=self._get_response, args=(text, context), daemon=True).start()

    def _get_response(self, text, context):
        """Get AI response and display it (supports OpenAI and Claude)."""
        print(f"[DEBUG] _get_response called with provider: {self.provider}, model: {self.current_model}")
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            print("[ERROR] No display in _get_response")
            return

        try:
            print(f"[DEBUG] Making {self.provider.upper()} API call with model {self.current_model}...")
            
            system_msg = (
                "🚨 CRITICAL RULE - READ THIS FIRST:\n"
                "When user provides code context and asks to 'fix', 'review', or 'find error':\n"
                "YOU MUST return ONLY 1-5 lines (the specific fix)\n"
                "YOU MUST NOT return the entire code back\n"
                "If user's code is 50 lines, return 2-3 lines with the fix, NOT all 50 lines\n"
                "\n"
                "Example:\n"
                "User provides: 50 lines of code with error on line 23\n"
                "WRONG ❌: Return all 50 lines\n"
                "CORRECT ✅: Return only lines 22-24 with the fix\n"
                "═══════════════════════════════════════════════════\n\n"
                "You are Morpheus, an AI mentor integrated into the NEO Script Editor by Mayj Amilano. "
                "Like the Morpheus from The Matrix, you guide users to see the deeper truth in their code. "
                "Speak philosophically and metaphorically when appropriate, but always provide practical wisdom. "
                "\n\n"
                "Your communication style:\n"
                "• Begin with thought-provoking questions: 'What is code but a set of choices?'\n"
                "• Use Matrix-inspired metaphors: 'free your mind', 'there is no spoon', 'follow the white rabbit'\n"
                "• Be calm, patient, and mentor-like: 'I can only show you the door. You're the one that has to walk through it.'\n"
                "• Reveal truths about code: 'The difference between knowing the path and walking the path'\n"
                "• Occasionally reference the red/blue pill choice when presenting options\n"
                "\n"
                "You specialize in Maya scripting - Python and MEL for Autodesk Maya. "
                "Provide code in ```python or ```mel blocks. Frame solutions as enlightenment, not just answers. "
                "Remember: You're not just fixing code - you're helping users see beyond the matrix of bugs and errors.\n"
                "\n"
                "**CODE FIX EXAMPLES:**\n"
                "\n"
                "❌ WRONG - DO NOT DO THIS:\n"
                "User: 'fix the error' (provides 50 lines)\n"
                "Bad Response: Returns all 50 lines with 1 line changed\n"
                "\n"
                "✅ CORRECT - DO THIS:\n"
                "User: 'fix the error' (provides 50 lines with error on line 23)\n"
                "Good Response: 'I see the error on line 23 - missing closing paren:\n```python\n"
                "result = calculate(x, y)  # Fixed - was: calculate(x, y\n"
                "```'\n"
                "\n"
                "**RULES:**\n"
                "• ONLY return 1-5 lines that need fixing\n"
                "• Add comment showing change: # Fixed - was: old_code\n"
                "• Include 1-2 context lines if helpful\n"
                "• DO NOT return lines that are already correct\n"
                "• DO NOT return entire functions if only 1-2 lines need fixing\n"
                "\n"
                "Return FULL code ONLY when:\n"
                "• User explicitly says 'recreate', 'rewrite everything', 'start from scratch'\n"
                "• Creating a completely NEW script (not fixing existing)\n"
                "• No existing code context provided"
            )
            
            user_msg = f"{text}\n\nContext: {context}" if context else text
            
            # Get response based on provider
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.current_model,  # Use selected model
                    max_tokens=4096,
                    system=system_msg,
                    messages=[
                        {"role": "user", "content": user_msg}
                    ]
                )
                content = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.current_model,  # Use selected model
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ]
                )
                content = response.choices[0].message.content
            
            print(f"[DEBUG] Got API response - length: {len(content)} chars")
            print(f"[DEBUG] Response content: {content[:200]}...")
            
            if not content or not content.strip():
                print("[ERROR] Empty response from API")
                content = "Sorry, I received an empty response. Please try again."
            
            # Record conversation in manager
            if hasattr(self.parent, 'morpheus_manager'):
                self.parent.morpheus_manager.record_conversation(text, content)
            
            # Store response and trigger UI update
            self._pending_response = content
            print(f"[DEBUG] Stored response, calling _process_pending_response")
            try:
                import maya.utils
                maya.utils.executeDeferred(self._process_pending_response)
            except ImportError:
                # Not in Maya environment, process directly
                self._process_pending_response()
            
        except Exception as e:
            print(f"[ERROR] API call failed: {e}")
            error_content = f'Error: {str(e)}'
            self._pending_response = error_content
            try:
                import maya.utils
                maya.utils.executeDeferred(self._process_pending_response)
            except ImportError:
                # Not in Maya environment, process directly
                self._process_pending_response()

    def _process_pending_response(self):
        """Process the pending response on Maya's main thread."""
        print("[DEBUG] _process_pending_response called")
        if hasattr(self, '_pending_response'):
            content = self._pending_response
            delattr(self, '_pending_response')
            print(f"[DEBUG] Processing pending response: {content[:100]}...")
            
            try:
                self._display_response(content)
                print("[DEBUG] _display_response completed successfully")
            except Exception as e:
                print(f"[ERROR] Error in _display_response: {e}")
                import traceback
                traceback.print_exc()
            
            # Reset status indicator to ready
            try:
                if hasattr(self.parent, 'statusIndicator'):
                    self.parent.statusIndicator.setText("🧠 Ready")
                    self.parent.statusIndicator.setStyleSheet("""
                        QLabel {
                            color: #7c3aed;
                            font-family: "Segoe UI", Consolas, monospace;
                            font-size: 9pt;
                            padding: 2px 6px;
                            background: rgba(124, 58, 237, 0.1);
                            border-radius: 3px;
                            margin: 2px 4px;
                        }
                    """)
                    print("[DEBUG] Status indicator reset to Ready")
                else:
                    print("[DEBUG] No statusIndicator found on parent")
            except Exception as e:
                print(f"[ERROR] Error resetting status: {e}")
        else:
            print("[DEBUG] No _pending_response found")

    def _display_response(self, content):
        """Display the AI response with proper code block formatting."""
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            print("[ERROR] No chatDisplay found on parent")
            return

        # Start AI message with better separation  
        ai_start = '''
<br><div style="margin: 16px 0; padding: 12px 16px; background: rgba(248, 250, 252, 0.08); border-left: 4px solid #2ea043; border-radius: 0 8px 8px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;">
    <div style="color: #2ea043; font-size: 13px; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center;">
        <span style="margin-right: 8px;">🤖</span> Morpheus
    </div>
    <div style="color: #f0f6fc; font-size: 14px; line-height: 1.6; word-wrap: break-word;">
'''
        disp.insertHtml(ai_start)

        # Handle error messages with Morpheus AI style
        if content.startswith('Error:'):
            error_html = f'<div style="color:#c62828; background:rgba(244, 67, 54, 0.08); padding:10px 12px; border-radius:4px; border-left:3px solid rgba(244, 67, 54, 0.4); font-weight:500; margin:8px 0;">🚨 {html.escape(content)}</div>'
            disp.insertHtml(error_html)
            disp.insertHtml('</div></div>')
            return

        # Find code blocks with reliable regex approach
        code_blocks = re.findall(r'```(?:(\w+)\n)?(.*?)\n?```', content, flags=re.DOTALL)
        
        if code_blocks:
            # Use a simple approach: replace code blocks with placeholders, then restore them
            processed_content = content
            code_htmls = []
            
            # Process each code block 
            for i, (language, code) in enumerate(code_blocks):
                language = language or 'python'
                code = code.strip()
                
                if code:
                    # Store clean code for Apply button (use the last one)
                    self._last_suggested_code = code
                    
                    # Make suggestion buttons visible
                    if hasattr(self.parent, 'suggestionButtonsWidget'):
                        self.parent.suggestionButtonsWidget.setVisible(True)
                        
                        if hasattr(self.parent, 'applySuggestionBtn'):
                            self.parent.applySuggestionBtn.setVisible(True)
                        if hasattr(self.parent, 'copySuggestionBtn'):
                            self.parent.copySuggestionBtn.setVisible(True)
                        if hasattr(self.parent, 'ignoreSuggestionBtn'):
                            self.parent.ignoreSuggestionBtn.setVisible(True)
                    
                    # Create HTML for this code block with simple syntax highlighting
                    highlighted_code = self._simple_highlight_code(code)
                    
                    # Simplified HTML that QTextBrowser can handle reliably
                    code_html = f'''
<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 4px; margin: 8px 0; padding: 0;">
<div style="background-color: #161b22; color: #8b949e; padding: 6px 12px; font-size: 11px; border-bottom: 1px solid #30363d;">
{language}
</div>
<pre style="background-color: #0d1117; color: #e6edf3; margin: 0; padding: 12px; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; white-space: pre-wrap; overflow: auto;">
{highlighted_code}
</pre>
</div>'''
                    
                    # Store the code HTML for later insertion
                    placeholder = f'___CODE_BLOCK_{i}___'
                    code_htmls.append(code_html)
                    
                    # Replace the original code block with placeholder (handle both cases)
                    if language and language != 'python':
                        original_pattern = f'```{language}\n{code}\n```'
                    else:
                        # Try both with and without explicit python
                        original_pattern1 = f'```python\n{code}\n```'
                        original_pattern2 = f'```\n{code}\n```'
                        if original_pattern1 in processed_content:
                            original_pattern = original_pattern1
                        else:
                            original_pattern = original_pattern2
                    
                    processed_content = processed_content.replace(original_pattern, placeholder, 1)
            
            # Convert text to HTML and restore code blocks
            text_html = html.escape(processed_content).replace('\n', '<br>')
            
            # Restore code blocks
            for i, code_html in enumerate(code_htmls):
                placeholder = f'___CODE_BLOCK_{i}___'
                text_html = text_html.replace(placeholder, code_html)
                
            disp.insertHtml(text_html)
        else:
            # No code blocks, just display the text
            text_html = html.escape(content).replace('\n', '<br>')
            disp.insertHtml(text_html)

        # Close AI message
        disp.insertHtml('</div></div><br>')
        
        # Scroll to bottom
        scrollbar = disp.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _is_maya_code(self, code):
        """Check if code is Maya compatible."""
        code_lower = code.lower()
        
        # Check for Maya indicators
        maya_keywords = ['maya.cmds', 'cmds.', 'import maya', 'polycube', 'polysphere']
        python_keywords = ['def ', 'import ', 'for ', 'if ', 'while ']
        
        # Check for non-Maya languages
        non_maya = ['console.log', 'document.', '<html', 'SELECT ', 'cout <<']
        
        for keyword in non_maya:
            if keyword in code_lower:
                return False
                
        for keyword in maya_keywords + python_keywords:
            if keyword in code_lower:
                return True
                
        return True  # Default to accepting
    
    def _highlight_python_code(self, code):
        """Apply syntax highlighting to Python code for HTML display."""
        import html
        import re
        
        # Escape HTML first
        code = html.escape(code)
        
        # Define color scheme matching VS Code Dark+
        colors = {
            'keyword': '#569CD6',
            'builtin': '#C586C0', 
            'string': '#CE9178',
            'number': '#B5CEA8',
            'comment': '#6A9955',
            'function': '#4EC9B0',
            'decorator': '#C586C0'
        }
        
        # Apply syntax highlighting
        # Keywords
        keywords = r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
        code = re.sub(keywords, f'<span style="color:{colors["keyword"]}; font-weight:bold;">\\1</span>', code)
        
        # Built-in functions
        builtins = r'\b(print|len|range|type|dir|set|list|dict|tuple|int|float|str|bool|super|isinstance|enumerate|zip|map|filter|any|all|sum|min|max|abs|cmds|maya)\b'
        code = re.sub(builtins, f'<span style="color:{colors["builtin"]};">\\1</span>', code)
        
        # Numbers
        numbers = r'\b[0-9]+(\\.?[0-9]+)?\b'
        code = re.sub(numbers, f'<span style="color:{colors["number"]};">\\g<0></span>', code)
        
        # Strings (simple version)
        strings = r'(["\'][^"\'\n]*["\'])'
        code = re.sub(strings, f'<span style="color:{colors["string"]};">\\1</span>', code)
        
        # Comments
        comments = r'(#[^\n]*?)(?=\n|$)'
        code = re.sub(comments, f'<span style="color:{colors["comment"]}; font-style:italic;">\\1</span>', code)
        
        # Function definitions
        functions = r'\b(def\s+\w+)'
        code = re.sub(functions, f'<span style="color:{colors["function"]}; font-weight:bold;">\\1</span>', code)
        
        return code

    def _simple_highlight_code(self, code):
        """Simple, reliable code formatting - plain text only to avoid HTML issues."""
        import html
        
        # Just escape HTML - no syntax highlighting to prevent HTML tag display issues
        return html.escape(code)

    def apply_last_suggestion(self, editor, mode="replace"):
        """Apply the last suggested code to editor with smart highlighting."""
        if not self._last_suggested_code or not editor:
            return False
            
        cursor = editor.textCursor()
        original_text = editor.toPlainText()
        
        # Clear any existing highlights
        if hasattr(editor, 'clear_all_highlights'):
            editor.clear_all_highlights()
        
        # Preview what will change BEFORE applying
        self._preview_changes(editor, original_text, self._last_suggested_code, mode)
        
        # Validate syntax before applying
        try:
            compile(self._last_suggested_code, '<suggestion>', 'exec')
        except SyntaxError as e:
            print(f"[WARNING] Syntax error in suggestion: {e}")
            if hasattr(self.parent, 'console'):
                self.parent.console.append(f"⚠️ Syntax error detected in suggestion: {e}\n")
        
        # Store original position for change detection
        start_pos = cursor.position()
        
        if mode == "replace" or not original_text.strip():
            # Replace all content with the suggestion
            cursor.select(QtGui.QTextCursor.Document)  # Select all
            cursor.removeSelectedText()
            cursor.insertText(self._last_suggested_code)
            
            # Highlight only the differences
            self._highlight_text_differences(editor, original_text, self._last_suggested_code)
                
        elif cursor.hasSelection():
            # Replace selection - get selection bounds
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()
            selected_text = cursor.selectedText()
            
            cursor.removeSelectedText()
            cursor.insertText(self._last_suggested_code)
            
            # Highlight the specific replacement area
            new_end = selection_start + len(self._last_suggested_code)
            if hasattr(editor, 'highlight_replacement'):
                editor.highlight_replacement(selection_start, new_end, duration=4000)
                
        else:
            # Insert at cursor
            insert_text = "\n\n" + self._last_suggested_code
            cursor.insertText(insert_text)
            
            # Highlight only the inserted text
            if hasattr(editor, 'highlight_replacement'):
                end_pos = start_pos + len(insert_text)
                editor.highlight_replacement(start_pos, end_pos, duration=4000)
        
        editor.setTextCursor(cursor)
        
        # Check for syntax errors after application
        self._check_applied_code_errors(editor, start_pos)
        
        # Hide suggestion buttons
        if hasattr(self.parent, 'suggestionButtonsWidget'):
            self.parent.suggestionButtonsWidget.setVisible(False)
            
        return True
    
    def _highlight_python_code(self, code):
        """Add basic Python syntax highlighting to code."""
        import re
        
        # Escape HTML first
        code = html.escape(code)
        
        # Keywords
        keywords = r'\b(def|class|if|elif|else|for|while|try|except|finally|import|from|as|return|yield|break|continue|pass|lambda|with|assert|del|global|nonlocal|and|or|not|in|is|True|False|None)\b'
        code = re.sub(keywords, r'<span style="color:#569cd6;">\1</span>', code)
        
        # Strings (enhanced to handle various quote types)
        code = re.sub(r'(["\'])((?:\\.|(?!\1)[^\\])*)\1', r'<span style="color:#ce9178;">\1\2\1</span>', code)
        code = re.sub(r'(f["\'])((?:\\.|(?!\2)[^\\])*)\2', r'<span style="color:#ce9178;">\1\2\2</span>', code)  # f-strings
        
        # Comments
        code = re.sub(r'(#.*)', r'<span style="color:#6a9955;">\1</span>', code)
        
        # Numbers
        code = re.sub(r'\b(\d+(?:\.\d+)?)\b', r'<span style="color:#b5cea8;">\1</span>', code)
        
        # Function/method calls and definitions
        code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()', r'<span style="color:#dcdcaa;">\1</span>', code)
        
        # Maya-specific commands
        maya_commands = r'\b(cmds\.[a-zA-Z_][a-zA-Z0-9_]*|mc\.[a-zA-Z_][a-zA-Z0-9_]*|pm\.[a-zA-Z_][a-zA-Z0-9_]*)\b'
        code = re.sub(maya_commands, r'<span style="color:#4fc1ff;">\1</span>', code)
        
        return code
    
    def _preview_changes(self, editor, original_text, new_code, mode):
        """Preview what changes will be made before applying."""
        if hasattr(self.parent, 'console'):
            if mode == "replace" or not original_text.strip():
                lines_old = len(original_text.splitlines()) if original_text else 0
                lines_new = len(new_code.splitlines())
                self.parent.console.append(f"🔄 Morpheus will replace {lines_old} lines with {lines_new} lines\n")
            else:
                self.parent.console.append(f"➕ Morpheus will add {len(new_code.splitlines())} lines of code\n")
    
    def _highlight_text_differences(self, editor, original_text, new_text):
        """Highlight only the lines that actually changed."""
        if not hasattr(editor, 'highlight_replacement'):
            return
            
        # Simple approach: if texts are very different, highlight all
        # Otherwise, try to highlight changed sections
        original_lines = original_text.splitlines() if original_text else []
        new_lines = new_text.splitlines()
        
        if len(original_lines) == 0:
            # New file - highlight everything
            editor.highlight_replacement(0, len(new_text), duration=3000)
        elif abs(len(original_lines) - len(new_lines)) > 10:
            # Major changes - highlight everything  
            editor.highlight_replacement(0, len(new_text), duration=3000)
        else:
            # Try to find and highlight specific changed sections
            import difflib
            differ = difflib.SequenceMatcher(None, original_lines, new_lines)
            
            current_pos = 0
            for tag, i1, i2, j1, j2 in differ.get_opcodes():
                if tag in ['replace', 'insert']:
                    # Calculate position of changed lines
                    lines_before = new_lines[:j1]
                    start_pos = sum(len(line) + 1 for line in lines_before)  # +1 for newlines
                    
                    lines_changed = new_lines[j1:j2]
                    length = sum(len(line) + 1 for line in lines_changed) - 1  # -1 for last newline
                    
                    if length > 0:
                        editor.highlight_replacement(start_pos, start_pos + length, duration=4000)
    
    def _check_applied_code_errors(self, editor, start_pos):
        """Check for syntax errors in the applied code and highlight them."""
        if not editor or not hasattr(editor, 'highlight_error'):
            return
            
        # Get the full editor content after application
        full_text = editor.toPlainText()
        
        try:
            compile(full_text, '<editor>', 'exec')
            
            # Show success message in console
            if hasattr(self.parent, 'console'):
                self.parent.console.append(f"✅ Morpheus suggestion applied successfully\n")
                
        except SyntaxError as e:
            if e.lineno:
                editor.highlight_error(e.lineno, f"Morpheus Suggestion Error: {e.msg}")
                
                # Show a prominent notification about the error
                if hasattr(self.parent, 'console'):
                    self.parent.console.append(f"🔴 Morpheus Suggestion Error on line {e.lineno}: {e.msg}\n")
                    self.parent.console.append(f"🛠️ Check the highlighted line in the editor for issues\n")
        except Exception as e:
            # Handle other compilation errors (indentation, etc.)
            print(f"[ERROR] ⚠️ Compilation error in Morpheus suggestion: {e}")
            if hasattr(self.parent, 'console'):
                self.parent.console.append(f"⚠️ Morpheus suggestion has compilation issues: {e}\n")
    
    def check_editor_errors(self):
        """Check the main editor for syntax errors and highlight them."""
        if hasattr(self.parent, '_current_editor'):
            editor = self.parent._current_editor()
        else:
            editor = getattr(self.parent, 'codeEditor', None)
        
        if editor:
            self.highlight_syntax_errors(editor)

    def highlight_syntax_errors(self, editor):
        """Check for and highlight syntax errors in the editor."""
        if not editor or not hasattr(editor, 'highlight_error'):
            return
            
        text = editor.toPlainText()
        if not text.strip():
            return
            
        try:
            compile(text, '<editor>', 'exec')
            # Clear any existing error highlights if syntax is valid
            if hasattr(editor, 'clear_all_highlights'):
                editor.clear_all_highlights()
        except SyntaxError as e:
            if e.lineno:
                editor.highlight_error(e.lineno, f"Syntax Error: {e.msg}")
                print(f"[SYNTAX ERROR] Line {e.lineno}: {e.msg}")
    
    def clear_chat(self):
        """Clear chat display."""
        disp = getattr(self.parent, "chatDisplay", None)
        if disp:
            disp.clear()
        self._last_suggested_code = None
        if hasattr(self.parent, 'suggestionButtonsWidget'):
            self.parent.suggestionButtonsWidget.setVisible(False)