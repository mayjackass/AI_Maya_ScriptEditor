# NEO Script Editor - Shelf Integration with Logo

## 🎨 **NEW: Dedicated NEO Shelf Tab with Logo Buttons**

The NEO Script Editor now includes a complete shelf integration system that creates a dedicated "NEO" shelf tab with beautiful buttons using the NEO logo from the assets folder.

## 🚀 **One-Click Complete Setup**

### **Option 1: Complete Setup (Recommended)**
```python
# In Maya Script Editor (Python tab):
complete_neo_setup()
```
This will:
- ✅ Create a "NEO" shelf tab with logo buttons
- ✅ Launch the dockable NEO Script Editor
- ✅ Set up all convenience functions
- ✅ Switch to the NEO shelf automatically

### **Option 2: Just Create the Shelf**
```python
# In Maya Script Editor (Python tab):
create_neo_shelf()
```

## 🎯 **What You Get**

### **NEO Shelf Tab Contains:**
1. **🔥 NEO (Large Button)** - Launch dockable NEO Script Editor
   - Uses the Matrix/Morpheus logo from assets folder
   - Large, prominent button for main functionality
   
2. **👁️ Hide Button** - Hide the docked NEO Script Editor
   - Quick way to hide without closing
   
3. **🪟 Win Button** - Launch standalone NEO Script Editor window
   - For when you want a separate floating window
   
4. **📜 Maya Button** - Maya's built-in Script Editor
   - For comparison/backup access

### **Visual Design:**
- **NEO Logo Icons** - Uses `matrix.png` or `morpheus.png` from assets
- **Professional Look** - Matches Maya's native shelf style
- **Clear Labels** - Each button has descriptive tooltips
- **Logical Layout** - Main NEO button is largest, others are utility buttons

## 🎨 **Icon Assets Used**

The shelf buttons automatically detect and use NEO logo icons:
- **Primary:** `assets/matrix.png` (The Matrix theme logo)
- **Secondary:** `assets/morpheus.png` (Morpheus character logo)
- **Fallback:** Maya's default Python icon if NEO logos not found

## 📖 **Usage Workflow**

1. **Initial Setup:** Run `complete_neo_setup()` once
2. **Daily Use:** Click the large **NEO** button in the shelf
3. **Dock at Top:** Drag the editor panel to the top of Maya
4. **Perfect Workflow:** Editor on top, viewport below!

## 🔧 **Management Commands**

```python
# Shelf management
create_neo_shelf()      # Create the NEO shelf tab
delete_neo_shelf()      # Remove the NEO shelf tab

# Editor management  
neo_docked()           # Launch dockable editor
hide_neo_docked()      # Hide docked editor
launch_neo_editor()    # Launch standalone window

# Complete setup
complete_neo_setup()   # Everything at once
setup_neo()           # Alias for complete setup
```

## 🎯 **Perfect Maya Workflow**

1. **Launch:** Click **NEO** button in shelf (or run `complete_neo_setup()`)
2. **Dock:** Drag NEO Script Editor to the **top** of Maya's interface
3. **Code:** Write Python/MEL scripts in the top panel
4. **See Results:** Viewport below shows immediate results
5. **AI Help:** Use built-in AI assistance for coding help

This gives you the perfect scripting workflow - just like Maya's built-in Script Editor but with all the advanced NEO features!

## 🏗️ **File Structure**

```
ai_script_editor/
├── maya_shelf_creator.py          # Creates shelf with logo buttons
├── complete_setup.py              # One-click complete setup
├── maya_dockable_launcher.py      # Docking functionality
├── userSetup.py                   # Enhanced userSetup (current file)
├── assets/
│   ├── matrix.png                 # NEO logo (primary)
│   ├── morpheus.png               # NEO logo (secondary)
│   └── ... (other icons)
└── ... (rest of NEO Script Editor)
```

## 🔄 **Upgrading from Basic Setup**

If you were using the basic userSetup.py:
1. Your existing setup still works
2. Just run `create_neo_shelf()` to add the shelf
3. Or run `complete_neo_setup()` for the full experience

## 🐛 **Troubleshooting**

### **Shelf doesn't appear:**
- Make sure Maya has write permissions to preferences
- Try: `delete_neo_shelf()` then `create_neo_shelf()`
- Check Maya Script Editor for error messages

### **Logo icons don't show:**
- Buttons will work with Maya default icons as fallback
- Check that `assets/matrix.png` or `assets/morpheus.png` exist
- File paths are automatically detected

### **Buttons don't work:**
- Make sure userSetup.py is properly installed
- Restart Maya if you just installed userSetup.py
- Try running commands manually first: `neo_docked()`

## 💡 **Pro Tips**

- **Pin the NEO shelf:** Right-click on shelf tabs to set NEO as default
- **Customize layout:** You can rearrange the NEO shelf buttons
- **Multi-monitor:** Use standalone + docked versions simultaneously
- **Quick access:** The large NEO button is designed for frequent clicking
- **Workspace layouts:** Maya will remember your NEO panel position in workspace layouts