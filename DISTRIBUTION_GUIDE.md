# Distribution & Packaging Guide

## Beta Release Packaging

### Quick Distribution (ZIP File)

The simplest way to distribute the beta:

```powershell
# From the project root directory
Compress-Archive -Path ai_script_editor -DestinationPath NEO_Script_Editor_v3.0_beta.zip
```

### What to Include

✅ **Include:**
- All Python source files (`.py`)
- Assets folder with icons
- `README.md`
- `LICENSE.txt`
- `BETA_LICENSE.md`
- `MAYA_SETUP.md` (installation instructions)

❌ **Exclude:**
- `.venv/` (virtual environment - users create their own)
- `__pycache__/` folders
- `.git/` folder
- `tests/` folder (optional, but can include for transparency)
- Personal API keys in config files

---

## Distribution Methods

### 1. GitHub Releases (Recommended)

**Advantages:**
- Free hosting
- Version control
- Download tracking
- Professional appearance
- Easy updates

**Steps:**
1. Create a new release on GitHub
2. Tag: `v3.0-beta`
3. Upload ZIP file
4. Include release notes
5. Mark as "Pre-release"

**Example Release Notes:**
```markdown
# NEO Script Editor v3.0 Beta

**Beta Period:** Oct 13, 2025 - Jan 31, 2026

## Beta Tester Benefits
- Full access to all features for 3.5 months
- 50% discount on full version after beta
- Direct influence on development priorities

## Installation
1. Download `NEO_Script_Editor_v3.0_beta.zip`
2. Extract to Maya scripts folder
3. Follow instructions in `MAYA_SETUP.md`

## Beta Software Notice
This is testing software. Please report bugs on GitHub Issues.

## Links
- [Documentation](README.md)
- [Beta License](BETA_LICENSE.md)
- [Report Bugs](https://github.com/mayjackass/AI_Maya_ScriptEditor/issues)
```

---

### 2. Direct Download (Google Drive, Dropbox)

**Advantages:**
- Simple for users
- No GitHub account needed
- Can track downloads

**Setup:**
1. Upload ZIP to cloud storage
2. Set to "Anyone with link can view"
3. Share link on social media, forums, etc.

---

### 3. Gumroad (Free Product with Email Collection)

**Advantages:**
- Collect emails for full version launch
- Professional download page
- Analytics built-in
- Easy to add purchase link later

**Setup:**
1. Create free Gumroad account
2. Add product (set price to $0)
3. Enable "Email required to download"
4. Add product description and screenshots
5. Share Gumroad link

**Email Collection Benefits:**
- Notify beta testers when full version launches
- Send upgrade discount codes (50% OFF)
- Share development updates
- Build customer base before launch

---

### 4. Maya Community Forums

**Where to Share:**
- Autodesk Maya Forums
- CGSociety
- Polycount
- r/Maya (Reddit)
- Creative Crash
- Tech Artists forums

**Post Template:**
```
NEW: NEO Script Editor v3.0 Beta - AI-Powered Maya Scripting

FREE Beta testing now available! (Expires Jan 31, 2026)

Features:
- Morpheus AI assistant with GPT-4 and Claude support
- VSCode-style inline diff preview
- Real-time error detection
- Matrix-themed dark UI

Beta testers get 50% OFF the full version!

[Download Link]
[GitHub Repository]

Looking for feedback - please report bugs and suggestions!
```

---

## Pre-Launch Checklist

Before distributing, verify:

### ✅ Code Quality
- [ ] All features working
- [ ] No hard-coded personal paths
- [ ] No API keys in code
- [ ] Print statements cleaned up (or kept for debugging)
- [ ] Comments are professional

### ✅ Documentation
- [ ] `README.md` is up-to-date
- [ ] Installation instructions are clear
- [ ] `BETA_LICENSE.md` explains terms
- [ ] Contact information is correct

### ✅ Beta System
- [ ] Expiration date is correct (Jan 31, 2026)
- [ ] Warning dialogs display properly
- [ ] Status bar shows beta info
- [ ] "Beta Information" menu item works

### ✅ Assets
- [ ] All icons are included
- [ ] No copyrighted materials
- [ ] Matrix theme is applied everywhere

### ✅ Legal
- [ ] `LICENSE.txt` is included
- [ ] Copyright year is current (2025)
- [ ] Beta terms are clear

---

## Creating Distribution Package

### Automated PowerShell Script

Save as `create_distribution.ps1`:

```powershell
# NEO Script Editor - Distribution Builder
# Creates a clean ZIP file for beta distribution

$projectName = "NEO_Script_Editor_v3.0_beta"
$sourceDir = "ai_script_editor"
$outputZip = "$projectName.zip"

Write-Host "Creating distribution package..." -ForegroundColor Green

# Remove old ZIP if exists
if (Test-Path $outputZip) {
    Remove-Item $outputZip
    Write-Host "Removed old package" -ForegroundColor Yellow
}

# Create temporary directory
$tempDir = "temp_dist"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy files
Write-Host "Copying files..." -ForegroundColor Cyan
Copy-Item -Path $sourceDir -Destination "$tempDir/$sourceDir" -Recurse

# Remove unnecessary files
Write-Host "Cleaning up..." -ForegroundColor Cyan
Remove-Item -Recurse -Force "$tempDir/$sourceDir/.venv" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$tempDir/$sourceDir/__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$tempDir/$sourceDir/.git" -ErrorAction SilentlyContinue
Get-ChildItem -Path $tempDir -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Cyan
Compress-Archive -Path "$tempDir/*" -DestinationPath $outputZip

# Cleanup temp
Remove-Item -Recurse -Force $tempDir

Write-Host "✅ Distribution package created: $outputZip" -ForegroundColor Green
Write-Host "Ready to upload!" -ForegroundColor Yellow
```

Run with: `.\create_distribution.ps1`

---

## Post-Release Tasks

### 1. Monitor Feedback
- Check GitHub Issues daily
- Respond to emails
- Engage with forum posts
- Track common problems

### 2. Update Documentation
- Add FAQ based on common questions
- Create video tutorials
- Write blog posts about features

### 3. Prepare for Full Release
- Set up payment processor (Gumroad, Stripe)
- Create upgrade pathway for beta testers
- Design license key system
- Plan launch marketing

### 4. Collect Email Addresses
If using Gumroad or similar:
- Build email list
- Send progress updates
- Announce full version launch
- Send 50% discount codes

---

## Beta to Full Version Transition

### Timeline (Example)

**January 2026:**
- Send "Beta ending soon" email (2 weeks before)
- Announce full version pricing
- Activate beta tester discount codes

**February 1, 2026:**
- Beta expires automatically
- Full version launches
- Beta testers receive upgrade link

**Post-Launch:**
- Continue support for paid users
- Release regular updates
- Build new features

---

## Pricing Strategy (Suggestions)

### Option 1: One-Time Payment
- **Beta Tester:** $49 (50% OFF)
- **Regular:** $99
- **Includes:** Lifetime license + 1 year updates

### Option 2: Tiered Pricing
- **Basic:** $29 (limited AI queries)
- **Pro:** $69 (unlimited AI, priority support)
- **Beta Tester:** 50% OFF any tier

### Option 3: Subscription
- **Monthly:** $9.99/month
- **Yearly:** $79/year (save 34%)
- **Beta Tester:** First year 50% OFF

**Recommendation:** One-time payment is popular with developers who dislike subscriptions.

---

## Support Channels

### For Beta Testers
- **Email:** mayjackass@example.com
- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions

### For Future Paid Users
Consider adding:
- Discord server for community
- Dedicated support email
- Documentation website
- Video tutorials on YouTube

---

## Marketing Ideas

### Pre-Launch (During Beta)
- Post on Maya forums
- Share on LinkedIn
- Tweet with #maya #python hashtags
- Record demo video
- Write blog post about development

### Launch (Full Version)
- Email beta testers with discount
- Press release to CG news sites
- Update Gumroad/store listing
- Post "success stories" from beta testers

---

## Questions?

If you need help with:
- Setting up Gumroad
- Creating GitHub releases
- Email marketing tools
- Payment processing
- License key systems

Feel free to ask! I can provide detailed guides for any of these.

---

**Next Steps:**
1. Test the beta system (check expiration warnings)
2. Create distribution ZIP
3. Upload to GitHub Releases
4. Share with trusted users first
5. Gather initial feedback
6. Public announcement

Good luck with your beta launch!
