# 🎯 Maya Validation Quick Reference

## Common Typos That Get Detected

### Plural Mistakes ❌
```python
cmds.setAttrs()        → cmds.setAttr()
cmds.getAttrs()        → cmds.getAttr()
cmds.connectAttrs()    → cmds.connectAttr()
cmds.disconnectAttrs() → cmds.disconnectAttr()
cmds.addAttrs()        → cmds.addAttr()
cmds.deleteAttrs()     → cmds.deleteAttr()
```

### List Mistakes ❌
```python
cmds.listConnection()  → cmds.listConnections()
cmds.listRelative()    → cmds.listRelatives()
cmds.listAttribute()   → cmds.listAttr()
```

### Spelling Mistakes ❌
```python
cmds.polySpere()       → cmds.polySphere()
cmds.polySpheres()     → cmds.polySphere()
cmds.createNode()      → cmds.createNode() ✅ (correct)
cmds.shadingNode()     → cmds.shadingNode() ✅ (correct)
```

## API Usage Errors That Get Detected

### Missing Return Index ❌
```python
# Wrong:
sphere = cmds.polySphere()

# Correct:
sphere = cmds.polySphere()[0]  # Gets transform node
```

### Missing setAttr Value ❌
```python
# Wrong:
cmds.setAttr("pCube1.tx")

# Correct:
cmds.setAttr("pCube1.tx", 10)
```

### Missing connectAttr Destination ❌
```python
# Wrong:
cmds.connectAttr("pCube1.tx")

# Correct:
cmds.connectAttr("pCube1.tx", "pCube2.tx")
```

### Missing .attribute Format ❌
```python
# Wrong:
cmds.setAttr("pCube1", 10)
cmds.getAttr("pCube1")

# Correct:
cmds.setAttr("pCube1.translateX", 10)
cmds.getAttr("pCube1.translateX")
```

## Import Errors That Get Detected

### Missing maya.cmds ❌
```python
# Wrong (without import):
sphere = cmds.polySphere()

# Correct:
import maya.cmds as cmds
sphere = cmds.polySphere()[0]
```

### Missing PyMEL ❌
```python
# Wrong (without import):
sphere = pm.polySphere()

# Correct:
import pymel.core as pm
sphere = pm.polySphere()
```

### Missing OpenMaya ❌
```python
# Wrong (without import):
obj = MObject()

# Correct:
import maya.api.OpenMaya as om
obj = om.MObject()
```

## PyMEL-Specific Errors

### >> Operator Misuse ❌
```python
# Wrong:
sphere.tx >> cube  # Missing .attr on destination

# Correct:
sphere.tx >> cube.tx  # Both need .attr
```

## MEL Errors

### mel.eval Without String ❌
```python
# Wrong:
mel.eval(polySphere)

# Correct:
mel.eval("polySphere -r 5")
```

## OpenMaya Warnings

### MObject Without Null Check ⚠️
```python
# Warning:
obj = MObject()
# Use it directly... (dangerous!)

# Better:
obj = MObject()
if not obj.isNull():
    # Safe to use
```

## Full Example: Common Mistakes

```python
# ❌ WRONG - Multiple errors:
sphere = cmds.polySpheres()           # Typo: should be polySphere
value = cmds.getAttrs("node.attr")   # Typo: should be getAttr
cmds.setAttrs("node.attr")           # Typo + missing value
connections = cmds.listConnection()   # Typo: should be listConnections

# ✅ CORRECT:
import maya.cmds as cmds
sphere = cmds.polySphere()[0]                    # Get transform
value = cmds.getAttr("pCube1.translateX")       # Correct spelling
cmds.setAttr("pCube1.translateX", 10)           # Correct + value
connections = cmds.listConnections("pCube1.tx") # Correct plural
```

## How Suggestions Work

### High Similarity (90%+)
```
User types: setAttrs
Suggestion: "Did you mean 'setAttr'?"
```

### Medium Similarity (70-89%)
```
User types: polySpere
Suggestion: "Did you mean 'polySphere'?"
```

### Low Similarity (60-69%)
```
User types: polyShpere
Suggestion: "Did you mean 'polySphere'?"
```

### No Match (<60%)
```
User types: thisDoesNotExist
Message: "Unknown cmds command. Check Maya documentation."
```

## Test Your Knowledge!

**Can you spot the errors?**

```python
import maya.cmds as cmds

# How many errors are in this code?
sphere = cmds.polySpere()
cmds.setAttrs("pSphere1.tx", 10)
value = cmds.getAttrs("pSphere1")
connections = cmds.listConnection("pSphere1.tx")
cmds.connectAttrs("pSphere1.tx", "pCube1.tx")
```

**Answers:**
1. Line 4: `polySpere` → `polySphere`
2. Line 4: Missing `[0]` on return
3. Line 5: `setAttrs` → `setAttr`
4. Line 6: `getAttrs` → `getAttr`
5. Line 6: Missing `.attribute` format
6. Line 7: `listConnection` → `listConnections`
7. Line 8: `connectAttrs` → `connectAttr`

**Total: 7 errors!** (The app catches ALL of them! ✅)

## Pro Tips

1. **Watch the Problems Window** - Errors appear instantly
2. **Hover over errors** - See full message
3. **Trust the suggestions** - Fuzzy matching is smart
4. **Fix before running** - Save time debugging
5. **Learn as you code** - Suggestions teach correct syntax

## Most Common Mistakes (Top 10)

1. `setAttrs` instead of `setAttr`
2. `getAttrs` instead of `getAttr`
3. `polySpere` instead of `polySphere`
4. `listConnection` instead of `listConnections`
5. `listRelative` instead of `listRelatives`
6. Missing `[0]` on primitive creation
7. `setAttr` without value
8. `connectAttr` with one argument
9. Missing `.attribute` in get/setAttr
10. Forgetting to import maya.cmds

**The app catches EVERY SINGLE ONE!** 🎯

---

**Remember:** This validation is **unique to this IDE**! No other Maya tool has this level of intelligence! 🚀
