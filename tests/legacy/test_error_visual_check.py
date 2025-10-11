#!/usr/bin/env python
"""Test multiple error detection and visual highlighting"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main_window import AiScriptEditor
from PySide6.QtWidgets import QApplication
from PySide6 import QtCore, QtGui

def test_multiple_error_highlighting():
    """Test that multiple errors are both detected AND visually highlighted"""
    
    # Create app
    if not QApplication.instance():
        app = QApplication([])
    
    # Create editor instance
    editor = AiScriptEditor()
    editor.show()
    
    # Code with multiple obvious syntax errors
    error_code = '''# Multiple syntax error test
if True  # Missing colon - ERROR 1
    print("test")
    
x = 5 +   # Incomplete expression - ERROR 2

def broken_func(  # Unclosed parenthesis - ERROR 3
    return "test"
    
for i in range(5)  # Missing colon - ERROR 4
    print(i)
'''
    
    # Set the code in the editor
    current_editor = editor._get_current_editor()
    if current_editor:
        current_editor.setPlainText(error_code)
        
        # Manually trigger syntax checking
        print("🔍 Triggering syntax check...")
        editor._check_syntax()
        
        # Check detection results
        problems = editor._get_python_syntax_errors(error_code)
        print(f"\n📊 DETECTION RESULTS:")
        print(f"   Total problems detected: {len(problems)}")
        for i, problem in enumerate(problems, 1):
            print(f"   {i}. Line {problem['line']}: {problem['message']}")
        
        # Check visual highlighting
        print(f"\n🎨 VISUAL HIGHLIGHTING:")
        if hasattr(current_editor, '_error_lines'):
            print(f"   Error lines stored: {sorted(current_editor._error_lines)}")
        else:
            print("   ❌ No _error_lines attribute found")
            
        if hasattr(current_editor, '_error_selections'):
            print(f"   Error selections count: {len(current_editor._error_selections)}")
        else:
            print("   ❌ No _error_selections attribute found")
        
        # Check current selections
        current_selections = current_editor.extraSelections()
        error_selections = [sel for sel in current_selections 
                          if sel.format.underlineColor() == QtGui.QColor("#ff0000")]
        print(f"   Active error selections: {len(error_selections)}")
        
        # Manual check of problems panel
        print(f"\n🗃️ PROBLEMS PANEL:")
        if hasattr(editor, 'problems_tree') and editor.problems_tree:
            items_count = editor.problems_tree.topLevelItemCount()
            print(f"   Problems panel items: {items_count}")
        else:
            print("   ❌ Problems panel not found")
        
        return len(problems) >= 3 and len(error_selections) >= 3
    
    return False

if __name__ == "__main__":
    print("🔧 Testing Multiple Error Detection & Visual Highlighting...")
    
    success = test_multiple_error_highlighting()
    
    if success:
        print("\n✅ SUCCESS: Multiple errors detected AND visually highlighted!")
    else:
        print("\n❌ ISSUE: Problems with detection or visual highlighting")
    
    # Keep app running briefly
    app = QApplication.instance()
    if app:
        QtCore.QTimer.singleShot(3000, app.quit)  # Auto-quit after 3 seconds
        app.exec_()