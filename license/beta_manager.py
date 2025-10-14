"""
Beta Manager - Time-Limited Beta System
Handles expiration checking, warnings, and upgrade prompts
"""
import os
from datetime import datetime, timedelta
from PySide6 import QtWidgets, QtCore, QtGui
from .license_core import get_license, is_dev_mode


class BetaManager:
    """Manages beta expiration and licensing for NEO Script Editor"""
    
    # Development Mode - now requires both flag AND key
    DEV_MODE = is_dev_mode()
    
    # Version Configuration
    BASE_VERSION = "3.0"
    DEV_ITERATION = os.environ.get('NEO_DEV_ITERATION', '1')
    
    # Beta Configuration
    VERSION = f"{BASE_VERSION}-beta" if not DEV_MODE else f"{BASE_VERSION}-dev.{DEV_ITERATION}"
    IS_BETA = True if not DEV_MODE else False
    
    # Warning thresholds
    WARNING_DAYS = 14  # Start showing warnings 2 weeks before expiry
    URGENT_DAYS = 7    # Urgent warnings 1 week before expiry
    
    def __init__(self):
        self.settings = QtCore.QSettings("NEO_Script_Editor", "license")
        self.license = get_license()
        
        # Get expiry from secure license core
        self.expiry_date = self.license.get_expiry_date()
        self.BETA_EXPIRY_DATE = self.license.get_expiry_string()
        
        # Auto-increment dev iteration if in dev mode
        if self.DEV_MODE:
            self._update_dev_iteration()
    
    def _update_dev_iteration(self):
        """Auto-increment dev iteration counter"""
        # Get last saved iteration
        last_iteration = self.settings.value("dev_iteration", 0, type=int)
        
        # Increment
        current_iteration = last_iteration + 1
        
        # Save new iteration
        self.settings.setValue("dev_iteration", current_iteration)
        
        # Update VERSION class variable dynamically
        BetaManager.DEV_ITERATION = str(current_iteration)
        BetaManager.VERSION = f"{self.BASE_VERSION}-dev.{current_iteration}"
        
        print(f"🔧 Dev Mode Iteration: {current_iteration}")
    
    def get_dev_iteration(self):
        """Get current dev iteration number"""
        if not self.DEV_MODE:
            return None
        return self.settings.value("dev_iteration", 0, type=int)
    
    def reset_dev_iteration(self):
        """Reset dev iteration counter (useful for fresh start)"""
        if self.DEV_MODE:
            self.settings.setValue("dev_iteration", 0)
            print("🔄 Dev iteration reset to 0")

        
        # Auto-increment dev iteration if in dev mode
        if self.DEV_MODE:
            self._update_dev_iteration()
    
    def is_expired(self):
        """Check if beta has expired"""
        if not self.IS_BETA:
            return False
        
        # Use secure license validation
        if not self.license.validate():
            return True  # Treat validation failure as expired
        
        return self.license.is_expired()
    
    def days_remaining(self):
        """Get number of days remaining in beta"""
        if not self.IS_BETA:
            return None
        return self.license.days_remaining()
    
    def should_show_warning(self):
        """Check if we should show expiration warning"""
        if not self.IS_BETA or self.is_expired():
            return False
        days = self.days_remaining()
        return days is not None and days <= self.WARNING_DAYS
    
    def get_warning_level(self):
        """Get warning urgency level: 'info', 'warning', 'urgent'"""
        if not self.IS_BETA or self.is_expired():
            return None
        days = self.days_remaining()
        if days <= self.URGENT_DAYS:
            return 'urgent'
        elif days <= self.WARNING_DAYS:
            return 'warning'
        return 'info'
    
    def get_title_suffix(self):
        """Get suffix to add to window title"""
        if self.DEV_MODE:
            return " - DEV MODE"
        if not self.IS_BETA:
            return ""
        if self.is_expired():
            return " - BETA EXPIRED"
        days = self.days_remaining()
        if days is not None and days <= self.URGENT_DAYS:
            return f" - BETA (Expires in {days} days!)"
        return " - BETA"
    
    def show_startup_notice(self, parent=None):
        """Show beta notice on startup if needed"""
        # Dev mode bypasses all checks
        if self.DEV_MODE:
            return True
        
        # Check if user dismissed notice today
        last_shown = self.settings.value("last_notice_date", "")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.is_expired():
            self._show_expired_dialog(parent)
            return False  # Block application
        
        elif self.should_show_warning() and last_shown != today:
            self._show_warning_dialog(parent)
            self.settings.setValue("last_notice_date", today)
        
        return True  # Allow application to continue
    
    def _show_expired_dialog(self, parent):
        """Show dialog when beta has expired"""
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Beta Period Expired")
        dialog.setMinimumWidth(500)
        
        # Apply Matrix theme
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #f0f6fc;
            }
            QLabel {
                color: #f0f6fc;
                font-size: 11pt;
            }
            QLabel#title {
                color: #00ff41;
                font-size: 16pt;
                font-weight: bold;
            }
            QLabel#expiry {
                color: #ff4136;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton {
                background-color: #00cc33;
                color: #000000;
                border: 2px solid #00ff41;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #00ff41;
            }
            QPushButton#closeBtn {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
            }
            QPushButton#closeBtn:hover {
                background-color: #3e3e42;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QtWidgets.QLabel("⏰ Beta Period Has Ended")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Expiry message
        expiry_msg = QtWidgets.QLabel(f"Expired: {self.BETA_EXPIRY_DATE}")
        expiry_msg.setObjectName("expiry")
        expiry_msg.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(expiry_msg)
        
        # Message
        message = QtWidgets.QLabel(
            "Thank you for testing <b>NEO Script Editor v3.0 Beta</b>!<br><br>"
            "The beta testing period has concluded. To continue using the full version, "
            "please purchase a license.<br><br>"
            "<b>Benefits of the Full Version:</b><br>"
            "✅ Unlimited access to Morpheus AI<br>"
            "✅ Advanced code intelligence features<br>"
            "✅ Priority support and updates<br>"
            "✅ Lifetime license (pay once, use forever)<br><br>"
        )
        message.setWordWrap(True)
        message.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(message)
        
        # Contact info
        contact = QtWidgets.QLabel(
            '📧 Contact: <a href="mailto:mayjackass@example.com" style="color: #00ff41;">mayjackass@example.com</a><br>'
            '🌐 Website: <a href="https://github.com/mayjackass/AI_Maya_ScriptEditor" style="color: #00ff41;">GitHub Repository</a>'
        )
        contact.setOpenExternalLinks(True)
        contact.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(contact)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        upgrade_btn = QtWidgets.QPushButton("Get Full Version")
        upgrade_btn.clicked.connect(lambda: self._open_purchase_page())
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(upgrade_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _show_warning_dialog(self, parent):
        """Show warning dialog when expiry is approaching"""
        days = self.days_remaining()
        level = self.get_warning_level()
        
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Beta Expiration Notice")
        dialog.setMinimumWidth(450)
        
        # Apply Matrix theme
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #f0f6fc;
            }
            QLabel {
                color: #f0f6fc;
                font-size: 11pt;
            }
            QLabel#title {
                color: #00ff41;
                font-size: 14pt;
                font-weight: bold;
            }
            QLabel#countdown {
                color: #ffa500;
                font-size: 18pt;
                font-weight: bold;
            }
            QPushButton {
                background-color: #00cc33;
                color: #000000;
                border: 2px solid #00ff41;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff41;
            }
            QPushButton#laterBtn {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
            }
            QPushButton#laterBtn:hover {
                background-color: #3e3e42;
            }
            QCheckBox {
                color: #8b949e;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #30363d;
                border-radius: 3px;
                background: #0d1117;
            }
            QCheckBox::indicator:checked {
                background: #00ff41;
                border-color: #00ff41;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        icon = "⚠️" if level == 'urgent' else "ℹ️"
        title = QtWidgets.QLabel(f"{icon} Beta Expiration Notice")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Countdown
        countdown = QtWidgets.QLabel(f"{days} days remaining")
        countdown.setObjectName("countdown")
        countdown.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(countdown)
        
        # Message
        message = QtWidgets.QLabel(
            f"Your beta access expires on <b>{self.BETA_EXPIRY_DATE}</b>.<br><br>"
            "Thank you for testing NEO Script Editor! Consider upgrading to the full version "
            "to continue enjoying all features without interruption."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Don't show again checkbox
        dont_show = QtWidgets.QCheckBox("Don't show this again today")
        layout.addWidget(dont_show)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        learn_more_btn = QtWidgets.QPushButton("Learn More")
        learn_more_btn.clicked.connect(lambda: self._open_purchase_page())
        
        later_btn = QtWidgets.QPushButton("Remind Me Later")
        later_btn.setObjectName("laterBtn")
        later_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(learn_more_btn)
        button_layout.addWidget(later_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _open_purchase_page(self):
        """Open purchase/contact page"""
        import webbrowser
        # Update this URL to your actual sales page
        webbrowser.open("https://github.com/mayjackass/AI_Maya_ScriptEditor")
    
    def show_about_beta(self, parent=None):
        """Show beta information in Help menu"""
        msg_box = QtWidgets.QMessageBox(parent)
        msg_box.setWindowTitle("Version Information")
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        
        # Set custom icon (suggestion.png)
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        icon_path = os.path.join(assets_dir, "suggestion.png")
        if os.path.exists(icon_path):
            icon_pixmap = QtGui.QPixmap(icon_path)
            msg_box.setIconPixmap(icon_pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        # Set window icon (matrix.png)
        matrix_icon_path = os.path.join(assets_dir, "matrix.png")
        if os.path.exists(matrix_icon_path):
            msg_box.setWindowIcon(QtGui.QIcon(matrix_icon_path))
        
        if self.DEV_MODE:
            iteration = self.get_dev_iteration()
            msg_box.setText(f"NEO Script Editor {self.VERSION}")
            msg_box.setInformativeText(
                "Development Mode: Active\n"
                f"Iteration: {iteration}\n\n"
                "All beta restrictions are bypassed.\n"
                "No expiration date.\n\n"
                "Version auto-increments with each launch.\n"
                "This is for development and testing purposes only."
            )
        elif self.is_expired():
            msg_box.setText("Beta Period Expired")
            msg_box.setInformativeText(
                f"This beta version expired on {self.BETA_EXPIRY_DATE}.\n\n"
                "Please contact mayjackass@example.com to upgrade to the full version."
            )
        else:
            days = self.days_remaining()
            msg_box.setText(f"NEO Script Editor {self.VERSION}")
            msg_box.setInformativeText(
                f"Beta Status: Active\n"
                f"Days Remaining: {days}\n"
                f"Expires: {self.BETA_EXPIRY_DATE}\n\n"
                "Thank you for testing! Please report any issues on GitHub."
            )
        
        # Apply Matrix theme
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #0d1117;
                color: #f0f6fc;
            }
            QLabel {
                color: #f0f6fc;
            }
            QPushButton {
                background-color: #00cc33;
                color: #000000;
                border: 2px solid #00ff41;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #00ff41;
            }
        """)
        
        msg_box.exec()
    
    def get_status_bar_message(self):
        """Get message to show in status bar"""
        if self.DEV_MODE:
            return "🔧 Development Mode - No Restrictions"
        if not self.IS_BETA:
            return ""
        if self.is_expired():
            return "⚠️ Beta expired - Please upgrade"
        days = self.days_remaining()
        if days is None:
            return ""
        if days <= self.URGENT_DAYS:
            return f"⚠️ Beta expires in {days} days!"
        elif days <= self.WARNING_DAYS:
            return f"ℹ️ Beta expires in {days} days"
        return f"Beta - {days} days remaining"
