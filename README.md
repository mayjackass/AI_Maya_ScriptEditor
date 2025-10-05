# AI Script Editor for Maya 

A modular, PySide6-based script editor for Autodesk Maya with built-in OpenAI integration (GPT-powered coding assistant).  
Supports secure local encryption of API keys, live code execution, syntax highlighting, and Copilot-style inline completions.

## Features
- Line numbering, syntax highlighting, dark theme (Charcoal 2)
- Run & lint scripts inside Maya
- Secure local OpenAI key encryption
- Integrated AI chat and code suggestions
- Tabbed editor, explorer, and output console

## Installation
1. Copy the `ai_script_editor` folder into your Maya `scripts/` directory.
2. Launch from Maya Script Editor:
   ```python
   import ai_script_editor.ai_script_editor as aise
   aise.launch_ai_script_editor()
