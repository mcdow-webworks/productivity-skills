#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install the quick note (qn) CLI function to your PowerShell profile.

.DESCRIPTION
    This script adds a 'qn' function to your PowerShell profile that enables
    fast note capture using Claude Haiku 4.5 for automatic categorization.

.EXAMPLE
    .\install-qn.ps1

    After installation, restart PowerShell and use:
    qn "meeting with Jim about pricing"
#>

# Determine the quick_note.py script path
$scriptRoot = Split-Path -Parent $PSScriptRoot
$quickNotePath = Join-Path $scriptRoot "plugins\productivity-suite\skills\note-taking\scripts\quick_note.py"

# Verify the script exists
if (-not (Test-Path $quickNotePath)) {
    Write-Error "quick_note.py not found at: $quickNotePath"
    Write-Host "Make sure you're running this from the productivity-skills repository."
    exit 1
}

# Get the standard PowerShell profile path
$profilePath = $PROFILE

# Create profile directory if needed
$profileDir = Split-Path -Parent $profilePath
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "Created profile directory: $profileDir"
}

# Define the qn function - using single quotes to avoid expansion issues
$functionDef = @'

# Quick Note - Fast note capture using Claude Haiku 4.5
# Part of productivity-skills: https://github.com/mcdow-webworks/productivity-skills
function qn {
    if ($args.Count -eq 0) {
        Write-Host "Usage: qn <note content>" -ForegroundColor Yellow
        return
    }
    $noteContent = $args -join " "
    python "QUICK_NOTE_PATH_PLACEHOLDER" $noteContent
}
'@

# Replace placeholder with actual path
$functionDef = $functionDef -replace 'QUICK_NOTE_PATH_PLACEHOLDER', $quickNotePath

# Check if qn function already exists in profile
if (Test-Path $profilePath) {
    $existingContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
    if ($existingContent -and $existingContent -match "function qn\s*\{") {
        Write-Host "The 'qn' function already exists in your profile." -ForegroundColor Yellow
        Write-Host "Profile location: $profilePath"
        Write-Host ""
        $response = Read-Host "Do you want to replace it? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Host "Installation cancelled."
            exit 0
        }
        # Remove existing qn function (simple approach - remove the line with function qn and following lines until next function or end)
        $newContent = $existingContent -replace '(?ms)# Quick Note - Fast note capture.*?function qn \{.*?\n\}\r?\n?', ''
        Set-Content $profilePath $newContent
        Write-Host "Removed existing qn function."
    }
    Add-Content $profilePath $functionDef
    Write-Host "Added qn function to existing profile."
} else {
    Set-Content $profilePath $functionDef
    Write-Host "Created new profile with qn function."
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Profile location: $profilePath"
Write-Host "Script location: $quickNotePath"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Set your Anthropic API key:"
Write-Host "   `$env:ANTHROPIC_API_KEY = 'sk-ant-...'"
Write-Host "   (Add this to your profile for persistence)"
Write-Host ""
Write-Host "2. Restart PowerShell or run:"
Write-Host "   . `$PROFILE"
Write-Host ""
Write-Host "3. Try it out:"
Write-Host "   qn test note from installation"
