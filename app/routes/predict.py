# app/routes/predict.py
"""
Router-based /v1/predict endpoint.

Why this file exists:
- Your repo currently defines /v1/predict in TWO places:
    1) app/main.py
    2) app/routes/predict.py
- CI/test execution can hit either route depending on how routers are included.

Fix applied here:
- Enforce API-key authentication on THIS router endpoint too, so "wrong-key"
  never returns 200 in CI or production.

Best practice note:
- Long-term, you should keep only ONE /v1/predict definition to avoid drift.
  For now, we secure both.
"""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, Request

from app.main import require_api_key
from app.schemas import FraudDecision, FraudRequest, FraudResponse

router = APIRouter()


@router.post("/v1/predict", response_model=FraudResponse)
async def predict(
    request: Request,
    payload: FraudRequest,
    _api_key: str = Depends(require_api_key),
) -> FraudResponse:
    """
    Fraud prediction endpoint (router version).

    Security posture:
    - `_api_key` is intentionally unused; it exists to enforce authentication.
    - `payload` is validated via FraudRequest.
    - Response is shaped by FraudResponse to prevent response drift/leakage.
    - Never echo raw request payload back to the client.
    """

    # Correlation ID:
    # If request-id middleware sets request.state.request_id, use it.
    # Otherwise generate a valid UUID so response validation always passes.
    request_id = getattr(request.state, "request_id", None) or str(uuid4())

    # TODO: Replace with real model inference.
    # Keep deterministic placeholder logic so tests remain stable.
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
