#Requires -Version 7.0
<#
.SYNOPSIS
    Bootstrap the entire restaurant-platform development environment on Windows.
.DESCRIPTION
    Starts Docker services, installs backend/frontend/mobile dependencies,
    runs migrations, and installs git hooks.
#>

$ErrorActionPreference = 'Stop'

Write-Host "`n=== Restaurant Platform - Bootstrap ===" -ForegroundColor Cyan
Write-Host ""

# 1. Start infrastructure
Write-Host "[1/5] Starting local services..." -ForegroundColor Yellow
Push-Location infrastructure\docker
docker compose up -d
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Docker Compose failed to start" }
Pop-Location

# 2. Backend setup
Write-Host "[2/5] Setting up backend..." -ForegroundColor Yellow
Push-Location backend

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "  Created .env from .env.example"
}

uv sync --all-extras
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "uv sync failed" }
Write-Host "  Dependencies installed"

Write-Host "  Waiting for PostgreSQL..."
$retries = 0
do {
    $retries++
    try {
        docker exec rp-postgres pg_isready -U platform -d restaurant_platform 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { break }
    } catch {}
    Start-Sleep -Seconds 1
} while ($retries -lt 30)

if ($retries -ge 30) { Pop-Location; throw "PostgreSQL did not become ready in time" }

uv run alembic upgrade head
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Alembic migrations failed" }
Write-Host "  Migrations applied"
Pop-Location

# 3. Frontend setup
Write-Host "[3/5] Setting up frontend..." -ForegroundColor Yellow
Push-Location frontend
if (Test-Path package.json) {
    npm ci
    if ($LASTEXITCODE -ne 0) { Pop-Location; throw "npm ci failed" }
    Write-Host "  Dependencies installed"
} else {
    Write-Host "  Skipped (not yet initialized)"
}
Pop-Location

# 4. Mobile setup
Write-Host "[4/5] Setting up mobile..." -ForegroundColor Yellow
Push-Location mobile
if (Test-Path pubspec.yaml) {
    dart pub get
    if ($LASTEXITCODE -ne 0) { Pop-Location; throw "dart pub get failed" }
    Write-Host "  Workspace dependencies resolved"
} else {
    Write-Host "  Skipped (not yet initialized)"
}
Pop-Location

# 5. Git hooks
Write-Host "[5/5] Installing git hooks..." -ForegroundColor Yellow
if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
    pre-commit install
    Write-Host "  Pre-commit hooks installed"
} else {
    Write-Host "  pre-commit not found. Install: pip install pre-commit" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "=== Bootstrap complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Start backend:  cd backend; uv run uvicorn app.main:create_app --factory --reload --port 8000"
Write-Host "Start frontend: cd frontend; npm start"
Write-Host "Start mobile:   cd mobile\apps\customer_app; flutter run"
Write-Host ""
