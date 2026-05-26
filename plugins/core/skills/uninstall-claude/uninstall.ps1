#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$claudeDir = Join-Path $env:USERPROFILE ".claude"
$claudeBinInfo = Get-Command claude -ErrorAction SilentlyContinue
$claudeBin = if ($claudeBinInfo) { $claudeBinInfo.Source } else { $null }

# Detect install method
$installMethod = "unknown"
if ($claudeBin) {
    $npmOut = & npm list -g @anthropic-ai/claude-code 2>$null
    if ($npmOut -match "claude-code") { $installMethod = "npm" }
    else { $installMethod = "direct" }
}

# PowerShell profile entries referencing claude
$psProfile = $PROFILE
$rcMatches = @()
if (Test-Path $psProfile) {
    Get-Content $psProfile | ForEach-Object {
        if ($_ -match '\.claude[/\\"]|anthropic-ai[/-]claude') {
            $rcMatches += "  ${psProfile}: $_"
        }
    }
}

Write-Host ""
Write-Host "Claude Code Uninstaller" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "Shell: PowerShell $($PSVersionTable.PSVersion)"
Write-Host ""
Write-Host "Will remove:" -ForegroundColor White
if (Test-Path $claudeDir) {
    Write-Host "  x $claudeDir  (settings, memory, history, plugins)" -ForegroundColor Red
} else {
    Write-Host "  - $claudeDir  (not found)"
}
if ($claudeBin) {
    Write-Host "  x $claudeBin  (binary, install method: $installMethod)" -ForegroundColor Red
} else {
    Write-Host "  - claude binary  (not found in PATH)"
}
if ($rcMatches.Count -gt 0) {
    Write-Host "  x PowerShell profile entries referencing claude:" -ForegroundColor Red
    $rcMatches | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "  - no PowerShell profile entries referencing claude found"
}

Write-Host ""
Write-Host "This cannot be undone." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Type DELETE to confirm, or anything else to cancel"

if ($confirm -ne "DELETE") {
    Write-Host "Cancelled."
    exit 0
}

Write-Host ""

# Uninstall binary
if ($claudeBin) {
    if ($installMethod -eq "npm") {
        Write-Host "Uninstalling via npm..."
        npm uninstall -g @anthropic-ai/claude-code
    } else {
        Write-Host "Removing $claudeBin ..."
        Remove-Item -Force $claudeBin
    }
    Write-Host "  done" -ForegroundColor Green
}

# Remove .claude dir
if (Test-Path $claudeDir) {
    Write-Host "Removing $claudeDir ..."
    Remove-Item -Recurse -Force $claudeDir
    Write-Host "  done" -ForegroundColor Green
}

# Clean PowerShell profile
if (Test-Path $psProfile) {
    $lines = Get-Content $psProfile
    $cleaned = $lines | Where-Object { $_ -notmatch '\.claude[/\\"]|anthropic-ai[/-]claude' }
    $removed = $lines.Count - $cleaned.Count
    if ($removed -gt 0) {
        $cleaned | Set-Content $psProfile
        Write-Host "  Removed $removed line(s) from $psProfile" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Done. Restart your terminal to complete cleanup." -ForegroundColor Green
Write-Host ""
