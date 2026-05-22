# Architecture Overview

## Current Platform Flow

Client Request
    ↓
NGINX Reverse Proxy (localhost:8080)
    ↓
Docker Internal Network
    ↓
asset-service container
    ↓
FastAPI application
    ↓
/health endpoint

---

## Current Stack

- Ubuntu WSL2
- Docker Compose
- FastAPI
- Uvicorn
- NGINX
- Docker Networking

---

## Current Services

### asset-service

Purpose:
- foundational internal API service
- health endpoint validation
- future asset/device management functionality

Endpoints:
- GET /health
- GET /

---

## Reverse Proxy Routing

NGINX handles ingress traffic on:

http://localhost:8080

Current route mappings:

/api/assets/*
    ↓
asset-service:8000

---

## Docker Networking

Services communicate through:

ops-platform-network

Internal service discovery uses Docker DNS:

http://asset-service:8000

## Current Operational Flow

Development Workflow:
- VS Code connected through WSL Ubuntu
- Docker Compose orchestrates platform services
- NGINX acts as centralized ingress/reverse proxy
- asset-service runs as a containerized FastAPI application

Traffic Flow:
Client
    ↓
localhost:8080
    ↓
NGINX reverse proxy
    ↓
asset-service container
    ↓
FastAPI endpoint

Current Characteristics:
- stateless service architecture
- Docker bridge networking
- environment-variable-driven configuration
- local development environment