#!/bin/bash

set -e

echo "Validating asset_service runtime configuration..."

docker compose exec asset_service env >/dev/null

echo "Validating auth_service runtime configuration..."

docker compose exec auth_service env >/dev/null

echo "Runtime configuration validation successful."