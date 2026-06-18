# Prometheus Target Down Runbook

## Status

Active

## Alert

- PrometheusTargetDown

## Severity

Critical

## Category

Observability

## Purpose

This runbook provides investigation and response procedures when Prometheus detects that one or more monitored targets are unavailable.

The objective is to restore monitoring visibility, identify the source of the outage, and ensure metrics collection resumes successfully.

---

## Detection

### Alert

- PrometheusTargetDown

### Trigger

promql
up == 0

### Data Source

Prometheus

### Dashboards

- Ops Platform - Platform Overview
- Ops Platform - Service Reliability

---

## Initial Assessment

Determine:

- Which target is down
- Duration of the outage
- Whether monitoring visibility is impacted
- Whether multiple targets are affected

Questions:

- Is only one target unavailable?
- Are multiple targets unavailable?
- Is Prometheus functioning normally?
- Is the target container running?

---

## Investigation

### Step 1 — Review Prometheus Targets

Open:

http://localhost:9090/targets

Review:

- Target status
- Scrape status
- Last scrape time
- Error messages

Determine:

- Which target is failing
- When failures began
- Whether failures are isolated or widespread

---

### Step 2 — Review Service Health

Validate service availability:

bash
docker compose ps

Review health endpoints:

http://localhost:8001/health
http://localhost:8002/health

Determine:

- Service status
- Container health
- Endpoint availability

---

### Step 3 — Review Container Logs

Review logs for affected services:

bash
docker compose logs asset_service --tail=100

bash
docker compose logs auth_service --tail=100

bash
docker compose logs prometheus --tail=100

Review for:

- Startup failures
- Connection errors
- Resource exhaustion
- Configuration issues

---

### Step 4 — Validate Prometheus Configuration

Validate configuration:

bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

Verify:

- Scrape targets
- Rule files
- Configuration syntax

Determine whether configuration changes introduced the failure.

---

### Step 5 — Validate Network Connectivity

Review target configuration:

yaml
scrape_configs:

Confirm:

- Target hostnames resolve correctly
- Target ports are reachable
- Containers share expected Docker networks

Investigate:

bash
docker network inspect ops-platform-network

---

## Validation

Confirm:

- Target status returns to UP
- Metrics are being scraped
- Dashboards populate successfully
- Alert clears automatically

Validate:

promql
up

Expected:

1 = healthy
0 = unavailable

---

## Containment

If monitoring visibility remains degraded:

### Immediate Actions

- Restart affected service
- Restart Prometheus if required
- Validate Docker networking
- Restore previous configuration if recent changes were made

### Evidence Preservation

Capture:

- Prometheus logs
- Service logs
- Alert timestamps
- Dashboard screenshots
- Investigation notes

---

## Recovery

Validate:

- Prometheus scrape targets are healthy
- Metrics collection resumes
- Dashboards display current data
- Alert clears automatically

Monitor:

- up
- scrape_duration_seconds
- scrape_samples_post_metric_relabeling

for at least 30 minutes following recovery.

---

## Escalation

Escalate immediately if:

- Multiple scrape targets are unavailable
- Prometheus fails to start
- Metrics collection remains interrupted
- Monitoring visibility cannot be restored

---

## Post-Incident Review

Document:

- Timeline
- Root cause
- Impact
- Detection effectiveness
- Response effectiveness
- Corrective actions

Reference:

- docs/18-security-incident-report-template.md
- docs/20-post-incident-review-template.md