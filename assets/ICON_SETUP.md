# Morpheus Icon Setup Guide

## 🎯 Quick Setup

The AI Script Editor is already configured to use a custom Morpheus icon!

### Current Status
- ✅ Code configured for custom icon support
- ⚠️ Waiting for `morpheus.png` to be placed in this folder

---

## 📥 How to Add the Icon

### Option 1: Save the Image File
1. **Right-click** on the Morpheus image (the one with sunglasses)
2. Select **"Save Image As..."**
3. Save it as: `morpheus.png`
4. Place it in: `assets\` folder (this folder!)

### Option 2: Copy & Paste
1. **Copy** the Morpheus image to clipboard
2. Open **Paint** or any image editor
3. **Paste** the image (Ctrl+V)
4. **Save As** → `morpheus.png`
5. Save location: This `assets\` folder

### Option 3: Drag & Drop
1. **Download** the Morpheus image
2. **Rename** it to: `morpheus.png`
3. **Drag** it into this `assets\` folder

---

## 🎨 Icon Specifications

**Recommended:**
- Format: PNG (with transparency)
- Size: 24x24 to 48x48 pixels
- Background: Transparent preferred

**Supported Formats:**
- PNG ✅ (recommended)
- JPG/JPEG ✅
- ICO ✅
- BMP ✅

---

## ✅ Verification

Once you've added the icon:

1. **Check** that `morpheus.png` exists in this folder
2. **Restart** the AI Script Editor
3. **Look** for the Morpheus icon in the toolbar (instead of 🤖 emoji)

---

## 🔧 Technical Details

The code looks for the icon at:
```
assets/morpheus.png
```

If the file is not found, it automatically falls back to the 🤖 emoji.

---

## ❓ Troubleshooting

**Icon not showing?**
- ✓ Check filename is exactly: `morpheus.png` (case-sensitive)
- ✓ Check file is in the correct folder: `assets\`
- ✓ Try restarting the application
- ✓ Check console for error messages

**Want to change the icon?**
- Just replace `morpheus.png` with any image
- Restart the application
- The new icon will appear automatically!

---

## 🎬 About the Icon

The Morpheus icon represents the AI assistant in the NEO Script Editor - inspired by Morpheus from The Matrix, who guides Neo in his journey to understanding the Matrix. Similarly, the Morpheus AI guides you in your Maya scripting journey! 🕶️
