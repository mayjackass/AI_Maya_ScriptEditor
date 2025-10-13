# 🚀 Quick Start Guide

## Installation (2 Minutes)

### 1. Extract Files
Extract this ZIP to your Maya scripts folder:
```
C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor\
```

### 2. Install PySide6
Open Command Prompt:
```bash
pip install PySide6
```

### 3. Set API Key (Optional for Morpheus AI)
Edit `ai/__init__.py`:
```python
OPENAI_API_KEY = "your-key-here"
```

### 4. Launch in Maya
In Maya Script Editor (Python tab):
```python
import sys
sys.path.insert(0, r"C:\Users\<YourName>\Documents\maya\scripts\ai_script_editor")
from main_window import AiScriptEditor
neo_window = AiScriptEditor()
neo_window.show()
```

**Done!** 🎉

---

## 📖 Full Documentation
- **INSTALLATION_GUIDE.md** - Complete installation steps
- **README.md** - Features and overview
- **MAYA_SETUP.md** - Maya integration details

## 💬 Support
- GitHub: https://github.com/mayjackass/AI_Maya_ScriptEditor
- Email: mayjackass@example.com

---

**NEO Script Editor v3.0 Beta** | Expires: January 31, 2026
