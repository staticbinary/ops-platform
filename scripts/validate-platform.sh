#!/bin/bash

set -e

./scripts/validate-config.sh
./scripts/validate-runtime.sh
./scripts/validate-services.sh

echo ""
echo "Platform validation completed successfully."