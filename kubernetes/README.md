# Ops Platform Kubernetes Deployment

This directory contains the Kubernetes deployment configuration for the Ops Platform.

## Structure

- `base/` contains reusable Kubernetes resources.
- `environments/local/` contains Docker Desktop-specific configuration.

## Initial Migration Scope

The first Kubernetes deployment includes:

- PostgreSQL
- Auth Service
- Asset Service
- Traefik Ingress Controller

The existing Docker Compose NGINX reverse proxy will not be migrated.

## Health Contract

Application workloads expose:

- `/health/live`
- `/health/ready`
- `/health/startup`
