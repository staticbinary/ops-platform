# Auth Architecture

## Phase 4.1 Goal

Move the platform from basic authentication to enterprise-style identity and access control.

## Core Concepts

### Users
Human accounts that authenticate into the platform.

### Roles
Named permission groups assigned to users.

Initial roles:

- `admin`
- `engineer`
- `viewer`

### Permissions
Specific actions a role is allowed to perform.

Examples:

- `users:read`
- `users:write`
- `devices:read`
- `devices:write`
- `audit:read`
- `admin:access`

## Access Model

Users receive one role.

Routes and API endpoints check the user role before allowing access.

## Initial Role Design

### Admin
Full platform access.

### Engineer
Operational access to devices, alerts, and troubleshooting data.

### Viewer
Read-only access.

## Phase 4.1 Scope

- Add role field to users
- Add backend authorization checks
- Add protected frontend routes
- Add audit logging for login and security events