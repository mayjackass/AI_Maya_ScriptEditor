# 🔧 Developer Mode Guide

## How to Bypass Beta Expiration (For Development)

As the developer, you have **3 easy ways** to bypass the beta expiration so you can continue working on the project even after the beta expires.

---

## ✅ Method 1: Use .devmode File (Simplest)

**Already Done!** I created a `.devmode` file in your project root.

```
ai_script_editor/.devmode  ← This file bypasses beta checks
```

**How it works:**
- When the app starts, it looks for `.devmode` file
- If found, beta expiration is completely bypassed
- Window title shows "BETA (DEV MODE)"
- Status bar shows "Developer Mode - Beta checks disabled"

**To disable:**
```powershell
# Simply delete the file
Remove-Item .devmode
```

**To re-enable:**
```powershell
# Create an empty file
New-Item -ItemType File -Name .devmode
```

---

## ✅ Method 2: Environment Variable

Set an environment variable before running:

### Windows (PowerShell):
```powershell
# Temporary (current session only)
$env:NEO_DEV_MODE = "1"
.venv\Scripts\python.exe run.py

# Or in one line:
$env:NEO_DEV_MODE = "1"; .venv\Scripts\python.exe run.py
```

### Windows (Permanent):
```powershell
# Add to system environment variables
[System.Environment]::SetEnvironmentVariable('NEO_DEV_MODE', '1', 'User')
```

### Mac/Linux:
```bash
# Temporary
export NEO_DEV_MODE=1
python run.py

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export NEO_DEV_MODE=1' >> ~/.bashrc
```

---

## ✅ Method 3: Change Expiry Date

Edit `license/beta_manager.py` line 15:

```python
# Set to far future date
BETA_EXPIRY_DATE = "2099-12-31"  # Never expires
```

**⚠️ Remember to change it back before distribution!**

---

## 🎯 Recommended Workflow

### During Development:
```
✅ Keep .devmode file in project
✅ Work normally without expiration warnings
✅ Test all features freely
```

### Before Distribution:
```
1. ❌ DELETE .devmode file
2. ✅ Set correct expiry date (2026-01-31)
3. ✅ Test that beta expiration works
4. ✅ Create distribution package
```

---

## 🔍 How to Tell Dev Mode is Active

When dev mode is active, you'll see:

**Console Output:**
```
[DEV MODE] Beta expiration bypassed for development
```

**Window Title:**
```
⚡️ NEO Script Editor v3.0 - Morpheus AI - BETA (DEV MODE)
```

**Status Bar:**
```
🔧 Developer Mode - Beta checks disabled
```

---

## 📋 Quick Reference

| Method | Pros | Cons |
|--------|------|------|
| **.devmode file** | ✅ Simple, automatic | ⚠️ Must delete before distribution |
| **Environment variable** | ✅ No file changes | ⚠️ Must set each time (temp) |
| **Change date** | ✅ Works always | ⚠️ Easy to forget to change back |

**Recommendation:** Use `.devmode` file (Method 1) - it's already set up!

---

## ⚠️ IMPORTANT: Before Distribution

**Pre-Distribution Checklist:**

```powershell
# 1. DELETE .devmode file
Remove-Item .devmode

# 2. Clear environment variable (if set)
[System.Environment]::SetEnvironmentVariable('NEO_DEV_MODE', $null, 'User')

# 3. Verify expiry date is correct
# Check license/beta_manager.py line 15:
# BETA_EXPIRY_DATE = "2026-01-31"

# 4. Test that beta expiration works
# (Temporarily change date to past, test blocking dialog)

# 5. Create distribution package
.\create_distribution.ps1
```

The `create_distribution.ps1` script **automatically excludes** `.devmode` file, but it's good practice to delete it first.

---

## 🧪 Testing Beta Expiration

To test that the beta system works correctly:

### Test Expired State:
```python
# Edit license/beta_manager.py line 15
BETA_EXPIRY_DATE = "2025-10-01"  # Past date

# Run and verify blocking dialog appears
.venv\Scripts\python.exe run.py

# Change back to real date
BETA_EXPIRY_DATE = "2026-01-31"
```

### Test Warning State:
```python
# Edit license/beta_manager.py line 15
import datetime
BETA_EXPIRY_DATE = (datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")

# Run and verify urgent warnings appear
.venv\Scripts\python.exe run.py
```

---

## 🔐 Security Note

**The `.devmode` file is NOT security:**
- It's for YOUR convenience during development
- Users could create it to bypass expiration
- For full version, implement proper license keys

**For now:**
- It's fine for beta testing
- Just make sure to exclude from distribution
- Consider it a "developer secret"

---

## 📝 Summary

**Current Setup:**
- ✅ `.devmode` file exists in your project
- ✅ Beta expiration bypassed automatically
- ✅ You can develop freely
- ✅ Easy to disable before distribution

**To Use:**
```powershell
# Just run normally - dev mode is active!
.venv\Scripts\python.exe run.py
```

**Before Sharing:**
```powershell
# Remove dev mode file
Remove-Item .devmode

# Create distribution
.\create_distribution.ps1
```

You're all set! You can now work on the project indefinitely without beta warnings. 🎉
