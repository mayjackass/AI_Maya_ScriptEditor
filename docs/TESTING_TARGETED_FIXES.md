# 🧪 Testing Guide: Targeted Fix System

## Overview
This guide helps you verify that Morpheus returns **targeted fixes** (not entire code) and that the system works correctly.

---

## Visual Indicators

### Code Block Badges

The chat now shows badges indicating code type:

#### ✅ Targeted Fix (Green Badge)
```
┌────────────────────────────────────────┐
│ Python  [Targeted Fix]   Keep Copy Undo│  ← Green badge
├────────────────────────────────────────┤
│ # Line 45 - Fixed typo                 │
│ result = calculate(x, y)               │
└────────────────────────────────────────┘
```
**What it means:** AI returned ≤10 lines (focused fix)

#### 🔵 Full Code (Blue Badge)
```
┌────────────────────────────────────────┐
│ Python  [Full Code (50 lines)]  Keep...│  ← Blue badge
├────────────────────────────────────────┤
│ def my_function():                     │
│     # ... entire function code ...     │
└────────────────────────────────────────┘
```
**What it means:** AI returned >10 lines (full code or large fix)

---

## Test Cases

### Test 1: Simple Error Fix ✅

**Setup:**
```python
def create_sphere():
    cmds.polySphere(r=1)
    cmds.move(0, 0, 0  # Missing closing paren - ERROR!
```

**Test Steps:**
1. Open NEO Script Editor
2. Paste the code above
3. Open Morpheus chat
4. Type: `"review this code and fix the error"`
5. Send

**Expected Result:**
- ✅ Green badge: "Targeted Fix"
- ✅ Returns 1-3 lines:
  ```python
  cmds.move(0, 0, 0)  # Fixed missing paren
  ```
- ✅ Explanation mentions the specific error
- ✅ Does NOT return entire function

**If Blue Badge Appears:** AI didn't follow prompt - needs refinement

---

### Test 2: Logic Error Fix ✅

**Setup:**
```python
def scale_objects(objects):
    for obj in objects:
        cmds.setAttr(obj + ".scaleX", 2)  # ERROR: Only scales X
        cmds.setAttr(obj + ".scaleY", 2)
        cmds.setAttr(obj + ".scaleZ", 2)  # Tedious!
```

**Test Steps:**
1. Paste code
2. Ask: `"fix this code - it's not efficient"`

**Expected Result:**
- ✅ Green badge: "Targeted Fix"
- ✅ Returns 1-2 lines:
  ```python
  cmds.setAttr(obj + ".scale", 2, 2, 2)  # Simplified - sets all axes
  ```
- ✅ Explains why this is better
- ✅ Does NOT return entire loop

---

### Test 3: Typo Fix ✅

**Setup:**
```python
def crete_cube():  # Typo!
    cmds.polyCube()
```

**Test Steps:**
1. Paste code
2. Ask: `"what's wrong with this?"`

**Expected Result:**
- ✅ Green badge: "Targeted Fix"
- ✅ Returns 1 line:
  ```python
  def create_cube():  # Fixed: crete → create
  ```
- ✅ Points out the typo

---

### Test 4: Request Full Code (Should Return Full) 🔵

**Setup:**
```python
# Some existing code
```

**Test Steps:**
1. Ask: `"recreate the whole code with better structure"`

**Expected Result:**
- 🔵 Blue badge: "Full Code (X lines)"
- ✅ Returns entire rewritten code
- ✅ This is CORRECT behavior when explicitly requested

---

### Test 5: New Script From Scratch 🔵

**Setup:**
- Empty editor

**Test Steps:**
1. Ask: `"create a sphere creation tool"`

**Expected Result:**
- 🔵 Blue badge: "Full Code (X lines)"
- ✅ Returns complete new script
- ✅ This is CORRECT (no existing code to fix)

---

## Debugging Failed Tests

### Issue: Blue Badge When Green Expected

**Cause:** AI returned full code instead of targeted fix

**Debug Steps:**

1. **Check the prompt sent to AI:**
   - Look in console for `[DEBUG]` messages
   - Verify `[Current Editor Context]` was included
   - Check if code was in the prompt

2. **Check AI response:**
   - Look for trigger words in your question:
     - ✅ Good: "fix", "review", "error", "what's wrong"
     - ❌ Might trigger full code: "recreate", "rewrite", "from scratch"

3. **Check code complexity:**
   - AI might return full code if:
     - Multiple errors in different locations
     - Structural changes needed (refactoring)
     - Unclear what specific part needs fixing

**Solutions:**
- Be more specific: "fix the syntax error on line 10"
- Ask for one thing: "fix the missing paren" not "review everything"
- Provide clearer context: "the error is in the move command"

---

### Issue: Green Badge But Wrong Code

**Cause:** AI identified wrong section or misunderstood

**Debug Steps:**
1. Check if the fix makes sense
2. Verify line numbers in AI response
3. Check if AI understood the context

**Solutions:**
- Be more specific about the error location
- Highlight the problematic code before asking
- Rephrase: "line 5 has a typo" instead of "there's a typo"

---

### Issue: "Keep" Button Not Working

**Cause:** Code matching failed

**Debug Steps:**
1. Check console for `[INFO]` messages
2. Look for "Could not find matching code"
3. Check if editor code changed since asking

**Solutions:**
- Don't modify code while waiting for AI response
- If prompted, choose "Append" or "Replace All"
- Copy code manually and apply fix yourself

---

## Success Metrics

After each test, record:

| Test | Badge Color | Lines Returned | Correct? | Notes |
|------|-------------|----------------|----------|-------|
| Error Fix | 🟢 Green | 2 | ✅ Yes | Perfect! |
| Logic Fix | 🟢 Green | 3 | ✅ Yes | Good |
| Typo Fix | 🟢 Green | 1 | ✅ Yes | Excellent |
| Recreate | 🔵 Blue | 45 | ✅ Yes | Expected |
| New Script | 🔵 Blue | 60 | ✅ Yes | Expected |

**Target:** 80%+ of fix requests should show green badge

---

## Advanced Testing

### Test 6: Multiple Errors

**Setup:**
```python
def process(data)  # Missing colon
    result = data + 5
    return reuslt  # Typo
```

**Test Steps:**
1. Ask: `"fix all errors"`

**Expected Result:**
- ✅ Green badge (if AI returns only the 2 fixed lines)
- 🔵 Blue badge acceptable (both lines need fixing)
- ✅ Should fix BOTH errors

---

### Test 7: Ambiguous Request

**Setup:**
```python
# 50 lines of code
```

**Test Steps:**
1. Ask: `"make this better"`

**Expected Result:**
- 🔵 Blue badge likely (ambiguous = full code)
- ⚠️ AI might return full refactored code
- **Lesson:** Be specific in requests

---

## Reporting Issues

If tests fail, report with:

1. **Test Case:** Which test failed
2. **Badge Color:** Green or Blue
3. **Expected:** What should have happened
4. **Actual:** What actually happened
5. **Code Sample:** The code you tested
6. **Question:** Exact question asked
7. **AI Response:** Full AI response
8. **Screenshot:** Chat window with badge visible

---

## Best Practices for Users

### DO ✅
- Be specific: "fix the syntax error"
- Mention location: "error on line 10"
- One issue at a time: "fix the missing paren"
- Use trigger words: "review", "fix", "error"

### DON'T ❌
- Be vague: "make this work"
- Ask multiple things: "fix everything and optimize"
- Use confusing words: "recreate but only fix one thing"
- Modify code while waiting for response

---

## Console Debug Messages

Look for these in output console:

```
[DEBUG] Making OPENAI API call with model gpt-4o-mini...
[Current Editor Context - untitled_1.py (PYTHON)]
[User Question]
review this code and fix the error
[DEBUG] Got API response - length: 245 chars
[MORPHEUS] Code suggestion available - use buttons above input field
[INFO] 💡 Review the suggested changes in the editor
```

**Good signs:**
- ✅ "length: 100-500 chars" = targeted fix
- ✅ `[INFO] Review the suggested changes`

**Warning signs:**
- ⚠️ "length: 2000+ chars" = full code returned
- ⚠️ `[WARNING] Could not find matching code`

---

## Summary

### Green Badge (Targeted Fix) = Success ✅
- AI returned focused fix (≤10 lines)
- Prompt is working correctly
- System behaving as expected

### Blue Badge (Full Code) = Check Context 🔵
- Expected for:
  - "recreate", "rewrite", "from scratch"
  - New scripts
  - Major refactoring
- Unexpected for:
  - Simple error fixes
  - Typos
  - Single-line changes
- **Action:** Refine your question to be more specific

### No Badge = Error ❌
- Code block failed to render
- Check console for errors
- Refresh chat or restart app

---

## Quick Reference

| Your Request | Expected Badge | Expected Lines |
|--------------|----------------|----------------|
| "fix the error" | 🟢 Green | 1-5 |
| "what's wrong?" | 🟢 Green | 1-5 |
| "review this" | 🟢 Green | 3-10 |
| "recreate all" | 🔵 Blue | Full code |
| "new script" | 🔵 Blue | Full code |
| "optimize" | 🟢/🔵 Mixed | Depends |

**Remember:** The badge color helps you instantly verify if AI followed the targeted fix instruction!
