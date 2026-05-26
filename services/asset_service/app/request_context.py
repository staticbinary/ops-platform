import time
import uuid
from contextvars import ContextVar
from app.metrics import record_request_metric

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_utils import (
    build_request_completed_log,
    build_request_failed_log,
    build_request_started_log,
    log_event,
)


request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)

source_ip_context: ContextVar[str | None] = ContextVar(
    "source_ip",
    default=None,
)


def get_request_id() -> str | None:
    return request_id_context.get()


def get_source_ip() -> str | None:
    return source_ip_context.get()


def get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    return request.client.host if request.client else None


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request_id_context.set(request_id)

        method = request.method
        path = request.url.path
        client = get_client_ip(request)
        source_ip_context.set(client)

        start_time = time.perf_counter()

        log_event(
            build_request_started_log(
                request_id=request_id,
                method=method,
                path=path,
                client=client,
            )
        )

        try:
            response = await call_next(request)

            duration_seconds = time.perf_counter() - start_time
            duration_ms = round(duration_seconds * 1000, 2)

            record_request_metric(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_seconds=duration_seconds,
            )

            log_event(
                build_request_completed_log(
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )
            )

            response.headers["x-request-id"] = request_id

            return response

        except Exception as exc:
            duration_seconds = time.perf_counter() - start_time
            duration_ms = round(duration_seconds * 1000, 2)

            record_request_metric(
                method=method,
                path=path,
                status_code=500,
                duration_seconds=duration_seconds,
            )

            log_event(
                build_request_failed_log(
                    request_id=request_id,
                    method=method,
                    path=path,
                    duration_ms=duration_ms,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
            )

            raise