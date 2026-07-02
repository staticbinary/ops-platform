# Phase 6.5 CI/CD Pipeline Automation

## Overview

Phase 6.5 introduces the first automated continuous integration workflow for the Ops Platform.

Previous Phase 6 work established local validation, runtime checks, service validation, deployment validation, and automated functional testing. Phase 6.5 begins converting those local engineering controls into automated repository-level checks.

The initial CI implementation is intentionally lightweight and deterministic. It validates repository correctness without requiring running containers, initialized databases, seeded test users, or full platform startup.

## Objectives

The primary objective of Phase 6.5 is to move from manual validation toward automated validation.

Current model:

```text
Engineer Runs Validation
```

Target model:

```text
GitHub Runs Validation
```

This prepares the platform for future pull request gates, release gates, deployment automation, and Kubernetes validation.

## CI Workflow Location

The GitHub Actions workflow is located at:

```text
.github/workflows/ci.yml
```

## Workflow Triggers

The CI workflow runs on:

```text
Pushes to main

Pull requests targeting main
```

## Current Validation Scope

The initial CI pipeline validates:

```text
Repository checkout

Docker Compose configuration

Shell script syntax

Required repository structure
```

## Pipeline Execution Flow

```text
Checkout Repository
        ↓
Validate Docker Compose Configuration
        ↓
Validate Shell Script Syntax
        ↓
Validate Repository Structure
        ↓
Report Pass / Fail Status
```

## Validation Stages

### Repository Checkout

The workflow checks out the repository using GitHub Actions so the pipeline can inspect the current code state.

### Docker Compose Validation

The workflow validates Docker Compose syntax and resolved configuration.

Command:

```bash
docker compose config
```

This confirms that the Compose file can be parsed and rendered successfully.

### Shell Script Syntax Validation

The workflow validates shell script syntax for operational scripts.

Command:

```bash
find scripts -type f -name "*.sh" -exec bash -n {} \;
```

This catches shell syntax errors before scripts are executed manually or used in later automation.

### Repository Structure Validation

The workflow confirms that required top-level directories and files exist.

Current required structure:

```text
docker-compose.yml

services/

scripts/

infrastructure/

docs/
```

## Current CI Workflow

```yaml
name: Ops Platform CI

on:
  push:
    branches:
      - main

  pull_request:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Validate Docker Compose Configuration
        run: |
          docker compose config

      - name: Validate Shell Scripts
        run: |
          find scripts -type f -name "*.sh" -exec bash -n {} \;

      - name: Validate Repository Structure
        run: |
          test -f docker-compose.yml
          test -d services
          test -d scripts
          test -d infrastructure
          test -d docs

      - name: CI Validation Complete
        run: |
          echo "Repository validation successful"
```

## Relationship to Existing Validation Scripts

Phase 6.5 does not replace the existing validation framework.

It complements the existing local validation workflow:

```text
validate-config.sh

validate-runtime.sh

validate-services.sh

validate-platform.sh

pre-deploy-check.sh

post-deploy-check.sh

release-readiness.sh

scripts/tests/test-all.sh
```

Current release validation hierarchy:

```text
Configuration Validation
        ↓
Runtime Validation
        ↓
Service Validation
        ↓
Automated Functional Testing
        ↓
Release Readiness Validation
        ↓
CI Validation Automation
```

## Why the Initial CI Scope Is Limited

The current automated functional tests depend on:

```text
Running containers

Database availability

Configured test accounts

Shared JWT secrets

Operational asset_service and auth_service instances
```

Because of those dependencies, the first CI workflow does not yet start containers or run the full functional test suite.

This avoids introducing unstable CI behavior before the platform has a dedicated CI runtime configuration.

## Future CI Expansion Plan

Recommended CI maturity path:

```text
Stage 1: Static validation

Stage 2: Docker Compose validation

Stage 3: Container startup validation

Stage 4: Health endpoint validation

Stage 5: Automated functional test execution

Stage 6: Release readiness validation

Stage 7: Deployment automation
```

Future workflow additions may include:

```text
docker compose up -d --build

scripts/validate-services.sh

scripts/tests/test-all.sh

scripts/release-readiness.sh

Prometheus rule validation

Grafana dashboard JSON validation

Container image build checks

Security scanning

Kubernetes manifest validation
```

## Operational Procedure

Before committing CI changes locally, validate:

```bash
docker compose config
bash -n scripts/*.sh
bash -n scripts/tests/*.sh
git status
```

After committing and pushing, confirm that GitHub Actions runs automatically.

Expected result:

```text
Ops Platform CI passes successfully
```

## Failure Handling

### Docker Compose Validation Failure

If the Docker Compose validation step fails, inspect:

```text
docker-compose.yml

.env

Referenced bind mounts

Service definitions

Network definitions

Volume definitions
```

Validate locally with:

```bash
docker compose config
```

### Shell Script Validation Failure

If shell syntax validation fails, run:

```bash
find scripts -type f -name "*.sh" -exec bash -n {} \;
```

Then inspect the script reported by the failing command.

Common causes include:

```text
Missing fi

Missing done

Unclosed quote

Invalid conditional syntax

Incorrect function syntax
```

### Repository Structure Validation Failure

If structure validation fails, confirm that required files and directories exist:

```bash
test -f docker-compose.yml
test -d services
test -d scripts
test -d infrastructure
test -d docs
```

## Security Considerations

The CI workflow should not expose secrets.

Do not hard-code credentials directly in workflow files.

Sensitive values should be stored using appropriate secret-management controls before being introduced into CI execution.

Current CI does not require secret access because it performs static repository validation only.

## Phase 6.5 Outcome

Phase 6.5 establishes the Ops Platform's first automated repository validation workflow.

The platform now supports:

```text
Local validation

Runtime validation

Service validation

Deployment validation

Automated functional testing

Initial CI validation
```

This marks the transition from manual engineering checks toward automated CI/CD discipline.
