#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/test-config.sh"
source "$SCRIPT_DIR/test-utils.sh"

info "Starting asset CRUD tests"

ADMIN_TOKEN=$(curl -s -X POST "$AUTH_BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_ADMIN_USER\",\"password\":\"$TEST_ADMIN_PASSWORD\"}" \
    | python -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

if [ -n "$ADMIN_TOKEN" ]; then
    pass "Admin token acquired"
else
    fail "Admin token acquisition failed"
fi

create_status=$(curl -s -o /tmp/asset-create-response.json -w "%{http_code}" \
    -X POST "$ASSET_BASE_URL/assets" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "hostname": "asset-crud-test-host",
        "owner": "phase-6-4",
        "status": "active"
    }')

if [ "$create_status" -eq 200 ] || [ "$create_status" -eq 201 ]; then
    pass "Asset created"
else
    fail "Asset create returned HTTP $create_status"
fi

ASSET_ID=$(python -c 'import json; print(json.load(open("/tmp/asset-create-response.json"))["id"])')

if [ -n "$ASSET_ID" ]; then
    pass "Asset ID captured: $ASSET_ID"
else
    fail "Asset ID capture failed"
fi

read_status=$(curl -s -o /dev/null -w "%{http_code}" \
    "$ASSET_BASE_URL/assets/$ASSET_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$read_status" -eq 200 ]; then
    pass "Asset read by ID"
else
    fail "Asset read returned HTTP $read_status"
fi

update_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X PUT "$ASSET_BASE_URL/assets/$ASSET_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "hostname": "asset-crud-test-host-updated",
        "owner": "phase-6-4",
        "status": "inactive"
    }')

if [ "$update_status" -eq 200 ]; then
    pass "Asset updated"
else
    fail "Asset update returned HTTP $update_status"
fi

delete_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X DELETE "$ASSET_BASE_URL/assets/$ASSET_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$delete_status" -eq 200 ]; then
    pass "Asset deleted"
else
    fail "Asset delete returned HTTP $delete_status"
fi

verify_delete_status=$(curl -s -o /dev/null -w "%{http_code}" \
    "$ASSET_BASE_URL/assets/$ASSET_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$verify_delete_status" -eq 404 ]; then
    pass "Deleted asset returns 404"
else
    fail "Deleted asset check returned HTTP $verify_delete_status"
fi

rm -f /tmp/asset-create-response.json

info "Asset CRUD tests completed successfully"