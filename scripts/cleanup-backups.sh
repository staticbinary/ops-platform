#!/bin/bash

set -e

POSTGRES_RETENTION=30
AUTH_RETENTION=30

echo "Cleaning PostgreSQL backups..."

ls -1t backups/postgres/*.sql 2>/dev/null \
  | tail -n +$((POSTGRES_RETENTION + 1)) \
  | xargs -r rm -f

echo "Cleaning auth backups..."

ls -1t backups/auth/*.tar.gz 2>/dev/null \
  | tail -n +$((AUTH_RETENTION + 1)) \
  | xargs -r rm -f

echo "Backup retention cleanup completed."