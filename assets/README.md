# Assets Folder - Custom Icons

This folder contains custom icons for the AI Script Editor toolbar.

## Morpheus AI Icon

To add a custom Morpheus icon from The Matrix:

1. **Find an icon image:**
   - Search for "Morpheus Matrix icon" or "Morpheus sunglasses icon"
   - Look for images showing Morpheus with his iconic red/blue pill sunglasses
   - Recommended sites: 
     - iconarchive.com
     - flaticon.com
     - iconfinder.com
     - Or search Google Images for "morpheus matrix icon png"

2. **Download the icon:**
   - Save as **PNG** or **ICO** format
   - Recommended size: 32x32 or 48x48 pixels
   - Transparent background works best

3. **Save the file:**
   - Save it in this folder as: `morpheus.png`
   - Full path: `ai_script_editor/assets/morpheus.png`

4. **Restart the application:**
   - The icon will automatically load when you restart NEO Script Editor
   - If the file is not found, it will fall back to the 🤖 emoji

## Supported Formats
- PNG (recommended)
- ICO
- SVG
- JPG/JPEG

## Icon Requirements
- Size: 32x32 to 64x64 pixels recommended
- Transparent background preferred
- High contrast for dark theme

## Example Icon Names
Current icons that can be customized:
- `morpheus.png` - Morpheus AI Chat button

You can add more custom icons by editing `main_window.py` and using the `icon_file` parameter in `_create_action()`.
