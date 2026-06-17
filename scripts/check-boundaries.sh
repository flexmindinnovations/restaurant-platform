#!/usr/bin/env bash
set -euo pipefail

echo "=== Checking Architecture Boundaries ==="

echo "[Backend] import-linter..."
cd backend
uv run lint-imports

if [ -f ../frontend/package.json ]; then
    echo "[Frontend] Nx boundary rules..."
    cd ../frontend
    npx nx run-many --target=lint --all
fi

echo "=== All boundary checks passed ==="
