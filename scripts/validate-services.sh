#!/bin/bash

set -e

echo "Validating service health..."

docker compose ps

UNHEALTHY_SERVICES=$(docker compose ps --format json | grep -i "unhealthy" || true)

if [ -n "$UNHEALTHY_SERVICES" ]; then
  echo ""
  echo "ERROR: One or more services are unhealthy."
  echo "$UNHEALTHY_SERVICES"
  exit 1
fi

echo "Service validation complete."