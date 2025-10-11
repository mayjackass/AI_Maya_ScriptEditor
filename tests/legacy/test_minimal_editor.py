#!/usr/bin/env python
"""
Minimal version of AiScriptEditor to test component by component
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtCore, QtGui

class MinimalAiEditor(QtWidgets.QMainWindow):
    def __init__(self):
        print("🔧 Starting minimal constructor...")
        super().__init__()
        print("✅ super().__init__() completed")
        
        self.setWindowTitle("Minimal AI Script Editor")
        print("✅ Window title set")
        
        self.resize(800, 600)
        print("✅ Window resized")
        
        # Try creating the basic components one by one
        try:
            print("🔧 Creating central widget...")
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            print("✅ Central widget created")
        except Exception as e:
            print(f"❌ Central widget failed: {e}")
            raise
            
        try:
            print("🔧 Creating basic layout...")
            layout = QtWidgets.QVBoxLayout(central)
            print("✅ Layout created")
        except Exception as e:
            print(f"❌ Layout failed: {e}")
            raise
            
        try:
            print("🔧 Creating test tab widget...")
            tabs = QtWidgets.QTabWidget()
            layout.addWidget(tabs)
            print("✅ Tab widget created")
        except Exception as e:
            print(f"❌ Tab widget failed: {e}")
            raise
            
        print("✅ Minimal constructor completed successfully!")

def test_minimal_editor():
    """Test the minimal editor."""
    try:
        print("🔧 Creating QApplication...")
        app = QtWidgets.QApplication(sys.argv)
        
        print("🔧 Creating minimal editor...")
        window = MinimalAiEditor()
        
        print("🔧 Showing window...")
        window.show()
        window.raise_()
        window.activateWindow()
        
        print("✅ Minimal editor should now be visible!")
        print("   Window visible:", window.isVisible())
        print("   Window size:", window.size())
        
        # Keep it alive for a few seconds
        import time
        for i in range(50):
            app.processEvents()
            time.sleep(0.1)
            
        return True
        
    except Exception as e:
        print(f"❌ Minimal editor failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TESTING MINIMAL AI EDITOR")
    print("=" * 40)
    
    if test_minimal_editor():
        print("\n✅ Minimal editor works!")
        print("🎯 The issue is in the full AiScriptEditor constructor")
        print("   Check for complex imports or component initialization")
    else:
        print("\n❌ Even minimal editor fails")
        print("🎯 There's a more fundamental Qt or system issue")