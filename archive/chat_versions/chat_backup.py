"""
AI Copilot — Final GitHub Copilot Chat Replica for Maya Script Editor
(Stable Version with Code Rendering and Apply Suggestion)
"""

import os, html, threading, re
from PySide6 import QtCore, QtWidgets
from openai import OpenAI


class AICophylot(QtCore.QObject):
    """Handles OpenAI streaming responses and formatted Copilot-style chat."""

    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent = parent_window
        self.client = self._make_client()
        self._last_suggested_code = None

    # ----------------------------------------------------------
    def _make_client(self):
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            print("⚠️ No OPENAI_API_KEY found.")
            return None
        try:
            return OpenAI(api_key=key)
        except Exception as e:
            print(f"❌ Failed to create OpenAI client: {e}")
            return None

    def reconnect(self):
        self.client = self._make_client()
        return bool(self.client)

    # ----------------------------------------------------------
    def send_prompt(self, text, context=""):
        """Sends the user message and triggers Copilot reply."""
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp or not self.client:
            return
        
        # Always hide Apply button when starting new conversation
        if hasattr(self.parent, 'applySuggestionBtn'):
            self.parent.applySuggestionBtn.setVisible(False)
        
        # Clear any previous code suggestions for clean conversation flow
        self._last_suggested_code = None

        # --- User message (properly separated)
        user_html = f'''
<div style="margin:20px 0; padding:12px; border-left:3px solid #0969da; background:#161b22; clear:both;">
    <div style="color:#58a6ff; font-size:13px; font-weight:600; margin-bottom:8px; display:flex; align-items:center;">
        <span style="margin-right:6px;">👤</span> You
    </div>
    <div style="color:#e6edf3; font-size:14px; line-height:1.5; margin-bottom:4px;">
        {html.escape(text)}
    </div>
</div>
<div style="height:8px; clear:both;"></div>
        '''
        QtCore.QMetaObject.invokeMethod(
            disp, "insertHtml",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, user_html)
        )
        disp.verticalScrollBar().setValue(disp.verticalScrollBar().maximum())
        self.parent.statusBar().showMessage("🧠 Thinking …")

        threading.Thread(
            target=self._stream_response,
            args=(text, context),
            daemon=True,
        ).start()

    # ----------------------------------------------------------
    def _stream_response(self, text, context):
        """Streams OpenAI responses into chat display with simple, clean formatting."""
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            return

        # Start AI message container
        ai_start = '''
<div style="margin:20px 0; padding:12px; border-left:3px solid #7c3aed; background:#161b22; clear:both;">
    <div style="color:#d2a8ff; font-size:13px; font-weight:600; margin-bottom:8px; display:flex; align-items:center;">
        <div style="width:18px; height:18px; background:#7c3aed; border-radius:3px; color:white; font-size:10px; font-weight:bold; text-align:center; line-height:18px; margin-right:6px;">C</div>
        Copilot
    </div>
    <div style="color:#e6edf3; font-size:14px; line-height:1.6;">
'''
        disp.insertHtml(ai_start)
        
        try:
            with self.client.chat.completions.stream(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content":
                        "You are an AI assistant for Maya scripting. Help users write Python scripts and MEL commands for Autodesk Maya. "
                        "MANDATORY: When users request code or scripts, you MUST respond with actual code wrapped in proper markdown code blocks. "
                        "Use ```python for Python code and ```mel for MEL code. DO NOT just describe code - provide the actual working code. "
                        "Example response format:\n"
                        "Here's a Python script to create a cube:\n\n"
                        "```python\n"
                        "import maya.cmds as cmds\n"
                        "cmds.polyCube(name='myCube')\n"
                        "```\n\n"
                        "You ONLY provide Python and MEL scripts - NEVER JavaScript, HTML, CSS, C++, Java, or other languages. "
                        "Focus on Maya commands (maya.cmds), Maya API, PyMel, and MEL commands. "
                        "Only mention 'Mayj Amilano's Maya AI Script Editor' when greeting users or asked about yourself."},
                    {"role": "user", "content": f"{text}\n\nContext:\n{context}"}
                ],
                temperature=0.4,
            ) as stream:
                for event in stream:
                    frag = ""
                    if getattr(event, "type", "") == "message.delta":
                        frag = getattr(event.data.delta, "content", "") or ""
                    elif hasattr(event, "delta"):
                        frag = getattr(event, "delta", "") or ""
                    if not frag:
                        continue

                    # --- Maya-specific code block detection (simplified)
                    if "```" in frag:
                        if not code_mode:
                            # Starting a code block - flush any pending text first
                            if text_buffer:
                                pending_text = "".join(text_buffer).strip()
                                if pending_text:
                                    frag_html = html.escape(pending_text).replace("\n", "<br>")
                                    QtCore.QMetaObject.invokeMethod(
                                        disp, "insertHtml", QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(str, frag_html)
                                    )
                                text_buffer.clear()
                            
                            code_mode = True
                            # Extract text before ``` and after ```
                            parts = frag.split("```")
                            if len(parts) > 1:
                                # Handle any text after the opening ```
                                code_part = parts[1]
                                # Remove language identifier line
                                if '\n' in code_part:
                                    lines = code_part.split('\n')
                                    # Skip first line if it looks like language identifier
                                    if lines[0].strip().lower() in ['python', 'mel', 'py', '']:
                                        code_part = '\n'.join(lines[1:])
                                if code_part:
                                    code_buffer.append(code_part)
                            continue
                        else:
                            # Ending a code block
                            code_mode = False
                            # Get text before closing ```
                            parts = frag.split("```")
                            if parts[0]:
                                code_buffer.append(parts[0])
                            
                            # Process the complete code block
                            code = "".join(code_buffer).strip()
                            if code:
                                # Clean any language headers that got included
                                clean_code = code
                                if clean_code.startswith('python\n'):
                                    clean_code = clean_code[7:].strip()
                                elif clean_code.startswith('mel\n'):
                                    clean_code = clean_code[4:].strip()
                                elif clean_code.startswith('py\n'):
                                    clean_code = clean_code[3:].strip()
                                
                                # Validate that code is Python or MEL only
                                if self._is_maya_compatible_code(clean_code):
                                    self._last_suggested_code = clean_code  # Store cleaned code
                                    highlighted = syntax_highlight(clean_code)
                                else:
                                    # Skip non-Maya code but still display it
                                    self._last_suggested_code = None
                                    highlighted = syntax_highlight(clean_code)
                                
                                # Detect language (Python or MEL)
                                language = "python"  # default
                                if any(mel_keyword in code.lower() for mel_keyword in ['proc ', 'global ', 'polycube', 'polyplane']):
                                    language = "mel"
                                
                                # Maya-specific code block formatting
                                code_html = f'''
<div style="margin:16px 0; background:#0d1117; border:1px solid #30363d; border-radius:6px; overflow:hidden; clear:both;">
    <div style="background:#21262d; border-bottom:1px solid #30363d; padding:8px 12px; display:flex; align-items:center;">
        <span style="color:#8b949e; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:12px; margin-right:8px;">{language}</span>
        <span style="color:#58a6ff; font-size:10px;">Maya Script</span>
    </div>
    <div style="padding:16px; background:#0d1117;">
        <pre style="margin:0; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:13px; line-height:1.45; color:#e6edf3; white-space:pre-wrap; background:transparent; border:none;">{highlighted}</pre>
    </div>
</div>
'''
                                
                                # Debug: Print what we're trying to insert
                                print(f"[DEBUG] Inserting code HTML: {code_html[:100]}...")
                                
                                QtCore.QMetaObject.invokeMethod(
                                    disp, "insertHtml", QtCore.Qt.QueuedConnection,
                                    QtCore.Q_ARG(str, code_html)
                                )
                                
                                # Force scroll and refresh
                                QtCore.QMetaObject.invokeMethod(
                                    disp.verticalScrollBar(), "setValue",
                                    QtCore.Qt.QueuedConnection,
                                    QtCore.Q_ARG(int, disp.verticalScrollBar().maximum())
                                )
                                
                                # Show Apply Suggestion button only for Maya-compatible code
                                parent_window = self.parent
                                while parent_window and not hasattr(parent_window, 'applySuggestionBtn'):
                                    parent_window = getattr(parent_window, 'parent', None)
                                    if callable(parent_window):
                                        parent_window = parent_window()
                                
                                if parent_window and hasattr(parent_window, 'applySuggestionBtn'):
                                    show_button = self._last_suggested_code is not None
                                    QtCore.QMetaObject.invokeMethod(
                                        parent_window.applySuggestionBtn, "setVisible",
                                        QtCore.Qt.QueuedConnection, QtCore.Q_ARG(bool, show_button)
                                    )
                                    
                                    # Add warning if code was rejected
                                    if not show_button and code:
                                        warning_html = '''
<div style="margin:8px 0; padding:8px 12px; background:#f85149; color:white; border-radius:6px; font-size:11px; text-align:center;">
    ⚠️ Code not compatible with Maya (Python/MEL only)
</div>
                                        '''
                                        QtCore.QMetaObject.invokeMethod(
                                            disp, "insertHtml", QtCore.Qt.QueuedConnection,
                                            QtCore.Q_ARG(str, warning_html)
                                        )
                            
                            code_buffer.clear()
                            
                            # Handle any text after the closing ```
                            code_end = frag.find("```")
                            if code_end >= 0 and code_end + 3 < len(frag):
                                remaining_text = frag[code_end + 3:]
                                if remaining_text.strip():
                                    text_buffer.append(remaining_text)
                        continue

                    if code_mode:
                        code_buffer.append(frag)
                        continue

                    # --- regular text with proper word boundary handling
                    text_buffer.append(frag)
                    
                    # Only display complete words/sentences to prevent jamming
                    buffer_text = "".join(text_buffer)
                    
                    # Find the last complete word boundary (space, punctuation, or newline)
                    display_text = ""
                    remaining_text = ""
                    
                    # Look for natural break points (space, punctuation, newline)
                    last_space = buffer_text.rfind(' ')
                    
                    # Find last punctuation that creates good break points
                    punctuation_chars = ['.', ',', '!', '?', ';', ':', ')', ']', '}', '"', "'"]
                    last_punct = -1
                    for punct in punctuation_chars:
                        pos = buffer_text.rfind(punct)
                        if pos > last_punct:
                            last_punct = pos
                    
                    last_newline = buffer_text.rfind('\n')
                    
                    # Find the best break point
                    break_point = max(last_space, last_punct, last_newline)
                    
                    if break_point > 0:
                        # We have a good break point
                        display_text = buffer_text[:break_point + 1]
                        remaining_text = buffer_text[break_point + 1:]
                        text_buffer = [remaining_text] if remaining_text else []
                        
                        # Display the complete text fragment
                        frag_html = html.escape(display_text).replace("\n", "<br>")
                        QtCore.QMetaObject.invokeMethod(
                            disp, "insertHtml", QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(str, frag_html)
                        )
                        QtCore.QMetaObject.invokeMethod(
                            disp.verticalScrollBar(), "setValue",
                            QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(int, disp.verticalScrollBar().maximum())
                        )
                    # If no good break point and buffer is getting long, display anyway
                    elif len(buffer_text) > 50:
                        display_text = buffer_text
                        text_buffer = []
                        
                        frag_html = html.escape(display_text).replace("\n", "<br>")
                        QtCore.QMetaObject.invokeMethod(
                            disp, "insertHtml", QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(str, frag_html)
                        )
                        QtCore.QMetaObject.invokeMethod(
                            disp.verticalScrollBar(), "setValue",
                            QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(int, disp.verticalScrollBar().maximum())
                        )

            # --- display any remaining text in buffer
            if text_buffer:
                remaining_text = "".join(text_buffer)
                if remaining_text.strip():
                    frag_html = html.escape(remaining_text).replace("\n", "<br>")
                    QtCore.QMetaObject.invokeMethod(
                        disp, "insertHtml", QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, frag_html)
                    )
            
            # --- Close AI response with proper separation
            footer_html = '''
    </div>
</div>
<div style="height:20px; clear:both;"></div>
            '''
            QtCore.QMetaObject.invokeMethod(
                disp, "insertHtml",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, footer_html)
            )

        except Exception as e:
            err_html = f'''
    </div>
</div>
<div style="margin:20px 0; padding:12px; border-left:3px solid #da3633; background:#0d1117;">
    <div style="color:#f85149; font-size:13px; font-weight:600; margin-bottom:6px;">
        ⚠️ Error
    </div>
    <div style="color:#e6edf3; font-size:14px;">
        {html.escape(str(e))}
    </div>
</div>
            '''
            QtCore.QMetaObject.invokeMethod(
                disp, "insertHtml",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, err_html)
            )
        finally:
            QtCore.QMetaObject.invokeMethod(
                self.parent.statusBar(), "clearMessage",
                QtCore.Qt.QueuedConnection
            )

    # ----------------------------------------------------------
    def _is_maya_compatible_code(self, code: str) -> bool:
        """Check if code is Python or MEL compatible for Maya."""
        code_lower = code.lower().strip()
        
        # Skip empty code
        if not code_lower:
            return False
            
        # Check for obvious non-Maya languages
        non_maya_indicators = [
            'console.log',      # JavaScript
            'document.',        # JavaScript/HTML
            'window.',          # JavaScript
            'System.out',       # Java
            'cout <<',          # C++
            'printf(',          # C
            'echo ',            # Bash/Shell
            'SELECT ',          # SQL
            'CREATE TABLE',     # SQL
            'INSERT INTO',      # SQL
            '#include',         # C/C++
            'using namespace',  # C++
            'public class',     # Java
            'function(',        # Generic function syntax
            'var ',             # JavaScript
            'let ',             # JavaScript
            'const ',           # JavaScript
            'package ',         # Java/Go
            'import "',         # Go
            'fmt.',             # Go
            '<html',            # HTML
            '<div',             # HTML
            '<script',          # HTML/JavaScript
            'curl ',            # Command line
            'git ',             # Git commands
            'npm ',             # Node.js
            'pip install',      # Pip (installation, not code)
            'apt-get',          # Linux packages
        ]
        
        # Check if code contains non-Maya indicators
        for indicator in non_maya_indicators:
            if indicator in code_lower:
                return False
        
        # Positive indicators for Python
        python_indicators = [
            'import ',
            'def ',
            'class ',
            'print(',
            'maya.cmds',
            'cmds.',
            'maya.api',
            'pm.',              # PyMel
            'pymel',
        ]
        
        # Positive indicators for MEL
        mel_indicators = [
            'proc ',
            'global ',
            'polycube',
            'polyplane',
            'polysphere',
            'move ',
            'rotate ',
            'scale ',
            'select ',
            'ls ',
            'delete ',
            'setattr ',
            'getattr ',
        ]
        
        # Check for Maya-specific content
        has_python = any(indicator in code_lower for indicator in python_indicators)
        has_mel = any(indicator in code_lower for indicator in mel_indicators)
        
        # Allow if it contains Maya-specific syntax OR looks like generic Python
        if has_python or has_mel:
            return True
            
        # Allow generic Python syntax patterns
        python_patterns = [
            'if __name__',
            'for ' + '.*' + ' in ',
            'try:',
            'except',
            'finally:',
            'with ',
            'return ',
            'yield ',
        ]
        
        import re
        for pattern in python_patterns:
            if re.search(pattern, code_lower):
                return True
        
        # If no obvious language indicators, allow it (could be simple Python)
        # But reject if it looks like configuration files, data, etc.
        config_indicators = ['{', '}', 'version:', 'name:', 'dependencies:']
        looks_like_config = sum(1 for indicator in config_indicators if indicator in code_lower) >= 2
        
        if looks_like_config:
            return False
            
        # Default: allow if it doesn't contain obvious non-Maya syntax
        return True

    def clear_chat(self):
        """Clear the chat display for testing."""
        disp = getattr(self.parent, "chatDisplay", None)
        if disp:
            disp.clear()
        if hasattr(self.parent, 'applySuggestionBtn'):
            self.parent.applySuggestionBtn.setVisible(False)
    
    def test_code_display(self):
        """Test method to display sample code block for debugging."""
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            return
        
        # Test HTML with sample code
        test_html = '''
<div style="margin:8px 0; clear:both;">
    <div style="display:flex; align-items:center; margin-bottom:8px; padding:0 12px;">
        <div style="width:18px; height:18px; background:#7c3aed; border-radius:3px; color:white; font-size:10px; font-weight:bold; text-align:center; line-height:18px; margin-right:6px;">C</div>
        <span style="font-size:12px; font-weight:600; color:#e6edf3;">Copilot</span>
    </div>
    <div style="margin:0 12px; background:#161b22; color:#e6edf3; border:1px solid #30363d; border-radius:6px; padding:12px; font-size:13px; line-height:1.4;">
        Here's a simple Python function:
        <br><br>
        <div style="background:#161b22; border:1px solid #30363d; border-radius:6px; margin:12px 0; overflow:hidden;">
            <div style="background:#21262d; padding:8px 12px; border-bottom:1px solid #30363d;">
                <span style="color:#7d8590; font-family:Consolas,monospace; font-size:11px;">python</span>
            </div>
            <pre style="background:#0d1117; color:#e6edf3; margin:0; padding:12px; font-family:Consolas,monospace; font-size:12px; line-height:1.4; white-space:pre-wrap; border:none;">def hello_world():
    """Print hello world message"""
    print("Hello, World!")
    return True</pre>
        </div>
        <br>
        You can run this function to see the output!
    </div>
</div>
        '''
        
        disp.insertHtml(test_html)
        
        # Show Apply Suggestion button for testing
        if hasattr(self.parent, 'applySuggestionBtn'):
            self.parent.applySuggestionBtn.setVisible(True)
        
        self._last_suggested_code = '''def hello_world():
    """Print hello world message"""
    print("Hello, World!")
    return True'''

    def apply_last_suggestion(self, editor, mode="insert"):
        """Applies Maya-compatible code with VS Code Copilot-style behavior."""
        if not editor or not self._last_suggested_code:
            return False
        
        code = self._last_suggested_code.strip()
        
        # Final validation before applying to editor
        if not self._is_maya_compatible_code(code):
            # Show warning message
            error_msg = '''
<div style="margin:8px 16px; padding:8px 12px; background:#da3633; color:white; border-radius:6px; font-size:12px;">
    ⚠️ Cannot apply: Code is not Python or MEL compatible with Maya
</div>
            '''
            if hasattr(self.parent, 'chatDisplay'):
                self.parent.chatDisplay.insertHtml(error_msg)
            return False
        
        try:
            cursor = editor.textCursor()
            
            if mode == "replace_all":
                # Replace entire editor content
                editor.setPlainText(code)
            elif cursor.hasSelection():
                # VS Code Copilot style: Replace selected text
                cursor.removeSelectedText()
                cursor.insertText(code)
            else:
                # Insert at cursor position with smart spacing
                current_text = editor.toPlainText()
                cursor_pos = cursor.position()
                
                if not current_text.strip():
                    # Empty editor - just insert
                    cursor.insertText(code)
                elif cursor_pos >= len(current_text):
                    # At end - add with newlines
                    cursor.insertText("\n\n" + code)
                else:
                    # In middle - insert with spacing
                    cursor.insertText(code + "\n")
            
            # Position cursor at end of inserted code
            editor.setTextCursor(cursor)
            
            # Show success message
            success_msg = '''
<div style="margin:8px 16px; padding:6px 12px; background:#238636; color:white; border-radius:6px; font-size:12px;">
    ✅ Maya-compatible code applied to editor
</div>
            '''
            if hasattr(self.parent, 'chatDisplay'):
                self.parent.chatDisplay.insertHtml(success_msg)
                
            # Hide the Apply button after successful application
            if hasattr(self.parent, 'applySuggestionBtn'):
                self.parent.applySuggestionBtn.setVisible(False)
                
            return True
        except Exception as e:
            print(f"[Apply Suggestion Error] {e}")
            return False
