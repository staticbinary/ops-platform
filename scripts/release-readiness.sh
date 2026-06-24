#!/bin/bash

set -e

echo "Release Readiness Check"

./scripts/pre-deploy-check.sh

echo ""
echo "Checking backup availability..."

ls backups/postgres/*.sql >/dev/null
ls backups/auth/*.tar.gz >/dev/null

echo "Backups available."

echo ""
echo "Release readiness confirmed."
