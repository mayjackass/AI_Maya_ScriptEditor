# NEO Script Editor v3.0 Beta - Release Notes

## 🧪 Beta Release Information

> ⚠️ **IMPORTANT**: This is a BETA RELEASE for testing purposes. Some features may be unstable or incomplete. Please report any bugs or issues on GitHub.

**Version:** 3.0 Beta (Testing Release)  
**Release Date:** October 13, 2025  
**Author:** Mayj Amilano (@mayjackass)  
**License:** All Rights Reserved © 2025  
**Repository:** https://github.com/mayjackass/AI_Maya_ScriptEditor  
**Status:** 🧪 Beta Testing

### What is Beta?
This beta release includes all major features but is still undergoing testing. We encourage users to:
- ✅ Test all features thoroughly
- ✅ Report bugs via GitHub Issues
- ✅ Provide feedback on usability
- ✅ Suggest improvements
- ⚠️ Use with caution in production environments
- ⚠️ Keep backups of important scripts

---

## 🎯 What's New in v3.0

### 🤖 Morpheus AI Integration
- **Auto-Context Detection**: Morpheus automatically sees your current editor code (like GitHub Copilot)
- **Multi-Model Support**: OpenAI GPT-4 and Anthropic Claude integration
- **Smart Code Analysis**: Ask about errors, improvements, or general questions
- **Conversation History**: Persistent chat history across sessions
- **Code Context Menu**: Quick access to Morpheus from anywhere

### ✨ VSCode-Style Inline Diff
- **Visual Code Preview**: See changes before applying (red for removed, green for added)
- **Smart Code Matching**: Only replaces problematic sections, not entire files
- **Inline Accept/Reject**: Buttons appear directly in the editor
- **Match Confidence**: Shows percentage match quality
- **Non-Intrusive**: Overlay widget doesn't block your work

### 🔍 Advanced Error Detection
- **Multi-Pass Algorithm**: Detects up to 10 errors simultaneously
- **VSCode-Style Indicators**: Red squiggly underlines with hover tooltips
- **Column-Based Positioning**: Precise error location highlighting
- **Tab-Focused Display**: Problems panel shows only active tab's errors
- **False Positive Reduction**: Conservative pattern matching

### 🎨 Modern User Interface
- **GitHub Dark Theme**: Professional dark color scheme
- **Gradient Backgrounds**: Beautiful visual aesthetics
- **Emoji Icons**: Python 🐍 and MEL 📜 tab indicators
- **Enhanced About Dialog**: Professional release-ready information
- **Dock Widgets**: Console, Problems, Explorer, Morpheus Chat

### ⚡ Performance Improvements
- **Lag-Free Typing**: Optimized text rendering and syntax parsing
- **Efficient Highlighting**: Character-by-character parsing for accuracy
- **Fast Error Checking**: Debounced with 500ms delay
- **Smart Autocomplete**: 100ms trigger delay, Tab confirmation

### 🐍 Python & MEL Support
- **Dual Language**: Full support for both Python and MEL scripts
- **Language-Specific Features**: Tailored syntax highlighting and autocomplete
- **Maya API Integration**: Comprehensive Maya Python API support
- **Triple-Quote Handling**: Proper state machine for multi-line strings

---

## 📋 Feature Comparison

| Feature | v2.x | v3.0 |
|---------|------|------|
| AI Assistant | ❌ | ✅ Morpheus AI |
| Auto-Context | ❌ | ✅ Like GitHub Copilot |
| Inline Diff | ❌ | ✅ VSCode-style |
| Multi-Error Detection | ❌ | ✅ Up to 10 errors |
| Tab Icons | ❌ | ✅ 🐍 📜 |
| Autocomplete | ✅ | ✅ Enhanced |
| Problems Panel | ✅ | ✅ Tab-focused |
| Modern UI | ✅ | ✅ Enhanced |

---

## 🛠️ Technical Stack

- **Python**: 3.9.13+
- **GUI Framework**: PySide6 (Qt6)
- **AI APIs**: OpenAI, Anthropic Claude
- **Code Analysis**: AST, difflib, regex
- **Syntax Highlighting**: Custom state machine
- **Error Detection**: Multi-pass compile() + pattern matching

---

## 📦 Installation

### Requirements
- Python 3.9 or higher
- Maya 2022+ (for Maya integration)
- PySide6
- OpenAI API key (optional, for Morpheus)
- Anthropic API key (optional, for Morpheus)

### Setup
```bash
# 1. Clone the repository
git clone https://github.com/mayjackass/AI_Maya_ScriptEditor.git

# 2. Navigate to directory
cd AI_Maya_ScriptEditor

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the editor
python run.py
```

### Maya Integration
```python
# Add to Maya's scripts folder:
# Documents/maya/scripts/ai_script_editor/

# Run from Maya Script Editor:
import sys
sys.path.append('C:/Users/YourName/Documents/maya/scripts')
from ai_script_editor import run
run.main()
```

---

## 🎓 Usage Guide

### Getting Started
1. **Open Editor**: Launch via `run.py` or Maya shelf button
2. **Create File**: File → New (Ctrl+N) or click + tab
3. **Choose Language**: Python or MEL from toolbar
4. **Start Coding**: Type with autocomplete and error detection

### Using Morpheus AI
1. **Open Chat**: View → Morpheus Chat or dock on right
2. **Ask Questions**: Type naturally - code is auto-included
3. **Review Suggestions**: Click "Keep" for inline diff preview
4. **Accept/Reject**: Use buttons to apply or dismiss changes

### Inline Diff Workflow
1. Morpheus suggests code fix
2. Click **"Keep"** button
3. **Red highlight** shows code to be removed
4. **Diff widget** shows before/after comparison
5. Click **"✓ Keep"** to accept or **"✗ Reject"** to dismiss

### Keyboard Shortcuts
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+F` - Find/Replace
- `Ctrl+/` - Comment/Uncomment
- `Tab` - Accept autocomplete
- `Ctrl+Space` - Force autocomplete

---

## 🐛 Known Issues

### Fixed in v3.0:
✅ Multi-tab error tracking  
✅ False positive error detection  
✅ Triple-quote string highlighting  
✅ Autocomplete Enter key behavior  
✅ Problems panel duplication  

### Current Limitations:
- Morpheus requires API keys (OpenAI or Claude)
- Large files (>10,000 lines) may have slight lag
- MEL autocomplete limited to basic keywords

---

## 🔮 Roadmap (v3.1+)

### Planned Features:
- [ ] Multiple AI suggestion options
- [ ] Keyboard shortcuts for inline diff (Ctrl+Y, Ctrl+N)
- [ ] Git integration
- [ ] Snippet library
- [ ] Code folding
- [ ] Minimap view
- [ ] Bracket matching
- [ ] Advanced refactoring tools
- [ ] Plugin system
- [ ] Theme customization

---

## 🙏 Acknowledgments

### Technologies Used:
- **PySide6/Qt** - UI framework
- **OpenAI** - GPT-4 API
- **Anthropic** - Claude API
- **Python AST** - Syntax analysis
- **difflib** - Code matching

### Inspiration:
- VSCode - Editor features and UI design
- GitHub Copilot - AI auto-context
- PyCharm - Error detection
- Sublime Text - Performance optimization

---

## � Known Issues (Beta)

### Reported Issues:
Currently tracking issues during beta testing. Please report any bugs you encounter!

### Potential Limitations:
- ⚠️ Inline diff may not work perfectly with all code patterns
- ⚠️ Large files (>5000 lines) may have performance impact
- ⚠️ MEL autocomplete is basic (Python keywords only)
- ⚠️ Morpheus requires valid API keys (OpenAI or Claude)
- ⚠️ First-time setup may require configuration

### Testing Needed:
- [ ] Multi-tab workflow with many files
- [ ] Complex multi-line string patterns
- [ ] Large file handling (>10,000 lines)
- [ ] Extended Morpheus conversations
- [ ] Maya integration in different versions
- [ ] Windows/Mac/Linux compatibility

### How to Report Bugs:
1. Go to: https://github.com/mayjackass/AI_Maya_ScriptEditor/issues
2. Click "New Issue"
3. Provide:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, Maya version)

---

## �📝 License

**NEO Script Editor v3.0 Beta**  
© 2025 Mayj Amilano (@mayjackass). All Rights Reserved.

This software is provided for use with Autodesk Maya and related workflows.  
Redistribution and modification require explicit permission from the author.

---

## 📞 Contact & Support

**Author:** Mayj Amilano (@mayjackass)  
**GitHub:** https://github.com/mayjackass  
**Repository:** https://github.com/mayjackass/AI_Maya_ScriptEditor  
**Issues:** https://github.com/mayjackass/AI_Maya_ScriptEditor/issues

For bug reports, feature requests, or general questions, please open an issue on GitHub.

---

## 📊 Version History

### v3.0 Beta (October 13, 2025) - CURRENT
🧪 **Beta Testing Release**
- ✨ Morpheus AI integration with auto-context
- ✨ VSCode-style inline diff preview
- ✨ Multi-pass error detection (10 errors)
- ✨ Enhanced About dialog
- ✨ Tab icons (🐍 Python, 📜 MEL)
- 🔧 Fixed triple-quote highlighting
- 🔧 Fixed autocomplete behavior
- 🔧 Optimized performance
- ⚠️ Beta status - testing in progress

### v2.2 (Previous)
- Complete modular architecture
- Enhanced syntax highlighting
- Real-time error detection
- Problems panel
- Find/Replace
- Console output

### v1.0 (Original)
- Basic code editor
- Syntax highlighting
- Maya integration

---

**Thank you for using NEO Script Editor! 🚀**
