# Authentication Failure Spike Runbook

## Status

Active

## Alert

AuthenticationFailureSpike

## Severity

High

## Category

Security

## Purpose

This runbook provides investigation and response procedures when an abnormal volume of authentication failures is detected.

The objective is to determine whether the failures are caused by:

* User error
* Application issues
* Credential stuffing
* Brute force activity
* Service degradation

and to prevent unauthorized access attempts.

---

## Detection

### Alert

AuthenticationFailureSpike

### Trigger

promql
sum(increase(auth_login_failure_total[5m])) >= 5


### Data Source

Prometheus

### Dashboard

Ops Platform - Security Operations

Ops Platform - Security Investigation

---

## Initial Assessment

Determine:

* Number of failed login attempts
* Time window of activity
* Source IP addresses
* Affected user accounts
* Geographic concentration (if available)

Questions:

* Is activity isolated to a single account?
* Are multiple accounts affected?
* Is activity originating from one source or many?
* Are failures continuing to increase?

---

## Investigation

### Step 1 — Review Security Dashboard

Review:

Authentication Failures

Invalid Tokens

Permission Denials

Rate Limit Violations


Identify related activity within the same timeframe.

---

### Step 2 — Review Loki Logs

Search:

logql
{service="auth-service"} |= "authentication"


Review:

* request_id
* trace_id
* username
* source IP
* failure reason

Determine:

* user_not_found
* wrong_password
* other authentication failures

---

### Step 3 — Trace Correlation

Using trace_id:

1. Open Tempo
2. Locate associated trace
3. Follow request path
4. Confirm authentication workflow execution
5. Identify service-side failures

Validate whether failures are:

* Legitimate credential failures
* Application defects
* Service communication issues

---

### Step 4 — Review Related Alerts

Investigate:

InvalidTokenSpike

PermissionDeniedSpike

RateLimitAbuseDetected


Determine whether authentication failures are part of a broader attack pattern.

---

## Validation

Confirm:

* User identities involved
* Source IP addresses
* Failure reasons
* Service health
* Trace behavior

Classify activity as:

* User error
* Operational issue
* Suspicious activity
* Malicious activity

---

## Containment

If malicious activity is suspected:

### Immediate Actions

* Monitor affected accounts
* Enforce rate limiting
* Temporarily disable compromised accounts if necessary
* Block source IP if appropriate

### Evidence Preservation

Capture:

* Authentication logs
* Trace IDs
* Source IP addresses
* Alert timestamps
* Investigation notes

---

## Recovery

Validate:

* Authentication success rates normalize
* Login failures decrease
* Services remain healthy
* No unauthorized access occurred

Monitor:

auth_login_failure_total
auth_login_success_total
rate_limit_exceeded_total

for at least 30 minutes after containment.

---

## Escalation

Escalate immediately if:

* Multiple accounts are targeted
* Login failures continue increasing
* Credential stuffing is suspected
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