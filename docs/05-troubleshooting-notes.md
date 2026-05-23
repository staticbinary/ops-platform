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