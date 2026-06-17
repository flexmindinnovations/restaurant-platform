# Development Setup Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Git | >= 2.40 | [git-scm.com](https://git-scm.com) |
| Docker Desktop | >= 4.30 | [docker.com](https://www.docker.com/products/docker-desktop) |
| Python | 3.13+ | [python.org](https://www.python.org/downloads/) |
| uv | >= 0.5 | `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 22 LTS | [nodejs.org](https://nodejs.org) |
| Flutter | Stable (latest) | [flutter.dev](https://docs.flutter.dev/get-started/install) |
| Dart | >= 3.9.0 | Bundled with Flutter |
| pre-commit | >= 4.0 | `pip install pre-commit` |

### Optional

| Tool | Purpose | Install |
|------|---------|---------|
| Android Studio | Android emulator + SDK | [developer.android.com](https://developer.android.com/studio) |
| Xcode | iOS simulator (macOS only) | Mac App Store |
| Terraform | >= 1.9 — Infrastructure management | [terraform.io](https://developer.hashicorp.com/terraform/downloads) |
| AWS CLI | v2 — AWS interactions | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| Make | Run Makefile targets | See Windows notes below |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/flexmindinnovations/restaurant-platform.git
cd restaurant-platform

# 2. Start local services (PostgreSQL, Valkey, LocalStack, Mailpit)
cd infrastructure/docker && docker compose up -d && cd ../..

# 3. Backend
cd backend
cp .env.example .env
uv sync --all-extras
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload --port 8000
# → http://localhost:8000/docs

# 4. Frontend (new terminal)
cd frontend
npm ci
npm start
# → http://localhost:4200

# 5. Mobile (new terminal)
cd mobile
dart pub get
cd apps/customer_app && flutter run
```

---

## Detailed Setup

### 1. Local Infrastructure

Start all backing services with Docker Compose:

```bash
cd infrastructure/docker
docker compose up -d
```

This starts:

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL 17 + PostGIS | 5432 | Primary database |
| Valkey 8 | 6379 | Cache, sessions, pub/sub (Redis-compatible) |
| LocalStack | 4566 | AWS service emulation (S3, SQS, SNS, SES) |
| Mailpit | 1025 / 8025 | Email testing (SMTP + Web UI) |

Verify services are healthy:

```bash
docker compose ps
```

Access Mailpit UI at http://localhost:8025 to inspect emails sent during development.

### 2. Backend Setup

```bash
cd backend

# Create environment file
cp .env.example .env

# Install all dependencies (including dev)
uv sync --all-extras

# Run database migrations
uv run alembic upgrade head

# Start the dev server
uv run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

The API docs are available at http://localhost:8000/docs (Swagger) and http://localhost:8000/redoc (ReDoc).

**Common backend commands:**

```bash
uv run pytest                              # Run all tests
uv run pytest tests/unit -m unit           # Unit tests only
uv run pytest --cov=src --cov-report=html  # Tests with coverage
uv run ruff check src/ tests/              # Lint
uv run ruff format src/ tests/             # Auto-format
uv run mypy src/                           # Type checking
uv run lint-imports                        # Architecture boundary check
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm ci

# Start dev server (proxies /api to localhost:8000)
npm start
```

The admin dashboard is at http://localhost:4200.

**Common frontend commands:**

```bash
npm start          # Dev server (port 4200)
npm test           # Run Vitest unit tests
npm run test:ci    # Tests with coverage (no watch)
npm run lint       # ESLint + boundary rules
npm run e2e        # Playwright E2E tests
npm run format     # Prettier formatting
npm run build:prod # Production build
```

### 4. Mobile Setup

```bash
cd mobile

# Install workspace dependencies
dart pub get

# Run all 3 apps (pick one):
cd apps/customer_app && flutter run
cd apps/restaurant_app && flutter run
cd apps/delivery_app && flutter run
```

**Common mobile commands (from `mobile/` root):**

```bash
dart run melos run analyze    # Lint all packages
dart run melos run test       # Test all packages
dart run melos run format     # Check formatting
dart run melos run format-fix # Fix formatting
dart run melos run generate   # Run build_runner code generation
dart run melos run clean      # Clean all packages
```

### 5. Git Hooks

Install pre-commit hooks for automated code quality checks:

```bash
pre-commit install
```

This runs trailing-whitespace cleanup, ruff linting, secret detection, and more on every commit.

---

## Windows-Specific Notes

### Make

The project includes a `Makefile` for common tasks. Windows doesn't ship with `make`. Options:

1. **Install via Chocolatey:** `choco install make`
2. **Install via Scoop:** `scoop install make`
3. **Use PowerShell scripts instead:** The `scripts/` directory contains `.ps1` equivalents:

```powershell
.\scripts\bootstrap.ps1   # Full project setup
.\scripts\lint-all.ps1    # Run all linters
.\scripts\test-all.ps1    # Run all test suites
```

### Manual PowerShell equivalents for Makefile targets:

```powershell
# Infrastructure
cd infrastructure\docker; docker compose up -d; cd ..\..

# Backend
cd backend; uv sync --all-extras; cd ..
cd backend; uv run uvicorn app.main:create_app --factory --reload --port 8000; cd ..
cd backend; uv run pytest; cd ..

# Frontend
cd frontend; npm ci; cd ..
cd frontend; npm start; cd ..
cd frontend; npm test -- --watch=false; cd ..

# Mobile
cd mobile; dart pub get; cd ..
cd mobile; dart run melos run analyze; cd ..
cd mobile; dart run melos run test; cd ..
```

### Path Separators

Use backslashes (`\`) in PowerShell paths. Forward slashes (`/`) work in most contexts but may fail in some native Windows tools.

### Line Endings

The `.gitattributes` file normalizes line endings to LF in the repository. Git on Windows will auto-convert to CRLF in the working tree. If you encounter issues, run:

```bash
git config core.autocrlf true
```

---

## Troubleshooting

### Docker Compose won't start

- Ensure Docker Desktop is running
- Check for port conflicts: `netstat -an | findstr "5432 6379 4566"`
- Reset volumes: `cd infrastructure/docker && docker compose down -v && docker compose up -d`

### `uv sync` fails

- Ensure Python 3.13+ is installed: `python --version`
- Ensure uv is installed: `uv --version`
- Try clearing the cache: `uv cache clean`

### Frontend `npm ci` fails

- Ensure Node.js 22: `node --version`
- Delete `node_modules` and retry: `rm -rf node_modules && npm ci`
- If `package-lock.json` conflicts: `npm install` (regenerates lock)

### Mobile `dart pub get` fails

- Ensure Flutter stable: `flutter --version`
- Ensure Dart >= 3.9.0: `dart --version`
- Run from the `mobile/` root (workspace root), not from an individual app

### `dart run melos` not found

- Melos is a dev dependency, not globally installed. Always run from `mobile/` directory
- Ensure `dart pub get` was run in the workspace root first

### Tests fail with database connection errors

- Ensure Docker services are running: `docker compose ps` (from `infrastructure/docker/`)
- Check PostgreSQL is ready: `docker exec rp-postgres pg_isready -U platform`
- Integration tests use testcontainers, which require Docker to be running

### Pre-commit hooks fail on Windows

- Install pre-commit: `pip install pre-commit`
- Run `pre-commit install` from the repo root
- If gitleaks fails to download, install it manually: `scoop install gitleaks`

---

## IDE Setup

### VS Code (recommended)

Install these extensions:

- **Python**: `ms-python.python`, `ms-python.mypy-type-checker`, `charliermarsh.ruff`
- **Angular**: `angular.ng-template`
- **Flutter**: `dart-code.flutter`, `dart-code.dart-code`
- **General**: `esbenp.prettier-vscode`, `dbaeumer.vscode-eslint`, `hashicorp.terraform`, `ms-azuretools.vscode-docker`

Recommended workspace settings (`.vscode/settings.json`):

```json
{
  "editor.formatOnSave": true,
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": { "source.fixAll.ruff": "explicit" }
  },
  "[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[html]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[dart]": { "editor.formatOnSave": true }
}
```

### JetBrains (IntelliJ / PyCharm / WebStorm / Android Studio)

- Backend: Open `backend/` as a Python project, configure Python 3.13 interpreter from `.venv`
- Frontend: Open `frontend/` as a Node.js project, enable ESLint + Prettier
- Mobile: Open `mobile/` in Android Studio with Flutter plugin
- Install the Ruff plugin for Python linting
