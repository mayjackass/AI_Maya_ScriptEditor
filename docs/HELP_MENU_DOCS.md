# Help Menu - Documentation Links

**Date:** January 15, 2025  
**Feature:** Added Python and MEL documentation links to Help menu

## What Was Added

### Help Menu Structure
```
Help
├── Beta Information
├── ──────────────────
├── 📚 Documentation
│   ├── Python Documentation
│   ├── MEL Documentation
│   ├── ──────────────
│   └── Maya Python API
├── ──────────────────
├── Documentation (NEO Editor)
├── GitHub Repository
├── ──────────────────
└── About
```

## Documentation Links

### 1. Python Documentation
**URL:** https://docs.python.org/3/  
**Description:** Official Python 3 documentation  
**Covers:**
- Python language reference
- Standard library
- Built-in functions
- Tutorials and guides

### 2. MEL Documentation
**URL:** https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=__CommandsPython_index_html  
**Description:** Maya MEL command reference  
**Covers:**
- MEL commands (cmds module)
- MEL syntax
- Command flags and options
- Maya-specific scripting

**Fallback URL:** https://help.autodesk.com/cloudhelp/2024/ENU/Maya-Tech-Docs/Commands/

### 3. Maya Python API
**URL:** https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=Maya_SDK_py_ref_index_html  
**Description:** Maya Python API documentation  
**Covers:**
- OpenMaya API
- Maya Python modules
- API classes and methods
- Advanced Maya scripting

## Usage

### From Menu Bar
1. Click **Help** menu
2. Hover over **📚 Documentation** submenu
3. Select the documentation you need:
   - **Python Documentation** - General Python help
   - **MEL Documentation** - Maya MEL commands
   - **Maya Python API** - Advanced Maya API

### Keyboard Shortcuts
Currently no shortcuts assigned (menu access only)

## Implementation Details

### Code Location
**File:** `ui/menu_manager.py`

**Methods Added:**
```python
def _open_python_docs(self):
    """Open Python official documentation"""
    import webbrowser
    webbrowser.open("https://docs.python.org/3/")

def _open_mel_docs(self):
    """Open Maya MEL command reference"""
    import webbrowser
    webbrowser.open("https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=__CommandsPython_index_html")

def _open_maya_python_docs(self):
    """Open Maya Python API documentation"""
    import webbrowser
    webbrowser.open("https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=Maya_SDK_py_ref_index_html")
```

### Menu Setup
**Location:** `setup_menus()` method  
**Menu Type:** QAction with submenu  
**Icon:** 📚 (book emoji for visual clarity)

## User Benefits

### Quick Access to Help
- No need to search for documentation URLs
- One-click access from within the editor
- Always opens the most current documentation

### Learning Aid
- Students learning Python can quickly reference docs
- Maya artists can look up MEL commands
- Technical artists can explore Maya API

### Workflow Integration
- Stay in the editor while learning
- Quick reference during coding
- Seamless documentation lookup

## Version Compatibility

### Python Documentation
- Links to Python 3 docs (current Python 3.x)
- Compatible with Python 3.9+ (Maya 2022+)

### Maya Documentation
- Links to Maya 2024 documentation
- Works for Maya 2022-2025 (minor differences only)
- Commands are mostly backwards compatible

## Future Enhancements

### Possible Additions
🔲 Add context-sensitive help (right-click on code)  
🔲 Add PySide6/Qt documentation link  
🔲 Add keyboard shortcuts for quick access  
🔲 Add "Search Documentation" feature  
🔲 Add local documentation fallback (for offline use)  
🔲 Add version-specific Maya docs (detect Maya version)

### Smart Features
🔲 Detect word under cursor and open relevant docs  
🔲 Show documentation tooltips inline (already done for hover)  
🔲 Add documentation search in-app  
🔲 Cache commonly accessed docs

## Testing

### Manual Testing Checklist
✅ Help menu appears in menu bar  
✅ Documentation submenu expands  
✅ Python docs link opens browser  
✅ MEL docs link opens browser  
✅ Maya Python API link opens browser  
✅ All links point to correct URLs  
✅ No errors in console  

### Browser Compatibility
✅ Windows default browser  
✅ Chrome, Firefox, Edge  
✅ Maya internal browser (if applicable)

## Known Issues

### None Currently
All documentation links working as expected.

### Potential Issues
⚠️ **Offline Access:** Links require internet connection  
**Solution:** Consider adding local documentation fallback in future

⚠️ **Maya Version:** Links point to Maya 2024 docs  
**Solution:** Most commands work in 2022-2025, consider auto-detection in future

## Related Features

### Existing Documentation Features
1. **Hover Tooltips** - Shows docs when hovering over code
2. **About Dialog** - Shows NEO Editor information
3. **GitHub Repository** - Links to project source

### Complementary Features
- Output console (for testing commands)
- Morpheus AI chat (for code help)
- Syntax highlighting (visual code understanding)

## Changelog

| Date | Change | Version |
|------|--------|---------|
| 2025-01-15 | Added Python/MEL/Maya API doc links | 3.0-beta |
| 2025-01-15 | Created documentation submenu | 3.0-beta |
| 2025-01-15 | Added tooltips to menu items | 3.0-beta |

---

**Status:** ✅ Complete and tested  
**User Impact:** Improved learning and productivity  
**Documentation:** Complete
