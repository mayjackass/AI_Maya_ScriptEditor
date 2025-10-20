# Running NEO Script Editor in Maya

## Quick Start

### Method 1: Using userSetup.py (Automatic on Maya Startup)

1. **Create or edit your `userSetup.py` in Maya scripts folder:**
   ```
   Location: C:\Users\<YourUsername>\Documents\maya\scripts\userSetup.py
   ```
   
   **Copy and paste this code into your userSetup.py:**
   ```python
   """
   NEO Script Editor Auto-Setup for Maya
   """
   import sys
   import os

   def setup_neo_editor():
       """Setup NEO Script Editor for Maya"""
       # Add the ai_script_editor directory to Python path
       neo_path = os.path.join(os.path.dirname(__file__), 'ai_script_editor')
       
       if neo_path not in sys.path:
           sys.path.insert(0, neo_path)
           print("[NEO] Script Editor path added")
       
       # Create launcher function
       def launch_neo_editor():
           """Launch NEO Script Editor in Maya"""
           try:
               from main_window import AiScriptEditor
               window = AiScriptEditor()
               window.show()
               return window
           except Exception as e:
               print(f"[NEO] Launch failed: {e}")
               return None
       
       # Make it globally available in Maya
       import __main__
       __main__.launch_neo_editor = launch_neo_editor
       print("[NEO] Ready! Use: launch_neo_editor()")

   setup_neo_editor()
   ```

2. **Restart Maya**

3. **Launch from Maya Script Editor (Python tab):**
   ```python
   launch_neo_editor()
   ```

### Method 2: Manual Launch (Without userSetup)

Open Maya's Script Editor (Python tab) and run:

```python
import sys
import os

# Add NEO Script Editor to path
neo_path = r"C:\Users\Burn\Documents\maya\scripts\ai_script_editor"
if neo_path not in sys.path:
    sys.path.insert(0, neo_path)

# Launch
from launchers.launch import launch_neo_editor
launch_neo_editor()
```

### Method 3: Create a Shelf Button

1. Open Maya
2. Select your shelf (Custom or Scripts)
3. Right-click empty space → **New Shelf Button**
4. In the **Command** tab, paste:
   ```python
   launch_neo_editor()
   ```
5. **Optional:** Add icon, label, tooltip
6. Click **Save**

Now you can launch NEO Script Editor with one click!

## Features Available in Maya

All Features Work:
- VS Code-style syntax highlighting (Python & MEL)
- Real-time find/replace with highlighting
- AI chat with OpenAI or Claude
- Dockable panels (Explorer, Console, Problems, AI)
- Maya-specific MEL support
- Multi-tab editing
- Error detection

Maya Integration:
- Works with Maya's PySide2/PySide6
- Shares Maya's Qt application
- Can execute Maya commands
- Access Maya Python API (maya.cmds, maya.OpenMaya)

## Compatibility

- **Maya 2022+**: Uses PySide2
- **Maya 2024+**: Uses PySide6
- **Standalone**: Works outside Maya too!

## Tips

### Execute in Maya Context

Any code you write in NEO Script Editor can access Maya:

```python
import maya.cmds as cmds

# Create a sphere
cmds.polySphere(r=5)

# Get selection
sel = cmds.ls(selection=True)
print(f"Selected: {sel}")
```

### Use Maya Console Output

The Output Console shows:
- Maya command results
- Script output
- Error messages
- AI responses

### Keyboard Shortcuts in Maya

- `Ctrl+F` - Find
- `Ctrl+H` - Find & Replace
- `Ctrl+S` - Save
- `Ctrl+Shift+H` - Hide all panels
- `Ctrl+Shift+A` - Show all panels
- `Esc` - Close find widget

## Troubleshooting

### "Module not found" error

Make sure the path is correct:
```python
import os
neo_path = r"C:\Users\Burn\Documents\maya\scripts\ai_script_editor"
print(f"Path exists: {os.path.exists(neo_path)}")
```

### "No Qt bindings found"

Maya should have PySide2/PySide6 built-in. If not:
- Check Maya version (2022+)
- Verify Maya installation

### Window doesn't show

Try:
```python
window = launch_neo_editor()
if window:
    window.raise_()
    window.activateWindow()
```

## Best Practices

1. **Save your work**: Use `Ctrl+S` frequently
2. **Use tabs**: Organize multiple scripts
3. **Leverage AI**: Ask Morpheus for Maya-specific help
4. **Dock wisely**: Arrange panels to fit your workflow
5. **Hide panels**: Use `Ctrl+Shift+H` for more editing space

## Maya-Specific AI Prompts

Try asking Morpheus AI:

- "Create a Maya script to select all polygon objects"
- "How do I create a custom Maya shelf button?"
- "Write a MEL script to rename selected objects"
- "Explain Maya's node graph architecture"
- "Create a rigging script for a character arm"

The AI understands both Python and MEL for Maya!

---

**Enjoy coding in Maya with NEO Script Editor!**
