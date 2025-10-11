#!/usr/bin/env python
"""
NEO Script Editor - Test Runner
Run all tests to validate functionality.
"""

import os
import sys
import subprocess

# Add parent directory to path so tests can import the modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

def run_test(test_file):
    """Run a single test file and return success status."""
    try:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_file}")
        print(f"{'='*60}")
        
        result = subprocess.run([sys.executable, test_file], 
                              cwd=script_dir, 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ PASSED")
            print(result.stdout)
            return True
        else:
            print("❌ FAILED")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 NEO Script Editor - Test Suite Runner")
    print("=" * 60)
    
    # Define test files in order of importance
    test_files = [
        "test_regex.py",               # Basic regex functionality
        "test_parsing.py",             # Code block parsing 
        "test_final_integration.py",   # Integration tests
        "test_morpheus_debug.py",      # AI response processing
        "test_bug_fixes.py",           # Bug fix validation
        "test_complete_features.py",   # Full feature validation
    ]
    
    # Optional UI tests (require manual verification)
    ui_tests = [
        "test_ai_display.py",          # AI display (requires PySide6)
        "test_chat.py",               # Chat functionality
        "test_improvements.py",       # UI improvements
        "test_conversation_style.py", # Conversation styling
        "test_python_support.py",     # Python support
    ]
    
    passed = 0
    failed = 0
    
    print(f"📋 Running {len(test_files)} core tests...\n")
    
    # Run core tests
    for test_file in test_files:
        if os.path.exists(os.path.join(script_dir, test_file)):
            if run_test(test_file):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    # Show results
    print(f"\n{'='*60}")
    print(f"📊 TEST RESULTS")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total Tests: {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 ALL CORE TESTS PASSED!")
        print(f"   NEO Script Editor is ready for use!")
    else:
        print(f"\n⚠️  {failed} tests failed - check output above")
    
    # Show optional tests
    print(f"\n📋 Optional UI Tests (run manually in Maya):")
    for test_file in ui_tests:
        if os.path.exists(os.path.join(script_dir, test_file)):
            print(f"   • {test_file}")
    
    print(f"\n💡 To run individual tests:")
    print(f"   cd tests && python test_name.py")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)