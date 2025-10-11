"""
Simple diagnostic script to check chat history and button issues
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_main_window():
    """Analyze the main window code for potential issues."""
    print("=== Code Analysis ===")
    
    # Check if required imports are present
    with open('main_window.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    checks = {
        'historyUpdated signal connection': 'historyUpdated.connect' in content,
        'get_conversation_info method call': 'get_conversation_info' in content,
        '_update_history_info method': 'def _update_history_info' in content,
        'floating action setup': '_setup_floating_code_actions' in content,
        'button click connections': 'clicked.connect' in content,
        'current_floating_code variable': 'current_floating_code' in content,
        'MorpheusManager creation': 'MorpheusManager(self)' in content,
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {passed}")
    
    # Check for potential issues
    print("\n=== Potential Issues ===")
    
    # Check if historyUpdated signal is emitted in copilot_manager
    with open('ai/copilot_manager.py', 'r', encoding='utf-8') as f:
        copilot_content = f.read()
    
    signal_emit_checks = {
        'historyUpdated.emit() calls': 'historyUpdated.emit' in copilot_content,
        'Signal definition': 'historyUpdated = QtCore.Signal' in copilot_content,
        'record_conversation method': 'def record_conversation' in copilot_content,
    }
    
    for check, passed in signal_emit_checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {passed}")
    
    # Look for specific error patterns
    if '_update_history_info' in content and 'get_conversation_info' in content:
        print("✅ History update logic is present")
    else:
        print("❌ History update logic may be missing")
        
    if 'floatingCopyBtn.clicked.connect' in content:
        print("✅ Button connections are present")
    else:
        print("❌ Button connections may be missing")

def check_signal_emission():
    """Check if signals are properly emitted."""
    print("\n=== Signal Emission Analysis ===")
    
    with open('ai/copilot_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Look for historyUpdated.emit() calls
    emit_lines = []
    for i, line in enumerate(lines):
        if 'historyUpdated.emit' in line:
            emit_lines.append((i+1, line.strip()))
    
    if emit_lines:
        print(f"✅ Found {len(emit_lines)} historyUpdated.emit() calls:")
        for line_num, line_text in emit_lines:
            print(f"   Line {line_num}: {line_text}")
    else:
        print("❌ No historyUpdated.emit() calls found!")
        print("   This could be why the history counter isn't updating")

if __name__ == "__main__":
    analyze_main_window()
    check_signal_emission()