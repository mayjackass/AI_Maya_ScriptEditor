"""
Test file for Maya and PyMEL syntax highlighting and tooltips
Hover over the highlighted keywords to see tooltips
"""

# Import Maya modules
import maya.cmds as cmds
import pymel.core as pm

# Test Maya cmds functions - hover over these
sphere = cmds.polySphere(radius=5, name="mySphere")
cube = cmds.polyCube(width=3, height=3, depth=3)
cmds.select(all=True)
cmds.setAttr("mySphere.translateX", 10)
cmds.move(0, 5, 0)
cmds.rotate(45, 0, 90)

# Test PyMEL functions - hover over these  
pm_sphere = pm.polySphere(radius=5)
selected = pm.selected()
children = pm_sphere[0].getChildren()
translation = pm_sphere[0].getTranslation()

# Test Python built-ins - hover over these
print("Hello Maya")
items = list(range(10))
length = len(items)

# Test PySide6/Qt - hover over these
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Qt, QTimer

button = QPushButton("Click me")
widget = QWidget()
