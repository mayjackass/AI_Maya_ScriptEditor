"""
Hover Documentation System
Provides VS Code-style tooltips with syntax highlighting and intelligent code analysis
"""
import ast
import inspect
import re

# VS Code-style syntax colors (matching the actual editor theme)
COLORS = {
    'keyword': '#c586c0',      # Purple (def, class, if, for, etc.)
    'function': '#dcdcaa',     # Yellow (function names)
    'class': '#4ec9b0',        # Cyan (class names)
    'string': '#ce9178',       # Orange (strings)
    'number': '#b5cea8',       # Light green (numbers)
    'operator': '#d4d4d4',     # Light gray (operators)
    'parameter': '#9cdcfe',    # Light blue (parameters)
    'builtin': '#4ec9b0',      # Cyan (built-in types)
    'comment': '#6a9955',      # Green (comments)
    'default': '#d4d4d4',      # Default text color
}

# Python keywords documentation
PYTHON_KEYWORDS = {
    'def': ('keyword', 'Define a function'),
    'class': ('keyword', 'Define a class'),
    'if': ('keyword', 'Conditional statement'),
    'elif': ('keyword', 'Else if conditional'),
    'else': ('keyword', 'Else clause for conditionals and loops'),
    'for': ('keyword', 'For loop iteration'),
    'while': ('keyword', 'While loop'),
    'return': ('keyword', 'Return a value from a function'),
    'yield': ('keyword', 'Yield a value (generator)'),
    'import': ('keyword', 'Import a module'),
    'from': ('keyword', 'Import specific items from a module'),
    'as': ('keyword', 'Create an alias'),
    'try': ('keyword', 'Try block for exception handling'),
    'except': ('keyword', 'Catch and handle exceptions'),
    'finally': ('keyword', 'Code that runs regardless of exceptions'),
    'with': ('keyword', 'Context manager'),
    'lambda': ('keyword', 'Anonymous function expression'),
    'pass': ('keyword', 'Null operation (placeholder)'),
    'break': ('keyword', 'Exit the current loop'),
    'continue': ('keyword', 'Skip to next loop iteration'),
    'raise': ('keyword', 'Raise an exception'),
    'assert': ('keyword', 'Assert a condition is true'),
    'global': ('keyword', 'Declare a global variable'),
    'nonlocal': ('keyword', 'Declare a nonlocal variable'),
    'del': ('keyword', 'Delete an object'),
    'True': ('keyword', 'Boolean true constant'),
    'False': ('keyword', 'Boolean false constant'),
    'None': ('keyword', 'Null value constant'),
    'and': ('keyword', 'Logical AND operator'),
    'or': ('keyword', 'Logical OR operator'),
    'not': ('keyword', 'Logical NOT operator'),
    'in': ('keyword', 'Membership test operator'),
    'is': ('keyword', 'Identity test operator'),
    'async': ('keyword', 'Define an asynchronous function'),
    'await': ('keyword', 'Wait for an async operation'),
}

# Python built-in functions with signatures
PYTHON_BUILTINS = {
    'print': ('print(*objects, sep=" ", end="\\n", file=sys.stdout, flush=False)', 
              'Print objects to the text stream file, separated by sep and followed by end'),
    'len': ('len(obj, /)', 
            'Return the length (the number of items) of an object'),
    'range': ('range(stop) or range(start, stop[, step])', 
              'Return an immutable sequence of numbers from start to stop by step'),
    'str': ('str(object="") or str(object=b"", encoding="utf-8", errors="strict")', 
            'Create a new string object from the given object'),
    'int': ('int(x=0) or int(x, base=10)', 
            'Convert a number or string to an integer'),
    'float': ('float(x=0.0)', 
              'Convert a string or number to a floating point number'),
    'list': ('list() or list(iterable)', 
             'Create a mutable sequence, initialized from iterable if provided'),
    'dict': ('dict(**kwargs) or dict(mapping, **kwargs) or dict(iterable, **kwargs)', 
             'Create a new dictionary'),
    'set': ('set() or set(iterable)', 
            'Create a new set object, optionally with elements from iterable'),
    'tuple': ('tuple() or tuple(iterable)', 
              'Create a tuple, an immutable sequence'),
    'bool': ('bool(x=False)', 
             'Convert a value to a Boolean using the standard truth testing procedure'),
    'type': ('type(object) or type(name, bases, dict)', 
             'Return the type of an object or create a new type object'),
    'isinstance': ('isinstance(object, classinfo)', 
                   'Return True if object is an instance of classinfo'),
    'open': ('open(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None)', 
             'Open file and return a corresponding file object'),
    'input': ('input(prompt="")', 
              'Read a string from standard input'),
    'enumerate': ('enumerate(iterable, start=0)', 
                  'Return an enumerate object yielding (index, value) pairs'),
    'zip': ('zip(*iterables, strict=False)', 
            'Iterate over several iterables in parallel'),
    'map': ('map(function, iterable, ...)', 
            'Apply function to every item of iterable and return an iterator'),
    'filter': ('filter(function, iterable)', 
               'Construct an iterator from elements of iterable for which function returns true'),
    'sorted': ('sorted(iterable, /, *, key=None, reverse=False)', 
               'Return a new sorted list from the items in iterable'),
    'reversed': ('reversed(sequence)', 
                 'Return a reverse iterator over the values of sequence'),
    'sum': ('sum(iterable, /, start=0)', 
            'Return the sum of a start value plus an iterable of numbers'),
    'min': ('min(iterable, *[, key, default]) or min(arg1, arg2, *args[, key])', 
            'Return the smallest item in an iterable or the smallest of arguments'),
    'max': ('max(iterable, *[, key, default]) or max(arg1, arg2, *args[, key])', 
            'Return the largest item in an iterable or the largest of arguments'),
    'abs': ('abs(x)', 
            'Return the absolute value of a number'),
    'round': ('round(number, ndigits=None)', 
              'Round a number to a given precision in decimal digits'),
    'pow': ('pow(base, exp, mod=None)', 
            'Return base to the power exp; if mod is present, return base**exp % mod'),
    'all': ('all(iterable)', 
            'Return True if all elements of the iterable are true'),
    'any': ('any(iterable)', 
            'Return True if any element of the iterable is true'),
    'dir': ('dir(object)', 
            'Return a list of valid attributes for the object'),
    'help': ('help(object)', 
             'Invoke the built-in help system'),
    'vars': ('vars(object)', 
             'Return the __dict__ attribute for a module, class, instance, or any object'),
    'locals': ('locals()', 
               'Update and return a dictionary representing the current local symbol table'),
    'globals': ('globals()', 
                'Return the dictionary containing the current global symbol table'),
    'hasattr': ('hasattr(object, name)', 
                'Return True if the object has the named attribute'),
    'getattr': ('getattr(object, name, default=None)', 
                'Get a named attribute from an object'),
    'setattr': ('setattr(object, name, value)', 
                'Set a named attribute on an object'),
    'delattr': ('delattr(object, name)', 
                'Delete a named attribute from an object'),
    'callable': ('callable(object)', 
                 'Return True if the object appears callable'),
    'format': ('format(value, format_spec="")', 
               'Return value formatted according to format_spec'),
}

# String/List/Dict methods
BUILTIN_METHODS = {
    'join': ('str.join(iterable)', 
             'Concatenate strings in iterable with separator string'),
    'split': ('str.split(sep=None, maxsplit=-1)', 
              'Return a list of the words in the string, using sep as delimiter'),
    'replace': ('str.replace(old, new, count=-1)', 
                'Return a copy with all occurrences of old replaced by new'),
    'strip': ('str.strip(chars=None)', 
              'Return a copy with leading and trailing characters removed'),
    'upper': ('str.upper()', 
              'Return a copy of the string converted to uppercase'),
    'lower': ('str.lower()', 
              'Return a copy of the string converted to lowercase'),
    'startswith': ('str.startswith(prefix, start=0, end=len(string))', 
                   'Return True if string starts with the prefix'),
    'endswith': ('str.endswith(suffix, start=0, end=len(string))', 
                 'Return True if the string ends with the suffix'),
    'append': ('list.append(object)', 
               'Add an item to the end of the list'),
    'extend': ('list.extend(iterable)', 
               'Extend list by appending elements from the iterable'),
    'insert': ('list.insert(index, object)', 
               'Insert object before index'),
    'remove': ('list.remove(value)', 
               'Remove first occurrence of value'),
    'pop': ('list.pop(index=-1)', 
            'Remove and return item at index (default last)'),
    'keys': ('dict.keys()', 
             'Return a new view of the dictionary\'s keys'),
    'values': ('dict.values()', 
               'Return a new view of the dictionary\'s values'),
    'items': ('dict.items()', 
              'Return a new view of the dictionary\'s items (key-value pairs)'),
    'get': ('dict.get(key, default=None)', 
            'Return the value for key if key is in dictionary, else default'),
    'update': ('dict.update(other)', 
               'Update the dictionary with key/value pairs from other'),
}

# PySide6/Qt documentation
QT_DOCS = {
    'QtWidgets': ('module', 'PySide6.QtWidgets - Classes for creating classic desktop-style UIs'),
    'QtCore': ('module', 'PySide6.QtCore - Core non-GUI functionality'),
    'QtGui': ('module', 'PySide6.QtGui - GUI components and event handling'),
    'QWidget': ('class QWidget(parent: QWidget = None)', 
                'Base class for all UI objects in Qt'),
    'QMainWindow': ('class QMainWindow(parent: QWidget = None)', 
                    'Main application window with menu bar, toolbars, status bar, and dockable widgets'),
    'QPushButton': ('class QPushButton(text: str = "", parent: QWidget = None)', 
                    'Command button widget'),
    'QLabel': ('class QLabel(text: str = "", parent: QWidget = None)', 
               'Text or image display widget'),
    'QLineEdit': ('class QLineEdit(contents: str = "", parent: QWidget = None)', 
                  'Single line text editor widget'),
    'QTextEdit': ('class QTextEdit(text: str = "", parent: QWidget = None)', 
                  'Multi-line rich text editor widget'),
    'QVBoxLayout': ('class QVBoxLayout(parent: QWidget = None)', 
                    'Lines up widgets vertically'),
    'QHBoxLayout': ('class QHBoxLayout(parent: QWidget = None)', 
                    'Lines up widgets horizontally'),
    'QApplication': ('class QApplication(argv: List[str])', 
                     'Manages GUI application\'s control flow and main settings'),
    'Signal': ('class Signal(*types)', 
               'Define a signal for inter-object communication'),
    'Slot': ('Slot(*types)', 
             'Decorator to define a slot that can receive signals'),
}

# Maya commands - Comprehensive Maya cmds documentation
MAYA_DOCS = {
    # Core modules
    'cmds': ('module maya.cmds', 
             'Maya Commands module - Procedural interface to Maya. All Maya operations available as functions.'),
    'mel': ('module maya.mel', 
            'Execute MEL commands from Python using mel.eval("MEL code")'),
    'pm': ('module pymel.core', 
           'PyMEL core - Object-oriented, Pythonic interface to Maya with automatic type conversion'),
    'pymel': ('module pymel', 
              'PyMEL - Python in Maya Done Right. Wraps Maya commands with Python classes and proper return types'),
    'OpenMaya': ('module maya.api.OpenMaya', 
                 'Maya Python API 2.0 - High-performance low-level API for advanced Maya scripting and plugins'),
    'OpenMayaUI': ('module maya.api.OpenMayaUI', 
                   'Maya API for UI and viewport manipulation - Access to Maya\'s UI elements and 3D viewport'),
    
    # Creation commands (Polygon primitives)
    'polySphere': ('cmds.polySphere(radius=1.0, sx=20, sy=20, ax=[0,1,0], cuv=2, ch=1, name="")', 
                   'Create polygonal sphere. Returns [transform, polySphere_node]. Use for basic sphere geometry.'),
    'polyCube': ('cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=[0,1,0], cuv=4, ch=1, name="")', 
                 'Create polygonal cube. Returns [transform, polyCube_node]. Basic box primitive for modeling.'),
    'polyCylinder': ('cmds.polyCylinder(r=1, h=2, sx=20, sy=1, sz=1, ax=[0,1,0], rcp=0, cuv=3, ch=1, name="")',
                     'Create polygonal cylinder. Returns [transform, polyCylinder_node]. Useful for columns, tubes, pipes.'),
    'polyPlane': ('cmds.polyPlane(w=1, h=1, sx=10, sy=10, ax=[0,1,0], cuv=2, ch=1, name="")',
                  'Create polygonal plane. Returns [transform, polyPlane_node]. Flat surface for floors, terrain, etc.'),
    'polyTorus': ('cmds.polyTorus(r=1, sr=0.5, tw=0, sx=20, sy=20, ax=[0,1,0], cuv=1, ch=1, name="")',
                  'Create polygonal torus (donut shape). Returns [transform, polyTorus_node].'),
    'polyCone': ('cmds.polyCone(r=1, h=2, sx=20, sy=1, sz=0, ax=[0,1,0], rcp=0, cuv=3, ch=1, name="")',
                 'Create polygonal cone. Returns [transform, polyCone_node]. Pyramid or cone shapes.'),
    'polyPyramid': ('cmds.polyPyramid(w=1, ns=4, sc=0, ax=[0,1,0], cuv=1, ch=1, name="")',
                    'Create polygonal pyramid. Returns [transform, polyPyramid_node]. Multi-sided pyramid primitive.'),
    'polyPipe': ('cmds.polyPipe(r=1, h=2, t=0.5, sa=20, sh=1, sc=0, ax=[0,1,0], rcp=0, cuv=1, ch=1, name="")',
                 'Create polygonal pipe (hollow cylinder). Returns [transform, polyPipe_node].'),
    
    # Selection commands
    'select': ('cmds.select(*objects, r=True, add=False, d=False, ne=True, all=False, hi=False, cl=False)', 
               'Select objects in scene. r=replace, add=add to selection, d=deselect, all=select all, cl=clear selection.'),
    'ls': ('cmds.ls(selection=True, type=None, long=False, dag=False, shapes=False, transforms=False)', 
           'List objects in scene. Query scene objects by type, name pattern, or get current selection. Essential for object queries.'),
    'filterExpand': ('cmds.filterExpand(selectionList, sm=None, ex="", fp=False)',
                     'Expand selection list to include components. sm: selection mask (31=vertices, 32=edges, 34=faces).'),
    'listRelatives': ('cmds.listRelatives(object, p=False, c=False, s=False, f=False, type=None)',
                      'List relatives of object. p=parent, c=children, s=shapes, f=fullPath. Returns hierarchy relationships.'),
    'listHistory': ('cmds.listHistory(object, future=False, pdo=True, lf=True, il=2)',
                    'List dependency graph history. Shows construction history nodes. future=downstream, pdo=pruneDagObjects.'),
    'listConnections': ('cmds.listConnections(attribute, s=True, d=True, type=None, c=False)',
                        'List node connections. Query what\'s connected to attributes. s=source, d=destination, c=return connections.'),
    
    # Attribute commands
    'setAttr': ('cmds.setAttr("node.attribute", value, type=None, clamp=False, lock=False)', 
                'Set attribute value. type: "double3" for vectors, "string" for text. Essential for animation keyframing.'),
    'getAttr': ('cmds.getAttr("node.attribute", time=None, asString=False)', 
                'Get attribute value. Returns current value or value at specific time. Use for querying object properties.'),
    'addAttr': ('cmds.addAttr(node, ln="attrName", at="double", min=0, max=1, dv=0, k=True, h=False)',
                'Add custom attribute. ln=longName, at=attributeType, dv=defaultValue, k=keyable, h=hidden.'),
    'deleteAttr': ('cmds.deleteAttr("node.attribute")',
                   'Delete custom attribute from node. Cannot delete built-in attributes.'),
    'listAttr': ('cmds.listAttr(node, k=False, cb=False, s=False, r=False, w=False, c=False, ud=False)',
                 'List node attributes. k=keyable, cb=channelBox, s=scalar, ud=userDefined, w=writable.'),
    'attributeExists': ('cmds.attributeExists("attribute", "node")',
                        'Check if attribute exists on node. Returns True/False. Use before getAttr/setAttr.'),
    'connectAttr': ('cmds.connectAttr("source.attr", "dest.attr", f=False, na=False)',
                    'Connect attributes. f=force (break existing), na=nextAvailable (for multi attrs). Creates dependency.'),
    'disconnectAttr': ('cmds.disconnectAttr("source.attr", "dest.attr")',
                       'Disconnect attributes. Breaks dependency connection between nodes.'),
    
    # Transform commands
    'move': ('cmds.move(x, y, z, objects, r=False, os=False, ws=False, wd=False, a=False)',
             'Move objects. r=relative, os=objectSpace, ws=worldSpace, wd=worldSpaceDistance, a=absolute.'),
    'rotate': ('cmds.rotate(x, y, z, objects, r=False, os=False, ws=False, fo=False, a=False, eu=True)',
               'Rotate objects. Angles in degrees. os=objectSpace, ws=worldSpace, fo=forceOrderXYZ, eu=euler.'),
    'scale': ('cmds.scale(x, y, z, objects, r=False, os=False, cs=False, p=[0,0,0], a=False)',
              'Scale objects. r=relative, os=objectSpace, cs=componentSpace, p=pivot, a=absolute.'),
    'xform': ('cmds.xform(object, q=True, ws=False, os=False, t=True, ro=True, s=True, piv=True, m=True)',
              'Query/set transformations. q=query, t=translation, ro=rotation, s=scale, m=matrix. Versatile transform tool.'),
    'makeIdentity': ('cmds.makeIdentity(objects, apply=True, t=True, r=True, s=True, n=0, pn=True)',
                     'Freeze transformations. Resets transform values to 0,0,0 while maintaining appearance. Essential before rigging.'),
    
    # Hierarchy commands  
    'parent': ('cmds.parent(child, parent, add=False, r=False, s=False, nc=False, w=False)',
               'Parent objects. w=world (unparent), r=relative, s=shape, add=add to existing parents.'),
    'group': ('cmds.group(*objects, em=True, n="group1", w=False, p=None, r=False)',
              'Create group node. em=empty group, w=world, p=parent. Organizes scene hierarchy.'),
    'unparent': ('cmds.parent(object, w=True)',
                 'Remove parent (move to world). Same as parent with world=True flag.'),
    'instance': ('cmds.instance(object, n="", lf=True, st="transform")',
                 'Create instance of object. Shares shape node. Changes to original affect instances.'),
    'duplicate': ('cmds.duplicate(object, n="", rr=False, un=False, ic=False, po=False, rc=False)', 
                  'Duplicate objects. rr=returnRootsOnly, un=upstreamNodes, ic=inputConnections, po=parentOnly.'),
    
    # Scene commands
    'delete': ('cmds.delete(*objects, ch=False, hi="none", s=False, e=True, cn=True)', 
               'Delete objects. ch=constructionHistory, hi=hierarchy, s=shape, e=expressions, cn=constraints.'),
    'rename': ('cmds.rename(object, "newName")',
               'Rename object. Returns new name. Maya may add numbers for uniqueness.'),
    'hide': ('cmds.hide(*objects)',
             'Hide objects (set visibility=False). Objects remain in scene but invisible.'),
    'show': ('cmds.show(*objects)',
             'Show hidden objects (set visibility=True). Makes objects visible.'),
    'objExists': ('cmds.objExists("nodeName")',
                  'Check if object exists. Returns True/False. Use before operations on named nodes.'),
    
    # Node/Type queries
    'createNode': ('cmds.createNode("nodeType", n="", p=None, s=False, ss=False)', 
                   'Create dependency node. nodeType: "transform", "mesh", "joint", etc. Low-level node creation.'),
    'nodeType': ('cmds.nodeType(node, api=False, i=False)',
                 'Get node type string. api=API type number, i=inherited types. Returns node class name.'),
    'objectType': ('cmds.objectType(object, i="", isa=False)',
                   'Check object type. isa=check inheritance. Returns True/False or type string.'),
    
    # Animation commands
    'keyframe': ('cmds.keyframe(attribute, q=True, sl=True, t=(start,end), fc=0, vc=0, kc=0)',
                 'Query/set keyframes. q=query, t=time range, fc=floatChange, vc=valueChange, kc=keyframeCount.'),
    'setKeyframe': ('cmds.setKeyframe(attribute, t=None, v=None, bd=True, hi="none", cp=True, s=False)',
                    'Set keyframe. t=time, v=value, bd=breakdown, hi=hierarchy, cp=controlPoints, s=shape.'),
    'currentTime': ('cmds.currentTime(time, e=True, u=True)',
                    'Get/set timeline time. e=edit, u=update. Returns current frame or sets playback position.'),
    'playblast': ('cmds.playblast(f="", fmt="", st=1, et=100, v=True, p=100, w=1920, h=1080)',
                  'Create playblast. f=filename, fmt=format, st=startTime, et=endTime, w=width, h=height.'),
    
    # Polygon operations
    'polyEvaluate': ('cmds.polyEvaluate(object, f=True, e=True, v=True, t=True, uvs=True)',
                     'Get polygon stats. f=faces, e=edges, v=vertices, t=triangles, uvs=UV count.'),
    'polyUnite': ('cmds.polyUnite(*objects, ch=True, mergeUVSets=1, n="")',
                  'Combine polygon objects. ch=history, mergeUVSets. Returns combined object.'),
    'polySeparate': ('cmds.polySeparate(object, ch=True)',
                     'Separate polygon shells. Splits multi-shell mesh into separate objects.'),
    
    # Shading and Materials - CRITICAL for Maya workflows
    'shadingNode': ('cmds.shadingNode("nodeType", asShader=True, asTexture=False, asLight=False, asUtility=False, name="")',
                    'Create shading node. asShader: lambert/blinn/phong. asTexture: file/checker. asUtility: bump/reverse. Essential for materials.'),
    'sets': ('cmds.sets(*objects, renderable=True, noSurfaceShader=False, empty=False, name="", add=False, remove=False)',
             'Create/edit shading group (material assignment). renderable=True for shading groups. Use with shadingNode and connectAttr.'),
    'hyperShade': ('cmds.hyperShade(assign="material", objects=[])',
                   'Assign material to objects. assign=material name. Alternative: cmds.sets(objects, e=True, forceElement="materialSG").'),
    'shadingConnection': ('cmds.shadingConnection(cs=True, sn="")',
                          'Query shading connections. cs=connectionState, sn=shadingNode. Returns connected shading groups.'),
    'defaultNavigation': ('cmds.defaultNavigation(source="", destination="", ce=True, force=True)',
                          'Connect shading nodes. ce=connectToExisting. Use for .outColor to .surfaceShader connections.'),
    
    # Material node types (for shadingNode)
    'lambert': ('material type', 'Basic diffuse material. No specular highlights. Fastest render. Use shadingNode("lambert", asShader=True).'),
    'blinn': ('material type', 'Shiny material with specular. Good for plastics, glass. shadingNode("blinn", asShader=True).'),
    'phong': ('material type', 'High specular material. Sharp highlights. Good for metals. shadingNode("phong", asShader=True).'),
    'phongE': ('material type', 'Phong with enhanced controls. More realistic specularity. shadingNode("phongE", asShader=True).'),
    'standardSurface': ('material type', 'Physically-based shader (Arnold). Industry standard PBR material. shadingNode("standardSurface", asShader=True).'),
    'aiStandardSurface': ('material type', 'Arnold standard surface. Full PBR with metalness, roughness, transmission. shadingNode("aiStandardSurface", asShader=True).'),
    
    # Texture nodes
    'file': ('texture type', 'Image file texture. Load PNG/JPG/EXR. shadingNode("file", asTexture=True). Connect .outColor to material.'),
    'checker': ('texture type', 'Procedural checker pattern. shadingNode("checker", asTexture=True). Useful for UV testing.'),
    'noise': ('texture type', 'Procedural noise texture. shadingNode("noise", asTexture=True). For bump, displacement, variation.'),
    'ramp': ('texture type', 'Gradient ramp texture. shadingNode("ramp", asTexture=True). Color/opacity gradients.'),
    'fractal': ('texture type', 'Fractal noise pattern. shadingNode("fractal", asTexture=True). Natural variation, clouds.'),
    
    # Utility nodes  
    'bump2d': ('utility type', 'Bump map converter. shadingNode("bump2d", asUtility=True). Connect texture to .bumpValue, output to material.bumpMap.'),
    'place2dTexture': ('utility type', 'UV coordinate node. Auto-created with textures. Controls tiling, offset, rotation of 2D textures.'),
    'reverse': ('utility type', 'Invert values. shadingNode("reverse", asUtility=True). outputX = 1 - inputX. For masks.'),
    'multiplyDivide': ('utility type', 'Math operations. shadingNode("multiplyDivide", asUtility=True). operation: 1=multiply, 2=divide, 3=power.'),
    'blendColors': ('utility type', 'Blend between colors. shadingNode("blendColors", asUtility=True). blender=0-1 interpolation.'),
    'condition': ('utility type', 'Conditional logic. shadingNode("condition", asUtility=True). If firstTerm operation secondTerm, output colorIfTrue else colorIfFalse.'),
    'clamp': ('utility type', 'Clamp values to range. shadingNode("clamp", asUtility=True). min/max limits. Prevents values going out of bounds.'),
    'remapValue': ('utility type', 'Remap value range. shadingNode("remapValue", asUtility=True). inputMin/Max to outputMin/Max with curve control.'),
    'luminance': ('utility type', 'Convert color to grayscale. shadingNode("luminance", asUtility=True). Weighted RGB to luminance.'),
    
    # Lights
    'pointLight': ('cmds.pointLight(name="", intensity=1.0, color=[1,1,1], decay=2, rgb=[1,1,1])',
                   'Create point light (omni). Radiates in all directions. decay: 0=none, 1=linear, 2=quadratic (realistic).'),
    'spotLight': ('cmds.spotLight(name="", intensity=1.0, color=[1,1,1], coneAngle=40, penumbra=0, decay=2)',
                  'Create spot light. Directional cone. coneAngle=spread, penumbra=edge softness. For focused lighting.'),
    'directionalLight': ('cmds.directionalLight(name="", intensity=1.0, color=[1,1,1], rgb=[1,1,1])',
                         'Create directional light (sun). Parallel rays. Infinite distance. For outdoor scenes, key lights.'),
    'ambientLight': ('cmds.ambientLight(name="", intensity=0.5, color=[1,1,1], rgb=[1,1,1])',
                     'Create ambient light. Flat, non-directional fill. Use sparingly. Better to use area/sky lights.'),
    'areaLight': ('cmds.areaLight(name="", intensity=1.0, color=[1,1,1], decay=2)',
                  'Create area light. Soft shadows. More realistic. Slower render. Good for interior lighting.'),
    
    # Rendering
    'render': ('cmds.render(camera="", layer="", x=1920, y=1080)',
               'Render current frame. camera=camera name. x/y=resolution. Returns image path.'),
    'renderWindowEditor': ('cmds.renderWindowEditor(q=True, writeImage="")',
                           'Render window control. writeImage=save path. Query/edit render view settings.'),
    'arnoldRender': ('cmds.arnoldRender(camera="", width=1920, height=1080)',
                     'Arnold render. Physically-based renderer. Industry standard for film/VFX.'),
}

# PyMEL-specific documentation (object-oriented approach) - COMPREHENSIVE
PYMEL_DOCS = {
    # Core PyMEL functions
    'selected': ('pm.selected() -> List[PyNode]', 
                 'Get currently selected objects as PyNode list. More pythonic than cmds.ls(sl=True). Returns empty list if nothing selected.'),
    'PyNode': ('pm.PyNode("nodeName") -> PyNode', 
               'Convert string to PyNode object. Enables object-oriented access to any Maya node. Raises error if node doesn\'t exist.'),
    
    # PyMEL object creation (returns tuple of transform and shape)
    'polySphere': ('pm.polySphere(name="", radius=1.0, **kwargs) -> Tuple[Transform, polySphere]',
                   'Create polygon sphere. Returns (transform_node, shape_node) tuple. Object-oriented alternative to cmds.polySphere.'),
    'polyCube': ('pm.polyCube(name="", width=1.0, height=1.0, depth=1.0) -> Tuple[Transform, polyCube]',
                 'Create polygon cube. Returns (transform, shape) tuple. Use result[0] for transform node.'),
    'polyCylinder': ('pm.polyCylinder(name="", radius=1.0, height=2.0, **kwargs) -> Tuple[Transform, polyCylinder]', 
                     'Create polygon cylinder. Returns (transform_node, shape_node) tuple. Pythonic creation method.'),
    'polyPlane': ('pm.polyPlane(name="", width=1.0, height=1.0, **kwargs) -> Tuple[Transform, polyPlane]', 
                  'Create polygon plane. Returns (transform_node, shape_node) tuple. For floors, terrain.'),
    'polyTorus': ('pm.polyTorus(name="", radius=1.0, sectionRadius=0.5, **kwargs) -> Tuple[Transform, polyTorus]', 
                  'Create polygon torus. Returns (transform_node, shape_node) tuple. Donut shape primitive.'),
    
    # PyMEL shading - Critical for materials
    'shadingNode': ('pm.shadingNode("nodeType", asShader=True, asTexture=False, asUtility=False, name="")',
                    'Create shading node (PyMEL). Returns PyNode. asShader: lambert/blinn. asTexture: file/checker. asUtility: bump/reverse.'),
    'sets': ('pm.sets(*objects, renderable=True, noSurfaceShader=False, empty=False, name="")',
             'Create shading group (PyMEL). Returns PyNode of set. Use with shadingNode for material assignment.'),
    'hyperShade': ('pm.hyperShade(assign="material")',
                   'Assign material (PyMEL). Cleaner: pm.sets(obj, e=True, forceElement=matSG).'),
    
    # PyMEL node types
    'Transform': ('class Transform(PyNode)', 
                  'Transform node with position, rotation, scale. Access attributes: node.tx.get(), node.ry.set(45). Pythonic attribute access.'),
    'Mesh': ('class Mesh(PyNode)', 
             'Polygon mesh shape node. Methods: numVertices(), numFaces(), getPoints(). Access components pythonically.'),
    'Camera': ('class Camera(PyNode)', 
               'Camera node. Methods: getFocalLength(), setFocalLength(). Control view frustum, film back, clipping planes.'),
    'Joint': ('class Joint(Transform)', 
              'Skeletal joint node for rigging. Inherits from Transform. Additional attributes: radius, preferredAngle, jointOrient.'),
    
    # PyMEL attribute operations
    'Attribute': ('class Attribute', 
                  'Node attribute wrapper. Methods: get(), set(), connect(dest), disconnect(). Pythonic attr >> dest for connections.'),
    'connectAttr': ('sourceAttr >> targetAttr', 
                    'Connect attributes (PyMEL). Use >> operator: sphere.tx >> cube.tx. More pythonic than cmds.connectAttr.'),
    'disconnectAttr': ('sourceAttr // targetAttr', 
                       'Disconnect attributes (PyMEL). Use // operator. Cleaner syntax than cmds.disconnectAttr.'),
    
    # PyMEL hierarchy operations
    'getChildren': ('node.getChildren(type=None, allDescendents=False) -> List[PyNode]', 
                    'Get child nodes. type="transform" filters by type. allDescendents=True for full hierarchy. Returns PyNode list.'),
    'getParent': ('node.getParent() -> PyNode', 
                  'Get parent node. Returns None if no parent (world). Single parent only in most cases.'),
    'getShapes': ('node.getShapes(noIntermediate=True) -> List[PyNode]', 
                  'Get shape nodes under transform. noIntermediate=True filters out intermediate shapes. Returns Mesh, NurbsCurve, etc.'),
    
    # PyMEL transform operations
    'getTranslation': ('node.getTranslation(space="world") -> Vector', 
                       'Get position. space: "world", "object". Returns MVector with x,y,z. Pythonic alternative to getAttr translateX/Y/Z.'),
    'setTranslation': ('node.setTranslation(vector, space="world")', 
                       'Set position. Pass [x,y,z] or Vector. space: "world", "object". Pythonic setAttr for position.'),
    'getRotation': ('node.getRotation(space="world") -> EulerRotation', 
                    'Get rotation in degrees. Returns EulerRotation with x,y,z. space: "world", "object".'),
    'setRotation': ('node.setRotation(rotation, space="world")', 
                    'Set rotation. Pass [x,y,z] or EulerRotation. Values in degrees. space: "world", "object".'),
    'getScale': ('node.getScale() -> [float, float, float]', 
                 'Get scale values. Returns list [x,y,z]. Object space only (scale is always local).'),
    'setScale': ('node.setScale([x, y, z])', 
                 'Set scale values. Pass list [x,y,z]. Object space. Uniform scale: setScale([2,2,2]).'),
    
    # PyMEL mesh operations  
    'numVertices': ('mesh.numVertices() -> int', 
                    'Get vertex count. Mesh shape method. Faster than polyEvaluate. Part of PyMEL Mesh API.'),
    'numFaces': ('mesh.numFaces() -> int', 
                 'Get face count. Mesh shape method. Polygon count for mesh. Pythonic query.'),
    'numEdges': ('mesh.numEdges() -> int', 
                 'Get edge count. Mesh shape method. Edge count for mesh topology.'),
    'getPoints': ('mesh.getPoints(space="world") -> List[Point]',
                  'Get all vertex positions. Returns MPointArray. space: "world", "object". For mesh deformation.'),
    'setPoints': ('mesh.setPoints(pointArray, space="world")',
                  'Set all vertex positions. Pass MPointArray or list of [x,y,z]. For custom deformers.'),
    
    # PyMEL utility
    'listAttr': ('node.listAttr(keyable=False, userDefined=False) -> List[Attribute]',
                 'List attributes. Returns Attribute objects. keyable=True for animatable. userDefined=True for custom attrs.'),
}

# OpenMaya API 2.0 - COMPREHENSIVE Low-level API Documentation  
# This is CRITICAL for advanced Maya scripting, plugins, and high-performance operations
OPENMAYA_DOCS = {
    # Core API classes - Foundation
    'MObject': ('class MObject', 
                'Handle to Maya dependency graph node. Lightweight reference. Use with MFn function sets. Core API object handle.'),
    'MDagPath': ('class MDagPath', 
                 'Path to DAG (Directed Acyclic Graph) node. Full path from world root. Use for transforms, shapes. More efficient than MObject for DAG nodes.'),
    'MSelectionList': ('class MSelectionList', 
                       'List of selected objects. Add by name, get MDagPath/MObject. Core selection interface: MGlobal.getActiveSelectionList().'),
    'MFnBase': ('class MFnBase', 
                'Base class for all function sets. Function sets operate on MObjects. MFn classes wrap MObject with typed methods.'),
    
    # Function Sets - MFn classes for typed node access
    'MFnDependencyNode': ('class MFnDependencyNode(MObject)', 
                          'Access dependency graph nodes. Get/set attributes, find plugs, query connections. Works on any node type.'),
    'MFnDagNode': ('class MFnDagNode(MDagPath or MObject)', 
                   'Access DAG nodes. Get parent/child, transformation, world matrices. Inherits MFnDependencyNode.'),
    'MFnTransform': ('class MFnTransform(MDagPath or MObject)', 
                     'Access transform nodes. Get/set translation, rotation, scale. Most common for object manipulation.'),
    'MFnMesh': ('class MFnMesh(MDagPath or MObject)', 
                'Access polygon mesh data. Get/set vertices, faces, normals, UVs. High-performance mesh operations.'),
    'MFnNurbsCurve': ('class MFnNurbsCurve(MDagPath or MObject)', 
                      'Access NURBS curve data. Get/set CVs, knots, degree. For curves and hair.'),
    'MFnNurbsSurface': ('class MFnNurbsSurface(MDagPath or MObject)', 
                        'Access NURBS surface data. Patch-based surfaces. Less common than polygons.'),
    'MFnCamera': ('class MFnCamera(MDagPath or MObject)', 
                  'Access camera nodes. Get/set focal length, film back, clipping planes. For viewport and rendering.'),
    'MFnLight': ('class MFnLight(MDagPath or MObject)', 
                 'Access light nodes. Base class for all lights. Get/set intensity, color, decay.'),
    'MFnSkinCluster': ('class MFnSkinCluster(MObject)', 
                       'Access skin cluster deformer. Get/set weights, influences. For character rigging.'),
    'MFnBlendShapeDeformer': ('class MFnBlendShapeDeformer(MObject)', 
                              'Access blend shape deformer. Get/set targets, weights. For facial animation.'),
    
    # Iterators - Efficient traversal of scene hierarchy
    'MItDag': ('class MItDag(MItDag.kBreadthFirst or kDepthFirst, MFn.kTransform)', 
               'Iterate DAG hierarchy. Filter by type. Efficient scene traversal. Use for batch operations on all objects.'),
    'MItDependencyNodes': ('class MItDependencyNodes(MFn.kNodeType)', 
                           'Iterate all dependency nodes of type. Non-DAG nodes included. For finding all nodes of specific type.'),
    'MItSelectionList': ('class MItSelectionList(MSelectionList)', 
                         'Iterate selection list. Get MDagPath/MObject for each. Process multi-selection efficiently.'),
    'MItMeshVertex': ('class MItMeshVertex(MDagPath or MObject)', 
                      'Iterate mesh vertices. Get/set positions, normals. Fast vertex operations.'),
    'MItMeshPolygon': ('class MItMeshPolygon(MDagPath or MObject)', 
                       'Iterate mesh faces. Get vertices, edges, normals, area. Face-level operations.'),
    'MItMeshEdge': ('class MItMeshEdge(MDagPath or MObject)', 
                    'Iterate mesh edges. Get connected faces, vertices. Edge-level operations.'),
    'MItGeometry': ('class MItGeometry(MDagPath or MObject)', 
                    'Iterate geometry points. Works on all deformable geometry. For custom deformers.'),
    'MItCurveCV': ('class MItCurveCV(MDagPath or MObject)', 
                   'Iterate curve CVs (control vertices). Get/set CV positions. Curve editing.'),
    'MItSurfaceCV': ('class MItSurfaceCV(MDagPath or MObject)', 
                     'Iterate NURBS surface CVs. 2D parameter space. Surface editing.'),
    
    # Data Types - Containers for geometry data
    'MPoint': ('class MPoint(x, y, z, w=1.0)', 
               'Homogeneous point (x,y,z,w). Used for 3D positions. w=1 for points, w=0 for vectors.'),
    'MVector': ('class MVector(x, y, z)', 
                'Direction vector. Math operations: +, -, *, /, dot, cross, normalize(). No w component.'),
    'MFloatVector': ('class MFloatVector(x, y, z)', 
                     'Float precision vector. Faster than MVector. Use for normals, colors.'),
    'MMatrix': ('class MMatrix', 
                '4x4 transformation matrix. Combines translate, rotate, scale. Matrix multiplication for transforms.'),
    'MTransformationMatrix': ('class MTransformationMatrix(MMatrix)', 
                              'Decomposed transformation. Extract translation, rotation, scale separately. Easier than raw matrix.'),
    'MColor': ('class MColor(r, g, b, a=1.0)', 
               'RGBA color (0-1 range). Used for vertex colors, materials.'),
    'MPointArray': ('class MPointArray', 
                    'Array of MPoints. Efficient bulk storage. Used by MFnMesh.getPoints().'),
    'MVectorArray': ('class MVectorArray', 
                     'Array of MVectors. Normals, velocities. Used by MFnMesh.getNormals().'),
    'MIntArray': ('class MIntArray', 
                  'Array of integers. Face/vertex indices. Used by MFnMesh.getVertices().'),
    'MFloatArray': ('class MFloatArray', 
                    'Array of floats. Weights, UVs. Used by MFnSkinCluster.getWeights().'),
    
    # Plugs and Attributes - Node attribute access
    'MPlug': ('class MPlug', 
              'Connection to node attribute. Get/set values, make/break connections. Low-level attribute access.'),
    'MFnAttribute': ('class MFnAttribute(MObject)', 
                     'Function set for attributes. Query attribute properties, type, default value.'),
    'MFnNumericAttribute': ('class MFnNumericAttribute(MObject)', 
                            'Numeric attributes. Int, float, double, bool. Create custom attributes.'),
    'MFnTypedAttribute': ('class MFnTypedAttribute(MObject)', 
                          'Typed attributes. String, matrix, mesh data. Complex data types.'),
    'MFnCompoundAttribute': ('class MFnCompoundAttribute(MObject)', 
                             'Compound attributes. Parent of child attributes. E.g., translate has translateX/Y/Z.'),
    
    # Messages and Callbacks - Event notification
    'MMessage': ('class MMessage', 
                 'Base message class. Register callbacks for Maya events. Scene changes, selection, time.'),
    'MNodeMessage': ('class MNodeMessage', 
                     'Node-specific messages. attributeChanged, nameChanged. Track node modifications.'),
    'MEventMessage': ('class MEventMessage', 
                      'Global event messages. timeChanged, selectionChanged, sceneUpdate. App-level events.'),
    'MDGMessage': ('class MDGMessage', 
                   'Dependency graph messages. Node added/removed, connection made/broken. DG modifications.'),
    'MModelMessage': ('class MModelMessage', 
                      'Model messages. Before/after create, delete, duplicate. Geometry operations.'),
    'MAnimMessage': ('class MAnimMessage', 
                     'Animation messages. Keyframe added/removed, animation curve changed. Animation events.'),
    
    # Utility Classes
    'MGlobal': ('class MGlobal', 
                'Global utility functions. Get selection, execute commands, display info. Static methods only.'),
    'MFileIO': ('class MFileIO', 
                'File operations. Open, save, import, export, reference. Scene file management.'),
    'MScriptUtil': ('class MScriptUtil', 
                    'Pass Python values to API functions requiring pointers. Workaround for pointer arguments.'),
    'MArgList': ('class MArgList', 
                 'Command argument list. Parse command arguments in custom commands.'),
    'MArgDatabase': ('class MArgDatabase(MSyntax, MArgList)', 
                     'Argument parser. Flag-based argument parsing for commands.'),
    'MSyntax': ('class MSyntax', 
                'Command syntax definition. Define flags, arguments for custom commands.'),
    
    # Plugin Classes - For creating custom nodes and commands
    'MPxNode': ('class MPxNode', 
                'Base proxy node. Inherit to create custom nodes. Override compute() for calculations.'),
    'MPxCommand': ('class MPxCommand', 
                   'Base proxy command. Inherit for custom commands. Override doIt() for command logic.'),
    'MPxDeformerNode': ('class MPxDeformerNode(MPxNode)', 
                        'Custom deformer node. Override deform() to modify geometry. For custom deformations.'),
    'MPxLocatorNode': ('class MPxLocatorNode(MPxNode)', 
                       'Custom locator node. Override draw() for viewport display. Visual helpers.'),
    'MPxSurfaceShape': ('class MPxSurfaceShape', 
                        'Custom shape node. For custom geometry types. Advanced plugin development.'),
}


def format_signature_with_colors(signature):
    """
    Format a function/class signature with proper syntax highlighting colors.
    Uses QTextCharFormat like the code editor for consistent rendering.
    """
    if not signature:
        return ""
    
    # IMPORTANT: Return as plain text with color markers
    # The tooltip will apply colors using QTextCharFormat like the editor does
    # For now, return a simple code block that the QTextEdit can render
    
    import html as html_module
    import re
    
    # Escape HTML first
    signature_escaped = html_module.escape(signature)
    
    # Build HTML with inline styles (Qt supports limited CSS)
    # Use the SAME colors as the highlighter
    result = signature_escaped
    replacements = []
    
    # Define patterns with colors matching the highlighter
    patterns = [
        (r'\b(def|class|return|yield|if|elif|else|for|while|in|is|and|or|not|True|False|None|import|from|as)\b', '#c586c0'),  # Keywords - purple
        (r'\b([A-Z][a-zA-Z0-9_]*)\b', '#4ec9b0'),  # Class names - cyan
        (r'\b(str|int|float|bool|list|dict|set|tuple|object)\b', '#4ec9b0'),  # Built-in types - cyan
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()', '#dcdcaa'),  # Function names - yellow
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?==)', '#9cdcfe'),  # Parameters - light blue
        (r'([\[\]\(\)\{\},:])', '#d4d4d4'),  # Brackets and punctuation - light gray
        (r'(&quot;[^&]*&quot;|&#x27;[^&]*&#x27;)', '#ce9178'),  # Strings - orange
        (r'\b(\d+\.?\d*)\b', '#b5cea8'),  # Numbers - light green
    ]
    
    # Find all matches
    for pattern, color in patterns:
        for match in re.finditer(pattern, signature_escaped):
            if match.group(0):
                replacements.append((match.start(), match.end(), match.group(0), color))
    
    # Sort by position and remove overlaps (keep first match)
    replacements.sort(key=lambda x: x[0])
    final_replacements = []
    last_end = -1
    for start, end, text, color in replacements:
        if start >= last_end:
            final_replacements.append((start, end, text, color))
            last_end = end
    
    # Apply colors from end to start to preserve positions
    final_replacements.reverse()
    for start, end, text, color in final_replacements:
        # Use simple inline style with color
        colored_text = f'<span style="color: {color}">{text}</span>'
        result = result[:start] + colored_text + result[end:]
    
    # Wrap in pre tag to preserve formatting and use monospace
    return f'<pre style="font-family: Consolas, Monaco, monospace; font-size: 12px; background-color: #1e1e1e; padding: 8px; border-radius: 4px; color: #d4d4d4; margin: 0;">{result}</pre>'
    html_result = f"<p style='font-family:Consolas,Monaco,monospace; font-size:12px; background-color:#1e1e1e; padding:6px; border-radius:4px; margin:0'>{result}</p>"
    return html_result


def analyze_code_object(code_text, word, cursor_position):
    """
    Analyze the code to find classes, functions, and methods defined in the file.
    Returns (type, signature, description) or None.
    """
    try:
        tree = ast.parse(code_text)
        
        # Find all definitions
        for node in ast.walk(tree):
            # Check for function definitions
            if isinstance(node, ast.FunctionDef) and node.name == word:
                # Build signature
                args = []
                for arg in node.args.args:
                    arg_str = arg.arg
                    # Check for type hints
                    if arg.annotation:
                        arg_str += f": {ast.unparse(arg.annotation)}"
                    args.append(arg_str)
                
                # Check for defaults
                defaults = node.args.defaults
                if defaults:
                    num_defaults = len(defaults)
                    for i in range(len(args) - num_defaults, len(args)):
                        default_val = ast.unparse(defaults[i - (len(args) - num_defaults)])
                        args[i] += f" = {default_val}"
                
                signature = f"def {node.name}({', '.join(args)})"
                
                # Add return type if present
                if node.returns:
                    signature += f" -> {ast.unparse(node.returns)}"
                
                signature += ":"
                
                # Extract docstring
                description = ast.get_docstring(node) or "User-defined function"
                
                return ('function', signature, description)
            
            # Check for class definitions
            elif isinstance(node, ast.ClassDef) and node.name == word:
                # Build class signature
                bases = [ast.unparse(base) for base in node.bases]
                if bases:
                    signature = f"class {node.name}({', '.join(bases)}):"
                else:
                    signature = f"class {node.name}:"
                
                # Extract docstring
                description = ast.get_docstring(node) or "User-defined class"
                
                return ('class', signature, description)
        
        return None
    except:
        return None


def get_documentation(word, code_text=None, cursor_position=None):
    """
    Get documentation for a word with proper syntax highlighting.
    Returns (formatted_html, doc_type) or (None, None) if not found.
    """
    # Check if it's a user-defined class/function
    if code_text and cursor_position:
        analysis = analyze_code_object(code_text, word, cursor_position)
        if analysis:
            obj_type, signature, description = analysis
            colored_sig = format_signature_with_colors(signature)
            return (colored_sig, description, obj_type)
    
    # Check Python keywords
    if word in PYTHON_KEYWORDS:
        keyword_type, description = PYTHON_KEYWORDS[word]
        color = COLORS['keyword']
        signature_html = f"<code style='background:#1e1e1e; padding:4px 8px; display:block; border-radius:4px; font-family:Consolas,monospace'><span style='color:{color}'>{word}</span></code>"
        return (signature_html, description, 'keyword')
    
    # Check Python built-ins
    if word in PYTHON_BUILTINS:
        signature, description = PYTHON_BUILTINS[word]
        colored_sig = format_signature_with_colors(signature)
        return (colored_sig, description, 'builtin')
    
    # Check built-in methods
    if word in BUILTIN_METHODS:
        signature, description = BUILTIN_METHODS[word]
        colored_sig = format_signature_with_colors(signature)
        return (colored_sig, description, 'method')
    
    # Check Qt docs
    if word in QT_DOCS:
        signature, description = QT_DOCS[word]
        colored_sig = format_signature_with_colors(signature)
        doc_type = 'module' if 'module' in signature.lower() else 'class'
        return (colored_sig, description, doc_type)
    
    # Check Maya docs
    if word in MAYA_DOCS:
        signature, description = MAYA_DOCS[word]
        colored_sig = format_signature_with_colors(signature)
        doc_type = 'module' if 'module' in signature.lower() else 'function'
        return (colored_sig, description, doc_type)
    
    # Check PyMEL-specific documentation
    if word in PYMEL_DOCS:
        signature, description = PYMEL_DOCS[word]
        colored_sig = format_signature_with_colors(signature)
        doc_type = 'pymel'
        return (colored_sig, description, doc_type)
    
    # Check OpenMaya API documentation - CRITICAL for advanced Maya scripting
    if word in OPENMAYA_DOCS:
        signature, description = OPENMAYA_DOCS[word]
        colored_sig = format_signature_with_colors(signature)
        doc_type = 'api'
        return (colored_sig, description, doc_type)
    
    return (None, None, None)

