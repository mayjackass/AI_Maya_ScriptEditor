# PyMEL Examples for NEO Script Editor

"""
PyMEL (Python in Maya Done Right) provides a more pythonic, object-oriented
interface to Maya compared to maya.cmds.

Key advantages:
- Object-oriented (nodes are objects, not strings)
- More intuitive attribute access
- Better type safety
- Cleaner syntax with operators
"""

import pymel.core as pm

# ===================================================================
# BASIC PYMEL vs CMDS COMPARISON
# ===================================================================

# --- Creating Objects ---
# cmds way:
# sphere = cmds.polySphere(name="mySphere")[0]

# PyMEL way (returns tuple of transform and shape):
sphere, sphere_shape = pm.polySphere(name="mySphere")
print(f"Created: {sphere} with shape: {sphere_shape}")

# ===================================================================
# SELECTION AND LISTING
# ===================================================================

# Get selected objects as PyNode objects
selected_objs = pm.selected()
print(f"Selected: {selected_objs}")

# List all meshes in scene
all_meshes = pm.ls(type='mesh')
print(f"Meshes: {all_meshes}")

# List transforms only
transforms = pm.ls(type='transform')

# ===================================================================
# ATTRIBUTE ACCESS (Most Pythonic Feature!)
# ===================================================================

# Get attribute value
x_position = sphere.tx.get()
print(f"Sphere X position: {x_position}")

# Set attribute value
sphere.tx.set(5.0)
sphere.ty.set(3.0)
sphere.tz.set(0.0)

# Get multiple attributes
translation = sphere.getTranslation()
print(f"Translation: {translation}")

# Set multiple attributes
sphere.setTranslation([10, 5, 2])

# ===================================================================
# ATTRIBUTE CONNECTIONS (Using >> Operator!)
# ===================================================================

# Create two spheres
sphere1, _ = pm.polySphere(name="sphere1")
sphere2, _ = pm.polySphere(name="sphere2")

# Connect attributes using >> operator (SO CLEAN!)
sphere1.tx >> sphere2.tx  # sphere2 follows sphere1's X position
sphere1.ty >> sphere2.ty
sphere1.tz >> sphere2.tz

# Disconnect using // operator
sphere1.tx // sphere2.tx

# Traditional way (also works)
pm.connectAttr(sphere1.tx, sphere2.tx)

# ===================================================================
# HIERARCHY OPERATIONS
# ===================================================================

# Get parent (returns PyNode or None)
parent_node = sphere.getParent()
print(f"Parent: {parent_node}")

# Get children (returns list of PyNodes)
children = sphere.getChildren()
print(f"Children: {children}")

# Get shape nodes
shapes = sphere.getShapes()
print(f"Shapes: {shapes}")

# Parent objects
cube, _ = pm.polyCube(name="myCube")
sphere.setParent(cube)  # PyMEL way
# or: pm.parent(sphere, cube)

# ===================================================================
# TRANSFORMATION OPERATIONS
# ===================================================================

# Get transformation
pos = sphere.getTranslation()
rot = sphere.getRotation()
scale = sphere.getScale()

print(f"Position: {pos}")
print(f"Rotation: {rot}")
print(f"Scale: {scale}")

# Set transformation (more intuitive than cmds.move, cmds.rotate)
sphere.setTranslation([5, 10, 3])
sphere.setRotation([0, 45, 0])
sphere.setScale([2, 2, 2])

# ===================================================================
# OBJECT CREATION
# ===================================================================

# Create various primitives
cube, _ = pm.polyCube(name="myCube", width=2, height=2, depth=2)
cylinder, _ = pm.polyCylinder(name="myCylinder", radius=1, height=3)
plane, _ = pm.polyPlane(name="myPlane", width=10, height=10)
torus, _ = pm.polyTorus(name="myTorus", radius=2, sectionRadius=0.5)

# Position them
cube.setTranslation([0, 0, 0])
cylinder.setTranslation([5, 0, 0])
plane.setTranslation([0, -2, 0])
torus.setTranslation([-5, 0, 0])

# ===================================================================
# WORKING WITH MESHES
# ===================================================================

# Get mesh info (PyMEL provides direct properties!)
mesh_shape = sphere.getShape()
num_verts = mesh_shape.numVertices()
num_faces = mesh_shape.numFaces()
num_edges = mesh_shape.numEdges()

print(f"Vertices: {num_verts}, Faces: {num_faces}, Edges: {num_edges}")

# Access vertices, faces, edges pythonically
vertices = mesh_shape.vtx[:]  # All vertices
faces = mesh_shape.f[:]       # All faces
edges = mesh_shape.e[:]       # All edges

# Select specific components
mesh_shape.vtx[0:5].select()  # Select first 5 vertices

# ===================================================================
# ANIMATION
# ===================================================================

# Set keyframes
pm.currentTime(1)
sphere.tx.set(0)
pm.setKeyframe(sphere, attribute='translateX')

pm.currentTime(24)
sphere.tx.set(10)
pm.setKeyframe(sphere, attribute='translateX')

# Query keyframes
keyframes = pm.keyframe(sphere, query=True, timeChange=True)
print(f"Keyframes at: {keyframes}")

# ===================================================================
# MODELING OPERATIONS
# ===================================================================

# Duplicate object
duplicated = pm.duplicate(sphere)
print(f"Duplicated: {duplicated}")

# Combine meshes
cube1, _ = pm.polyCube(name="cube1")
cube2, _ = pm.polyCube(name="cube2")
cube2.setTranslation([2, 0, 0])
combined, _ = pm.polyUnite(cube1, cube2, name="combined")

# Separate mesh
separated = pm.polySeparate(combined)
print(f"Separated into: {separated}")

# Delete objects
pm.delete(separated)

# ===================================================================
# PYMEL DATA TYPES
# ===================================================================

# Vector operations
from pymel.core.datatypes import Vector, Point, Matrix

vec1 = Vector(1, 2, 3)
vec2 = Vector(4, 5, 6)

# Vector math
vec_sum = vec1 + vec2
vec_dot = vec1.dot(vec2)
vec_cross = vec1.cross(vec2)
vec_length = vec1.length()

print(f"Vector sum: {vec_sum}")
print(f"Dot product: {vec_dot}")
print(f"Cross product: {vec_cross}")
print(f"Length: {vec_length}")

# Point in space
point = Point(5, 10, 3)
sphere.setTranslation(point)

# ===================================================================
# CHECKING OBJECT EXISTENCE
# ===================================================================

# Check if object exists
if pm.objExists("mySphere"):
    print("Sphere exists!")

# Check object type
if isinstance(sphere, pm.nt.Transform):
    print("It's a transform node!")

# ===================================================================
# LISTING ATTRIBUTES
# ===================================================================

# List all attributes
attrs = sphere.listAttr()
print(f"Attributes: {attrs[:10]}...")  # First 10

# List keyable attributes
keyable_attrs = sphere.listAttr(keyable=True)
print(f"Keyable attributes: {keyable_attrs}")

# ===================================================================
# CONVERTING BETWEEN STRINGS AND PYNODES
# ===================================================================

# String to PyNode
sphere_node = pm.PyNode("mySphere")
print(f"Got PyNode: {sphere_node}")

# PyNode to string
sphere_name = str(sphere)
print(f"Node name: {sphere_name}")

# ===================================================================
# PYMEL BEST PRACTICES
# ===================================================================

"""
1. Use PyNodes instead of strings whenever possible
2. Use .get()/.set() for attributes instead of getAttr/setAttr
3. Use >> operator for connecting attributes
4. Use .getChildren(), .getParent(), .getShapes() instead of listRelatives
5. Use object methods like .setTranslation() instead of cmds.move()
6. Store PyNode objects in variables for cleaner code
7. Use isinstance() to check node types
8. Use Vector and Point for 3D math operations
"""

# ===================================================================
# COMMON PYMEL PATTERNS
# ===================================================================

# Pattern 1: Process all selected objects
for obj in pm.selected():
    print(f"Processing: {obj}")
    obj.ty.set(obj.ty.get() + 1)  # Move up by 1 unit

# Pattern 2: Find and modify specific nodes
for mesh in pm.ls(type='mesh'):
    transform = mesh.getParent()
    if transform:
        transform.visibility.set(True)

# Pattern 3: Build hierarchy
root = pm.group(empty=True, name="root")
for i in range(5):
    cube, _ = pm.polyCube(name=f"cube_{i}")
    cube.setParent(root)
    cube.tx.set(i * 2)

# Pattern 4: Attribute connection chain
control = pm.circle(name="control")[0]
target1, _ = pm.polySphere(name="target1")
target2, _ = pm.polySphere(name="target2")
target3, _ = pm.polySphere(name="target3")

# Chain connections
control.tx >> target1.tx >> target2.tx >> target3.tx

print("\\n=== PyMEL Examples Complete! ===")
print("PyMEL makes Maya scripting more pythonic and intuitive!")
