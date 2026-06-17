#!/usr/bin/env bash
set -euo pipefail

echo "Setting up local development infrastructure..."

cd "$(dirname "$0")/../docker"
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
echo "  Valkey:      localhost:6379 (Redis-compatible)"
echo "  LocalStack:  localhost:4566 (S3, SQS, SNS, SES, Secrets Manager)"
echo "  Mailpit:     localhost:8025 (SMTP on 1025)"
