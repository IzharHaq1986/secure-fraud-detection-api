"""
tests/test_rate_limit.py

Rate limiting tests.

Intent:
- Prove the rate limiter middleware is active.
- Keep tests fast and stable by using test-specific limiter thresholds.
- Ensure authentication is valid so requests reach the endpoint consistently.

Notes:
- These tests are not benchmarks.
- Each test builds a small FastAPI app instance with the same routers as the service,
  but with a lower max_requests/window_seconds configuration for deterministic results.
"""

from __future__ import annotations

import time
from typing import List

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware import SimpleRateLimitMiddleware
from app.routes.health import router as health_router
from app.routes.predict import router as predict_router


def _build_test_client(max_requests: int, window_seconds: int) -> TestClient:
    """
    Build a TestClient for a minimal app with:
    - SimpleRateLimitMiddleware configured with given thresholds
    - Health + predict routers registered
    """
    test_app = FastAPI()
    test_app.add_middleware(
        SimpleRateLimitMiddleware,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )

    test_app.include_router(health_router)
    test_app.include_router(predict_router)

    return TestClient(test_app)


def _fraud_payload() -> dict:
    """
    Minimal valid FraudRequest payload for /v1/predict.
    """
    return {
        "amount": 25.50,
        "currency": "USD",
        "merchant_country": "US",
        "channel": "card_present",
    }


def test_predict_rate_limited_under_burst(monkeypatch) -> None:
    """
    Send a burst of authenticated requests and expect at least one 429 response.

    Approach:
    - Configure API_KEY_ADMIN so auth passes.
    - Use a low limiter threshold for deterministic behavior.
    """
    monkeypatch.setenv("API_KEY_ADMIN", "test-admin-key")

    client = _build_test_client(max_requests=3, window_seconds=60)

    headers = {"X-API-Key": "test-admin-key"}
    payload = _fraud_payload()

    burst_count = 10
    status_codes: List[int] = []

    for _ in range(burst_count):
        response = client.post("/v1/predict", headers=headers, json=payload)
        status_codes.append(response.status_code)

        # Stop early once rate limiting is observed
        if response.status_code == 429:
            break

    assert 429 in status_codes, f"Expected 429 in burst, got: {status_codes}"


def test_rate_limit_window_resets(monkeypatch) -> None:
    """
    Confirm the limiter allows requests again after the window expires.

    Configuration:
    - max_requests=2 within a 1-second window
    """
    monkeypatch.setenv("API_KEY_ADMIN", "test-admin-key")

    client = _build_test_client(max_requests=2, window_seconds=1)

    headers = {"X-API-Key": "test-admin-key"}
    payload = _fraud_payload()

    # Consume allowed requests
    assert client.post("/v1/predict", headers=headers, json=payload).status_code == 200
    assert client.post("/v1/predict", headers=headers, json=payload).status_code == 200

    # Next request exceeds the limit
    assert client.post("/v1/predict", headers=headers, json=payload).status_code == 429

    # After the window expires, requests should be allowed again
    time.sleep(1.1)
    assert client.post("/v1/predict", headers=headers, json=payload).status_code == 200
