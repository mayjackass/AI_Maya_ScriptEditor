# Maya Version Compatibility Guide

## Supported Maya Versions

NEO Script Editor now supports **all modern Maya versions**:

### Maya 2022 - 2024 (PySide2 / Qt 5)
- ✅ **Fully supported**
- Uses PySide2 (Qt 5) which is built into Maya
- No additional Qt installation needed

### Maya 2025 - 2026+ (PySide6 / Qt 6)
- ✅ **Fully supported**  
- Uses PySide6 (Qt 6) which is built into Maya
- No additional Qt installation needed

## How It Works

NEO Script Editor uses a **Qt compatibility layer** (`qt_compat.py`) that automatically detects which Qt version is available and uses the appropriate one:

```python
# The app automatically detects and uses the right Qt version
from qt_compat import QtWidgets, QtCore, QtGui, QT_VERSION

# QT_VERSION will be either 2 (PySide2) or 6 (PySide6)
print(f"Using Qt version: {QT_VERSION}")
```

## Installation by Maya Version

### Maya 2025+
Maya 2025 and newer already include PySide6. No special installation needed:

```python
# In Maya Script Editor:
import sys
sys.path.insert(0, r"C:\path\to\ai_script_editor")
from main_window import AiScriptEditor
win = AiScriptEditor()
win.show()
```

### Maya 2022-2024
Maya 2022-2024 already include PySide2. No special installation needed:

```python
# In Maya Script Editor (same code works!):
import sys
sys.path.insert(0, r"C:\path\to\ai_script_editor")
from main_window import AiScriptEditor
win = AiScriptEditor()
win.show()
```

## What Changed in v3.2

### Before (v3.1 and earlier)
- Only supported Maya 2025+ (PySide6 only)
- Would crash in Maya 2022-2024 with import errors

### After (v3.2+)
- ✅ Supports ALL Maya versions (2022-2026+)
- ✅ Auto-detects PySide2 or PySide6
- ✅ Same code works in all versions
- ✅ No manual configuration needed

## Technical Details

### Qt Version Detection
The compatibility layer tries PySide6 first, then falls back to PySide2:

1. **Try PySide6**: For Maya 2025+
2. **Fall back to PySide2**: For Maya 2022-2024
3. **Report Error**: If neither is found

### API Compatibility
While PySide2 and PySide6 are mostly compatible, there are some differences:
- `app.exec()` vs `app.exec_()` - Handled by `qt_compat.app_exec()`
- `dialog.exec()` vs `dialog.exec_()` - Handled by `qt_compat.exec_dialog()`
- Enum access patterns - Handled by helper functions

All these differences are abstracted away - you don't need to worry about them!

## Troubleshooting

### "No Qt bindings found" Error
This shouldn't happen in Maya, but if it does:

**Maya 2025+:**
```bash
mayapy -m pip install PySide6
```

**Maya 2022-2024:**
```bash
mayapy -m pip install PySide2
```

### Wrong Qt Version Detected
The app will print which version it's using:
```
[Qt Compat] Using PySide2 (Qt 5) - Maya 2022-2024
```
or
```
[Qt Compat] Using PySide6 (Qt 6) - Maya 2025+
```

If this doesn't match your Maya version, check your Python environment.

## For Developers

### Adding New Features
When adding new Qt-dependent code, always use:

```python
from qt_compat import QtWidgets, QtCore, QtGui, QT_VERSION
```

Never directly import from PySide2 or PySide6!

### Checking Qt Version
If you need version-specific code:

```python
from qt_compat import QT_VERSION, is_pyside2, is_pyside6

if is_pyside6():
    # PySide6-specific code
    pass
elif is_pyside2():
    # PySide2-specific code
    pass
```

### Dialog Execution
Use the compatibility helper:

```python
from qt_compat import exec_dialog

dialog = QtWidgets.QDialog()
result = exec_dialog(dialog)  # Works in both Qt 5 and Qt 6
```

## Version Matrix

| Maya Version | Qt Version | PySide Module | NEO Support |
|--------------|------------|---------------|-------------|
| 2022         | Qt 5       | PySide2       | ✅ Yes      |
| 2023         | Qt 5       | PySide2       | ✅ Yes      |
| 2024         | Qt 5       | PySide2       | ✅ Yes      |
| 2025         | Qt 6       | PySide6       | ✅ Yes      |
| 2026+        | Qt 6       | PySide6       | ✅ Yes      |

## Summary

✅ **Universal Compatibility**: Works in all modern Maya versions (2022-2026+)  
✅ **Auto-Detection**: Automatically uses the correct Qt version  
✅ **Zero Configuration**: No manual setup or version selection needed  
✅ **Future-Proof**: Will work with future Maya versions  
✅ **Single Codebase**: Same code runs everywhere  

---

**Upgrade Notes:**
- If upgrading from v3.1 or earlier, no changes needed
- Your existing Maya scripts will continue to work
- The app will now work in older Maya versions too!
