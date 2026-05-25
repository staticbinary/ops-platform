## Module Import Troubleshooting

Issue:
- FastAPI container failed with:
  ModuleNotFoundError: No module named 'app.database'

Root Cause:
- database.py created in incorrect nested directory:
  services/asset_service/services/asset_service/app/

Resolution:
- moved database.py into:
  services/asset_service/app/
- removed accidental nested services directory
- rebuilt containers using:
  docker compose up -d --build

Key Lesson:
- Python module import paths depend on correct project structure alignment
- containerized application paths must match runtime import expectations

## PostgreSQL Table Verification

Validation Steps:
- entered PostgreSQL container directly using docker exec
- connected to database through psql
- validated automatic ORM table creation using:
  \dt

Result:
- confirmed assets table successfully generated through SQLAlchemy metadata initialization

Key Lesson:
- ORM models dynamically generate relational database schema structures
- direct infrastructure verification is important during backend development

## CRUD Endpoint Debugging

Issue:
- FastAPI container returned 502 Bad Gateway during CRUD implementation

Root Cause:
- malformed indentation in database.py dependency function

Validation Steps:
- inspected container logs using:
  docker compose logs asset-service

Resolution:
- corrected indentation within get_db() dependency function
- rebuilt containers using:
  docker compose up -d --build

Result:
- CRUD endpoints successfully created persistent PostgreSQL records

Key Lesson:
- container log inspection is critical for backend runtime debugging
- dependency injection lifecycle errors can prevent application startup

### Symptoms
# PUT Endpoint Returned 405 Method Not Allowed

## Symptoms

Attempting to update an asset with:

```bash
curl -X PUT http://localhost:8080/api/assets/assets/1 \
  -H "Content-Type: application/json" \
  -d '{"hostname":"t5500-lab-node","owner":"ops-team","status":"maintenance"}'

  Root Cause

PUT /assets/{asset_id} endpoint had not actually been added to:

services/asset_service/app/main.py

Additionally:

AssetUpdate import was missing
update logic was not registered in FastAPI
container rebuild succeeded, but application lacked PUT handler

FastAPI therefore recognized the route path, but not the PUT method.

Resolution

Updated:

from .schemas import AssetCreate, AssetUpdate, AssetResponse

Added:

@app.put("/assets/{asset_id}", response_model=AssetResponse)

Implemented:

database update logic
SQLAlchemy commit/refresh
proper 404 handling for unknown assets
Rebuild Procedure
docker compose up -d --build

Verified:

asset-service rebuilt successfully
containers restarted cleanly
reverse proxy remained healthy
Validation
Successful Asset Update
curl -X PUT http://localhost:8080/api/assets/assets/1 \
  -H "Content-Type: application/json" \
  -d '{"hostname":"t5500-lab-node","owner":"ops-team","status":"maintenance"}'

Returned successful updated asset response.

Confirmed:

endpoint registration
request parsing
database update behavior
API serialization

## DELETE Endpoint Returned 405 Method Not Allowed

### Symptoms

Attempting to delete an asset with:

```bash
curl -X DELETE http://localhost:8080/api/assets/assets/1

The route path existed and was reachable through the reverse proxy, but the DELETE method was not being accepted by FastAPI.

Initial Analysis

A 405 Method Not Allowed response indicated:

route path existed
reverse proxy routing was functioning
FastAPI application was reachable
HTTP method was not registered for the route

Potential causes considered:

DELETE endpoint not properly registered
indentation/placement issue in main.py
failed container reload
stale container image
invalid decorator placement
Root Cause

The DELETE endpoint was not properly registered in the running FastAPI application.

To eliminate possible indentation or placement issues, the entire:

services/asset_service/app/main.py

file was replaced with a known-good full application version containing:

GET endpoints
POST endpoint
PUT endpoint
DELETE endpoint

This ensured all route decorators existed at proper root indentation level.

Resolution

Implemented:

@app.delete("/assets/{asset_id}")

Added:

database lookup logic
SQLAlchemy delete operation
commit handling
proper 404 behavior
deletion success response

Performed full container teardown and rebuild:

docker compose down
docker compose up -d --build

This ensured:

stale containers were removed
fresh application image was rebuilt
updated routes loaded cleanly
Validation
Successful Asset Delete
curl -X DELETE http://localhost:8080/api/assets/assets/1

Returned expected response:

{"message":"Asset 1 deleted successfully"}

Confirmed:

DELETE endpoint registration
database delete behavior
SQLAlchemy commit operation
API response serialization
Deleted Asset Verification
curl http://localhost:8080/api/assets/assets/1

Returned expected response:

{"detail":"Asset not found"}

Confirmed:

asset removal persisted in database
GET endpoint correctly handled deleted object state
Unknown Asset Delete Validation
curl -X DELETE http://localhost:8080/api/assets/assets/999

Returned expected response:

{"detail":"Asset not found"}

Confirmed proper 404 behavior for nonexistent asset deletion attempts.

Lessons Learned
405 Method Not Allowed commonly indicates:
route exists
HTTP method not registered
Full-file replacement can quickly eliminate hidden indentation or decorator placement problems during early FastAPI development
docker compose down followed by rebuild helps eliminate stale container/runtime issues during endpoint troubleshooting
CRUD endpoint validation should always include:
success path
retrieval validation
failure path testing
Proper API lifecycle validation improves confidence in service reliability and operational behavior

## Swagger/OpenAPI Docs Failed Behind Reverse Proxy

### Symptoms

Opening Swagger through the gateway initially failed:

```text
http://localhost:8080/api/assets/docs

Swagger UI loaded partially, but showed:

Failed to load API definition
Fetch error
Not Found /openapi.json
Root Cause

FastAPI was generating the OpenAPI path as:

/openapi.json

but the service is exposed through the reverse proxy under:

/api/assets

So Swagger needed to know the app was running behind a path prefix.

Resolution

Updated services/asset_service/app/main.py FastAPI configuration:

app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets"
)

Also added Swagger route organization with tags:

tags=["Health"]
tags=["Assets"]
tags=["Root"]
Rebuild
docker compose up -d --build
Validation

Confirmed Swagger loads successfully at:

http://localhost:8080/api/assets/docs

Confirmed OpenAPI exposes:

GET     /health
GET     /db-health
GET     /assets
POST    /assets
GET     /assets/{asset_id}
PUT     /assets/{asset_id}
DELETE  /assets/{asset_id}
GET     /
Result

Swagger now displays clean grouped sections:

Health
Assets
Root
Schemas
Lesson Learned

When FastAPI runs behind a reverse proxy path prefix, set:

root_path="/api/assets"

so Swagger/OpenAPI generates the correct API definition path.

## Request Logging Middleware Implementation

### Objective

Add basic operational visibility to the Asset Service by logging each HTTP request and response.

---

### Implementation

Updated FastAPI import in:

```text
services/asset_service/app/main.py

Added Request:

from fastapi import Depends, FastAPI, HTTPException, Request

Added HTTP middleware:

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")

    response = await call_next(request)

    print(f"Completed response: {response.status_code}")

    return response
Issue Encountered

Base.metadata.create_all(bind=engine) was accidentally pasted near the top of the file before Base and engine were imported.

This was corrected by removing the misplaced line and keeping only the proper instance after the FastAPI app initialization.

Validation

Rebuilt containers:

docker compose up -d --build

Generated test traffic:

curl http://localhost:8080/api/assets/health

Checked service logs:

docker compose logs asset-service

Confirmed middleware output:

Incoming request: GET http://asset-service:8000/health
Completed response: 200
Result

Request logging middleware is functioning correctly.

Confirmed:

middleware registration
request interception
response interception
reverse proxy forwarding
container log visibility
Lesson Learned

FastAPI middleware provides a clean foundation for operational telemetry.

This basic logging can later evolve into:

structured logging
request IDs
correlation IDs
audit trails
observability pipelines


## Troubleshooting / Implementation Notes

```markdown
## Request ID Correlation Logging

### Objective
Improve request logging by assigning each API request a unique correlation ID.

### Implementation
Added:

```python
import uuid

Updated middleware to generate a request ID:

request_id = str(uuid.uuid4())

Added the request ID to:

incoming request logs
completed response logs
HTTP response headers

Header added:

X-Request-ID
Issue Encountered

Initial test returned:

500 Internal Server Error

Service logs showed:

NameError: name 'uuid' is not defined
Root Cause

The running container did not yet have the updated code with:

import uuid
Resolution

Confirmed import uuid existed at the top of main.py, then rebuilt containers:

docker compose up -d --build
Validation

Ran:

curl -i http://localhost:8080/api/assets/health

Confirmed:

x-request-id: <uuid>

Checked logs:

docker compose logs asset-service

Confirmed the same request ID appeared in both request and response log entries.

Result

Request correlation logging is functioning correctly.

Lesson Learned

Correlation IDs make it much easier to trace a single request across:

HTTP responses
application logs
reverse proxy flow
future multi-service communication

## Phase 4.0 Auth Foundation Setup

### Objective
Begin securing the Asset Service by adding JWT-based authentication support.

### Implemented
Updated `main.py` with:
- JWT imports
- OAuth2 password flow support
- authentication configuration
- token creation helper
- token validation helper
- `/auth/login` endpoint
- `/auth/me` protected endpoint

### File Structure Reminder
Current `main.py` order:
1. Imports
2. App configuration
3. Auth constants
4. OAuth2 scheme
5. Database initialization
6. Helper functions
7. Middleware
8. API routes

### Issue Encountered
Attempted to run:

```bash
services/asset_service/requirements.txt

This returned:

Permission denied
Root Cause

requirements.txt is a dependency list, not an executable script.

Resolution

Open/edit the file in VS Code and add dependencies there.

Next Validation

Rebuild and test:

login token generation
protected /auth/me
failed login behavior
missing token behavior

## Phase 4.0 — JWT Authentication Foundation

### Objective
Begin securing the Asset Service by implementing JWT-based authentication and protected route support.

---

### Authentication Components Added

Updated `main.py` to include:

#### JWT Imports

```python
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

returned:

502 Bad Gateway

from nginx.

Initial Analysis

A 502 Bad Gateway response indicated:

nginx reverse proxy was reachable
request forwarding occurred
upstream FastAPI application failed internally

Potential causes considered:

missing dependency
FastAPI startup failure
OAuth2 form parsing issue
broken auth import
container runtime crash
Root Cause

OAuth2PasswordRequestForm requires multipart form parsing support through:

python-multipart

This dependency was missing from:

services/asset_service/requirements.txt

Without it, FastAPI failed while processing form-based login requests.

Additional Issue Encountered

Attempted to run:

services/asset_service/requirements.txt

which returned:

Permission denied
Root Cause

requirements.txt is a dependency definition file and is not executable.

Dependencies must be edited within the file itself and installed during Docker build execution.

Resolution

Updated:

services/asset_service/requirements.txt

Added:

python-jose[cryptography]
python-multipart

Rebuilt containers:

docker compose up -d --build

Confirmed:

dependency installation completed
asset-service started successfully
nginx reverse proxy reconnected to upstream service
Validation
Successful Login Validation
curl -X POST http://localhost:8080/api/assets/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"

Confirmed:

200 OK
JWT access token returned
bearer token response structure valid
Protected Route Validation
curl http://localhost:8080/api/assets/auth/me \
  -H "Authorization: Bearer <token>"

Confirmed:

authenticated request succeeded
token validation worked correctly
authenticated username returned
Unauthorized Access Validation
curl http://localhost:8080/api/assets/auth/me

Returned expected response:

{"detail":"Not authenticated"}

Confirmed protected route enforcement works correctly.

Result

JWT authentication is functioning correctly with:

OAuth2 password flow
JWT token issuance
protected route validation
bearer token authentication
unauthorized request rejection
Lessons Learned
FastAPI OAuth2 form handling requires python-multipart
502 Bad Gateway commonly indicates upstream application failure
Dependency issues inside containers often surface as proxy failures
Authentication validation should always include:
successful login
token validation
unauthorized access checks
dependency verification

## Phase 4.1 Auth Service Troubleshooting

### Issue: Auth service not reachable after adding OAuth2 token endpoint

**Symptom**

`localhost:8001/docs` refused to connect after rebuilding the auth service.

**Cause**

The `/token` endpoint used `OAuth2PasswordRequestForm`, which requires the `python-multipart` package. Without it, FastAPI fails during startup.

**Fix**

Added `python-multipart` to:

```txt
services/auth_service/requirements.txt

---

## Phase 4.1B Audit Logging & RBAC Troubleshooting

### Issue: Audit endpoint returned `401 Not authenticated`

**Symptom**

Authenticated user attempting to access:

```txt
GET /audit

received:

{
  "detail": "Not authenticated"
}

Cause

Swagger authorization state had expired or bearer auth had not been re-applied after rebuilding/restarting services.

Fix

Re-authorized using Swagger OAuth2 flow:

Click Authorize
Authenticate via /token
Retry protected endpoint
Issue: Audit endpoint returned 403 Insufficient permissions

Symptom

Authenticated user attempting to access:

GET /audit

received:

{
  "detail": "Insufficient permissions"
}

Cause

The authenticated JWT contained:

{
  "role": "viewer"
}

while /audit required:

auth.require_role("admin")

Fix

Created temporary development-only admin promotion endpoint:

POST /dev/promote-admin/{email}

Then re-authenticated to generate a new JWT containing:

{
  "role": "admin"
}
Issue: Auth users disappeared after rebuilds

Symptom

Previously registered users no longer existed after rebuilding the auth service.

User IDs restarted from:

id = 1

indicating a fresh database.

Cause

Auth service currently uses local SQLite storage:

sqlite:///./auth.db

The SQLite database exists only inside the container filesystem and is not attached to a persistent Docker volume.

Container recreation wipes:

users
roles
audit logs

Future Fix Options

Short-term

Add Docker volume persistence for SQLite.

Long-term (preferred)

Migrate auth service to PostgreSQL like the asset service.

Confirmed Working Audit Capabilities

The following audit events were verified:

Successful login events
Failed login events
OAuth2 token issuance events
Role promotion events
Admin-only audit access
RBAC enforcement on audit endpoints

Audit log entries currently include:

event type
user email
success/failure outcome
event detail

---

## Phase 4.2 Auth Persistence & Audit Timestamp Troubleshooting

### Issue: Docker command not found in WSL

**Symptom**

Running:

```bash
docker compose up -d --build

returned:

The command 'docker' could not be found in this WSL 2 distro.

Cause

Docker Desktop was not running, so the Docker CLI was unavailable inside WSL.

Fix

Started Docker Desktop. When Docker appeared stuck starting the engine, Docker-related processes were killed and Docker Desktop was restarted. After restart, Docker engine loaded normally and WSL access resumed.

Issue: Docker Compose volume validation failed

Symptom

Running Docker Compose returned:

validating docker-compose.yml:
volumes.postgres-data Additional property auth-data is not allowed

Cause

The auth-data volume was accidentally nested under postgres-data instead of being defined as a separate top-level volume.

Incorrect:

volumes:
  postgres-data:
    auth-data:

Correct:

volumes:
  postgres-data:
  auth-data:

Fix

Corrected the bottom-level volumes: section so both Docker volumes are aligned at the same indentation level.

Issue: Auth users disappeared after rebuilds

Symptom

Previously registered users were lost after rebuilding/recreating the auth service. New registrations restarted at:

id = 1

Cause

The auth service originally stored SQLite data at:

sqlite:///./auth.db

inside the container filesystem. Container recreation wiped the local SQLite database.

Fix

Moved auth SQLite storage to a mounted Docker volume.

Updated auth database path:

DATABASE_URL = "sqlite:///./data/auth.db"

Updated auth-service in docker-compose.yml:

auth-service:
  volumes:
    - auth-data:/app/data

Added top-level Docker volume:

volumes:
  postgres-data:
  auth-data:

Validation

After rebuilding, attempting to register the same user returned:

{
  "detail": "Email already registered"
}

confirming auth persistence was working.

Issue: Login returned 500 after adding audit timestamp column

Symptom

After adding created_at to the AuditLog model, login returned:

500 Internal Server Error

Cause

The existing persistent SQLite database had already created the audit_logs table before the created_at column existed.

Base.metadata.create_all() creates missing tables but does not modify existing table schemas.

Fix

Reset the development auth volume once so SQLite could recreate the table with the new column:

docker compose down
docker volume rm ops-platform_auth-data
docker compose up -d --build

Future Fix

Use Alembic migrations for schema changes instead of resetting development volumes.

Issue: Audit endpoint returned 403 after user promotion

Symptom

After promoting a user to admin, /audit still returned:

{
  "detail": "Insufficient permissions"
}

Cause

The existing JWT was issued before the role change and still contained:

{
  "role": "viewer"
}

Fix

Logged out of Swagger authorization and re-authenticated after promotion so the new JWT contained:

{
  "role": "admin"
}
Confirmed Working After Fixes

The following were verified:

Auth SQLite data persists across rebuilds
Registered users survive container recreation
Roles persist across rebuilds
Audit logs persist across rebuilds
Audit events include created_at timestamps
Admin-only /audit endpoint works after re-authentication
JWT role claims correctly reflect role state at token issuance time