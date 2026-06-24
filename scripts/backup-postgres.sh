#!/bin/bash

set -e

mkdir -p backups/postgres

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker compose exec -T postgres pg_dump \
  -U ops_user \
  ops_platform \
  > backups/postgres/ops_platform_${TIMESTAMP}.sql

echo "PostgreSQL backup completed:"
echo "backups/postgres/ops_platform_${TIMESTAMP}.sql"