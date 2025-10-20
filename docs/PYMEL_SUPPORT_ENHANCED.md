# Enhanced PyMEL Support - Feature Documentation

**Date:** January 15, 2025  
**Feature:** Enhanced PyMEL documentation and hover tooltips

## What Was Added

### 1. Comprehensive PyMEL Documentation Dictionary (50+ entries)

Added `PYMEL_DOCS` dictionary with detailed documentation for:

#### Core PyMEL Functions
- `selected()` - Get selected objects as PyNode list
- `PyNode()` - Convert string to PyNode object
- Object creation functions (polyCylinder, polyPlane, polyTorus, etc.)

#### PyMEL Node Types
- `Transform` - Transform nodes with position/rotation/scale
- `Mesh` - Polygon mesh shape nodes
- `Camera` - Camera nodes
- `Joint` - Skeletal joints for rigging
- `Attribute` - Attribute wrapper class

#### PyMEL Attribute Operations
- `connectAttr` - Connect using >> operator
- `disconnectAttr` - Disconnect using // operator
- `.get()` / `.set()` methods
- Direct attribute access (node.tx, node.ry, etc.)

#### PyMEL Hierarchy Operations
- `getChildren()` - Get child nodes
- `getParent()` - Get parent node
- `getShapes()` - Get shape nodes
- `listRelatives()` - List related nodes

#### PyMEL Transformation Methods
- `getTranslation()` / `setTranslation()`
- `getRotation()` / `setRotation()`
- `getScale()` / `setScale()`

#### PyMEL Animation
- `setKeyframe()` - Set keyframes
- `keyframe()` - Query/edit keyframes
- `currentTime()` - Get/set timeline frame
- `playblast()` - Create preview animation

#### PyMEL Modeling
- `polyUnite()` - Combine meshes
- `polySeparate()` - Separate meshes
- `polyEvaluate()` - Get mesh statistics

#### PyMEL Data Types
- `Vector` - 3D vector math
- `Point` - 3D point in space
- `Matrix` - Transformation matrix
- `Color` - RGBA color

### 2. Hover Tooltip Integration

All PyMEL functions now show:
- ✅ Proper syntax highlighting
- ✅ Function signatures with type hints
- ✅ Detailed descriptions
- ✅ Comparison with cmds equivalents
- ✅ Object-oriented approach explanations

### 3. PyMEL Examples File

Created `tests/test_pymel_examples.py` with:
- 300+ lines of PyMEL examples
- PyMEL vs cmds comparisons
- Common patterns and best practices
- Object-oriented usage examples
- Attribute connection examples with >> operator
- Vector math demonstrations

## Key Features

### Object-Oriented Approach
```python
# PyMEL (object-oriented)
sphere, _ = pm.polySphere()
sphere.tx.set(5)
x = sphere.tx.get()

# vs cmds (procedural)
sphere = cmds.polySphere()[0]
cmds.setAttr(sphere + ".tx", 5)
x = cmds.getAttr(sphere + ".tx")
```

### Intuitive Attribute Connections
```python
# PyMEL uses >> operator
sphere1.tx >> sphere2.tx

# vs cmds
cmds.connectAttr("sphere1.tx", "sphere2.tx")
```

### Pythonic Methods
```python
# PyMEL
children = node.getChildren()
parent = node.getParent()
shapes = node.getShapes()

# vs cmds
children = cmds.listRelatives(node, children=True)
parent = cmds.listRelatives(node, parent=True)[0]
shapes = cmds.listRelatives(node, shapes=True)
```

## Hover Tooltip Examples

### Hovering over `pm.selected()`
```
pm.selected() -> List[PyNode]

Get currently selected objects as PyNode list. 
More pythonic than cmds.ls(sl=True)

(pymel function)
```

### Hovering over `PyNode`
```
pm.PyNode("nodeName") -> PyNode

Convert string to PyNode object. Enables 
object-oriented access to any Maya node

(pymel class)
```

### Hovering over `.getTranslation()`
```
node.getTranslation() -> Vector

Get translation as Vector object

(pymel method)
```

## Testing

### Manual Testing
✅ Hover over PyMEL keywords shows documentation  
✅ Syntax highlighting works for PyMEL code  
✅ PyMEL examples file loads without errors  
✅ All 50+ PyMEL entries documented  

### Example Code to Test
```python
import pymel.core as pm

# Test these - all should show tooltips:
pm.selected()
pm.PyNode("sphere")
sphere.getChildren()
sphere.tx.get()
sphere.setTranslation([1,2,3])
pm.polySphere()
```

## Documentation Coverage

### Total PyMEL Entries: 50+

**Categories:**
- Core functions: 3
- Object creation: 4
- Node types: 5
- Attributes: 4
- Hierarchy: 4
- Transformation: 6
- Animation: 4
- Modeling: 3
- Data types: 4
- Utilities: 13+

## Benefits

### For Users
1. **Better Learning Curve** - Hover tooltips explain PyMEL concepts
2. **Quick Reference** - No need to open browser for docs
3. **Object-Oriented Clarity** - Understand PyNode vs string approach
4. **Comparison** - See PyMEL vs cmds differences

### For Developers
1. **Type Safety** - PyNodes provide better type checking
2. **Cleaner Code** - >> operator, pythonic methods
3. **Less String Manipulation** - No string concatenation for attributes
4. **Better IDE Support** - Object methods show in autocomplete

## Future Enhancements

### Possible Additions
🔲 Add more PyMEL node types (Nurbs, Lights, etc.)  
🔲 Add PyMEL constraint documentation  
🔲 Add PyMEL rigging utilities  
🔲 Add PyMEL animation curve utilities  
🔲 Add PyMEL shader/material docs  
🔲 Add PyMEL deformer documentation  

### Interactive Features
🔲 PyMEL code snippets in Morpheus AI  
🔲 PyMEL vs cmds converter tool  
🔲 PyMEL best practices checker  
🔲 Interactive PyMEL tutorial in editor  

## Comparison: cmds vs PyMEL

| Feature | maya.cmds | PyMEL |
|---------|-----------|-------|
| Objects | Strings | PyNode objects |
| Attributes | String paths | Object properties |
| Connections | connectAttr() | >> operator |
| Hierarchy | listRelatives() | .getChildren() |
| Type Safety | Low | High |
| Readability | Procedural | Object-oriented |
| Performance | Faster | Slightly slower |
| Best For | Scripts | Tools/Pipelines |

## Files Modified

1. **editor/hover_docs.py**
   - Added PYMEL_DOCS dictionary (50+ entries)
   - Updated get_documentation() to check PyMEL docs
   - Enhanced MAYA_DOCS with mel, pymel, OpenMaya entries

2. **tests/test_pymel_examples.py** (NEW)
   - 300+ lines of PyMEL examples
   - Comprehensive coverage of PyMEL features
   - Best practices and common patterns

## Summary

**PyMEL support is now comprehensive!**

Users get:
- ✅ 50+ documented PyMEL functions/classes
- ✅ Hover tooltips with syntax highlighting
- ✅ 300+ lines of example code
- ✅ PyMEL vs cmds comparisons
- ✅ Best practices documentation

The NEO Script Editor now provides **professional-grade PyMEL support** for Maya technical artists and developers! 🚀

---

**Status:** ✅ Complete and tested  
**PyMEL Coverage:** Comprehensive (50+ entries)  
**Documentation:** Complete with examples
