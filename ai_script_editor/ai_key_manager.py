# ai_key_manager.py
import os, base64, json
from cryptography.fernet import Fernet
from PySide6 import QtWidgets, QtCore

KEY_FILE = os.path.join(os.path.expanduser("~"), ".ai_script_editor_key")

def _get_secret():
    """Generate or retrieve local encryption key (Fernet symmetric key)."""
    secret_file = os.path.join(os.path.expanduser("~"), ".ai_secret.bin")
    if os.path.exists(secret_file):
        return open(secret_file, "rb").read()
    key = Fernet.generate_key()
    with open(secret_file, "wb") as f:
        f.write(key)
    return key

def encrypt_api_key(api_key: str):
    f = Fernet(_get_secret())
    data = f.encrypt(api_key.encode("utf-8"))
    with open(KEY_FILE, "wb") as fh:
        fh.write(data)

def decrypt_api_key() -> str | None:
    if not os.path.exists(KEY_FILE):
        return None
    try:
        f = Fernet(_get_secret())
        data = open(KEY_FILE, "rb").read()
        return f.decrypt(data).decode("utf-8")
    except Exception:
        return None

def show_key_dialog(parent=None):
    """Dialog to enter or update OpenAI API key."""
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle("Set OpenAI API Key")
    layout = QtWidgets.QVBoxLayout(dlg)
    info = QtWidgets.QLabel("Enter your OpenAI API key (kept encrypted locally):")
    edit = QtWidgets.QLineEdit()
    edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
    layout.addWidget(info)
    layout.addWidget(edit)
    btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    layout.addWidget(btns)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    if dlg.exec():
        key = edit.text().strip()
        if key:
            encrypt_api_key(key)
            QtWidgets.QMessageBox.information(parent, "AI Key Saved", "🔐 Your key was securely stored.")
            return key
    return None
