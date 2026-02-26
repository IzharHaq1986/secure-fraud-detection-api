# tests/test_no_secret_leak.py
"""
Security tests: prevent secret leakage.

Goal:
- Ensure responses never contain API keys or secret env values.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_predict_does_not_leak_api_keys() -> None:
    """
    Even on errors, the API must not echo secrets.
    """

    # Use an invalid key to trigger an auth error response.
    response = client.post(
        "/v1/predict",
        headers={"x-api-key": "wrong-key"},
        json={
            "amount": 25.50,
            "currency": "USD",
            "merchant_country": "US",
            "channel": "card_present",
        },
    )

    # Auth should fail.
    assert response.status_code in (401, 403)

    body_text = response.text.lower()

    # These strings must not appear in the response body.
    assert "admin-secret-123" not in body_text
    assert "service-secret-123" not in body_text
    assert "api_key_admin" not in body_text
    assert "api_key_service" not in body_text
