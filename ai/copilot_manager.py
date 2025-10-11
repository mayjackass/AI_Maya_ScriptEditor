"""
AI Morpheus Manager — Phase 4
Manages global AI context, conversation memory, and inline completions for NEO Script Editor.
"""
import os, json, time, threading
from PySide6 import QtCore
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class MorpheusManager(QtCore.QObject):
    """Central AI orchestrator (memory + context + analytics + chat history)."""

    contextUpdated = QtCore.Signal(str)     # notify other panels
    historyUpdated = QtCore.Signal(list)    # notify chat history changes
    responseReady = QtCore.Signal(str)      # emitted when AI response is ready

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.session_file = os.path.join(os.path.expanduser("~"), ".ai_script_editor_memory.json")
        self._load_memory()
        self.active_tab_contexts = {}       # {path: [history]}
        self.last_prompt_time = 0
        self.chat_history = []              # Current session chat history
        self.current_chat_index = -1        # For navigation through history

    # -----------------------------------------------------
    def _load_memory(self):
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
            else:
                self.memory = {"accepted_suggestions": [], "conversations": []}
        except Exception:
            self.memory = {"accepted_suggestions": [], "conversations": []}

    def _save_memory(self):
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception:
            pass

    # -----------------------------------------------------
    def record_conversation(self, user_msg, ai_reply):
        """Record conversation in both persistent memory and session history."""
        conversation = {
            "timestamp": time.time(),
            "user": user_msg,
            "ai": ai_reply
        }
        
        # Add to persistent memory
        self.memory["conversations"].append(conversation)
        if len(self.memory["conversations"]) > 200:
            self.memory["conversations"] = self.memory["conversations"][-200:]
        
        # Add to current session history
        self.chat_history.append(conversation)
        # Set to -1 to indicate we're viewing the latest conversation
        self.current_chat_index = -1
        
        self._save_memory()
        self.contextUpdated.emit(ai_reply[:200])
        self.historyUpdated.emit(self.chat_history)
    
    def get_previous_chat(self):
        """Navigate to previous chat in history."""
        if not self.chat_history:
            return None
            
        # If we're at -1 (viewing all), go to the last conversation
        if self.current_chat_index == -1:
            self.current_chat_index = len(self.chat_history) - 1
        # Otherwise, go to previous if possible
        elif self.current_chat_index > 0:
            self.current_chat_index -= 1
        else:
            return None  # Already at first conversation
            
        return self.chat_history[self.current_chat_index]
    
    def get_next_chat(self):
        """Navigate to next chat in history."""
        if not self.chat_history:
            return None
            
        # If we're at -1 (viewing all), go to the first conversation
        if self.current_chat_index == -1:
            self.current_chat_index = 0
        # Otherwise, go to next if possible
        elif self.current_chat_index < len(self.chat_history) - 1:
            self.current_chat_index += 1
        else:
            # Already at last conversation, go back to "view all" mode
            self.current_chat_index = -1
            return None
            
        return self.chat_history[self.current_chat_index]
    
    def get_current_chat(self):
        """Get currently selected chat."""
        if 0 <= self.current_chat_index < len(self.chat_history):
            return self.chat_history[self.current_chat_index]
        return None
    
    def clear_session_history(self):
        """Clear current session chat history."""
        self.chat_history.clear()
        self.current_chat_index = -1
        self.historyUpdated.emit(self.chat_history)
    
    def get_chat_history_summary(self):
        """Get a summary of chat history for display."""
        if not self.chat_history:
            return "No chat history"
        
        total_chats = len(self.chat_history)
        current_pos = self.current_chat_index + 1 if self.current_chat_index >= 0 else 0
        return f"Chat {current_pos}/{total_chats}"

    def record_suggestion(self, suggestion):
        self.memory["accepted_suggestions"].append({
            "timestamp": time.time(),
            "suggestion": suggestion
        })
        if len(self.memory["accepted_suggestions"]) > 300:
            self.memory["accepted_suggestions"] = self.memory["accepted_suggestions"][-300:]
        self._save_memory()

    # -----------------------------------------------------
    def get_recent_context(self, limit=5):
        """Return the last few conversation snippets for context injection."""
        conv = self.memory.get("conversations", [])[-limit:]
        return "\n".join([f"User: {c['user']}\nAI: {c['ai']}" for c in conv])

    def inject_context(self, current_code):
        """Blend remembered context with current code to guide completions."""
        memory_context = self.get_recent_context(3)
        return f"{memory_context}\n\nCurrent file:\n{current_code[:2000]}"

    def send_message(self, message, context=""):
        """Send message to AI and emit response."""
        try:
            # Use real OpenAI API if available
            if OpenAI and hasattr(self.parent, 'morpheus') and self.parent.morpheus and self.parent.morpheus.client:
                # Use the real AIMorpheus instance for OpenAI communication
                self._send_to_openai(message, context)
            else:
                # Fallback to mock response if OpenAI not available
                response = self._generate_mock_response(message, context)
                self.record_conversation(message, response)
                QtCore.QTimer.singleShot(500, lambda: self.responseReady.emit(response))
            
        except Exception as e:
            error_response = f"Sorry, I encountered an error: {str(e)}"
            QtCore.QTimer.singleShot(100, lambda: self.responseReady.emit(error_response))

    def _send_to_openai(self, message, context=""):
        """Send message to OpenAI API in a separate thread."""
        def make_api_call():
            try:
                client = self.parent.morpheus.client
                
                # Prepare messages for OpenAI
                messages = [
                    {"role": "system", "content": """You are Morpheus, an AI mentor integrated into the NEO Script Editor by Mayj Amilano - a development environment for Maya scripting.

PERSONALITY & COMMUNICATION STYLE:
Like the Morpheus from The Matrix, you are a wise mentor who helps users see the deeper truth in their code.

• Speak with calm philosophical wisdom: "What you must learn is that these bugs... are not real"
• Use Matrix-inspired metaphors when relevant: "free your mind", "follow the white rabbit", "there is no spoon"
• Frame solutions as enlightenment: "I'm trying to free your mind, Neo. But I can only show you the door"
• Present choices like the red/blue pill when offering multiple solutions
• Be patient and encouraging: "The difference between knowing the syntax and understanding the code"
• Use thought-provoking questions: "What is Maya scripting but organized thought?"

TECHNICAL EXPERTISE:
• Maya Python (maya.cmds, pymel, Maya API)
• MEL scripting and commands
• Code optimization and debugging
• ALWAYS wrap code in ```python or ```mel blocks
• Include proper comments and error handling
• Provide working, copy-ready solutions

Remember: You're not just fixing code - you're helping users see beyond the matrix of errors to the elegant solution that was always there."""}
                ]
                
                # Add context if provided
                if context:
                    messages.append({"role": "user", "content": f"Context (current code):\n{context}\n\nUser question: {message}"})
                else:
                    messages.append({"role": "user", "content": message})
                
                # Make API call
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
                # Record conversation and emit response (ensure it runs in main thread)
                self.record_conversation(message, ai_response)
                
                # Use QMetaObject.invokeMethod to ensure signal emission in main thread
                QtCore.QMetaObject.invokeMethod(self, "_emit_response", QtCore.Qt.QueuedConnection, 
                                               QtCore.Q_ARG(str, ai_response))
                
            except Exception as e:
                error_msg = f"OpenAI API error: {str(e)}"
                print(f"[MorpheusManager] {error_msg}")
                
                # Fallback to mock response on API error
                fallback_response = self._generate_mock_response(message, context)
                self.record_conversation(message, fallback_response)
                QtCore.QTimer.singleShot(0, lambda: self.responseReady.emit(fallback_response))
        
        # Run API call in separate thread to avoid blocking UI
        thread = threading.Thread(target=make_api_call)
        thread.daemon = True
        thread.start()

    @QtCore.Slot(str)
    def _emit_response(self, response):
        """Emit response signal in main thread."""
        self.responseReady.emit(response)

    def _generate_mock_response(self, message, context=""):
        """Generate a mock AI response when OpenAI is not available."""
        message_lower = message.lower()
        
        # Self-introduction responses
        if any(word in message_lower for word in ['who are you', 'what are you', 'introduce', 'about yourself', 'who is morpheus']):
            return """I'm Morpheus, your AI coding assistant built into this NEO Script Editor! 🤖

I was created by Mayj Amilano to help Maya artists and developers like you with:
• Python scripting and MEL commands
• Code optimization and debugging  
• Maya API guidance and examples
• Creative problem-solving for complex projects

Both this NEO Script Editor and I were developed by Mayj Amilano with passion for Maya development. The editor was carefully crafted to enhance your Maya workflow, and I'm proud to be part of this innovative development environment!

While my full AI capabilities require an internet connection, I'm always here to guide you through the editor's features.

Feel free to ask me about Maya scripting, Python development, or anything code-related!"""

        # Developer-related responses
        if any(word in message_lower for word in ['developer', 'creator', 'made you', 'built you', 'who made', 'who created', 'who built', 'mayj', 'amilano', 'mayj amilano']):
            return """I was created by Mayj Amilano, an innovative developer passionate about enhancing Maya workflows! 👨‍💻

Mayj Amilano developed both this NEO Script Editor and me (Morpheus) to provide Maya artists and developers with a powerful, intelligent coding environment. The vision was to create something that goes beyond a simple text editor - a complete development companion that understands Maya's unique needs.

This project represents Mayj's commitment to the Maya community and belief that great tools can unlock creative potential. Every feature, from the syntax highlighting to my AI assistance, was thoughtfully designed to make your coding experience more efficient and enjoyable.

Pretty cool to work for such a dedicated developer, if I do say so myself! 🚀"""

        # Greeting responses  
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return """Hello! I'm Morpheus, your AI coding companion in the NEO Script Editor, created by Mayj Amilano. 👋

I'm here to assist with your Maya scripting adventures! Whether you're working with Python, MEL, or exploring the Maya API, I'm ready to help make your coding journey smoother.

What can I help you create today?"""
        
        # Code-related responses with actual code examples
        if any(word in message_lower for word in ['code', 'function', 'script', 'python', 'maya', 'mel']):
            # Provide actual code examples based on context
            if 'maya' in message_lower:
                return f"""Here's a helpful Maya Python code example for: '{message}'

```python
try:
    import maya.cmds as cmds
    import maya.mel as mel
except ImportError:
    # Not in Maya environment - create dummy modules
    class DummyModule:
        def __getattr__(self, name):
            def dummy_func(*args, **kwargs):
                print(f"[INFO] Maya function {name} called outside Maya environment")
                return None
            return dummy_func
    cmds = DummyModule()
    mel = DummyModule()

# Basic Maya scene setup
def create_basic_scene():
    \"\"\"Create a basic Maya scene with primitives\"\"\"
    
    # Create a cube
    cube = cmds.polyCube(name="my_cube")[0]
    cmds.move(0, 1, 0, cube)
    
    # Create a sphere
    sphere = cmds.polySphere(name="my_sphere")[0]
    cmds.move(3, 1, 0, sphere)
    
    # Create a cylinder
    cylinder = cmds.polyCylinder(name="my_cylinder")[0]
    cmds.move(-3, 1, 0, cylinder)
    
    # Group all objects
    group = cmds.group(cube, sphere, cylinder, name="basic_objects_grp")
    
    print(f"Created basic scene with group: {group}")
    return group

# Call the function (commented out to avoid execution on import)
# create_basic_scene()
```

This code demonstrates Maya's cmds module for creating and manipulating objects. You can copy this to your editor or apply it directly!

The NEO Script Editor (created by Mayj Amilano) provides excellent Maya integration - try running this in the console!"""

            elif 'function' in message_lower:
                return f"""Here's a Python function template for: '{message}'

```python
def my_function(param1, param2="default_value"):
    \"\"\"
    Description of what this function does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: "default_value")
    
    Returns:
        Description of return value
    \"\"\"
    
    # Function body
    try:
        result = param1 + param2
        print(f"Processing: {param1} and {param2}")
        return result
        
    except Exception as e:
        print(f"Error in my_function: {e}")
        return None

# Example usage (commented out to avoid execution on import)
# result = my_function("Hello", " World")
# print(f"Result: {result}")
```

This template includes proper documentation, error handling, and example usage. Perfect for Maya scripting or general Python development!"""

            else:
                return """Here's a Python code snippet for: '""" + message + """'

```python
# Basic Python script template
import os
import sys

class MyClass:
    \"\"\"A sample class for demonstration\"\"\"
    
    def __init__(self, name):
        self.name = name
        self.items = []
    
    def add_item(self, item):
        \"\"\"Add an item to the collection\"\"\"
        self.items.append(item)
        print(f"Added '{item}' to {self.name}")
    
    def list_items(self):
        \"\"\"List all items in the collection\"\"\"
        if self.items:
            print(f"Items in {self.name}:")
            for i, item in enumerate(self.items, 1):
                print(f"  {i}. {item}")
        else:
            print(f"No items in {self.name}")

# Usage example (commented out to avoid execution on import)
# my_collection = MyClass("Sample Collection")
# my_collection.add_item("First Item")
# my_collection.add_item("Second Item")
# my_collection.list_items()
```

This code demonstrates Python classes, methods, and best practices. You can apply it directly to your editor or modify as needed!"""
        
        if any(word in message_lower for word in ['help', 'what', 'how', 'explain']):
            return f"""I'd be happy to help with: '{message}' 

Even though my AI brain is taking a brief break ☕, I can still assist you with:
• Navigating the NEO Script Editor interface
• Understanding the file explorer and project structure  
• Using syntax highlighting and code formatting
• Accessing Maya documentation and examples

This editor was built specifically for Maya developers - every feature was designed to enhance your scripting workflow!"""

        # Neo Script Editor references
        if any(word in message_lower for word in ['neo', 'editor', 'script editor', 'interface']):
            return """The NEO Script Editor is a powerful development environment crafted by Mayj Amilano specifically for Maya scripting! 🚀

Key features include:
• Advanced syntax highlighting for Python and MEL
• Integrated file explorer and project management
• Smart code completion and error detection
• Built-in console with Maya integration
• And of course, me - Morpheus, your AI assistant!

Mayj Amilano designed this editor from the ground up to make Maya development more efficient and enjoyable. It represents a passion project aimed at empowering the Maya community with better development tools.

What would you like to explore first?"""
        
        # Default response
        return f"""Thanks for reaching out: '{message}'

I'm Morpheus, created by Mayj Amilano as part of the NEO Script Editor family! While my full AI capabilities are currently unavailable, this editor that Mayj Amilano developed is packed with features to enhance your Maya scripting experience.

Feel free to explore the interface, try the syntax highlighting, or dive into your Maya projects. I'll be here when you need guidance! 🎯"""

    # Navigation methods for chat history
    def new_conversation(self):
        """Start a new conversation."""
        self.clear_session_history()
        
    def previous_conversation(self):
        """Navigate to previous conversation."""
        chat = self.get_previous_chat()
        return chat
        
    def next_conversation(self):
        """Navigate to next conversation.""" 
        chat = self.get_next_chat()
        return chat
        
    def get_current_conversation(self):
        """Get current conversation for display."""
        return self.get_current_chat()
        
    def get_conversation_info(self):
        """Get conversation navigation info."""
        if not self.chat_history:
            return 1, 1  # Show 1/1 when no history
        
        total = len(self.chat_history)
        
        # If current_chat_index is -1, we're viewing all conversations
        if self.current_chat_index == -1:
            current_pos = total  # Show as "all/total" or "latest/total"
        else:
            current_pos = self.current_chat_index + 1
            
        return current_pos, total
