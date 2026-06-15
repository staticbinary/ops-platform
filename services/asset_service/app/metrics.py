from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


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

RATE_LIMIT_EXCEEDED_TOTAL = Counter(
    "rate_limit_exceeded_total",
    "Total rate limit violations",
    ["service", "path"],
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
        service="asset-service",
        method=method,
        handler=path,
        status=status,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        service="asset-service",
        method=method,
        handler=path,
    ).observe(duration_seconds)


def record_rate_limit_exceeded(path: str):
    RATE_LIMIT_EXCEEDED_TOTAL.labels(
        service="asset-service",
        path=path,
    ).inc()


def metrics_response():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
