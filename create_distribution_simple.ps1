# Simple Distribution Builder for NEO Script Editor
# Creates a clean ZIP package for marketplace distribution

param(
    [string]$Version = "3.0-beta"
)

Write-Host "`n=== NEO Script Editor - Distribution Builder ===" -ForegroundColor Cyan
Write-Host "Version: $Version`n" -ForegroundColor Yellow

# Create dist folder
$distDir = "dist"
if (!(Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

# Create temp folder
$tempDir = "temp_neo_dist"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "Copying files..." -ForegroundColor Green

# Copy main files
Copy-Item -Path "*.py" -Destination $tempDir
Copy-Item -Path "*.md" -Destination $tempDir
Copy-Item -Path "*.txt" -Destination $tempDir -ErrorAction SilentlyContinue

# Copy directories
$folders = @("ai", "editor", "license", "model", "ui", "utils", "assets")
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Copy-Item -Path $folder -Destination $tempDir -Recurse
    }
}

Write-Host "Cleaning up..." -ForegroundColor Green

# Remove unwanted files
$cleanupPatterns = @("__pycache__", "*.pyc", "*.pyo", ".pytest_cache")
foreach ($pattern in $cleanupPatterns) {
    Get-ChildItem -Path $tempDir -Recurse -Force -Include $pattern -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

# Create INSTALL.txt
$installInstructions = @"
NEO Script Editor v$Version - Installation Instructions
========================================================

QUICK START:
1. Extract this ZIP to your Maya scripts folder:
   - Windows: C:\Users\<username>\Documents\maya\scripts\
   - macOS: ~/Library/Preferences/Autodesk/maya/scripts/
   - Linux: ~/maya/scripts/

2. Install dependencies (if not already installed):
   pip install PySide6 openai anthropic

3. Launch the editor:
   python run.py

MAYA INTEGRATION:
See MAYA_SETUP.md for instructions on launching from within Maya.

API KEYS:
- Go to Tools → Settings to enter your OpenAI or Anthropic API key
- Or use the offline mode toggle in the chat panel

BETA INFORMATION:
- This beta expires: January 31, 2026
- Report issues: https://github.com/mayjackass/AI_Maya_ScriptEditor/issues

For full documentation, see README.md

Created by: Mayj Amilano
Website: https://github.com/mayjackass
"@

Set-Content -Path "$tempDir\INSTALL.txt" -Value $installInstructions

Write-Host "Creating ZIP archive..." -ForegroundColor Green

# Create ZIP
$zipPath = "$distDir\NEO_Script_Editor_v$Version.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -CompressionLevel Optimal

# Get file size
$fileSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
$fileCount = (Get-ChildItem -Path $tempDir -Recurse -File).Count

# Cleanup
Remove-Item -Recurse -Force $tempDir

Write-Host "`n=== SUCCESS! ===" -ForegroundColor Green
Write-Host "Package created: $zipPath" -ForegroundColor Cyan
Write-Host "File size: $fileSize MB" -ForegroundColor Cyan
Write-Host "Files included: $fileCount" -ForegroundColor Cyan
Write-Host "`nReady to upload to your marketplace!`n" -ForegroundColor Yellow
