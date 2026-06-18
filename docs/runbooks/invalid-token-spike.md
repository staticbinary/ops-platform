# Invalid Token Spike Runbook

## Status

Active

## Alert

InvalidTokenSpike

## Severity

High

## Category

Security

## Purpose

This runbook provides investigation and response procedures when an abnormal volume of invalid token events is detected.

The objective is to determine whether invalid token activity is caused by:

* Expired tokens
* Misconfigured clients
* Stale application sessions
* Token replay attempts
* Malicious authentication abuse

and to ensure the integrity of platform authentication mechanisms.

---

## Detection

### Alert

InvalidTokenSpike

### Trigger

promql
sum(increase(invalid_token_total[5m])) >= 5


### Data Source

Prometheus

### Dashboard

Ops Platform - Security Operations

Ops Platform - Security Investigation

---

## Initial Assessment

Determine:

* Number of invalid token events
* Time window of activity
* Source IP addresses
* Affected user accounts
* Associated services

Questions:

* Are events isolated to a single user?
* Are multiple users affected?
* Is a client application malfunctioning?
* Is activity continuing to increase?

---

## Investigation

### Step 1 — Review Security Dashboard

Review:

Invalid Tokens

Authentication Failures

Permission Denials

Privilege Escalation Attempts

Look for correlated security activity within the same timeframe.

---

### Step 2 — Review Loki Logs

Search:

logql
{service="auth-service"} |= "invalid_token"

Review:

* request_id
* trace_id
* source IP
* user identity
* token validation details

Determine:

* Invalid token
* Malformed token
* Expired token
* Missing token
* Unexpected authorization behavior

---

### Step 3 — Trace Correlation

Using trace_id:

1. Open Tempo
2. Locate associated trace
3. Follow request execution path
4. Review authentication workflow
5. Identify service interactions

Validate whether failures originated from:

* User requests
* Application requests
* Automation workflows
* Internal service communication

---

### Step 4 — Review Related Alerts

Investigate:

AuthenticationFailureSpike

PermissionDeniedSpike

PrivilegeEscalationActivity

Determine whether invalid token activity is part of a broader security event.

---

## Validation

Confirm:

* User identity
* Source IP address
* Token type
* Authentication flow behavior
* Service health

Classify activity as:

* Expired token usage
* Client-side application issue
* Configuration issue
* Suspicious activity
* Malicious activity

---

## Containment

If suspicious or malicious activity is suspected:

### Immediate Actions

* Revoke affected tokens
* Force user reauthentication
* Investigate source systems
* Block source IP if appropriate

### Evidence Preservation

Capture:

* Logs
* Trace IDs
* User identifiers
* Alert timestamps
* Investigation notes

---

## Recovery

Validate:

* Invalid token events decrease
* Authentication success rates normalize
* Token issuance functions correctly
* Services remain healthy

Monitor:

invalid_token_total

expired_token_total

auth_login_success_total

auth_login_failure_total

for at least 30 minutes following containment.

---

## Escalation

Escalate immediately if:

* Multiple users are affected
* Invalid token volume continues increasing
* Token replay activity is suspected
* Additional security alerts correlate to the same source

---

## Post-Incident Review

Document:

* Timeline
* Root cause
* Impact
* Detection effectiveness
* Response effectiveness
* Corrective actions

Reference:

docs/18-security-incident-report-template.md

docs/20-post-incident-review-template.md