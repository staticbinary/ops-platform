## Current Compose Services

### reverse-proxy
Purpose:
- centralized ingress routing
- reverse proxy layer
- external traffic entrypoint

### asset-service
Purpose:
- FastAPI backend service
- internal API processing
- future CRUD/data management

### postgres
Purpose:
- relational database persistence
- stateful infrastructure layer
- backend data storage

---

## Docker Volumes

### postgres-data

Purpose:
- persistent PostgreSQL storage
- survive container recreation/removal

Mapped path:
```text
/var/lib/postgresql/data