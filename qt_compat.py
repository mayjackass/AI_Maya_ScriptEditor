"""
Qt Compatibility Layer
Supports both PySide2 (Maya 2022-2024) and PySide6 (Maya 2025+)

This module provides a unified import interface that works across Qt versions.
"""
import sys

# Detect which Qt version is available
QT_VERSION = None
QtWidgets = None
QtCore = None
QtGui = None

# Try PySide6 first (Maya 2025+)
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    QT_VERSION = 6
    print("[Qt Compat] Using PySide6 (Qt 6) - Maya 2025+")
except ImportError:
    # Fall back to PySide2 (Maya 2022-2024)
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        QT_VERSION = 2
        print("[Qt Compat] Using PySide2 (Qt 5) - Maya 2022-2024")
    except ImportError:
        print("[Qt Compat] ERROR: Neither PySide6 nor PySide2 found!")
        print("[Qt Compat] Install with: mayapy -m pip install PySide2")
        raise ImportError("No Qt bindings found. Install PySide2 or PySide6.")

# Export the detected version
__all__ = ['QtWidgets', 'QtCore', 'QtGui', 'QT_VERSION']


def get_qt_version():
    """Returns the Qt major version (2 or 6)"""
    return QT_VERSION


def is_pyside6():
    """Returns True if using PySide6"""
    return QT_VERSION == 6


def is_pyside2():
    """Returns True if using PySide2"""
    return QT_VERSION == 2


# Qt 5 vs Qt 6 API compatibility helpers
if QT_VERSION == 6:
    # PySide6 uses different enum access
    def get_alignment_flag(alignment):
        """Get alignment flag compatible with Qt version"""
        return alignment
    
    def get_text_interaction_flags():
        """Get text interaction flags"""
        return QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
    
    def get_orientation(orientation):
        """Get orientation flag"""
        return orientation
        
else:
    # PySide2 enum access
    def get_alignment_flag(alignment):
        """Get alignment flag compatible with Qt version"""
        return alignment
    
    def get_text_interaction_flags():
        """Get text interaction flags"""
        return QtCore.Qt.TextSelectableByMouse
    
    def get_orientation(orientation):
        """Get orientation flag"""
        return orientation


# QSettings compatibility
if QT_VERSION == 6:
    # PySide6
    QSettings = QtCore.QSettings
else:
    # PySide2
    QSettings = QtCore.QSettings


# Exec compatibility (exec_ in PySide6, exec in PySide2)
if hasattr(QtWidgets.QApplication, 'exec'):
    app_exec = lambda app: app.exec()
elif hasattr(QtWidgets.QApplication, 'exec_'):
    app_exec = lambda app: app.exec_()
else:
    raise AttributeError("Cannot find exec method on QApplication")


def exec_dialog(dialog):
    """Execute a dialog with proper Qt version compatibility"""
    if hasattr(dialog, 'exec'):
        return dialog.exec()
    elif hasattr(dialog, 'exec_'):
        return dialog.exec_()
    else:
        raise AttributeError(f"Cannot find exec method on {type(dialog).__name__}")


print(f"[Qt Compat] Successfully loaded Qt {QT_VERSION} bindings")
print(f"[Qt Compat] QtCore: {QtCore.__name__}")
print(f"[Qt Compat] QtWidgets: {QtWidgets.__name__}")
print(f"[Qt Compat] QtGui: {QtGui.__name__}")
