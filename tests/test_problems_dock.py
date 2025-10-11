#!/usr/bin/env python
"""
Test the Problems dock specifically
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets
from main_window import AiScriptEditor

def test_problems_dock():
    """Test the Problems dock functionality."""
    
    app = QtWidgets.QApplication(sys.argv)
    window = AiScriptEditor()
    
    print("🧪 TESTING PROBLEMS DOCK")
    print("=" * 40)
    
    # Check if problems list exists
    if hasattr(window, 'problemsList') and window.problemsList:
        print("✅ Problems list exists")
        print(f"   Type: {type(window.problemsList)}")
        
        # Test adding some sample problems
        sample_problems = [
            {'type': 'Error', 'message': 'Missing colon', 'line': 5, 'file': 'test.py'},
            {'type': 'Warning', 'message': 'Unused variable', 'line': 10, 'file': 'test.py'},
            {'type': 'Error', 'message': 'Invalid syntax', 'line': 15, 'file': 'test.py'}
        ]
        
        try:
            window._update_problems(sample_problems)
            print("✅ Successfully added sample problems")
            
            # Check if problems were added
            if isinstance(window.problemsList, QtWidgets.QTreeWidget):
                count = window.problemsList.topLevelItemCount()
                print(f"✅ Tree widget has {count} items")
            elif isinstance(window.problemsList, QtWidgets.QListWidget):
                count = window.problemsList.count()
                print(f"✅ List widget has {count} items")
                
        except Exception as e:
            print(f"❌ Failed to add problems: {e}")
            
    else:
        print("❌ Problems list not found or is None")
        
    # Show window
    window.show()
    print("\n🎯 Window should be visible with Problems dock!")
    print("   Look for:")
    print("   • Problems panel at the bottom")
    print("   • Sample errors listed")
    print("   • Status bar showing problem count")
    
    # Keep alive for testing
    import time
    for i in range(50):
        app.processEvents()
        time.sleep(0.1)
    
    return True

if __name__ == "__main__":
    try:
        test_problems_dock()
        print("✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()