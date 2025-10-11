#!/usr/bin/env python
"""
Debug script to test AI response processing directly.
"""

def test_morpheus_response():
    """Test what happens when we process a typical AI response."""
    
    # Simulate a typical AI response with code block
    test_response = '''Here's a simple Python script for Maya:

```python
import maya.cmds as cmds

def create_simple_cube():
    """Create a simple cube in Maya."""
    # Create a cube
    cube = cmds.polyCube(name="simple_cube")[0]
    
    # Move it up slightly
    cmds.move(0, 2, 0, cube)
    
    # Print confirmation
    print(f"Created cube: {cube}")
    
    return cube

# Run the function
create_simple_cube()
```

This script creates a cube and moves it up 2 units.'''

    print("🧪 Testing AI Response Processing")
    print("=" * 50)
    
    # Test the regex pattern
    import re
    import html
    
    print(f"📝 Test response content:")
    print(f"Length: {len(test_response)} characters")
    print(f"Content preview: {repr(test_response[:100])}...")
    
    # Test code block detection
    pattern = r'```(?:(\w+)\n)?(.*?)\n?```'
    code_blocks = re.findall(pattern, test_response, flags=re.DOTALL)
    
    print(f"\n🔍 Code block detection:")
    print(f"Pattern: {pattern}")
    print(f"Found {len(code_blocks)} code blocks")
    
    if code_blocks:
        for i, (language, code) in enumerate(code_blocks):
            print(f"\n  Block {i+1}:")
            print(f"    Language: {repr(language)}")
            print(f"    Code length: {len(code)} chars")
            print(f"    Code preview: {repr(code[:50])}...")
            
            # Test HTML generation
            highlighted_code = html.escape(code.strip())
            
            code_html = f'''<div style="margin: 12px 0; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; font-family: 'Consolas', 'Monaco', monospace;">
    <div style="background: #161b22; border-bottom: 1px solid #30363d; padding: 8px 12px; font-size: 12px; color: #8b949e;">
        {language or 'python'}
    </div>
    <div style="padding: 12px; overflow-x: auto;">
        <pre style="margin: 0; color: #e6edf3; font-size: 13px; line-height: 1.45; white-space: pre-wrap;">{highlighted_code}</pre>
    </div>
</div>'''
            
            print(f"    HTML generated: {len(code_html)} chars")
            
        # Test the full processing logic
        print(f"\n🔄 Testing full processing...")
        
        processed_content = test_response
        code_htmls = []
        
        for i, (language, code) in enumerate(code_blocks):
            language = language or 'python'
            code = code.strip()
            
            placeholder = f'___CODE_BLOCK_{i}___'
            highlighted_code = html.escape(code)
            
            code_html = f'''<div style="margin: 12px 0; background: #0d1117;">
    <div style="background: #161b22; color: #8b949e;">{language}</div>
    <pre style="color: #e6edf3;">{highlighted_code}</pre>
</div>'''
            
            code_htmls.append(code_html)
            
            # Replace original with placeholder
            if language != 'python':
                original_pattern = f'```{language}\n{code}\n```'
            else:
                original_pattern1 = f'```python\n{code}\n```'
                original_pattern2 = f'```\n{code}\n```'
                if original_pattern1 in processed_content:
                    original_pattern = original_pattern1
                else:
                    original_pattern = original_pattern2
            
            processed_content = processed_content.replace(original_pattern, placeholder, 1)
            print(f"    Replaced code block {i+1} with {placeholder}")
        
        # Convert to HTML and restore
        text_html = html.escape(processed_content).replace('\n', '<br>')
        
        for i, code_html in enumerate(code_htmls):
            placeholder = f'___CODE_BLOCK_{i}___'
            text_html = text_html.replace(placeholder, code_html)
        
        print(f"\n✅ Final HTML length: {len(text_html)} chars")
        print(f"   Contains code blocks: {'<div style=' in text_html}")
        print(f"   Contains placeholders: {'CODE_BLOCK_' in text_html}")
        
        return True
    else:
        print("❌ No code blocks found - regex issue!")
        return False

if __name__ == "__main__":
    success = test_morpheus_response()
    if success:
        print("\n🎉 Processing logic working correctly!")
    else:
        print("\n⚠️ Issues detected in processing logic")