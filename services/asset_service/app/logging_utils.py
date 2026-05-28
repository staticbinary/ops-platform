import json
from datetime import datetime, timezone

from opentelemetry import trace

from app.log_redaction import redact_log_data


SERVICE_NAME = "asset-service"
ENVIRONMENT = "development"

VALID_LOG_CATEGORIES = {
    "infrastructure",
    "database",
    "application",
    "security",
    "authentication",
    "authorization",
    "validation",
    "rate_limit",
    "audit",
    "observability",
}

VALID_LOG_SEVERITIES = {
    "debug",
    "info",
    "warning",
    "error",
    "critical",
}


def get_trace_context():
    current_span = trace.get_current_span()
    span_context = current_span.get_span_context()

    if not span_context.is_valid:
        return {
            "trace_id": None,
            "span_id": None,
        }

    return {
        "trace_id": format(span_context.trace_id, "032x"),
        "span_id": format(span_context.span_id, "016x"),
    }


def log_event(event_data: dict):
    safe_event_data = redact_log_data(event_data)
    print(json.dumps(safe_event_data))


def base_log_event(
    event: str,
    severity: str = "info",
    category: str = "application",
):
    if severity not in VALID_LOG_SEVERITIES:
        severity = "error"

    if category not in VALID_LOG_CATEGORIES:
        category = "application"

    trace_context = get_trace_context()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "severity": severity,
        "category": category,
        "event": event,
        "trace_id": trace_context["trace_id"],
        "span_id": trace_context["span_id"],
    }


def build_request_started_log(
    request_id: str,
    method: str,
    path: str,
    client: str | None,
):
    event = base_log_event(
        "request.started",
        severity="info",
        category="application",
    )
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
    duration_ms: float,
):
    severity = "info"
    category = "application"

    if status_code == 401:
        severity = "warning"
        category = "authentication"
    elif status_code == 403:
        severity = "warning"
        category = "authorization"
    elif status_code == 422:
        severity = "warning"
        category = "validation"
    elif status_code == 429:
        severity = "warning"
        category = "rate_limit"
    elif status_code >= 500:
        severity = "error"
        category = "application"
    elif status_code >= 400:
        severity = "warning"
        category = "application"

    event = base_log_event(
        "request.completed",
        severity=severity,
        category=category,
    )
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
):
    event = base_log_event(
        "request.failed",
        severity="error",
        category="application",
    )
    event.update({
        "request_id": request_id,
        "method": method,
        "path": path,
        "duration_ms": duration_ms,
        "error_type": error_type,
        "error_message": error_message,
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
    event = base_log_event(
        "auth.failure",
        severity="warning",
        category="authentication",
    )
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
    event = base_log_event(
        "auth.success",
        severity="info",
        category="authentication",
    )
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
    event = base_log_event(
        "permission.denied",
        severity="warning",
        category="authorization",
    )
    event.update({
        "request_id": request_id,
        "actor": actor or "unknown",
        "role": role or "unknown",
        "source_ip": source_ip,
        "permission": permission,
        "reason": "missing_permission",
    })
    return event


def build_dependency_health_log(
    dependency: str,
    status: str,
    severity: str,
    category: str = "infrastructure",
    error_type: str | None = None,
    error_message: str | None = None,
):
    event = base_log_event(
        f"dependency.{dependency}.{status}",
        severity=severity,
        category=category,
    )
    event.update({
        "dependency": dependency,
        "dependency_status": status,
    })

    if error_type:
        event["error_type"] = error_type

    if error_message:
        event["error_message"] = error_message

    return event