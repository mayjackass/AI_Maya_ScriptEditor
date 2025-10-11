#!/usr/bin/env python
"""
Diagnostic test for AI code block parsing - tests the regex logic without UI.
"""
import re

def test_code_block_parsing():
    """Test the code block parsing logic from chat.py"""
    
    print("🧪 Testing AI Code Block Parsing Logic")
    print("=" * 50)
    
    # Test content with code block
    test_content = """Here's a Maya Python script to create a cube:

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

    print("📝 Test content:")
    print(repr(test_content))
    print("\n" + "=" * 50)
    
    # Test the regex pattern from chat.py
    pattern = r'```(?:(\w+)\n)?(.*?)```'
    
    print("🔍 Testing regex pattern:", repr(pattern))
    code_blocks = re.findall(pattern, test_content, flags=re.DOTALL)
    
    print(f"\n📊 Found {len(code_blocks)} code blocks:")
    
    for i, (language, code) in enumerate(code_blocks, 1):
        print(f"\n  Block {i}:")
        print(f"    Language: {repr(language)}")
        print(f"    Code length: {len(code)} characters")
        print(f"    Code preview: {repr(code[:100])}...")
        
        # Test if code is detected as Maya-compatible
        is_maya = (
            'maya.cmds' in code or
            'cmds.' in code or
            language.lower() in ['python', 'mel'] or
            any(cmd in code for cmd in ['polyCube', 'polySphere', 'move', 'rotate', 'scale'])
        )
        print(f"    Maya compatible: {is_maya}")
    
    if code_blocks:
        print("\n✅ Code block parsing is working!")
    else:
        print("\n❌ No code blocks found - regex might be broken")
        
        # Try alternative patterns
        print("\n🔧 Testing alternative patterns...")
        
        # Test simpler pattern
        simple_pattern = r'```[\s\S]*?```'
        simple_matches = re.findall(simple_pattern, test_content)
        print(f"Simple pattern found {len(simple_matches)} matches")
        
        # Test with different flags
        dotall_matches = re.findall(r'```(?:(\w+)\n)?(.*?)```', test_content, re.DOTALL)
        print(f"With DOTALL flag: {len(dotall_matches)} matches")

if __name__ == "__main__":
    test_code_block_parsing()