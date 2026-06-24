#!/bin/bash

set -e

echo "Starting pre-deployment validation..."

./scripts/validate-platform.sh

echo ""
echo "Checking repository status..."

git diff --quiet

echo "Repository clean."

echo ""
echo "Pre-deployment validation successful."