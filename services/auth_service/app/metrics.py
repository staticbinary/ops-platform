from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


SERVICE_NAME = "auth-service"


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the service",
    ["service", "method", "handler", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["service", "method", "handler"],
)

AUTH_LOGIN_SUCCESS_TOTAL = Counter(
    "auth_login_success_total",
    "Total successful authentication attempts",
    ["service", "method"],
)

AUTH_LOGIN_FAILURE_TOTAL = Counter(
    "auth_login_failure_total",
    "Total failed authentication attempts",
    ["service", "method", "reason"],
)

ROLE_CHANGE_TOTAL = Counter(
    "role_change_total",
    "Total role change events",
    ["service", "outcome"],
)

INVALID_TOKEN_TOTAL = Counter(
    "invalid_token_total",
    "Total invalid JWT token events",
    ["service", "reason"],
)

EXPIRED_TOKEN_TOTAL = Counter(
    "expired_token_total",
    "Total expired JWT token events",
    ["service", "reason"],
)

PERMISSION_DENIED_TOTAL = Counter(
    "permission_denied_total",
    "Total permission denied events",
    ["service", "reason", "required_role"],
)

ADMIN_ENDPOINT_ACCESS_TOTAL = Counter(
    "admin_endpoint_access_total",
    "Total administrative endpoint access events",
    ["service", "endpoint"],
)

PRIVILEGE_ESCALATION_ATTEMPT_TOTAL = Counter(
    "privilege_escalation_attempt_total",
    "Total privilege escalation attempt events",
    ["service", "required_role"],
)

USER_MANAGEMENT_ACTION_TOTAL = Counter(
    "user_management_action_total",
    "Total user management action events",
    ["service", "action", "outcome"],
)

def normalize_status_code(status_code: int) -> str:
    if 200 <= status_code < 300:
        return "2xx"
    if 300 <= status_code < 400:
        return "3xx"
    if 400 <= status_code < 500:
        return "4xx"
    if 500 <= status_code < 600:
        return "5xx"

    return "unknown"

def record_request_metric(
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
):
    status = normalize_status_code(status_code)

    HTTP_REQUESTS_TOTAL.labels(
        service=SERVICE_NAME,
        method=method,
        handler=path,
        status=status,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        service=SERVICE_NAME,
        method=method,
        handler=path,
    ).observe(duration_seconds)

def record_login_success(method: str):
    AUTH_LOGIN_SUCCESS_TOTAL.labels(
        service=SERVICE_NAME,
        method=method,
    ).inc()

def record_login_failure(method: str, reason: str):
    AUTH_LOGIN_FAILURE_TOTAL.labels(
        service=SERVICE_NAME,
        method=method,
        reason=reason,
    ).inc()

def record_role_change(outcome: str):
    ROLE_CHANGE_TOTAL.labels(
        service=SERVICE_NAME,
        outcome=outcome,
    ).inc()

def record_invalid_token(reason: str):
    INVALID_TOKEN_TOTAL.labels(
        service=SERVICE_NAME,
        reason=reason,
    ).inc()

def record_expired_token(reason: str):
    EXPIRED_TOKEN_TOTAL.labels(
        service=SERVICE_NAME,
        reason=reason,
    ).inc()

def record_permission_denied(reason: str, required_role: str):
    PERMISSION_DENIED_TOTAL.labels(
        service=SERVICE_NAME,
        reason=reason,
        required_role=required_role,
    ).inc()

def record_admin_endpoint_access(endpoint: str):
    ADMIN_ENDPOINT_ACCESS_TOTAL.labels(
        service=SERVICE_NAME,
        endpoint=endpoint,
    ).inc()

def record_privilege_escalation_attempt(required_role: str):
    PRIVILEGE_ESCALATION_ATTEMPT_TOTAL.labels(
        service=SERVICE_NAME,
        required_role=required_role,
    ).inc()

def record_user_management_action(action: str, outcome: str):
    USER_MANAGEMENT_ACTION_TOTAL.labels(
        service=SERVICE_NAME,
        action=action,
        outcome=outcome,
    ).inc()

def metrics_response():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )