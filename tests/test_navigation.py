#!/usr/bin/env python3
"""
Test chat history navigation functionality.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up QApplication for testing
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv)

from ai.copilot_manager import MorpheusManager

print("[TEST] Testing chat history navigation...")

# Create MorpheusManager
manager = MorpheusManager(None)

print(f"[INIT] Initial state - Index: {manager.current_chat_index}, History: {len(manager.chat_history)}")

# Simulate some conversations
print("[TEST] Adding test conversations...")
manager.record_conversation("Hello", "Hi there!")
print(f"[CONV1] After conv 1 - Index: {manager.current_chat_index}, History: {len(manager.chat_history)}")

manager.record_conversation("How are you?", "I'm doing great!")
print(f"[CONV2] After conv 2 - Index: {manager.current_chat_index}, History: {len(manager.chat_history)}")

manager.record_conversation("What can you do?", "I can help with coding!")
print(f"[CONV3] After conv 3 - Index: {manager.current_chat_index}, History: {len(manager.chat_history)}")

# Test navigation
print("\n[TEST] Testing navigation methods...")
print("=== Testing previous_conversation ===")
manager.previous_conversation()
print(f"[PREV] After previous - Index: {manager.current_chat_index}")
current, total = manager.get_conversation_info()
print(f"[INFO] Conversation info: {current}/{total}")

print("=== Testing previous_conversation again ===")
manager.previous_conversation()
print(f"[PREV] After previous - Index: {manager.current_chat_index}")
current, total = manager.get_conversation_info()
print(f"[INFO] Conversation info: {current}/{total}")

print("=== Testing next_conversation ===")
manager.next_conversation()
print(f"[NEXT] After next - Index: {manager.current_chat_index}")
current, total = manager.get_conversation_info()
print(f"[INFO] Conversation info: {current}/{total}")

print("=== Testing new_conversation ===")
manager.new_conversation()
print(f"[NEW] After new - Index: {manager.current_chat_index}")
current, total = manager.get_conversation_info()
print(f"[INFO] Conversation info: {current}/{total}")

print("\n[SUCCESS] Navigation test completed!")