# Alert Routing Review

## Phase

5.11.1 Security Operations Automation

## Alert Rule Source

Prometheus

Location:

infrastructure/monitoring/prometheus-alerts.yml

## Availability Alerts

| Alert | Severity | Category |
|---------|---------|---------|
| PrometheusTargetDown | Critical | Platform |
| AssetServiceDown | Critical | Platform |
| AuthServiceDown | Critical | Platform |
| cAdvisorDown | High | Platform |

## Security Alerts

| Alert | Severity | Category |
|---------|---------|---------|
| AuthenticationFailureSpike | High | Security |
| InvalidTokenSpike | High | Security |
| PermissionDeniedSpike | High | Security |
| RateLimitAbuseDetected | Medium | Security |
| PrivilegeEscalationActivity | Critical | Security |
| AssetService5xxErrors | High | Platform |

## Validation

Validated in Prometheus Rule Health view.

Date Validated:

2026-06-18

## Current Status

Alert rules operational.

Notification routing pending.

Incident runbooks pending.

Alert tuning pending.