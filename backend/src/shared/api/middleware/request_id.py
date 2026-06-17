import contextvars
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Context variable to store request ID for logging correlation
REQUEST_ID_CTX_KEY = "request_id"
request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(REQUEST_ID_CTX_KEY, default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # noqa: PLR6301
        # Retrieve incoming request ID or generate a new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set the contextvar for the duration of this request task
        token = request_id_ctx_var.set(request_id)
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        finally:
            # Clean up contextvar
            request_id_ctx_var.reset(token)

        # Set X-Request-ID in response headers
        response.headers["X-Request-ID"] = request_id
        return response
