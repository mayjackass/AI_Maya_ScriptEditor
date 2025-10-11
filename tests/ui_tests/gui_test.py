#!/usr/bin/env python3
"""
Simple GUI test to check if PySide6 is working
"""
import sys
import os

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from PySide6 import QtWidgets, QtCore
    
    print("Testing PySide6...")
    
    class SimpleWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test Window")
            self.setGeometry(100, 100, 400, 300)
            
            # Simple text editor
            central = QtWidgets.QTextEdit()
            central.setPlainText("Testing PySide6 installation...")
            self.setCentralWidget(central)
    
    app = QtWidgets.QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    
    print("✅ GUI test window created successfully!")
    
    # Run for a short time then exit
    QtCore.QTimer.singleShot(1000, app.quit)
    sys.exit(app.exec())
    
except Exception as e:
    print(f"❌ GUI test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)