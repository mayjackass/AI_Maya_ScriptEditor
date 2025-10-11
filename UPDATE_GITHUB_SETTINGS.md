# Update GitHub Repository Settings

## 🎯 Current Status
Your code has been pushed, but the GitHub repository settings need to be updated manually on GitHub.com.

---

## 📋 Step-by-Step Guide to Update GitHub Settings

### 1. Update Repository Description

**Go to:** https://github.com/mayjackass/AI_Maya_ScriptEditor

**Steps:**
1. Click the **⚙️ Settings** icon (gear) next to "About" on the right side
2. Update the fields:

   - **Description:** 
     ```
     Next-generation Maya script editor with Morpheus AI - Your philosophical mentor for Python and MEL scripting 🕶️
     ```
   
   - **Website:** (optional - add if you have a portfolio/demo link)
   
   - **Topics:** Click "Add topics" and add:
     - `maya`
     - `python`
     - `script-editor`
     - `ai-assistant`
     - `morpheus`
     - `openai`
     - `anthropic`
     - `pyside6`
     - `the-matrix`
     - `code-editor`

3. Click **"Save changes"**

---

### 2. (Optional) Rename Repository

**If you want to rename from `AI_Maya_ScriptEditor` to `NEO_Script_Editor`:**

**Go to:** https://github.com/mayjackass/AI_Maya_ScriptEditor/settings

**Steps:**
1. Scroll down to **"Danger Zone"** section
2. Click **"Rename repository"**
3. Enter new name: `NEO_Script_Editor`
4. Click **"I understand, rename repository"**

**⚠️ Important:** After renaming, update your local git remote:
```bash
git remote set-url origin https://github.com/mayjackass/NEO_Script_Editor.git
```

---

### 3. Create v3.0.0 Release

**Go to:** https://github.com/mayjackass/AI_Maya_ScriptEditor/releases/new

**Release Details:**

- **Tag:** `v3.0.0`
- **Release title:** `🕶️ NEO Script Editor v3.0 - Morpheus AI Release`
- **Description:**

```markdown
# 🕶️ NEO Script Editor v3.0 - The Morpheus AI Update

*"I can only show you the door. You're the one that has to walk through it."*

## 🎉 Major Features

### 🤖 Morpheus AI - Your Coding Mentor
- Matrix-inspired AI personality with philosophical guidance
- Dual AI support: **OpenAI GPT-4o** & **Anthropic Claude Sonnet**
- Context-aware code assistance with interactive Copy/Apply/Keep buttons
- Custom Morpheus icon (with sunglasses!) throughout the interface
- Shorter, impactful Matrix-themed welcome message

### 🏗️ Architecture Overhaul
- **83.9% code reduction!** (2242 lines → 361 lines in main window)
- Manager Pattern for clean separation of concerns:
  - `FileManager` - File operations and folder browsing
  - `MenuManager` - Menu bar and keyboard shortcuts
  - `DockManager` - Panel management (Explorer, Console, Problems)
  - `FindReplaceManager` - Search and replace functionality
  - `ChatManager` - Morpheus AI chat system
- Dramatically improved maintainability and extensibility

### ✨ New Features
- **Open Folder** (`Ctrl+Shift+O`): Browse and open entire project folders
- **Save As** (`Ctrl+Shift+S`): Save files with new names
- **Enhanced Toolbar**: Professional icons with consistent sizing
- **Custom Dock Controls**: Close and float buttons on Morpheus chat
- **Thinking Indicator**: Visual "⏳ Morpheus is pondering..." feedback
- **Matrix Welcome**: Philosophical greeting in chat dock

### 🎨 UI/UX Improvements
- Morpheus icon appears in:
  - Toolbar (18x18, properly sized)
  - View menu
  - Chat messages (16x16)
- Removed icon clutter from dock title bar
- Optimized icon sizes for visual consistency
- "MORPHEUS" tag in output console (was "COPILOT")
- Updated window title: "🕶️ NEO Script Editor v3.0 - Morpheus AI"

### 🐛 Bug Fixes
- Fixed Morpheus chat button not opening dock
- Fixed missing close/detach buttons on custom dock title
- Fixed toolbar icon sizing inconsistencies
- Fixed "Save" icon showing as question mark
- Changed Syntax Check icon from 🔍 to ✓

## 📥 Installation

See [README.md](https://github.com/mayjackass/AI_Maya_ScriptEditor/blob/main/README.md) for complete setup instructions.

**Quick Start:**
```bash
# Install dependencies
pip install PySide6 openai anthropic

# Run the editor
python main_window.py

# Configure API key in Tools → Settings
```

## 📚 Documentation

- **README.md** - Complete feature overview and installation
- **GITHUB_UPDATE_GUIDE.md** - Guide for updating repository settings
- **docs/** - Comprehensive feature documentation

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Morpheus AI Chat | `Ctrl+Shift+M` |
| Open Folder | `Ctrl+Shift+O` |
| Save As | `Ctrl+Shift+S` |
| Run Script | `F5` |
| Syntax Check | `F7` |

## 🙏 Credits

**Created by:** [Mayj Amilano](https://github.com/mayjackass)  
**Inspired by:** The Matrix (1999)  
**Special Thanks:** The Maya community and all contributors

---

### *"Remember... all I'm offering is the truth. Nothing more."* 💊

### Full Changelog

**Added:**
- Morpheus AI with Matrix-inspired personality and responses
- Dual AI provider support (OpenAI GPT-4o + Anthropic Claude Sonnet)
- Open Folder feature with folder browser
- Save As functionality
- Custom Morpheus icon system (assets/morpheus.png)
- Manager Pattern architecture (5 dedicated managers)
- Enhanced toolbar with proper icon sizing
- Custom dock title controls (close/float buttons)
- Philosophical Matrix-themed chat greeting

**Changed:**
- Window title: "NEO Script Editor v3.0 - Morpheus AI"
- Main window reduced from 2242 to 361 lines (refactored to managers)
- Morpheus chat greeting shortened for better UX
- Thinking indicator: "⏳ Morpheus is pondering..." (was robot emoji)
- Console tag: "MORPHEUS" (was "COPILOT")
- Syntax Check icon: ✓ (was 🔍)
- Toolbar icon sizes standardized (18x18 for custom icons)

**Fixed:**
- Morpheus button not triggering chat dock
- Missing dock control buttons on custom title bar
- Inconsistent toolbar icon sizes
- Save icon displaying incorrectly

**Removed:**
- Icon clutter from chat dock title
- All "copilot" references in code and comments
```

---

### 4. Update README Badge (Optional)

Add a version badge to your README.md:

```markdown
![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Maya](https://img.shields.io/badge/Maya-2020+-orange)
![License](https://img.shields.io/badge/license-MIT-green)
```

---

### 5. Social Media Announcement Template

**For Reddit r/Maya, CGSociety, etc.:**

```
🕶️ NEO Script Editor v3.0 Released - Morpheus AI for Maya!

Just released a major update to my Maya script editor with an AI assistant 
that talks like Morpheus from The Matrix!

Key Features:
• Morpheus AI mentor with philosophical coding wisdom
• Dual AI support (OpenAI GPT-4o & Anthropic Claude)
• Manager Pattern architecture (83.9% code reduction!)
• Modern dark theme with professional tools
• Open Folder, Save As, and enhanced workflow

Free & Open Source → https://github.com/mayjackass/AI_Maya_ScriptEditor

"I can only show you the door. You're the one that has to walk through it."

#Maya #Python #AI #TheMatrix #OpenSource
```

---

## ✅ Quick Checklist

- [ ] Update repository description
- [ ] Add topics/tags
- [ ] Create v3.0.0 release
- [ ] (Optional) Rename repository to NEO_Script_Editor
- [ ] (Optional) Add version badge to README
- [ ] (Optional) Announce on social media

---

## 📌 Direct Links

- **Repository:** https://github.com/mayjackass/AI_Maya_ScriptEditor
- **Settings:** https://github.com/mayjackass/AI_Maya_ScriptEditor/settings
- **New Release:** https://github.com/mayjackass/AI_Maya_ScriptEditor/releases/new
- **Edit About:** Click ⚙️ gear icon next to "About" section on main page

---

**Need Help?** Check GitHub's official guides:
- [About repositories](https://docs.github.com/en/repositories)
- [Creating releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
