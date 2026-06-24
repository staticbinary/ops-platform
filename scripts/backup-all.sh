#!/bin/bash

set -e

./scripts/backup-postgres.sh
./scripts/backup-auth.sh
./scripts/cleanup-backups.sh

echo ""
echo "All backups completed successfully."