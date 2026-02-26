# tests/test_predict_rejects_extra_fields.py
"""
Schema security tests.

Goal:
- Ensure FraudRequest uses extra="forbid"
- Unknown fields must be rejected with 422
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_predict_rejects_unknown_fields() -> None:
    """
    Unknown input fields must be rejected (prevents garbage / risky inputs).
    """
    response = client.post(
        "/v1/predict",
        headers={"x-api-key": "admin-secret-123"},
        json={
            "amount": 25.50,
            "currency": "USD",
            "merchant_country": "US",
            "channel": "card_present",
            "unexpected_field": "should_not_be_allowed",
        },
    )

    assert response.status_code == 422
