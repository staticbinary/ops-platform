#!/bin/bash

set -e

echo "Starting post-deployment validation..."

./scripts/validate-platform.sh

echo ""
echo "Checking application readiness..."

curl -fs http://localhost:8001/health/ready >/dev/null
curl -fs http://localhost:8002/health >/dev/null

echo "Application health checks successful."

echo ""
echo "Post-deployment validation successful."