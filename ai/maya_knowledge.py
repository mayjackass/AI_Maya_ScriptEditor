"""
Maya Knowledge Base for Morpheus AI
====================================
This module contains comprehensive Maya documentation that Morpheus uses to provide
expert-level assistance with Maya Python scripting, PyMEL, and OpenMaya API.

Morpheus has MASTERED:
- maya.cmds (100+ commands)
- PyMEL (60+ methods)  
- OpenMaya API 2.0 (80+ classes)
- Shading/Materials workflow
- Rigging best practices
- Performance optimization

This knowledge is automatically available to Morpheus for code generation,
debugging, and answering Maya-specific questions.
"""

# This imports all the comprehensive Maya documentation
from ..editor.hover_docs import MAYA_DOCS, PYMEL_DOCS, OPENMAYA_DOCS


class MayaKnowledge:
    """
    Maya expertise database for Morpheus AI assistant.
    Provides structured access to all Maya documentation.
    """
    
    def __init__(self):
        self.cmds_docs = MAYA_DOCS
        self.pymel_docs = PYMEL_DOCS
        self.api_docs = OPENMAYA_DOCS
        
    def get_command_info(self, command_name):
        """
        Get detailed information about a Maya command.
        Returns: (signature, description, category)
        """
        # Check in all documentation sources
        if command_name in self.cmds_docs:
            sig, desc = self.cmds_docs[command_name]
            return (sig, desc, 'maya.cmds')
        
        if command_name in self.pymel_docs:
            sig, desc = self.pymel_docs[command_name]
            return (sig, desc, 'pymel.core')
            
        if command_name in self.api_docs:
            sig, desc = self.api_docs[command_name]
            return (sig, desc, 'maya.api.OpenMaya')
            
        return None
    
    def get_workflow_guidance(self, task):
        """
        Get Maya workflow guidance for common tasks.
        Morpheus uses this for contextual suggestions.
        """
        workflows = {
            'create_material': {
                'approach': 'Use shadingNode + sets + connectAttr',
                'steps': [
                    '1. Create shader: shader = cmds.shadingNode("lambert", asShader=True)',
                    '2. Create shading group: sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)',
                    '3. Connect shader to SG: cmds.connectAttr(shader+".outColor", sg+".surfaceShader")',
                    '4. Assign to object: cmds.sets(obj, e=True, forceElement=sg)',
                ],
                'best_practice': 'Always create shading group (SG) with sets(). Connect shader.outColor to SG.surfaceShader.',
            },
            'freeze_transforms': {
                'approach': 'Use makeIdentity before rigging',
                'steps': [
                    '1. Select objects: cmds.select(objects)',
                    '2. Freeze: cmds.makeIdentity(apply=True, t=True, r=True, s=True)',
                ],
                'best_practice': 'ALWAYS freeze transforms before rigging or constraints. Critical for proper transform behavior.',
            },
            'iterate_mesh': {
                'approach': 'Use OpenMaya API for performance',
                'steps': [
                    '1. Get MSelectionList: sel = OpenMaya.MGlobal.getActiveSelectionList()',
                    '2. Get MDagPath: dagPath = sel.getDagPath(0)',
                    '3. Create MFnMesh: fnMesh = OpenMaya.MFnMesh(dagPath)',
                    '4. Use MItMeshVertex for vertices',
                ],
                'best_practice': 'OpenMaya API is 10-100x faster than cmds for large meshes. Always use for production tools.',
            },
            'get_selection': {
                'cmds': 'selected = cmds.ls(selection=True)',
                'pymel': 'selected = pm.selected()',
                'api': 'sel = OpenMaya.MGlobal.getActiveSelectionList()',
                'best_practice': 'PyMEL most pythonic. API fastest. cmds most compatible.',
            },
            'connect_attributes': {
                'cmds': 'cmds.connectAttr("source.attr", "dest.attr", force=True)',
                'pymel': 'source.attr >> dest.attr  # Use >> operator',
                'api': 'sourcePlug.connect(destPlug)',
                'best_practice': 'PyMEL >> operator is clearest. force=True breaks existing connections.',
            },
        }
        
        return workflows.get(task, None)
    
    def get_api_comparison(self):
        """
        Compare maya.cmds vs PyMEL vs OpenMaya API.
        Morpheus uses this to recommend the best approach.
        """
        return {
            'maya.cmds': {
                'pros': [
                    'Most compatible - works everywhere',
                    'Well documented',
                    'Simple procedural interface',
                    'No imports needed in Maya',
                ],
                'cons': [
                    'Returns strings, not objects',
                    'Verbose syntax',
                    'Less pythonic',
                    'Slower than API',
                ],
                'use_when': 'Quick scripts, simple operations, maximum compatibility',
            },
            'pymel.core': {
                'pros': [
                    'Most pythonic - object-oriented',
                    'Returns PyNode objects',
                    'Cleaner syntax (>> for connections)',
                    'Automatic type conversion',
                    'Better for complex scenes',
                ],
                'cons': [
                    'Slower startup time',
                    'Some overhead vs cmds',
                    'Requires import',
                    'Larger memory footprint',
                ],
                'use_when': 'Tool development, complex hierarchies, cleaner code desired',
            },
            'maya.api.OpenMaya': {
                'pros': [
                    '10-100x faster than cmds/PyMEL',
                    'Direct C++ API access',
                    'Minimal overhead',
                    'Essential for plugins',
                    'Production-grade performance',
                ],
                'cons': [
                    'Steeper learning curve',
                    'More verbose code',
                    'Pointer/handle management',
                    'Less intuitive',
                ],
                'use_when': 'Heavy iteration, plugins, performance-critical code, batch processing',
            },
        }
    
    def get_common_patterns(self):
        """
        Common Maya scripting patterns that Morpheus can suggest.
        """
        return {
            'safe_delete': '''
# Safe deletion with existence check
if cmds.objExists(node):
    cmds.delete(node)
''',
            'create_locator_at_selection': '''
# Create locator at selected object's position
sel = cmds.ls(selection=True)[0]
pos = cmds.xform(sel, q=True, ws=True, t=True)
loc = cmds.spaceLocator()[0]
cmds.xform(loc, ws=True, t=pos)
''',
            'iterate_hierarchy': '''
# Iterate all children recursively
def get_all_children(node):
    children = cmds.listRelatives(node, children=True, fullPath=True) or []
    all_descendants = list(children)
    for child in children:
        all_descendants.extend(get_all_children(child))
    return all_descendants
''',
            'get_mesh_vertex_positions': '''
# Get all vertex positions (fast with API)
import maya.api.OpenMaya as om
sel = om.MGlobal.getActiveSelectionList()
dagPath = sel.getDagPath(0)
fnMesh = om.MFnMesh(dagPath)
points = fnMesh.getPoints(om.MSpace.kWorld)  # MPointArray
''',
            'create_material_workflow': '''
# Complete material creation and assignment
shader = cmds.shadingNode('lambert', asShader=True, name='myMaterial')
sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='myMaterialSG')
cmds.connectAttr(shader + '.outColor', sg + '.surfaceShader', force=True)
cmds.select('pSphere1')
cmds.sets(forceElement=sg)
''',
            'undo_chunk': '''
# Wrap operations in undo chunk (single undo)
cmds.undoInfo(openChunk=True)
try:
    # Your operations here
    cmds.polySphere()
    cmds.move(0, 5, 0)
finally:
    cmds.undoInfo(closeChunk=True)
''',
            'pymel_object_oriented': '''
# PyMEL object-oriented approach
import pymel.core as pm
sphere = pm.polySphere()[0]  # Transform node
sphere.translateY.set(5)
sphere.scaleX.set(2)
children = sphere.getChildren()
shape = sphere.getShape()  # Mesh node
vert_count = shape.numVertices()
''',
            'api_mesh_iteration': '''
# Fast mesh vertex iteration with OpenMaya
import maya.api.OpenMaya as om
sel = om.MGlobal.getActiveSelectionList()
dagPath = sel.getDagPath(0)
itVert = om.MItMeshVertex(dagPath)
while not itVert.isDone():
    pos = itVert.position(om.MSpace.kWorld)
    print(f"Vertex {itVert.index()}: {pos.x}, {pos.y}, {pos.z}")
    itVert.next()
''',
        }
    
    def get_performance_tips(self):
        """
        Performance optimization tips for Maya Python.
        """
        return {
            'use_api_for_iteration': 'OpenMaya API is 10-100x faster than cmds for large datasets',
            'batch_operations': 'Batch operations instead of per-vertex/face operations',
            'disable_viewport': 'Use cmds.refresh(suspend=True) for heavy operations',
            'undo_chunks': 'Wrap operations in undoInfo chunks to reduce overhead',
            'avoid_ls_in_loops': 'Cache cmds.ls() results outside loops',
            'use_long_names': 'Use long names to avoid ambiguity, faster lookups',
            'pymel_overhead': 'PyMEL has initialization overhead but cleaner code',
            'list_comprehensions': 'Use list comprehensions instead of loops',
            'avoid_string_concat': 'Use f-strings instead of + concatenation',
            'cache_function_refs': 'Cache function references: ls = cmds.ls',
        }
    
    def get_error_solutions(self, error_type):
        """
        Common Maya error solutions.
        """
        solutions = {
            'object_not_found': {
                'error': "RuntimeError: Object 'pSphere1' not found",
                'causes': [
                    'Object name misspelled',
                    'Object deleted or renamed',
                    'Name not unique (use long names)',
                    'Object in referenced file',
                ],
                'solutions': [
                    'Check with: if cmds.objExists("pSphere1")',
                    'Use long names: cmds.ls("pSphere1", long=True)',
                    'List all objects: cmds.ls(type="transform")',
                ],
            },
            'attribute_not_found': {
                'error': "AttributeError: 'pSphere1.customAttr' not found",
                'causes': [
                    'Attribute does not exist',
                    'Attribute name misspelled',
                    'Attribute on wrong node',
                ],
                'solutions': [
                    'Check: cmds.attributeExists("customAttr", "pSphere1")',
                    'List attrs: cmds.listAttr("pSphere1")',
                    'Add attr: cmds.addAttr(longName="customAttr")',
                ],
            },
            'api_null_object': {
                'error': "RuntimeError: (kInvalidParameter): Object is invalid",
                'causes': [
                    'MObject is null',
                    'Node was deleted',
                    'Invalid MDagPath',
                ],
                'solutions': [
                    'Check: if not mobject.isNull()',
                    'Verify node exists before API operations',
                    'Use try/except for API calls',
                ],
            },
        }
        return solutions.get(error_type, None)
    
    def get_all_commands_summary(self):
        """
        Get summary of all available Maya commands.
        Returns total count and categorized lists.
        """
        return {
            'total_cmds_commands': len(self.cmds_docs),
            'total_pymel_methods': len(self.pymel_docs),
            'total_api_classes': len(self.api_docs),
            'total_documented': len(self.cmds_docs) + len(self.pymel_docs) + len(self.api_docs),
            'categories': {
                'creation': ['polySphere', 'polyCube', 'polyCylinder', 'polyPlane', 'polyTorus', 'polyCone'],
                'selection': ['select', 'ls', 'filterExpand', 'listRelatives', 'listHistory'],
                'attributes': ['setAttr', 'getAttr', 'addAttr', 'deleteAttr', 'connectAttr', 'disconnectAttr'],
                'transform': ['move', 'rotate', 'scale', 'xform', 'makeIdentity'],
                'hierarchy': ['parent', 'group', 'unparent', 'instance', 'duplicate'],
                'shading': ['shadingNode', 'sets', 'hyperShade', 'lambert', 'blinn', 'phong'],
                'animation': ['keyframe', 'setKeyframe', 'currentTime', 'playblast'],
                'pymel_core': ['selected', 'PyNode', 'getChildren', 'getParent', 'getShapes'],
                'api_function_sets': ['MFnMesh', 'MFnTransform', 'MFnDagNode', 'MFnDependencyNode'],
                'api_iterators': ['MItDag', 'MItMeshVertex', 'MItMeshPolygon', 'MItMeshEdge'],
            },
        }


# Global instance for easy access
maya_knowledge = MayaKnowledge()


def get_morpheus_context():
    """
    Get comprehensive Maya context for Morpheus.
    This is called when Morpheus needs Maya expertise.
    """
    return {
        'expertise': 'Maya Python Expert - maya.cmds, PyMEL, OpenMaya API',
        'knowledge_base': maya_knowledge,
        'capabilities': [
            'Generate Maya Python scripts',
            'Debug Maya code errors',
            'Explain Maya API differences',
            'Suggest performance optimizations',
            'Provide workflow best practices',
            'Create materials and shaders',
            'Write custom Maya tools',
            'Develop Maya plugins',
            'Rigging automation',
            'Batch processing scripts',
        ],
        'documentation_coverage': maya_knowledge.get_all_commands_summary(),
    }


# Export for Morpheus to import
__all__ = ['MayaKnowledge', 'maya_knowledge', 'get_morpheus_context']
