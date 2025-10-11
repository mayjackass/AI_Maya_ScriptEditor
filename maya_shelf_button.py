"""
Maya Shelf Button Script for NEO Script Editor

To create a shelf button:
1. Open Maya
2. Go to your shelf
3. Right-click on empty space → "New Shelf Button"
4. In the "Command" tab, paste the code below (lines 18-23)
5. Give it a nice icon (optional)
6. Click "Save"

Or just copy the code below and run it from Maya's Script Editor
"""

# === PASTE THIS CODE IN MAYA SHELF BUTTON ===
import sys, os
neo_path = os.path.join(os.path.expanduser('~'), 'Documents', 'maya', 'scripts', 'ai_script_editor')
sys.path.insert(0, neo_path) if neo_path not in sys.path else None
from main_window import AiScriptEditor
window = AiScriptEditor()
window.show()
