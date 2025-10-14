"""
Dialog Styles
Centralized styling for all dialogs to maintain consistent theme
"""
import os
from PySide6 import QtGui

# Dark theme matching the AI Provider Settings dialog
DARK_DIALOG_STYLE = """
    QDialog {
        background: #0d1117;
        color: #f0f6fc;
    }
    QGroupBox {
        color: #f0f6fc;
        border: 1px solid #30363d;
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 8px;
        font-weight: 600;
    }
    QGroupBox::title {
        color: #00ff41;
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    QLabel {
        color: #8b949e;
    }
    QLabel a {
        color: #00ff41;
    }
    QLineEdit {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 6px;
        color: #f0f6fc;
    }
    QLineEdit:focus {
        border: 1px solid #00ff41;
    }
    QComboBox {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 6px;
        color: #f0f6fc;
    }
    QComboBox:hover {
        border-color: #00ff41;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView {
        background: #21262d;
        border: 1px solid #30363d;
        selection-background-color: transparent;
        color: #f0f6fc;
        outline: none;
    }
    QComboBox QAbstractItemView::item {
        padding: 4px 8px;
        min-height: 20px;
        border-left: 3px solid transparent;
    }
    QComboBox QAbstractItemView::item:selected {
        border-left: 3px solid #00ff41;
        background: transparent;
    }
    QTextEdit, QPlainTextEdit {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #f0f6fc;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        padding: 8px;
    }
    QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #00ff41;
    }
    QTextBrowser {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #f0f6fc;
        padding: 12px;
    }
    QTextBrowser:focus {
        border: 1px solid #00ff41;
    }
    QTreeWidget {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #f0f6fc;
        alternate-background-color: #1c2128;
        selection-background-color: #238636;
        outline: none;
    }
    QTreeWidget::item {
        padding: 4px;
    }
    QTreeWidget::item:hover {
        background: #21262d;
    }
    QTreeWidget::item:selected {
        background: #238636;
        color: #ffffff;
    }
    QHeaderView::section {
        background: #21262d;
        color: #f0f6fc;
        padding: 6px;
        border: none;
        border-bottom: 1px solid #30363d;
        border-right: 1px solid #30363d;
        font-weight: 600;
    }
    QPushButton {
        background: #00cc33;
        border: 1px solid #00ff41;
        color: #000000;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        min-width: 80px;
    }
    QPushButton:hover {
        background: #00ff41;
    }
    QPushButton:pressed {
        background: #00aa2b;
    }
    QPushButton:disabled {
        background: #30363d;
        border: 1px solid #484f58;
        color: #6e7681;
    }
    QPushButton#cancelBtn, QPushButton[text="Cancel"], QPushButton[text="Close"] {
        background: #21262d;
        border: 1px solid #30363d;
        color: #f0f6fc;
    }
    QPushButton#cancelBtn:hover, QPushButton[text="Cancel"]:hover, QPushButton[text="Close"]:hover {
        background: #30363d;
    }
    QPushButton#stopBtn, QPushButton[text*="Stop"] {
        background: #da3633;
        border: 1px solid #f85149;
        color: #ffffff;
    }
    QPushButton#stopBtn:hover, QPushButton[text*="Stop"]:hover {
        background: #f85149;
    }
    QScrollBar:vertical {
        background: #0d1117;
        border: 1px solid #30363d;
        width: 12px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background: #484f58;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #00ff41;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        background: none;
        border: none;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }
    QScrollBar:horizontal {
        background: #0d1117;
        border: 1px solid #30363d;
        height: 12px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background: #484f58;
        border-radius: 5px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #00ff41;
    }
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        background: none;
        border: none;
    }
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: none;
    }
    QSplitter::handle {
        background: #30363d;
    }
    QSplitter::handle:hover {
        background: #00ff41;
    }
"""


def apply_dark_theme(dialog):
    """
    Apply consistent dark theme to a dialog and set the Matrix icon
    
    Args:
        dialog: QDialog instance to style
    """
    # Apply stylesheet
    dialog.setStyleSheet(DARK_DIALOG_STYLE)
    
    # Set window icon
    try:
        # Get path to matrix.png icon
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        icon_path = os.path.join(assets_dir, "matrix.png")
        
        if os.path.exists(icon_path):
            icon = QtGui.QIcon(icon_path)
            dialog.setWindowIcon(icon)
    except Exception as e:
        # Silently fail if icon can't be loaded
        print(f"[Dialog] Could not load icon: {e}")


def get_app_icon():
    """
    Get the application icon for use in message boxes and dialogs
    
    Returns:
        QtGui.QIcon: The Matrix icon, or empty icon if not found
    """
    try:
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        icon_path = os.path.join(assets_dir, "matrix.png")
        
        if os.path.exists(icon_path):
            return QtGui.QIcon(icon_path)
    except Exception as e:
        print(f"[Dialog] Could not load icon: {e}")
    
    return QtGui.QIcon()  # Return empty icon as fallback


def create_message_box(parent, title, message, icon_type="information"):
    """
    Create a QMessageBox with the application icon
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Message text
        icon_type: Type of message box ("information", "warning", "critical", "question")
    
    Returns:
        QtWidgets.QMessageBox: Configured message box
    """
    from PySide6 import QtWidgets
    
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    # Set icon type
    icon_map = {
        "information": QtWidgets.QMessageBox.Information,
        "warning": QtWidgets.QMessageBox.Warning,
        "critical": QtWidgets.QMessageBox.Critical,
        "question": QtWidgets.QMessageBox.Question
    }
    msg_box.setIcon(icon_map.get(icon_type, QtWidgets.QMessageBox.Information))
    
    # Set window icon
    msg_box.setWindowIcon(get_app_icon())
    
    return msg_box


