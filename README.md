# AI Script Editor v2.0 — Personal Edition

**Developed by:** [Mayj Amilano](https://github.com/mayjackass)  
**Built for:** Autodesk Maya 2026  
**Framework:** PySide6 / OpenAI API v1.x  

---

## Overview

**AI Script Editor** is a lightweight, modern Python editor built directly for **Maya’s embedded Python environment**.  
It combines the comfort of a mini-IDE with the power of **AI-assisted coding**, offering smart completions, linting, and contextual chat—all inside Maya’s UI.

The tool is designed for **Technical Directors**, **Pipeline TDs**, and **Maya tool developers** who want a fast, native alternative to VS Code or PyCharm inside Maya.

---

## Features

### Code Editing
- Syntax highlighting (VS Code Dark+ style)
- Line numbers and current-line highlighting
- Smart indentation and tab spacing
- Real-time syntax linting (`ast`-based)

### AI Copilot
- Integrated **OpenAI GPT-4o mini** chat dock
- Context-aware suggestions using your active code
- Inline “ghost” completions triggered by `Ctrl + Space`
- Optional **Apply Suggestion** button to insert AI-generated code directly

### Explorer & Navigation
- Dockable file/folder explorer
- Auto-parses folders → files → classes/functions
- Double-click to open symbols in new tabs
- Recent-file and folder memory

### Execution & Output
- Run active script directly in Maya with `Ctrl + Enter`
- Output console dock for live logs and tracebacks
- Safe `stdout`/`stderr` redirection

### Interface & Theming
- Custom charcoal dark theme
- Tabbed editor workspace
- Search bar (`Ctrl + F`) and toolbar actions
- Menu-bar shortcuts similar to VS Code

---

## Installation

1. **Copy** the project folder into your Maya scripts directory, e.g.  
