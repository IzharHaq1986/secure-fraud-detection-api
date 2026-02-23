# tests/test_rate_limit.py
"""
Rate limiting tests.

Goal:
- Ensure rate limiting middleware is active on /v1/predict.
- After enough rapid requests, the API should start returning 429.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_predict_rate_limited_under_burst() -> None:
    """
    Sends a burst of requests and expects at least one 429 response.

    Note:
    - Adjust BURST_COUNT if your limiter threshold is higher.
    - This test is meant to prove the limiter is on, not to benchmark it.
    """

    headers = {"x-api-key": "admin-secret-123"}
    payload = {
        "amount": 25.50,
        "currency": "USD",
        "merchant_country": "US",
        "channel": "card_present",
    }

    burst_count = 10
    status_codes = []

    for _ in range(burst_count):
        response = client.post("/v1/predict", headers=headers, json=payload)
        status_codes.append(response.status_code)

        # Stop early once we see rate limiting kick in.
        if response.status_code == 429:
            break

    assert 429 in status_codes
