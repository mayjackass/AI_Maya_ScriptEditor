# NEO Script Editor - Python & MEL Support Test

def test_python_functionality():
    """Test Python functionality in NEO Script Editor."""
    print("🐍 Testing Python functionality...")
    
    # Basic Python operations
    numbers = [1, 2, 3, 4, 5]
    squared = [x**2 for x in numbers]
    print(f"Original numbers: {numbers}")
    print(f"Squared numbers: {squared}")
    
    # Maya Python commands (when running in Maya)
    try:
        import maya.cmds as cmds
        print("✅ Maya Python module available")
        
        # Create a simple cube
        cube = cmds.polyCube(name="python_test_cube")
        print(f"Created cube: {cube[0]}")
        
        # Move it
        cmds.move(2, 0, 0, cube[0])
        print("Moved cube to (2, 0, 0)")
        
    except ImportError:
        print("ℹ️ Maya not available - basic Python test only")
        
    print("✅ Python test completed!")

if __name__ == "__main__":
    test_python_functionality()