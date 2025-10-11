#!/usr/bin/env python
"""
Test the improved code block parsing logic.
"""
import html
import re

def highlight_python_code(code):
    """Simple highlighting for testing."""
    return html.escape(code)

def test_improved_parsing():
    """Test the new code block processing logic."""
    
    print("🧪 Testing Improved Code Block Processing")
    print("=" * 60)
    
    # Test content with code block
    content = """Here's a Maya Python script to create a cube:

```python
import maya.cmds as cmds

def create_cube():
    cube = cmds.polyCube(name="test_cube")[0]
    cmds.move(0, 5, 0, cube)
    return cube

# Create the cube
cube = create_cube()
print(f"Created cube: {cube}")
```

This script creates a cube and moves it up 5 units."""

    print("📝 Original content:")
    print(repr(content))
    print("\n" + "=" * 60)
    
    # Simulate the new logic from chat.py
    code_blocks = re.findall(r'```(?:(\w+)\n)?(.*?)```', content, flags=re.DOTALL)
    print(f"🔍 Found {len(code_blocks)} code blocks")
    
    if code_blocks:
        # Process content like in the improved method
        processed_content = content
        code_htmls = []
        
        # Process each code block 
        for i, (language, code) in enumerate(code_blocks):
            language = language or 'python'
            code = code.strip()
            
            if code:
                print(f"\n  📋 Code block {i+1}:")
                print(f"    Language: {language}")
                print(f"    Code: {repr(code[:100])}...")
                
                # Create HTML for this code block
                highlighted_code = highlight_python_code(code)
                
                code_html = f'''<div style="margin: 12px 0; background: #0d1117;">
    <div style="background: #161b22; color: #8b949e;">{language}</div>
    <pre style="color: #e6edf3;">{highlighted_code}</pre>
</div>'''
                
                # Replace the code block with a placeholder
                original_block = f'```{language}\n{code}\n```' if language != 'python' else f'```python\n{code}\n```'
                placeholder = f'___CODE_BLOCK_{i}___'
                processed_content = processed_content.replace(original_block, placeholder, 1)
                code_htmls.append(code_html)
                
                print(f"    ✅ Replaced with placeholder: {placeholder}")
        
        print(f"\n🔄 Processed content with placeholders:")
        print(repr(processed_content))
        
        # Convert text to HTML and restore code blocks
        text_html = html.escape(processed_content).replace('\n', '<br>')
        print(f"\n📝 HTML-escaped content:")
        print(repr(text_html))
        
        # Restore code blocks
        for i, code_html in enumerate(code_htmls):
            placeholder = f'___CODE_BLOCK_{i}___'
            text_html = text_html.replace(placeholder, code_html)
            
        print(f"\n✨ Final HTML with restored code blocks:")
        print(text_html)
        
        print(f"\n✅ Processing completed successfully!")
    else:
        print("❌ No code blocks found")

if __name__ == "__main__":
    test_improved_parsing()