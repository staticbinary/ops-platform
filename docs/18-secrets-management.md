# Secrets Management Strategy

## Purpose

This document defines the secrets management standards for Ops Platform.

Objectives:

- Eliminate undocumented secrets
- Reduce exposure risk
- Support credential rotation
- Establish ownership and usage standards
- Prepare for future production-grade secrets management solutions

This document serves as the source of truth for secret handling within the platform.

## Secret Classification Matrix

| Classification | Description | Examples |
|---------------|-------------|----------|
| Critical | Compromise grants administrative or platform-wide access | JWT signing keys, database passwords |
| High | Compromise affects security monitoring or operational visibility | Grafana admin credentials, SMTP credentials |
| Medium | Internal service credentials | Service account tokens |
| Low | Non-sensitive configuration values | Hostnames, ports, environment names |

## Current Secrets Inventory

| Secret | Service | Classification | Storage Location |
|----------|----------|---------------|------------------|
| JWT Secret Key | auth_service | Critical | Environment Variable |
| PostgreSQL Password | postgres | Critical | Environment Variable |
| Grafana Admin Password | grafana | High | Environment Variable |
| SMTP Password | grafana | High | Environment Variable |

## Secret Ownership

| Secret Type | Owner |
|-------------|--------|
| Authentication Secrets | Identity Platform |
| Database Credentials | Database Services |
| SMTP Credentials | Notification Services |
| Future API Keys | Integrating Service |
| Future Service Tokens | Service Owner |

## Environment Variable Standards

Secrets must:

- Never be hardcoded in source code
- Never be committed to Git
- Never appear in documentation examples
- Be injected through environment variables
- Be stored in .env files during development
- Be migrated to a centralized secrets platform in future phases

## Rotation Strategy

### JWT Signing Keys

Rotation Trigger:

- Suspected compromise
- Scheduled security maintenance
- Key exposure event

### Database Credentials

Rotation Trigger:

- Personnel change
- Credential exposure
- Scheduled maintenance

### SMTP Credentials

Rotation Trigger:

- Provider recommendation
- Credential exposure
- Scheduled maintenance

## Future State

Future phases may implement:

- HashiCorp Vault
- Kubernetes Secrets
- External Secrets Operator
- Cloud Secret Managers

Selection will occur after Kubernetes adoption and production readiness reviews.

## Phase 6.0.0 Initial Secrets Audit

### Password Keyword Scan

Command:

bash
grep -R \
  --exclude-dir=.venv \
  --exclude-dir=__pycache__ \
  "password" services infrastructure docs

  ## Phase 6.0.0 Secrets Audit Results

### Default Secret Scan

Command:

bash
grep -R --exclude-dir=.venv --exclude-dir=__pycache__ "super-secret-dev-key"