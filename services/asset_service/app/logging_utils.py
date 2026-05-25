import json
from datetime import datetime, timezone


def log_event(event_data: dict):
    print(json.dumps(event_data))


def build_request_started_log(
    request_id: str,
    method: str,
    path: str,
    client: str | None
):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "request.started",
        "request_id": request_id,
        "method": method,
        "path": path,
        "client": client
    }


def build_request_completed_log(
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float
):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "request.completed",
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms
    }