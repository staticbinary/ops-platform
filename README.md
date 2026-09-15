# Ops Platform

Ops Platform is a Kubernetes-based operations platform built to explore production-style backend infrastructure, identity, observability, CI/CD, reliability, and infrastructure automation.

The project began as a Docker Compose environment and has progressively moved toward Kubernetes-based deployment and infrastructure management.

## Architecture

The platform currently includes:

- Python / FastAPI backend services
- PostgreSQL persistent storage
- Kubernetes Deployments, StatefulSets, Services, PVCs, Jobs, and HPA
- Traefik ingress and routing
- Keycloak identity integration
- Prometheus metrics and alerting
- Grafana dashboards
- Loki log aggregation
- Tempo distributed tracing
- OpenTelemetry instrumentation
- GitHub Actions CI/CD
- Terraform Kubernetes provider configuration

## Services

### Asset Service

FastAPI service providing asset management functionality backed by PostgreSQL.

Includes:

- REST API endpoints
- Database migrations with Alembic
- Health and readiness checks
- Authentication and authorization integration
- Kubernetes deployment and autoscaling

### Auth Service

FastAPI authentication service used for platform authentication and authorization workflows.

Includes:

- JWT authentication
- Role-based access control
- Persistent application data
- Kubernetes deployment and health validation

## Kubernetes

Kubernetes manifests are maintained under 'kubernetes/base/' and include:

- Application Deployments and Services
- PostgreSQL StatefulSet and persistent storage
- Database migration Jobs
- ConfigMaps and local Secret templates
- Horizontal Pod Autoscaling
- Traefik Ingress resources
- Keycloak identity services
- Grafana and observability integrations

The platform has been tested for workload scaling, persistent storage behavior, service discovery, ingress routing, and application readiness.

## Observability

The observability stack includes:

- Prometheus
- Grafana
- Loki
- Tempo
- OpenTelemetry
- Alertmanager
- Grafana Alloy

Operational documentation includes alert investigation procedures, security telemetry testing, dashboard standards, and incident runbooks.

## Infrastructure as Code

Terraform configuration under 'terraform/kubernetes/' is being developed to manage Kubernetes platform resources declaratively.

Terraform state and local working directories are intentionally excluded from source control.

## Operations and Documentation

The 'docs/' directory contains the operational material developed alongside the platform, including:

- Architecture documentation
- Architecture Decision Records
- CI/CD documentation
- Security investigations
- Authentication and secrets-management documentation
- Observability investigations
- Incident response runbooks
- Troubleshooting notes
- Post-incident and investigation templates

The goal is to treat documentation, validation, troubleshooting, and recovery as part of the platform rather than as separate afterthoughts.

## Repository Structure

services/          FastAPI application services
kubernetes/        Kubernetes platform definitions
terraform/         Infrastructure-as-Code configuration
infrastructure/    Monitoring and reverse-proxy configuration
scripts/           Validation, testing, and operational tooling
docs/              Architecture, ADRs, runbooks, and operations documentation

## Engineering Focus

This project is intentionally built around operational concerns beyond simply deploying an application:

- Repeatable deployments
- Health and readiness validation
- Persistent data management
- Authentication and authorization
- Observability and incident investigation
- Failure and recovery testing
- CI/CD automation
- Infrastructure automation
- Operational documentation
