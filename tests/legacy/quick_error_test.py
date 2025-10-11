import sys
sys.path.insert(0, '.')

from PySide6 import QtWidgets
from main_window import AiScriptEditor

# Create QApplication
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

# Test multiple errors
test_code = """if True  # Missing colon
    x = 5 +  # Incomplete
def func(  # Unclosed paren"""

print("Testing multiple error detection...")
editor = AiScriptEditor()
problems = editor._get_python_syntax_errors(test_code)

print(f"Found {len(problems)} errors:")
for p in problems:
    print(f"  Line {p['line']}: {p['message']}")

if len(problems) >= 3:
    print("SUCCESS: Multiple error detection working!")
else:
    print("ISSUE: Still only finding single error")