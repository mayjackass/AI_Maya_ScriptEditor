"""
Comprehensive Maya cmds and PyMEL Test File
Hover over any Maya command to see detailed contextual documentation!
All commands below should be highlighted and show tooltips with usage examples.
"""

import maya.cmds as cmds
import pymel.core as pm

# ============================================================================
# POLYGON CREATION - All should be highlighted and documented
# ============================================================================
sphere = cmds.polySphere(radius=5, name="mySphere")
cube = cmds.polyCube(width=3, height=3, depth=3)
cylinder = cmds.polyCylinder(radius=2, height=5)
plane = cmds.polyPlane(width=10, height=10)
torus = cmds.polyTorus(radius=3, sectionRadius=0.5)
cone = cmds.polyCone(radius=2, height=4)
pyramid = cmds.polyPyramid(sideLength=3)
pipe = cmds.polyPipe(radius=2, height=4, thickness=0.2)

# ============================================================================
# SELECTION COMMANDS - Essential for querying scene
# ============================================================================
cmds.select(sphere, add=True)
cmds.select(all=True)
cmds.select(clear=True)

all_objects = cmds.ls()
selected = cmds.ls(selection=True)
transforms = cmds.ls(type="transform")
meshes = cmds.ls(type="mesh")

# ============================================================================
# ATTRIBUTE OPERATIONS - Set/Get object properties
# ============================================================================
cmds.setAttr("mySphere.translateX", 10)
cmds.setAttr("mySphere.translateY", 5)
cmds.setAttr("mySphere.scaleX", 2)

x_pos = cmds.getAttr("mySphere.translateX")
visibility = cmds.getAttr("mySphere.visibility")

# Add custom attributes
cmds.addAttr("mySphere", longName="customAttr", attributeType="double", defaultValue=1.0)
cmds.listAttr("mySphere", keyable=True)

# Connect attributes
cmds.connectAttr("mySphere.translateX", "pCube1.translateX")
cmds.disconnectAttr("mySphere.translateX", "pCube1.translateX")

# ============================================================================
# TRANSFORM OPERATIONS - Move, Rotate, Scale
# ============================================================================
cmds.move(0, 5, 0, "mySphere")
cmds.rotate(45, 0, 90, "mySphere")
cmds.scale(2, 2, 2, "mySphere")
cmds.xform("mySphere", query=True, translation=True)
cmds.makeIdentity("mySphere", apply=True, translate=True, rotate=True, scale=True)

# ============================================================================
# HIERARCHY OPERATIONS - Parent/Group/Organize
# ============================================================================
cmds.parent("pSphere1", "pCube1")
group = cmds.group("pSphere1", "pCube1", name="myGroup")
cmds.unparent("pSphere1")
instance = cmds.instance("pSphere1")
duplicate = cmds.duplicate("pSphere1")

# ============================================================================
# SCENE MANAGEMENT - Delete, Rename, Hide/Show
# ============================================================================
cmds.delete("pCube1")
cmds.rename("pSphere1", "mySphere_renamed")
cmds.hide("mySphere")
cmds.show("mySphere")
exists = cmds.objExists("mySphere")

# ============================================================================
# NODE OPERATIONS - Create nodes, query types
# ============================================================================
node = cmds.createNode("transform", name="myTransform")
node_type = cmds.nodeType("mySphere")
is_transform = cmds.objectType("mySphere", isType="transform")

# ============================================================================
# HIERARCHY QUERIES - List relatives, history, connections
# ============================================================================
children = cmds.listRelatives("myGroup", children=True)
parent = cmds.listRelatives("mySphere", parent=True)
shapes = cmds.listRelatives("mySphere", shapes=True)
history = cmds.listHistory("mySphere")
connections = cmds.listConnections("mySphere.translateX")

# ============================================================================
# ANIMATION - Keyframes and timeline
# ============================================================================
cmds.setKeyframe("mySphere", attribute="translateX", time=1, value=0)
cmds.setKeyframe("mySphere", attribute="translateX", time=24, value=10)
keys = cmds.keyframe("mySphere", query=True, keyframeCount=True)
cmds.currentTime(12)
cmds.playblast(filename="test", format="image", width=1920, height=1080)

# ============================================================================
# POLYGON OPERATIONS - Evaluate, Combine, Separate
# ============================================================================
face_count = cmds.polyEvaluate("mySphere", face=True)
vert_count = cmds.polyEvaluate("mySphere", vertex=True)
edge_count = cmds.polyEvaluate("mySphere", edge=True)

combined = cmds.polyUnite("pSphere1", "pCube1", name="combined")
separated = cmds.polySeparate("combined")

# ============================================================================
# PYMEL - Object-Oriented Approach (All should be highlighted!)
# ============================================================================

# PyMEL Selection - More pythonic than cmds
selected_nodes = pm.selected()
sphere_node = pm.PyNode("mySphere")

# PyMEL Creation - Returns PyNode objects
pm_sphere = pm.polySphere(radius=5)
pm_cube = pm.polyCube(width=3)
pm_cylinder = pm.polyCylinder(radius=2, height=5)

# PyMEL Hierarchy - Object methods instead of functions
children = sphere_node.getChildren()
parent = sphere_node.getParent()
shapes = sphere_node.getShapes()

# PyMEL Transforms - Direct attribute access
translation = sphere_node.getTranslation()
sphere_node.setTranslation([10, 5, 0])
rotation = sphere_node.getRotation()
sphere_node.setRotation([45, 0, 90])
scale = sphere_node.getScale()
sphere_node.setScale([2, 2, 2])

# PyMEL Attributes - Pythonic attribute access
sphere_node.translateX.set(10)
x_value = sphere_node.translateX.get()
sphere_node.visibility.set(True)

# PyMEL Mesh Operations - Object-oriented mesh queries
if isinstance(sphere_node.getShape(), pm.Mesh):
    mesh_shape = sphere_node.getShape()
    num_verts = mesh_shape.numVertices()
    num_faces = mesh_shape.numFaces()
    num_edges = mesh_shape.numEdges()

print("✅ All Maya cmds and PyMEL commands demonstrated!")
print("💡 Hover over any command to see detailed documentation!")
