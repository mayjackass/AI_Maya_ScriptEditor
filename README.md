# NEO Script Editor v3.2 Beta - Now with Maya Dockable Integration!
### *"I can only show you the door. You're the one that has to walk through it."*

[![Version](https://img.shields.io/badge/version-3.2--beta-orange.svg)](https://github.com/mayjackass/AI_Maya_ScriptEditor)
[![Status](https://img.shields.io/badge/status-beta--testing-yellow.svg)](https://github.com/mayjackass/AI_Maya_ScriptEditor)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Maya](https://img.shields.io/badge/maya-320%2B%20commands-green.svg)](https://github.com/mayjackass/AI_Maya_ScriptEditor)
[![License](https://img.shields.io/badge/license-Beta%20License-red.svg)](BETA_LICENSE.md)

**Developed by:** Mayj Amilano ([mayjackass](https://github.com/mayjackass))  
**Built for:** Autodesk Maya 2022+  
**Framework:** PySide6 (Qt6) | Python 3.9+  
**Release Date:** October 20, 2025  
**Beta Expires:** January 31, 2026  
**Status:** Free Beta Testing

> **BETA NOTICE**: This is a time-limited beta release for testing and evaluation. Please report issues on [GitHub Issues](https://github.com/mayjackass/AI_Maya_ScriptEditor/issues).

A next-generation AI-powered Maya script editor with **Morpheus AI** integration, VSCode-style features, and **THE MOST COMPREHENSIVE Maya command validation** of any IDE! Experience coding like using GitHub Copilot, but built specifically for Maya Python and MEL with **intelligent error detection** for all 320+ Maya commands.

## 🆕 NEW in v3.2: Maya Dockable Integration!

**Perfect Maya Workflow:** Editor on top, viewport below! 

- **🔥 Maya Workspace Control**: Docks like built-in Maya panels (Script Editor, Outliner, etc.)
- **🎨 NEO Shelf Tab**: Dedicated shelf with NEO logo buttons for one-click access
- **📌 Native Integration**: Tabs with other panels, remembers position, saves in workspace layouts
- **⚡ Perfect Workflow**: Dock at top for editor-above, viewport-below setup

---

## Revolutionary Features

### Comprehensive Maya Command Validation
- 320+ Maya commands validated in real-time
- Smart typo detection with "Did you mean...?" suggestions
- All Maya APIs covered: cmds, PyMEL, OpenMaya, MEL
- Intelligent fuzzy matching for typos (e.g., `setAttrs` → suggests `setAttr`)
- 12 validation types: Missing imports, invalid commands, API usage errors, and more
- Real-time feedback in Problems window before you even run the code!

**Example:** Type `cmds.polySpere()` and the editor instantly detects: *"Unknown cmds command: 'polySpere'. Did you mean 'polySphere'?"*

### Morpheus AI Assistant
- Auto-context detection (sees your code automatically)
- Multi-model support (OpenAI GPT-4, Anthropic Claude)
- Conversation history with persistent storage
- Smart code suggestions with inline diff preview
- Knows all 320+ Maya commands and can explain validation errors
- Offline mode toggle for working without API connection

### VSCode-Style Editor
- Inline diff preview with red/green highlighting
- Real-time Maya command validation (catches typos instantly!)
- Advanced autocomplete with Tab confirmation
- Syntax highlighting for Python & MEL with 270+ Maya keywords

### Smart Maya Code Analysis
- 12 comprehensive validation checks (import detection, command validation, API usage, MEL syntax)
- Fuzzy command matching algorithm (90%+ similarity detection)
- Multi-pass error detection (up to 10 errors)
- Column-based error positioning
- Tab-focused problems panel
- False positive reduction

### Professional Maya-Aware Interface
- Maya command tooltips with documentation (270+ commands)
- GitHub Dark theme with gradient backgrounds
- Custom Python/MEL tab icons
- Customizable dock widgets
- Problems window with intelligent Maya suggestions

---

## Key Features

**Morpheus AI Assistant**
- Auto-context detection (sees your code automatically)
- Multi-model support (OpenAI GPT-4, Anthropic Claude)
- Conversation history with persistent storage
- Smart code suggestions with inline diff preview
- Offline mode toggle for working without API connection

**VSCode-Style Editor**
- Inline diff preview with red/green highlighting
- Real-time error detection (up to 10 errors)
- Advanced autocomplete with Tab confirmation
- Syntax highlighting for Python & MEL

**Maya Integration Options**
- **🔥 Dockable Mode**: Integrates into Maya's UI like built-in Script Editor
- **🪟 Standalone Mode**: Traditional floating window for multi-monitor setups
- **🎨 NEO Shelf**: Dedicated shelf tab with logo buttons for easy access

**Smart Code Analysis**
- Multi-pass error detection algorithm
- Column-based error positioning
- Tab-focused problems panel
- False positive reduction

**Modern Interface**
- GitHub Dark theme with gradient backgrounds
- Custom Python/MEL tab icons
- Customizable dock widgets
- Professional release-quality UI

---

## Quick Start

### Option 1: Maya Dockable Mode (Recommended) 🔥

1. **Copy `scripts/maya/userSetup.py` to:** `Documents/maya/scripts/userSetup.py`
2. **Restart Maya**  
3. **Run in Maya Script Editor:**
   ```python
   complete_neo_setup()  # Creates shelf + launches docked editor
   ```
4. **Perfect Workflow:** Drag NEO editor to top of Maya for editor-above, viewport-below!

### Option 2: Standalone Mode

```bash
# Clone the repository
git clone https://github.com/mayjackass/AI_Maya_ScriptEditor.git
cd AI_Maya_ScriptEditor

# Install dependencies  
pip install -r requirements.txt

# Launch the editor
python run.py
```

**First Time Setup:**
1. Set your OpenAI or Anthropic API key in `Tools → Settings`
2. Open Morpheus chat from the toolbar or `View → Morpheus Chat`  
3. Start coding - Morpheus automatically sees your code!
4. Toggle offline mode if you want to work without API connection

### Maya Commands Available:
- `complete_neo_setup()` - Complete setup: shelf + docked editor
- `neo_docked()` - Launch dockable editor
- `create_neo_shelf()` - Create NEO shelf tab with logo buttons
- `launch_neo_editor()` - Launch standalone window

---

## Project Structure

```
ai_script_editor/
├── run.py                 # Main launcher
├── main_window.py         # Application window
├── __init__.py            # Package initialization
│
├── ai/                    # AI integration
│   ├── chat.py           # Morpheus AI chat system
│   └── copilot_manager.py # Copilot-style features
│
├── editor/                # Code editor
│   ├── code_editor.py    # Main editor with Maya validation
│   ├── highlighter.py    # Python/MEL syntax highlighting
│   ├── hover_docs.py     # Maya command documentation (270+ commands)
│   ├── maya_commands.py  # Maya command validation database (320+ commands)
│   └── inline_diff.py    # VSCode-style inline diff
│
├── ui/                    # User interface
│   ├── chat_manager.py   # Morpheus chat UI
│   ├── dock_manager.py   # Dock widgets manager
│   ├── file_manager.py   # File operations
│   ├── find_replace_manager.py # Find/Replace
│   ├── menu_manager.py   # Menu system
│   └── output_console.py # Console output
│
├── model/                 # Data models
│   └── hierarchy.py      # Code structure
│
├── utils/                 # Utilities
│   └── redirect_output.py # Output redirection
│
├── scripts/maya/              # 🆕 Maya Integration Scripts
│   ├── maya_dockable_launcher.py     # Dockable Maya workspace control  
│   ├── maya_shelf_creator.py         # NEO shelf tab with logo buttons
│   ├── complete_setup.py             # One-click complete setup
│   ├── maya_shelf_button.py          # Shelf button instructions
│   └── userSetup.py                  # Enhanced Maya userSetup.py
│
├── tests/                 # Test suite
├── docs/                  # Documentation
└── assets/               # Icons and resources (includes NEO logos)
```
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
- **270+ Maya Commands Highlighted**: polySphere, setAttr, shadingNode, MFnMesh, etc.
- **Comprehensive Maya Validation**: 320+ commands checked in real-time
- **Smart Typo Detection**: Fuzzy matching suggests correct commands
- **Multi-Error Detection**: Finds ALL syntax errors, not just the first one
- **Visual Error Indicators**: Red wavy underlines with detailed problem descriptions
- **Line Numbers & Current Line Highlighting**: Professional IDE experience
- **Smart Indentation**: Auto-indent with Tab/Shift+Tab support
- **Undo/Redo**: Full edit history management

### Intelligent Maya Tools
- **Maya Command Validation**: Real-time checking of all cmds, PyMEL, OpenMaya, MEL commands
- **Smart Suggestions**: "Did you mean 'polySphere'?" for typos like 'polySpere'
- **Import Detection**: Catches missing maya.cmds, PyMEL, OpenMaya imports
- **API Usage Validation**: Detects common mistakes (missing [0], setAttr without value, etc.)
- **Problems Panel**: Real-time Maya-aware error reporting with helpful fixes
- **Command Tooltips**: Hover documentation for 270+ Maya commands
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

**Ask Morpheus About Maya:**
- "How do I create a sphere in Maya?"
- "Why is setAttrs giving me an error?" *(Morpheus knows it should be setAttr!)*
- "What's the difference between cmds and PyMEL?"
- "Optimize this loop for better performance"
- "What's wrong with my script?"
- "Explain this Maya API error"
- "Show me how to use shadingNode correctly"

**Morpheus responds with:**
- Philosophical coding wisdom
- Matrix-inspired metaphors
- Practical Python/MEL solutions
- Maya command validation explanations
- Interactive code blocks you can Copy/Apply/Keep

**Example:**
> **You:** "Why am I getting 'setAttrs' error?"
> 
> **Morpheus:** "Ah, I see you've encountered a typo in the Matrix. The correct command is `setAttr` (singular), not `setAttrs` (plural). Maya's attribute commands use singular form - one attribute, one command. The NEO editor detected this automatically and suggested the fix. Here's the correct usage:
> ```python
> cmds.setAttr("pCube1.translateX", 10)
> ```
> Remember: Free your mind from typos. The editor sees what you cannot see yet."

## Documentation

Comprehensive guides in the `docs/` folder:
- `COMPREHENSIVE_MAYA_VALIDATION.md` - Complete Maya validation system docs
- `MAYA_VALIDATION_QUICK_GUIDE.md` - Quick reference for common typos
- `MAYA_VALIDATION_SUMMARY.md` - Implementation details
- `MORPHEUS_AI.md` - AI system configuration
- `COMPLETE_MAYA_INTEGRATION.md` - Maya API documentation (270+ commands)
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