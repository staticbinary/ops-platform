#!/bin/bash

set -e

echo "Release Readiness Check"

echo "Starting pre-deployment validation..."
./scripts/pre-deploy-check.sh

echo ""
echo "Checking backup availability..."

ls backups/postgres/*.sql >/dev/null
ls backups/auth/*.tar.gz >/dev/null

echo "Backups available."

echo ""
echo "Running automated test suite..."
./scripts/tests/test-all.sh

echo ""
echo "Checking repository status..."

git status --short

echo ""
echo "======================================="
echo "Release readiness confirmed."
echo "======================================="