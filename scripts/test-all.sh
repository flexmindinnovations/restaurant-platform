#!/usr/bin/env bash
set -euo pipefail

echo "=== Running All Tests ==="

echo "[Backend] tests..."
cd backend
uv run pytest
cd ..

if [ -f frontend/package.json ]; then
    echo "[Frontend] tests..."
    cd frontend
    npx nx run-many --target=test --all
    cd ..
fi

if [ -f mobile/melos.yaml ]; then
    echo "[Mobile] tests..."
    cd mobile
    melos run test
    cd ..
fi

echo "=== All tests passed ==="
