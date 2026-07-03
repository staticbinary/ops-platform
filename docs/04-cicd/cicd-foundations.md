# CI/CD Foundations

## Purpose

This document defines continuous integration and continuous delivery standards for the Ops Platform.

Objectives:

- Standardize deployment workflows
- Define deployment validation requirements
- Reduce deployment risk
- Automate quality checks
- Improve platform reliability

## Deployment Workflow

Development Workflow:

1. Make changes
2. Run validation scripts
3. Review configuration changes
4. Commit changes
5. Push to repository
6. Execute deployment
7. Validate platform health

Current Deployment Model:

Manual Deployment

Future Deployment Model:

Automated CI/CD Pipeline

## Deployment Gates

The following checks must pass before deployment:

### Configuration Validation

bash
./scripts/validate-config.sh

./scripts/validate-runtime.sh

./scripts/validate-services.sh

./scripts/validate-platform.sh

---

# Quality Standards

markdown

## Quality Standards

Deployments should satisfy:

- No unhealthy services
- No failed configuration validation
- No unresolved secrets issues
- No unresolved backup failures
- No configuration drift
- Repository in clean state

## Deployment Validation Framework

### Pre-Deployment Validation

Purpose:

Validate platform readiness before deployment activities occur.

Validation Script:

scripts/pre-deploy-check.sh

Checks:

- Docker Compose configuration validation
- Runtime configuration validation
- Service health validation
- Platform validation
- Repository cleanliness validation

Validation Flow:

Validate Configuration
        ↓
Validate Runtime
        ↓
Validate Services
        ↓
Validate Platform
        ↓
Validate Repository State

### Post-Deployment Validation

Purpose:

Validate platform functionality after deployment completion.

Validation Script:

scripts/post-deploy-check.sh

Checks:

- Platform validation
- Asset service readiness
- Auth service health
- Service availability

Validation Flow:

Deployment Complete
        ↓
Validate Platform
        ↓
Validate Readiness Endpoints
        ↓
Confirm Service Availability

---

## Release Readiness Framework

Purpose:

Determine whether the platform is safe to release.

Validation Script:

scripts/release-readiness.sh

Checks:

- Pre-deployment validation successful
- Backup availability confirmed
- Repository state validated
- Service health validated
- Platform validation successful

Release Workflow:

Developer Change
        ↓
Pre-Deployment Validation
        ↓
Deployment
        ↓
Post-Deployment Validation
        ↓
Backup Verification
        ↓
Release Readiness Confirmation

Release Criteria:

- No unhealthy services
- No configuration validation failures
- No runtime validation failures
- No deployment validation failures
- Backups available
- Repository clean

---

## Operational Validation Tooling

Current Validation Scripts:

scripts/

validate-config.sh
validate-runtime.sh
validate-services.sh
validate-platform.sh

pre-deploy-check.sh
post-deploy-check.sh

release-readiness.sh

Current Backup Scripts:

scripts/

backup-postgres.sh
backup-auth.sh
backup-all.sh
cleanup-backups.sh

---

## CI/CD Maturity Progression

Phase 6.3 establishes the foundational deployment workflow for future CI/CD automation.

Current State:

Manual Validation
        ↓
Manual Deployment
        ↓
Manual Post-Deployment Verification

Future State:

Git Commit
        ↓
Automated Validation
        ↓
Automated Testing
        ↓
Deployment Approval
        ↓
Automated Deployment
        ↓
Post-Deployment Verification

Future Integrations:

- GitHub Actions
- Automated Testing Pipeline
- Deployment Automation
- Release Approval Gates
- Deployment Rollback Procedures

## Configuration Drift Case Study

### Scenario

A PostgreSQL credential change introduced a mismatch between runtime configuration and persistent database credentials.

### Symptoms

* Asset service unhealthy
* Readiness endpoint returned 503
* Database unavailable status
* PostgreSQL authentication failures

### Root Cause

Environment configuration was updated, but credentials stored within the initialized PostgreSQL volume remained unchanged.

### Resolution

Restored matching database credentials and recreated affected services.

### Outcome

The deployment validation framework successfully detected the issue before it could progress further into the deployment lifecycle.

### Lesson Learned

Configuration validation and deployment gates provide early detection of operational issues and reduce deployment risk.

---

# Phase 6.9 CI/CD Modernization

The CI/CD pipeline has been expanded beyond basic configuration validation into a multi-stage platform validation workflow.

Current validation stages include:

```text
Repository Validation
        │
        ├──────────────┐
        ▼              ▼
Docker Compose     Observability
Validation         Configuration Validation
        │              │
        └──────┬───────┘
               ▼
      Platform Runtime Validation
```

This structure provides fast failure detection while keeping each stage focused on a specific aspect of the platform.

---

# Repository Validation

The Repository Validation stage performs static validation before any containers are started.

Validation includes:

- Repository structure
- Documentation directory structure
- Infrastructure directory structure
- Docker Compose files
- Shell script syntax
- Python source compilation
- Grafana dashboard JSON validation

This stage is intended to detect repository issues as early as possible.

---

# Docker Compose Validation

The Docker Compose Validation stage verifies that the platform configuration can be successfully rendered.

Validation includes:

- Environment variable generation
- Docker Compose configuration parsing
- Compose dependency validation

This stage ensures the deployment configuration is valid before runtime testing begins.

---

# Observability Configuration Validation

Observability components are validated independently from runtime testing.

Validation includes:

- Grafana provisioning
- Dashboard configuration
- Prometheus alert rules
- Prometheus rule syntax using `promtool`

Separating observability validation allows configuration errors to be detected before the platform is started.

---

# Platform Runtime Validation

The final stage launches the complete platform and performs operational validation.

Rather than duplicating individual commands, CI now executes the same operational workflow used during local development.

The platform startup process includes:

- Platform startup
- Database health validation
- Service health validation
- Observability health validation

Additional runtime validation includes:

- Asset Service health endpoint
- Asset Service readiness endpoint
- Authentication Service health endpoint
- Prometheus scrape targets
- Blackbox monitoring metrics

Using the same operational scripts locally and in CI ensures both environments validate the platform consistently.

---

# Operational Validation Scripts

Phase 6.9 introduced standardized operational validation scripts.

| Script | Purpose |
|---------|---------|
| `daily-startup.sh` | Complete platform startup workflow |
| `database-health-check.sh` | PostgreSQL and Alembic validation |
| `service-health-check.sh` | Platform service validation |
| `observability-health-check.sh` | Monitoring stack validation |

These scripts provide a consistent operational workflow for both developers and CI pipelines.

---

# Failure Diagnostics

If runtime validation fails, GitHub Actions automatically collects diagnostic information from platform services.

Collected logs include:

- PostgreSQL
- PostgreSQL Exporter
- Node Exporter
- Blackbox Exporter
- cAdvisor
- Asset Service
- Authentication Service
- Reverse Proxy
- Prometheus
- Grafana
- Loki
- Promtail
- Tempo

Automatic log collection significantly reduces troubleshooting time when CI failures occur.

---

# CI/CD Philosophy

The Ops Platform CI/CD pipeline follows a layered validation approach.

```text
Repository
      │
      ▼
Configuration
      │
      ▼
Infrastructure
      │
      ▼
Platform
      │
      ▼
Operations
```

Each stage validates a progressively more complete portion of the platform.

This approach minimizes failed deployments, improves troubleshooting efficiency, and ensures that operational validation remains consistent between local development and continuous integration environments.