#!/usr/bin/env python3
"""
Simple test for triple quote highlighting without GUI.
This simulates the QSyntaxHighlighter behavior.
"""

import re
from typing import List, Tuple

class MockTextCharFormat:
    def __init__(self, name):
        self.name = name
        
    def __eq__(self, other):
        return isinstance(other, MockTextCharFormat) and self.name == other.name
        
    def __repr__(self):
        return f"Format({self.name})"

class MockHighlighter:
    def __init__(self):
        # Mock formats
        self.string_format = MockTextCharFormat("string")
        self.f_string_format = MockTextCharFormat("f_string")
        
        # Triple quote patterns
        self.triple_quote_patterns = [
            (re.compile(r'"""'), self.string_format, 1),      # Triple double quotes - state 1
            (re.compile(r"'''"), self.string_format, 2),      # Triple single quotes - state 2  
            (re.compile(r'f"""'), self.f_string_format, 3),   # F-string triple double - state 3
            (re.compile(r"f'''"), self.f_string_format, 4),   # F-string triple single - state 4
        ]
        
        # Mock state tracking
        self._current_state = 0
        self._previous_state = 0
        self._formatted_ranges = []  # (start, length, format)
        
    def setCurrentBlockState(self, state):
        self._current_state = state
        
    def currentBlockState(self):
        return self._current_state
        
    def previousBlockState(self):
        return self._previous_state
        
    def setPreviousBlockState(self, state):
        self._previous_state = state
        
    def setFormat(self, start, length, format_obj):
        self._formatted_ranges.append((start, length, format_obj))
        
    def clearFormats(self):
        self._formatted_ranges.clear()
        
    def getFormattedRanges(self):
        return self._formatted_ranges.copy()
    
    def _highlight_multiline_strings(self, text):
        """Handle multi-line string highlighting with state management."""
        # Start with no format override
        self.setCurrentBlockState(0)
        
        start_index = 0
        
        # If we're continuing from previous block's multi-line string
        if self.previousBlockState() > 0:
            # We're inside a multi-line string from previous block
            state = self.previousBlockState()
            if state == 1:  # Triple double quotes
                pattern = re.compile(r'"""')
                format_obj = self.string_format
            elif state == 2:  # Triple single quotes
                pattern = re.compile(r"'''")
                format_obj = self.string_format
            elif state == 3:  # F-string triple double
                pattern = re.compile(r'"""')
                format_obj = self.f_string_format
            elif state == 4:  # F-string triple single
                pattern = re.compile(r"'''")
                format_obj = self.f_string_format
            else:
                return
                
            # Look for the closing triple quote
            match = pattern.search(text)
            if match:
                # Found end of multi-line string
                end_index = match.end()
                self.setFormat(0, end_index, format_obj)
                self.setCurrentBlockState(0)
                start_index = end_index
            else:
                # Still inside multi-line string
                self.setFormat(0, len(text), format_obj)
                self.setCurrentBlockState(state)
                return
        
        # Look for new multi-line strings starting in this block
        # Process patterns in order of specificity (f-strings first, then regular strings)
        # Find all potential matches first
        all_matches = []
        for pattern, format_obj, state in self.triple_quote_patterns:
            for match in pattern.finditer(text, start_index):
                all_matches.append((match.start(), match.end(), pattern, format_obj, state, match))
        
        # Sort by position and prefer longer matches (f-strings over regular strings)
        all_matches.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        
        # Process the first valid match
        for start_pos, end_pos, pattern, format_obj, state, match in all_matches:
            if start_pos < start_index:
                continue  # Skip matches we've already processed
                
            # Look for closing triple quote on same line
            closing_pattern = re.compile(pattern.pattern.replace('f"""', '"""').replace("f'''", "'''"))
            closing_match = closing_pattern.search(text, end_pos)
            
            if closing_match:
                # Complete multi-line string on same line
                complete_end = closing_match.end()
                self.setFormat(start_pos, complete_end - start_pos, format_obj)
                start_index = complete_end
                break  # Process only one match per call
            else:
                # Multi-line string starts here and continues to next block
                self.setFormat(start_pos, len(text) - start_pos, format_obj)
                self.setCurrentBlockState(state)
                return

def test_multiline_highlighting():
    """Test multi-line string highlighting logic."""
    
    highlighter = MockHighlighter()
    
    # Test case 1: Complete docstring on multiple blocks
    print("=== Test Case 1: Multi-block docstring ===")
    
    # Block 1: Start of docstring
    text1 = '    """This is a docstring'
    highlighter.clearFormats()
    highlighter._highlight_multiline_strings(text1)
    
    print(f"Block 1: {repr(text1)}")
    print(f"Formatted ranges: {highlighter.getFormattedRanges()}")
    print(f"Block state: {highlighter.currentBlockState()}")
    
    # Block 2: Middle of docstring
    highlighter.setPreviousBlockState(highlighter.currentBlockState())
    text2 = '    that spans multiple lines'
    highlighter.clearFormats()
    highlighter._highlight_multiline_strings(text2)
    
    print(f"Block 2: {repr(text2)}")
    print(f"Formatted ranges: {highlighter.getFormattedRanges()}")
    print(f"Block state: {highlighter.currentBlockState()}")
    
    # Block 3: End of docstring
    highlighter.setPreviousBlockState(highlighter.currentBlockState())
    text3 = '    and ends here"""'
    highlighter.clearFormats()
    highlighter._highlight_multiline_strings(text3)
    
    print(f"Block 3: {repr(text3)}")
    print(f"Formatted ranges: {highlighter.getFormattedRanges()}")
    print(f"Block state: {highlighter.currentBlockState()}")
    
    # Test case 2: Complete string on single line
    print("\n=== Test Case 2: Single-line triple quote ===")
    
    highlighter.setPreviousBlockState(0)
    text4 = '    multi = """Complete string"""'
    highlighter.clearFormats()
    highlighter._highlight_multiline_strings(text4)
    
    print(f"Block: {repr(text4)}")
    print(f"Formatted ranges: {highlighter.getFormattedRanges()}")
    print(f"Block state: {highlighter.currentBlockState()}")
    
    # Test case 3: F-string multi-line
    print("\n=== Test Case 3: F-string multi-line ===")
    
    highlighter.setPreviousBlockState(0)
    text5 = '    f"""F-string start'
    highlighter.clearFormats()
    
    # Debug: check which patterns match
    for pattern, fmt, state in highlighter.triple_quote_patterns:
        matches = list(pattern.finditer(text5))
        if matches:
            print(f"  Pattern {pattern.pattern} matches at: {[(m.start(), m.end()) for m in matches]}")
    
    highlighter._highlight_multiline_strings(text5)
    
    print(f"Block 1: {repr(text5)}")
    print(f"Formatted ranges: {highlighter.getFormattedRanges()}")
    print(f"Block state: {highlighter.currentBlockState()}")
    
    highlighter.setPreviousBlockState(highlighter.currentBlockState())
    text6 = '    with {variable}"""'
    highlighter.clearFormats()
    highlighter._highlight_multiline_strings(text6)
    
    print(f"Block 2: {repr(text6)}")
    print(f"Formatted ranges: {highlighter.getFormattedRanges()}")
    print(f"Block state: {highlighter.currentBlockState()}")

if __name__ == "__main__":
    test_multiline_highlighting()