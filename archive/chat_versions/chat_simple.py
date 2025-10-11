"""
Simple, working AI Chat for Maya Script Editor
"""
import html
import re
import threading
from PySide6 import QtCore, QtWidgets
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI not available")
    OpenAI = None

class CopilotChat:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.client = None
        self._last_suggested_code = None
        if OpenAI:
            try:
                self.client = OpenAI()
            except Exception as e:
                print(f"OpenAI init error: {e}")

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

        # Display user message
        user_html = f'''
<div style="margin:20px 0; padding:12px; border-left:3px solid #0969da; background:#161b22; clear:both;">
    <div style="color:#58a6ff; font-size:13px; font-weight:600; margin-bottom:8px;">
        👤 You
    </div>
    <div style="color:#e6edf3; font-size:14px; line-height:1.5;">
        {html.escape(text)}
    </div>
</div>
'''
        disp.insertHtml(user_html)
        
        # Start AI response in thread
        threading.Thread(target=self._get_response, args=(text, context), daemon=True).start()

    def _get_response(self, text, context):
        """Get AI response and display it."""
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            return

        # Start AI message
        ai_start = '''
<div style="margin:20px 0; padding:12px; border-left:3px solid #7c3aed; background:#161b22; clear:both;">
    <div style="color:#d2a8ff; font-size:13px; font-weight:600; margin-bottom:8px;">
        🤖 Copilot
    </div>
    <div style="color:#e6edf3; font-size:14px; line-height:1.6;">
'''
        
        QtCore.QMetaObject.invokeMethod(
            disp, "insertHtml", QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, ai_start)
        )

        try:
            # Get response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": 
                        "You are an AI assistant for Maya scripting. "
                        "When users ask for code, provide it in ```python or ```mel blocks. "
                        "Only provide Maya Python and MEL code - never other languages."
                    },
                    {"role": "user", "content": f"{text}\n\nContext: {context}"}
                ]
            )
            
            content = response.choices[0].message.content
            
            # Process and display response
            QtCore.QMetaObject.invokeMethod(
                self, "_display_response", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, content)
            )
            
        except Exception as e:
            error_html = f'<div style="color:#ff6b6b;">Error: {str(e)}</div>'
            QtCore.QMetaObject.invokeMethod(
                disp, "insertHtml", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, error_html)
            )

    @QtCore.Slot(str)
    def _display_response(self, content):
        """Display the AI response with proper code block formatting."""
        disp = getattr(self.parent, "chatDisplay", None)
        if not disp:
            return

        # Find code blocks
        parts = re.split(r'```(\w+)?\n?(.*?)\n?```', content, flags=re.DOTALL)
        
        for i in range(0, len(parts), 4):
            # Text before code block
            if i < len(parts) and parts[i].strip():
                text_html = html.escape(parts[i]).replace('\n', '<br>')
                disp.insertHtml(text_html)
            
            # Code block
            if i + 2 < len(parts):
                language = parts[i + 1] if parts[i + 1] else 'python'
                code = parts[i + 2].strip()
                
                if code:
                    # Store code for Apply button
                    if self._is_maya_code(code):
                        self._last_suggested_code = code
                        if hasattr(self.parent, 'applySuggestionBtn'):
                            self.parent.applySuggestionBtn.setVisible(True)
                    
                    # Display code block
                    highlighted_code = self._highlight_code(code)
                    code_html = f'''
<div style="margin:16px 0; background:#0d1117; border:1px solid #30363d; border-radius:6px;">
    <div style="background:#21262d; border-bottom:1px solid #30363d; padding:8px 12px;">
        <span style="color:#8b949e; font-size:12px;">{language}</span>
        <span style="color:#58a6ff; font-size:10px; margin-left:8px;">Maya Script</span>
    </div>
    <div style="padding:16px; background:#0d1117;">
        <pre style="margin:0; color:#e6edf3; font-family:Consolas,monospace; font-size:13px; white-space:pre-wrap;">{highlighted_code}</pre>
    </div>
</div>
'''
                    disp.insertHtml(code_html)

        # Close AI message
        disp.insertHtml('</div></div>')
        
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

    def _highlight_code(self, code):
        """Simple syntax highlighting."""
        code = html.escape(code)
        
        # Keywords
        keywords = r'\b(import|def|class|if|else|elif|for|while|try|except|return|maya|cmds)\b'
        code = re.sub(keywords, r'<span style="color:#ff7b72;">\1</span>', code)
        
        # Strings
        code = re.sub(r'(["\'])(.*?)\1', r'<span style="color:#a5d6ff;">\1\2\1</span>', code)
        
        # Comments
        code = re.sub(r'(#.*?)$', r'<span style="color:#8b949e;">\1</span>', code, flags=re.MULTILINE)
        
        return code

    def apply_last_suggestion(self, editor, mode="insert"):
        """Apply the last suggested code to editor."""
        if not self._last_suggested_code or not editor:
            return False
            
        cursor = editor.textCursor()
        
        if cursor.hasSelection():
            # Replace selection
            cursor.removeSelectedText()
            cursor.insertText(self._last_suggested_code)
        else:
            # Insert at cursor
            current_text = editor.toPlainText()
            if current_text.strip():
                cursor.insertText("\n\n" + self._last_suggested_code)
            else:
                cursor.insertText(self._last_suggested_code)
        
        editor.setTextCursor(cursor)
        
        # Hide Apply button
        if hasattr(self.parent, 'applySuggestionBtn'):
            self.parent.applySuggestionBtn.setVisible(False)
            
        return True

    def clear_chat(self):
        """Clear chat display."""
        disp = getattr(self.parent, "chatDisplay", None)
        if disp:
            disp.clear()
        self._last_suggested_code = None
        if hasattr(self.parent, 'applySuggestionBtn'):
            self.parent.applySuggestionBtn.setVisible(False)