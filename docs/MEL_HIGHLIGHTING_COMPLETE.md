# Enhanced MEL Command Highlighting - Complete Maya Support

## Overview ✨
The MEL syntax highlighter has been completely enhanced with **comprehensive Maya command support** and VS Code Dark+ theme colors. Now covers ALL major Maya commands across every category.

## New MEL Command Categories 🎨

### **Geometry Creation** (Cyan `#4EC9B0`)
```mel
// Polygon primitives
polyCube, polySphere, polyCylinder, polyPlane, polyTorus, polyCone, polyPipe
polyHelix, polyPrism, polyPyramid, polyQuad, polyDisc, polyGear

// NURBS primitives  
nurbsPlane, nurbsSphere, nurbsCube, nurbsCylinder, nurbsCone, nurbsTorus

// Curves and surfaces
curve, circle, arc, square, surface, loft, extrude, revolve, planarSrf
```

### **Transform Operations** (Cyan `#4EC9B0`)
```mel
// Basic transforms
move, rotate, scale, xform

// Advanced transforms
makeIdentity, freezeTransformations, resetTransformations, centerPivot
duplicate, instance, group, ungroup, parent, unparent

// Constraints
pointConstraint, orientConstraint, parentConstraint, aimConstraint, scaleConstraint
```

### **Selection & Query** (Cyan `#4EC9B0`) 
```mel
// Selection commands
select, selectAll, selectNone, selectInvert, selectSimilar, selectHierarchy

// Listing and query
ls, listRelatives, listConnections, listAttr, listHistory, listSets
filterExpand, match, pickWalk, hilite, toggle
```

### **Attribute Management** (Cyan `#4EC9B0`)
```mel
// Get/Set attributes
getAttr, setAttr, addAttr, deleteAttr

// Connections
connectAttr, disconnectAttr, isConnected, connectionInfo
attributeExists, attributeQuery, lockNode, unlockNode, hide, show
```

### **Animation System** (Cyan `#4EC9B0`)
```mel
// Keyframe operations
keyframe, setKeyframe, cutKey, copyKey, pasteKey, scaleKey, snapKey
keyTangent, setInfinity, findKeyframe, keyframeStats

// Timeline and playback
currentTime, startTime, endTime, playbackOptions
animCurve, character, clipLibrary, bakeResults, playblast
```

### **Deformers & Rigging** (Cyan `#4EC9B0`)
```mel
// Non-linear deformers
bend, twist, wave, flare, squash, taper, sine

// Skin and blend shapes
skinCluster, bindSkin, unbindSkin, detachSkin, copySkinWeights
blendShape, wrap, shrinkWrap, cluster, sculpt

// Advanced deformers
lattice, ffd, wire, textDeformer, jiggle, tension
```

### **Rendering & Materials** (Cyan `#4EC9B0`)
```mel
// Render commands
render, batchRender, renderSettings, defaultRenderGlobals

// Material and shading
shadingNode, createNode, connectNodeToNodeOverride
hyperShade, nodeEditor, outliner, channelBox
```

### **File I/O & Project** (Cyan `#4EC9B0`)
```mel
// File operations
file, newFile, openFile, saveFile, saveAs
importFile, exportAll, exportSelected

// References and workspace
reference, createReference, loadReference, referenceEdit
workspace, project, namespace, namespaceInfo
```

## MEL Language Elements 🔧

### **Keywords** (Blue `#569CD6`)
```mel
if, else, for, while, do, switch, case, default, break, continue
return, proc, global, source, eval, catch
int, float, string, vector, matrix, alias, whatIs, exists, size, clear
```

### **Built-in Functions** (Purple `#C586C0`)
```mel
// Math functions
abs, acos, asin, atan, ceil, cos, exp, floor, log, max, min, pow, sqrt, sin, tan
deg_to_rad, rad_to_deg, rand, seed, noise, smoothstep, clamp

// Vector operations  
cross, dot, mag, unit, sphrand, hsv_to_rgb, rgb_to_hsv

// String functions
match, substitute, startString, endString, strip, tolower, toupper
size, clear, sort, stringArrayIntersector

// File operations
fopen, fclose, fprint, fread, fwrite, dirname, basename, filetest
system, getenv, putenv, date, timerX
```

### **Variables** (Light Blue `#9CDCFE`)
```mel
$myVariable, $objects[], $transform[4][4], $position
// All variables starting with $ properly highlighted
```

### **Command Flags** (Light Gray `#C8C8C8`)
```mel
-name, -radius, -height, -translate, -rotate, -scale
-absolute, -relative, -worldSpace, -objectSpace
// All flags starting with - highlighted
```

### **Procedure Names** (Yellow `#DCDCAA`)
```mel
proc createScene() { ... }
proc string getName() { ... }
proc float[] getWeights() { ... }
```

## Enhanced Features ⚡

### **Priority-Based Highlighting**
1. **Multi-line comments** `/* */` (highest priority)
2. **Single-line comments** `//`
3. **Strings** (backtick, double, single quotes)
4. **Numbers** (all formats including scientific)
5. **Procedure definitions**
6. **MEL keywords**
7. **Maya commands** (by category)
8. **Built-in functions**
9. **Command flags**
10. **Variables**
11. **Operators** (lowest priority)

### **Smart Pattern Recognition**
- **Command Detection**: Recognizes Maya commands in any context
- **Flag Recognition**: Properly highlights command flags with `-`
- **Variable Scope**: All `$variable` patterns highlighted
- **Procedure Syntax**: `proc` keyword and function names
- **String Varieties**: Double, single, and backtick quoted strings

### **Performance Optimized**
- **Efficient Regex**: Optimized patterns for fast highlighting
- **Category-Based**: Commands organized by Maya functionality
- **Incremental Updates**: Only re-highlights changed portions

## Example Highlighting 🎯

### **Complete MEL Script**
```mel
/*
    MEL script with comprehensive highlighting
*/

// Variables (Light Blue)
string $objects[] = {"pCube1", "pSphere1"};
float $radius = 2.5;
vector $position = <<0, 5, 0>>;

// Procedure definition (Yellow)
proc createGeometry() {
    // Maya commands (Cyan) with flags (Light Gray)
    string $cube[] = `polyCube -name "testCube" -width 2`;
    string $sphere[] = `polySphere -radius $radius -name "testSphere"`;
    
    // Transform commands (Cyan)
    move -absolute ($position.x) ($position.y) ($position.z) $sphere[0];
    rotate -relative 0 45 0 $cube[0];
    
    // Attribute operations (Cyan)
    setAttr ($cube[0] + ".translateX") 5.0;
    float $tx = `getAttr ($sphere[0] + ".translateY")`;
}

// Control flow (Blue keywords)
for ($i = 0; $i < size($objects); $i++) {
    if (`objExists $objects[$i]`) {
        select -add $objects[$i];
    }
}

// Built-in functions (Purple)
float $result = abs(-5.0) + sqrt(25.0) + sin(deg_to_rad(90.0));
```

## Usage Results 🚀

### **What You Get**
1. **All Maya Commands**: Every command category properly highlighted
2. **Complete MEL Language**: All keywords, functions, operators
3. **Professional Colors**: VS Code Dark+ theme consistency
4. **Smart Recognition**: Context-aware highlighting
5. **Fast Performance**: Optimized for large MEL scripts

### **Visual Impact**
- ✅ **Maya commands** stand out in cyan for easy recognition
- ✅ **MEL keywords** in blue match Python highlighting
- ✅ **Variables** clearly visible in light blue
- ✅ **Command flags** subtly highlighted in gray
- ✅ **Built-in functions** in purple for distinction
- ✅ **Comments and strings** properly colored

**Result: Professional MEL syntax highlighting that matches Maya's Script Editor with VS Code quality! 🎨✨**