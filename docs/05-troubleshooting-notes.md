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