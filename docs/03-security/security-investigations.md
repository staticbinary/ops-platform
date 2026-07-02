# Authentication Failure Investigation

## Detection

Trigger:

- Authentication Failure Spike Alert

Metrics:

- auth_login_failure_total

Dashboard:

- Ops Platform - Security Detection

---

## Initial Triage

Determine:

- When did failures begin?
- Is the activity ongoing?
- Is the activity isolated or widespread?

Review:

- Authentication Failures (5m)
- Invalid Tokens (5m)

---

## Investigation

### Step 1: Locate Events

Grafana → Explore → Loki

Query:

```logql
{service="auth-service"} |= "auth.failed"

Identify:

username
source IP
request path
trace_id
Step 2: Trace Analysis

Grafana → Explore → Tempo

Search:

trace_id from event

Review:

request flow
service interactions
error spans
Step 3: Log Correlation

Grafana → Explore → Loki

Query:

{service=~".*"} |= "<trace_id>"

Review:

request.started
auth.failed
request.completed
Validation

Determine:

Invalid credentials?
Expired token?
Service issue?
Malicious activity?
Response

Possible actions:

Notify security team
Block source IP
Investigate account activity
Escalate incident
Recovery

Confirm:

Failure rate returns to baseline
No ongoing abuse detected

---

# Permission Abuse Investigation

Use:

```markdown
Metrics:
- permission_denied_total

Logs:
- permission.denied

Dashboard:
- Permission Denied Events (5m)

Workflow:

Alert
↓
Locate permission.denied
↓
Extract trace_id
↓
Open trace
↓
Determine endpoint
↓
Determine user role
↓
Determine abuse vs normal behavior
Invalid Token Investigation

Use:

Metrics:
- invalid_token_total
- expired_token_total

Logs:
- token.invalid
- token.expired

Determine:

User error?
Expired token?
Automated attack?
Replay attempt?
Rate Limit Abuse Investigation

Use:

Metrics:
- rate_limit_exceeded_total

Logs:
- rate_limit.exceeded

Determine:

Single IP?
Multiple IPs?
Specific endpoint?
Credential stuffing?
Bot activity?
Privilege Escalation Investigation

Use:

Metrics:
- privilege_escalation_attempt_total

Logs:
- permission.denied
- role_change_total
- user_management_action_total

Determine:

Role modification attempt?
Admin endpoint access?
Unauthorized role assignment?

# Trace-Centric Investigation Workflow

## Entry Point

Sources:

- Security Detection Dashboard
- Security Investigation Dashboard
- Grafana Alerts

---

## Investigation

### Step 1

Identify:

- Event Type
- Service
- Timestamp

---

### Step 2

Open Grafana Explore → Loki

Query:

{service=~".*asset.*|.*auth.*"} |= "trace_id"

Locate:

- trace_id
- span_id

---

### Step 3

Open Grafana Explore → Tempo

Search:

- trace_id

Review:

- spans
- timing
- service interactions

---

### Step 4

Return to Loki

Search:

"<trace_id>"

Review:

- request.started
- security events
- dependency events
- request.completed

---

## Outcome

Determine:

- Root Cause
- Affected Service
- Affected Endpoint
- Security Impact