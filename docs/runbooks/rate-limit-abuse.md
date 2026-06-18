# Rate Limit Abuse Runbook

## Status

Active

## Alert

RateLimitAbuseDetected

## Severity

Medium

## Category

Security

## Purpose

This runbook provides investigation and response procedures when excessive rate limit violations are detected.

The objective is to determine whether the activity is caused by:

* Legitimate load testing
* Application defects
* Misconfigured clients
* Automated scanning
* Brute force activity
* Denial-of-service behavior

and to ensure platform availability is maintained.

---

## Detection

### Alert

RateLimitAbuseDetected

### Trigger

promql
sum(increase(rate_limit_exceeded_total[5m])) >= 10


### Data Source

Prometheus

### Dashboard

Ops Platform - Security Operations

Ops Platform - Security Investigation

---

## Initial Assessment

Determine:

* Number of rate limit violations
* Time window of activity
* Source IP addresses
* Target endpoints
* Request volume trends

Questions:

* Is activity originating from one source?
* Are multiple sources involved?
* Is a load test currently running?
* Is application behavior expected?

---

## Investigation

### Step 1 — Review Security Dashboard

Review:

Rate Limit Violations

Request Volume

Error Rates

Authentication Failures

Determine whether request volume has increased significantly.

---

### Step 2 — Review Loki Logs

Search:

logql
{service="asset-service"} |= "rate_limit"

Review:

* request_id
* trace_id
* source IP
* endpoint
* request method
* rate limit event details

Determine:

* Most active source IPs
* Most targeted endpoints
* Request patterns
* Repeated abuse behavior

---

### Step 3 — Trace Correlation

Using trace_id:

1. Open Tempo
2. Locate associated trace
3. Review request execution path
4. Identify targeted services
5. Confirm rate limit enforcement

Validate whether activity originated from:

* User requests
* API integrations
* Automation
* Internal services

---

### Step 4 — Review Related Alerts

Investigate:

AuthenticationFailureSpike

InvalidTokenSpike

PermissionDeniedSpike

Determine whether rate limit violations are associated with a larger attack pattern.

---

## Validation

Confirm:

* Source IP addresses
* Target endpoints
* Request volume
* Service health
* Rate limiting functionality

Classify activity as:

* Expected traffic
* Load testing
* Client misconfiguration
* Suspicious activity
* Malicious activity

---

## Containment

If abuse is confirmed:

### Immediate Actions

* Block offending source IPs if appropriate
* Increase monitoring frequency
* Notify platform administrators
* Review affected endpoints

### Evidence Preservation

Capture:

* Logs
* Trace IDs
* Source IP addresses
* Alert timestamps
* Investigation notes

---

## Recovery

Validate:

* Request volume returns to normal
* Rate limit violations decrease
* Services remain healthy
* Response latency stabilizes

Monitor:

rate_limit_exceeded_total

http_requests_total

http_request_duration_seconds

for at least 30 minutes following containment.

---

## Escalation

Escalate immediately if:

* Multiple sources are involved
* Request volume continues increasing
* Service degradation occurs
* Denial-of-service activity is suspected

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