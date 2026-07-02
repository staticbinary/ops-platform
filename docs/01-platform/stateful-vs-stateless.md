# Stateful vs Stateless Architecture

## Stateless Services

Stateless services do not permanently retain application data internally.

Current example:
- asset-service

Characteristics:
- easy to restart
- horizontally scalable
- no persistent local data
- simpler operational lifecycle

---

## Stateful Services

Stateful services retain persistent application or infrastructure data.

Current example:
- PostgreSQL

Characteristics:
- persistent storage required
- data durability important
- backup/recovery considerations
- more complex operational lifecycle

---

## Current Platform Model

Client
    ↓
NGINX reverse proxy
    ↓
stateless API service
    ↓
stateful PostgreSQL database
    ↓
persistent Docker volume