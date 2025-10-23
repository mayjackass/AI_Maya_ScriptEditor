"""
Dialog Styles
Centralized styling for all dialogs to maintain consistent theme
"""
import os
from qt_compat import QtGui

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
    from qt_compat import QtWidgets
    
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


def show_about_dialog(parent=None):
    """
    Show the standard NEO About dialog that can be used by both installer and main UI
    
    Args:
        parent: Parent widget (can be None for standalone use)
    """
    from qt_compat import QtWidgets, QtCore, QtGui
    
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle("About NEO Script Editor")
    dialog.setMinimumSize(550, 600)
    dialog.setMaximumSize(550, 600)
    
    # Apply consistent dark theme
    apply_dark_theme(dialog)
    
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setSpacing(10)
    layout.setContentsMargins(25, 20, 25, 20)
    
    # Logo/Title Section
    titleLayout = QtWidgets.QVBoxLayout()
    titleLayout.setSpacing(4)
    
    # Create horizontal layout for icon + title
    iconTitleLayout = QtWidgets.QHBoxLayout()
    iconTitleLayout.setAlignment(QtCore.Qt.AlignCenter)
    iconTitleLayout.setSpacing(10)
    
    # Add Matrix icon to the left
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "matrix.png")
    if os.path.exists(icon_path):
        iconLabel = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(icon_path)
        # Scale the icon smaller (36x36)
        scaled_pixmap = pixmap.scaled(36, 36, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        iconLabel.setPixmap(scaled_pixmap)
        iconLabel.setAlignment(QtCore.Qt.AlignVCenter)
        iconTitleLayout.addWidget(iconLabel)
    
    # Title
    titleLabel = QtWidgets.QLabel("NEO Script Editor")
    titleLabel.setStyleSheet("""
        font-size: 22px;
        font-weight: 600;
        color: #cccccc;
        letter-spacing: 0.5px;
    """)
    titleLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
    iconTitleLayout.addWidget(titleLabel)
    
    # Add the horizontal layout to the main title layout
    titleLayout.addLayout(iconTitleLayout)
    
    # Version and tagline
    versionLabel = QtWidgets.QLabel("Version 3.2 Beta • Beta Testing Release")
    versionLabel.setStyleSheet("""
        font-size: 11px;
        color: #888888;
        font-weight: 400;
    """)
    versionLabel.setAlignment(QtCore.Qt.AlignCenter)
    
    # Quote
    quoteLabel = QtWidgets.QLabel('"I can only show you the door. You\'re the one that has to walk through it."')
    quoteLabel.setStyleSheet("""
        font-size: 12px;
        color: #999999;
        font-style: italic;
        margin: 10px 0;
    """)
    quoteLabel.setAlignment(QtCore.Qt.AlignCenter)
    quoteLabel.setWordWrap(True)
    
    titleLayout.addWidget(versionLabel)
    titleLayout.addWidget(quoteLabel)
    layout.addLayout(titleLayout)
    
    # Separator
    separator1 = QtWidgets.QFrame()
    separator1.setFrameShape(QtWidgets.QFrame.HLine)
    separator1.setStyleSheet("background: #444444; max-height: 1px;")
    layout.addWidget(separator1)
    
    # Author Section - compressed
    authorLayout = QtWidgets.QVBoxLayout()
    authorLayout.setSpacing(2)
    
    authorLabel = QtWidgets.QLabel("Developed by Mayj Amilano (@mayjackass)")
    authorLabel.setStyleSheet("""
        font-size: 10px;
        color: #777777;
        font-weight: 400;
    """)
    authorLabel.setAlignment(QtCore.Qt.AlignCenter)
    
    # Website link
    githubLabel = QtWidgets.QLabel('<a href="https://mayjamilano.com/digital/neo-script-editor-ai-powered-script-editor-for-maya-tsuyr">NEO Script Editor Website</a>')
    githubLabel.setStyleSheet("""
        font-size: 10px;
        color: #777777;
        font-weight: 400;
    """)
    githubLabel.setAlignment(QtCore.Qt.AlignCenter)
    githubLabel.setOpenExternalLinks(True)
    
    authorLayout.addWidget(authorLabel)
    authorLayout.addWidget(githubLabel)
    layout.addLayout(authorLayout)
    
    # Separator
    separator2 = QtWidgets.QFrame()
    separator2.setFrameShape(QtWidgets.QFrame.HLine)
    separator2.setStyleSheet("background: #444444; max-height: 1px;")
    layout.addWidget(separator2)
    
    # Features Section
    featuresLabel = QtWidgets.QLabel("KEY FEATURES")
    featuresLabel.setStyleSheet("""
        font-size: 10px;
        color: #888888;
        font-weight: 500;
        letter-spacing: 1px;
        margin-bottom: 8px;
    """)
    layout.addWidget(featuresLabel)
    
    # Features list
    featuresBrowser = QtWidgets.QTextBrowser()
    featuresBrowser.setMinimumHeight(280)
    featuresBrowser.setMaximumHeight(320)
    featuresBrowser.setOpenExternalLinks(False)
    
    featuresBrowser.setHtml("""
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background: #1e1e1e; 
                margin: 0; 
                padding: 8px 12px; 
                color: #cccccc;
            }
            .feature { 
                margin-bottom: 10px; 
                line-height: 1.5; 
            }
            .feature-title { 
                color: #bbbbbb; 
                font-weight: 500; 
                font-size: 12px;
                display: block;
                margin-bottom: 2px;
            }
            .text { 
                color: #999999; 
                font-size: 11px;
                display: block;
            }
        </style>
        <div class="feature">
            <span class="feature-title">Maya Command Validation</span>
            <span class="text">320+ commands validated with smart typo detection</span>
        </div>
        <div class="feature">
            <span class="feature-title">Morpheus AI Assistant</span>
            <span class="text">Integrated AI with OpenAI & Claude</span>
        </div>
        <div class="feature">
            <span class="feature-title">VSCode-Style Editor</span>
            <span class="text">Advanced syntax highlighting and autocomplete</span>
        </div>
        <div class="feature">
            <span class="feature-title">Real-Time Analysis</span>
            <span class="text">12 validation checks with instant error detection</span>
        </div>
        <div class="feature">
            <span class="feature-title">Smart Suggestions</span>
            <span class="text">Typo correction and import detection</span>
        </div>
        <div class="feature">
            <span class="feature-title">Maya Documentation</span>
            <span class="text">270+ command tooltips with complete API coverage</span>
        </div>
        <div class="feature">
            <span class="feature-title">Problems Panel</span>
            <span class="text">Maya-aware error tracking with fix suggestions</span>
        </div>
        <div class="feature">
            <span class="feature-title">Modern UI</span>
            <span class="text">Dark theme with customizable interface</span>
        </div>
    """)
    layout.addWidget(featuresBrowser)
    
    # Separator
    separator3 = QtWidgets.QFrame()
    separator3.setFrameShape(QtWidgets.QFrame.HLine)
    separator3.setStyleSheet("background: #444444; max-height: 1px;")
    layout.addWidget(separator3)
    
    # Tech Stack & Release Info
    techLabel = QtWidgets.QLabel("BUILT WITH")
    techLabel.setStyleSheet("""
        font-size: 9px;
        color: #888888;
        font-weight: 500;
        letter-spacing: 1px;
    """)
    layout.addWidget(techLabel)
    
    techStackLabel = QtWidgets.QLabel("Python 3.9+ • PySide6 • OpenAI • Anthropic Claude")
    techStackLabel.setStyleSheet("""
        font-size: 11px;
        color: #777777;
        margin-bottom: 8px;
    """)
    techStackLabel.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(techStackLabel)
    
    # Release info
    releaseLabel = QtWidgets.QLabel("Released: October 2025 • Beta Expires: January 31, 2026")
    releaseLabel.setStyleSheet("""
        font-size: 10px;
        color: #666666;
        margin-bottom: 12px;
    """)
    releaseLabel.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(releaseLabel)
    
    # Close button
    buttonLayout = QtWidgets.QHBoxLayout()
    buttonLayout.addStretch()
    
    closeBtn = QtWidgets.QPushButton("Close")
    closeBtn.clicked.connect(dialog.accept)
    closeBtn.setCursor(QtCore.Qt.PointingHandCursor)
    
    buttonLayout.addWidget(closeBtn)
    buttonLayout.addStretch()
    layout.addLayout(buttonLayout)
    
    # Show dialog
    dialog.exec()


def create_themed_dialog(parent, title, width=400, height=300):
    """
    Create a dialog with NEO theming applied
    
    Args:
        parent: Parent widget
        title: Dialog title
        width: Dialog width
        height: Dialog height
    
    Returns:
        QtWidgets.QDialog: Themed dialog
    """
    from qt_compat import QtWidgets
    
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumSize(width, height)
    apply_dark_theme(dialog)
    
    return dialog


