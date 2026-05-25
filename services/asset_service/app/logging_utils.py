import json
from datetime import datetime, timezone

SERVICE_NAME = "asset-service"
ENVIRONMENT = "development"


def log_event(event_data: dict):
    print(json.dumps(event_data))


def base_log_event(
    event: str,
    severity: str = "info",
):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "severity": severity,
        "event": event,
    }


def build_request_started_log(
    request_id: str,
    method: str,
    path: str,
    client: str | None
):
    event = base_log_event("request.started", "info")
    event.update({
        "request_id": request_id,
        "method": method,
        "path": path,
        "client": client,
    })
    return event


def build_request_completed_log(
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float
):
    severity = "info"

    if status_code >= 500:
        severity = "error"
    elif status_code >= 400:
        severity = "warning"

    event = base_log_event("request.completed", severity)
    event.update({
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    })
    return event


def build_request_failed_log(
    request_id: str,
    method: str,
    path: str,
    duration_ms: float,
    error_type: str,
    error_message: str,
    stack_trace: str,
):
    event = base_log_event("request.failed", "error")
    event.update({
        "request_id": request_id,
        "method": method,
        "path": path,
        "duration_ms": duration_ms,
        "error_type": error_type,
        "error_message": error_message,
        "stack_trace": stack_trace,
    })
    return event

def build_auth_failure_log(
    request_id: str | None,
    actor: str | None,
    role: str | None,
    source_ip: str | None,
    reason: str,
    permission: str | None = None,
):
    event = base_log_event("auth.failure", "warning")
    event.update({
        "request_id": request_id,
        "actor": actor or "unknown",
        "role": role or "unknown",
        "source_ip": source_ip,
        "reason": reason,
        "permission": permission,
    })
    return event


def build_auth_success_log(
    request_id: str | None,
    actor: str | None,
    role: str | None,
    source_ip: str | None,
):
    event = base_log_event("auth.success", "info")
    event.update({
        "request_id": request_id,
        "actor": actor or "unknown",
        "role": role or "unknown",
        "source_ip": source_ip,
    })
    return event


def build_permission_denied_log(
    request_id: str | None,
    actor: str | None,
    role: str | None,
    source_ip: str | None,
    permission: str,
):
    event = base_log_event("permission.denied", "warning")
    event.update({
        "request_id": request_id,
        "actor": actor or "unknown",
        "role": role or "unknown",
        "source_ip": source_ip,
        "permission": permission,
        "reason": "missing_permission",
    })
    return event