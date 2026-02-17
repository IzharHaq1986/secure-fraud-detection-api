# app/main.py
"""
Secure Fraud Detection API (FastAPI)

This file defines:
- A FastAPI app factory (create_app) for clean initialization and testability
- A strict /v1/predict endpoint contract:
    FraudRequest -> FraudResponse
- API-key authentication enforced as an explicit dependency (hard to bypass)
- A safe request_id fallback when middleware is not present (CI/test friendly)

Why this exists:
- CI must never allow "wrong-key" to return 200.
- The predict endpoint must never return untyped / drifting response payloads.
"""

from __future__ import annotations

import os
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request

from app.schemas import FraudDecision, FraudRequest, FraudResponse


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """
    Enforce API-key authentication for protected endpoints.

    Notes:
    - Reads from 'x-api-key' header.
    - Valid keys are provided via environment variables:
        API_KEY_ADMIN
        API_KEY_SERVICE
      In CI, these should be set using GitHub Actions Secrets.
    - Returns 403 for missing/invalid key (matches your current behavior/tests).
    """

    if not x_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key.")

    allowed_keys = {
        os.getenv("API_KEY_ADMIN", ""),
        os.getenv("API_KEY_SERVICE", ""),
    }

    # If env vars are not set, the allowed set will contain empty strings.
    # This keeps the behavior secure-by-default (no accidental open access).
    if x_api_key not in allowed_keys:
        raise HTTPException(status_code=403, detail="Invalid API key.")

    return x_api_key


def create_app() -> FastAPI:
    """
    App factory (industry best practice).

    Benefits:
    - Cleaner imports for testing
    - Prevents side effects during module import
    - Keeps all initialization in one place
    """

    app = FastAPI(
        title="Secure Fraud Detection API",
        version="1.0.0",
    )

    @app.post(
        "/v1/predict",
        response_model=FraudResponse,
        # Dependency runs before the handler. If it fails, the handler is never executed.
        dependencies=[Depends(require_api_key)],
    )
    async def predict(request: Request, payload: FraudRequest) -> FraudResponse:
        """
        Fraud prediction endpoint (strict + authenticated).

        Security posture:
        - Auth is enforced via dependency (cannot be skipped accidentally).
        - Payload is validated by FraudRequest (required fields, extra="forbid").
        - Response is shaped by FraudResponse (prevents drift/leakage).
        - Never echo raw payload back to caller.
        """

        # Correlation ID:
        # If a request-id middleware sets request.state.request_id, use it.
        # Otherwise, generate a valid UUID to keep schemas + logs consistent.
        request_id = getattr(request.state, "request_id", None) or str(uuid4())

        # TODO: Replace with real model inference.
        # Keep deterministic placeholder logic for stable tests/CI behavior.
        score = 0.50

        # Simple decision policy mapping (replace with your real thresholds).
        if score >= 0.80:
            decision = FraudDecision.block
        elif score >= 0.50:
            decision = FraudDecision.review
        else:
            decision = FraudDecision.allow

        return FraudResponse(
            request_id=request_id,
            model_version="v1-placeholder",
            score=score,
            decision=decision,
        )

    return app


# Uvicorn entrypoint: "app.main:app"
app = create_app()
