#!/bin/bash

set -e

mkdir -p backups/auth

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker run --rm \
  -v ops-platform_auth-data:/source \
  -v $(pwd)/backups/auth:/backup \
  alpine \
  tar czf /backup/auth-data-backup_${TIMESTAMP}.tar.gz \
  -C /source .

echo "Auth backup completed:"
echo "backups/auth/auth-data-backup_${TIMESTAMP}.tar.gz"