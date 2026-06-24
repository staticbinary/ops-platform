#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "======================================="
echo "Ops Platform Automated Test Suite"
echo "======================================="
echo

"$SCRIPT_DIR/test-platform.sh"

echo

"$SCRIPT_DIR/test-auth.sh"

echo

"$SCRIPT_DIR/test-rbac.sh"

echo

"$SCRIPT_DIR/test-assets.sh"

echo
echo "======================================="
echo "All automated tests passed"
echo "======================================="
echo