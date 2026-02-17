# app/main.py
"""
Secure Fraud Detection API (FastAPI)

This module provides:
- An app factory (`create_app`) for clean initialization and testability
- A strict, authenticated `/v1/predict` endpoint:
    FraudRequest -> FraudResponse
- API-key auth enforced via endpoint dependency (hard to bypass)
- A safe request_id fallback (UUID) when middleware is absent (CI/test friendly)

Security notes:
- CI does NOT load your local .env by default.
- In CI, API keys should be provided via environment variables:
    API_KEY_ADMIN
    API_KEY_SERVICE
"""

from __future__ import annotations

import os
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request

from app.schemas import FraudDecision, FraudRequest, FraudResponse


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """
    Enforce API-key authentication.

    - Reads API key from the `x-api-key` header.
    - Valid keys are read from environment variables:
        * API_KEY_ADMIN
        * API_KEY_SERVICE
    - Returns HTTP 403 for missing/invalid key (matches current tests).

    IMPORTANT:
    - This is secure-by-default: if env keys are missing, no request is allowed.
    """

    if not x_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key.")

    admin_key = os.getenv("API_KEY_ADMIN", "")
    service_key = os.getenv("API_KEY_SERVICE", "")

    allowed_keys = {admin_key, service_key}

    # If the env vars were not configured, allowed_keys may contain empty strings.
    # This keeps the API locked down rather than accidentally open.
    if x_api_key not in allowed_keys:
        raise HTTPException(status_code=403, detail="Invalid API key.")

    return x_api_key


def create_app() -> FastAPI:
    """
    FastAPI app factory (industry best practice).

    Benefits:
    - Reduces side effects during import
    - Makes TestClient usage clean and predictable
    - Keeps initialization logic centralized
    """

    app = FastAPI(
        title="Secure Fraud Detection API",
        version="1.0.0",
    )

    @app.post("/v1/predict", response_model=FraudResponse)
    async def predict(
        request: Request,
        payload: FraudRequest,
        _api_key: str = Depends(require_api_key),
    ) -> FraudResponse:
        """
        Fraud prediction endpoint (strict + authenticated).

        - `_api_key` is intentionally unused; it exists to enforce auth.
        - `payload` is validated by FraudRequest (required fields + extra="forbid").
        - Response is shaped by FraudResponse (prevents response drift/leakage).
        - Never echo raw payload back to the caller.
        """

        # Correlation ID:
        # If request-id middleware sets request.state.request_id, use it.
        # Otherwise generate a valid UUID so response validation always passes.
        request_id = getattr(request.state, "request_id", None) or str(uuid4())

        # TODO: Replace with real model inference.
        # Keep deterministic placeholder logic so tests remain stable.
        score = 0.50

        # Decision policy mapping (replace with your real thresholds/policy).
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
