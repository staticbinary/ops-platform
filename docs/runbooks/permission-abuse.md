# Permission Abuse Runbook

## Status

Active

## Alert

PermissionDeniedSpike

## Severity

High

## Category

Security

## Purpose

This runbook provides investigation and response procedures when an abnormal volume of permission denied events is detected.

The objective is to determine whether authorization failures are caused by:

* RBAC misconfiguration
* Application defects
* User error
* Administrative misuse
* Privilege discovery attempts
* Malicious activity

and to ensure authorization controls are functioning correctly.

---

## Detection

### Alert

PermissionDeniedSpike

### Trigger

promql
sum(increase(permission_denied_total[5m])) >= 5

### Data Source

Prometheus

### Dashboard

Ops Platform - Security Operations

Ops Platform - Security Investigation

---

## Initial Assessment

Determine:

* Number of permission denied events
* Affected user accounts
* Source IP addresses
* Target endpoints
* Requested permissions

Questions:

* Is a single user affected?
* Are multiple users affected?
* Are admin endpoints being targeted?
* Is activity increasing over time?

---

## Investigation

### Step 1 — Review Security Dashboard

Review:

Permission Denials

Admin Endpoint Access

Privilege Escalation Attempts

Authentication Failures

Identify related activity occurring during the same timeframe.

---

### Step 2 — Review Loki Logs

Search:

logql
{service="auth-service"} |= "permission"

Review:

* request_id
* trace_id
* username
* role
* source IP
* requested resource
* required permission

Determine:

* Which resources were targeted
* Whether the request was expected
* Whether RBAC enforcement operated correctly

---

### Step 3 — Trace Correlation

Using trace_id:

1. Open Tempo
2. Locate associated trace
3. Review request path
4. Validate authorization workflow
5. Confirm denial decision

Determine whether activity originated from:

* User interface actions
* API requests
* Automation
* Internal service communication

---

### Step 4 — Review Related Alerts

Investigate:

AuthenticationFailureSpike

InvalidTokenSpike

PrivilegeEscalationActivity

Determine whether authorization failures are part of a larger security event.

---

## Validation

Confirm:

* User identity
* Assigned role
* Requested permission
* Expected permission set
* Authorization decision

Classify activity as:

* User error
* RBAC misconfiguration
* Application defect
* Suspicious activity
* Malicious activity

---

## Containment

If suspicious activity is detected:

### Immediate Actions

* Review affected accounts
* Review recent role changes
* Restrict access if necessary
* Investigate source systems

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

* RBAC enforcement is functioning correctly
* Permission denials return to normal levels
* No unauthorized access occurred
* User roles are correctly assigned

Monitor:

permission_denied_total

admin_endpoint_access_total

privilege_escalation_attempt_total

for at least 30 minutes following containment.

---

## Escalation

Escalate immediately if:

* Administrative resources are targeted
* Multiple users are involved
* Privilege escalation activity is detected
* Permission denial volume continues increasing

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