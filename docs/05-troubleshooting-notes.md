# Operations Platform — Troubleshooting & Implementation Notes

---

## Module Import Troubleshooting

### Symptoms

Asset service failed during startup with:

ModuleNotFoundError: No module named 'app.database'

### Root Cause

`database.py` was accidentally created inside:

services/asset_service/services/asset_service/app/

instead of:

services/asset_service/app/

### Resolution

Moved `database.py` into the correct application package:

services/asset_service/app/

Removed the accidental nested `services` directory and rebuilt containers:

bash
docker compose up -d --build

### Validation

Confirmed:

- asset-service container started successfully
- imports resolved correctly
- FastAPI initialized normally

### Lessons Learned

Python module imports inside containers are highly dependent on correct package structure and runtime path alignment.

---

## PostgreSQL Table Verification

### Objective

Validate ORM-generated PostgreSQL table creation.

### Validation Steps

Entered the PostgreSQL container:

bash
docker exec -it ops-postgres sh

Connected using:

bash
psql -U postgres

Verified generated tables:

sql
\dt

### Result

Confirmed SQLAlchemy successfully generated the `assets` table using:

python
Base.metadata.create_all(bind=engine)

### Lessons Learned

Direct infrastructure validation is important during backend development to verify ORM behavior and persistence.

---

## CRUD Endpoint Startup Failure

### Symptoms

CRUD implementation caused:

502 Bad Gateway

through nginx.

### Root Cause

Malformed indentation inside the `get_db()` dependency function prevented FastAPI from starting.

### Resolution

Reviewed logs:

bash
docker compose logs asset-service

Corrected dependency indentation and rebuilt containers:

bash
docker compose up -d --build

### Validation

Confirmed:

- FastAPI started successfully
- CRUD endpoints became reachable
- PostgreSQL persistence functioned correctly

### Lessons Learned

Container log inspection is critical for diagnosing backend runtime failures.

---

## PUT Endpoint Returned 405 Method Not Allowed

### Symptoms

Updating assets returned:

405 Method Not Allowed

### Root Cause

`PUT /assets/{asset_id}` had not actually been implemented in `main.py`.

Missing components included:

- `AssetUpdate` schema import
- update route registration
- SQLAlchemy update logic

### Resolution

Added:

python
@app.put("/assets/{asset_id}", response_model=AssetResponse)

Implemented:

- database lookup logic
- SQLAlchemy update handling
- commit/refresh logic
- 404 handling

Rebuilt containers:

bash
docker compose up -d --build

### Validation

Confirmed:

- successful asset updates
- request parsing
- database persistence
- API response serialization

### Lessons Learned

A 405 response commonly indicates:

- route path exists
- HTTP method is not registered

---

## DELETE Endpoint Returned 405 Method Not Allowed

### Symptoms

Deleting assets returned:

405 Method Not Allowed

### Root Cause

The DELETE route was not properly registered in the running FastAPI application.

### Resolution

Replaced the full `main.py` file with a verified application version containing:

- GET routes
- POST route
- PUT route
- DELETE route

Implemented:

python
@app.delete("/assets/{asset_id}")

Added:

- database lookup logic
- delete handling
- commit operations
- proper 404 responses

Performed a full rebuild:

bash
docker compose down
docker compose up -d --build

### Validation

Confirmed:

- asset deletion succeeded
- deleted assets returned 404 on retrieval
- nonexistent assets returned proper 404 responses

### Lessons Learned

Full-file replacement can eliminate hidden decorator or indentation issues during early FastAPI development.

---

## Swagger/OpenAPI Failed Behind Reverse Proxy

### Symptoms

Swagger UI loaded partially through nginx but failed with:

Failed to load API definition
/openapi.json not found

### Root Cause

FastAPI generated OpenAPI paths relative to `/` while the service operated behind:

/api/assets

through the reverse proxy.

### Resolution

Updated FastAPI initialization:

python
app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets"
)

Also organized Swagger sections using route tags.

### Validation

Confirmed Swagger loads correctly at:

<http://localhost:8080/api/assets/docs>

### Lessons Learned

When running FastAPI behind a reverse proxy path prefix, `root_path` must be configured correctly for Swagger/OpenAPI generation.

---

## Request Logging Middleware

### Objective

Add operational visibility for incoming requests and responses.

### Implementation

Added FastAPI middleware:

python
@app.middleware("http")
async def log_requests(request: Request, call_next):

Middleware logs:

- incoming requests
- completed responses
- HTTP status codes

### Issue Encountered

`Base.metadata.create_all(bind=engine)` was temporarily pasted before imports were initialized.

### Resolution

Removed the misplaced line and kept the proper initialization after app creation.

### Validation

Confirmed:

- middleware registration
- request interception
- response interception
- reverse proxy forwarding
- container log visibility

### Lessons Learned

Middleware provides the foundation for:

- operational telemetry
- structured logging
- observability pipelines

---

## Request Correlation IDs

### Objective

Improve operational tracing using unique request identifiers.

### Implementation

Added:

python
import uuid

Middleware now:

- generates unique request IDs
- logs request IDs
- adds `X-Request-ID` response headers

### Issue Encountered

Initial requests returned:

500 Internal Server Error

### Root Cause

Container rebuild had not yet included:

python
import uuid

### Resolution

Confirmed imports and rebuilt containers:

bash
docker compose up -d --build

### Validation

Confirmed:

- request IDs appear in logs
- request IDs appear in HTTP headers
- request correlation functions correctly

### Lessons Learned

Correlation IDs significantly improve debugging across:

- logs
- reverse proxies
- future multi-service communication

---

## OAuth2 Login Returned 502 Bad Gateway

### Symptoms

Submitting login requests through Swagger returned:

502 Bad Gateway

### Root Cause

`OAuth2PasswordRequestForm` requires:

python-multipart

which was missing from `requirements.txt`.

### Resolution

Updated dependencies:

python-jose[cryptography]
python-multipart

Rebuilt containers:

bash
docker compose up -d --build

### Validation

Confirmed:

- JWT token issuance
- bearer token responses
- protected route authentication
- unauthorized request rejection

### Lessons Learned

Dependency failures inside FastAPI containers frequently surface as reverse proxy errors.

---

## requirements.txt Permission Denied

### Symptoms

Attempting to run:

bash
services/asset_service/requirements.txt

returned:

Permission denied

### Root Cause

`requirements.txt` is a dependency definition file, not an executable script.

### Resolution

Edited dependencies directly inside the file and rebuilt containers.

### Lessons Learned

Python dependencies are installed during Docker image build execution, not by directly running `requirements.txt`.

---

## Auth Service Failed After OAuth2 Integration

### Symptoms

localhost:8001/docs

refused connections after rebuild.

### Root Cause

`python-multipart` was also missing from the auth-service dependency list.

### Resolution

Added:

python-multipart

to:

services/auth_service/requirements.txt

Rebuilt services successfully.

---

## Audit Endpoint Returned 401 Not Authenticated

### Symptoms

Authenticated users received:

json
{
  "detail": "Not authenticated"
}

### Root Cause

Swagger authorization state expired after rebuilds or restart cycles.

### Resolution

Re-authorized using Swagger OAuth2 flow and retried requests.

### Lessons Learned

Swagger authorization state does not persist reliably across rebuilds and service restarts.

---

## Audit Endpoint Returned 403 Insufficient Permissions

### Symptoms

Viewer users attempting to access admin endpoints received:

json
{
  "detail": "Insufficient permissions"
}

### Root Cause

JWT tokens contained:

json
{
  "role": "viewer"
}

while endpoints required:

python
auth.require_role("admin")

### Resolution

Added temporary admin promotion endpoint:

POST /dev/promote-admin/{email}

Re-authenticated after promotion to generate a new JWT containing updated role claims.

### Lessons Learned

JWT role claims reflect role state at token issuance time.

---

## Auth Users Disappeared After Rebuilds

### Symptoms

Users and roles reset after rebuilding containers.

### Root Cause

Auth service initially stored SQLite data inside the container filesystem without persistent volumes.

### Resolution

Added persistent Docker volume:

yaml
auth-service:
  volumes:
    - auth-data:/app/data

Updated SQLite path:

python
DATABASE_URL = "sqlite:///./data/auth.db"

### Validation

Confirmed:

- users persist across rebuilds
- roles persist across rebuilds
- audit logs persist across rebuilds

---

## Docker Not Found Inside WSL

### Symptoms

Running Docker commands inside WSL returned:

docker: command not found

### Root Cause

Docker Desktop engine was not running.

### Resolution

Restarted Docker Desktop and confirmed WSL integration resumed normally.

---

## Docker Compose Volume Validation Failed

### Symptoms

Docker Compose returned:

Additional property auth-data is not allowed

### Root Cause

`auth-data` volume was incorrectly nested under `postgres-data`.

### Resolution

Corrected top-level volume alignment:

yaml
volumes:
  postgres-data:
  auth-data:

---

## Audit Timestamp Migration Failure

### Symptoms

Adding `created_at` to the audit model caused login requests to return:

500 Internal Server Error

### Root Cause

Persistent SQLite tables already existed without the new column.

`Base.metadata.create_all()` does not alter existing schemas.

### Resolution

Reset development volume:

bash
docker compose down
docker volume rm ops-platform_auth-data
docker compose up -d --build

### Future Improvement

Use Alembic migrations for schema evolution.

---

## Asset Service Not Reachable On Port 8000

### Root Cause

Multiple contributing issues:

- incorrect Docker Compose `expose` usage
- conflicting host ports
- startup crashes from import failures

### Resolution

Updated Docker Compose to use explicit host port mappings:

yaml
asset-service:
  ports:
    - "8000:8000"

Validated using:

bash
docker compose ps
docker compose config

---

## Asset Service ImportError After Adding Auth Module

### Symptoms

Asset service failed with:

ImportError: cannot import name 'auth' from 'app'

### Root Cause

`auth.py` existed outside the FastAPI app package.

### Resolution

Moved:

services/asset_service/auth.py

into:

services/asset_service/app/auth.py

---

## Swagger OAuth Flow Failed Across Services

### Symptoms

Swagger authorization failed with:

TypeError: Failed to fetch

### Root Cause

Cross-origin OAuth requests between:

- asset-service Swagger
- auth-service token endpoint

caused browser/CORS failures.

### Resolution

Switched asset-service authentication from OAuth2 password flow to direct Bearer token validation using:

python
HTTPBearer
HTTPAuthorizationCredentials

### Result

Users now:

- authenticate through auth-service
- copy JWT tokens
- authorize asset-service Swagger manually

---

## Asset Service Failed After HTTPBearer Migration

### Root Cause

Legacy references to:

python
oauth2_scheme

remained after switching to `HTTPBearer`.

### Resolution

Replaced the auth module with a clean bearer-token validation implementation.

---

## Asset Creation Returned 500 Internal Server Error

### Symptoms

Admin POST requests returned:

500 Internal Server Error

### Root Cause

Swagger default payload reused duplicate unique hostname values:

json
{
  "hostname": "string"
}

### Resolution

Retested using unique hostnames.

### Future Improvement

Add explicit duplicate hostname handling.

---

## CRUD Error Handling Improvements

### Objective

Replace raw database failures with clean operational responses.

### Implementation

Added:

- `409 Conflict` handling
- graceful SQLAlchemy exception handling
- rollback protection
- structured HTTP error responses

### Validation

Confirmed:

- duplicate hostname conflicts return clean 409 responses
- missing assets return 404 responses
- rollback protection functions correctly

---

## PostgreSQL External Access For DBeaver

### Symptoms

DBeaver connected successfully but tables were not visible.

### Root Causes

Two separate issues:

1. Connected to default `postgres` database instead of the application database
2. PostgreSQL container port was not externally exposed

### Resolution

Added Docker port mapping:

yaml
ports:

- "5432:5432"

Updated DBeaver connection to use the application database instead of the default PostgreSQL database.

### Validation

Confirmed visibility of:

- assets
- audit_logs

tables.

---

## Audit Telemetry Implementation

### Objective

Implement persistent operational audit logging.

### Implementation

Added:

- `AuditLog` SQLAlchemy model
- CRUD audit event generation
- timestamped audit records
- `/audit-logs` admin endpoint
- PostgreSQL-backed telemetry storage

Tracked events:

- asset.create
- asset.update
- asset.delete

### Validation

Confirmed:

- audit entries persist in PostgreSQL
- audit events accessible through Swagger
- timestamps populate correctly
- asset IDs tracked correctly

### Current Limitation

Audit actor currently resolves as:

unknown

because JWT payloads do not yet contain:

- `username`
- `sub`

claims in the expected format.

### Planned Improvements

Future hardening work:

- JWT expiration support
- identity-aware JWT claims
- actor attribution improvements
- structured JSON logging
- org/tenant-aware telemetry

# Phase 4.5 — Troubleshooting Notes

---

## Issue

Logging Middleware Import / Initialization Problems

### Symptoms

- FastAPI application startup failures
- middleware registration errors
- import-related exceptions during container startup

### Root Cause

Logging utilities and request logging logic were originally embedded directly inside `main.py`, causing organizational complexity and dependency issues as the application expanded.

### Resolution

Created centralized logging utility module:

`app/logging_utils.py`

Separated:

- JSON formatting
- timestamp generation
- helper functions
- middleware support logic

Reduced logging complexity inside `main.py`.

### Validation

- FastAPI application started successfully
- middleware loaded correctly
- request logging executed consistently across endpoints

### Lessons Learned

Separating platform utilities early prevents architectural sprawl and significantly improves maintainability as backend services grow.

---

## Issue

JSON Serialization Failures in Structured Logging

### Symptoms

- internal server errors during request logging
- serialization exceptions in container logs
- failed logging events during API requests

### Root Cause

Certain request/response objects and datetime values were not automatically JSON serializable.

### Resolution

Implemented:

- explicit timestamp formatting
- controlled dictionary construction
- JSON-safe serialization handling

Ensured only serializable values are written into structured logs.

### Validation

- structured logs generated successfully
- no additional serialization exceptions observed
- logs displayed correctly in Docker container output

### Lessons Learned

Structured logging requires careful control of serialized object types, especially when working with request lifecycle objects and datetime handling.

---

## Issue

Duplicate Log Entries

### Symptoms

- repeated request log entries
- duplicate middleware logging output
- cluttered container logs

### Root Cause

Multiple logger handlers were being attached during application startup or reload cycles.

### Resolution

Added safeguards to prevent duplicate handler registration before logger initialization.

### Validation

- duplicate log entries stopped
- request telemetry normalized
- logging output became consistent

### Lessons Learned

Python logging handlers can unintentionally stack during development reloads if initialization safeguards are not implemented.

---

## Issue

Inconsistent Request Timing Metrics

### Symptoms

- inaccurate request duration values
- inconsistent middleware timing calculations

### Root Cause

Timing calculations were not consistently initialized before request execution.

### Resolution

Moved request timing initialization to the start of middleware execution and standardized duration calculations.

### Validation

- request duration values became consistent
- middleware timing metrics aligned with expected API behavior

### Lessons Learned

Middleware timing instrumentation must initialize before any request processing occurs to ensure reliable telemetry.

---

## Issue

Docker Cache / Rebuild Inconsistencies

### Symptoms

- updated logging code not appearing
- stale middleware behavior after code changes
- old log formats persisting

### Root Cause

Docker containers were still using cached image layers or mounted application state.

### Resolution

Performed container rebuilds using:

`docker compose up -d --build`

In some cases:

- full teardown
- container recreation
- volume reset

were required.

### Validation

- updated logging behavior appeared correctly
- middleware changes reflected immediately
- latest code executed successfully

### Lessons Learned

Docker layer caching can preserve outdated application behavior if containers are not rebuilt properly after backend architecture changes.

---

## Issue

Audit Log Date Filtering Inconsistencies

### Symptoms

- incomplete date filtering behavior
- unexpected audit log query results
- inconsistent search output

### Root Cause

Date parsing and filtering logic lacked consistent validation handling during initial implementation.

### Resolution

Improved:

- datetime parsing logic
- query parameter validation
- filtering conditions

Validated filtering behavior using multiple date range test cases.

### Validation

- date range filtering worked correctly
- audit queries returned expected results
- filtering logic behaved consistently across tests

### Lessons Learned

Date handling introduces subtle edge cases that require strict validation and consistent formatting standards.

---

## Issue

Main.py Becoming Monolithic

### Symptoms

- increasing difficulty navigating `main.py`
- mixed concerns across logging and API logic
- reduced maintainability

### Root Cause

Application responsibilities accumulated inside a single file as features expanded.

### Resolution

Began modularization process by extracting:

- logging utilities
- middleware helper logic

into reusable application modules.

### Validation

- `main.py` became cleaner and easier to navigate
- logging logic became reusable
- backend structure improved significantly

### Lessons Learned

Modularization should begin early in backend projects to avoid technical debt and reduce future refactoring complexity.

---

# Phase 4.6 — Troubleshooting Notes

---

## Issue

Alembic Files Created Only Inside Container

### Symptoms

- `alembic.ini` not visible locally
- Alembic directories missing from VS Code
- `find . -name "alembic.ini"` returned no results on host

### Root Cause

Alembic was initialized inside a non-bind-mounted container filesystem path instead of the project-mounted application directory.

### Resolution

- Identified actual runtime working directory
- Reinitialized Alembic inside `/app/app`
- Copied Alembic files from container to host repository using `docker cp`

### Validation

- `alembic.ini` appeared locally
- Alembic directories became visible in VS Code
- migration files persisted correctly after container restarts

### Lessons Learned

Docker bind mount boundaries directly impact filesystem persistence. Runtime-generated files must exist inside mounted directories to persist locally.

---

## Issue

Alembic Could Not Locate Configuration File

### Symptoms

- `FAILED: No config file 'alembic.ini' found`

### Root Cause

Alembic commands were executed from incorrect working directories inside the container.

### Resolution

Executed Alembic commands from:

bash
cd /app
alembic -c app/alembic.ini

# Phase 4.7 — RBAC & Permission Enforcement Hardening

## Issue

The platform required stronger RBAC enforcement validation and permission-aware authorization behavior before expanding observability and integration layers.

### Symptoms

- Viewer accounts could still access read endpoints successfully
- Authorization testing initially targeted incorrect endpoints
- Need for centralized permission validation structure
- Permission failures were not yet generating structured telemetry
- Auth flows lacked standardized error helper usage

### Root Cause

The platform initially focused on role validation but lacked:

- permission-centric authorization flow
- standardized forbidden/unauthorized error helpers
- centralized permission telemetry
- separation between authentication and authorization event handling

Additional contributing issue:

- testing initially used `GET /assets`
- viewer role legitimately possessed `asset:read`
- proper RBAC validation required `POST /assets`

### Validation

Confirmed:

#### Viewer Token

- `GET /assets` → `200`
- `POST /assets` → `403`

#### Admin Token

- `POST /assets` → `200`

#### Authorization Behavior

- permission checks correctly enforced
- role permissions mapped properly
- standardized forbidden responses operational

#### Middleware Stability

- auth middleware integrated successfully with FastAPI dependency injection
- bearer token extraction functioning correctly
- token claim validation functioning correctly

### Lessons Learned

- Permission-based authorization scales better than strict role-only checks
- `401` and `403` should remain operationally distinct
- RBAC testing must target endpoints requiring elevated permissions
- Standardized error utilities simplify future telemetry integration
- Permission abstractions improve future integration readiness

---

# Phase 4.8 — Request Correlation & Exception Observability

## Issue

The platform lacked centralized request lifecycle observability, request correlation IDs, and structured exception telemetry.

### Symptoms

- No request correlation tracking
- Request logs duplicated across middleware systems
- Unhandled exceptions lacked centralized structured logging
- Internal stack traces risked leaking during failures
- Service startup failures occurred after observability integration changes
- Localhost connectivity failures appeared after middleware updates

### Root Cause

The platform originally relied on decentralized route-level logging and lacked a dedicated middleware-driven observability layer.

Additional contributing issues:

- legacy request middleware remained active alongside new middleware
- circular imports developed between:
  - `request_con.py`
  - `logging_utils.py`
- request con utilities were imported directly into logging helpers
- exception handling lacked centralized failure-event generation

### Validation

Confirmed successful operation of:

#### Request Lifecycle Events

- `request.started`
- `request.completed`
- `request.failed`

#### Request Correlation

- shared `request_id` persisted across request lifecycle
- `x-request-id` response headers functioning correctly

#### Exception Handling

- sanitized `500` responses returned correctly
- middleware survived unhandled exceptions
- stack traces logged internally
- traceback leakage prevented to clients

#### Middleware Architecture

- duplicate request logging removed successfully
- centralized middleware architecture functioning correctly
- request con propagation stable under failures

#### Docker & Infrastructure Stability

- containers recovered successfully after rebuilds
- reverse proxy remained stable
- PostgreSQL remained healthy across restart cycles
- FastAPI startup sequence validated successfully

### Lessons Learned

- Middleware-driven observability is cleaner than route-level instrumentation
- `ConVar` provides reliable async-safe request con propagation
- Circular imports become increasingly likely in observability-heavy architectures
- Request correlation IDs are foundational for future distributed tracing
- Structured lifecycle logging greatly improves debugging and operational visibility
- Centralized exception telemetry significantly improves platform maintainability
- Duplicate middleware chains create noisy and misleading telemetry

---

# Phase 4.9 — Security Telemetry & Observability Hardening

## Issue

Centralized observability, request correlation, and security telemetry were not yet standardized across the platform. Authentication failures, RBAC denials, and unhandled exceptions lacked structured SIEM-ready logging and request traceability.

### Symptoms

- No request correlation IDs
- Duplicate request logging middleware
- No structured auth failure telemetry
- No structured RBAC denial telemetry
- Unhandled exceptions lacked centralized structured failure events
- Service startup failures caused by circular imports during middleware integration
- Inconsistent request lifecycle logging behavior
- Limited visibility into authorization failures and request origins

### Root Cause

The platform originally relied on decentralized request logging and lacked a dedicated middleware-driven observability architecture.

Additional contributing issues:

- request lifecycle logging existed both in middleware and `main.py`
- logging utilities imported request con directly, creating circular dependencies
- auth failures and RBAC denials returned HTTP errors without structured security telemetry
- no standardized event schema existed for operational or security events

### Validation

Validated successful operation of:

#### Request Lifecycle Logging

- `request.started`
- `request.completed`
- `request.failed`

#### Security Telemetry

- `auth.failure`
- `permission.denied`

#### Request Correlation

- shared `request_id` across all lifecycle and security events

#### Structured Metadata

Confirmed logging of:

- request_id
- actor email
- actor role
- source IP
- HTTP method
- request path
- status code
- severity
- environment
- service name
- stack traces
- denial reasons
- missing permissions

#### Auth & RBAC Behavior

Confirmed:

- Missing token → `401 auth.failure`
- Invalid permission → `403 permission.denied`
- Unhandled exception → `500 request.failed`
- Successful requests → `200 request.completed`

#### Middleware Stability

Confirmed:

- middleware survives exceptions
- request con persists correctly
- reverse proxy routing remains stable
- structured logging survives rebuilds and failures

### Lessons Learned

- Middleware-based observability is significantly cleaner than route-level logging
- `ConVar` provides reliable async-safe request con propagation in FastAPI
- Circular imports become increasingly common as observability layers mature
- Security telemetry should be treated as first-class platform infrastructure
- Structured JSON logging dramatically improves future SIEM and observability integration readiness
- Separating `401` authentication failures from `403` authorization failures provides clearer operational visibility
- Centralized logging schemas simplify future integrations with:
  - Datadog
  - Splunk
  - OpenTelemetry
  - Jaeger/Tempo
  - SIEM tooling
- Standardized severity tagging greatly improves future alerting and event classification

# Phase 5.0 — RBAC + Transaction Hardening

## Issue

Unauthorized access handling and database transaction recovery behavior required stabilization across protected endpoints.

### Symptoms

- `401 Unauthorized` responses after logout or expired tokens.
- `403 Forbidden` responses when viewer accounts attempted restricted operations.
- `500 Internal Server Error` during asset creation/update operations.
- Risk of unstable DB sessions after failed writes.

### Root Cause

- RBAC enforcement had not yet been fully validated across all permission scopes.
- Database transactions lacked sufficient rollback handling.
- SQLAlchemy exceptions were not consistently normalized into structured API responses.

### Resolution

- Validated JWT authorization flow through Swagger/OpenAPI authorization.
- Confirmed permission enforcement for:
  - `asset:create`
  - `asset:update`
  - `asset:delete`
  - `asset:read`
- Added exception handling for:
  - `IntegrityError`
  - `SQLAlchemyError`
- Implemented transactional rollback protections:
python
db.rollback()

md

# Phase 5.1 — Audit Logging + Query Optimization

## Issue

Audit logging lacked enterprise-grade filtering, pagination, and query protections.

### Symptoms

- Large unfiltered audit responses.
- No pagination support.
- No date range filtering.
- Invalid date formats caused server-side exceptions.
- Potential for excessive database query loads.

### Root Cause

- Audit endpoint was originally implemented as a basic query without scalability considerations.
- Missing validation around date parsing.
- No query constraints or pagination safeguards existed.

### Resolution

Added:

- Pagination:
python
limit
offset

md

# Phase 5.2 — Health Checks + Reliability Foundation

## Issue

Health monitoring endpoints lacked consistency, readiness support, and secure failure handling.

### Symptoms

- Duplicate `/db-health` endpoints existed simultaneously.
- Older DB health implementation exposed raw exception output.
- No readiness endpoint existed for orchestration validation.
- Mixed DB connection handling patterns across implementations.

### Root Cause

- Earlier temporary DB health implementation was not removed after newer dependency-injected version was added.
- Exception responses exposed internal database details.
- Readiness validation had not yet been implemented for orchestration support.

### Resolution

Removed legacy implementation:
python
with engine.connect()

## Issue

### Symptoms

Swagger UI failed to load correctly behind the nginx reverse proxy. `/docs` attempted to retrieve `/openapi.json` from an invalid location, causing broken API documentation rendering.

### Root Cause

FastAPI `root_path` and `openapi_url` settings conflicted with nginx reverse proxy path handling.

### Resolution

Updated FastAPI configuration to properly support reverse proxy routing:

python
root_path="/api/assets"
docs_url="/docs"
openapi_url="/openapi.json"

Validated nginx routing and rebuilt reverse proxy containers.

### Validation

Verified:

- `/api/assets/docs`
- `/api/assets/openapi.json`

Swagger UI loaded successfully behind nginx.

### Lessons Learned

FastAPI `root_path` already prepends proxied paths internally. `openapi_url` should remain local to the application rather than including the proxy prefix itself.

## Issue

### Symptoms

nginx returned `502 Bad Gateway` after TrustedHostMiddleware configuration changes.

### Root Cause

Malformed Python syntax inside the `TrustedHostMiddleware` configuration block prevented the asset service container from starting.

### Resolution

Removed leftover host entries and simplified the configuration to:

python
allowed_hosts=["*"]

Rebuilt the asset service container.

### Validation

Verified:

- asset service container healthy
- reverse proxy routing restored
- `/api/assets/health` returned expected responses

### Lessons Learned

Successful Docker rebuilds do not guarantee successful application startup. Container logs should always be inspected after middleware or syntax modifications.

## Issue

### Symptoms

TrustedHostMiddleware rejected valid localhost requests with:

400 Invalid host header

### Root Cause

nginx forwarded host headers differently than initially expected, causing TrustedHostMiddleware validation mismatches.

### Resolution

Temporarily relaxed trusted host enforcement using:

python
allowed_hosts=["*"]

Added nginx debug headers for future host validation troubleshooting.

### Validation

Validated successful requests through:

- localhost browser access
- curl testing
- nginx reverse proxy routing
- direct container access

### Lessons Learned

Reverse proxy host forwarding behavior must be fully understood before strict host validation rules are enforced.

## Issue

### Symptoms

Rate limiting behavior initially appeared inconsistent during rapid request testing.

### Root Cause

Request bursts exceeded configured thresholds very quickly, producing expected 429 responses without immediately obvious confirmation.

### Resolution

Performed controlled request flood testing using repeated curl loops and validated middleware enforcement behavior through structured logs.

### Validation

Observed:

- `429 Too Many Requests`
- structured warning logs
- request correlation IDs
- consistent middleware enforcement

### Lessons Learned

Structured request telemetry significantly improves validation and troubleshooting during security hardening implementation.

# Phase 5.5+ Troubleshooting Notes

## Issue

Grafana dashboard panels initially returned no data.

### Symptoms

Grafana connected to Prometheus successfully, but the first custom request-rate query did not populate.

### Root Cause

The assumed metric name `http_requests_total` was not the metric exposed by the asset service.

### Resolution

Verified available metrics using Prometheus/Grafana queries and switched to the actual exported metric:

promql
sum(rate(asset_service_http_request_duration_seconds_count[1m]))
Validation

The Platform Request Rate panel populated successfully.

Lessons Learned

Always confirm actual exported metric names before building dashboard panels.

Issue

Prometheus and Grafana connection needed validation.

Symptoms

Custom metric queries failed, making it unclear whether Grafana, Prometheus, or the application metrics were the problem.

Root Cause

The original issue was not the Prometheus/Grafana connection; it was an incorrect PromQL metric name.

Resolution

Ran the baseline query:

up
Validation

Grafana returned up = 1 for asset-service.

Lessons Learned

Use up first to validate scrape connectivity before troubleshooting application-level metrics.

Issue

Raw asset-service metric query showed unexpected metric labels and bucket data.

Symptoms

Querying the asset-service metric directly returned many series and bucket-style data.

Root Cause

The metric was a histogram-backed request duration metric, not a simple request counter.

Resolution

Used the _count suffix for request-rate calculations:

sum(rate(asset_service_http_request_duration_seconds_count[1m]))
Validation

Request rate displayed correctly.

Lessons Learned

Histogram metrics expose multiple series. Use _count for request count/rate and_bucket with histogram_quantile() for latency percentiles.

Issue

Swagger/OpenAPI failed behind reverse proxy.

Symptoms

Swagger UI displayed a failure loading the API definition and attempted to fetch:

/openapi.json
Root Cause

FastAPI docs were being accessed through a reverse-proxy path, but OpenAPI was still being requested from the root path instead of the proxied service path.

Resolution

Used the direct asset service docs endpoint temporarily:

<http://localhost:8001/docs>
Validation

Swagger loaded successfully through the direct service port.

Lessons Learned

FastAPI docs behind a reverse proxy may require root_path or adjusted Nginx path handling.

Issue

Latency panel initially risked using raw histogram buckets incorrectly.

Symptoms

Raw bucket metrics produced unsuitable graph behavior and inflated-looking values.

Root Cause

Histogram bucket metrics are cumulative and should not be graphed directly as normal latency values.

Resolution

Used histogram_quantile() for P95 latency:

histogram_quantile(
  0.95,
  sum by (le) (
    rate(asset_service_http_request_duration_seconds_bucket[5m])
  )
)
Validation

The P95 latency panel displayed meaningful latency values.

Lessons Learned

Use histogram buckets only with proper PromQL histogram functions.

Issue

Grafana unit option for latency was not obvious.

Symptoms

The Unit dropdown did not clearly show a seconds option.

Root Cause

Grafana groups and searches units by shorthand/category.

Resolution

Searched the Unit field for:

s

or:

seconds

and selected seconds.

Validation

Latency panel was configured with the appropriate unit.

Lessons Learned

Grafana unit settings may require searching by shorthand values.

Issue

5xx error-rate panel did not populate.

Symptoms

The 5xx error-rate query returned no data.

Root Cause

No matching 5xx series existed, and the initial assumed metric name did not exist.

Resolution

Attempted to use the confirmed request-duration count metric with status filtering.

Validation

The query still did not populate, which led to deeper inspection of available labels.

Lessons Learned

An empty error-rate panel can mean either no errors occurred or the required labels do not exist.

Issue

4xx/5xx error-rate filtering was not supported by current metrics.

Symptoms

Filtering by status or status_code did not produce useful results.

Root Cause

The asset service metric did not expose HTTP response status labels.

Resolution

Deferred true error-rate dashboards and replaced the panel with endpoint traffic distribution:

sum by (path) (
  rate(asset_service_http_request_duration_seconds_count[5m])
)
Validation

Endpoint traffic distribution populated successfully.

Lessons Learned

True error-rate dashboards require status-code-aware metrics.

Issue

Endpoint traffic panel was dominated by Prometheus scrape noise.

Symptoms

/metrics appeared as the highest-traffic endpoint.

Root Cause

Prometheus scraping the /metrics endpoint generated frequent internal monitoring traffic.

Resolution

Excluded /metrics from the endpoint traffic query:

sum by (path) (
  rate(
    asset_service_http_request_duration_seconds_count{
      path!="/metrics"
    }[5m]
  )
)
Validation

Real application endpoint traffic became easier to see.

Lessons Learned

Operational dashboards should often exclude internal scrape endpoints from application traffic panels.

Issue

Swagger/OpenAPI traffic added noise to endpoint traffic panels.

Symptoms

/docs and /openapi.json appeared in endpoint traffic visualizations.

Root Cause

Manual Swagger usage generated traffic that was useful for testing but noisy for operational dashboards.

Resolution

Recommended excluding docs/OpenAPI paths when needed:

sum by (path) (
  rate(
    asset_service_http_request_duration_seconds_count{
      path!="/metrics",
      path!="/docs",
      path!="/openapi.json"
    }[5m]
  )
)
Validation

Dashboard became more focused on real API traffic.

Lessons Learned

Dashboard queries should distinguish user/API traffic from tooling traffic.

Issue

Asset service status card needed to be converted from graph to health indicator.

Symptoms

The up{job="asset-service"} query displayed as a time-series graph.

Root Cause

The visualization type was still set to Time series.

Resolution

Changed visualization type to Stat.

Validation

Panel displayed a clear 1 for healthy asset-service status.

Lessons Learned

Availability checks are easier to read as Stat panels than time-series charts.

Issue

Auth service status card showed asset-service data instead of auth-service data.

Symptoms

The Auth Service Status panel displayed only asset-service-related data.

Root Cause

Prometheus was only scraping asset-service at that time.

Resolution

Added an auth-service scrape job to Prometheus configuration.

Validation

Prometheus began attempting to scrape auth-service.

Lessons Learned

Every service must be explicitly added to Prometheus scrape configuration.

Issue

Prometheus restart appeared to hang after adding auth-service scraping.

Symptoms

Prometheus did not restart cleanly after editing prometheus.yml.

Root Cause

The Prometheus configuration contained a duplicate static_configs field.

Resolution

Corrected prometheus.yml to use separate scrape jobs:

scrape_configs:

- job_name: "asset-service"
    static_configs:
  - targets: ["asset_service:8000"]

- job_name: "auth-service"
    static_configs:
  - targets: ["auth_service:8000"]
Validation

Prometheus logs showed:

Server is ready to receive web requests.
Lessons Learned

Prometheus YAML is sensitive to structure and duplicate fields.

Issue

Auth-service target appeared in Prometheus but showed HTTP 404.

Symptoms

Prometheus targets page showed auth-service as down with a 404 on /metrics.

Root Cause

The auth service did not expose a /metrics endpoint yet.

Resolution

Added Prometheus FastAPI instrumentation to auth_service/main.py:

from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
Validation

The /metrics endpoint became available after rebuilding the service.

Lessons Learned

Adding a Prometheus scrape target is not enough; the application must expose a metrics endpoint.

Issue

Browser access to auth-service metrics on port 8000 hit the wrong service.

Symptoms

Opening:

<http://localhost:8000/metrics>

did not show auth-service metrics.

Root Cause

Port 8000 was mapped to the Nginx reverse proxy, not directly to auth_service.

Resolution

Used the direct auth-service host port:

<http://localhost:8002/metrics>
Validation

Auth-service metrics loaded from port 8002.

Lessons Learned

Always distinguish reverse-proxy ports from direct service ports.

Issue

Auth-service direct port initially did not respond.

Symptoms

<http://localhost:8002/metrics> failed to load.

Root Cause

The auth_service container was not running.

Resolution

Checked container state:

docker compose ps

and restarted/rebuilt auth_service.

Validation

auth_service appeared in Docker Compose status after rebuild.

Lessons Learned

Before troubleshooting networking, verify the target container is running.

Issue

auth_service container was missing from docker compose ps.

Symptoms

docker compose ps listed asset_service, Grafana, Postgres, Prometheus, and reverse proxy, but not auth_service.

Root Cause

auth_service was crashing during startup.

Resolution

Checked logs:

docker compose logs auth_service --tail=80
Validation

Logs revealed the exact Python import error.

Lessons Learned

A missing service in docker compose ps often means the container exited immediately after startup.

Issue

auth_service crashed after adding Prometheus instrumentation.

Symptoms

Logs showed:

ModuleNotFoundError: No module named 'prometheus_fastapi_instrumentator'
Root Cause

The instrumentation package was imported in code but not installed in the auth service container.

Resolution

Added the dependency to services/auth_service/requirements.txt:

prometheus-fastapi-instrumentator

Then rebuilt:

docker compose up -d --build auth_service
Validation

auth_service started successfully.

Lessons Learned

Any new Python import used inside a container must be added to that service’s requirements file.

Issue

Auth service metrics needed validation after dependency fix.

Symptoms

Needed to confirm whether /metrics was actually exposed after rebuild.

Root Cause

Instrumentation was newly added and required endpoint validation.

Resolution

Opened:

<http://localhost:8002/metrics>
Validation

Metrics output appeared, including:

python_gc_objects_collected_total
process_cpu_seconds_total
http_requests_total
http_request_duration_seconds
Lessons Learned

Direct endpoint validation is the fastest way to confirm service instrumentation.

Issue

Prometheus auth-service target needed final validation.

Symptoms

After metrics were exposed, Prometheus still needed to re-scrape auth-service.

Root Cause

Prometheus target health updates only after scrape attempts.

Resolution

Refreshed:

<http://localhost:9090/targets>
Validation

auth-service showed UP.

Lessons Learned

After fixing metrics endpoints, always validate in Prometheus targets before relying on Grafana panels.

Issue

Auth Service Status Grafana panel required the correct job label.

Symptoms

Auth-service status panel initially could not show data.

Root Cause

The correct Prometheus job label only existed after auth-service was added and successfully scraped.

Resolution

Used:

up{job="auth-service"}
Validation

Grafana displayed auth-service as healthy.

Lessons Learned

Grafana service health cards depend on consistent Prometheus job naming.

Issue

Database health card did not have direct Postgres metrics available.

Symptoms

A direct query like:

up{job="postgres"}

was not available.

Root Cause

No PostgreSQL exporter had been added yet.

Resolution

Used application-level database health endpoint traffic as a temporary health signal.

Validation

Database health checks were visible through application metrics.

Lessons Learned

True database infrastructure metrics require a database exporter.

Issue

CPU usage panel needed a process-level metric.

Symptoms

Needed a dashboard panel for runtime CPU behavior.

Root Cause

CPU telemetry was available through Prometheus client process metrics.

Resolution

Used:

rate(process_cpu_seconds_total[1m])
Validation

CPU usage panel populated.

Lessons Learned

Process-level metrics provide useful baseline runtime visibility before container-level exporters are added.

Issue

Memory usage panel needed a process-level metric.

Symptoms

Needed a dashboard panel for runtime memory behavior.

Root Cause

Memory telemetry was available through Prometheus client process metrics.

Resolution

Used:

process_resident_memory_bytes
Validation

Memory usage panel populated.

Lessons Learned

Resident memory is a useful starting point for service memory dashboards.

Issue

Observability coverage was initially inconsistent across services.

Symptoms

asset_service exposed metrics, but auth_service did not.

Root Cause

Instrumentation had been implemented service-by-service rather than standardized across the platform.

Resolution

Added Prometheus instrumentation to auth_service and configured Prometheus to scrape both services.

Validation

Both asset-service and auth-service showed healthy in Prometheus and Grafana.

Lessons Learned

Observability should be treated as a platform-wide baseline requirement for every service.

## Issue

### Symptoms

Grafana per-service CPU dashboard panels displayed no data despite cAdvisor running and Prometheus targets appearing healthy.

### Root Cause

The original PromQL queries depended on Docker Compose metadata labels (`container_label_com_docker_compose_service`) that were not exposed by the WSL2/Docker Desktop cAdvisor environment.

### Resolution

Validated cAdvisor metric exposure directly through:

- <http://localhost:8080/metrics>
- Prometheus query testing

Replaced label-dependent PromQL queries with direct container ID matching:

promql
rate(container_cpu_usage_seconds_total{
  id=~"/docker/.*",
  cpu="total"
}[5m])* 100

## Issue

### Symptoms

Grafana memory telemetry panels initially failed to display meaningful infrastructure usage trends.

### Root Cause

Grafana auto-unit detection and initial query structure were not aligned with container telemetry formatting.

### Resolution

Created dedicated memory telemetry panels using:

promql
container_memory_usage_bytes{
  id=~"/docker/.*"
}

## Issue

### Symptoms

Promtail successfully started but Grafana Loki queries returned no container logs.

### Root Cause

WSL2/Docker Desktop did not expose Docker JSON log files under:
`/var/lib/docker/containers/*/*.log`

The mounted log directory inside the Promtail container was effectively empty.

### Resolution

Switched Promtail from filesystem log scraping to Docker service discovery using Docker socket integration.

Updated Promtail configuration to use:

yaml
docker_sd_configs:

- host: unix:///var/run/docker.sock

## Issue

### Symptoms

Security dashboard panels for:

- auth.failed
- permission.denied
- token.invalid
- token.expired

initially displayed no data.

### Root Cause

Authentication and authorization failures were only generating generic HTTP status code responses without explicit structured security telemetry events.

### Resolution

Implemented structured security event logging inside `auth.py` and `main.py`:

- auth.failed
- permission.denied
- token.invalid
- token.expired

Added:

- category
- event
- reason
- client
- path
- method
- outcome
- user_email

to structured JSON log payloads.

### Validation

Grafana Loki security telemetry panels successfully populated during failed authentication and authorization testing.

### Lessons Learned

Operational observability and security observability require intentional structured event design rather than reliance on generic HTTP response codes.

## Issue

### Symptoms

Grafana SMTP test notifications failed authentication repeatedly.

### Root Cause

Several SMTP configuration mismatches existed:

- Proton Mail free tier does not support SMTP app-password authentication
- Grafana SMTP environment variables still referenced Proton SMTP host/user
- Gmail app password initially included whitespace formatting

### Resolution

Migrated SMTP integration to Gmail app-password authentication.

Updated:
yaml
GF_SMTP_HOST: "smtp.gmail.com:587"
GF_SMTP_USER: "<staticbinaryops@gmail.com>"
GF_SMTP_FROM_ADDRESS: "<staticbinaryops@gmail.com>"

## Issue

### Symptoms

Grafana alert emails were not being delivered after SMTP configuration.

### Root Cause

Grafana SMTP configuration used Gmail SMTP settings initially, while the environment later transitioned toward Proton Mail SMTP configuration and required consistent container environment variables.

### Resolution

Updated Grafana SMTP environment variables in `docker-compose.yml`, validated SMTP configuration inside the running Grafana container, and rebuilt/restarted the Grafana service.

### Validation

- Verified SMTP variables inside the container with:

  bash
  docker compose exec grafana env | grep GF_SMTP
  
- Successfully generated and received Grafana alert test emails.

### Lessons Learned

- SMTP configuration should be externally validated from inside containers.
- Alerting infrastructure should be validated early before larger observability expansion.
- Consistent mail provider configuration avoids future operational confusion.

---

## Issue

### Symptoms

Grafana dashboard panels became empty when Prometheus or dependent telemetry services were unavailable.

### Root Cause

Grafana dashboards depended on Prometheus query availability for visualization rendering.

### Resolution

Reviewed service dependency behavior and intentionally shifted architecture philosophy toward graceful degradation instead of hard service coupling.

### Validation

- Verified Grafana remained operational even during Prometheus outages.
- Confirmed only visualization data disappeared while the Grafana service itself remained healthy.

### Lessons Learned

- Observability services should fail independently whenever possible.
- Service survivability is more important than maintaining every visualization during outages.
- Graceful degradation is a critical platform engineering principle.

---

## Issue

### Symptoms

Docker service startup order occasionally caused dependent services to initialize before PostgreSQL or other infrastructure dependencies were healthy.

### Root Cause

Initial `depends_on` configuration only validated container startup order rather than service health readiness.

### Resolution

Added Docker health checks and upgraded `depends_on` to use:

yaml
condition: service_healthy

### Validation

- PostgreSQL health checks completed before dependent service startup.
- `asset_service` and `auth_service` waited for healthy database initialization before starting.

### Lessons Learned

- Container startup does not equal application readiness.
- Health-aware dependencies significantly improve orchestration reliability.
- Proper startup sequencing improves operational resilience.

---

## Issue

### Symptoms

`asset_service` readiness endpoint failed after PostgreSQL outage simulation.

### Root Cause

Database retry logic did not correctly receive the SQLAlchemy session object required for rollback handling.

### Resolution

Updated:

python
retry_database_operation(..., db=db)

within `/health/ready` readiness validation logic.

### Validation

- Successfully stopped PostgreSQL and validated:

  json
  {
    "status": "not_ready"
  }
  
- Successfully restarted PostgreSQL and validated automatic readiness recovery.

### Lessons Learned

- Resilience testing exposes hidden dependency assumptions.
- Retry utilities should always support explicit rollback handling.
- Readiness checks are critical for operational survivability.

---

## Issue

### Symptoms

`dependency.database.unavailable` messages appeared as plain  rather than structured JSON logs.

### Root Cause

Database dependency failure events were not routed through centralized structured logging utilities.

### Resolution

Created:

python
build_dependency_health_log()

inside `logging_utils.py` and migrated dependency telemetry into structured JSON logging.

### Validation

- Dependency failures appeared in structured JSON format.
- Loki correctly parsed dependency events.

### Lessons Learned

- Operational telemetry should always use centralized structured logging.
- Plain  logs reduce searchability and observability value.
- Infrastructure telemetry should follow the same schema as application telemetry.

---

## Issue

### Symptoms

Request correlation IDs were not consistently propagated across request lifecycle logs.

### Root Cause

Middleware request con management lacked centralized request ID handling and cleanup.

### Resolution

Implemented:

- `RequestIDMiddleware`
- request con variables
- request lifecycle correlation
- request cleanup/reset handling

### Validation

- Request IDs consistently appeared across:

  - request.started
  - request.completed
  - dependency events
  - auth events

### Lessons Learned

- Correlation IDs are foundational for operational debugging.
- Middleware-level con management greatly improves observability consistency.
- Cleanup/reset handling is important for long-running async services.

---

## Issue

### Symptoms

Tempo container continuously restarted after deployment.

### Root Cause

Tempo configuration schema used unsupported fields:

yaml
compactor:
ingester:
compaction:

for the deployed Tempo image version.

### Resolution

Reduced Tempo configuration to a minimal supported schema using only:

- server
- distributor
- storage

### Validation

- Tempo container started successfully.
- OTLP receivers initialized correctly.

### Lessons Learned

- Grafana ecosystem components can have significant version-specific configuration differences.
- Minimal working configurations are best for initial deployments.
- Observability components should be validated incrementally.

---

## Issue

### Symptoms

OpenTelemetry traces were not visible in Grafana Tempo despite successful service instrumentation.

### Root Cause

Tempo OTLP receivers bound only to:

127.0.0.1

inside the Tempo container, preventing Docker network access from other containers.

### Resolution

Updated Tempo OTLP receiver bindings to:

yaml
endpoint: 0.0.0.0:4317
endpoint: 0.0.0.0:4318

### Validation

- Tempo OTLP receivers became reachable from other containers.
- Traces successfully appeared inside Grafana Explore.

### Lessons Learned

- Container-local loopback interfaces are inaccessible across Docker networks.
- Observability pipelines require explicit network exposure validation.
- Receiver binding configuration is critical in distributed systems.

---

## Issue

### Symptoms

OpenTelemetry traces were not exporting successfully from `asset_service`.

### Root Cause

Incorrect OTLP gRPC endpoint formatting:

python
endpoint="<http://tempo:4317>"

### Resolution

Updated exporter configuration to:

python
endpoint="tempo:4317"

and later validated HTTP OTLP exporter compatibility as well.

### Validation

- Trace export errors disappeared.
- Tempo successfully ingested traces.

### Lessons Learned

- OTLP gRPC exporters require raw host:port formatting.
- Exporter transport protocols must match receiver configuration.
- Telemetry transport validation is critical during observability rollout.

---

## Issue

### Symptoms

Trace queries returned zero results despite successful Tempo deployment.

### Root Cause

Grafana Tempo query syntax used incorrect selector format.

### Resolution

Updated trace queries to:

{resource.service.name="asset-service"}

### Validation

- Traces successfully appeared in Grafana Explore.
- Trace search functionality became operational.

### Lessons Learned

- Tempo queries use label selector syntax similar to Loki.
- Trace ingestion and trace querying are separate validation steps.
- Query syntax correctness is essential during observability validation.

---

## Issue

### Symptoms

Structured logs lacked trace correlation metadata.

### Root Cause

OpenTelemetry span con was not injected into centralized structured logging.

### Resolution

Added:

- `get_trace_con()`
- `trace_id`
- `span_id`

to base structured logging events.

### Validation

- Structured logs displayed trace correlation fields.
- Loki logs matched Tempo traces successfully.

### Lessons Learned

- Logs and traces become exponentially more valuable when correlated.
- Shared telemetry identifiers dramatically improve investigations.
- Trace-aware logging is foundational for mature observability systems.

---

## Issue

### Symptoms

Multi-service tracing existed independently but lacked cross-service propagation.

### Root Cause

`asset_service` used local JWT validation rather than calling `auth_service` remotely.

### Resolution

Instrumented both services independently and added outbound Requests instrumentation to prepare for future distributed trace propagation.

### Validation

- `asset_service` traces operational.
- `auth_service` traces operational.
- Requests instrumentation active.

### Lessons Learned

- True distributed tracing requires actual inter-service communication.
- Independent instrumentation is still valuable foundational work.
- Trace propagation readiness should be built before architectural expansion.

---

## Issue

### Symptoms

Request metadata was not visible inside Tempo spans.

### Root Cause

OpenTelemetry spans were not enriched with request lifecycle metadata.

### Resolution

Added middleware-level trace enrichment:

- request ID
- HTTP method
- request path
- client IP

using:

python
current_span.set_attribute(...)

### Validation

- Request attributes appeared inside Grafana Tempo spans.
- Trace investigation visibility improved significantly.

### Lessons Learned

- Raw traces are far less useful without enrichment.
- Middleware-level enrichment provides consistent telemetry coverage.
- Request metadata dramatically improves operational investigations.

# Phase 5.9.1 Troubleshooting Notes

## Issue

### Symptoms

- Docker commands unavailable after reboot
- WSL reported Docker command missing
- Docker Desktop integration failure reported

### Root Cause

- Docker Desktop WSL integration failed to reconnect after reboot

### Resolution

- Restarted Docker Desktop
- Verified Ubuntu WSL integration
- Restarted platform stack

### Validation

- Docker commands functional
- Docker Compose services visible
- Platform services accessible

### Lessons Learned

- Always verify Docker Desktop before opening project terminals after reboot
- WSL integration failures can temporarily make Docker appear unavailable

---

## Issue

### Symptoms

- Asset Service Down alert remained Normal while service was offline
- Prometheus target showed DOWN

### Root Cause

- Alert query logic conflicted with Grafana threshold evaluation

### Resolution

Replaced:

promql
up{job="asset-service"} == 0

With:

promql
up{job="asset-service"}

Threshold:

IS BELOW 1

### Validation

- Alert entered Pending
- Alert entered Firing
- Email notification received
- Recovery notification received

### Lessons Learned

- Use native Prometheus metric values when possible
- Avoid unnecessary Boolean conversions in alert expressions

---

## Issue

### Symptoms

- Prometheus Target Down alert repeatedly entered No Data state
- Alert generated unnecessary notifications

### Root Cause

- Prometheus was not configured as a scrape target
- Alert monitored a target that did not exist

### Resolution

- Paused Prometheus Target Down alert
- Deferred until Prometheus self-monitoring is implemented

### Validation

- Alert noise eliminated
- Remaining alerts continued functioning normally

### Lessons Learned

- Every alert should be actionable
- No Data conditions require investigation before production use

---

## Issue

### Symptoms

- Asset Service telemetry missing from shared request metrics
- Queries returned data for Auth Service only

### Root Cause

Asset Service used:

asset_service_http_requests_total
asset_service_http_request_duration_seconds

Auth Service used:

http_requests_total
http_request_duration_seconds

### Resolution

- Standardized Asset Service metric naming
- Added shared service labels

### Validation

Prometheus successfully returned:

promql
http_requests_total{service="asset-service"}

### Lessons Learned

- Shared telemetry standards simplify dashboards and alerting
- Metric consistency should be enforced platform-wide

---

## Issue

### Symptoms

- Asset Service 5xx Error Alert returned No Data
- Alert never entered Pending or Firing

### Root Cause

- No 5xx telemetry existed
- Only 2xx status series were present

### Resolution

Implemented:

promql
(
  sum(
    rate(
      http_requests_total{
        service="asset-service",
        status="5xx"
      }[5m]
    )
  )
)
or vector(0)

Added temporary endpoint to generate controlled HTTP 500 responses.

### Validation

- HTTP 500 generated successfully
- Prometheus recorded status="5xx"
- Alert entered Pending
- Alert entered Firing
- Email notification delivered

### Lessons Learned

- Application alerts require application failures for validation
- Controlled testing endpoints are useful during alert validation
- Use `or vector(0)` to eliminate No Data ambiguity

---

## Issue

### Symptoms

- Availability alerts only detected service outages
- Application failures could occur without triggering alerts

### Root Cause

- Monitoring strategy initially focused on container availability

### Resolution

- Expanded monitoring to include application-level error telemetry
- Implemented Asset Service 5xx Error Alert

### Validation

- Application-generated failures detected successfully
- Alert pipeline validated without requiring service outage

### Lessons Learned

- Availability monitoring is necessary but insufficient
- Error rate monitoring provides significantly more operational value
- Future alert development should prioritize readiness, latency, and dependency health monitoring

# Phase 5.9.2 Troubleshooting Notes

## Issue

### Symptoms

Request Volume by Service panel displayed:

{service="asset-service"}
{}

instead of showing both Asset Service and Auth Service separately.

### Root Cause

Auth Service metrics were being emitted without a `service` label, causing Prometheus to group the metrics into an unlabeled `{}` series.

### Resolution

Investigated Prometheus metrics and discovered Auth Service was exposing `http_requests_total` without the standardized service label.

Created:

services/auth_service/app/metrics.py

Added standardized metric definitions and custom metric recording logic.

Added custom metrics middleware to Auth Service and exposed a dedicated:

/metrics

endpoint.

### Validation

Prometheus query:

promql
http_requests_total{job="auth-service"}

returned:

service="auth-service"

Dashboard query:

promql
sum by (service) (
  rate(http_requests_total{service!=""}[5m])
)

successfully displayed:

asset-service
auth-service

### Lessons Learned

Dashboard validation can expose instrumentation inconsistencies that are not obvious during service development. Standardized metric labels are critical for multi-service observability.

---

## Issue

### Symptoms

Auth Service metrics appeared in Prometheus but did not follow the same labeling standards as Asset Service.

### Root Cause

Auth Service relied on automatic Prometheus instrumentation rather than the custom metrics framework used by Asset Service.

### Resolution

Removed automatic instrumentation and implemented a dedicated metrics module:

services/auth_service/app/metrics.py

Added:

- Request counter
- Request duration histogram
- Status code normalization
- Metrics endpoint
- Metrics middleware

### Validation

Both services now expose:

http_requests_total
http_request_duration_seconds

with identical label structures:

service
method
handler
status

### Lessons Learned

Consistency between services is more important than convenience. Shared observability standards simplify dashboards, alerting, and future expansion.

---

## Issue

### Symptoms

Container CPU Usage dashboard panel displayed:

No data

### Root Cause

Grafana query expected cAdvisor metrics to contain:

name=

or

container=

labels.

Current cAdvisor deployment exposed container metrics using only:

id=

labels.

### Resolution

Inspected Prometheus metrics:

promql
container_cpu_usage_seconds_total

Discovered Docker container identifiers were stored in the `id` label.

Updated panel query:

promql
sum by (id) (
  rate(
    container_cpu_usage_seconds_total{
      id=~"/docker/.*"
    }[5m]
  )
)

### Validation

CPU utilization graphs populated successfully for all running containers.

### Lessons Learned

Do not assume label names in exported metrics. Always inspect raw Prometheus metrics before designing dashboard queries.

---

## Issue

### Symptoms

Container Memory Usage dashboard panel displayed:

No data

### Root Cause

Memory query relied on nonexistent container labels.

cAdvisor exposed Docker metrics through:

id=

rather than:

container=

or

name=

### Resolution

Updated memory query:

promql
sum by (id) (
  container_memory_usage_bytes{
    id=~"/docker/.*"
  }
)

### Validation

Memory utilization panel successfully displayed active Docker containers and memory consumption.

### Lessons Learned

cAdvisor label structures can vary between versions and deployment methods. Validate actual metric labels before creating Grafana panels.

---

## Issue

### Symptoms

Container CPU and Memory panels displayed Docker container IDs rather than service names.

### Root Cause

cAdvisor exported metrics using Docker container identifiers:

/docker/<container-id>

without human-readable container name labels.

### Resolution

Mapped Docker IDs to container names using:

bash
docker ps --format "table {{.ID}}\t{{.Names}}"

Documented the relationship between IDs and container names for troubleshooting.

Deferred friendly-name relabeling as a future enhancement.

### Validation

Container resource metrics became usable despite identifier formatting limitations.

### Lessons Learned

Functional observability takes priority over dashboard polish. Service-name relabeling can be implemented later without impacting operational visibility.

---

## Issue

### Symptoms

Dashboard development uncovered inconsistencies between service instrumentation implementations.

### Root Cause

Observability validation had not previously been performed using cross-service Grafana dashboards.

### Resolution

Built and validated the following dashboard panels:

- Service Availability
- Request Volume by Service
- 5xx Error Rate by Service
- 4xx Error Rate by Service
- P95 Request Latency by Service
- P95 Request Latency by Endpoint
- Container CPU Usage
- Container Memory Usage

Exported dashboard JSON for version control.

### Validation

Dashboard successfully visualized:

- Service health
- Traffic volume
- Error rates
- Request latency
- Container resource consumption

### Lessons Learned

Operational dashboards are not just visualization tools; they are validation tools that expose implementation gaps, telemetry inconsistencies, and monitoring blind spots.

# Phase 5.9.3 — Troubleshooting Notes

## Issue

### Symptoms

Security counters appeared in `/metrics` output but no metric values were displayed.

Example:

# HELP auth_login_success_total Total successful authentication attempts

# TYPE auth_login_success_total counter

without corresponding metric data.

### Root Cause

Counters are only created after the first event is recorded.

Metric definitions existed but no authentication events had occurred since deployment.

### Resolution

Generated test activity:

Successful logins
Failed logins
Role changes

to initialize counters.

### Validation

Verified metric values appeared:

auth_login_success_total{...} 1.0
auth_login_failure_total{...} 2.0
role_change_total{...} 1.0

### Lessons Learned

Prometheus counters do not emit label values until an event increments the metric.

---

## Issue

### Symptoms

Permission denied metric remained at zero despite testing authorization workflows.

### Root Cause

Test account:

<viewer2@test.com>

had previously been promoted to:

admin

during earlier testing.

The account no longer generated authorization failures.

### Resolution

Created a new viewer-only account:

<viewer3@test.com>

and attempted access to:

/admin

endpoint.

### Validation

Observed:

json
{
  "detail": "Insufficient permissions"
}

Verified metric:

permission_denied_total{reason="insufficient_role",required_role="admin",service="auth-service"} 1.0

### Lessons Learned

Maintain dedicated test accounts for:

viewer
admin
security testing

to prevent role drift from affecting validation.

---

## Issue

### Symptoms

Security Operations Dashboard showed:

No Data

for Expired Token Events.

### Root Cause

No expired JWT tokens had been generated since deployment.

Metric existed but had never been incremented.

### Resolution

Confirmed instrumentation was present in:

python
verify_token()

and deferred validation until a future expired token test.

### Validation

Verified metric registration:

expired_token_total

appeared in `/metrics`.

### Lessons Learned

"No Data" is not necessarily a dashboard failure.

In security monitoring it often indicates:

No observed security events

which is valid operational information.

---

## Issue

### Symptoms

Loki queries using:

logql
{service="auth-service"}

returned no results.

### Root Cause

Promtail label values differed from application log values.

Actual label:

service=auth_service

Expected label:

service=auth-service

### Resolution

Inspected Loki labels and discovered:

container=/ops-auth-service
service=auth_service
service_name=auth_service
job=docker

Updated queries to use:

logql
{container="/ops-auth-service"}

### Validation

Successfully retrieved:

auth.failed
token.invalid
permission.denied

events.

### Lessons Learned

Always inspect Loki labels before building dashboard queries.

Do not assume label values match application service names.

---

## Issue

### Symptoms

Security Event Volume panel produced visualization errors.

Example:

Data is missing a string field

### Root Cause

Incorrect LogQL filtering syntax was used.

Initial queries contained malformed quote escaping and filter placement.

### Resolution

Updated query:

logql
count_over_time(
  {container="/ops-auth-service"}
  |= "\"category\": \"security\""
  [5m]
)

### Validation

Observed security-event spikes during testing activity.

### Lessons Learned

LogQL metric queries are more sensitive to filter placement and quote escaping than PromQL.

Validate queries directly in Explore before dashboard creation.

---

## Issue

### Symptoms

Loki panel returned:

parse error at line 1
syntax error: unexpected IDENTIFIER

### Root Cause

Prometheus and Loki query languages were accidentally mixed.

Example:

sum(invalid_token_total)
{container="/ops-auth-service"} |= "token.invalid"

combined PromQL and LogQL syntax.

### Resolution

Separated dashboards into:

Prometheus Metrics
Loki Log Queries

Prometheus:

promql
sum(invalid_token_total)

Loki:

logql
{container="/ops-auth-service"} |= "token.invalid"

### Validation

Both panels rendered correctly after separation.

### Lessons Learned

Prometheus metrics and Loki logs should be treated as separate data models even when displayed on the same dashboard.

---

## Issue

### Symptoms

Authentication Failure Rate panel appeared to display extremely small values.

Example:

0.003

instead of expected failure counts.

### Root Cause

Query used:

promql
rate(auth_login_failure_total[5m])

which calculates:

events per second

rather than total events.

### Resolution

Confirmed behavior was correct.

Evaluated alternative query:

promql
increase(auth_login_failure_total[5m])

for count-based visualization.

### Validation

Rate spikes matched generated authentication failures.

### Lessons Learned

Use:

promql
rate()

for velocity and trend monitoring.

Use:

promql
increase()

for event count monitoring.

Both provide useful but different operational perspectives.

---

## Issue

### Symptoms

Docker commands failed after system reboot and BSOD recovery.

Examples:

docker ps
Failed to initialize: protocol not available

unable to get image
failed to connect to docker API

### Root Cause

Docker Desktop WSL integration became disabled following Docker Desktop restart.

Ubuntu WSL instance no longer had access to Docker Desktop's shared socket.

### Resolution

Re-enabled:

Docker Desktop
→ Settings
→ Resources
→ WSL Integration
→ Ubuntu

Restarted Docker Desktop.

### Validation

Verified:

bash
docker ps

returned successfully.

Verified:

bash
docker compose up -d

started all platform services.

### Lessons Learned

Docker Desktop updates, crashes, and WSL restarts can silently disable WSL integration.

When Docker suddenly loses access to:

/var/run/docker.sock

check WSL Integration settings before troubleshooting containers.

## Issue

Security Metrics Not Appearing In Grafana

### Symptoms

auth_login_failure_total returned no data
invalid_token_total returned no data
permission_denied_total returned no data

### Root Cause

Security metrics were implemented but had not yet been incremented by platform activity.

Prometheus only exposed series after the counters were created and updated.

### Resolution

Generated validation security events:

Failed Authentication Attempts
Invalid JWT Requests
Permission Denied Requests

Confirmed metrics became available through:

<http://localhost:8002/metrics>

### Validation

auth_login_failure_total visible
invalid_token_total visible
permission_denied_total visible

### Lessons Learned

Prometheus counters may not appear until the metric has been incremented at least once.

---

## Issue

Authentication Failure Detection Validation

### Symptoms

Need to validate authentication failure detection pipeline.

### Root Cause

Detection rule existed but required real event generation for testing.

### Resolution

Generated:

15+ failed login attempts

Validated:

auth_login_failure_total
sum(increase(auth_login_failure_total[5m]))

### Validation

Threshold exceeded
Alert entered FIRING state
Detection screenshot captured

### Lessons Learned

Detection validation should always include real event generation and alert verification.

---

## Issue

Invalid Token Detection Validation

### Symptoms

Need to validate invalid token monitoring and alerting.

### Root Cause

Alert rule required live security events.

### Resolution

Generated:

15+ invalid JWT requests

Validated:

invalid_token_total
sum(increase(invalid_token_total[5m]))

### Validation

Metric incremented
Threshold exceeded
Alert evaluated successfully

### Lessons Learned

Security detections should be validated using repeatable event-generation procedures.

---

## Issue

Loki Security Event Detection Query Validation

### Symptoms

Need to confirm Loki can identify security events.

### Root Cause

Log-based detection had not previously been validated.

### Resolution

Queried:

logql
{container="/ops-auth-service"}
|= "\"category\": \"security\""

Confirmed structured security events existed.

### Validation

Observed:

auth.failed
token.invalid
permission.denied

events within Loki.

### Lessons Learned

Structured logging enables detection engineering without requiring additional application changes.

---

## Issue

Security Event Volume Detection Validation

### Symptoms

Need to validate log-driven security alerting.

### Root Cause

Security event volume alert required threshold testing.

### Resolution

Generated:

Authentication Failures
Invalid Token Events

Executed:

logql
sum(
  count_over_time(
    {container="/ops-auth-service"}
    |= "\"category\": \"security\""
    [5m]
  )
)

### Validation

Security event count exceeded threshold
Alert evaluation successful
Detection graph captured

### Lessons Learned

Loki-based detections provide complementary visibility beyond metric-based monitoring.

---

## Issue

Token Abuse Detection Validation

### Symptoms

Need to validate token abuse monitoring.

### Root Cause

New Loki detection required event generation.

### Resolution

Generated:

15+ invalid token requests

Executed:

logql
sum(
  count_over_time(
    {container="/ops-auth-service"}
    |= "token.invalid"
    [5m]
  )
)

### Validation

Threshold exceeded
Detection logic validated

### Lessons Learned

Specific event detections provide more actionable alerting than generic volume monitoring.

# Phase 5.9.5 Troubleshooting Notes

## Issue

### Symptoms

Auth service container failed to start after adding administrative monitoring telemetry.

### Root Cause

`main.py` imported new metric functions that did not yet exist in `metrics.py`.

### Resolution

Added:

- `record_admin_endpoint_access()`
- `record_privilege_escalation_attempt()`
- `record_user_management_action()`

to `services/auth_service/app/metrics.py`.

### Validation

bash
curl -s <http://localhost:8002/metrics> | grep -E \
"admin_endpoint_access|privilege_escalation|user_management_action"

Metrics successfully exposed.

### Lessons Learned

When adding new telemetry, implement metric definitions before importing them into application code.

---

## Issue

### Symptoms

Auth service failed startup with:

ImportError: cannot import name 'record_admin_endpoint_access'

### Root Cause

Function existed in source file but was incorrectly indented, causing Python to treat it as nested within another function.

### Resolution

Corrected indentation so all metric helper functions existed at module scope.

### Validation

bash
python -m py_compile services/auth_service/app/metrics.py

Returned no errors.

### Lessons Learned

Module-level helper functions must align with other function definitions. Indentation errors can appear as import failures.

---

## Issue

### Symptoms

Auth service continued failing after source code corrections.

### Root Cause

Modified files had not been saved prior to Docker rebuild.

### Resolution

Saved all modified files and rebuilt container.

### Validation

bash
docker compose build --no-cache auth_service
docker compose up -d auth_service

Container started successfully.

### Lessons Learned

Always save source files before rebuilding containers. Docker only copies saved filesystem contents into build con.

---

## Issue

### Symptoms

Asset service returned HTTP 500 responses during rate-limit validation.

### Root Cause

Rate-limit logging initially used an incorrect logging function signature.

### Resolution

Reworked rate-limit event generation using:

python
event_data = base_log_event(...)
event_data.update(...)
log_event(event_data)

### Validation

bash
for i in {1..120}; do
  curl <http://localhost:8001/health>
done

Produced:

100 200
20 429

### Lessons Learned

Security logging should reuse established structured logging patterns to avoid runtime exceptions.

---

## Issue

### Symptoms

Asset service failed startup with:

NameError: name 'cat' is not defined

### Root Cause

Shell heredoc commands were accidentally pasted into Python source files.

### Resolution

Removed:

bash
cat > filename <<'EOF'
...
EOF

from application source code.

### Validation

bash
python -m py_compile services/asset_service/app/*.py

Completed successfully.

### Lessons Learned

Distinguish between terminal commands and file contents when applying updates.

---

## Issue

### Symptoms

Rate-limit metric existed but appeared to have no values.

### Root Cause

Metric had been registered but no rate-limit events had occurred.

### Resolution

Generated test traffic exceeding middleware threshold.

### Validation

bash
curl -s <http://localhost:8001/metrics> | grep rate_limit_exceeded_total

Returned:

rate_limit_exceeded_total{path="/health",service="asset-service"} 20

### Lessons Learned

Prometheus counters often appear with only HELP/TYPE entries until events occur.

---

## Issue

### Symptoms

Grafana panels displayed "No Data".

### Root Cause

Associated security events had never occurred within the selected time window.

### Resolution

Generated authentication failures, invalid tokens, permission denials, and rate-limit events to populate metrics.

### Validation

Panels populated after test activity.

### Lessons Learned

"No Data" does not necessarily indicate dashboard misconfiguration; verify metric generation before troubleshooting queries.

---

## Issue

### Symptoms

Administrative telemetry required validation.

### Root Cause

New metrics had been added but not exercised.

### Resolution

Executed:

- `/admin`
- `/audit`
- `/dev/promote-admin/{email}`

with both admin and viewer accounts.

### Validation

Verified:

admin_endpoint_access_total
privilege_escalation_attempt_total
user_management_action_total
role_change_total
permission_denied_total

incremented appropriately.

### Lessons Learned

Every new metric should have a documented validation procedure before phase completion.

# Phase 5.10 Troubleshooting Notes

## Issue

### Tempo TraceQL Search Returned 400 Bad Request

### Symptoms

- Grafana Explore successfully connected to Tempo.
- Tempo datasource loaded.
- Query execution returned:

failed to execute search query
status: 400 Bad Request

- Searching with:

asset-service

failed.

### Root Cause

Tempo TraceQL requires valid TraceQL syntax.

A service name by itself is not a valid TraceQL expression.

### Resolution

Switched from TraceQL testing to Tempo Search mode.

Validated traces using:

Service Name:
asset-service

Service Name:
auth-service

Confirmed Grafana successfully retrieved traces.

### Validation

Verified:

Asset Service traces visible
Auth Service traces visible
Trace IDs visible
Span IDs visible
Tempo search operational

### Lessons Learned

Tempo connectivity can be healthy while TraceQL syntax is invalid.

Always validate datasource connectivity using Search mode before troubleshooting TraceQL expressions.

---

## Issue

### Loki Trace Correlation Query Returned No Results

### Symptoms

Queries returned:

No logs found

Examples:

logql
{container_name=~".+"}

logql
{container_name=~".*asset.*|.*auth.*"} |= "trace_id"

### Root Cause

Promtail labels did not include:

container_name

Available labels were:

container
job
service
service_name
stream

Query assumptions did not match actual Loki labels.

### Resolution

Used Grafana Label Browser to inspect available labels.

Updated investigation queries to use:

logql
{service=~".*asset.*|.*auth.*"} |= "trace_id"

and

logql
{service_name=~".*asset.*|.*auth.*"} |= "trace_id"

### Validation

Successfully retrieved:

trace_id
span_id
request.started
dependency.database.available
request.completed

events.

### Lessons Learned

Never assume Loki labels.

Always validate labels using Label Browser before building dashboards and investigation workflows.

---

## Issue

### Security Investigation Dashboard Displayed No Data

### Symptoms

All investigation dashboard panels displayed:

No data

including:

Authentication Failures
Invalid Tokens
Permission Denied Events
Privilege Escalation Attempts

### Root Cause

Metrics existed and were registered in Prometheus, but no metric samples had been generated.

Prometheus exposed:

# HELP

# TYPE

definitions only.

No counters had been incremented since container startup.

### Resolution

Generated test security events:

Authentication failures
Invalid token attempts
Permission denied events
Privilege escalation attempts

using manual API testing.

### Validation

Confirmed metric samples existed:

auth_login_failure_total
invalid_token_total
permission_denied_total
privilege_escalation_attempt_total

Grafana panels populated successfully.

### Lessons Learned

Prometheus counters do not emit labeled time series until the first increment occurs.

Dashboard validation requires event generation, not merely metric registration.

---

## Issue

### Authentication Failure Metrics Not Incrementing

### Symptoms

Failed login testing produced:

422 Unprocessable Entity

Metrics remained unchanged.

### Root Cause

Test payload used:

json
{
  "username": "...",
  "password": "..."
}

while the endpoint expected:

json
{
  "email": "...",
  "password": "..."
}

Validation failed before authentication logic executed.

### Resolution

Retested using:

json
{
  "email": "<bad-user@test.com>",
  "password": "wrong-password"
}

### Validation

Confirmed:

auth_login_failure_total{method="json_login",reason="user_not_found"} 5

### Lessons Learned

API validation failures do not execute business logic.

Always verify request schemas before testing observability metrics.

---

## Issue

### Invalid Token Dashboard Panel Returned No Data

### Symptoms

Invalid token panel displayed:

No data

despite invalid token testing.

### Root Cause

Metric had not yet been generated.

Dashboard validation occurred before invalid token events were produced.

### Resolution

Generated invalid token events using:

bash
for i in {1..5}; do
  curl -s <http://localhost:8002/me> \
    -H "Authorization: Bearer invalid.token.value"
done

### Validation

Confirmed:

invalid_token_total{reason="invalid_token",service="auth-service"} 5

### Lessons Learned

Investigation dashboards require representative event generation before validation.

---

## Issue

### Permission Denied And Privilege Escalation Panels Required Validation

### Symptoms

Dashboard panels showed:

No data

for:

Permission Denied Events
Privilege Escalation Attempts

### Root Cause

No unauthorized access attempts had occurred since service startup.

### Resolution

Authenticated using viewer account:

<viewertest@test.com>

Attempted access to:

/admin

with viewer role.

### Validation

Confirmed:

permission_denied_total{reason="insufficient_role"} 1

and

privilege_escalation_attempt_total{required_role="admin"} 1

### Lessons Learned

RBAC investigation telemetry should be validated using real authorization failures rather than synthetic metric injection.

---

## Issue

### Rate Limit Metrics Appeared Missing

### Symptoms

Query:

bash
curl -s <http://localhost:8001/metrics> | grep rate_limit_exceeded_total

returned no output.

### Root Cause

Initial validation occurred before inspecting the full metric output.

Metric existed but required con-aware inspection.

### Resolution

Generated rate limit violations:

bash
for i in {1..120}; do
  curl <http://localhost:8001/health>
done

Inspected metrics using:

bash
curl -s <http://localhost:8001/metrics> | grep -A 5 -B 2 rate_limit

### Validation

Confirmed:

rate_limit_exceeded_total{path="/health",service="asset-service"} 140

and

rate_limit_exceeded_total{path="/metrics",service="asset-service"} 2

### Lessons Learned

Metric validation should inspect full metric con rather than relying solely on simple grep output.

Rate limiting telemetry and logging are functioning correctly.

## Issue

Prometheus Alert Rules Not Loading

### Symptoms

- Prometheus started successfully
- `promtool check config` reported:

SUCCESS: 1 rule files found
SUCCESS: /etc/prometheus/prometheus.yml is valid
SUCCESS: 0 rules found

- Alert rules were expected but none appeared in Prometheus

### Root Cause

The `prometheus-alerts.yml` file existed but contained no alert definitions.

Prometheus successfully mounted and parsed the file, but the file was empty.

### Resolution

Created initial alert rule groups:

- ops-platform-availability
- ops-platform-security

Implemented alert definitions for:

- PrometheusTargetDown
- AssetServiceDown
- AuthServiceDown
- cAdvisorDown
- AuthenticationFailureSpike
- InvalidTokenSpike
- PermissionDeniedSpike
- RateLimitAbuseDetected
- PrivilegeEscalationActivity
- AssetService5xxErrors

### Validation

Validated using:

bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

Verified:

SUCCESS: 10 rules found

Prometheus Rules page displayed both alert groups and all configured alerts.

### Lessons Learned

Prometheus can successfully load an empty rule file without generating errors.

Always verify:

- Rule file existence
- Rule file contents
- Rule count reported by promtool
- Rules page visibility

## Issue

Prometheus Alert Rules Not Loading

### Symptoms

- Prometheus started successfully
- `promtool check config` reported:

SUCCESS: 1 rule files found
SUCCESS: /etc/prometheus/prometheus.yml is valid
SUCCESS: 0 rules found

- Alert rules were expected but none appeared in Prometheus

### Root Cause

The `prometheus-alerts.yml` file existed but contained no alert definitions.

Prometheus successfully mounted and parsed the file, but the file was empty.

### Resolution

Created initial alert rule groups:

- ops-platform-availability
- ops-platform-security

Implemented alert definitions for:

- PrometheusTargetDown
- AssetServiceDown
- AuthServiceDown
- cAdvisorDown
- AuthenticationFailureSpike
- InvalidTokenSpike
- PermissionDeniedSpike
- RateLimitAbuseDetected
- PrivilegeEscalationActivity
- AssetService5xxErrors

### Validation

Validated using:

bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

Verified:

SUCCESS: 10 rules found

Prometheus Rules page displayed both alert groups and all configured alerts.

### Lessons Learned

Prometheus can successfully load an empty rule file without generating errors.

Always verify:

- Rule file existence
- Rule file contents
- Rule count reported by promtool
- Rules page visibility

## Issue

Prometheus Alert Rule File Not Found Inside Container

### Symptoms

Prometheus configuration validation failed with:

"/etc/prometheus/prometheus-alerts.yml" does not point to an existing file

### Root Cause

The alert rule file existed on the host but was not mounted into the Prometheus container.

Only `prometheus.yml` was mounted.

### Resolution

Added alert rule volume mount:

yaml
volumes:

- ./infrastructure/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
- ./infrastructure/monitoring/prometheus-alerts.yml:/etc/prometheus/prometheus-alerts.yml:ro

Restarted Prometheus container.

### Validation

Validated configuration:

bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

Prometheus successfully detected the rule file.

### Lessons Learned

Adding a rule file to Prometheus requires:

- rule_files entry in prometheus.yml
- Docker volume mount
- Container restart

All three components must exist for rules to load.

## Issue

Prometheus Alert Rules Not Updating After File Modification

### Symptoms

Alert definitions were added in VS Code.

Prometheus continued reporting:

SUCCESS: 0 rules found

### Root Cause

The updated file contents had not been saved to disk.

VS Code contained unsaved changes.

Prometheus was reading the previously saved empty file.

### Resolution

Saved the file and recreated the Prometheus container.

bash
docker compose rm -sf prometheus
docker compose up -d prometheus

### Validation

Validated file contents inside the container and confirmed alert rules were loaded.

Prometheus Rules page displayed all configured alerts.

### Lessons Learned

When configuration changes appear to be ignored:

- Verify files are saved
- Verify bind mounts
- Verify container contents
- Verify rule count with promtool

## Issue

Prometheus Container Entered Restart Cycle During Rule Deployment

### Symptoms

Prometheus repeatedly restarted after configuration changes.

Validation commands became unreliable.

### Root Cause

Configuration changes were being tested while Prometheus was restarting and loading new configuration.

The container state became difficult to verify during troubleshooting.

### Resolution

Removed and recreated the Prometheus container:

bash
docker compose rm -sf prometheus
docker compose up -d prometheus

Collected startup logs after recreation.

### Validation

Confirmed:

ops-prometheus Started

Prometheus initialized normally and loaded configuration successfully.

### Lessons Learned

When troubleshooting Prometheus configuration:

- Prefer clean recreation over repeated restart attempts
- Review startup logs immediately after container creation
- Validate configuration after service stabilization

## Issue

Unexpected Long Container Uptime Appearing In Dashboard

### Symptoms

Grafana dashboard displayed a container uptime value exceeding 160,000 seconds.

Observed value appeared inconsistent with recently restarted platform services.

### Root Cause

The metric originated from Docker BuildKit / Buildx infrastructure rather than Ops Platform application containers.

Docker builder runtime metrics were included in container uptime visualizations.

### Resolution

Investigated:

bash
docker ps
docker buildx ls

Confirmed the long-running object belonged to Docker build infrastructure and not the platform stack.

No corrective action required.

### Validation

Verified all Ops Platform containers had expected uptime values.

Observed uptime values aligned with recent container restarts.

### Lessons Learned

Container metrics may include:

- Docker infrastructure containers
- BuildKit builders
- Buildx runtimes

Dashboard filtering may be required to isolate platform services from Docker internals.

## Issue

Prometheus Alert Framework Implemented Without Operational Procedures

### Symptoms

Prometheus alerts existed conceptually but no documented response process existed.

Alert recipients would have no standardized response workflow.

### Root Cause

Detection capabilities matured faster than operational documentation.

Runbooks had not yet been developed.

### Resolution

Created incident response runbooks:

- authentication-failure-spike.md
- invalid-token-spike.md
- permission-abuse.md
- privilege-escalation-activity.md
- rate-limit-abuse.md
- service-outage.md
- prometheus-target-down.md

Created:

- 16-alert-routing-review.md
- 17-alert-tuning-review.md

### Validation

Validated runbook coverage for:

- Security Operations
- Incident Response
- Platform Operations
- Observability Operations

### Lessons Learned

Observability maturity requires:

Metrics
→ Alerting
→ Detection
→ Investigation
→ Response

Alert generation without response procedures creates operational gaps.

## Issue

Prometheus Alert Rules Generated Duplicate Availability Alerts

### Symptoms

A generic target availability alert existed alongside service-specific availability alerts.

Potential duplicate alerts could occur when a monitored service became unavailable.

Examples:

- PrometheusTargetDown
- AssetServiceDown
- AuthServiceDown
- cAdvisorDown

A single outage condition could trigger multiple alerts for the same event.

### Root Cause

The generic alert:

promql
up == 0

overlapped with service-specific target alerts.

This reduced signal quality and increased alert noise.

### Resolution

Removed:

PrometheusTargetDown

Retained service-specific alerts:

- AssetServiceDown
- AuthServiceDown
- cAdvisorDown

Adjusted alert durations to reduce transient alert generation.

### Validation

Validated:

bash
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

Confirmed:

SUCCESS: 9 rules found

Alert inventory reduced from 10 rules to 9 rules.

### Lessons Learned

Alerting should be specific and actionable.

Overlapping alerts increase operational noise and contribute to alert fatigue.

## Issue

Availability Alerts Generated Excessive Noise During Short Restarts

### Symptoms

Short service restarts could trigger outage alerts.

Container recreation or Docker Compose operations could potentially produce unnecessary incidents.

### Root Cause

Availability alerts used short evaluation windows:

1 minute

which increased sensitivity to temporary interruptions.

### Resolution

Adjusted alert durations:

AssetServiceDown:
1m → 2m

AuthServiceDown:
1m → 2m

cAdvisorDown:
1m → 3m

AssetService5xxErrors:
1m → 2m

### Validation

Prometheus loaded updated rules successfully.

Alert durations reflected updated values.

### Lessons Learned

Operational alerts should tolerate short service interruptions while still detecting meaningful outages.

## Issue

Security Alert Severity Did Not Match Operational Risk

### Symptoms

Invalid token activity generated the same alert severity as more serious security conditions.

Examples:

- InvalidTokenSpike
- PermissionDeniedSpike

Both were classified as high severity.

### Root Cause

Initial severity assignments focused on implementation rather than operational impact.

Invalid token events may occur because of:

- Expired sessions
- Stale tokens
- Client-side errors
- Misconfigured integrations

### Resolution

Adjusted:

InvalidTokenSpike

High
↓
Medium

Retained:

AuthenticationFailureSpike = High

PermissionDeniedSpike = High

PrivilegeEscalationActivity = Critical

### Validation

Prometheus successfully loaded updated alert definitions.

Dashboard severity grouping reflected updated classifications.

### Lessons Learned

Alert severity should reflect operational risk rather than event existence.

## Issue

Security Response Dashboard Displayed No Data For Valid Metrics

### Symptoms

Security Response dashboard panels displayed:

No data

despite valid metrics existing in Prometheus.

Examples:

- Security Event Volume
- Authentication Failures
- Permission Denials
- Privilege Escalation Attempts
- Rate Limit Violations

### Root Cause

Queries used:

promql
sum(increase(metric_name[time]))

When a metric contained no series during the selected time range, Grafana returned no data instead of zero.

### Resolution

Updated dashboard queries to use:

promql
sum(increase(metric_name[time])) or vector(0)

Examples:

promql
sum(increase(auth_login_failure_total[1h])) or vector(0)

sum(increase(permission_denied_total[1h])) or vector(0)

sum(increase(rate_limit_exceeded_total[1h])) or vector(0)

### Validation

Dashboard panels displayed:

0

instead of:

No data

when no events existed.

### Lessons Learned

Operational dashboards should display zero activity explicitly rather than showing no data whenever possible.

## Issue

Security Event Volume Panel Failed To Render Combined Security Activity

### Symptoms

The Security Event Volume panel displayed:

No data

even when security telemetry existed.

Observed metrics included:

- invalid_token_total
- rate_limit_exceeded_total

### Root Cause

The query combined multiple metrics.

If one metric returned no series, the aggregate expression could return no data.

### Resolution

Updated the query to provide default values:

promql
(sum(increase(auth_login_failure_total[5m])) or vector(0))
+
(sum(increase(invalid_token_total[5m])) or vector(0))
+
(sum(increase(permission_denied_total[5m])) or vector(0))
+
(sum(increase(privilege_escalation_attempt_total[5m])) or vector(0))
+
(sum(increase(rate_limit_exceeded_total[5m])) or vector(0))

### Validation

Generated:

- Invalid token events
- Rate limit events

Confirmed Security Event Volume populated correctly.

### Lessons Learned

Aggregate dashboard queries should gracefully handle missing metric series.

## Issue

Security Response Dashboard Required End-To-End Validation

### Symptoms

Dashboard imported successfully but initial validation only confirmed panel rendering.

Alert-to-dashboard visibility had not yet been verified.

### Root Cause

The full operational workflow had not yet been exercised.

Components requiring validation:

- Metrics
- Alert rules
- Alert firing state
- ALERTS metric
- Dashboard visibility

### Resolution

Generated security events:

- Invalid token activity
- Rate limit violations
- Authentication failures
- Permission-denied activity

Validated dashboard response.

### Validation

Confirmed:

Active Security Alerts

Alert State By Severity

Security Event Volume

Invalid Tokens

Rate Limit Violations

Service Target Health

populated successfully.

Validated complete workflow:

Event
↓
Metric
↓
Alert
↓
Dashboard

### Lessons Learned

Dashboard validation should include full operational workflow testing rather than UI verification alone.

## Issue

Security Response Dashboard Added To Operations Dashboard Portfolio

### Symptoms

The platform supported:

- Operations monitoring
- Detection
- Investigation

but lacked a dedicated response-oriented dashboard.

### Root Cause

Security telemetry and alerting capabilities matured faster than response visualization.

### Resolution

Created:

Ops Platform - Security Response

Implemented panels for:

- Active Security Alerts
- Active Platform Alerts
- Alert State By Severity
- Security Event Volume
- Authentication Failures
- Invalid Tokens
- Permission Denials
- Privilege Escalation Attempts
- Rate Limit Violations
- Service Target Health

### Validation

Dashboard imported successfully.

Prometheus queries executed successfully.

Security telemetry populated panels.

### Lessons Learned

Effective incident response requires dedicated operational visibility separate from detection and investigation workflows.

## Issue
### Symptoms
No standardized format existed for documenting investigations, incidents, or post-incident reviews.

### Root Cause
Operational processes matured through alerting, investigation, and response phases without a formal documentation framework.

### Resolution
Created reusable incident management templates covering:

- Security Incident Reports
- Investigation Summaries
- Post-Incident Reviews

### Validation
Verified all templates include required operational sections and support metrics, logs, traces, timelines, evidence collection, remediation tracking, and lessons learned.

### Lessons Learned
Operational maturity requires standardized documentation in addition to observability and response tooling.