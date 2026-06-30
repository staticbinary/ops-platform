# Security Testing Demo Scripts

## Demo Goal

Trigger controlled security events that appear in Grafana dashboards for:

* Authentication failures
* Invalid token attempts
* Permission denied events
* Rate limit activity
* Service health validation
* Request volume
* Error rate visibility

---

## 1. Authentication Failure Spike

### Purpose

Generate failed login attempts against the Auth Service.

### Command

bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST <http://localhost:8002/login> \
    -H "Content-Type: application/json" \
    -d '{"username":"bad-user","password":"wrong-password"}'
done

### Expected Result

401 responses

### Grafana Signal

auth_login_failure_total
AuthenticationFailureSpike
Security Operations Dashboard
Security Detection Dashboard
Security Response Dashboard

---

## 2. Invalid Token Activity

### Purpose

Generate invalid JWT/token events.

### Command

bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    <http://localhost:8002/me> \
    -H "Authorization: Bearer invalid-token-demo"
done

### Expected Result

401 responses

### Grafana Signal

invalid_token_total
InvalidTokenSpike
Security Operations Dashboard
Security Detection Dashboard
Security Response Dashboard

---

## 3. Asset Service Invalid Token Activity

### Purpose

Generate invalid token activity against the Asset Service.

### Command

bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    <http://localhost:8001/assets> \
    -H "Authorization: Bearer invalid-token-demo"
done

### Expected Result

401 responses

### Grafana Signal

invalid_token_total
Security Investigation Dashboard
Security Operations Dashboard

---

## 4. Permission Denied / RBAC Test

### Purpose

Generate permission denied events by authenticating as a non-admin user and accessing an admin-only endpoint.

### Step 1: Login as Viewer

bash
VIEWER_TOKEN=$(curl -s -X POST <http://localhost:8002/login> \
  -H "Content-Type: application/json" \
  -d '{"username":"viewer","password":"viewerpass"}' | jq -r '.access_token')

### Step 2: Attempt Admin Access

bash
for i in {1..5}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    <http://localhost:8002/admin> \
    -H "Authorization: Bearer $VIEWER_TOKEN"
done

### Expected Result

403 responses

### Grafana Signal

permission_denied_total
PermissionDeniedSpike
Security Operations Dashboard
Security Detection Dashboard
Security Response Dashboard

---

## 5. Rate Limit Test

### Purpose

Generate rate limit activity against a safe endpoint.

### Command

bash
for i in {1..130}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    <http://localhost:8001/health>
done

### Expected Result

Mostly 200 responses followed by 429 responses

### Grafana Signal

rate_limit_exceeded_total
RateLimitAbuse
Security Operations Dashboard
Security Detection Dashboard
Security Response Dashboard

---

## 6. Request Volume Spike

### Purpose

Generate normal traffic volume for dashboard visibility.

### Command

bash
for i in {1..50}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    <http://localhost:8001/health>

  curl -s -o /dev/null -w "%{http_code}\n" \
    <http://localhost:8002/health>
done

### Expected Result

200 responses

### Grafana Signal

http_requests_total
Request Volume panels
Service Reliability Dashboard
Platform Overview Dashboard

---

## 7. Readiness Validation Traffic

### Purpose

Generate health and readiness telemetry.

### Command

bash
curl -s <http://localhost:8001/health>
curl -s <http://localhost:8001/health/live>
curl -s <http://localhost:8001/health/ready>
curl -s <http://localhost:8001/health/startup>

curl -s <http://localhost:8002/health>

### Expected Result

Healthy service responses

### Grafana Signal

Service health panels
Availability panels
Readiness metrics
Platform Overview Dashboard
Service Reliability Dashboard

---

## 8. Mixed Security Demo Run

### Purpose

Run a compact demo that triggers several security dashboard signals.

### Command

bash
echo "Generating authentication failures..."
for i in {1..10}; do
  curl -s -o /dev/null -w "bad-login:%{http_code}\n" \
    -X POST <http://localhost:8002/login> \
    -H "Content-Type: application/json" \
    -d '{"username":"bad-user","password":"wrong-password"}'
done

echo "Generating invalid token events..."
for i in {1..10}; do
  curl -s -o /dev/null -w "invalid-token:%{http_code}\n" \
    <http://localhost:8002/me> \
    -H "Authorization: Bearer invalid-token-demo"
done

echo "Generating rate limit activity..."
for i in {1..130}; do
  curl -s -o /dev/null -w "rate-limit:%{http_code}\n" \
    <http://localhost:8001/health>
done

echo "Generating normal request volume..."
for i in {1..25}; do
  curl -s -o /dev/null -w "asset-health:%{http_code}\n" \
    <http://localhost:8001/health>

  curl -s -o /dev/null -w "auth-health:%{http_code}\n" \
    <http://localhost:8002/health>
done

echo "Security demo traffic complete."

### Expected Result

401 responses for failed login and invalid token attempts
429 responses during rate limit test
200 responses for normal health checks

### Grafana Signal

Authentication failures
Invalid tokens
Rate limit events
Request volume
Service health
Security detection panels
Security response panels

---

## 9. View Logs During Demo

### Purpose

Observe structured logs while running demo traffic.

### Command

bash
docker compose logs -f asset_service auth_service

### Expected Result

Structured JSON logs showing request, authentication, authorization, and rate limit events

---

## 10. Reset Demo Runtime

### Purpose

Stop and clean the demo runtime after testing.

### Preserve Data

bash
docker compose down

### Clean Environment

bash
docker compose down -v

Use `down -v` only when intentionally resetting volumes and runtime state.