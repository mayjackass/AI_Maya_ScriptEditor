#!/usr/bin/env python3
"""
Quick test to verify Morpheus chat is working.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up QApplication for testing
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv)

from ai.copilot_manager import MorpheusManager

print("[TEST] Creating MorpheusManager...")
manager = MorpheusManager(None)

# Connect response signal
response_received = []

def on_response(response):
    print(f"[RESPONSE] Got AI response: {response[:100]}...")
    response_received.append(response)
    app.quit()

manager.responseReady.connect(on_response)

print("[TEST] Sending test message...")
manager.send_message("Hello Morpheus, are you working?", "")

# Give it 10 seconds to respond
QtCore.QTimer.singleShot(10000, app.quit)

print("[TEST] Waiting for response...")
app.exec()

if response_received:
    print("[SUCCESS] Chat system is working! ✅")
    print(f"Response preview: {response_received[0][:200]}...")
else:
    print("[ERROR] No response received ❌")