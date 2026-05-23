# Ops Platform — Phase Roadmap

## Project Vision

Build a modular enterprise-style operations platform capable of:

- device inventory management
- telemetry and monitoring
- media hosting/catalog services
- authentication and identity management
- storefront/e-commerce experimentation
- observability and analytics
- AI-assisted operational tooling
- homelab/self-hosted deployment
- real-world infrastructure demonstrations

Long-term deployment goals:
- public domain exposure
- HTTPS/TLS
- authentication-protected services
- T5500 homelab deployment
- production-style operational workflows

---

# Architectural Principles

Core platform goals:

- modular service-oriented architecture
- infrastructure-first development
- operational discipline
- persistent relational data modeling
- centralized ingress management
- environment-driven configuration
- separation of concerns
- controlled complexity growth
- documentation-first operational workflows

---

# Completed Phases

## Phase 1 — Platform Foundation ✔

Objectives:
- establish Linux development environment
- initialize Git repository
- create project structure
- containerize first backend service

Completed:
- Ubuntu WSL2 development environment
- Git initialization/configuration
- VS Code WSL integration
- Docker Compose foundation
- FastAPI asset-service
- initial health endpoints
- container build/runtime validation

Key Concepts Learned:
- WSL/Linux development
- container runtimes
- FastAPI service architecture
- Git workflow basics
- Docker image lifecycle

---

## Phase 1.5 — Operational Foundation ✔

Objectives:
- improve repository hygiene
- establish operational workflows
- centralize runtime configuration
- begin engineering documentation

Completed:
- .env runtime configuration
- compose parameterization
- operational runbooks
- architecture overview documentation
- troubleshooting notes
- Git checkpoint discipline

Key Concepts Learned:
- environment configuration management
- operational workflows
- infrastructure-as-code concepts
- documentation discipline
- rollback/checkpoint strategy

---

## Phase 2 — Stateful Infrastructure ✔

Objectives:
- introduce persistent infrastructure
- establish database connectivity
- implement ORM foundation

Completed:
- PostgreSQL container deployment
- persistent Docker volumes
- SQLAlchemy integration
- DB health validation
- ORM model creation
- automatic schema generation
- assets relational table creation

Key Concepts Learned:
- stateful vs stateless architecture
- persistent storage
- ORM concepts
- relational schema design
- container networking
- database abstraction layers
- direct infrastructure verification

---

# Active Development Phase

# Phase 3.5 — Operational Maturity & Service Decoupling

## Completed

### CRUD API Improvements
- Added `GET /assets/{asset_id}`
- Implemented proper `404` handling
- Rebuilt services successfully
- Validated retrieval of known asset
- Validated expected failure behavior for unknown asset IDs

## In Progress
- PUT endpoint implementation
- DELETE endpoint implementation

## Upcoming
- RBAC foundation
- JWT auth
- Observability stack
- Worker service
- Event bus

# Phase 3.6 — Asset Update Lifecycle

## Completed

### Asset Update Endpoint
- Added `PUT /assets/{asset_id}`
- Added `AssetUpdate` schema model
- Implemented database-backed asset update logic
- Added proper `404` handling for unknown asset updates
- Rebuilt containers successfully after endpoint implementation

### Validation Completed

#### Successful Asset Update
Validated successful update of existing asset:

```bash
curl -X PUT http://localhost:8080/api/assets/assets/1 \
  -H "Content-Type: application/json" \
  -d '{"hostname":"t5500-lab-node","owner":"ops-team","status":"maintenance"}'

  # Phase 3.7 — Asset Deletion Lifecycle

## Completed

### Asset Delete Endpoint
- Added `DELETE /assets/{asset_id}`
- Implemented database-backed asset deletion logic
- Added proper `404` handling for unknown asset deletion
- Rebuilt containers successfully after endpoint implementation

### Validation Completed

#### Successful Asset Delete
Validated successful deletion of existing asset:

```bash
curl -X DELETE http://localhost:8080/api/assets/assets/1

# Phase 3.8 — API Documentation and OpenAPI Hardening

## Completed

### FastAPI Metadata
- Added service title, description, and version metadata
- Confirmed Swagger UI displays service information correctly
- Confirmed OpenAPI schema generation is active

### Reverse Proxy Swagger Support
- Added `root_path="/api/assets"` to FastAPI configuration
- Resolved Swagger/OpenAPI failure behind reverse proxy
- Confirmed `/api/assets/openapi.json` loads successfully
- Confirmed Swagger UI loads at:

```text
http://localhost:8080/api/assets/docs

Swagger Organization
Added route tags for API grouping
Organized endpoints into:
Health
Assets
Root
Schemas
Validation Completed

Confirmed Swagger displays:

GET     /health
GET     /db-health
GET     /assets
POST    /assets
GET     /assets/{asset_id}
PUT     /assets/{asset_id}
DELETE  /assets/{asset_id}
GET     /
Status

Asset Service now has discoverable API documentation through Swagger/OpenAPI.

# Phase 3.9 — Middleware and Request Logging Foundation

## Completed

### Request Logging Middleware
- Added FastAPI HTTP middleware layer
- Implemented request/response lifecycle logging
- Added request interception using:

```python
@app.middleware("http")

Added request logging for:
HTTP method
request URL
response status code
FastAPI Middleware Integration

Updated imports:

from fastapi import Depends, FastAPI, HTTPException, Request

Implemented middleware:

@app.middleware("http")
async def log_requests(request: Request, call_next):

Middleware now logs:

Incoming request: GET http://asset-service:8000/health
Completed response: 200
Validation Completed
Health Endpoint Test
curl http://localhost:8080/api/assets/health

Returned expected response:

{"status":"ok","service":"asset-service"}
Container Log Validation
docker compose logs asset-service

Confirmed:

middleware execution
request interception
response interception
container log visibility
reverse proxy request forwarding
Operational Validation

Confirmed nginx reverse proxy correctly forwards requests internally to:

http://asset-service:8000

within the Docker network.

Status

Asset Service now supports:

full CRUD lifecycle
OpenAPI/Swagger documentation
middleware request logging
operational telemetry visibility
reverse proxy request tracing

# Phase 3.10 — Request IDs and Correlation Logging

## Completed

### Request ID Middleware
- Added UUID-based request IDs to middleware
- Added `X-Request-ID` response header
- Updated logs to include matching request IDs for each request lifecycle
- Confirmed request and response logs share the same correlation ID

### Validation Completed

Tested health endpoint with response headers:

```bash
curl -i http://localhost:8080/api/assets/health

# Phase 4.0 — Authentication Foundation

## In Progress

### JWT Authentication Setup
- Added JWT-related imports
- Added OAuth2 password flow imports
- Added authentication configuration:
  - `SECRET_KEY`
  - `ALGORITHM`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `oauth2_scheme`
- Added JWT helper functions:
  - `create_access_token()`
  - `verify_token()`
- Added authentication endpoints:
  - `POST /auth/login`
  - `GET /auth/me`
- Rebuilt containers successfully after auth foundation updates

## Status
Authentication foundation has been added to `main.py`.

## Next Step
Validate:
- successful login/token generation
- protected route access
- invalid login failure
- missing token failure

---

## Phase 5 — Frontend Platform Interface

Objectives:
- create operational web interface
- expose platform functionality visually

Planned:
- React frontend
- dashboard layout
- asset inventory UI
- service overview panels
- navigation shell
- responsive layouts

Key Concepts:
- frontend/backend separation
- API consumption
- component architecture
- operational dashboard design

---

## Phase 6 — Identity & Access Management

Objectives:
- implement enterprise-style authentication
- centralize identity management

Planned:
- Keycloak integration
- JWT authentication
- RBAC
- protected API routes
- SSO concepts
- user/session management

Key Concepts:
- OAuth2/OpenID Connect
- token-based authentication
- identity separation
- authorization boundaries

---

## Phase 7 — Telemetry & Monitoring Platform

Objectives:
- collect operational telemetry
- visualize infrastructure health

Planned:
- Prometheus
- Grafana
- telemetry ingestion APIs
- hardware/system metrics
- alerting concepts
- monitoring dashboards

Potential Data:
- CPU usage
- memory usage
- temperatures
- service status
- disk health
- uptime

Key Concepts:
- observability
- telemetry pipelines
- metrics collection
- monitoring architecture

---

## Phase 8 — Homelab Deployment (T5500)

Objectives:
- deploy platform onto dedicated hardware
- separate dev vs server environments

Planned:
- Ubuntu Server deployment
- Docker host configuration
- SSH administration
- remote management
- persistent storage setup
- backup strategy

Key Concepts:
- infrastructure deployment
- server administration
- remote operations
- persistent infrastructure hosting

---

## Phase 9 — Public Exposure & Domain Integration

Objectives:
- expose platform publicly and securely
- implement internet-facing ingress

Planned:
- domain registration
- Cloudflare integration
- HTTPS/TLS
- reverse proxy hardening
- DNS management
- secure public ingress

Key Concepts:
- DNS
- TLS certificates
- internet ingress
- edge security
- reverse proxy hardening

---

## Phase 10 — Media Platform Services

Objectives:
- support media hosting/catalog functionality
- integrate persistent media metadata

Planned:
- media metadata database
- catalog APIs
- storage indexing
- streaming architecture concepts
- media dashboard

Key Concepts:
- metadata systems
- storage abstraction
- media indexing
- content organization

---

## Phase 11 — Storefront/E-Commerce Service

Objectives:
- build isolated commerce-oriented service

Planned:
- product catalog
- order schemas
- cart workflows
- payment flow simulation
- service isolation

Key Concepts:
- transactional systems
- service decomposition
- relational commerce modeling

---

## Phase 12 — AI & Operational Intelligence Layer

Objectives:
- integrate AI-assisted operational tooling

Planned:
- local LLM experimentation
- RAG architecture
- operational assistant
- telemetry summarization
- documentation retrieval
- infrastructure reasoning

Key Concepts:
- AI service integration
- vector databases
- retrieval systems
- operational automation

---

# Long-Term Platform Vision

Final architecture direction:

Internet
    ↓
Cloudflare
    ↓
NGINX ingress
    ↓
Keycloak identity layer
    ↓
platform services
    ├── asset-service
    ├── telemetry-service
    ├── media-service
    ├── storefront-service
    ├── AI-service
    └── monitoring stack

Shared infrastructure:
- PostgreSQL
- Docker networking
- persistent storage
- observability stack
- centralized auth
- operational dashboards

---

# End Goal

Create a fully self-hosted modular operations platform demonstrating:

- infrastructure engineering
- backend architecture
- operational workflows
- service-oriented architecture
- observability
- identity management
- persistence modeling
- container orchestration
- real-world deployment strategy

Primary professional objective:
- demonstrate practical platform engineering capability
- expand beyond escalation/support specialization
- create portfolio-grade operational infrastructure experience

