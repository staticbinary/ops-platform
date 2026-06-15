import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.logging_utils import base_log_event, log_event
from app.metrics import record_rate_limit_exceeded
from app.request_context import get_request_id, get_source_ip


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        source_ip = get_source_ip()

        if source_ip is None:
            source_ip = request.client.host if request.client else "unknown"

        now = time.time()
        request_times = self.requests[source_ip]
        path = request.url.path

        while request_times and request_times[0] <= now - self.window_seconds:
            request_times.popleft()

        if len(request_times) >= self.max_requests:
            request_id = get_request_id()

            record_rate_limit_exceeded(path)

            event_data = base_log_event(
                event="rate_limit.exceeded",
                severity="warning",
                category="security",
            )

            event_data.update(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "client": source_ip,
                    "status_code": 429,
                    "reason": "rate_limit_exceeded",
                }
            )

            log_event(event_data)

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "status_code": 429,
                    "request_id": request_id,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                },
            )

        request_times.append(now)

        return await call_next(request)
