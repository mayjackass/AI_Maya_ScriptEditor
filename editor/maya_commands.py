"""
Maya Command Validation Database
==================================
Comprehensive list of ALL valid Maya commands, PyMEL methods, and MEL commands.
Used for intelligent syntax error detection and typo suggestions.

This is a KEY SELLING POINT: The app KNOWS Maya and can detect typos intelligently!
"""

# All valid maya.cmds commands (1000+ commands in real Maya, we list the most common)
# This list is extracted from our hover_docs.py and expanded with additional Maya commands
VALID_CMDS_COMMANDS = {
    # Core modules
    'cmds', 'mel', 'OpenMaya', 'OpenMayaUI', 'OpenMayaAnim', 'OpenMayaFX', 'OpenMayaRender',
    
    # Creation - Polygons
    'polySphere', 'polyCube', 'polyCylinder', 'polyPlane', 'polyTorus', 'polyCone',
    'polyPyramid', 'polyPipe', 'polyPrism', 'polyHelix', 'polyGear',
    
    # Creation - NURBS
    'sphere', 'cube', 'cylinder', 'cone', 'torus', 'plane',
    'nurbsSphere', 'nurbsCube', 'nurbsCylinder', 'nurbsPlane', 'nurbsTorus',
    'circle', 'square', 'curve', 'curveOnSurface',
    
    # Creation - Other
    'spaceLocator', 'joint', 'ikHandle', 'cluster', 'lattice',
    'camera', 'light', 'annotate', 'dimensionShape',
    
    # Selection & Query
    'select', 'ls', 'filterExpand', 'listRelatives', 'listHistory', 'listConnections',
    'listAttr', 'attributeQuery', 'objExists', 'nodeType', 'objectType',
    'selectedNodes', 'hilite', 'selectMode', 'selectType', 'selectPref',
    
    # Attributes
    'setAttr', 'getAttr', 'addAttr', 'deleteAttr', 'attributeExists',
    'connectAttr', 'disconnectAttr', 'listConnections', 'isConnected',
    'attributeInfo', 'attributeName', 'attributeQuery',
    
    # Transform
    'move', 'rotate', 'scale', 'xform', 'makeIdentity',
    'centerPivot', 'resetPivot', 'matchTransform', 'align', 'snap',
    
    # Hierarchy
    'parent', 'group', 'unparent', 'instance', 'duplicate',
    'listRelatives', 'pickWalk', 'reorder',
    
    # Scene
    'delete', 'rename', 'hide', 'show', 'objExists',
    'file', 'newFile', 'openFile', 'saveFile', 'saveAs',
    'importFile', 'exportSelected', 'reference', 'createReference',
    
    # Nodes
    'createNode', 'nodeType', 'objectType', 'listNodeTypes',
    'shadingNode', 'createRenderNode',
    
    # Animation
    'keyframe', 'setKeyframe', 'cutKey', 'copyKey', 'pasteKey',
    'currentTime', 'playbackOptions', 'playblast',
    'animCurve', 'findKeyframe', 'keyTangent', 'setInfinity',
    
    # Deformers
    'skinCluster', 'blendShape', 'cluster', 'lattice', 'wire',
    'nonLinear', 'sculpt', 'textureDeformer', 'wrap',
    'skinPercent', 'skinCluster', 'bindSkin', 'unbindSkin',
    
    # Constraints
    'parentConstraint', 'pointConstraint', 'orientConstraint',
    'scaleConstraint', 'aimConstraint', 'poleVectorConstraint',
    'geometryConstraint', 'normalConstraint', 'tangentConstraint',
    
    # Polygon Operations
    'polyEvaluate', 'polyUnite', 'polySeparate', 'polyMergeVertex',
    'polyExtrudeFacet', 'polyExtrudeEdge', 'polyBevel', 'polySmooth',
    'polyReduce', 'polyTriangulate', 'polyQuad', 'polyDelFacet',
    'polyDelEdge', 'polyDelVertex', 'polyMoveVertex', 'polyMoveEdge',
    'polyMoveFacet', 'polyNormal', 'polySetToFaceNormal',
    'polyMergeUV', 'polySplitVertex', 'polyChipOff', 'polySplit',
    
    # UV Operations
    'polyProjection', 'polyPlanarProjection', 'polyCylProjection',
    'polyMapCut', 'polyMapSew', 'polyEditUV', 'polyForceUV',
    'polyNormalizeUV', 'polyLayoutUV',
    
    # Shading & Materials (CRITICAL!)
    'shadingNode', 'sets', 'hyperShade', 'listNodeTypes',
    'shadingConnection', 'defaultNavigation',
    
    # Material types
    'lambert', 'blinn', 'phong', 'phongE', 'anisotropic',
    'standardSurface', 'aiStandardSurface', 'surfaceShader',
    
    # Texture nodes
    'file', 'checker', 'noise', 'ramp', 'fractal', 'grid', 'cloth',
    'place2dTexture', 'place3dTexture', 'projection',
    'uvChooser', 'stencil', 'layeredTexture',
    
    # Utility nodes
    'bump2d', 'reverse', 'multiplyDivide', 'blendColors',
    'condition', 'clamp', 'remapValue', 'luminance',
    'plusMinusAverage', 'setRange', 'contrast', 'gammaCorrect',
    'hsvToRgb', 'rgbToHsv', 'vectorProduct', 'angleBetween',
    
    # Lights (CRITICAL!)
    'pointLight', 'spotLight', 'directionalLight', 'ambientLight', 'areaLight',
    'aiAreaLight', 'aiSkyDomeLight', 'lightlink', 'lightInfo',
    
    # Rendering
    'render', 'renderWindowEditor', 'arnoldRender', 'renderSettings',
    'batchRender', 'renderLayerEditor', 'renderPartition',
    
    # Dynamics & FX
    'particle', 'emitter', 'nParticle', 'nucleus', 'nCloth', 'nRigid',
    'fluid', 'volumeAxis', 'spring', 'rigidBody', 'gravity', 'turbulence',
    
    # Misc
    'namespace', 'undo', 'redo', 'undoInfo', 'dgdirty', 'dgeval',
    'refresh', 'flushUndo', 'quit', 'error', 'warning',
    'progressBar', 'progressWindow', 'waitCursor',
}

# All valid PyMEL methods
VALID_PYMEL_COMMANDS = {
    # Core
    'pm', 'pymel', 'selected', 'PyNode', 'Attribute',
    
    # Creation (same as cmds but returns PyNodes)
    'polySphere', 'polyCube', 'polyCylinder', 'polyPlane', 'polyTorus',
    'polyCone', 'polyPyramid', 'polyPipe',
    
    # Selection & Query (PyMEL versions)
    'select', 'ls', 'listRelatives', 'listConnections', 'listHistory',
    'listAttr', 'objExists', 'filterExpand',
    
    # Attributes (PyMEL supports both cmds-style AND object-style)
    'setAttr', 'getAttr', 'addAttr', 'deleteAttr', 'attributeExists',
    'connectAttr', 'disconnectAttr', 'isConnected',
    
    # Transform operations
    'move', 'rotate', 'scale', 'xform', 'makeIdentity',
    
    # Hierarchy
    'parent', 'group', 'duplicate', 'instance',
    
    # Scene
    'delete', 'rename', 'hide', 'show',
    
    # Shading
    'shadingNode', 'sets', 'hyperShade',
    
    # Node types  
    'Transform', 'Mesh', 'Camera', 'Joint', 'NurbsCurve', 'NurbsSurface',
    
    # Methods (accessed on PyNode objects - object.method() style)
    'getChildren', 'getParent', 'getShapes', 'getAllParents',
    'getTranslation', 'setTranslation', 'getRotation', 'setRotation',
    'getScale', 'setScale', 'getMatrix', 'setMatrix',
    'numVertices', 'numFaces', 'numEdges', 'getPoints', 'setPoints',
    'hasAttr', 'attr', 'get', 'set', 'connect', 'disconnect',
}

# OpenMaya API classes and functions
VALID_OPENMAYA_CLASSES = {
    # Core
    'MObject', 'MDagPath', 'MSelectionList', 'MFnBase', 'MGlobal',
    'MPlug', 'MPlugArray', 'MDataHandle', 'MDataBlock',
    
    # Function Sets
    'MFnDependencyNode', 'MFnDagNode', 'MFnTransform', 'MFnMesh',
    'MFnNurbsCurve', 'MFnNurbsSurface', 'MFnCamera', 'MFnLight',
    'MFnSkinCluster', 'MFnBlendShapeDeformer', 'MFnAttribute',
    'MFnNumericAttribute', 'MFnTypedAttribute', 'MFnEnumAttribute',
    
    # Iterators
    'MItDag', 'MItDependencyNodes', 'MItSelectionList',
    'MItMeshVertex', 'MItMeshPolygon', 'MItMeshEdge', 'MItGeometry',
    'MItCurveCV', 'MItSurfaceCV', 'MItKeyframe',
    
    # Data Types
    'MPoint', 'MVector', 'MFloatVector', 'MMatrix', 'MFloatMatrix',
    'MColor', 'MQuaternion', 'MEulerRotation', 'MAngle', 'MDistance',
    'MTime', 'MSpace', 'MBoundingBox',
    
    # Arrays
    'MPointArray', 'MVectorArray', 'MFloatVectorArray', 'MIntArray',
    'MFloatArray', 'MDoubleArray', 'MStringArray', 'MObjectArray',
    
    # Messages & Events
    'MMessage', 'MEventMessage', 'MNodeMessage', 'MDGMessage',
    'MModelMessage', 'MSceneMessage', 'MUiMessage',
    
    # Plugin
    'MPxNode', 'MPxCommand', 'MPxDeformerNode', 'MPxLocatorNode',
    'MFnPlugin', 'MTypeId', 'MCommandResult',
}

# Common MEL commands
VALID_MEL_COMMANDS = {
    # MEL execution
    'eval',
    
    # MEL-specific commands (some overlap with cmds)
    'print', 'echo', 'trace', 'catchQuiet',
    'proc', 'global', 'source',
    'whatIs', 'exists',
    
    # UI (MEL-heavy)
    'window', 'showWindow', 'deleteUI', 'windowPref',
    'formLayout', 'rowLayout', 'columnLayout', 'frameLayout',
    'button', 'textField', 'checkBox', 'radioButton',
    'intSlider', 'floatSlider', 'optionMenu', 'menuItem',
    'separator', 'text', 'scrollField', 'scriptTable',
}

# Common typos and their corrections (for smart suggestions)
COMMON_TYPOS = {
    # Plural mistakes
    'setAttrs': 'setAttr',
    'getAttrs': 'getAttr',
    'connectAttrs': 'connectAttr',
    'disconnectAttrs': 'disconnectAttr',
    'listAttributes': 'listAttr',
    'addAttrs': 'addAttr',
    'deleteAttrs': 'deleteAttr',
    
    # Spelling mistakes
    'listConnection': 'listConnections',
    'polySpere': 'polySphere',
    'polySpheres': 'polySphere',
    'listRelative': 'listRelatives',
    'listRelative': 'listRelatives',
    'setKeyframes': 'setKeyframe',
    'getKeyframes': 'keyframe',
    
    # Case mistakes
    'SetAttr': 'setAttr',
    'GetAttr': 'getAttr',
    'PolyS phere': 'polySphere',
    'PolyCube': 'polyCube',
    
    # Common confusions
    'selectAll': 'select',  # Use: cmds.select(all=True)
    'deselectAll': 'select',  # Use: cmds.select(clear=True)
    'makeGroup': 'group',
    'createGroup': 'group',
    'removeParent': 'unparent',
}

def get_closest_command(unknown_cmd, namespace='cmds'):
    """
    Find closest valid command using fuzzy matching.
    Returns (closest_match, similarity_score) or (None, 0) if no good match.
    """
    # First check exact typo dictionary
    if unknown_cmd in COMMON_TYPOS:
        return (COMMON_TYPOS[unknown_cmd], 1.0)
    
    # Choose appropriate command set
    if namespace == 'cmds':
        valid_commands = VALID_CMDS_COMMANDS
    elif namespace in ('pm', 'pymel'):
        valid_commands = VALID_PYMEL_COMMANDS
    elif namespace == 'OpenMaya':
        valid_commands = VALID_OPENMAYA_CLASSES
    elif namespace == 'mel':
        valid_commands = VALID_MEL_COMMANDS
    else:
        valid_commands = VALID_CMDS_COMMANDS
    
    # Simple fuzzy matching using Levenshtein-like approach
    best_match = None
    best_score = 0
    
    for valid_cmd in valid_commands:
        # Calculate similarity (simple character overlap)
        score = _calculate_similarity(unknown_cmd.lower(), valid_cmd.lower())
        if score > best_score and score > 0.6:  # 60% similarity threshold
            best_score = score
            best_match = valid_cmd
    
    return (best_match, best_score) if best_match else (None, 0)


def _calculate_similarity(str1, str2):
    """
    Calculate similarity between two strings (0.0 to 1.0).
    Uses simple character overlap + length penalty.
    """
    if str1 == str2:
        return 1.0
    
    # Check if one starts with the other
    if str1.startswith(str2) or str2.startswith(str1):
        return 0.9
    
    # Character overlap
    set1 = set(str1)
    set2 = set(str2)
    overlap = len(set1 & set2)
    total = len(set1 | set2)
    
    if total == 0:
        return 0.0
    
    # Base similarity on character overlap
    char_sim = overlap / total
    
    # Penalize length difference
    len_diff = abs(len(str1) - len(str2))
    len_penalty = 1.0 - (len_diff / max(len(str1), len(str2)))
    
    return (char_sim * 0.7 + len_penalty * 0.3)


def is_valid_maya_command(cmd_name, namespace='cmds'):
    """
    Check if a command is valid in the given namespace.
    Returns True if valid, False otherwise.
    """
    if namespace == 'cmds':
        return cmd_name in VALID_CMDS_COMMANDS
    elif namespace in ('pm', 'pymel'):
        return cmd_name in VALID_PYMEL_COMMANDS
    elif namespace == 'OpenMaya':
        return cmd_name in VALID_OPENMAYA_CLASSES
    elif namespace == 'mel':
        return cmd_name in VALID_MEL_COMMANDS
    else:
        return False


# Export for use in error detection
__all__ = [
    'VALID_CMDS_COMMANDS',
    'VALID_PYMEL_COMMANDS', 
    'VALID_OPENMAYA_CLASSES',
    'VALID_MEL_COMMANDS',
    'COMMON_TYPOS',
    'get_closest_command',
    'is_valid_maya_command',
]
