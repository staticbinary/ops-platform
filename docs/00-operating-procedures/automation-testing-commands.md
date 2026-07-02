# Automation Testing Commands

## Overview

This document provides a centralized reference for all validation, testing, deployment validation, release readiness, and CI/CD automation commands used throughout the Ops Platform.

The goal is to provide a single operational reference for engineers performing platform validation, troubleshooting, deployment verification, and automation testing activities.

---

## Configuration Validation

### Validate Environment Configuration

bash
./scripts/validate-config.sh

Purpose:

Validate environment configuration

Verify required variables

Detect configuration drift

Confirm deployment prerequisites

---

## Runtime Validation

### Validate Runtime Configuration

bash
./scripts/validate-runtime.sh

Purpose:

Validate runtime service configuration

Verify application startup requirements

Confirm environment consistency

---

## Service Validation

### Validate Service Health

bash
./scripts/validate-services.sh

Purpose:

Validate service availability

Verify health endpoints

Confirm operational services

---

## Platform Validation

### Validate Platform Status

bash
./scripts/validate-platform.sh

Purpose:

Validate overall platform readiness

Confirm infrastructure availability

Verify service integration status

---

## Deployment Validation

### Pre-Deployment Validation

bash
./scripts/pre-deploy-check.sh

Purpose:

Validate platform before deployment

Verify deployment prerequisites

Detect deployment blockers

### Post-Deployment Validation

bash
./scripts/post-deploy-check.sh

Purpose:

Validate deployment success

Verify service startup

Confirm operational readiness

---

## Release Readiness Validation

### Execute Release Readiness Validation

bash
./scripts/release-readiness.sh

Purpose:

Validate release readiness

Execute validation workflow

Confirm deployment confidence

Current validation chain:

Configuration Validation
        ↓
Runtime Validation
        ↓
Service Validation
        ↓
Platform Validation
        ↓
Release Readiness Validation

---

## Automated Testing Framework

### Execute Complete Test Suite

bash
./scripts/tests/test-all.sh

Purpose:

Execute all automated tests

Validate platform functionality

Confirm operational behavior

---

## Platform Smoke Testing

### Execute Platform Validation Tests

bash
./scripts/tests/test-platform.sh

Coverage:

Asset Service Health

Asset Service Readiness

Auth Service Health

Prometheus Health

Grafana Health

Loki Readiness

Tempo Readiness

---

## Authentication Testing

### Execute Authentication Tests

bash
./scripts/tests/test-auth.sh

Coverage:

Valid Login

JWT Issuance

JWT Validation

Invalid Password Rejection

Invalid User Rejection

---

## RBAC Testing

### Execute RBAC Tests

bash
./scripts/tests/test-rbac.sh

Coverage:

Viewer Read Access

Viewer Create Denial

Admin Read Access

Admin Create Access

---

## Asset CRUD Testing

### Execute Asset Service Tests

bash
./scripts/tests/test-assets.sh

Coverage:

Asset Create

Asset Read

Asset Update

Asset Delete

Deletion Verification

---

## Docker Validation

### Validate Docker Compose Configuration

bash
docker compose config

Purpose:

Validate Docker Compose syntax

Resolve environment variables

Validate service definitions

Validate network definitions

Validate volume definitions

---

## Shell Script Validation

### Validate Operational Scripts

bash
find scripts -type f -name "*.sh" -exec bash -n {} \;

Purpose:

Validate shell syntax

Detect script parsing failures

Identify automation defects

---

## GitHub Actions Validation

### CI Workflow Validation

Workflow:

.github/workflows/ci.yml

Execution Trigger:

Push to main

Pull Request to main

Validation Coverage:

Repository Checkout

Docker Compose Validation

Shell Script Validation

Repository Structure Validation

---

## Health Endpoint Validation

### Asset Service Health

bash
curl <http://localhost:8001/health>

### Asset Service Liveness

bash
curl <http://localhost:8001/health/live>

### Asset Service Readiness

bash
curl <http://localhost:8001/health/ready>

### Auth Service Health

bash
curl <http://localhost:8002/health>

---

## Metrics Validation

### Asset Service Metrics

bash
curl <http://localhost:8001/metrics>

### Auth Service Metrics

bash
curl <http://localhost:8002/metrics>

### Prometheus Targets

bash
<http://localhost:9090/targets>

---

## Container Validation

### View Container Status

bash
docker compose ps

### View Running Containers

bash
docker ps

### View Container Logs

bash
docker compose logs

### View Service Logs

bash
docker compose logs asset_service

docker compose logs auth_service

docker compose logs prometheus

docker compose logs grafana

---

## Local Development Validation Workflow

### Standard Engineering Workflow

1. Validate Configuration

2. Validate Runtime

3. Validate Services

4. Validate Platform

5. Execute Automated Tests

6. Execute Release Readiness Validation

7. Commit Changes

8. Push Changes

9. Verify GitHub Actions Execution

---

## CI/CD Validation Workflow

### Automated Workflow

Developer Pushes Code
        ↓
GitHub Actions Executes
        ↓
Docker Compose Validation
        ↓
Shell Script Validation
        ↓
Repository Structure Validation
        ↓
Pass / Fail Status Returned

---

## Future Automation Expansion

Planned automation additions:

Container Startup Automation

Health Validation Automation

Service Validation Automation

Automated Functional Test Execution

Release Validation Automation

Container Image Validation

Security Scanning

Kubernetes Manifest Validation

Deployment Automation

---

## Operational Goal

The Ops Platform validation framework is designed to evolve from:

Engineer Verifies Platform

to:

Platform Verifies Platform

through progressive automation, validation, testing, and continuous integration capabilities.

## CI Runtime Validation Commands

### Start Platform

Build the latest images and start the complete platform:

bash
docker compose up -d --build

---

### Verify Running Containers

Display the status of all platform containers:

bash
docker compose ps

Expected result:

* All required services are running.
* No containers have exited unexpectedly.

---

### Validate Asset Service Health

Verify the Asset Service health endpoint:

bash
curl --fail <http://localhost:8001/health>

Expected result:

* HTTP 200 response
* Health status returned successfully

---

### Validate Auth Service Health

Verify the Auth Service health endpoint:

bash
curl --fail <http://localhost:8002/health>

Expected result:

* HTTP 200 response
* Health status returned successfully

---

### View Container Logs

Inspect recent container logs when runtime validation fails:

bash
docker compose logs --tail=100

---

### Stop Platform (Preserve Data)

Stop and remove containers while preserving persistent volumes:

bash
docker compose down

Use during normal development to retain databases and other persistent data.

---

### Clean Runtime Environment

Stop the platform and remove containers, networks, and named volumes:

bash
docker compose down -v

Use for CI/CD validation or when a completely clean environment is required.

---

## Recommended Local Runtime Validation Workflow

bash
docker compose up -d --build
docker compose ps
curl --fail <http://localhost:8001/health>
curl --fail <http://localhost:8002/health>
docker compose down -v

This workflow mirrors the runtime validation performed by the GitHub Actions CI pipeline.