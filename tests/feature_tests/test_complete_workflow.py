"""
Test script to verify syntax error detection and highlighting workflow
"""

import sys
import os
import time
sys.path.append(os.path.dirname(__file__))

from PySide6 import QtWidgets, QtCore, QtGui
from main_window import AiScriptEditor

def test_complete_workflow():
    """Test the complete syntax error detection and highlighting workflow"""
    
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    try:
        print("🔧 Creating AI Script Editor...")
        
        # Create editor window
        editor_window = AiScriptEditor()
        editor_window.show()
        editor_window.setWindowTitle("SYNTAX ERROR WORKFLOW TEST")
        
        # Wait for initialization
        QtCore.QTimer.singleShot(500, lambda: test_syntax_detection(editor_window, app))
        
        app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_syntax_detection(editor_window, app):
    """Test syntax detection after window is initialized"""
    
    try:
        print("\n🧪 Testing syntax error detection workflow...")
        
        # Get the active editor
        editor = editor_window._active_editor()
        if not editor:
            print("❌ No active editor found")
            return
            
        print(f"✅ Active editor found: {type(editor)}")
        
        # Test code with multiple syntax errors
        error_code = '''# Test syntax errors
print("Missing quote
def test():
print("Bad indent")
if True
    pass
x == = 5
'''
        
        print("📝 Setting test code with syntax errors...")
        editor.setPlainText(error_code)
        
        # Check if syntax timer exists
        if hasattr(editor, '_syntax_timer'):
            print(f"✅ Syntax timer found: {editor._syntax_timer}")
        else:
            print("❌ No syntax timer found")
            
        # Check text changed connections
        print("🔄 Triggering text change...")
        editor.insertPlainText("")  # Trigger text change
        
        # Wait for timer and check results
        def check_results():
            print("\n📊 CHECKING RESULTS:")
            
            # Check if errors were detected
            if hasattr(editor, '_error_lines'):
                print(f"  Error lines: {editor._error_lines}")
            else:
                print("  No error lines found")
                
            if hasattr(editor, '_error_selections'):
                print(f"  Error selections: {len(editor._error_selections)}")
            else:
                print("  No error selections found")
                
            # Check problems panel
            if hasattr(editor_window, 'problemsList'):
                count = editor_window.problemsList.topLevelItemCount() if hasattr(editor_window.problemsList, 'topLevelItemCount') else 0
                print(f"  Problems panel items: {count}")
            else:
                print("  No problems panel found")
                
            print("\n✅ Test completed! Check the editor window for visual results.")
            
            # Keep running for visual inspection
            QtCore.QTimer.singleShot(30000, app.quit)  # Close after 30 seconds
        
        QtCore.QTimer.singleShot(2000, check_results)  # Wait 2 seconds for detection
        
    except Exception as e:
        print(f"❌ Error in syntax detection test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_workflow()