#Requires -Version 7.0
<#
.SYNOPSIS
    Run all test suites across backend, frontend, and mobile.
#>

$ErrorActionPreference = 'Stop'
$failed = @()

Write-Host "`n=== Running All Tests ===" -ForegroundColor Cyan

# Backend
Write-Host "`n[Backend] pytest..." -ForegroundColor Yellow
Push-Location backend
try {
    uv run pytest
    if ($LASTEXITCODE -ne 0) { $failed += 'backend' }
} catch { $failed += 'backend' }
Pop-Location

# Frontend
if (Test-Path frontend\package.json) {
    Write-Host "`n[Frontend] vitest..." -ForegroundColor Yellow
    Push-Location frontend
    try {
        npx ng test --watch=false
        if ($LASTEXITCODE -ne 0) { $failed += 'frontend' }
    } catch { $failed += 'frontend' }
    Pop-Location
}

# Mobile
if (Test-Path mobile\pubspec.yaml) {
    Write-Host "`n[Mobile] flutter test..." -ForegroundColor Yellow
    Push-Location mobile
    try {
        dart run melos run test
        if ($LASTEXITCODE -ne 0) { $failed += 'mobile' }
    } catch { $failed += 'mobile' }
    Pop-Location
}

# Summary
Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "=== All tests passed ===" -ForegroundColor Green
} else {
    Write-Host "=== Test failures: $($failed -join ', ') ===" -ForegroundColor Red
    exit 1
}
