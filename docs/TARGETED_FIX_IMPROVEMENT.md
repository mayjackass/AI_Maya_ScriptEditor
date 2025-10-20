# 🎯 Targeted Fix Improvement

## Overview
Morpheus AI now returns **only the specific code fix** instead of regenerating the entire code, making reviews clearer and more precise.

---

## Problem

### Before (❌ Entire Code Returned)
```
User: "Review this code and fix the error"

[100 lines of code with 1 error on line 45]

Morpheus returns: ALL 100 lines with line 45 fixed
```

**Issues:**
- Hard to see what actually changed
- Preview shows entire file (cluttered)
- Replaces everything (risky)
- Difficult to understand the fix
- Not how VSCode/Copilot work

---

## Solution

### After (✅ Targeted Fix Only)
```
User: "Review this code and fix the error"

[100 lines of code with 1 error on line 45]

Morpheus returns: Lines 44-46 with the fix + explanation
```

**Benefits:**
- ✅ **Clear:** Only see the actual change
- ✅ **Safe:** Only replaces problematic section
- ✅ **Fast:** Easier to review
- ✅ **Professional:** Matches VSCode behavior
- ✅ **Educational:** Focus on what was wrong

---

## Technical Implementation

### 1. AI System Prompt Enhancement

**File:** `ai/chat.py` (Lines 125-148)

Added **CRITICAL CODE FIX RULE** to system prompt:

```python
system_msg = (
    # ... existing prompt ...
    "\n"
    "**CRITICAL CODE FIX RULE:**\n"
    "When user provides existing code and asks to fix/review errors:\n"
    "• ONLY return the SPECIFIC lines that need to be fixed/changed\n"
    "• DO NOT return the entire code - only the problematic section with your fix\n"
    "• Include 1-2 lines of context before/after the fix for clarity\n"
    "• Explain what was wrong and what you changed\n"
    "• Example: If line 10 has an error, return lines 9-11 with the fix, not lines 1-100\n"
    "\n"
    "Only return the FULL code when:\n"
    "• User explicitly asks 'recreate the whole code' or 'rewrite everything'\n"
    "• User asks for a completely new script from scratch\n"
    "• No existing code is provided in context"
)
```

**Effect:** AI now intelligently decides when to return partial vs full code.

---

### 2. Enhanced Code Matching Algorithm

**File:** `ui/chat_manager.py` (Lines 754-829)

#### Strategy 1: Exact Substring Match
```python
# Perfect for small targeted fixes
if suggested_text in current_code:
    # Find exact position and replace
    return exact_match_info
```

**Use Case:** AI returns exact code snippet that exists in editor

#### Strategy 2: Difflib Matching with Adaptive Threshold
```python
matcher = difflib.SequenceMatcher(None, current_lines, suggested_lines)
min_match_size = min(2, len(suggested_lines) - 1)  # Adaptive

if match.size >= min_match_size:
    # Small fixes get minimal context (≤5 lines)
    # Large fixes get more context
```

**Use Case:** AI returns modified code with context

#### Strategy 3: Fuzzy Single-Line Matching
```python
# For 1-3 line fixes
ratio = difflib.SequenceMatcher(...).ratio()
if ratio > 0.6:  # 60% similarity
    return fuzzy_match_info
```

**Use Case:** AI returns similar but not exact match (typo fixes, etc.)

---

## User Experience Examples

### Example 1: Simple Typo Fix

**User Request:**
```
"Fix the typo in the function name"
```

**Original Code:**
```python
def crete_sphere():  # Line 10 - typo!
    cmds.polySphere()
```

**Morpheus Response:**
```
The path reveals a simple typo - 'crete' when you meant 'create'.

```python
def create_sphere():  # Fixed typo
    cmds.polySphere()
```

Replace line 10 with this correction.
```

**Preview:**
- Shows: Line 10 only
- Replaces: Line 10 only
- Clear what changed: `crete` → `create`

---

### Example 2: Logic Error Fix

**User Request:**
```
"Review this code and fix the error"
```

**Original Code:**
```python
1  def scale_objects(objects):
2      for obj in objects:
3          scale = cmds.getAttr(obj + ".scaleX")
4          if scale > 1:
5              cmds.setAttr(obj + ".scaleX", 1)  # Error: should be all axes
6          else:
7              cmds.setAttr(obj + ".scaleX", 2)
8      return objects
```

**Morpheus Response:**
```
I see the limitation - you're only modifying scaleX, leaving Y and Z unchanged.

```python
if scale > 1:
    cmds.setAttr(obj + ".scale", 1, 1, 1)  # All axes
else:
    cmds.setAttr(obj + ".scale", 2, 2, 2)  # All axes
```

Replace lines 4-7 with this uniform scaling approach.
```

**Preview:**
- Shows: Lines 4-7
- Replaces: Lines 4-7 only
- Rest of code untouched

---

### Example 3: When Full Code IS Returned

**User Request:**
```
"Create a sphere creation tool from scratch"
```

**Morpheus Response:**
```python
# Returns entire new script (correct behavior)
import maya.cmds as cmds

def create_sphere_tool():
    # ... full implementation ...
```

**Why:** No existing code context, explicit request for new script.

---

## Code Matching Flow

```
┌─────────────────────────────┐
│ Morpheus Returns Fix Code   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Strategy 1: Exact Match?    │
│ Is suggested code substring │
│ of current code?            │
└──────────┬──────────────────┘
           │ No
           ▼
┌─────────────────────────────┐
│ Strategy 2: Difflib Match?  │
│ Find longest similar block  │
│ (adaptive threshold)        │
└──────────┬──────────────────┘
           │ No
           ▼
┌─────────────────────────────┐
│ Strategy 3: Fuzzy Match?    │
│ Try line-by-line similarity │
│ (60% threshold)             │
└──────────┬──────────────────┘
           │ No
           ▼
┌─────────────────────────────┐
│ Show Options Dialog         │
│ • Replace All               │
│ • Append to End             │
│ • Cancel                    │
└─────────────────────────────┘
```

---

## Settings & Configuration

### Matching Thresholds

**Location:** `ui/chat_manager.py`

```python
# Fuzzy matching threshold (Strategy 3)
FUZZY_MATCH_THRESHOLD = 0.6  # 60% similarity

# Minimum match size for small fixes
min_match_size = min(2, len(suggested_lines) - 1)

# Context expansion for small vs large fixes
if len(suggested_lines) <= 5:
    # Small fix - minimal context
    context_lines = 0
else:
    # Large fix - more context
    context_lines = 2
```

**Tuning:** Adjust these values to make matching more/less strict.

---

## Testing

### Test Case 1: Single Line Fix
```python
# Original
result = calc(10, 20  # Missing closing paren

# Morpheus returns
result = calc(10, 20)  # Fixed

# Expected: Line 1 replaced
```

### Test Case 2: Multi-Line Fix
```python
# Original
if condition:
print("test")  # Wrong indentation

# Morpheus returns
if condition:
    print("test")  # Fixed indentation

# Expected: Lines 1-2 replaced
```

### Test Case 3: Full Rewrite Request
```python
# User: "Recreate the whole code with proper structure"

# Morpheus returns: ENTIRE new code
# Expected: Full file replacement option
```

---

## Comparison: Before vs After

| Scenario | Before | After |
|----------|--------|-------|
| **1 typo fix** | 100 lines | 1 line ✅ |
| **Logic error** | 100 lines | 5 lines ✅ |
| **Syntax fix** | 100 lines | 2 lines ✅ |
| **New script** | Full code ✅ | Full code ✅ |
| **Preview clarity** | ❌ Cluttered | ✅ Clean |
| **Review time** | 30 seconds | 5 seconds ✅ |
| **User confidence** | Low | High ✅ |

---

## User Workflow

### Step 1: Request Fix
```
User: "Review this code and fix the error"
```

### Step 2: Morpheus Analyzes
- Receives full code context
- Identifies error location
- Generates targeted fix (3-5 lines)

### Step 3: User Reviews
- Sees ONLY the fix in preview
- Clear before/after comparison
- Easy to understand change

### Step 4: Apply or Reject
- **Keep:** Replace specific lines
- **Copy:** Copy fix to clipboard
- **Undo:** Reject suggestion

---

## Benefits Summary

### For Users
✅ **Clarity:** See exactly what changes  
✅ **Speed:** Faster review process  
✅ **Safety:** Less risk of breaking code  
✅ **Learning:** Understand the fix better  
✅ **Confidence:** Trust AI suggestions  

### For Workflow
✅ **Professional:** Matches VSCode/Copilot  
✅ **Efficient:** Less scrolling/reading  
✅ **Precise:** Surgical code changes  
✅ **Reversible:** Easy to undo specific changes  

---

## Future Enhancements

### Potential Improvements
1. **Inline Diff View:** Show red/green diff in editor
2. **Multiple Fixes:** Handle multiple errors in one response
3. **Partial Accept:** Accept only some suggested lines
4. **AI Learning:** Train on user preferences
5. **Confidence Score:** Show match quality percentage

---

## Troubleshooting

### Issue: Morpheus still returns full code
**Solution:** Check if user request includes keywords:
- "recreate"
- "rewrite everything"
- "from scratch"

These trigger full code generation (intentional).

### Issue: No match found for fix
**Causes:**
- Code changed significantly since request
- AI misunderstood context
- Fix is too generic

**Fallback:** Dialog offers "Replace All" or "Append" options.

### Issue: Wrong section replaced
**Cause:** Multiple similar code blocks

**Solution:** AI should return more unique context lines.

---

## Commit Reference
- **Commit:** `be94427`
- **Date:** 2025-01-14
- **Files Modified:** `ai/chat.py`, `ui/chat_manager.py`
- **Lines Changed:** +68, -8

---

## Summary

✅ **Targeted fixes only** - no more entire code dumps  
✅ **3 matching strategies** - exact, difflib, fuzzy  
✅ **Adaptive context** - small fixes = minimal context  
✅ **Clear previews** - see only what changes  
✅ **Professional behavior** - matches VSCode/Copilot  
✅ **Better UX** - faster review, higher confidence  

**Result:** Morpheus now suggests like a senior developer - precise, focused, and easy to understand.
