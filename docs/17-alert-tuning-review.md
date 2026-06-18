# Alert Tuning Review

## Phase

5.11.3 Alert Tuning & Signal Quality

## Status

Complete

## Purpose

This document records the first alert tuning pass for the Ops Platform.

The goal of this phase was to reduce duplicate alerts, improve signal quality, align alert severity with operational impact, and reduce false-positive risk.

---

## Alert Tuning Summary

Before tuning:

- 10 Prometheus alert rules
- Duplicate target-down behavior
- Short outage detection windows
- Higher false-positive risk during restarts
- Invalid token activity classified as high severity

After tuning:

- 9 Prometheus alert rules
- Duplicate generic target-down alert removed
- Service-down alerts require longer persistence
- Observability degradation alert window increased
- Invalid token activity reclassified to medium severity
- 5xx alert persistence increased

---

## Rules File

Prometheus alert rules are defined in:

infrastructure/monitoring/prometheus-alerts.yml

Prometheus loads this file through:

infrastructure/monitoring/prometheus.yml

The file is mounted into the Prometheus container by:

docker-compose.yml

---

## Tuning Decisions

### Removed Generic Target Down Alert

Removed:

- PrometheusTargetDown

Reason:

The generic `up == 0` alert overlapped with service-specific alerts:

- AssetServiceDown
- AuthServiceDown
- cAdvisorDown

This could cause duplicate alert noise when a known platform target goes down.

Decision:

Use service-specific target alerts for now.

Future use:

Reintroduce a generic target-down alert later when additional scrape targets are added and routing can distinguish ownership.

---

### Asset Service Down

Alert:

- AssetServiceDown

Previous duration:

- 1m

Updated duration:

- 2m

Severity:

- Critical

Reason:

A short restart or Docker Compose operation could briefly interrupt the scrape target.

The 2-minute window reduces false positives while still detecting meaningful service outage conditions.

---

### Auth Service Down

Alert:

- AuthServiceDown

Previous duration:

- 1m

Updated duration:

- 2m

Severity:

- Critical

Reason:

Authentication service availability is critical, but short restarts should not immediately create incident-level alerts.

The 2-minute persistence window improves signal quality.

---

### cAdvisor Down

Alert:

- cAdvisorDown

Previous duration:

- 1m

Updated duration:

- 3m

Severity:

- High

Reason:

cAdvisor provides container observability, but application services can remain functional while cAdvisor is unavailable.

The alert remains important because container visibility is degraded, but the longer duration reduces noise during Docker restarts.

---

### Invalid Token Spike

Alert:

- InvalidTokenSpike

Previous severity:

- High

Updated severity:

- Medium

Threshold:

promql
sum(increase(invalid_token_total[5m])) >= 5

Reason:

Invalid token events can occur because of stale sessions, expired tokens, malformed requests, or client-side behavior.

This should still be investigated, but it is less severe than confirmed permission abuse or privilege escalation activity unless correlated with additional signals.

---

### Authentication Failure Spike

Alert:

- AuthenticationFailureSpike

Severity:

- High

Threshold:

promql
sum(increase(auth_login_failure_total[5m])) >= 5

Decision:

No change.

Reason:

Authentication failure spikes may indicate brute force activity, credential stuffing, user enumeration, or misconfigured clients.

This remains a high-priority security signal.

---

### Permission Denied Spike

Alert:

- PermissionDeniedSpike

Severity:

- High

Threshold:

promql
sum(increase(permission_denied_total[5m])) >= 5

Decision:

No change.

Reason:

Repeated permission denials may indicate RBAC probing, unauthorized access attempts, or role misconfiguration.

This remains more serious than invalid token activity because the user or client may already be authenticated.

---

### Rate Limit Abuse Detected

Alert:

- RateLimitAbuseDetected

Severity:

- Medium

Threshold:

promql
sum(increase(rate_limit_exceeded_total[5m])) >= 10

Decision:

No change.

Reason:

Rate limit events may be caused by legitimate load testing, buggy clients, automation loops, scanning, or abuse.

The current threshold is appropriate for the current lab environment.

Future tuning may increase the threshold after more baseline traffic data exists.

---

### Privilege Escalation Activity

Alert:

- PrivilegeEscalationActivity

Severity:

- Critical

Threshold:

promql
sum(increase(privilege_escalation_attempt_total[5m])) >= 1

Decision:

No change.

Reason:

Privilege escalation attempts should always trigger immediate investigation.

The threshold of one event is appropriate.

---

### Asset Service 5xx Errors

Alert:

- AssetService5xxErrors

Previous duration:

- 1m

Updated duration:

- 2m

Severity:

- High

Threshold:

promql
sum(increase(http_requests_total{service="asset-service",status="5xx"}[5m])) >= 3

Reason:

A small number of transient 5xx errors may occur during restarts, deployments, or isolated failures.

Requiring the condition to persist for 2 minutes reduces unnecessary alerts while retaining visibility into service instability.

Future improvement:

Convert this alert from a raw count threshold to an error-rate percentage once request volume increases.

---

## Final Alert Inventory

### Availability Alerts

| Alert | Severity | Duration | Runbook |
|---|---|---:|---|
| AssetServiceDown | Critical | 2m | docs/runbooks/service-outage.md |
| AuthServiceDown | Critical | 2m | docs/runbooks/service-outage.md |
| cAdvisorDown | High | 3m | docs/runbooks/service-outage.md |

### Security Alerts

| Alert | Severity | Duration | Runbook |
|---|---|---:|---|
| AuthenticationFailureSpike | High | 1m | docs/runbooks/authentication-failure-spike.md |
| InvalidTokenSpike | Medium | 1m | docs/runbooks/invalid-token-spike.md |
| PermissionDeniedSpike | High | 1m | docs/runbooks/permission-abuse.md |
| RateLimitAbuseDetected | Medium | 1m | docs/runbooks/rate-limit-abuse.md |
| PrivilegeEscalationActivity | Critical | 0m | docs/runbooks/privilege-escalation-activity.md |
| AssetService5xxErrors | High | 2m | docs/runbooks/service-outage.md |

---

## Validation

Validated Prometheus configuration with:

bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

Validation result:

SUCCESS: 9 rules found

Confirmed:

- Prometheus configuration is valid
- Alert rule file is mounted correctly
- Tuned alert rules are loaded
- Duplicate generic target-down rule was removed
- Rule count changed from 10 to 9

---

## Outcome

Phase 5.11.3 completed the first signal-quality improvement pass for Prometheus alerting.

The alerting model now better reflects operational severity:

- Critical alerts represent immediate platform or security incidents
- High alerts represent urgent investigation scenarios
- Medium alerts represent meaningful signals requiring review but not immediate incident escalation

The platform has moved from basic alert creation to tuned, response-oriented alerting.

---

## Future Improvements

Potential future tuning work:

- Convert 5xx alerting from raw count to error percentage
- Add source-IP-aware security alerts
- Add username-aware authentication failure detection
- Add composite alerts for correlated events
- Add environment labels
- Add owner/team labels
- Add dashboard links in alert annotations
- Add Alertmanager routing when notification routing is externalized
