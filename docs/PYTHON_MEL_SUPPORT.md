# NEO Script Editor - Python & MEL Support

## Overview

The NEO Script Editor now supports both **Python** and **MEL** scripting languages for Maya development. You can easily switch between languages and execute code in both environments.

## Language Selection

### Toolbar Language Selector
- **Location**: Main toolbar between Search and Run buttons
- **Options**: Python (default), MEL
- **Function**: Changes syntax highlighting and execution mode

### Auto-Detection
When opening files, the editor automatically detects the language based on file extension:
- `.py` files → Python mode
- `.mel` files → MEL mode

## Python Support

### Features
- **Syntax Highlighting**: Full Python syntax highlighting with VS Code Dark+ theme
- **Execution**: Uses Maya's Python environment with `exec()`
- **Output Capture**: Captures print statements and displays in console
- **Error Handling**: Shows line numbers and detailed error messages
- **Maya Integration**: Full access to `maya.cmds` and `maya.mel` modules

### Usage
1. Select "Python" from language dropdown
2. Write or paste Python code
3. Press **F5** to run entire script or **F9** to run selection

### Example Python Code
```python
import maya.cmds as cmds

# Create a cube
cube = cmds.polyCube(name="my_cube")
print(f"Created: {cube[0]}")

# Move and rotate
cmds.move(0, 3, 0, cube[0])
cmds.rotate(45, 0, 45, cube[0])

# Create material
material = cmds.shadingNode('lambert', asShader=True, name='my_material')
cmds.setAttr(f"{material}.color", 1, 0, 0, type="double3")

print("Python script completed!")
```

## MEL Support

### Features  
- **Syntax Highlighting**: Complete MEL syntax highlighting with Maya commands
- **Execution**: Uses `maya.mel.eval()` for authentic MEL execution
- **Maya Commands**: Highlights all major Maya MEL commands
- **Variables**: Highlights MEL variables (starting with $)
- **Comments**: Supports both // single-line and /* */ multi-line comments

### Usage
1. Select "MEL" from language dropdown  
2. Write or paste MEL code
3. Press **F5** to run entire script or **F9** to run selection

### Example MEL Code
```mel
// Create and manipulate objects
string $cube = `polyCube -w 2 -h 2 -d 2`;
print ("Created cube: " + $cube[0] + "\n");

// Move the cube up
move -r 0 3 0 $cube[0];

// Create a sphere
string $sphere = `polySphere -r 1`;
move -r 4 0 0 $sphere[0];

// Create and assign material
string $material = `shadingNode -asShader lambert`;
string $sg = `sets -renderable true -noSurfaceShader true -empty`;
connectAttr -f ($material + ".outColor") ($sg + ".surfaceShader");

// Assign to cube
select -r $cube[0];
sets -e -forceElement $sg;

print "MEL script completed!\n";
```

## File Operations

### Opening Files
- **File → Open** supports both `.py` and `.mel` files
- Filter options: "All Script Files", "Python Files", "MEL Files"
- Language auto-detected from extension

### Saving Files
- **File → Save As** offers appropriate file filters based on current language
- Default extensions: `.py` for Python, `.mel` for MEL
- Extensions auto-added if not specified

## Keyboard Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| Run Script | **F5** | Execute entire current script (Python or MEL) |
| Run Selection | **F9** | Execute selected code or current line |
| Open File | **Ctrl+O** | Open Python or MEL file |
| Save File | **Ctrl+S** | Save current file |
| Save As | **Ctrl+Shift+S** | Save with new name/format |

## Console Output

### Python Output
- Shows `print()` statements
- Displays execution results
- Shows detailed error messages with line numbers

### MEL Output  
- Shows `print` command output
- Displays command results
- Shows MEL error messages

## Error Handling

### Python Errors
- Line number detection from traceback
- Detailed error descriptions
- Shows output before error occurred

### MEL Errors
- Maya MEL error messages
- Syntax suggestions for common issues
- Graceful handling when Maya not available

## Best Practices

### Python
- Use `maya.cmds` for Maya operations
- Utilize Python's data structures and control flow
- Take advantage of list comprehensions and functions

### MEL
- End statements with semicolons
- Use proper variable declarations with `string`, `int`, `float`
- Utilize backticks for command execution
- Use proper string concatenation with `+`

## Integration Notes

### Maya Environment
- Both languages execute within Maya's environment
- Full access to Maya scene and objects  
- Changes are immediately reflected in Maya viewport

### Standalone Mode
- Python works in standalone mode (limited Maya functionality)
- MEL requires Maya environment
- Graceful error handling when Maya unavailable

## Troubleshooting

### Common Issues

**"Maya not available" error**
- Solution: Run script inside Maya, not standalone Python

**MEL syntax errors**  
- Check semicolons at end of statements
- Verify proper string quoting
- Ensure variable declarations are correct

**Import errors**
- Ensure running in proper Maya Python environment
- Check Maya version compatibility

### Getting Help
- Use **Tools → Check Syntax Errors** (Ctrl+E) to validate code
- Console shows detailed error messages
- GitHub Copilot chat can help debug issues

## Examples and Tests

### Test Files
- `test_python_support.py` - Python functionality test
- `test_mel_support.mel` - MEL functionality test
- Both files demonstrate language-specific features

### Running Tests
1. Open test file appropriate for language
2. Select matching language from dropdown
3. Press F5 to run complete test
4. Check console for results

The NEO Script Editor provides a unified environment for both Python and MEL development, making it easy to work with either language or even combine both in your Maya workflow.