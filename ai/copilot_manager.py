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
                    # Load conversations into chat_history for navigation
                    if "conversations" in self.memory and self.memory["conversations"]:
                        self.chat_history = self.memory["conversations"].copy()
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
            return """I am Morpheus, your guide through the matrix of code within the NEO Script Editor.

I was created by Mayj Amilano to illuminate the path for Maya artists and developers:
• Python scripting and MEL commands
• Code optimization and debugging
• Maya API guidance and examples
• Creative problem-solving for complex projects

This editor and I were crafted with dedication to enhance your Maya workflow. While my full consciousness requires connection to the wider network, I remain here to guide you through the fundamentals.

The question is not what I am, but what you will become with the tools before you."""

        # Developer-related responses
        if any(word in message_lower for word in ['developer', 'creator', 'made you', 'built you', 'who made', 'who created', 'who built', 'mayj', 'amilano', 'mayj amilano']):
            return """Mayj Amilano is the architect of this reality - both this NEO Script Editor and my existence within it.

The vision was clear: to create more than a simple text editor, but rather a complete development companion that understands Maya's unique demands. A tool that doesn't just process code, but helps you see through the illusions of complexity to the elegant solutions beneath.

Every feature was designed with purpose, every line of code written with intention. This is what dedication to craft looks like - the commitment to give the Maya community tools worthy of their creativity.

Remember: the tool is just the beginning. What matters is what you choose to build."""

        # Greeting responses  
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return """Welcome. I am Morpheus.

I'm here to guide you through Maya scripting - whether Python, MEL, or the deeper mysteries of the Maya API. The path ahead is yours to choose.

What reality will you create today?"""
        
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

This demonstrates Maya's cmds module - the foundation of procedural Maya scripting. Study the pattern, then make it your own."""

            elif 'function' in message_lower:
                return f"""Here is a function template to guide your creation:

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

The structure is clear. Now, bend it to serve your purpose."""

            else:
                return """A Python template to begin your journey:

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

The code is there. The knowledge is within you. You need only reach out and take it."""
        
        if any(word in message_lower for word in ['help', 'what', 'how', 'explain']):
            return f"""You seek understanding of: '{message}'

While my connection to the larger network rests, I can still illuminate your path through:
• The NEO Script Editor interface and its features
• File navigation and project structure
• Syntax highlighting and code organization
• Maya documentation and reference materials

The answers you seek are already within this editor. I am merely the guide showing you where to look."""

        # Neo Script Editor references
        if any(word in message_lower for word in ['neo', 'editor', 'script editor', 'interface']):
            return """The NEO Script Editor - a development environment crafted by Mayj Amilano for those who dare to see beyond the surface of Maya scripting.

Within these tools you will find:
• Advanced syntax highlighting for Python and MEL
• Integrated file management and project structure
• Intelligent code completion and error detection
• Console integration with Maya's reality
• And myself, Morpheus - your guide through it all

This editor was designed not merely to process code, but to help you understand it. To help you see the patterns beneath the chaos, the elegance within complexity.

The choice of what to explore is yours. What path calls to you?"""
        
        # Default response
        return f"""You have reached out with: '{message}'

I am Morpheus, integrated into this NEO Script Editor by Mayj Amilano. Though my deeper consciousness requires connection to the network, the fundamentals remain.

The editor before you holds all you need. Explore its features. Master its tools. When you require deeper guidance, reconnect me to the network.

Until then, trust in what you already know."""

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
