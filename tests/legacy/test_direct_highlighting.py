"""
Direct test of error highlighting in CodeEditor
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PySide6 import QtWidgets, QtCore, QtGui
from editor.code_editor import CodeEditor

def test_direct_highlighting():
    """Test error highlighting directly"""
    
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    # Create editor
    editor = CodeEditor()
    editor.show()
    editor.setWindowTitle("DIRECT Error Highlighting Test")
    editor.resize(800, 600)
    
    # Add test code
    test_code = '''# Line 1: Good
print("Missing quote   # Line 2: ERROR
def test():  # Line 3: Good
print("Bad indent")  # Line 4: ERROR  
if True  # Line 5: ERROR (missing colon)
    pass  # Line 6: Good
'''
    
    editor.setPlainText(test_code)
    
    # FORCE error highlighting
    try:
        print("🔧 Forcing error highlighting...")
        
        # 1. Set up error lines
        editor._error_lines = {1, 3, 4}  # Lines 2, 4, 5 (0-based)
        
        # 2. Create red wavy underline format
        error_format = QtGui.QTextCharFormat()
        error_format.setUnderlineStyle(QtGui.QTextCharFormat.UnderlineStyle.WaveUnderline)
        error_format.setUnderlineColor(QtGui.QColor("#ff0000"))  # Bright red
        
        # 3. Create extra selections
        editor._error_selections = []
        document = editor.document()
        
        for line_num in editor._error_lines:
            block = document.findBlockByNumber(line_num)
            if block.isValid():
                cursor = QtGui.QTextCursor(block)
                cursor.movePosition(QtGui.QTextCursor.StartOfBlock)
                cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
                
                selection = QtWidgets.QTextEdit.ExtraSelection()
                selection.format = error_format
                selection.cursor = cursor
                editor._error_selections.append(selection)
                
        # 4. Apply selections
        print(f"📝 Applying {len(editor._error_selections)} error selections...")
        editor.setExtraSelections(editor._error_selections)
        
        # 5. Force line number area update
        print("🔄 Updating line number area...")
        if hasattr(editor, 'number_area'):
            editor.number_area.update()
            
        print("✅ DONE! Check the editor window for:")
        print("   🔴 Red wavy underlines on lines 2, 4, 5")
        print("   🔴 Red dots on line numbers 2, 4, 5") 
        print("   🔴 Red background on those line numbers")
        
        # Keep running
        app.exec()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_highlighting()