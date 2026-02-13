import time
import uuid
# Optional was removed because it is not used in this module.
from typing import Dict, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Ensures every request has a request_id.

    - If client provides X-Request-Id, we respect it (useful for upstream tracing).
    - Otherwise, we generate a UUID.
    - We always return it in the response header.
    """
    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get("X-Request-Id", "").strip()
        request_id = incoming if incoming else str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds baseline security headers.

    These help reduce common web risks. Even for APIs, it signals security maturity.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # If you later serve over HTTPS only (you will with Nginx),
        # this header enforces HTTPS in browsers.
        # Safe to keep now; browsers ignore it on plain HTTP.
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Very small, in-memory rate limiter (v1).

    - Keyed by X-API-Key (or 'anonymous' if missing).
    - Uses a rolling window.
    - Suitable for demo/portfolio; replace with Redis in production.
    """
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds

        # key -> (window_start_epoch, count)
        self._state: Dict[str, Tuple[float, int]] = {}

    def _identity_key(self, request: Request) -> str:
        key = request.headers.get("X-API-Key")
        return key.strip() if key else "anonymous"

    async def dispatch(self, request: Request, call_next):
        now = time.time()
        identity = self._identity_key(request)

        window_start, count = self._state.get(identity, (now, 0))

        # If the window expired, reset it.
        if (now - window_start) > self._window_seconds:
            window_start = now
            count = 0

        count += 1
        self._state[identity] = (window_start, count)

        if count > self._max_requests:
            # 429 Too Many Requests
            return Response(
                content="Rate limit exceeded.",
                status_code=429,
                media_type="text/plain"
            )

        return await call_next(request)
