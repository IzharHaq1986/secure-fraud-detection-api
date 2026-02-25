"""
main.py

FastAPI application entrypoint for the Secure Fraud Detection API.

Goals:
- Provide a single, predictable application object: `app`
- Register middleware and routers
- Keep selected health endpoints public
- Advertise API-key auth clearly in OpenAPI by setting `security` at the operation level
- Include an OpenAPI marker to confirm the customization is active

Container layout (confirmed):
- Routers live under: app/routes/
  - app/routes/health.py
  - app/routes/predict.py
- Middleware lives as: app/middleware.py
"""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# ---------------------------------------------------------------------------
# Optional imports (kept resilient to refactors)
# ---------------------------------------------------------------------------

# Rate limiting middleware (file-based layout: app/middleware.py)
SimpleRateLimitMiddleware = None
try:
    from app.middleware import SimpleRateLimitMiddleware  # type: ignore
except Exception:
    # Keep startup resilient if middleware name/path changes or is absent
    SimpleRateLimitMiddleware = None

# Health router (folder-based layout: app/routes/health.py)
HEALTH_ROUTER = None
try:
    from app.routes.health import router as HEALTH_ROUTER  # type: ignore
except Exception:
    # Keep startup resilient if health router is moved/renamed
    HEALTH_ROUTER = None

# Predict router (folder-based layout: app/routes/predict.py)
PREDICT_ROUTER = None
try:
    from app.routes.predict import router as PREDICT_ROUTER  # type: ignore
except Exception:
    # Keep startup resilient if predict router is moved/renamed
    PREDICT_ROUTER = None

# ---------------------------------------------------------------------------
# OpenAPI customization
# ---------------------------------------------------------------------------

API_KEY_HEADER_NAME = "X-API-Key"

# Paths intended to be callable without authentication.
# Add/remove entries to match intended exposure.
PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/live",
    "/health/details",
}


def _apply_openapi_api_key_auth(app: FastAPI) -> Dict[str, Any]:
    """
    Build an OpenAPI schema that:
    - Defines an API-key security scheme (header: X-API-Key)
    - Sets operation-level security for every route:
        - Public paths:  operation["security"] = []
        - Protected:     operation["security"] = [{"ApiKeyAuth": []}]
    - Adds a marker field to confirm the customization is active

    Notes:
    - Operation-level security is used because many client tools and audits
      do not treat top-level `security` as sufficient.
    - Schema is rebuilt on each call to avoid stale cached schemas during iteration.
    """
    schema: Dict[str, Any] = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Marker field used for debugging/verification
    schema["x-openapi-custom"] = "api-key-op-security-v1"

    # Define the security scheme in components
    components: Dict[str, Any] = schema.setdefault("components", {})
    security_schemes: Dict[str, Any] = components.setdefault("securitySchemes", {})
    security_schemes["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": API_KEY_HEADER_NAME,
    }

    # Explicitly set security per operation (GET/POST/etc.)
    paths: Dict[str, Any] = schema.get("paths", {})
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for _, operation in path_item.items():
            # Operations are dicts under each path (get/post/put/delete/etc.)
            if not isinstance(operation, dict):
                continue

            if path in PUBLIC_PATHS:
                # Explicitly public
                operation["security"] = []
            else:
                # Explicitly protected
                operation["security"] = [{"ApiKeyAuth": []}]

    # Also set a global default for tools that read top-level security
    schema["security"] = [{"ApiKeyAuth": []}]

    # Store the generated schema on the app (FastAPI convention)
    app.openapi_schema = schema
    return schema


def _install_custom_openapi(app: FastAPI) -> None:
    """
    Attach the custom OpenAPI generator to the FastAPI app.
    """

    def custom_openapi() -> Dict[str, Any]:
        return _apply_openapi_api_key_auth(app)

    app.openapi = custom_openapi  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=os.getenv("APP_TITLE", "Secure Fraud Detection API"),
        version=os.getenv("APP_VERSION", "0.1.0"),
        description=os.getenv(
            "APP_DESCRIPTION",
            "Fraud scoring API with auditability and security controls.",
        ),
    )

    # Middleware: rate limiting
    if SimpleRateLimitMiddleware is not None:
        app.add_middleware(SimpleRateLimitMiddleware)

    # Routers
    if HEALTH_ROUTER is not None:
        app.include_router(HEALTH_ROUTER)

    if PREDICT_ROUTER is not None:
        app.include_router(PREDICT_ROUTER)

    # OpenAPI customization (advertise auth accurately)
    _install_custom_openapi(app)

    return app


# ---------------------------------------------------------------------------
# ASGI entrypoint
# ---------------------------------------------------------------------------

app = create_app()
