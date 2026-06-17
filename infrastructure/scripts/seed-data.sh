#!/usr/bin/env bash
set -euo pipefail

echo "Seeding development data..."

cd "$(dirname "$0")/../../backend"

# Run the backend seed command if it exists
if [ -f "app/initial_data.py" ]; then
    echo "Running backend seed script..."
    uv run python app/initial_data.py
else
    echo "Initial data/seed script not found. Please implement backend/app/initial_data.py."
fi

echo "Seeding process finished."
