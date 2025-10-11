# Indentation Guide Lines - NEO Script Editor

## 🎯 **Feature Overview**
The NEO Script Editor now includes vertical indentation guide lines that help visualize code structure and nesting levels, similar to VS Code's indentation guides.

## ✨ **Visual Features**

### **Indentation Guide Lines**
- **Vertical dotted lines** at each indentation level
- **Subtle gray color** (#404040) that doesn't interfere with code
- **Continuous lines** extending through the entire visible area
- **Real-time updates** when code is modified
- **Multi-level support** for deeply nested code

### **Smart Detection**
- **Tab size aware** (default 4 spaces)
- **Mixed indentation** support (spaces and tabs)
- **Empty line handling** (guides continue through empty lines)
- **Language agnostic** (works with Python and MEL)

## 🎨 **Visual Design**

### **Line Style**
```python
# Appearance Configuration
guide_color = QtGui.QColor("#404040")  # Subtle gray
line_style = QtCore.Qt.DotLine         # Dotted pattern
line_width = 1                         # Thin lines
```

### **Positioning**
- **Offset from line numbers**: Guides start after line number area
- **Character-width aligned**: Positioned at exact indentation columns
- **Font-aware spacing**: Uses actual character width for accuracy

## ⚙️ **User Controls**

### **Menu Toggle**
```
View → Show Indentation Guides ✓
```
- **Checkable menu item** for easy on/off toggle
- **Default enabled** for immediate visual feedback
- **Applies to all open tabs** for consistency

### **Programmatic Control**
```python
# Toggle indentation guides
editor.set_indentation_guides_visible(True/False)

# Set custom tab size
editor.set_tab_size(4)  # Default is 4 spaces
```

## 🛠️ **Technical Implementation**

### **Core Components**

#### **1. Paint Event Integration**
```python
def paintEvent(self, event):
    super().paintEvent(event)
    if self._show_indent_guides:
        self._draw_indentation_guides(event)
```

#### **2. Indentation Detection**
```python
def _get_indentation_level(self, line_text):
    """Calculate indentation level from line text."""
    spaces = 0
    for char in line_text:
        if char == ' ':
            spaces += 1
        elif char == '\t':
            spaces += self._tab_size
        else:
            break
    return spaces // self._tab_size
```

#### **3. Efficient Rendering**
```python
def _draw_indentation_guides(self, event):
    """Draw continuous vertical lines for all indentation levels."""
    # Two-pass algorithm:
    # 1. Collect all indentation levels in visible area
    # 2. Draw continuous vertical lines for each level
```

### **Performance Optimizations**

#### **Visible Area Only**
- Only processes blocks currently visible on screen
- Skips off-screen content for better performance
- Updates only when text changes or view scrolls

#### **Continuous Lines**
- Draws full-height lines instead of per-block segments
- Reduces drawing operations for better rendering speed
- Uses viewport boundaries for efficient clipping

## 📊 **Code Structure Support**

### **Python Indentation**
```python
class MyClass:              # Level 0 (no guide)
    def method(self):       # Level 1 (guide at column 4)
        if condition:       # Level 2 (guide at column 8)
            for item in items:  # Level 3 (guide at column 12)
                process(item)   # Level 4 (guide at column 16)
```

### **MEL Indentation**
```mel
global proc testProc() {    // Level 0 (no guide)
    if ($condition) {       // Level 1 (guide at column 4)
        for ($i=0; $i<10; $i++) {  // Level 2 (guide at column 8)
            print($i + "\n");      // Level 3 (guide at column 12)
        }
    }
}
```

### **Mixed Structures**
- **Nested functions**: Clear visual hierarchy
- **Control structures**: `if`, `for`, `while`, `try/catch` nesting
- **Data structures**: Lists, dictionaries, objects
- **Context managers**: `with` statements in Python

## 🎯 **Use Cases**

### **Code Navigation**
- **Quick visual assessment** of code complexity
- **Easy identification** of matching braces/blocks
- **Structure overview** without scrolling

### **Code Quality**
- **Indentation consistency** checking
- **Nesting depth** awareness for refactoring
- **Code review** assistance for structure analysis

### **Learning Aid**
- **Visual feedback** for proper indentation
- **Structure comprehension** for beginners
- **Best practices** reinforcement

## 🧪 **Testing & Validation**

### **Test Files Provided**
1. **`test_indentation_guides.py`**
   - Complex Python nesting scenarios
   - Class definitions with methods
   - Control structures (if/for/while/try)
   - List comprehensions and generators
   - Context managers

2. **`test_indentation_mel.mel`**
   - MEL procedure definitions
   - Switch/case statements
   - Nested loops and conditions
   - Array processing
   - Maya command sequences

### **Expected Behavior**
- ✅ **Immediate display** when opening indented files
- ✅ **Real-time updates** when typing/editing
- ✅ **Consistent positioning** across different content
- ✅ **Performance stability** with large files
- ✅ **Toggle functionality** via View menu

## 🚀 **Integration Benefits**

### **VS Code Parity**
- **Familiar visual cues** for VS Code users
- **Professional appearance** matching modern IDEs
- **Consistent behavior** across different file types

### **Maya Workflow Enhancement**
- **Python script** structure visualization
- **MEL procedure** nesting clarity
- **Code organization** improvement
- **Debugging assistance** through visual structure

## ✅ **Implementation Complete**

### **Features Delivered**
- 🎨 **Visual Indentation Guides** with dotted lines
- ⚙️ **Toggle Control** via View menu
- 🔧 **Configurable Tab Size** (default 4 spaces)
- 📱 **Real-time Updates** on text changes
- 🎯 **Multi-language Support** (Python & MEL)
- ⚡ **Performance Optimized** rendering
- 🧪 **Comprehensive Testing** with example files

### **Technical Achievements**
- **Efficient two-pass rendering** algorithm
- **Font-aware positioning** for accuracy
- **Viewport-optimized** drawing for performance
- **Event-driven updates** for responsiveness
- **Cross-platform compatibility** with Qt framework

**The NEO Script Editor now provides professional-grade visual assistance for code structure, making it easier to write, read, and maintain well-organized Python and MEL scripts!** 🚀