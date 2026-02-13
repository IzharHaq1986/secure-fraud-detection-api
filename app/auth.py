"""
auth.py

Minimal API-key authentication + role mapping for the Secure Fraud Detection API.

Security intent:
- Keep v1 simple (no DB, no user system).
- Map known API keys -> roles.
- Never log raw API keys.
"""

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status


@dataclass(frozen=True)
class CallerIdentity:
    """
    Minimal identity returned after authentication.

    role:
        Authorization tier for the caller (e.g., 'admin', 'service').

    key_id:
        A non-sensitive identifier for audit logs. This is NOT the raw key.
    """
    role: str
    key_id: str


def _read_env_value(name: str) -> str:
    """
    Read an environment variable and normalize it.

    Returns:
        A stripped string value. If missing, returns empty string.
    """
    value = os.getenv(name, "")
    return value.strip()


def _load_api_keys() -> dict:
    """
    Load API keys from environment variables.

    Expected variables:
    - API_KEY_ADMIN
    - API_KEY_SERVICE
    """
    return {
        "admin": _read_env_value("API_KEY_ADMIN"),
        "service": _read_env_value("API_KEY_SERVICE"),
    }


def authenticate(x_api_key: Optional[str]) -> CallerIdentity:
    """
    Validate an incoming API key and return a CallerIdentity.

    Args:
        x_api_key:
            The raw value of the X-API-Key header (may be None).

    Raises:
        HTTPException 401 if missing.
        HTTPException 403 if invalid or not configured.

    Returns:
        CallerIdentity describing the authenticated caller.
    """
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key (X-API-Key).",
        )

    provided_key = x_api_key.strip()
    keys = _load_api_keys()

    admin_key = keys.get("admin", "")
    service_key = keys.get("service", "")

    # If keys are not configured, fail closed.
    if not admin_key and not service_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API keys are not configured on the server.",
        )

    if admin_key and provided_key == admin_key:
        return CallerIdentity(role="admin", key_id="admin-key")

    if service_key and provided_key == service_key:
        return CallerIdentity(role="service", key_id="service-key")

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API key.",
    )
