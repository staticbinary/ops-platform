# Database Administration Guide

## Purpose

This document defines the standard operational procedures for administering the Ops Platform PostgreSQL database.

The goals of this guide are to:

- Verify PostgreSQL availability
- Validate database schema integrity
- Manage Alembic migrations
- Connect using DBeaver
- Inspect the live database
- Perform common administrative tasks
- Troubleshoot database issues

---

# Platform Database Architecture

Application
      │
      ▼
SQLAlchemy Models
      │
      ▼
Alembic Migrations
      │
      ▼
PostgreSQL
      │
      ▼
DBeaver

The SQLAlchemy models define the intended database structure.

Alembic generates version-controlled database migrations from those models.

PostgreSQL stores the live database.

DBeaver provides a graphical interface for inspecting and managing the live database.

---

# Standard Startup Workflow

## Step 1 - Start the Platform

Run the automated startup workflow.

bash
./scripts/daily-startup.sh

The startup workflow automatically:

- Starts all platform containers
- Verifies container status
- Executes the database health check
- Executes the service health check
- Executes the observability health check
- Displays platform access URLs

---

## Step 2 - Verify Database Health

The startup workflow automatically executes:

bash
./scripts/database-health-check.sh

The database health check validates:

- PostgreSQL container health
- Database connectivity
- Required database tables
- Current Alembic migration revision

---

## Step 3 - Connect Using DBeaver

### Connection Settings

| Setting | Value |
|----------|-------|
| Host | localhost |
| Port | 5432 |
| Database | ops_platform |
| Username | ops_user |
| Password | ops_password |

After connecting, expand:

Schemas
└── public
    └── Tables

Verify the following tables exist:

- alembic_version
- assets
- audit_logs

---

## Step 4 - Inspect Database Objects

For each table, inspect:

- Columns
- Constraints
- Indexes
- Foreign Keys
- Dependencies
- References

Right-click the table and select:

- Generate SQL

or

- DDL

Compare the generated SQL against:

1. SQLAlchemy models
2. Alembic migration
3. Live PostgreSQL schema

All three should match.

---

## Step 5 - View Table Data

Right-click the desired table.

Select:

View Data
└── All Rows

Use DBeaver primarily as an inspection and administration tool.

Avoid modifying production data directly.

---

# Database Change Workflow

Every schema modification should follow this workflow.

Modify SQLAlchemy Model
        │
        ▼
Generate Alembic Migration
        │
        ▼
Review Migration
        │
        ▼
Apply Migration
        │
        ▼
Verify Schema in DBeaver
        │
        ▼
Run Database Health Check
        │
        ▼
Test API
        │
        ▼
Verify Metrics
        │
        ▼
Commit Changes

---

# Common SQL Commands

## List Tables

sql
\dt

## List Schemas

sql
\dn

## View Current Alembic Revision

sql
SELECT version_num
FROM alembic_version;

## Count Assets

sql
SELECT COUNT(*)
FROM assets;

## View Assets

sql
SELECT *
FROM assets;

## View Audit Logs

sql
SELECT *
FROM audit_logs;

---

# Readiness Validation

The Asset Service readiness endpoint validates that the application is operational before reporting itself as ready.

Endpoint:

GET /api/assets/health/ready

Validation includes:

- Database connectivity
- Database schema availability
- Required application tables

Expected response:

json
{
  "status": "ready",
  "service": "asset-service",
  "checks": {
    "database": "ok",
    "schema": "ok",
    "required_tables": "ok"
  }
}

This provides stronger operational validation than simply verifying a database connection.

---

# Troubleshooting

## No Tables Visible

Possible causes:

- Connected to the wrong database
- Alembic migrations have not been applied
- Database volume recreated
- Wrong schema selected

Verify:

bash
docker compose exec postgres psql -U ops_user -d ops_platform -c "\dt"

---

## PostgreSQL Reachable but No Tables Exist

Symptoms:

- `pg_isready` succeeds
- Database connection succeeds
- DBeaver displays an empty schema

Resolution:

- Verify Alembic migration files exist.
- Apply migrations.
- Refresh the DBeaver connection.

---

## Connection Failures

Verify PostgreSQL is running.

bash
docker compose ps

Then verify connectivity.

bash
docker compose exec postgres pg_isready -U ops_user -d ops_platform

---

# Operational Automation

The standard operational workflow consists of the following scripts.

## daily-startup.sh

Responsibilities:

- Start all platform containers
- Verify container status
- Execute database health validation
- Execute service health validation
- Execute observability health validation
- Display platform access URLs

## database-health-check.sh

Validates:

- PostgreSQL container health
- Database connectivity
- Required database tables
- Current Alembic migration revision

## service-health-check.sh

Validates:

- Required platform services
- Docker container health
- Platform service availability

## observability-health-check.sh

Validates:

- Prometheus
- Grafana
- Loki
- Tempo
- cAdvisor
- Node Exporter
- PostgreSQL Exporter
- Blackbox Exporter

Together these scripts provide the standard operational validation workflow for the Ops Platform.

---

# Future Topics

This guide will continue to expand as the platform matures.

Planned additions:

- Database backups
- Restore procedures
- EXPLAIN ANALYZE
- Query optimization
- Index tuning
- Roles and permissions
- Connection monitoring
- Performance analysis
- Replication
- Partitioning
