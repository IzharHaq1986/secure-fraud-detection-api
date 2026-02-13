import os
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status


@dataclass(frozen=True)
class CallerIdentity:
    """
    Minimal identity model for v1.

    We intentionally keep this simple:
    - No database
    - No user accounts
    - Keys map to roles
    """
    role: str
    key_id: str  # A non-sensitive identifier for audit logs


def _load_api_keys() -> dict:
    """
    Load API keys from environment.

    This expects:
    - API_KEY_ADMIN
    - API_KEY_SERVICE
    """
    admin_key = os.getenv("API_KEY_ADMIN", "").strip()
    service_key = os.getenv("API_KEY_SERVICE", "").strip()

    return {
        "admin": admin_key,
        "service": service_key
    }


def authenticate(x_api_key: Optional[str]) -> CallerIdentity:
    """
    Validate the incoming API key and return the caller identity.

    We do not log raw API keys.
    We return a 'key_id' that is safe for audit logs.
    """
    keys = _load_api_keys()

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key (X-API-Key)."
        )

    x_api_key = x_api_key.strip()

    if x_api_key == keys["admin"]:
        return CallerIdentity(role="admin", key_id="admin-key")

    if x_api_key == keys["service"]:
        return CallerIdentity(role="service", key_id="service-key")

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API key."
    )
