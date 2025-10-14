# Simple Fix Strategy

## The Problem
- AI says "Fix line 9" and "Fix line 12"
- We fix line 9, delete it
- Line 12 is now line 11
- But we're still looking for "line 12"

## The SIMPLE Solution
**Don't use line numbers at all after the first fix.**

For fix #1: Use the AI's line number (it's accurate)
For fix #2+: Search the ENTIRE file for a line that:
- Contains the fixed code as a substring
- But is NOT identical to the fixed code
- Has minimal extra characters (closest match)

Example:
- AI suggests: `self._setup_rules()` (fixed)
- File has: `self._setup_rules())` (broken, with extra `)`)
- Match found! This is the line to fix.

## Code Logic
```python
# Fix #1
if is_first_fix:
    use AI line number directly
    
# Fix #2+  
else:
    for each line in file:
        if fixed_code IN line AND fixed_code != line:
            score = how close is the length?
            keep best score
```

That's it. No complex strategies, no line number adjustment, no stored state.
