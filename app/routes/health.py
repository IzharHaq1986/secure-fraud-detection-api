# app/routes/health.py
"""
Health endpoints.

These endpoints support:
- uptime checks (/health)
- diagnostic checks (/health/details)
- authenticated diagnostics (/health/secure-details)

Note:
- Keep responses small and non-sensitive.
- Secure details requires API-key auth.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.auth import require_api_key

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict:
    """
    Basic liveness check.
    """
    return {"status": "ok"}


@router.get("/details")
def health_details() -> dict:
    """
    Basic diagnostic details that remain safe to expose publicly.
    """
    return {
        "status": "ok",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/secure-details")
def health_secure_details(_api_key: str = Depends(require_api_key)) -> dict:
    """
    Authenticated diagnostic endpoint.

    `_api_key` is intentionally unused; it exists to enforce authentication.
    """
    return {
        "status": "ok",
        "secure": True,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
