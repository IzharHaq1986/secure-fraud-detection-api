# tests/test_predict.py

"""
Unit tests for /v1/predict endpoint.

These tests validate:
- Authentication enforcement
- Input schema validation
- Successful prediction response contract
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_HEADERS = {
    "x-api-key": "admin-secret-123"
}

VALID_PAYLOAD = {
    "amount": 25.50,
    "currency": "USD",
    "merchant_country": "US",
    "channel": "card_present"
}


def test_predict_success():
    """
    Should return 200 and a structured fraud response.
    """
    response = client.post(
        "/v1/predict",
        headers=VALID_HEADERS,
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()

    assert "request_id" in data
    assert "score" in data
    assert "decision" in data
    assert 0.0 <= data["score"] <= 1.0


def test_predict_missing_fields():
    """
    Should reject empty payload with 422 validation error.
    """
    response = client.post(
        "/v1/predict",
        headers=VALID_HEADERS,
        json={},
    )

    assert response.status_code == 422


def test_predict_invalid_api_key():
    """
    Should reject invalid API key.
    """
    response = client.post(
        "/v1/predict",
        headers={"x-api-key": "wrong-key"},
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 403
