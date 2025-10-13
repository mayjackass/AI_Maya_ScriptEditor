# NEO Script Editor - Distribution Package Builder
# Creates a clean ZIP file ready for beta distribution

param(
    [string]$Version = "3.0-beta",
    [switch]$IncludeTests = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$projectName = "NEO_Script_Editor_v$Version"
$sourceDir = "."
$outputDir = "dist"
$outputZip = "$outputDir/$projectName.zip"

Write-Host "`n🚀 NEO Script Editor - Distribution Builder" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host ""

# Create output directory
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Host "✅ Created output directory" -ForegroundColor Green
}

# Remove old package if exists
if (Test-Path $outputZip) {
    Remove-Item $outputZip
    Write-Host "🗑️  Removed old package" -ForegroundColor Yellow
}

# Create temporary directory
$tempDir = "temp_dist_$(Get-Random)"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null
Write-Host "📁 Created temporary directory" -ForegroundColor Cyan

# Files and folders to include
$includeItems = @(
    "*.py",
    "*.md",
    "*.txt",
    "ai",
    "editor",
    "license",
    "model",
    "ui",
    "utils",
    "assets"
)

if ($IncludeTests) {
    $includeItems += "tests"
}

# Copy files
Write-Host "`n📋 Copying files..." -ForegroundColor Cyan
foreach ($item in $includeItems) {
    $sourcePath = Join-Path $sourceDir $item
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $tempDir -Recurse -Force
        Write-Host "  ✓ $item" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $item (not found, skipping)" -ForegroundColor DarkGray
    }
}

# Remove unnecessary files and folders
Write-Host "`n🧹 Cleaning up..." -ForegroundColor Cyan

$excludePatterns = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".git",
    ".venv",
    "venv",
    ".vscode",
    ".idea",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
    ".devmode",           # Developer mode file - MUST exclude!
    "DEV_MODE_GUIDE.md"   # Developer documentation
)

foreach ($pattern in $excludePatterns) {
    Get-ChildItem -Path $tempDir -Recurse -Force -Include $pattern -ErrorAction SilentlyContinue | 
        ForEach-Object {
            Remove-Item -Recurse -Force $_.FullName -ErrorAction SilentlyContinue
            Write-Host "  ✓ Removed $($_.Name)" -ForegroundColor DarkGray
        }
}

# Create README in package root
$packageReadme = @"
# NEO Script Editor v$Version - Installation

## Quick Start

1. Extract this folder to your Maya scripts directory:
   - Windows: `C:\Users\<YourName>\Documents\maya\scripts\`
   - Mac: `~/Library/Preferences/Autodesk/maya/scripts/`
   - Linux: `~/maya/scripts/`

2. Open Maya Script Editor and run:
   ``````python
   import ai_script_editor.run as neo
   neo.main()
   ``````

3. Or create a shelf button - see MAYA_SETUP.md for details.

## Important Files

- **README.md** - Full documentation and features
- **BETA_LICENSE.md** - Beta terms and benefits
- **LICENSE.txt** - Legal license agreement
- **MAYA_SETUP.md** - Detailed installation instructions
- **DISTRIBUTION_GUIDE.md** - For developers/contributors

## Beta Information

- **Version:** $Version
- **Expires:** January 31, 2026
- **Beta Testers:** Get 50% OFF full version!

## Support

- 📧 Email: mayjackass@example.com
- 🐛 Bugs: https://github.com/mayjackass/AI_Maya_ScriptEditor/issues
- 📚 Docs: https://github.com/mayjackass/AI_Maya_ScriptEditor

Thank you for testing! 🚀
"@

Set-Content -Path "$tempDir\INSTALL.txt" -Value $packageReadme
Write-Host "  ✓ Created INSTALL.txt" -ForegroundColor Green

# Create version info file
$versionInfo = @"
NEO Script Editor - Version Information
========================================

Version: $Version
Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Build Type: Beta Release
Expiry Date: 2026-01-31

Package Contents:
"@

Get-ChildItem -Path $tempDir -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Replace("$tempDir\", "")
    $versionInfo += "`n  - $relativePath"
}

Set-Content -Path "$tempDir\VERSION.txt" -Value $versionInfo
Write-Host "  ✓ Created VERSION.txt" -ForegroundColor Green

# Count files
$fileCount = (Get-ChildItem -Path $tempDir -Recurse -File).Count
$folderCount = (Get-ChildItem -Path $tempDir -Recurse -Directory).Count

# Create ZIP archive
Write-Host "`n📦 Creating ZIP archive..." -ForegroundColor Cyan
Compress-Archive -Path "$tempDir\*" -DestinationPath $outputZip -CompressionLevel Optimal

# Get file size
$zipSize = (Get-Item $outputZip).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)

# Cleanup temp directory
Remove-Item -Recurse -Force $tempDir
Write-Host "  ✓ Cleaned up temporary files" -ForegroundColor Green

# Summary
Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "✅ DISTRIBUTION PACKAGE CREATED!" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host ""
Write-Host "📦 Package: " -NoNewline -ForegroundColor Cyan
Write-Host "$outputZip" -ForegroundColor Yellow
Write-Host "💾 Size: " -NoNewline -ForegroundColor Cyan
Write-Host "$zipSizeMB MB" -ForegroundColor Yellow
Write-Host "📁 Files: " -NoNewline -ForegroundColor Cyan
Write-Host "$fileCount" -ForegroundColor Yellow
Write-Host "📂 Folders: " -NoNewline -ForegroundColor Cyan
Write-Host "$folderCount" -ForegroundColor Yellow
Write-Host ""

# Next steps
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test the package in a fresh Maya installation" -ForegroundColor White
Write-Host "  2. Upload to GitHub Releases (tag: v$Version)" -ForegroundColor White
Write-Host "  3. Create release notes from BETA_LICENSE.md" -ForegroundColor White
Write-Host "  4. Mark as 'Pre-release' on GitHub" -ForegroundColor White
Write-Host "  5. Share download link with beta testers" -ForegroundColor White
Write-Host ""

Write-Host "🔗 Quick Commands:" -ForegroundColor Cyan
Write-Host "  Open folder: " -NoNewline -ForegroundColor White
Write-Host "explorer $outputDir" -ForegroundColor Yellow
Write-Host "  Extract test: " -NoNewline -ForegroundColor White
Write-Host "Expand-Archive -Path '$outputZip' -DestinationPath test_extract" -ForegroundColor Yellow
Write-Host ""

Write-Host "✨ Ready for distribution! Good luck with your beta launch! 🚀" -ForegroundColor Green
Write-Host ""

# Automatically open output folder
Start-Process explorer $outputDir
