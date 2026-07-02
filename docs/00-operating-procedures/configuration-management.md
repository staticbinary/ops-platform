# Configuration Management

## Purpose

This document defines configuration management standards for Ops Platform.

Objectives:

- Inventory platform configuration
- Standardize configuration management
- Separate configuration from code
- Define ownership and change control
- Prevent configuration drift
- Improve deployment consistency

## Configuration Inventory

| Component | Configuration Source | Criticality |
|------------|------------|------------|
| Asset Service | Environment Variables | Critical |
| Auth Service | Environment Variables | Critical |
| PostgreSQL | Environment Variables | Critical |
| NGINX | nginx.conf | High |
| Prometheus | prometheus.yml | High |
| Alert Rules | prometheus-alerts.yml | High |
| Grafana | dashboard JSON files | Medium |
| Loki | loki-config.yml | Medium |
| Promtail | promtail-config.yml | Medium |
| Tempo | tempo.yml | Medium |
| Docker Compose | docker-compose.yml | Critical |

## Configuration Classification

### Secrets

Examples:

- JWT signing keys
- Database passwords
- SMTP credentials
- Future API keys

Storage:

- Environment variables

### Service Configuration

Examples:

- Ports
- Service names
- Runtime settings
- Feature toggles

Storage:

- Environment variables
- Service configuration files

### Infrastructure Configuration

Examples:

- Docker Compose
- NGINX
- Prometheus
- Grafana

Storage:

- Version controlled files

## Environment Variable Standards

Rules:

- Secrets must never be hardcoded.
- Secrets must be supplied through environment variables.
- Configuration should be externalized from application code.
- Required configuration must fail startup when missing.
- Environment variables should use descriptive names.

## Configuration Drift Prevention

Configuration drift occurs when deployed configuration differs from documented configuration.

Mitigation:

- Version control all configuration files.
- Review configuration changes through Git.
- Validate changes before deployment.
- Maintain configuration documentation.
- Regularly compare deployed and repository configurations.

## Configuration Validation

Validate Repository State:

```bash
git status

docker compose config

docker compose ps

docker compose exec asset_service env

docker compose exec auth_service env

## Configuration Audit Results

### Docker Compose Rendered Configuration

Command:

```bash
docker compose config


## Also add this to the Runtime Inventory

```markdown
## Runtime Configuration Inventory

### Asset Service

Configuration observed through Docker Compose rendering:

- `DATABASE_URL`
- `ENVIRONMENT`
- `JWT_ALGORITHM`
- `SECRET_KEY`
- `SERVICE_NAME`

### Auth Service

Configuration observed through Docker Compose rendering:

- `AUTH_SERVICE_SECRET_KEY`

### PostgreSQL

Configuration observed through Docker Compose rendering:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

### Grafana

Configuration observed through Docker Compose rendering:

- `GF_SMTP_ENABLED`
- `GF_SMTP_FROM_ADDRESS`
- `GF_SMTP_FROM_NAME`
- `GF_SMTP_HOST`
- `GF_SMTP_PASSWORD`
- `GF_SMTP_SKIP_VERIFY`
- `GF_SMTP_STARTTLS_POLICY`
- `GF_SMTP_USER`

## Configuration Drift Finding

### Finding

`asset_service` runtime configuration initially retained an old JWT secret value even though `.env` had been updated.

### Root Cause

The `.env` file had been updated, but the running container had not yet been recreated with the updated environment value.

### Resolution

Recreated the asset service container:

```bash
docker compose up -d --force-recreate asset_service

## Configuration Ownership Matrix

| Configuration Area | Owner | Criticality |
|--------------------|---------|------------|
| .env | Platform Operations | Critical |
| docker-compose.yml | Platform Operations | Critical |
| nginx.conf | Platform Operations | High |
| prometheus.yml | Platform Operations | High |
| prometheus-alerts.yml | Platform Operations | High |
| Grafana Dashboards | Platform Operations | Medium |
| Loki Configuration | Platform Operations | Medium |
| Promtail Configuration | Platform Operations | Medium |
| Tempo Configuration | Platform Operations | Medium |
| Asset Service Runtime Configuration | Platform Operations | Critical |
| Auth Service Runtime Configuration | Platform Operations | Critical |

## Configuration Change Control

Configuration changes should follow the following workflow:

1. Update source-controlled configuration.
2. Validate configuration syntax.
3. Review changes.
4. Commit changes to Git.
5. Deploy changes.
6. Validate runtime configuration.
7. Verify service health.

Examples:

- docker-compose.yml
- nginx.conf
- prometheus.yml
- alert rules
- environment variables

### Configuration Consistency Validation

Render Docker Compose Configuration:

```bash
docker compose config

docker compose exec asset_service env | sort

docker compose exec auth_service env | sort

docker compose ps

git status

## Configuration Drift Case Study

### Scenario

Environment configuration was updated with a new PostgreSQL password.

### Outcome

The PostgreSQL container continued using the password established when the database volume was originally initialized.

Asset service adopted the new password from environment configuration and could no longer authenticate.

### Symptoms

- Asset service unhealthy
- `/health/ready` returned 503
- Database unavailable status
- PostgreSQL authentication failures

### Root Cause

Database credentials stored within the initialized PostgreSQL instance did not match updated environment configuration.

### Resolution

Restored the original database password value and recreated affected services.

### Lesson Learned

Changing environment configuration does not automatically modify credentials stored within persistent database volumes.

Credential rotation procedures must include database-side credential updates.