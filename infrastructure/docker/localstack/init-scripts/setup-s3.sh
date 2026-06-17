#!/bin/bash
# LocalStack initialization script — creates S3 buckets for local development
# This replaces the MinIO service (MinIO community edition was archived April 2026)

awslocal s3 mb s3://platform-assets-local
awslocal s3 mb s3://platform-documents-local

echo "S3 buckets created successfully"
