#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$claudeDir = Join-Path $env:USERPROFILE ".claude"
$claudeBinInfo = Get-Command claude -ErrorAction SilentlyContinue
$claudeBin = if ($claudeBinInfo) { $claudeBinInfo.Source } else { $null }

Write-Host ""
Write-Host "Claude Code User-Scope Purge" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "Will remove:" -ForegroundColor White
if (Test-Path $claudeDir) {
    Write-Host "  x $claudeDir  (settings, memory, plugins, hooks, sessions, history)" -ForegroundColor Red
} else {
    Write-Host "  - $claudeDir  (not found, nothing to purge)"
}
Write-Host ""
Write-Host "Will keep:" -ForegroundColor White
if ($claudeBin) {
    Write-Host "  + $claudeBin  (binary stays installed)" -ForegroundColor Green
} else {
    Write-Host "  + claude binary  (not in PATH, not touched either way)" -ForegroundColor Green
}
Write-Host "  + PowerShell profile  (not touched)" -ForegroundColor Green

if (-not (Test-Path $claudeDir)) {
    Write-Host ""
    Write-Host "Nothing to do."
    exit 0
}

Write-Host ""
Write-Host "This cannot be undone. The binary remains; only user-scope state is wiped." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Type PURGE to confirm, or anything else to cancel"

if ($confirm -ne "PURGE") {
    Write-Host "Cancelled."
    exit 0
}

Write-Host ""
Write-Host "Removing $claudeDir ..."
Remove-Item -Recurse -Force $claudeDir
Write-Host "  done" -ForegroundColor Green

Write-Host ""
Write-Host "Done. User-scope state purged. The claude binary is still installed. Next launch starts fresh." -ForegroundColor Green
Write-Host ""
