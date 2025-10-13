# 🧪 NEO Script Editor v3.0 Beta - Testing Guide

## Welcome Beta Testers! 👋

Thank you for helping test **NEO Script Editor v3.0 Beta**! Your feedback is crucial for making this the best Maya script editor possible.

---

## ⚠️ Beta Status

**What does Beta mean?**
- ✅ All major features are implemented
- ✅ Core functionality is working
- ⚠️ Some features may have bugs
- ⚠️ Performance optimizations ongoing
- ⚠️ Not recommended for critical production work yet

**Current Status:** Active Beta Testing  
**Expected Stable Release:** TBD based on testing feedback

---

## 🎯 What to Test

### Priority 1: Core Features
- [ ] **Code Editor**
  - Type Python and MEL code
  - Check syntax highlighting accuracy
  - Test autocomplete (Tab to accept)
  - Verify line numbers display correctly
  - Test undo/redo (Ctrl+Z, Ctrl+Y)

- [ ] **Error Detection**
  - Write code with intentional errors
  - Verify red underlines appear
  - Check if up to 10 errors are detected
  - Confirm Problems panel shows errors
  - Switch between tabs - errors should update

- [ ] **Multi-Tab Workflow**
  - Open multiple files
  - Create new tabs (Ctrl+N)
  - Switch between tabs
  - Close tabs
  - Verify problems panel updates per tab

### Priority 2: AI Features
- [ ] **Morpheus AI Chat**
  - Set up API key (Tools → Settings)
  - Open Morpheus chat
  - Ask questions about code
  - Verify auto-context (sees your code)
  - Test conversation history

- [ ] **Inline Diff (Keep Button)**
  - Ask Morpheus to fix code
  - Click "Keep" button
  - Verify inline diff appears
  - Check red (removed) and green (added) highlighting
  - Click "✓ Keep" to accept
  - Click "✗ Reject" to dismiss
  - Test with different code patterns

### Priority 3: UI/UX
- [ ] **Menus and Toolbars**
  - Test all menu items
  - Try keyboard shortcuts
  - Check toolbar buttons
  - Verify icons display correctly

- [ ] **Dock Widgets**
  - Open/close Console
  - Open/close Problems panel
  - Open/close Morpheus chat
  - Drag docks to different positions
  - Float/unfloat docks

- [ ] **Find/Replace**
  - Open Find/Replace (Ctrl+F)
  - Search for text
  - Replace text
  - Test "Replace All"
  - Test case sensitivity

### Priority 4: Performance
- [ ] **Typing Performance**
  - Type continuously
  - Check for lag or delays
  - Test with large files (>1000 lines)
  - Monitor CPU usage

- [ ] **Syntax Highlighting**
  - Verify highlighting is smooth
  - Check triple-quoted strings
  - Test f-strings
  - Verify comments highlight correctly

---

## 🐛 Known Issues

### Currently Being Tracked:
1. Inline diff positioning may be off on some screen sizes
2. Large files (>5000 lines) may have slight performance impact
3. MEL autocomplete is basic (limited keywords)

### Already Fixed:
✅ Multi-tab error tracking  
✅ False positive error detection  
✅ Triple-quote string highlighting  
✅ Autocomplete Enter key behavior  

---

## 📝 How to Report Issues

### GitHub Issues (Preferred)
1. Go to: https://github.com/mayjackass/AI_Maya_ScriptEditor/issues
2. Click "New Issue"
3. Title: Brief description (e.g., "Inline diff not appearing")
4. Include:
   ```
   **Description:** What happened?
   **Expected:** What should have happened?
   **Steps to Reproduce:**
   1. First do this...
   2. Then do this...
   3. Bug occurs...
   
   **Environment:**
   - OS: Windows 10/11 / macOS / Linux
   - Python: 3.9.13
   - Maya: 2022/2023/2024
   - NEO Script Editor: v3.0 Beta
   
   **Screenshots:** (if applicable)
   ```

### Critical Bugs
If you encounter:
- Data loss
- Crashes
- Security issues

Please report immediately with "CRITICAL" in the title.

---

## 💡 Feedback Areas

### What We Need Feedback On:

1. **Morpheus AI Integration**
   - Is auto-context helpful?
   - Are responses accurate?
   - Is the chat interface intuitive?
   - Suggestions for improvements?

2. **Inline Diff Preview**
   - Is it easy to understand?
   - Does it work as expected?
   - Visual clarity of red/green highlighting?
   - Button placement and labels clear?

3. **Error Detection**
   - False positives?
   - Missing errors that should be caught?
   - Error messages clear?
   - Problems panel useful?

4. **Overall UX**
   - Is the interface intuitive?
   - Are features easy to find?
   - Keyboard shortcuts logical?
   - Dark theme comfortable?

5. **Performance**
   - Any lag or delays?
   - Memory usage concerns?
   - Startup time acceptable?

---

## ✅ Testing Checklist

### Basic Workflow Test
```
□ Launch NEO Script Editor
□ Create new Python file
□ Write simple function
□ Introduce syntax error
□ Check error appears in Problems panel
□ Fix error
□ Save file
□ Open Morpheus chat
□ Ask Morpheus about the code
□ Click "Keep" on suggestion
□ Review inline diff
□ Accept changes
□ Run code in Maya (if testing with Maya)
□ Close editor
```

### Advanced Workflow Test
```
□ Open multiple files (5+)
□ Switch between tabs rapidly
□ Check Problems panel updates correctly
□ Test Find/Replace across tabs
□ Ask Morpheus complex question
□ Test inline diff with large code blocks
□ Check undo/redo with Morpheus changes
□ Test autocomplete with different code patterns
□ Monitor performance with all docks open
```

---

## 🎁 Tester Credits

All beta testers who provide valuable feedback will be:
- Credited in the final release notes
- Given early access to future updates
- Invited to provide input on future features

---

## 📊 Testing Progress

We're looking for feedback in these areas:

| Feature | Testing Status | Issues Found |
|---------|---------------|--------------|
| Code Editor | 🟡 Testing | 0 |
| Error Detection | 🟡 Testing | 0 |
| Morpheus AI | 🟡 Testing | 0 |
| Inline Diff | 🟡 Testing | 0 |
| Multi-Tab | 🟡 Testing | 0 |
| Performance | 🟡 Testing | 0 |

Legend:
- 🔴 Not Started
- 🟡 Testing
- 🟢 Completed

---

## 💬 Communication

### Where to Discuss:
- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and feedback
- **README:** Check for updates and documentation

### Response Time:
We aim to respond to:
- Critical bugs: Within 24 hours
- Major issues: Within 48 hours
- Minor issues/feedback: Within 1 week

---

## 🚀 Post-Beta Plans

After successful beta testing:
1. Fix all critical and major bugs
2. Implement highly requested features
3. Performance optimization pass
4. Documentation updates
5. **Stable v3.0 Release**

---

## 🙏 Thank You!

Your time and feedback are invaluable. Together, we're building the best AI-powered Maya script editor!

**Questions?** Open a GitHub Discussion  
**Found a bug?** Open a GitHub Issue  
**Want to contribute?** Check CONTRIBUTING.md (coming soon)

---

**NEO Script Editor v3.0 Beta**  
Developed by Mayj Amilano (@mayjackass)  
October 13, 2025
