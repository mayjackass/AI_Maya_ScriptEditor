#!/usr/bin/env python
"""
Step-by-step window creation test to isolate the issue
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_qt():
    """Test basic Qt functionality first."""
    try:
        from PySide6 import QtWidgets
        
        app = QtWidgets.QApplication(sys.argv)
        
        # Create a simple test window first
        test_window = QtWidgets.QMainWindow()
        test_window.setWindowTitle("Simple Test Window")
        test_window.resize(400, 300)
        test_window.show()
        
        print("✅ Simple Qt window created and shown")
        print("   Can you see a basic window titled 'Simple Test Window'?")
        
        # Process events briefly
        app.processEvents()
        
        # Keep it alive for 3 seconds
        import time
        for i in range(30):
            app.processEvents()
            time.sleep(0.1)
            
        return True
        
    except Exception as e:
        print(f"❌ Basic Qt test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_import_only():
    """Test just importing the main window without creating it."""
    try:
        print("🔧 Testing import only...")
        from main_window import AiScriptEditor
        print("✅ Import successful - no creation attempted")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 STEP-BY-STEP TESTING")
    print("=" * 40)
    
    print("\n1️⃣ Testing basic Qt functionality...")
    if test_basic_qt():
        print("   ✅ Basic Qt works")
    else:
        print("   ❌ Basic Qt failed - this is a Qt/display issue")
        sys.exit(1)
    
    print("\n2️⃣ Testing main window import...")
    if test_import_only():
        print("   ✅ Import works - issue is in constructor")
    else:
        print("   ❌ Import fails - syntax error in main_window.py")
        sys.exit(1)
        
    print("\n🎯 RESULTS:")
    print("   • Basic Qt works fine")
    print("   • Main window imports successfully") 
    print("   • Issue must be in AiScriptEditor.__init__()")
    print("\nThe problem is likely in the window initialization code.")