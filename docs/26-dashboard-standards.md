# Dashboard Standards

## Purpose

This document defines the standards for creating, organizing, and maintaining Grafana dashboards within the Ops Platform.

The objective is to ensure dashboards remain focused, maintainable, operationally useful, and scalable as additional services, infrastructure, and Kubernetes are introduced.

---

# Core Principles

## Every panel must answer an operational question

Before adding a panel, answer:

- What question does this panel answer?
- Who would use it?
- During what situation would it be referenced?

If no clear operational purpose exists, the panel should not be added.

---

## Avoid duplicate information

Each metric should have a primary dashboard.

Other dashboards may summarize important information but should avoid duplicating detailed analysis.

Example:

Platform Overview

- Global 5xx Error Rate

Service Reliability

- 5xx Error Rate by Service
- Top 5xx Endpoints

---

## Prefer operational signals over implementation details

Prioritize information that helps operators make decisions.

Examples:

Good

- Service availability
- Request latency
- Error rates
- Authentication failures
- Database failures
- Recovery events
- Active alerts

Avoid

- Internal scrape frequency
- Metrics generated solely by monitoring infrastructure
- Counters that do not provide operational value

---

## Dashboard organization

Platform Overview

Question answered:

Is the platform healthy?

Contains:

- Service status
- Request rate
- Latency
- Error rate
- Basic resource utilization
- Platform health

---

Service Reliability

Question answered:

Which service is experiencing problems?

Contains:

- Service availability
- Health checks
- Readiness failures
- Database failures
- Recovery events
- Endpoint error rates

---

System Metrics

Question answered:

Is the infrastructure healthy?

Contains:

- CPU
- Memory
- Network
- Filesystem
- Container resource usage

---

Security Operations

Question answered:

Is suspicious activity occurring?

Contains:

- Authentication failures
- Invalid tokens
- Permission denials
- Rate limit violations
- Security event volume

---

Security Investigation

Question answered:

Why did the event occur?

Contains:

- Loki log searches
- Trace correlation
- Infrastructure events
- Critical events
- Timeline analysis

---

Security Response

Question answered:

What actions are required?

Contains:

- Active alerts
- Alert severity
- Platform status
- Response workflow
- Recovery monitoring

---

# Panel Standards

Each panel should define:

- Clear title
- Appropriate visualization
- Proper units
- Meaningful legend
- Accurate description
- Correct data source

---

# Metric Standards

Prefer current metrics.

Avoid deprecated metric names.

Prefer generic service labels over Docker-specific labels whenever possible.

Future dashboards should remain compatible with Kubernetes label conventions.

---

# Application Traffic

Unless specifically monitoring platform health, exclude:

- /metrics
- /health
- /health/live
- /health/ready
- /health/startup
- /docs
- /openapi.json

Application dashboards should focus on real application traffic.

---

# Dashboard Lifecycle

When creating new dashboards:

1. Define the operational question.
2. Identify required metrics.
3. Create the minimum useful panels.
4. Validate with automation scripts.
5. Remove duplicate panels.
6. Document significant changes.

---

# Future Enhancements

- Dashboard provisioning
- Data source provisioning
- Alert provisioning
- Folder provisioning
- Node Exporter
- Blackbox Exporter
- PostgreSQL monitoring
- Kubernetes dashboards
- Keycloak monitoring
- Wazuh integration
- Suricata integration
- Home NOC dashboards
- AI infrastructure dashboards
