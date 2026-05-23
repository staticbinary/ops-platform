# API Endpoints

## asset-service

Base Route:
- /api/assets

---

## Health Endpoints

GET /health
Purpose:
- validate service availability

GET /db-health
Purpose:
- validate PostgreSQL connectivity

---

## Asset CRUD Endpoints

POST /assets
Purpose:
- create persistent asset records

Example payload:

{
  "hostname": "t5500-lab-node",
  "owner": "ops",
  "status": "online"
}

GET /assets
Purpose:
- retrieve all asset records