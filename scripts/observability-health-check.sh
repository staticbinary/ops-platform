#!/usr/bin/env bash

set -euo pipefail

echo "========================================="
echo "Ops Platform Observability Health Check"
echo "========================================="

check_http_status() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    local status_code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "${url}" || true)

    if [[ "${status_code}" == "${expected_status}" ]]; then
        echo "PASS: ${name} returned HTTP ${status_code}"
    else
        echo "FAIL: ${name} returned HTTP ${status_code}; expected HTTP ${expected_status}"
        exit 1
    fi
}

echo
echo "Checking observability endpoints..."

check_http_status "Prometheus" "http://localhost:9090/-/healthy"
check_http_status "Grafana" "http://localhost:3000/api/health"
check_http_status "Loki Metrics" "http://localhost:3100/metrics"
check_http_status "Tempo" "http://localhost:3200/ready"
check_http_status "cAdvisor" "http://localhost:8080/healthz"
check_http_status "Node Exporter" "http://localhost:9100/metrics"
check_http_status "PostgreSQL Exporter" "http://localhost:9187/metrics"
check_http_status "Blackbox Exporter" "http://localhost:9115/metrics"

echo
echo "========================================="
echo "Observability Status: HEALTHY"
echo "========================================="