# NEO Script Editor - Maya Dockable Integration

## 🎯 New Feature: Dockable Maya Integration

The NEO Script Editor can now be integrated into Maya's UI just like the built-in Script Editor! This allows you to have the editor docked at the top of your Maya interface while viewing script results in the viewport below.

## 🚀 Quick Setup

### Step 1: Install Enhanced userSetup.py

1. **Copy the enhanced userSetup file:**
   ```
   Copy: userSetup_enhanced.py
   To: C:\Users\<YourUsername>\Documents\maya\scripts\userSetup.py
   ```

2. **Restart Maya**

### Step 2: Launch Dockable NEO Script Editor

In Maya's Script Editor (Python tab), run:
```python
neo_docked()
```

Or use the full command:
```python
launch_neo_docked()
```

## 🎨 Usage Modes

### Dockable Version (NEW! 🆕)
- **Command:** `neo_docked()` or `launch_neo_docked()`
- **Features:**
  - Integrates into Maya's workspace like the built-in Script Editor
  - Can be docked anywhere in Maya's interface
  - Can be tabbed with other panels (Outliner, Channel Box, etc.)
  - Perfect for having editor on top with viewport below
  - Remembers position and size

### Standalone Version (Original)
- **Command:** `launch_neo_editor()`
- **Features:**
  - Separate floating window
  - Independent of Maya's interface
  - Good for multi-monitor setups

## 🛠️ Available Commands

```python
# Launch dockable version (recommended)
neo_docked()                # Short alias
launch_neo_docked()         # Full command

# Control dockable version
hide_neo_docked()           # Hide the docked editor
delete_neo_docked()         # Remove it completely

# Launch standalone version
launch_neo_editor()         # Original floating window
```

## 📌 Creating a Shelf Button

1. **Right-click on your Maya shelf** → "New Shelf Button"
2. **In the Command tab, paste:**
   ```python
   neo_docked()
   ```
3. **Optional:** Add icon, label, and tooltip
4. **Click Save**

Now you can launch the dockable NEO Script Editor with one click!

## 🎯 Recommended Workflow

1. **Launch dockable NEO Script Editor:** `neo_docked()`
2. **Dock it at the top** of Maya's interface (drag and drop)
3. **Write Python/MEL scripts** in the top panel
4. **See results in the viewport** below
5. **Use AI assistance** for code help and debugging

This setup mimics the traditional Maya Script Editor workflow but with all the enhanced features of NEO Script Editor:
- VS Code-style syntax highlighting
- AI-powered assistance
- Real-time error detection
- Advanced find/replace
- File explorer and project management

## 🔧 Technical Details

### Maya Workspace Control
The dockable version uses Maya's `workspaceControl` system, which is the same technology used by:
- Maya's Script Editor
- Outliner
- Channel Box
- Node Editor
- And other dockable panels

### Benefits of Workspace Control
- **Native Maya integration:** Behaves exactly like built-in Maya panels
- **Persistent docking:** Remembers where you docked it
- **Tabbing support:** Can be tabbed with other panels
- **Responsive resize:** Automatically adjusts to Maya's interface changes
- **Workspace layouts:** Saved with Maya's workspace layouts

## 🐛 Troubleshooting

### "Command not found" error
- Make sure `userSetup_enhanced.py` is in `Documents/maya/scripts/userSetup.py`
- Restart Maya to reload userSetup.py
- Check Maya's Script Editor for error messages

### Panel doesn't dock properly
- Try deleting and recreating: `delete_neo_docked()` then `neo_docked()`
- Check that Maya's workspace is not locked
- Try docking to different areas of the interface

### Performance issues
- Close unused tabs in the NEO Script Editor
- Use the standalone version for very large files
- Make sure your OpenAI API key is set up correctly

## 💡 Pro Tips

1. **Editor on top, viewport below:** Dock NEO Script Editor at the top for the perfect scripting workflow
2. **Tab with Script Editor:** You can tab NEO with Maya's built-in Script Editor for quick switching
3. **Use both versions:** Keep dockable for main work, standalone for secondary tasks
4. **Keyboard shortcuts:** All NEO Script Editor shortcuts work in docked mode
5. **Save workspace:** Maya will remember your docking setup in workspace layouts

## 🔄 Migration from Standalone

If you were using the standalone version:
1. Your settings and preferences are preserved
2. File history and recent files carry over
3. AI chat history is maintained
4. Just switch to using `neo_docked()` instead of `launch_neo_editor()`

The dockable version provides the same functionality with better Maya integration!