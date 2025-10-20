# VS Code-Style Hover Documentation Test
# Hover over ANY word below to see beautiful syntax-highlighted tooltips!

# ========== Python Built-in Functions ==========
# Hover over: print, len, range, str, int, float, list, dict, enumerate, zip
print("Hello World")
length = len([1, 2, 3, 4, 5])
numbers = range(10)
text = str(123)
value = int("456")
decimal = float(3.14)

# ========== Python Keywords ==========
# Hover over: def, class, if, for, while, return, import, try, except
def my_function(param1, param2="default"):
    """This is a user-defined function with docstring."""
    if param1 > 0:
        return param1 + param2
    elif param1 == 0:
        pass
    else:
        return None

# Hover over: for, in, break, continue
for item in [1, 2, 3, 4, 5]:
    if item == 3:
        break
    else:
        continue

# ========== User-Defined Classes ==========
# Hover over: MyClass (the class name itself!)
class MyClass:
    """This is a user-defined class with a docstring.
    It demonstrates intelligent code analysis."""
    
    def __init__(self, name):
        """Constructor method."""
        self.name = name
    
    def greet(self):
        """Instance method that greets."""
        return f"Hello, {self.name}!"

# ========== PySide6/Qt Widgets ==========
# Hover over: QtWidgets, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PySide6 import QtWidgets, QtCore, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        button = QtWidgets.QPushButton("Click me")
        label = QtWidgets.QLabel("Hello Qt")
        layout.addWidget(button)
        layout.addWidget(label)

# ========== String & List Methods ==========
# Hover over: split, join, append, extend, pop, keys, values, items
text = "hello world"
words = text.split()
result = " ".join(words)

my_list = [1, 2, 3]
my_list.append(4)
my_list.extend([5, 6])
my_list.pop()

my_dict = {"key": "value"}
keys = my_dict.keys()
values = my_dict.values()
items = my_dict.items()

# ========== Maya Commands (if available) ==========
# Hover over: cmds, polySphere, select, ls, setAttr, getAttr
# import maya.cmds as cmds
# sphere = cmds.polySphere(radius=2.0, name="mySphere")
# cmds.select(sphere)
# objects = cmds.ls(selection=True)
# cmds.setAttr("mySphere.translateY", 5.0)

# ========== Advanced Features ==========
# Hover over: lambda, with, async, await
process = lambda x: x * 2

with open("file.txt") as f:
    content = f.read()

# Try hovering over EVERY word - keywords, functions, methods, and user-defined elements!

