# app/main.py
"""
Secure Fraud Detection API (FastAPI)

This module provides:
- A FastAPI app factory (`create_app`) for clean initialization and testability
- Deterministic middleware wiring for both production and test runs
- Router registration:
    * /v1/predict           -> app/routes/predict.py
    * /health endpoints     -> app/routes/health.py

Why this layout:
- Keeps each route in a dedicated router file (single source of truth).
- Ensures OpenAPI includes both predict and health endpoints.
- Enables deterministic rate limiting in test mode.

Environment variables:
- APP_ENV:
    * "test"  -> low-threshold rate limiting (predictable 429 behavior)
    * other   -> middleware defaults
"""

from __future__ import annotations

import os

from fastapi import FastAPI

from app.middleware import SimpleRateLimitMiddleware
from app.routes.health import router as health_router
from app.routes.predict import router as predict_router


def create_app() -> FastAPI:
    """
    FastAPI app factory (industry best practice).

    Benefits:
    - Reduces side effects during import
    - Keeps initialization logic centralized
    - Makes TestClient usage predictable
    """

    app = FastAPI(
        title="Secure Fraud Detection API",
        version="1.0.0",
    )

    # ---------------------------------------------------------------------
    # Middleware
    # ---------------------------------------------------------------------
    # Rate limiting:
    # - Always enabled
    # - In test mode, use a tiny threshold so 429 can be asserted deterministically.
    if os.getenv("APP_ENV") == "test":
        app.add_middleware(
            SimpleRateLimitMiddleware,
            max_requests=3,
            window_seconds=60,
        )
    else:
        app.add_middleware(SimpleRateLimitMiddleware)

    # ---------------------------------------------------------------------
    # Routers
    # ---------------------------------------------------------------------
    # Primary scoring endpoint.
    app.include_router(predict_router)

    # Health endpoints used by monitoring/load balancers.
    app.include_router(health_router)

    return app


# Uvicorn entrypoint: "app.main:app"
app = create_app()
