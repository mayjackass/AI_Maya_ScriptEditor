# NEO Script Editor - Docking Guide

## Overview
NEO now supports **two modes** in Maya:
- **Floating Window** - Traditional standalone window (default, backwards compatible)
- **Docked Panel** - Integrated Maya workspace control (new feature)

## How to Use

### Method 1: Switch via Menu (Recommended)
1. Open NEO in Maya
2. Go to **View** menu
3. Choose:
   - **"Switch to Docked Mode"** - Dock NEO inside Maya's UI
   - **"Switch to Floating Mode"** - Use NEO as floating window

Your tabs/session will be saved and restored automatically!

### Method 2: Python Commands

```python
# Launch with your saved preference (docked or floating)
from scripts.maya.maya_workspace import launch_neo_with_preference
launch_neo_with_preference()

# Force docked mode
from scripts.maya.maya_workspace import launch_neo_docked
launch_neo_docked()

# Force floating mode
from scripts.maya.maya_workspace import launch_neo_floating
launch_neo_floating()

# Switch modes on the fly
from scripts.maya.maya_workspace import switch_to_docked, switch_to_floating
switch_to_docked()  # Save preference + relaunch as docked
switch_to_floating()  # Save preference + relaunch as floating
```

## Preferences
Your choice is automatically saved in `QSettings` and will persist:
- First launch: Floating mode (default)
- After switching: Your last choice is remembered

## Performance Notes

### Docked Mode Benefits:
✅ Better Maya integration
✅ No window management overhead
✅ Can't "lose" the window
✅ Multi-monitor friendly
✅ Persistent position across sessions

### Floating Mode Benefits:
✅ Can position anywhere (even on top of Maya)
✅ Traditional workflow
✅ Works with older Maya versions

## Technical Details

**Docked Mode Requirements:**
- Maya 2017+ (uses `workspaceControl` API)
- `MayaQWidgetDockableMixin` support

**Floating Mode:**
- Works with all Maya versions
- Uses Qt.Window with Maya parenting
- Stays above Maya, goes behind external apps

## Troubleshooting

**"Docked mode not available"**
- You may be on Maya 2016 or older
- Falls back to floating mode automatically

**"Min/Max buttons missing"**
- This was a floating mode issue, now fixed
- Try switching to docked mode for better controls

**"NEO disappeared"**
- In docked mode: Check Windows menu in Maya
- In floating mode: Relaunch from NEO shelf/menu

## Files Modified
- `scripts/maya/maya_workspace.py` - New workspace control wrapper
- `scripts/maya/complete_setup.py` - Auto-detect mode on launch
- `ui/menu_manager.py` - Added View menu options
- User preference saved in QSettings

---
**Version:** NEO v3.2 Beta
**Date:** October 2025
