#!/usr/bin/env bash

set -euo pipefail

echo "========================================="
echo "Ops Platform Daily Startup"
echo "========================================="

echo
echo "Starting platform containers..."
docker compose up -d

echo
echo "Verifying container status..."
docker compose ps

echo
echo "Running database health check..."
./scripts/database-health-check.sh

echo
echo "Waiting for Docker health checks to settle..."
sleep 20

echo
echo "Running service health check..."
./scripts/service-health-check.sh

echo
echo "Running observability health check..."
./scripts/observability-health-check.sh

echo
echo "Platform Access URLs:"
echo "Reverse Proxy: http://localhost:8000"
echo "Asset Service: http://localhost:8001"
echo "Auth Service: http://localhost:8002"
echo "Grafana: http://localhost:3000"
echo "Prometheus: http://localhost:9090"
echo "Loki: http://localhost:3100"
echo "Tempo: http://localhost:3200"
echo "cAdvisor: http://localhost:8080"
echo "Node Exporter: http://localhost:9100"
echo "PostgreSQL Exporter: http://localhost:9187"
echo "Blackbox Exporter: http://localhost:9115"

echo
echo "========================================="
echo "Daily Startup Completed"
echo "========================================="