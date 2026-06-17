#!/usr/bin/env bash
set -euo pipefail

echo "=== Restaurant Platform — Bootstrap ==="
echo ""

# 1. Start infrastructure
echo "[1/5] Starting local services..."
cd infrastructure/docker
docker compose up -d
cd ../..

# 2. Backend setup
echo "[2/5] Setting up backend..."
cd backend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from .env.example"
fi
uv sync --all-extras
echo "  Dependencies installed"

echo "  Waiting for PostgreSQL..."
until docker exec rp-postgres pg_isready -U platform -d restaurant_platform > /dev/null 2>&1; do
    sleep 1
done

uv run alembic upgrade head
echo "  Migrations applied"
cd ..

# 3. Frontend setup
echo "[3/5] Setting up frontend..."
cd frontend
if [ -f package.json ]; then
    npm ci
    echo "  Dependencies installed"
else
    echo "  Skipped (not yet initialized)"
fi
cd ..

# 4. Mobile setup
echo "[4/5] Setting up mobile..."
cd mobile
if [ -f pubspec.yaml ]; then
    dart pub get
    echo "  Workspace dependencies resolved"
else
    echo "  Skipped (not yet initialized)"
fi
cd ..

# 5. Git hooks
echo "[5/5] Installing git hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "  Pre-commit hooks installed"
else
    echo "  pre-commit not found, skipping"
fi

echo ""
echo "=== Bootstrap complete ==="
echo ""
echo "Start backend:  cd backend && uv run uvicorn app.main:create_app --factory --reload --port 8000"
echo "Start frontend: cd frontend && npm start"
echo "Start mobile:   cd mobile/apps/customer_app && flutter run"
