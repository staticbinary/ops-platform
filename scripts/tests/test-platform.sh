#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/test-config.sh"
source "$SCRIPT_DIR/test-utils.sh"

info "Starting platform smoke tests"

check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status" -eq "$expected_status" ]; then
        pass "$name"
    else
        fail "$name returned HTTP $status, expected $expected_status"
    fi
}

check_endpoint "Asset Service Health" "$ASSET_BASE_URL/health"
check_endpoint "Asset Service Readiness" "$ASSET_BASE_URL/health/ready"
check_endpoint "Auth Service Health" "$AUTH_BASE_URL/health"
check_endpoint "Prometheus Health" "$PROMETHEUS_BASE_URL/-/healthy"
check_endpoint "Grafana Health" "$GRAFANA_BASE_URL/api/health"
check_endpoint "Loki Readiness" "$LOKI_BASE_URL/ready"
check_endpoint "Tempo Readiness" "$TEMPO_BASE_URL/ready"

info "Platform smoke tests completed successfully"