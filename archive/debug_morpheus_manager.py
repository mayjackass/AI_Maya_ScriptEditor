#!/usr/bin/env python3
"""Debug test for MorpheusManager"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[DEBUG] Testing MorpheusManager...")

try:
    from ai.copilot_manager import MorpheusManager
    print("[OK] MorpheusManager imported successfully")
    
    # Test creating manager
    manager = MorpheusManager(None)
    print("[OK] MorpheusManager created successfully")
    
    # Test send_message method
    print("[TEST] Testing send_message method...")
    manager.send_message("hello test", "")
    print("[OK] send_message executed without errors")
    
except Exception as e:
    print(f"[ERROR] MorpheusManager test failed: {e}")
    import traceback
    traceback.print_exc()

print("[DEBUG] Test completed")