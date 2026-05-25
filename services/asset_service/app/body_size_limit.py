from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.request_context import get_request_id


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_body_size_bytes: int = 1_048_576,
    ):
        super().__init__(app)
        self.max_body_size_bytes = max_body_size_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if content_length is not None:
            try:
                body_size = int(content_length)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid Content-Length header",
                        "status_code": 400,
                        "request_id": get_request_id(),
                    },
                )

            if body_size > self.max_body_size_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Request body too large",
                        "status_code": 413,
                        "request_id": get_request_id(),
                    },
                )

        return await call_next(request)