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

# Maya commands
MAYA_DOCS = {
    'cmds': ('module', 'maya.cmds - Maya Commands module providing procedural interface to Maya'),
    'pm': ('module', 'pymel.core - PyMEL provides a more pythonic interface to Maya'),
    'polySphere': ('cmds.polySphere(radius=1.0, subdivisionX=20, subdivisionY=20, name="")', 
                   'Create a polygonal sphere'),
    'polyCube': ('cmds.polyCube(width=1, height=1, depth=1, name="")', 
                 'Create a polygonal cube'),
    'select': ('cmds.select(*args, replace=True, add=False, deselect=False)', 
               'Select objects in the scene'),
    'ls': ('cmds.ls(selection=True, type=None, long=False)', 
           'List objects in the scene'),
    'createNode': ('cmds.createNode(nodeType, name="", parent=None)', 
                   'Create a new dependency node'),
    'setAttr': ('cmds.setAttr(attribute, value, type=None)', 
                'Set the value of a dependency node attribute'),
    'getAttr': ('cmds.getAttr(attribute)', 
                'Get the value of a dependency node attribute'),
    'delete': ('cmds.delete(*objects)', 
               'Delete objects from the scene'),
    'duplicate': ('cmds.duplicate(object, name="", returnRootsOnly=True)', 
                  'Duplicate objects in the scene'),
    'parent': ('cmds.parent(object, parent, add=False, relative=False)', 
               'Make objects children of the given parent'),
}


def format_signature_with_colors(signature):
    """
    Format a function/class signature with proper syntax highlighting colors.
    Returns HTML with styled spans matching the editor colors.
    """
    if not signature:
        return ""
    
    # Patterns for different syntax elements
    patterns = [
        (r'\b(def|class|return|yield|if|elif|else|for|while|in|is|and|or|not|True|False|None)\b', 'keyword'),
        (r'\b([A-Z][a-zA-Z0-9_]*)\b', 'class'),  # Class names (capitalized)
        (r'\b(str|int|float|bool|list|dict|set|tuple|object)\b', 'builtin'),  # Built-in types
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()', 'function'),  # Function names before (
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?==)', 'parameter'),  # Parameters before =
        (r'([\[\]\(\)\{\},:])', 'operator'),  # Brackets and punctuation
        (r'(["\'])(?:(?=(\\?))\2.)*?\1', 'string'),  # Strings
        (r'\b(\d+\.?\d*)\b', 'number'),  # Numbers
    ]
    
    # Create a copy for processing
    result = signature
    replacements = []
    
    # Find all matches and their positions
    for pattern, color in patterns:
        for match in re.finditer(pattern, signature):
            start, end = match.span()
            matched_text = match.group(0)
            # Store replacement info
            replacements.append((start, end, matched_text, color))
    
    # Sort by position (reverse to replace from end to start)
    replacements.sort(key=lambda x: x[0], reverse=True)
    
    # Apply colorization from end to start to preserve positions
    for start, end, text, color in replacements:
        color_code = COLORS.get(color, COLORS['default'])
        styled = f"<span style='color:{color_code}'>{text}</span>"
        result = result[:start] + styled + result[end:]
    
    # Wrap in div without any background - just styled text
    return f"<div style='padding:6px 0px; font-family:Consolas,Monaco,monospace; font-size:12px'>{result}</div>"


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
    
    return (None, None, None)

