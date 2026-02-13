"""
middleware.py

Request/response middleware for the Secure Fraud Detection API.

Includes:
- RequestIdMiddleware:
    Ensures every request has a stable request_id for tracing and audit logging.
- SimpleRateLimitMiddleware:
    Minimal in-memory rate limiting keyed by API key (demo-friendly).
- SecurityHeadersMiddleware:
    Adds baseline security headers to every response.

Notes:
- This is a portfolio / demo implementation.
- For production, rate limiting should use a shared store (e.g., Redis) and
  the service should sit behind a proper API gateway / WAF.
"""

import time
import uuid
from typing import Dict, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Ensure every request has a request_id.

    Behavior:
    - If client provides X-Request-Id, we respect it.
    - Otherwise, generate a UUID4.
    - Always return X-Request-Id in the response.
    """

    async def dispatch(self, request: Request, call_next):
        incoming_request_id = request.headers.get("X-Request-Id", "").strip()

        if incoming_request_id:
            request_id = incoming_request_id
        else:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id

        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory rolling-window rate limiter.

    Key points:
    - Identity key: X-API-Key header (or "anonymous" if missing).
    - Window resets after window_seconds.
    - If max_requests exceeded, return HTTP 429.

    This is intentionally simple (demo-quality).
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds

        # identity -> (window_start_epoch_seconds, request_count)
        self._state: Dict[str, Tuple[float, int]] = {}

    @staticmethod
    def _get_identity(request: Request) -> str:
        """
        Derive an identity string for rate limiting.

        We use the API key value directly as the in-memory key for simplicity.
        In production, you would hash it or use a stable caller ID.
        """
        api_key = request.headers.get("X-API-Key")
        return api_key.strip() if api_key else "anonymous"

    async def dispatch(self, request: Request, call_next):
        now = time.time()
        identity = self._get_identity(request)

        window_start, count = self._state.get(identity, (now, 0))

        # Reset the window if it expired.
        if (now - window_start) > self._window_seconds:
            window_start = now
            count = 0

        count += 1
        self._state[identity] = (window_start, count)

        if count > self._max_requests:
            return Response(
                content="Rate limit exceeded.",
                status_code=429,
                media_type="text/plain",
            )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add baseline security headers to every response.

    These headers help reduce exposure to common web issues and signal
    security maturity, even for an API-only service.
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Avoid MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Reduce referrer leakage
        response.headers["Referrer-Policy"] = "no-referrer"

        # Disable powerful browser features (defense-in-depth)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # HSTS enforces HTTPS in browsers (ignored on plain HTTP).
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
