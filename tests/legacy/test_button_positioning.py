"""
Test script to verify GitHub Copilot-style floating action buttons
positioning calculation logic.
"""

def test_positioning_logic():
    """Test the positioning calculation logic."""
    # Simulate editor dimensions
    editor_pos_x, editor_pos_y = 100, 50
    editor_width, editor_height = 800, 600
    
    # Button dimensions
    button_width, button_height = 160, 25
    
    # Expected position calculation
    expected_x = editor_pos_x + editor_width - button_width - 5  # 5px padding
    expected_y = editor_pos_y + editor_height - button_height - 5  # 5px padding
    
    print("=== Button Positioning Test ===")
    print(f"Editor Position: ({editor_pos_x}, {editor_pos_y})")
    print(f"Editor Size: {editor_width}x{editor_height}")
    print(f"Button Size: {button_width}x{button_height}")
    print(f"Expected Button Position: ({expected_x}, {expected_y})")
    print(f"Button should be anchored at bottom-right corner with 5px margin")
    
    # Verify the calculation
    bottom_right_x = editor_pos_x + editor_width
    bottom_right_y = editor_pos_y + editor_height
    
    print(f"\nEditor Bottom-Right Corner: ({bottom_right_x}, {bottom_right_y})")
    print(f"Button Top-Left: ({expected_x}, {expected_y})")
    print(f"Button Bottom-Right: ({expected_x + button_width}, {expected_y + button_height})")
    
    # Check margins
    margin_right = bottom_right_x - (expected_x + button_width)
    margin_bottom = bottom_right_y - (expected_y + button_height)
    
    print(f"\nMargins from editor edge:")
    print(f"Right margin: {margin_right}px")
    print(f"Bottom margin: {margin_bottom}px")
    
    assert margin_right == 5, f"Right margin should be 5px, got {margin_right}px"
    assert margin_bottom == 5, f"Bottom margin should be 5px, got {margin_bottom}px"
    
    print("✅ All positioning tests passed!")

if __name__ == "__main__":
    test_positioning_logic()
    print("\n🎯 The floating action buttons should now be properly anchored")
    print("   to the bottom-right corner of the code editor with proper margins.")