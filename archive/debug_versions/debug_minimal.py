#!/usr/bin/env python
"""
Minimal test to find exactly where AiScriptEditor crashes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore, QtGui

class MinimalTest(QtWidgets.QMainWindow):
    def __init__(self):
        print("🔧 Starting MinimalTest.__init__")
        super().__init__()
        print("✅ super().__init__() completed")
        
        self.setWindowTitle("Minimal Test")
        print("✅ setWindowTitle completed")
        
        self.resize(800, 600)
        print("✅ resize completed")

def test_minimal():
    """Test minimal window creation."""
    try:
        print("🔧 Creating QApplication...")
        app = QtWidgets.QApplication([])
        
        print("🔧 Creating minimal window...")
        window = MinimalTest()
        
        print("🔧 Showing window...")
        window.show()
        
        print("✅ Minimal test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Minimal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_window():
    """Test the real AiScriptEditor step by step."""
    try:
        print("\n🔧 Testing real AiScriptEditor...")
        
        # Import with error catching
        try:
            from main_window import AiScriptEditor
            print("✅ Import successful")
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
        
        print("🔧 Creating QApplication...")
        app = QtWidgets.QApplication([])
        
        print("🔧 Creating AiScriptEditor...")
        # This is where it's crashing - let's see if we can catch it
        window = AiScriptEditor()
        
        print("✅ AiScriptEditor created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Real window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 DEBUGGING WINDOW CREATION")
    print("=" * 50)
    
    # Test 1: Minimal window
    if test_minimal():
        print("\n✅ Minimal window works - issue is in AiScriptEditor")
    else:
        print("\n❌ Even minimal window fails - Qt issue")
        sys.exit(1)
    
    # Test 2: Real window
    if test_real_window():
        print("\n✅ Real window works!")
    else:
        print("\n❌ Real window fails in constructor")
        
    print("\n🎯 Check the error details above to see exactly where it fails")