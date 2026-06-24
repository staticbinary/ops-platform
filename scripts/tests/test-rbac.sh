#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/test-config.sh"
source "$SCRIPT_DIR/test-utils.sh"

info "Starting RBAC tests"
TEST_RUN_ID="$(date +%s)"

get_token() {
    local email="$1"
    local password="$2"

    curl -s -X POST "$AUTH_BASE_URL/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$email\",\"password\":\"$password\"}" \
        | python -c 'import sys,json; print(json.load(sys.stdin)["access_token"])'
}

ADMIN_TOKEN=$(get_token "$TEST_ADMIN_USER" "$TEST_ADMIN_PASSWORD")
VIEWER_TOKEN=$(get_token "$TEST_VIEWER_USER" "$TEST_VIEWER_PASSWORD")

if [ -n "$ADMIN_TOKEN" ]; then
    pass "Admin token acquired"
else
    fail "Admin token acquisition failed"
fi

if [ -n "$VIEWER_TOKEN" ]; then
    pass "Viewer token acquired"
else
    fail "Viewer token acquisition failed"
fi

viewer_read_status=$(curl -s -o /dev/null -w "%{http_code}" \
    "$ASSET_BASE_URL/assets" \
    -H "Authorization: Bearer $VIEWER_TOKEN")

if [ "$viewer_read_status" -eq 200 ]; then
    pass "Viewer can read assets"
else
    fail "Viewer read returned HTTP $viewer_read_status"
fi

viewer_write_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$ASSET_BASE_URL/assets" \
    -H "Authorization: Bearer $VIEWER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "hostname": "viewer-rbac-denied-host",
        "owner": "phase-6-4",
        "status": "active"
    }')

if [ "$viewer_write_status" -eq 403 ]; then
    pass "Viewer denied asset creation"
else
    fail "Viewer write returned HTTP $viewer_write_status"
fi

admin_write_status=$(curl -s -o /tmp/rbac-admin-create-response.json -w "%{http_code}" \
    -X POST "$ASSET_BASE_URL/assets" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
    \"hostname\": \"viewer-rbac-denied-host-$TEST_RUN_ID\",
    \"owner\": \"phase-6-4\",
    \"status\": \"active\"
}")

if [ "$admin_write_status" -eq 200 ] || [ "$admin_write_status" -eq 201 ]; then
    pass "Admin can create assets"
else
    fail "Admin create returned HTTP $admin_write_status"
fi

admin_read_status=$(curl -s -o /dev/null -w "%{http_code}" \
    "$ASSET_BASE_URL/assets" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$admin_read_status" -eq 200 ]; then
    pass "Admin can read assets"
else
    fail "Admin read returned HTTP $admin_read_status"
fi

rm -f /tmp/rbac-admin-create-response.json

info "RBAC tests completed successfully"