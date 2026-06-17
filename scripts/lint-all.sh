#!/usr/bin/env bash
set -euo pipefail

echo "=== Linting All ==="

echo ""
echo "[Backend] ruff..."
cd backend
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

echo "[Backend] mypy..."
uv run mypy src/

echo "[Backend] import boundaries..."
uv run lint-imports
cd ..

if [ -f frontend/package.json ]; then
    echo ""
    echo "[Frontend] eslint..."
    cd frontend
    npx ng lint
    cd ..
fi

if [ -f mobile/pubspec.yaml ]; then
    echo ""
    echo "[Mobile] dart analyze..."
    cd mobile
    dart run melos run analyze
    cd ..
fi

echo ""
echo "=== All lints passed ==="
