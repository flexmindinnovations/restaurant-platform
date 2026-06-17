#!/usr/bin/env bash
set -euo pipefail

echo "=== Running All Tests ==="

echo ""
echo "[Backend] tests..."
cd backend
uv run pytest
cd ..

if [ -f frontend/package.json ]; then
    echo ""
    echo "[Frontend] tests..."
    cd frontend
    npx ng test --watch=false
    cd ..
fi

if [ -f mobile/pubspec.yaml ]; then
    echo ""
    echo "[Mobile] tests..."
    cd mobile
    dart run melos run test
    cd ..
fi

echo ""
echo "=== All tests passed ==="
