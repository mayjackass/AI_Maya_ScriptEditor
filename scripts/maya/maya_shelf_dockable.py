"""
Maya Shelf Button for Dockable NEO Script Editor
================================================

SHELF BUTTON CODE (Copy this for your Maya shelf button):
---------------------------------------------------------
neo_docked()


SETUP INSTRUCTIONS:
==================

1. Make sure you have the enhanced userSetup.py installed:
   - Copy userSetup_enhanced.py to: Documents/maya/scripts/userSetup.py
   - Restart Maya

2. Create shelf button:
   - Right-click on your shelf → "New Shelf Button"
   - In the "Command" tab, paste: neo_docked()
   - Optionally add icon and tooltip
   - Click Save

3. Click the button to launch dockable NEO Script Editor!

The dockable version allows you to:
- Dock the editor anywhere in Maya's interface
- Tab it with other panels (like Outliner, Script Editor)
- Resize and arrange it however you want
- Have the editor on top with viewport below (perfect workflow!)

ALTERNATIVE COMMANDS:
====================
launch_neo_docked()    # Full command name
hide_neo_docked()      # Hide the docked editor
delete_neo_docked()    # Remove it completely
launch_neo_editor()    # Original standalone window version

TROUBLESHOOTING:
===============
If the shelf button doesn't work:
1. Check Maya Script Editor for error messages
2. Make sure userSetup_enhanced.py is in the right location
3. Restart Maya to reload userSetup.py
4. Try running the command manually first: neo_docked()
"""

# The actual shelf button command is just:
# neo_docked()

print("📋 Shelf button code: neo_docked()")
print("📖 See comments above for full setup instructions")