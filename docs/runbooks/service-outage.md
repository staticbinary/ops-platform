# Service Outage Runbook

## Status

Active

## Alert

* AssetServiceDown
* AuthServiceDown
* AssetService5xxErrors

## Severity

Critical

## Category

Platform

## Purpose

This runbook provides investigation and response procedures when a platform service becomes unavailable or begins returning excessive server errors.

The objective is to restore service availability, identify the root cause, and minimize operational impact.

---

## Detection

### Alerts

* AssetServiceDown
* AuthServiceDown
* AssetService5xxErrors

### Data Source

Prometheus

### Dashboards

* Ops Platform - Platform Overview
* Ops Platform - Service Reliability
* Ops Platform - Security Investigation

---

## Initial Assessment

Determine:

* Which service is affected
* Duration of outage
* Current service availability
* User impact
* Error volume

Questions:

* Is the service completely unavailable?
* Is the service returning 5xx errors?
* Are dependent services affected?
* Is this a partial or full outage?

---

## Investigation

### Step 1 — Review Service Reliability Dashboard

Review:

* Service Availability
* Request Volume
* Error Rate
* Request Duration
* Container Health

Determine:

* When the issue began
* Whether degradation occurred before failure
* Whether multiple services are affected

---

### Step 2 — Review Loki Logs

Asset Service:

logql
{service="asset-service"}

Auth Service:

logql
{service="auth-service"}


Review:

* Error messages
* Exceptions
* Dependency failures
* Database connection issues
* Startup failures

Identify the first observable failure event.

---

### Step 3 — Review Tempo Traces

Using affected traces:

1. Open Tempo
2. Review failed requests
3. Identify failing spans
4. Determine service dependencies
5. Locate the failure point

Determine whether failures originate from:

* Application code
* Database connectivity
* External dependency failure
* Infrastructure issues

---

### Step 4 — Validate Container Health

Review container status:

bash
docker compose ps

Review logs:

bash
docker compose logs asset_service --tail=100

bash
docker compose logs auth_service --tail=100

Determine:

* Container health status
* Restart activity
* Startup failures
* Resource exhaustion

---

### Step 5 — Validate Database Health

Review PostgreSQL availability:

bash
docker compose ps postgres

Validate database connectivity through:

/api/assets/db-health

Determine:

* Database availability
* Connection failures
* Query failures
* Storage issues

---

## Validation

Confirm:

* Service health endpoints respond successfully
* Metrics are reporting normally
* Logs show no active failures
* Request traffic is processing successfully

Validate:

* /health
* /health/live
* /health/ready

---

## Containment

If service instability continues:

### Immediate Actions

* Restart affected service
* Restart dependent services if necessary
* Isolate failed components
* Increase monitoring frequency

### Evidence Preservation

Capture:

* Logs
* Trace IDs
* Dashboard screenshots
* Alert timestamps
* Investigation notes

---

## Recovery

Validate:

* Service availability returns to normal
* Error rates return to baseline
* Request latency stabilizes
* Database connectivity is restored
* Container health checks pass

Monitor:

* http_requests_total
* http_request_duration_seconds
* Service availability metrics
* Container health metrics

for at least 30 minutes following recovery.

---

## Escalation

Escalate immediately if:

* Multiple services are unavailable
* Database failure is involved
* Recovery actions are unsuccessful
* User impact continues after remediation

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

* docs/18-security-incident-report-template.md
* docs/20-post-incident-review-template.md