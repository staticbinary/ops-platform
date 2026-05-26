from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


REQUEST_COUNT = Counter(
    "asset_service_http_requests_total",
    "Total HTTP requests handled by asset service",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "asset_service_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)


def record_request_metric(
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
):
    REQUEST_COUNT.labels(
        method=method,
        path=path,
        status_code=str(status_code),
    ).inc()

    REQUEST_LATENCY.labels(
        method=method,
        path=path,
    ).observe(duration_seconds)


def metrics_response():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )