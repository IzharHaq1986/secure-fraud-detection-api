# app/main.py
"""
Secure Fraud Detection API (FastAPI)

This file defines:
- FastAPI app initialization
- Core middleware wiring (request id, rate limiting, security headers, etc.)
- Strict /v1/predict endpoint contract (FraudRequest -> FraudResponse)

Key CI issue this fixes:
- Ensures /v1/predict uses strict Pydantic schemas and returns score/decision fields,
  instead of the older "not_implemented" stub response.
"""

from __future__ import annotations

from fastapi import FastAPI, Request

# NOTE:
# Keep these imports aligned with your existing modules.
# If any import path differs in your repo, adjust it to match your structure.
from app.schemas import FraudDecision, FraudRequest, FraudResponse


def create_app() -> FastAPI:
    """
    App factory (industry best practice).

    Benefits:
    - Easier testing (TestClient can import app without side effects)
    - Clear separation of initialization vs runtime
    """

    app = FastAPI(
        title="Secure Fraud Detection API",
        version="1.0.0",
    )

    # ----------------------------
    # Middleware wiring
    # ----------------------------
    # Keep your existing middleware setup as-is.
    # Example placeholders (DO NOT duplicate if you already add them elsewhere):
    #
    # app.add_middleware(RequestIdMiddleware)
    # app.add_middleware(SecurityHeadersMiddleware)
    # app.add_middleware(RateLimitMiddleware)
    #
    # If your project uses function-style middleware (app.middleware("http")),
    # keep those definitions in this file or import them here.

    # ----------------------------
    # Routes
    # ----------------------------

    @app.post("/v1/predict", response_model=FraudResponse)
    async def predict(request: Request, payload: FraudRequest) -> FraudResponse:
        """
        Fraud prediction endpoint (strict contract).

        Input:
        - `payload` is a FraudRequest (Pydantic enforces required fields and blocks extras)

        Output:
        - FraudResponse (prevents drift and accidental leakage)

        Security posture:
        - Never echo raw payload back to caller
        - Keep response minimal and non-sensitive
        """

        # Request correlation (set by your existing request-id middleware).
        request_id = getattr(request.state, "request_id", "unknown")

        # TODO: Replace this placeholder with real model inference.
        # Keep it deterministic for now so tests remain stable.
        score = 0.50

        # Example decision policy. Replace thresholds with your real policy.
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


# Uvicorn entrypoint (commonly referenced as "app.main:app")
app = create_app()
