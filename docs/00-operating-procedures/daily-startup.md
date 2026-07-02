# Ops Platform Daily Startup

## Purpose

Standardized daily startup procedure for the Ops Platform development environment.

Complete the following validation steps before beginning development to ensure the platform is healthy and operating correctly.

---

# Step 1 - Open Development Environment

Navigate to the project directory and activate the Python virtual environment.

**Run**

    cd ~/projects/ops-platform

    source .venv/bin/activate

**Expected Result**

- Working directory is the project root.
- Python virtual environment is active.
- Shell prompt displays `(.venv)`.

---

# Step 2 - Start Platform

Start all platform services.

**Normal Startup**

    docker compose up -d

**Rebuild Images (Only When Required)**

    docker compose up -d --build

**Use --build When**

- Dockerfile changes.
- Python dependency changes.
- Application source changes copied into container images.
- Base images have changed.

**Expected Result**

- All containers start successfully.
- No restart loops occur.
- Health checks begin passing within approximately one minute.

---

# Step 3 - Verify Container Health

Confirm every service is running.

**Run**

    docker compose ps

**Expected Result**

All services report:

- Up
- Healthy (where applicable)

Expected services:

- reverse-proxy
- asset-service
- auth-service
- postgres
- postgres-exporter
- node-exporter
- blackbox-exporter
- prometheus
- grafana
- loki
- promtail
- tempo
- cadvisor

---

# Step 4 - Verify Prometheus Targets

Open Prometheus.

    http://localhost:9090/targets

**Expected Result**

Every scrape target reports:

- UP

Verify at minimum:

- asset-service
- auth-service
- postgres-exporter
- node-exporter
- blackbox-http
- cadvisor
- prometheus

---

# Step 5 - Verify Grafana

Open Grafana.

    http://localhost:3000

Confirm dashboards load successfully.

Primary dashboards:

- Platform Overview
- Infrastructure Overview
- Service Reliability
- Security Operations
- Security Detection
- Security Investigation
- Security Response
- System Metrics

---

# Step 6 - Verify Exporters

Check exporter availability.

**Run**

    curl -s "http://localhost:9090/api/v1/query?query=up"

**Expected Result**

All exporters return:

- value = 1

Verify:

- node-exporter
- postgres-exporter
- blackbox-http
- cadvisor
- prometheus

---

# Step 7 - Verify Synthetic Monitoring

Confirm endpoint probes are functioning.

**Run**

    curl -s "http://localhost:9090/api/v1/query?query=probe_success"

**Expected Result**

Critical endpoints return:

- value = 1

Verify:

- Grafana
- Prometheus
- Asset Health
- Asset Ready
- Authentication Health

---

# Step 8 - Quick Log Validation

Review startup logs for obvious issues.

**Grafana**

    docker compose logs grafana --tail=20

**Prometheus**

    docker compose logs prometheus --tail=20

**Expected Result**

- No provisioning failures.
- No configuration errors.
- No scrape failures.
- No startup failures.

**Known Benign Warning**

The following Grafana plugin message is expected and can be ignored:

- Elasticsearch bundled plugin permission warning.

---

# Step 9 - Verify Repository Status

Check the current Git working tree.

**Run**

    git status

**Expected Result**

Know whether the repository is:

- Clean
- Modified
- Contains untracked files

---

# Step 10 - Begin Development

Once all health checks pass, begin development.

Recommended workflow:

- Update code.
- Restart affected services if necessary.
- Validate Prometheus metrics.
- Review Grafana dashboards.
- Inspect Loki logs.
- Verify Tempo traces.
- Execute Postman collections.
- Commit validated changes.

---

# End of Day Shutdown

When development is complete:

**Run**

    docker compose down

**Expected Result**

- Containers stop cleanly.
- Persistent volumes remain intact.
- Database and Grafana data are preserved.

---

# Quick Troubleshooting

## Prometheus not updating

    docker compose restart prometheus

---

## Grafana dashboards not refreshing

    docker compose restart grafana

---

## Application code changes not reflected

    docker compose up -d --build

---

## Service startup problems

View logs for all services:

    docker compose logs

View logs for a specific service:

    docker compose logs <service>

---

# Development Philosophy

Always begin development from a known healthy platform.

Before writing or debugging application code, verify:

- All containers are healthy.
- Prometheus targets are UP.
- Grafana dashboards load correctly.
- Exporters are reporting metrics.
- Synthetic monitoring succeeds.
- Repository status is understood.

Starting from a validated environment significantly reduces troubleshooting time and helps isolate application issues from infrastructure problems.