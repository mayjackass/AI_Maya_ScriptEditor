# NEO Script Editor
### *"I can only show you the door. You're the one that has to walk through it."*

**Developed by:** [Mayj Amilano](https://github.com/mayjackass)  
**Built for:** Autodesk Maya 2020+  
**Framework:** PySide6 | Python 3.8+

A next-generation Maya script editor with **Morpheus AI** - your philosophical mentor for Python and MEL scripting. Like Neo discovering the Matrix, you'll see your code in ways you never imagined.

---

## Quick Start

```bash
# Launch NEO Script Editor
python main_window.py

# Or use the launcher
python launch.py
```

**First Time Setup:**
1. Set your OpenAI or Anthropic API key in `Tools → Settings`
2. Open the Morpheus AI chat (toolbar icon or `Ctrl+Shift+M`)
3. Start coding with AI guidance

## Project Structure

```
ai_script_editor/
├── main_window.py          # Main application entry point
├── launch.py              # Alternative launcher
├── run.py                 # Simple runner script
├── __init__.py            # Package initialization
│
├── ai/                    # AI and chat functionality
│   ├── chat.py           # AI Morpheus chat system
│   └── copilot_manager.py # GitHub Copilot-style features
│
├── editor/                # Code editor components
│   ├── code_editor.py    # Main code editor with syntax highlighting
│   └── highlighter.py    # Python and MEL syntax highlighters
│
├── model/                 # Data models
│   └── hierarchy.py      # Code hierarchy and structure
│
├── ui/                    # User interface components
│   └── output_console.py # Output console widget
│
├── utils/                 # Utility functions
│
├── tests/                 # Test files and legacy tests
│   ├── legacy/           # Archived test files
│   └── *.py              # Current test files
│
├── docs/                  # Documentation and markdown files
│   ├── *.md              # Feature documentation
│   └── PROJECT_STRUCTURE.md
│
└── archive/               # Archived and debug files
    ├── debug_*.py        # Debug utilities
    ├── main_window_*.py  # Backup versions
    └── *.py              # Other archived files
```

## Key Features

### Morpheus AI - Your Coding Mentor
- **Matrix-Inspired Personality**: Philosophical, mentor-like guidance for your code
- **Dual AI Support**: Choose between OpenAI GPT-4o or Anthropic Claude Sonnet
- **Context-Aware Chat**: Morpheus analyzes your current code and provides enlightened solutions
- **Code Suggestions**: Copy, Apply, or Keep AI-generated code with interactive buttons
- **Custom Morpheus Icon**: Authentic Matrix branding throughout the interface

### Professional Code Editor
- **Advanced Syntax Highlighting**: VS Code-style dark theme for Python and MEL
- **Multi-Error Detection**: Finds ALL syntax errors, not just the first one
- **Visual Error Indicators**: Red wavy underlines with detailed problem descriptions
- **Line Numbers & Current Line Highlighting**: Professional IDE experience
- **Smart Indentation**: Auto-indent with Tab/Shift+Tab support
- **Undo/Redo**: Full edit history management

### Intelligent Tools
- **Problems Panel**: Real-time error reporting with line numbers
- **Find & Replace**: `Ctrl+F` / `Ctrl+H` with regex support
- **File Explorer**: Dockable folder browser with double-click to open
- **Output Console**: Live execution logs and Maya command feedback
- **Syntax Checker**: Manual validation with `F7` shortcut
- **Script Runner**: Execute code directly in Maya with `F5`

### Modern Interface
- **Dockable Panels**: Explorer, Morpheus AI Chat, Output Console, Problems
- **Tabbed Editor**: Multiple files with auto-save prompts
- **Custom Toolbar**: Quick access to New, Open, Save, AI Chat, and more
- **Keyboard Shortcuts**: Full VS Code-style navigation
- **Dark Theme**: Easy on the eyes during long coding sessions

## Installation

### Requirements
- **Python 3.8+** (built-in with Maya 2020+)
- **PySide6** (Qt6 framework)
- **API Keys** (optional, for Morpheus AI):
  - OpenAI API key (GPT-4o, GPT-4o-mini)
  - OR Anthropic API key (Claude Sonnet)

### Setup Steps

1. **Install Dependencies**
```bash
pip install PySide6 openai anthropic
```

2. **Copy to Maya Scripts**
```bash
# Windows
C:\Users\<username>\Documents\maya\scripts\ai_script_editor\

# macOS
~/Library/Preferences/Autodesk/maya/scripts/ai_script_editor/

# Linux
~/maya/scripts/ai_script_editor/
```

3. **Configure API Keys**
- Launch the editor: `python main_window.py`
- Go to `Tools → Settings`
- Enter your OpenAI or Anthropic API key
- Select your preferred AI provider and model

4. **Optional: Maya Auto-Launch Setup**
Create a `userSetup.py` in your Maya scripts folder to auto-load NEO on Maya startup:
```python
"""
Place this file at: C:\Users\<username>\Documents\maya\scripts\userSetup.py
"""
import sys
import os

def setup_neo_editor():
    """Setup NEO Script Editor for Maya"""
    neo_path = os.path.join(os.path.dirname(__file__), 'ai_script_editor')
    if neo_path not in sys.path:
        sys.path.insert(0, neo_path)
        print("[NEO] ✓ Script Editor ready")
    
    # Create launcher function
    def launch_neo_editor():
        """Launch NEO Script Editor"""
        from main_window import AiScriptEditor
        window = AiScriptEditor()
        window.show()
        return window
    
    # Make it globally available in Maya
    import __main__
    __main__.launch_neo_editor = launch_neo_editor

setup_neo_editor()
```

Then in Maya, just run: `launch_neo_editor()`

**See [MAYA_SETUP.md](MAYA_SETUP.md) for detailed Maya integration guide**

### Running Tests
```bash
cd tests/
python test_morpheus_chat.py
python test_syntax_checker.py
python run_all_tests.py
```
> **Note:** The `tests/` directory is for development only and not included in releases.

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | `Ctrl+N` |
| Open File | `Ctrl+O` |
| Open Folder | `Ctrl+Shift+O` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |
| Find | `Ctrl+F` |
| Replace | `Ctrl+H` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |
| Run Script | `F5` |
| Syntax Check | `F7` |
| Morpheus AI Chat | `Ctrl+Shift+M` |
| Explorer Panel | `Ctrl+Shift+E` |
| Output Console | `Ctrl+Shift+C` |
| Problems Panel | `Ctrl+Shift+U` |

## Morpheus AI Tips

**Ask Morpheus:**
- "How do I create a sphere in Maya?"
- "Optimize this loop for better performance"
- "What's wrong with my script?"
- "Explain this error message"
- "Show me a better way to write this"

**Morpheus responds with:**
- Philosophical coding wisdom
- Matrix-inspired metaphors
- Practical Python/MEL solutions
- Interactive code blocks you can Copy/Apply/Keep

## Documentation

Comprehensive guides in the `docs/` folder:
- `MORPHEUS_AI.md` - AI system configuration
- `SYNTAX_HIGHLIGHTING.md` - Editor features
- `KEYBOARD_SHORTCUTS.md` - Full shortcut reference
- `PROJECT_STRUCTURE.md` - Codebase architecture
- Feature implementation docs and performance notes

## Configuration

Settings stored via QSettings (`AI_Script_Editor/settings`):
- **API Keys**: OpenAI and Anthropic credentials (encrypted)
- **AI Provider**: Selected provider and model
- **Editor Preferences**: Theme, font size, tab width
- **Window Layout**: Panel positions and visibility

## Contributing

Contributions welcome! This project uses:
- **Manager Pattern Architecture** for clean separation of concerns
- **PySide6** for cross-platform Qt6 UI
- **Custom Morpheus AI Integration** with Matrix-inspired philosophical responses
- **Dual AI Provider Support** (OpenAI & Anthropic)

**How to Contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Keep test files in `tests/`
4. Document new features in `docs/`
5. Submit a pull request

## License

MIT License - Free to use and modify.

---

## Credits

**Created by:** [Mayj Amilano](https://github.com/mayjackass)  
**Inspired by:** The Matrix (1999) - *"Free your mind"*  
**Special Thanks:** The Maya community and all contributors

---

### *"Remember... all I'm offering is the truth. Nothing more."*

[Back to Top](#neo-script-editor)