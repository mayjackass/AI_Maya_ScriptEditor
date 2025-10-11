#!/usr/bin/env python3
"""
Test Performance Rollback - Verify Responsive Typing
"""

import sys
sys.path.insert(0, '.')
import time

from PySide6 import QtWidgets
from main_window import AiScriptEditor

def test_fast_syntax_check():
    """Test the fast syntax checking performance."""
    print("🚀 Testing FAST syntax checking...")
    
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Test code with errors
    test_code = """if True  # Missing colon
    x = 5 +  # Incomplete
def func(  # Unclosed paren"""
    
    editor_window = AiScriptEditor()
    
    # Time the fast detection
    start_time = time.time()
    problems = editor_window._get_python_syntax_errors_fast(test_code)
    fast_time = time.time() - start_time
    
    print(f"   Fast detection: {fast_time:.4f}s, found {len(problems)} errors")
    
    # Time the full detection 
    start_time = time.time()
    problems_full = editor_window._get_python_syntax_errors(test_code)
    full_time = time.time() - start_time
    
    print(f"   Full detection: {full_time:.4f}s, found {len(problems_full)} errors")
    
    # Fast should be much quicker
    if fast_time < 0.01:  # Should be very fast
        print("   ✅ FAST: Detection is lightning quick!")
        return True
    else:
        print(f"   ⚠️  SLOW: Fast detection took {fast_time:.4f}s")
        return False

def test_timer_settings():
    """Test timer delay settings."""
    print("\n⏱️  Testing timer delays...")
    
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    editor_window = AiScriptEditor()
    
    # Create a new tab to get editor
    editor_window._new_tab()
    editor = editor_window._active_editor()
    
    if editor and hasattr(editor, '_syntax_timer'):
        # Check timer interval (should be 500ms now)
        timer_interval = editor._syntax_timer.interval()
        print(f"   Timer delay: {timer_interval}ms")
        
        if timer_interval <= 500:
            print("   ✅ RESPONSIVE: Timer set for quick response")
            return True
        else:
            print(f"   ❌ SLOW: Timer is {timer_interval}ms (too slow)")
            return False
    else:
        print("   ❌ ERROR: Could not find timer")
        return False

def main():
    """Test performance rollback."""
    print("=" * 50)
    print("🎯 PERFORMANCE ROLLBACK TEST")
    print("   Testing responsive typing improvements")
    print("=" * 50)
    
    try:
        results = []
        results.append(test_fast_syntax_check())
        results.append(test_timer_settings())
        
        print("\n" + "=" * 50)
        print("📊 ROLLBACK TEST RESULTS")
        print("=" * 50)
        
        if all(results):
            print("🎉 ROLLBACK SUCCESSFUL!")
            print("   ⚡ Fast syntax detection implemented")
            print("   🚀 Responsive 500ms timer delays")
            print("   💨 Should feel much snappier when typing!")
        else:
            failed_tests = []
            test_names = ["Fast Syntax Check", "Timer Settings"]
            for i, (name, result) in enumerate(zip(test_names, results)):
                if not result:
                    failed_tests.append(name)
            print(f"❌ Issues found: {', '.join(failed_tests)}")
    
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()