#!/usr/bin/env bash

set -euo pipefail

echo "========================================="
echo "Ops Platform Database Health Check"
echo "========================================="

echo
echo "Checking PostgreSQL container..."
docker compose ps postgres

echo
echo "Checking PostgreSQL readiness..."
docker compose exec postgres pg_isready -U ops_user -d ops_platform

echo
echo "Checking required database tables..."

REQUIRED_TABLES=("alembic_version" "assets" "audit_logs")

for table in "${REQUIRED_TABLES[@]}"; do
    if docker compose exec -T postgres psql -U ops_user -d ops_platform -tAc "SELECT to_regclass('public.${table}');" | grep -q "${table}"; then
        echo "PASS: ${table} table exists"
    else
        echo "FAIL: ${table} table is missing"
        exit 1
    fi
done

echo
echo "Checking current Alembic revision..."

CURRENT_REVISION=$(docker compose exec -T postgres psql -U ops_user -d ops_platform -tAc "SELECT version_num FROM alembic_version;")

echo "Current migration revision: ${CURRENT_REVISION}"

echo "========================================="
echo "Database Status: HEALTHY"
echo "========================================="