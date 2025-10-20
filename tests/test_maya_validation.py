"""
Test file for Comprehensive Maya Command Validation
====================================================
This file demonstrates the intelligent error detection system.
Open this file in the editor and watch the Problems window!

All errors below should be detected and shown with helpful suggestions.
"""

# =============================================================================
# TEST 1: Common Typos (Should all be detected with suggestions)
# =============================================================================

import maya.cmds as cmds

# ❌ Should detect: "setAttrs" should be "setAttr"
cmds.setAttrs("pCube1.translateX", 10)

# ❌ Should detect: "getAttrs" should be "getAttr"  
value = cmds.getAttrs("pCube1.translateX")

# ❌ Should detect: "polySpere" should be "polySphere"
sphere = cmds.polySpere(radius=5)

# ❌ Should detect: "listConnection" should be "listConnections"
connections = cmds.listConnection("pCube1.translateX")

# ❌ Should detect: "listRelative" should be "listRelatives"
children = cmds.listRelative("pCube1", children=True)

# ❌ Should detect: "connectAttrs" should be "connectAttr"
cmds.connectAttrs("pCube1.tx", "pCube2.tx")

# ❌ Should detect: "disconnectAttrs" should be "disconnectAttr"
cmds.disconnectAttrs("pCube1.tx", "pCube2.tx")


# =============================================================================
# TEST 2: Missing Imports (Should detect missing imports)
# =============================================================================

# ❌ Should detect: PyMEL not imported
sphere2 = pm.polySphere(radius=3)

# ❌ Should detect: OpenMaya not imported
obj = MObject()


# =============================================================================
# TEST 3: API Usage Errors (Should detect incorrect usage)
# =============================================================================

import maya.cmds as cmds

# ❌ Should detect: Missing [0] - primitives return [transform, shape]
sphere3 = cmds.polySphere(radius=5)

# ❌ Should detect: setAttr requires a value
cmds.setAttr("pCube1.translateX")

# ❌ Should detect: connectAttr needs two arguments
cmds.connectAttr("pCube1.translateX")

# ❌ Should detect: Missing .attribute format
cmds.setAttr("pCube1", 10)

# ❌ Should detect: getAttr missing .attribute format  
value2 = cmds.getAttr("pCube1")


# =============================================================================
# TEST 4: Completely Invalid Commands (Should detect with "Unknown command")
# =============================================================================

# ❌ Should detect: Unknown cmds command
cmds.thisCommandDoesNotExist()

# ❌ Should detect: Unknown cmds command (close to real command)
cmds.polyShpere(radius=5)  # Very close to polySphere

# ❌ Should detect: Unknown cmds command
cmds.setAttributes("node.attr", 10)


# =============================================================================
# TEST 5: CORRECT CODE (Should NOT show any errors)
# =============================================================================

import maya.cmds as cmds
import pymel.core as pm

# ✅ CORRECT - No errors
sphere_correct = cmds.polySphere(radius=5)[0]
cmds.setAttr("pCube1.translateX", 10)
value_correct = cmds.getAttr("pCube1.translateX")
connections_correct = cmds.listConnections("pCube1.translateX")
children_correct = cmds.listRelatives("pCube1", children=True)
cmds.connectAttr("pCube1.tx", "pCube2.tx")

# ✅ CORRECT - PyMEL
pm_sphere = pm.polySphere(radius=5)
selected = pm.selected()


# =============================================================================
# TEST 6: MEL Validation
# =============================================================================

import maya.mel as mel

# ❌ Should detect: mel.eval requires string
mel.eval(polySphere)

# ✅ CORRECT
mel.eval("polySphere -r 5")


print("Open the Problems window to see all detected errors!")
print("This file has intentional errors to test validation.")
