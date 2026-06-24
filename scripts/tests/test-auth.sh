#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/test-config.sh"
source "$SCRIPT_DIR/test-utils.sh"

info "Starting authentication tests"

login_status=$(curl -s -o /tmp/auth-login-response.json -w "%{http_code}" \
    -X POST "$AUTH_BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email":"admintest@test.com",
        "password":"Password123!"
    }')

if [ "$login_status" -eq 200 ]; then
    pass "Valid admin login"
else
    fail "Valid admin login returned HTTP $login_status"
fi

TOKEN=$(python -c 'import json; print(json.load(open("/tmp/auth-login-response.json"))["access_token"])')

if [ -n "$TOKEN" ]; then
    pass "JWT token returned"
else
    fail "JWT token was empty"
fi

me_status=$(curl -s -o /dev/null -w "%{http_code}" \
    "$AUTH_BASE_URL/me" \
    -H "Authorization: Bearer $TOKEN")

if [ "$me_status" -eq 200 ]; then
    pass "Token validation with /me"
else
    fail "Token validation returned HTTP $me_status"
fi

invalid_password_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$AUTH_BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email":"admintest@test.com",
        "password":"WrongPassword123!"
    }')

if [ "$invalid_password_status" -eq 401 ]; then
    pass "Invalid password rejected"
else
    fail "Invalid password returned HTTP $invalid_password_status"
fi

invalid_user_status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$AUTH_BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email":"not-a-real-user@test.com",
        "password":"Password123!"
    }')

if [ "$invalid_user_status" -eq 401 ]; then
    pass "Invalid user rejected"
else
    fail "Invalid user returned HTTP $invalid_user_status"
fi

rm -f /tmp/auth-login-response.json

info "Authentication tests completed successfully"