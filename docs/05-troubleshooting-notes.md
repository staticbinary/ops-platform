# Operations Platform — Troubleshooting & Implementation Notes

---

## Module Import Troubleshooting

### Symptoms

Asset service failed during startup with:

```text
ModuleNotFoundError: No module named 'app.database'
```

### Root Cause

`database.py` was accidentally created inside:

```text
services/asset_service/services/asset_service/app/
```

instead of:

```text
services/asset_service/app/
```

### Resolution

Moved `database.py` into the correct application package:

```text
services/asset_service/app/
```

Removed the accidental nested `services` directory and rebuilt containers:

```bash
docker compose up -d --build
```

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

```bash
docker exec -it ops-postgres sh
```

Connected using:

```bash
psql -U postgres
```

Verified generated tables:

```sql
\dt
```

### Result

Confirmed SQLAlchemy successfully generated the `assets` table using:

```python
Base.metadata.create_all(bind=engine)
```

### Lessons Learned

Direct infrastructure validation is important during backend development to verify ORM behavior and persistence.

---

## CRUD Endpoint Startup Failure

### Symptoms

CRUD implementation caused:

```text
502 Bad Gateway
```

through nginx.

### Root Cause

Malformed indentation inside the `get_db()` dependency function prevented FastAPI from starting.

### Resolution

Reviewed logs:

```bash
docker compose logs asset-service
```

Corrected dependency indentation and rebuilt containers:

```bash
docker compose up -d --build
```

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

```text
405 Method Not Allowed
```

### Root Cause

`PUT /assets/{asset_id}` had not actually been implemented in `main.py`.

Missing components included:
- `AssetUpdate` schema import
- update route registration
- SQLAlchemy update logic

### Resolution

Added:

```python
@app.put("/assets/{asset_id}", response_model=AssetResponse)
```

Implemented:
- database lookup logic
- SQLAlchemy update handling
- commit/refresh logic
- 404 handling

Rebuilt containers:

```bash
docker compose up -d --build
```

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

```text
405 Method Not Allowed
```

### Root Cause

The DELETE route was not properly registered in the running FastAPI application.

### Resolution

Replaced the full `main.py` file with a verified application version containing:
- GET routes
- POST route
- PUT route
- DELETE route

Implemented:

```python
@app.delete("/assets/{asset_id}")
```

Added:
- database lookup logic
- delete handling
- commit operations
- proper 404 responses

Performed a full rebuild:

```bash
docker compose down
docker compose up -d --build
```

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

```text
Failed to load API definition
/openapi.json not found
```

### Root Cause

FastAPI generated OpenAPI paths relative to `/` while the service operated behind:

```text
/api/assets
```

through the reverse proxy.

### Resolution

Updated FastAPI initialization:

```python
app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets"
)
```

Also organized Swagger sections using route tags.

### Validation

Confirmed Swagger loads correctly at:

```text
http://localhost:8080/api/assets/docs
```

### Lessons Learned

When running FastAPI behind a reverse proxy path prefix, `root_path` must be configured correctly for Swagger/OpenAPI generation.

---

## Request Logging Middleware

### Objective

Add operational visibility for incoming requests and responses.

### Implementation

Added FastAPI middleware:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
```

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

```python
import uuid
```

Middleware now:
- generates unique request IDs
- logs request IDs
- adds `X-Request-ID` response headers

### Issue Encountered

Initial requests returned:

```text
500 Internal Server Error
```

### Root Cause

Container rebuild had not yet included:

```python
import uuid
```

### Resolution

Confirmed imports and rebuilt containers:

```bash
docker compose up -d --build
```

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

```text
502 Bad Gateway
```

### Root Cause

`OAuth2PasswordRequestForm` requires:

```text
python-multipart
```

which was missing from `requirements.txt`.

### Resolution

Updated dependencies:

```text
python-jose[cryptography]
python-multipart
```

Rebuilt containers:

```bash
docker compose up -d --build
```

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

```bash
services/asset_service/requirements.txt
```

returned:

```text
Permission denied
```

### Root Cause

`requirements.txt` is a dependency definition file, not an executable script.

### Resolution

Edited dependencies directly inside the file and rebuilt containers.

### Lessons Learned

Python dependencies are installed during Docker image build execution, not by directly running `requirements.txt`.

---

## Auth Service Failed After OAuth2 Integration

### Symptoms

```text
localhost:8001/docs
```

refused connections after rebuild.

### Root Cause

`python-multipart` was also missing from the auth-service dependency list.

### Resolution

Added:

```text
python-multipart
```

to:

```text
services/auth_service/requirements.txt
```

Rebuilt services successfully.

---

## Audit Endpoint Returned 401 Not Authenticated

### Symptoms

Authenticated users received:

```json
{
  "detail": "Not authenticated"
}
```

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

```json
{
  "detail": "Insufficient permissions"
}
```

### Root Cause

JWT tokens contained:

```json
{
  "role": "viewer"
}
```

while endpoints required:

```python
auth.require_role("admin")
```

### Resolution

Added temporary admin promotion endpoint:

```text
POST /dev/promote-admin/{email}
```

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

```yaml
auth-service:
  volumes:
    - auth-data:/app/data
```

Updated SQLite path:

```python
DATABASE_URL = "sqlite:///./data/auth.db"
```

### Validation

Confirmed:
- users persist across rebuilds
- roles persist across rebuilds
- audit logs persist across rebuilds

---

## Docker Not Found Inside WSL

### Symptoms

Running Docker commands inside WSL returned:

```text
docker: command not found
```

### Root Cause

Docker Desktop engine was not running.

### Resolution

Restarted Docker Desktop and confirmed WSL integration resumed normally.

---

## Docker Compose Volume Validation Failed

### Symptoms

Docker Compose returned:

```text
Additional property auth-data is not allowed
```

### Root Cause

`auth-data` volume was incorrectly nested under `postgres-data`.

### Resolution

Corrected top-level volume alignment:

```yaml
volumes:
  postgres-data:
  auth-data:
```

---

## Audit Timestamp Migration Failure

### Symptoms

Adding `created_at` to the audit model caused login requests to return:

```text
500 Internal Server Error
```

### Root Cause

Persistent SQLite tables already existed without the new column.

`Base.metadata.create_all()` does not alter existing schemas.

### Resolution

Reset development volume:

```bash
docker compose down
docker volume rm ops-platform_auth-data
docker compose up -d --build
```

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

```yaml
asset-service:
  ports:
    - "8000:8000"
```

Validated using:

```bash
docker compose ps
docker compose config
```

---

## Asset Service ImportError After Adding Auth Module

### Symptoms

Asset service failed with:

```text
ImportError: cannot import name 'auth' from 'app'
```

### Root Cause

`auth.py` existed outside the FastAPI app package.

### Resolution

Moved:

```text
services/asset_service/auth.py
```

into:

```text
services/asset_service/app/auth.py
```

---

## Swagger OAuth Flow Failed Across Services

### Symptoms

Swagger authorization failed with:

```text
TypeError: Failed to fetch
```

### Root Cause

Cross-origin OAuth requests between:
- asset-service Swagger
- auth-service token endpoint

caused browser/CORS failures.

### Resolution

Switched asset-service authentication from OAuth2 password flow to direct Bearer token validation using:

```python
HTTPBearer
HTTPAuthorizationCredentials
```

### Result

Users now:
- authenticate through auth-service
- copy JWT tokens
- authorize asset-service Swagger manually

---

## Asset Service Failed After HTTPBearer Migration

### Root Cause

Legacy references to:

```python
oauth2_scheme
```

remained after switching to `HTTPBearer`.

### Resolution

Replaced the auth module with a clean bearer-token validation implementation.

---

## Asset Creation Returned 500 Internal Server Error

### Symptoms

Admin POST requests returned:

```text
500 Internal Server Error
```

### Root Cause

Swagger default payload reused duplicate unique hostname values:

```json
{
  "hostname": "string"
}
```

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

```yaml
ports:
  - "5432:5432"
```

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

```text
unknown
```

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

```bash
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
  - `request_context.py`
  - `logging_utils.py`
- request context utilities were imported directly into logging helpers
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
- request context propagation stable under failures

#### Docker & Infrastructure Stability
- containers recovered successfully after rebuilds
- reverse proxy remained stable
- PostgreSQL remained healthy across restart cycles
- FastAPI startup sequence validated successfully

### Lessons Learned

- Middleware-driven observability is cleaner than route-level instrumentation
- `ContextVar` provides reliable async-safe request context propagation
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
- logging utilities imported request context directly, creating circular dependencies
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
- request context persists correctly
- reverse proxy routing remains stable
- structured logging survives rebuilds and failures

### Lessons Learned

- Middleware-based observability is significantly cleaner than route-level logging
- `ContextVar` provides reliable async-safe request context propagation in FastAPI
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
```python
db.rollback()

```md
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
```python
limit
offset

```md
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
```python
with engine.connect()

## Issue
### Symptoms
Swagger UI failed to load correctly behind the nginx reverse proxy. `/docs` attempted to retrieve `/openapi.json` from an invalid location, causing broken API documentation rendering.

### Root Cause
FastAPI `root_path` and `openapi_url` settings conflicted with nginx reverse proxy path handling.

### Resolution
Updated FastAPI configuration to properly support reverse proxy routing:

```python
root_path="/api/assets"
docs_url="/docs"
openapi_url="/openapi.json"
```

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

```python
allowed_hosts=["*"]
```

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

```text
400 Invalid host header
```

### Root Cause
nginx forwarded host headers differently than initially expected, causing TrustedHostMiddleware validation mismatches.

### Resolution
Temporarily relaxed trusted host enforcement using:

```python
allowed_hosts=["*"]
```

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
