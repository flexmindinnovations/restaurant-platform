#!/usr/bin/env bash
set -euo pipefail

echo "Setting up local development infrastructure..."

# 1. Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker CLI is not installed. Please install Docker first."
    exit 1
fi

# 2. Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running. Please start Docker."
    exit 1
fi

cd "$(dirname "$0")/../docker"
echo "Starting Docker Compose services..."
docker compose up -d

echo "Waiting for PostgreSQL to be ready..."
until docker exec rp-postgres pg_isready -U platform -d restaurant_platform > /dev/null 2>&1; do
    sleep 1
done

echo "Waiting for Valkey (Redis-compatible) to be ready..."
until docker exec rp-redis valkey-cli ping > /dev/null 2>&1; do
    sleep 1
done

echo ""
echo "Local services are ready:"
echo "  PostgreSQL:  localhost:5432"
echo "  Valkey:      localhost:6379"
echo "  LocalStack:  localhost:4566 (S3, SQS, SNS, SES, Secrets Manager)"
echo "  Mailpit:     localhost:8025 (SMTP on 1025)"
echo ""

# Run migrations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/run-migrations.sh" ]; then
    echo "Invoking database migrations..."
    bash "$SCRIPT_DIR/run-migrations.sh"
else
    echo "Warning: run-migrations.sh not found, skipping migrations."
fi
