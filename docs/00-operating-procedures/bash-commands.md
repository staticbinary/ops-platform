Ops Platform Bash Command Reference
Purpose
This document contains commonly used Bash, Docker, Git, PostgreSQL, Prometheus, Grafana, and troubleshooting commands used throughout the Ops Platform project.

Project Navigation
Open Project Directory
cd ~/projects/ops-platform
Show Current Directory
pwd
List Files
ls
List Files with Details
ls -la

Python Virtual Environment
Activate Virtual Environment
source .venv/bin/activate
Deactivate Virtual Environment
deactivate
Install Dependencies
pip install -r requirements.txt
Show Installed Packages
pip list

Docker Commands
Build Containers
docker compose build
Build and Start Stack
docker compose up -d --build
Start Existing Containers
docker compose start
Stop Containers
docker compose stop
Stop and Remove Containers
docker compose down
View Running Containers
docker compose ps
Restart All Services
docker compose restart
Restart Specific Service
docker compose restart asset_service
View Container Logs
docker compose logs asset_service
View Last 50 Log Lines
docker compose logs asset_service --tail=50
Follow Logs Live
docker compose logs -f asset_service
Enter Running Container
docker compose exec asset_service sh

Health Validation
Asset Service Health
curl http://localhost:8001/health
Asset Service Liveness
curl http://localhost:8001/health/live
Asset Service Readiness
curl http://localhost:8001/health/ready
Asset Service Startup
curl http://localhost:8001/health/startup
Auth Service Health
curl http://localhost:8002/health

Metrics Validation
Asset Service Metrics
curl http://localhost:8001/metrics
Auth Service Metrics
curl http://localhost:8002/metrics
Prometheus UI
http://localhost:9090
Grafana UI
http://localhost:3000
cAdvisor UI
http://localhost:8080

PostgreSQL
Open PostgreSQL Shell
docker compose exec postgres psql -U ops
List Databases
\l
Connect to Database
\c ops_platform
List Tables
\dt
Describe Table
\d assets
Exit PostgreSQL
\q

Alembic
Create Migration
alembic revision --autogenerate -m "description"
Apply Migrations
alembic upgrade head
Show Migration History
alembic history
Show Current Revision
alembic current

Git Commands
Check Status
git status
View Branch
git branch
Stage All Changes
git add .
Commit Changes
git commit -m "description"
View Commit History
git log --oneline
Push Changes
git push
Pull Latest Changes
git pull

Troubleshooting
Show Container Resource Usage
docker stats
Inspect Container
docker inspect ops-asset-service
View Docker Networks
docker network ls
View Docker Volumes
docker volume ls
Check Listening Ports
ss -tulpn
Search Logs
docker compose logs asset_service | grep error
Follow Logs and Filter
docker compose logs -f asset_service | grep request_id

Frequently Used Development Workflow
Start Working
cd ~/projects/ops-platform
source .venv/bin/activate
docker compose start
docker compose ps
End Work Session
docker compose stop
deactivate
Full Rebuild
docker compose down
docker compose up -d --build
docker compose ps

Future Additions
As the platform grows, add sections for:
Loki
Tempo
Alertmanager
Keycloak
SSO
CI/CD
Kubernetes
Security Operations
Incident Response Runbooks
Backup and Recovery Procedures