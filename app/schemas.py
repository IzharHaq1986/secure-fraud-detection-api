# app/schemas.py
"""
Shared request/response schemas used by the FastAPI app.

Why this file exists:
- app.main imports FraudRequest and FraudResponse from here.
- We keep the API contract explicit and strict (fintech-safe).
- Pydantic v2 compliant (no legacy `class Config`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr


class Channel(str, Enum):
    """
    Where the transaction originated.
    Keep this list tight to prevent garbage inputs.
    """

    card_present = "card_present"
    web = "web"
    mobile = "mobile"
    api = "api"


class FraudDecision(str, Enum):
    """
    High-level action recommendation.
    """

    allow = "allow"
    review = "review"
    block = "block"


class FraudRequest(BaseModel):
    """
    Strict input schema for /v1/predict.

    Fintech notes:
    - Strong validation prevents garbage/risky fields.
    - `extra="forbid"` blocks unknown fields (common abuse vector).
    - Keep PII out unless you explicitly need it.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    amount: StrictFloat = Field(
        ...,
        gt=0.0,
        description="Transaction amount. Must be > 0.",
    )

    currency: StrictStr = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code (e.g., USD).",
    )

    merchant_country: StrictStr = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code (e.g., US).",
    )

    channel: Channel = Field(
        ...,
        description="Transaction channel/origin.",
    )

    # Optional, non-PII enrichment fields (keep conservative by default)
    customer_id: Optional[StrictStr] = Field(
        default=None,
        max_length=64,
        description="Optional customer identifier (avoid PII).",
    )

    device_id: Optional[StrictStr] = Field(
        default=None,
        max_length=128,
        description="Optional device identifier (avoid raw hardware identifiers).",
    )

    ip_address: Optional[StrictStr] = Field(
        default=None,
        max_length=64,
        description="Optional client IP (string form). Prefer server-derived IP when possible.",
    )

    transaction_id: Optional[StrictStr] = Field(
        default=None,
        max_length=64,
        description="Optional transaction reference ID.",
    )

    # Optional metadata for experimentation (kept strict)
    metadata: Optional[Dict[StrictStr, Any]] = Field(
        default=None,
        description="Optional metadata map (keys must be strings).",
    )


class FraudResponse(BaseModel):
    """
    Strict response schema for /v1/predict.

    Important:
    - Keep response minimal and safe to disclose.
    - Avoid returning raw features or anything that helps attackers.
    """

    # This avoids Pydantic warning for `model_version` (protected namespace "model_").
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        protected_namespaces=(),
    )

    request_id: StrictStr = Field(
        ...,
        description="Correlation ID for logs/audit tracing.",
        min_length=8,
        max_length=128,
    )

    model_version: StrictStr = Field(
        ...,
        description="Deployed model version identifier.",
        min_length=1,
        max_length=64,
    )

    score: StrictFloat = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraud risk score between 0.0 and 1.0.",
    )

    decision: FraudDecision = Field(
        ...,
        description="Recommended action derived from score/policy.",
    )

    timestamp_utc: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the decision.",
    )

    # Optional, safe-to-share fields
    reasons: Optional[List[StrictStr]] = Field(
        default=None,
        description="Short reason codes (no PII, no model internals).",
    )

    # Optional counters or debug flags (safe only)
    rules_version: Optional[StrictStr] = Field(
        default=None,
        max_length=64,
        description="Optional rules/policy version used for decisioning.",
    )

    # If you ever include this, keep it coarse and non-identifying.
    risk_band: Optional[StrictStr] = Field(
        default=None,
        max_length=16,
        description="Optional coarse risk band (low/medium/high).",
    )
