#!/usr/bin/env bash

set -euo pipefail

echo "========================================="
echo "Ops Platform Service Health Check"
echo "========================================="

check_service_running() {
    local service_name="$1"

    if docker compose ps --services --filter "status=running" | grep -qx "${service_name}"; then
        echo "PASS: ${service_name} is running"
    else
        echo "FAIL: ${service_name} is not running"
        echo
        echo "Current container status:"
        docker compose ps
        exit 1
    fi
}

check_container_health() {
    local container_name="$1"
    local service_label="$2"

    local health_status
    health_status=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${container_name}" 2>/dev/null || true)

    if [[ "${health_status}" == "healthy" ]]; then
        echo "PASS: ${service_label} health status is healthy"
    elif [[ "${health_status}" == "none" ]]; then
        echo "INFO: ${service_label} has no Docker healthcheck configured"
    else
        echo "FAIL: ${service_label} health status is ${health_status}"
        docker compose ps
        exit 1
    fi
}

echo
echo "Checking required services..."

REQUIRED_SERVICES=(
    "postgres"
    "asset_service"
    "auth_service"
    "reverse-proxy"
    "prometheus"
    "grafana"
    "loki"
    "tempo"
    "cadvisor"
    "node-exporter"
    "postgres-exporter"
    "blackbox-exporter"
    "promtail"
)

for service in "${REQUIRED_SERVICES[@]}"; do
    check_service_running "${service}"
done

echo
echo "Checking Docker health statuses..."

check_container_health "ops-postgres" "PostgreSQL"
check_container_health "ops-asset-service" "Asset Service"
check_container_health "ops-auth-service" "Auth Service"
check_container_health "ops-node-exporter" "Node Exporter"
check_container_health "ops-postgres-exporter" "PostgreSQL Exporter"
check_container_health "ops-blackbox-exporter" "Blackbox Exporter"

echo
echo "========================================="
echo "Service Status: HEALTHY"
echo "========================================="