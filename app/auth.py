# app/auth.py
"""
Authentication helpers.

This module exists to avoid circular imports:
- main.py registers routers
- routers need auth dependencies
- therefore auth must NOT live in main.py
"""

from __future__ import annotations

import os

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """
    Enforce API-key authentication.

    - Reads API key from the `x-api-key` header.
    - Valid keys are read from environment variables:
        * API_KEY_ADMIN
        * API_KEY_SERVICE
    - Returns HTTP 403 for missing/invalid key.

    Secure-by-default:
    - If env keys are missing, no request is allowed.
    """

    if not x_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key.")

    allowed_keys = {
        os.getenv("API_KEY_ADMIN", ""),
        os.getenv("API_KEY_SERVICE", ""),
    }

    if x_api_key not in allowed_keys:
        raise HTTPException(status_code=403, detail="Invalid API key.")

    return x_api_key
