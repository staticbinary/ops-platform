# Privilege Escalation Activity Runbook

## Status

Active

## Alert

PrivilegeEscalationActivity

## Severity

Critical

## Category

Security

## Purpose

This runbook provides investigation and response procedures when a privilege escalation attempt is detected within the Ops Platform.

The objective is to determine whether the activity represents:

* Misconfiguration
* Unauthorized access attempt
* Malicious activity
* Legitimate administrative testing

and to ensure platform integrity is maintained.

---

## Detection

### Alert


PrivilegeEscalationActivity


### Trigger

promql
sum(increase(privilege_escalation_attempt_total[5m])) >= 1

### Data Source

Prometheus

### Dashboard

Ops Platform - Security Operations

Ops Platform - Security Investigation

---

## Initial Assessment

Determine:

* Which user generated the event
* Source IP address
* Timestamp
* Target resource
* Requested privilege level

Questions:

* Was the request expected?
* Was administrative testing occurring?
* Has this source generated previous security events?

---

## Investigation

### Step 1 — Review Security Dashboard

Review:

Privilege Escalation Attempts
Permission Denials
Authentication Failures
Invalid Tokens

Look for related activity occurring within the same timeframe.

---

### Step 2 — Review Loki Logs

Search:

logql
{service=~".*auth.*|.*asset.*"} |= "privilege"

Review:

* request_id
* trace_id
* source IP
* user identity
* event details

---

### Step 3 — Trace Correlation

Using trace_id:

1. Open Tempo
2. Locate associated trace
3. Review request path
4. Identify service interactions
5. Determine source of escalation attempt

Validate whether the request originated from:

* UI workflow
* API request
* Automation
* Internal service communication

---

### Step 4 — Review Related Events

Investigate:

AuthenticationFailureSpike

InvalidTokenSpike

PermissionDeniedSpike


Determine whether the escalation attempt was part of a larger attack pattern.

---

## Validation

Confirm:

* User identity
* Source IP
* Trace path
* Request intent
* Authorization decision

Determine whether the activity was:

* Authorized
* Accidental
* Suspicious
* Malicious

---

## Containment

If malicious activity is suspected:

### Immediate Actions

* Disable affected account
* Revoke active tokens
* Block source IP if appropriate
* Notify platform administrators

### Evidence Preservation

Capture:

* Logs
* Trace IDs
* Alert timestamps
* User identifiers
* Investigation notes

---

## Recovery

Validate:

* No unauthorized access occurred
* Tokens are functioning normally
* RBAC enforcement remains operational
* Alert volume returns to baseline

Monitor:

privilege_escalation_attempt_total
permission_denied_total
invalid_token_total


for at least 30 minutes following containment.

---

## Escalation

Escalate immediately if:

* Multiple escalation attempts occur
* Administrative accounts are targeted
* Evidence of account compromise exists
* Multiple security alerts correlate to the same source

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