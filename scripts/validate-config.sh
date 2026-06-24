#!/bin/bash

set -e

echo "Validating Docker Compose configuration..."

docker compose config >/dev/null

echo "Docker Compose configuration valid."