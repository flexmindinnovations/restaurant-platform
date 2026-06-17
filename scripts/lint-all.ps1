#Requires -Version 7.0
<#
.SYNOPSIS
    Run all linters across backend, frontend, and mobile.
#>

$ErrorActionPreference = 'Stop'
$failed = @()

Write-Host "`n=== Linting All ===" -ForegroundColor Cyan

# Backend
Write-Host "`n[Backend] ruff check..." -ForegroundColor Yellow
Push-Location backend
try {
    uv run ruff check src/ tests/
    if ($LASTEXITCODE -ne 0) { $failed += 'ruff check' }
} catch { $failed += 'ruff check' }

Write-Host "[Backend] ruff format check..." -ForegroundColor Yellow
try {
    uv run ruff format --check src/ tests/
    if ($LASTEXITCODE -ne 0) { $failed += 'ruff format' }
} catch { $failed += 'ruff format' }

Write-Host "[Backend] mypy..." -ForegroundColor Yellow
try {
    uv run mypy src/
    if ($LASTEXITCODE -ne 0) { $failed += 'mypy' }
} catch { $failed += 'mypy' }

Write-Host "[Backend] import boundaries..." -ForegroundColor Yellow
try {
    uv run lint-imports
    if ($LASTEXITCODE -ne 0) { $failed += 'import-linter' }
} catch { $failed += 'import-linter' }
Pop-Location

# Frontend
if (Test-Path frontend\package.json) {
    Write-Host "`n[Frontend] eslint..." -ForegroundColor Yellow
    Push-Location frontend
    try {
        npx ng lint
        if ($LASTEXITCODE -ne 0) { $failed += 'eslint' }
    } catch { $failed += 'eslint' }
    Pop-Location
}

# Mobile
if (Test-Path mobile\pubspec.yaml) {
    Write-Host "`n[Mobile] dart analyze..." -ForegroundColor Yellow
    Push-Location mobile
    try {
        dart run melos run analyze
        if ($LASTEXITCODE -ne 0) { $failed += 'dart analyze' }
    } catch { $failed += 'dart analyze' }
    Pop-Location
}

# Summary
Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "=== All lints passed ===" -ForegroundColor Green
} else {
    Write-Host "=== Lint failures: $($failed -join ', ') ===" -ForegroundColor Red
    exit 1
}
