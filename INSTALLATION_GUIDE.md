# NEO Script Editor - Installation & Testing Guide

## 📦 What You Downloaded

You have downloaded **NEO Script Editor v3.0 Beta** - an advanced AI-powered script editor for Autodesk Maya.

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Extract the ZIP File
1. Download `NEO_Script_Editor_v3.0-beta.zip`
2. Extract to: `C:\Users\<YourName>\Documents\maya\scripts\`
3. Final path should be: `C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor\`

### Step 2: Install Dependencies
Open Command Prompt or PowerShell and run:

```bash
cd C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor
pip install PySide6
```

**OR** if you have multiple Python versions:
```bash
python -m pip install PySide6
```

### Step 3: Set Up Your OpenAI API Key
1. Get your API key from: https://platform.openai.com/api-keys
2. Open `ai/__init__.py` in the `ai_script_editor` folder
3. Find this line: `OPENAI_API_KEY = ""`
4. Replace with your key: `OPENAI_API_KEY = "sk-your-actual-key-here"`
5. Save the file

### Step 4: Launch in Maya
Open Maya, then open the **Script Editor** (Windows → General Editors → Script Editor)

**Python Tab**, paste and run:
```python
import sys
import os

# Add the script path
script_path = r"C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor"
if script_path not in sys.path:
    sys.path.insert(0, script_path)

# Import and launch
from main_window import AiScriptEditor

# Create window
neo_window = AiScriptEditor()
neo_window.show()
```

**That's it!** The NEO Script Editor window should appear! 🎉

---

## 📋 Detailed Installation Steps

### Requirements
- **Maya**: 2022 or newer (tested on 2022, 2023, 2024, 2025)
- **Python**: 3.7+ (included with Maya)
- **PySide6**: Qt framework for UI
- **OpenAI API Key**: For Morpheus AI assistant (optional for basic use)

### Installation Methods

#### Method 1: Maya Scripts Directory (Recommended)
1. **Extract ZIP** to Maya scripts folder:
   ```
   Windows: C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor\
   Mac: ~/Library/Preferences/Autodesk/maya/scripts/ai_script_editor/
   Linux: ~/maya/scripts/ai_script_editor/
   ```

2. **Install PySide6** (if not already installed):
   ```bash
   # Windows
   mayapy -m pip install PySide6
   
   # Mac/Linux
   mayapy -m pip install PySide6
   ```

3. **Configure API Key** (optional):
   - Open `ai/__init__.py`
   - Set `OPENAI_API_KEY = "your-key-here"`

4. **Launch from Maya**:
   ```python
   import sys
   sys.path.insert(0, r"C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor")
   from main_window import AiScriptEditor
   neo_window = AiScriptEditor()
   neo_window.show()
   ```

#### Method 2: Custom Location
1. **Extract ZIP** to any folder (e.g., `D:\Maya\Tools\`)
2. **Install dependencies** (same as above)
3. **Launch with full path**:
   ```python
   import sys
   sys.path.insert(0, r"D:\Maya\Tools\ai_script_editor")
   from main_window import AiScriptEditor
   neo_window = AiScriptEditor()
   neo_window.show()
   ```

#### Method 3: userSetup.py (Auto-launch)
Create or edit `userSetup.py` in your Maya scripts folder:

**Location:**
```
C:\Users\<YourName>\Documents\maya\scripts\userSetup.py
```

**Add this code:**
```python
import maya.cmds as cmds

def launch_neo_editor():
    """Launch NEO Script Editor"""
    import sys
    script_path = r"C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor"
    if script_path not in sys.path:
        sys.path.insert(0, script_path)
    
    from main_window import AiScriptEditor
    global neo_window
    neo_window = AiScriptEditor()
    neo_window.show()
    print("✅ NEO Script Editor loaded!")

# Optional: Launch on Maya startup
# cmds.evalDeferred(launch_neo_editor)

# Or create a shelf button
# (See MAYA_SETUP.md for shelf button instructions)
```

---

## 🧪 Testing the Installation

### Test 1: Basic Launch
Run the launch code in Maya Script Editor. You should see:
```
✅ NEO Script Editor launched successfully!
🎯 Window should now be visible
```

### Test 2: Code Editor
1. In the main editor window, type some Python code:
   ```python
   print("Hello from NEO!")
   import maya.cmds as cmds
   cmds.sphere()
   ```
2. Click **Run** or press `Ctrl+Enter`
3. A sphere should appear in Maya viewport

### Test 3: MEL Support
1. Switch to **MEL** mode (dropdown at top)
2. Type MEL code:
   ```mel
   sphere;
   print("MEL works!\n");
   ```
3. Run it - another sphere should appear

### Test 4: File Explorer
1. Check the **Explorer** dock (left side)
2. Browse your Maya scripts directory
3. Click files to open them in the editor

### Test 5: Syntax Highlighting
1. Type Python code - should see colors:
   - Keywords (blue): `def`, `class`, `import`
   - Strings (green): `"text"`
   - Comments (gray): `# comment`
   - Functions (yellow): `print()`

### Test 6: Morpheus AI (Optional)
**Requires OpenAI API Key**
1. Click **Morpheus AI** tab (right side)
2. Type a question: "How do I create a cube in Maya?"
3. Morpheus should respond with Maya commands

---

## 🎨 Features Overview

### VSCode-Style Interface
- **Dark theme** with professional code highlighting
- **Multiple docks**: Explorer, Console, Problems, Morpheus AI
- **Tabbed editing**: Open multiple files at once
- **Line numbers** with code folding (click ▶/▼ triangles)

### Code Intelligence
- **Syntax highlighting** for Python and MEL
- **Auto-indentation** (smart tab handling)
- **Find & Replace** with regex support
- **Error detection** (real-time syntax checking)

### AI Assistant (Morpheus)
- **Natural language** code generation
- **Context-aware** suggestions for Maya
- **Code explanations** and debugging help
- Powered by GPT-4 (requires OpenAI API key)

### Maya Integration
- **Execute in Maya**: Run code directly in viewport
- **Output console**: See results and errors
- **History tracking**: Browse previous commands
- **MEL support**: Full MEL language support

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PySide6'"
**Solution:**
```bash
mayapy -m pip install PySide6
# OR
python -m pip install PySide6
```

### Issue: "ImportError: cannot import name 'AiScriptEditor'"
**Solution:** Check your path is correct:
```python
import sys
print(sys.path)  # Verify path is included
```

### Issue: "Morpheus AI not responding"
**Solutions:**
1. Check API key in `ai/__init__.py`
2. Verify internet connection
3. Check OpenAI account has credits: https://platform.openai.com/usage

### Issue: "Window appears but is blank"
**Solution:** Update PySide6:
```bash
mayapy -m pip install --upgrade PySide6
```

### Issue: "Code doesn't execute"
**Solution:** Check Maya Script Editor for errors (Windows → General Editors → Script Editor)

### Issue: "Beta expired message"
**Solution:** This is a time-limited beta. Contact mayjackass@example.com for the full version.

---

## 📝 Beta Information

**Version:** 3.0-beta  
**Expiry Date:** January 31, 2026  
**Days Remaining:** Check Help → About

**Beta Limitations:**
- Time-limited until Jan 31, 2026
- All features fully functional during beta period
- Warning notifications 14 days before expiry

**After Beta Expires:**
- Contact for full version upgrade
- Email: mayjackass@example.com
- GitHub: https://github.com/mayjackass/AI_Maya_ScriptEditor

---

## 🎯 Quick Tips

### Keyboard Shortcuts
- `Ctrl+Enter` - Execute selected code
- `Ctrl+F` - Find in file
- `Ctrl+H` - Find & Replace
- `Ctrl+S` - Save file (if editing a file)
- `Ctrl+/` - Toggle comment
- `Tab` - Auto-indent

### Code Folding
- Click **▼** next to line numbers to collapse code blocks
- Click **▶** to expand
- Great for organizing long scripts!

### Multiple Files
- Open files from Explorer
- Tabs appear at the top
- Close tabs with X button
- Switch between tabs by clicking

### Morpheus AI Tips
- Be specific: "Create a cube at position 0,5,0"
- Ask for explanations: "Explain this Maya command"
- Request improvements: "Optimize this loop"

---

## 📞 Support

**Issues or Questions?**
- GitHub: https://github.com/mayjackass/AI_Maya_ScriptEditor/issues
- Email: mayjackass@example.com

**Feature Requests:**
- Open an issue on GitHub
- Tag with "enhancement"

**Bug Reports:**
- Include Maya version
- Include error messages
- Steps to reproduce

---

## 📄 License

This is a **beta version** with time-limited access.  
Full version available after beta testing period.  
© 2025 NEO Script Editor - All Rights Reserved

---

## 🚀 Next Steps

1. ✅ Install and launch NEO Script Editor
2. ✅ Test basic features (code execution, file opening)
3. ✅ Configure Morpheus AI (optional)
4. ✅ Create shelf button for easy access (see MAYA_SETUP.md)
5. ✅ Explore VSCode-style features
6. ✅ Provide feedback!

**Enjoy your enhanced Maya scripting experience!** 🎉

---

**Need help?** Check `README.md` and `MAYA_SETUP.md` for more details.
